"""Segunda rota de foto com licença (achado A7): a Wikimedia Commons, quando a Openverse não responde.

Teste do aluno (08/10/2026): a Openverse devolveu "Connection reset by peer" e o script não oferecia
outra rota; o aluno escreveu a própria consulta à API da Commons. Aqui a rede é SIMULADA: a resposta da
Commons é uma gravação real (`fixtures/commons-resposta.json`, busca "woodworking workshop"), e a
Openverse falha por exceção. A suíte não depende de internet.
"""
import importlib.util
import io
import json
import pathlib
import contextlib
import unittest
import urllib.error
import urllib.parse

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("assets_search", AQUI / "assets-search.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

GRAVADA = json.loads((AQUI / "fixtures" / "commons-resposta.json").read_text(encoding="utf-8"))


class Resp:
    """Resposta HTTP mínima para `urlopen` (usada como gerenciador de contexto)."""

    def __init__(self, corpo, status=200, cabecalhos=None):
        self._corpo = corpo if isinstance(corpo, bytes) else json.dumps(corpo).encode("utf-8")
        self.status = status
        self.headers = cabecalhos or {}

    def read(self):
        return self._corpo

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def http429(retry_after="2"):
    return urllib.error.HTTPError("https://commons.wikimedia.org/w/api.php", 429, "Too Many Requests",
                                  {"Retry-After": retry_after}, io.BytesIO(b""))


class Rede:
    """Roteia as chamadas: Openverse -> `openverse`, Commons -> fila `commons` (resposta ou exceção)."""

    def __init__(self, openverse, commons):
        self.openverse, self.commons = openverse, list(commons)
        self.chamadas, self.pausas = [], []

    def abrir(self, req, timeout=20):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        self.chamadas.append(url)
        if "openverse.org" in url:
            if isinstance(self.openverse, Exception):
                raise self.openverse
            return Resp(self.openverse)
        if "commons.wikimedia.org" in url:
            item = self.commons.pop(0)
            if isinstance(item, Exception):
                raise item
            return Resp(item)
        raise AssertionError("chamada de rede inesperada: " + url)

    def dormir(self, s):
        self.pausas.append(s)


class Commons(unittest.TestCase):
    def setUp(self):
        self._orig = (mod._abrir_url, mod.time.sleep)

    def tearDown(self):
        mod._abrir_url, mod.time.sleep = self._orig

    def instalar(self, rede):
        mod._abrir_url = rede.abrir
        mod.time.sleep = rede.dormir
        return rede

    def buscar(self, rede, limit=6):
        self.instalar(rede)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            r = mod.buscar_foto_sem_chave("woodworking workshop", limit=limit, orientation="landscape")
        return r, err.getvalue()

    def test_openverse_fora_do_ar_a_commons_responde_e_diz_qual_rota(self):
        rede = Rede(urllib.error.URLError(ConnectionResetError(54, "Connection reset by peer")), [GRAVADA])
        r, err = self.buscar(rede)
        self.assertEqual(r["fonte"], "commons")
        self.assertGreaterEqual(len(r["itens"]), 3)
        self.assertIn("Openverse não respondeu", r["motivo"])
        self.assertTrue(any("openverse.org" in u for u in rede.chamadas))
        self.assertTrue(any("commons.wikimedia.org" in u for u in rede.chamadas))
        saida = mod.format_openverse(r["itens"], "woodworking workshop", fonte="Wikimedia Commons", motivo=r["motivo"])
        self.assertIn("Rota que respondeu: Wikimedia Commons", saida)
        self.assertIn("Openverse não respondeu", saida)

    def test_mesmo_formato_e_mesmos_campos_de_licenca_da_openverse(self):
        rede = Rede(urllib.error.URLError("fora"), [GRAVADA])
        r, _ = self.buscar(rede)
        modelo = mod._normaliza_item_openverse({"id": "x", "title": "t", "url": "https://x/y.jpg", "creator": "a",
                                                "license": "by", "license_version": "2.0", "width": 10, "height": 5})
        for item in r["itens"]:
            self.assertEqual(set(item), set(modelo), "campos diferentes dos da Openverse")
            self.assertTrue(item["url"].startswith("https://"))
            self.assertTrue(item["licenca"].startswith(("CC0", "CC BY", "Public")), item["licenca"])
            self.assertTrue(item["licenca_url"].startswith("http"), item)
            self.assertTrue(item["autor"] and "<" not in item["autor"], item["autor"])
            self.assertIn(item["autor"], item["credito"])
            self.assertIn("commons.wikimedia.org/wiki/File:", item["pagina_origem"])
        cc2 = [i for i in r["itens"] if i["licenca"] == "CC BY 2.0"]
        self.assertTrue(cc2 and cc2[0]["exige_credito"])
        self.assertEqual(cc2[0]["autor"], "Shixart1985")
        self.assertIn("creativecommons.org/licenses/by/2.0", cc2[0]["licenca_url"])
        zero = [i for i in r["itens"] if i["licenca"].startswith("CC0")]
        self.assertTrue(zero and not zero[0]["exige_credito"])

    def test_openverse_respondendo_a_commons_nao_e_chamada(self):
        ov = {"results": [{"id": "1", "title": "Foto", "url": "https://live.staticflickr.com/a.jpg", "creator": "Ana",
                           "license": "cc0", "license_version": "1.0", "width": 4000, "height": 3000}]}
        rede = Rede(ov, [])
        mod._imagem_esta_viva = lambda url, timeout=8: True
        r, _ = self.buscar(rede)
        self.assertEqual(r["fonte"], "openverse")
        self.assertFalse(any("commons.wikimedia.org" in u for u in rede.chamadas))

    def test_pausa_antes_de_chamar_a_commons(self):
        rede = Rede(urllib.error.URLError("fora"), [GRAVADA])
        self.buscar(rede)
        self.assertTrue(rede.pausas and max(rede.pausas) >= mod.PAUSA_COMMONS, rede.pausas)

    def test_http_429_espera_o_retry_after_e_tenta_uma_vez(self):
        rede = Rede(urllib.error.URLError("fora"), [http429("3"), GRAVADA])
        r, err = self.buscar(rede)
        self.assertEqual(r["fonte"], "commons")
        self.assertGreaterEqual(len(r["itens"]), 3)
        self.assertIn(3, [int(p) for p in rede.pausas], rede.pausas)
        self.assertEqual(sum(1 for u in rede.chamadas if "commons.wikimedia.org" in u), 2)
        self.assertIn("429", err)

    def test_http_429_persistente_nao_entra_em_laco(self):
        rede = Rede(urllib.error.URLError("fora"), [http429("1"), http429("1"), http429("1")])
        r, err = self.buscar(rede)
        self.assertEqual(r["itens"], [])
        self.assertEqual(sum(1 for u in rede.chamadas if "commons.wikimedia.org" in u), 2)
        self.assertIn("429", err)
        self.assertIn("Wikimedia Commons", err)

    def test_retry_after_gigante_tem_teto(self):
        rede = Rede(urllib.error.URLError("fora"), [http429("86400"), GRAVADA])
        self.buscar(rede)
        self.assertLessEqual(max(rede.pausas), mod.TETO_ESPERA_COMMONS)

    def test_mutante_licenca_nc_nd_e_gfdl_nao_entram(self):
        ruim = json.loads(json.dumps(GRAVADA))
        paginas = list(ruim["query"]["pages"].values())
        for p, lic in zip(paginas, ["CC BY-NC 4.0", "CC BY-ND 2.0", "GFDL 1.2", "Copyrighted free use"]):
            p["imageinfo"][0]["extmetadata"]["LicenseShortName"]["value"] = lic
        rede = Rede(urllib.error.URLError("fora"), [ruim])
        r, _ = self.buscar(rede, limit=20)
        for item in r["itens"]:
            self.assertNotRegex(item["licenca"], r"NC|ND|GFDL|Copyrighted")
        self.assertEqual(len(r["itens"]), len(paginas) - 4)

    def test_as_duas_rotas_fora_devolvem_vazio_sem_estourar(self):
        rede = Rede(urllib.error.URLError("fora"), [urllib.error.URLError("tambem fora")])
        r, err = self.buscar(rede)
        self.assertEqual(r["itens"], [])
        self.assertIn("Openverse", err)
        self.assertIn("Commons", err)
        saida = mod.format_openverse([], "x", fonte="Wikimedia Commons")
        self.assertIn("Nenhuma foto encontrada", saida)

    def test_resposta_da_commons_fora_do_formato_nao_estoura(self):
        for lixo in ({}, {"query": {}}, {"query": {"pages": []}}, ["x"]):
            rede = Rede(urllib.error.URLError("fora"), [lixo])
            r, _ = self.buscar(rede)
            self.assertEqual(r["itens"], [], lixo)

    def test_rota_explicita_commons_na_linha_de_comando(self):
        rede = self.instalar(Rede(urllib.error.URLError("nunca chamada"), [GRAVADA]))
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            import sys
            velho = sys.argv
            sys.argv = ["assets-search.py", "woodworking workshop", "--type", "commons", "-n", "3"]
            try:
                mod.main()
            finally:
                sys.argv = velho
        self.assertIn("Wikimedia Commons", saida.getvalue())
        self.assertFalse(any("openverse.org" in u for u in rede.chamadas))


# ---- 3.5.8: achados N5 (acervo ruim, autor e categoria, miniatura) e N6 (larguras padrão da Commons) ----
def com_titulos(*titulos):
    """Resposta gravada com os títulos trocados (a licença e o resto continuam os da gravação)."""
    r = json.loads(json.dumps(GRAVADA))
    paginas = list(r["query"]["pages"].values())
    for p, t in zip(paginas, titulos):
        p["title"] = "File:" + t
    r["query"]["pages"] = {str(i): p for i, p in enumerate(paginas[:len(titulos)])}
    return r


class CommonsAcervoELarguras(unittest.TestCase):
    def setUp(self):
        self._orig = (mod._abrir_url, mod.time.sleep)

    def tearDown(self):
        mod._abrir_url, mod.time.sleep = self._orig

    def buscar(self, resposta, **kw):
        rede = Rede(urllib.error.URLError("fora"), [resposta])
        mod._abrir_url, mod.time.sleep = rede.abrir, rede.dormir
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            itens = mod.search_commons("solid wood dining table", limit=20, orientation="landscape", **kw)
        return itens, err.getvalue(), rede

    LIXO = ["EFTA00123456.jpg", "Dollhouse living room with tiny table.jpg", "Horse trailer interior.jpg",
            "Living room of the Museum of Decorative Arts.jpg"]
    BOM = ["Solid oak dining table in a bright kitchen.jpg", "Hand sanding a walnut table top.jpg"]

    def test_n5_acervo_de_museu_casa_de_boneca_trailer_e_prova_policial_ficam_de_fora_e_o_aviso_conta(self):
        itens, err, _ = self.buscar(com_titulos(*(self.LIXO + self.BOM)))
        titulos = [i["titulo"] for i in itens]
        self.assertEqual(len(itens), 2, titulos)
        self.assertTrue(all(t.startswith(("Solid oak", "Hand sanding")) for t in titulos), titulos)
        self.assertIn("4 resultado(s) descartado(s)", err)

    def test_n5_mutante_titulo_normal_com_palavra_parecida_nao_e_descartado(self):
        normais = ["Dolly cart with wooden table.jpg", "Trailer park wooden fence table.jpg", "Efta table in oak.jpg"]
        itens, _, _ = self.buscar(com_titulos(*normais))
        self.assertEqual(len(itens), 3, [i["titulo"] for i in itens])

    def test_n5_sem_filtro_devolve_tudo(self):
        itens, _, _ = self.buscar(com_titulos(*(self.LIXO + self.BOM)), filtrar_acervo=False)
        self.assertEqual(len(itens), 6)

    def test_n5_autor_e_categoria_entram_na_consulta_enviada_a_commons(self):
        _, _, rede = self.buscar(GRAVADA, autor="Shixart1985", categoria="Wooden furniture")
        url = [u for u in rede.chamadas if "commons.wikimedia.org" in u][0]
        busca = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["gsrsearch"][0]
        self.assertIn("Shixart1985", busca)
        self.assertIn('incategory:"Wooden furniture"', busca)
        self.assertIn("solid wood dining table", busca)

    def test_n5_sem_autor_nem_categoria_a_consulta_continua_a_mesma(self):
        _, _, rede = self.buscar(GRAVADA)
        url = [u for u in rede.chamadas if "commons.wikimedia.org" in u][0]
        busca = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["gsrsearch"][0]
        self.assertEqual(busca, "solid wood dining table filetype:bitmap")

    def test_n5_n6_a_saida_traz_miniatura_de_500_px_e_a_versao_de_1920_quando_a_foto_tem_tamanho(self):
        itens, _, _ = self.buscar(GRAVADA)
        grande = [i for i in itens if i["largura"] >= 1920 and "/thumb/" in i["url"]][0]
        self.assertIn("/500px-", grande["thumbnail"])
        saida = mod.format_openverse([grande], "x", fonte="Wikimedia Commons")
        self.assertIn("Miniatura (500 px)", saida)
        self.assertIn("/500px-", saida)
        self.assertIn("1920 px", saida)
        self.assertIn("/1920px-", saida)
        self.assertIn("500, 960, 1280 ou 1920", saida)

    def test_n6_larguras_padrao_e_url_so_com_largura_valida(self):
        url = ("https://thumb.wikimedia.org/wikipedia/commons/thumb/5/57/Mesa.jpg/1280px-Mesa.jpg"
               "?utm_source=commons.wikimedia.org")
        self.assertEqual(mod.LARGURAS_COMMONS, (500, 960, 1280, 1920))
        self.assertIn("/1920px-Mesa.jpg", mod.url_commons_na_largura(url, 1920, 4000))
        self.assertIn("/500px-Mesa.jpg", mod.url_commons_na_largura(url, 500, 4000))
        self.assertIn("/500px-Mesa.jpg", mod.url_commons_na_largura(url, 480, 4000), "480 não existe: sobe para 500")
        self.assertIn("/1920px-Mesa.jpg", mod.url_commons_na_largura(url, 1500, 4000), "1500 não existe: sobe para 1920")
        # foto menor que a largura pedida: a Commons responde 400, então não se monta a URL
        self.assertEqual(mod.url_commons_na_largura(url, 1920, 1486), "")
        self.assertEqual(mod.url_commons_na_largura("https://upload.wikimedia.org/x/Mesa.webp", 500, 4000), "")


# ---- 3.5.10, achado P6: --type openverse que falha cai sozinho para a Commons e avisa ----
class OpenverseExplicitoCaiNaCommons(unittest.TestCase):
    def setUp(self):
        self._orig = (mod._abrir_url, mod.time.sleep, mod._imagem_esta_viva)

    def tearDown(self):
        mod._abrir_url, mod.time.sleep, mod._imagem_esta_viva = self._orig

    def instalar(self, rede):
        mod._abrir_url = rede.abrir
        mod.time.sleep = rede.dormir
        return rede

    def rodar_main(self, rede, *argv):
        self.instalar(rede)
        saida, err = io.StringIO(), io.StringIO()
        import sys
        velho = sys.argv
        sys.argv = ["assets-search.py", "woodworking workshop", *argv]
        try:
            with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(err):
                mod.main()
        finally:
            sys.argv = velho
        return saida.getvalue(), err.getvalue()

    def test_p6_type_openverse_com_conexao_recusada_cai_na_commons_e_avisa(self):
        rede = Rede(ConnectionRefusedError(61, "Connection refused"), [GRAVADA])
        saida, err = self.rodar_main(rede, "--type", "openverse", "-n", "3")
        self.assertTrue(any("commons.wikimedia.org" in u for u in rede.chamadas), "não tentou a Commons")
        self.assertIn("Rota que respondeu: Wikimedia Commons", saida)
        self.assertIn("Openverse não respondeu", saida)
        self.assertIn("tentando a Wikimedia Commons", err)
        self.assertNotIn("Nenhuma foto encontrada", saida)

    def test_p6_type_cc_tem_o_mesmo_comportamento(self):
        rede = Rede(urllib.error.URLError(ConnectionRefusedError(61, "Connection refused")), [GRAVADA])
        saida, _ = self.rodar_main(rede, "--type", "cc", "-n", "3")
        self.assertIn("Rota que respondeu: Wikimedia Commons", saida)

    def test_p6_mutante_openverse_respondendo_nao_chama_a_commons_nem_avisa_de_queda(self):
        ov = {"results": [{"id": "1", "title": "Foto", "url": "https://live.staticflickr.com/a.jpg", "creator": "Ana",
                           "license": "cc0", "license_version": "1.0", "width": 4000, "height": 3000}]}
        rede = Rede(ov, [])
        mod._imagem_esta_viva = lambda url, timeout=8: True
        saida, err = self.rodar_main(rede, "--type", "openverse", "-n", "3")
        self.assertFalse(any("commons.wikimedia.org" in u for u in rede.chamadas))
        self.assertIn("Rota que respondeu: Openverse", saida)
        self.assertNotIn("tentando a Wikimedia Commons", err)

    def test_p6_as_duas_rotas_fora_dizem_que_nenhuma_respondeu(self):
        rede = Rede(ConnectionRefusedError(61, "Connection refused"), [urllib.error.URLError("fora")])
        saida, err = self.rodar_main(rede, "--type", "openverse", "-n", "3")
        self.assertIn("Nenhuma foto encontrada", saida)
        self.assertIn("tentando a Wikimedia Commons", err)

    def test_p6_a_ajuda_do_sem_chave_diz_que_o_unsplash_nao_abre_por_script(self):
        texto = mod.show_sem_chave_resources()
        self.assertIn("Unsplash", texto)
        self.assertIn("307", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
