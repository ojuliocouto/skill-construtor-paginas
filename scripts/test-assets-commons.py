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


if __name__ == "__main__":
    unittest.main(verbosity=2)
