"""Folha de contato da busca de foto (`assets-search.py --folha`) e acentos da saída (achado A9).

Sem internet: um servidor HTTP local (127.0.0.1, porta livre) serve miniaturas PNG geradas na hora,
cada uma de uma cor sólida. Assim o teste prova a NUMERAÇÃO: a célula N da folha tem que ter a cor da
miniatura do item N. A fonte dos números é a padrão da PIL (nada de fonte de sistema).

Precisa de Pillow; sem ela o teste se declara pulado (PULADO), nunca passa calado.
"""
import contextlib
import importlib.util
import io
import os
import pathlib
import re
import sys
import tempfile
import threading
import unittest
import unittest.mock
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    from PIL import Image
except ImportError:
    print("PULADO: Pillow não instalada, a folha de contato não foi provada")
    sys.exit(0)

os.environ["no_proxy"] = "127.0.0.1,localhost"
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("assets_search", AQUI / "assets-search.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CORES = [(220, 30, 30), (30, 200, 40), (40, 60, 230), (230, 220, 20), (200, 40, 200), (20, 210, 210), (250, 140, 10)]


def png(cor, tamanho=(800, 600)):
    buf = io.BytesIO()
    Image.new("RGB", tamanho, cor).save(buf, "PNG")
    return buf.getvalue()


class Servidor:
    """Serve /m/<n>.png. `falhas` mapeia caminho -> lista de (status, cabecalhos) a devolver antes do sucesso."""

    def __init__(self):
        self.pedidos = []
        self.falhas = {}
        dono = self

        class H(BaseHTTPRequestHandler):
            def do_GET(self):
                dono.pedidos.append(self.path)
                fila = dono.falhas.get(self.path, [])
                if fila:
                    status, cab = fila.pop(0)
                    self.send_response(status)
                    for k, v in cab.items():
                        self.send_header(k, v)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                m = re.match(r"/m/(\d+)\.png", self.path)
                if not m:
                    self.send_response(404)
                    self.send_header("Content-Length", "0")
                    self.end_headers()
                    return
                corpo = png(CORES[int(m.group(1)) % len(CORES)])
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(corpo)))
                self.end_headers()
                self.wfile.write(corpo)

            def log_message(self, *a):
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.porta = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def url(self, n):
        return "http://127.0.0.1:%d/m/%d.png" % (self.porta, n)

    def parar(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def item(srv, n, titulo=None):
    return {
        "id": str(n), "titulo": titulo or "Foto %d" % n, "url": "http://exemplo.invalido/%d.jpg" % n, "thumbnail": srv.url(n),
        "autor": "Autor %d" % n, "autor_url": "", "licenca": "CC BY 4.0", "licenca_url": "https://creativecommons.org/licenses/by/4.0/",
        "largura": 1600, "altura": 900, "pagina_origem": "https://exemplo.invalido/p/%d" % n, "exige_credito": True,
        "credito": "\"Foto %d\" por Autor %d" % (n, n),
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.srv = Servidor()
        self.addCleanup(self.srv.parar)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.pasta = pathlib.Path(self.tmp.name) / "pasta com espaço çá"
        self.sono = []
        p = unittest.mock.patch.object(mod.time, "sleep", side_effect=lambda s: self.sono.append(s))
        p.start()
        self.addCleanup(p.stop)

    def centro(self, folha, numero):
        """Cor no meio da célula `numero` (1 a N), longe do selo do número."""
        cw, ch = mod.FOLHA_CELULA
        m = mod.FOLHA_MARGEM
        cols = folha.n_colunas
        idx = numero - 1
        x = m + (idx % cols) * (cw + m) + cw // 2
        y = m + (idx // cols) * (ch + m) + ch // 2
        return folha.img.getpixel((x, y))

    def abrir(self, caminho, colunas):
        im = Image.open(caminho).convert("RGB")
        return type("F", (), {"img": im, "n_colunas": colunas})


class Folha(Base):
    def test_a_celula_n_tem_a_miniatura_do_item_n_e_o_numero_n(self):
        itens = [item(self.srv, n) for n in (1, 2, 3, 4, 5)]
        destino = self.pasta / "fotos.png"
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            mod.gerar_folha(itens, "openverse", str(destino))
        self.assertTrue(destino.exists(), "a folha não foi gravada (pasta nova com espaço e acento)")
        f = self.abrir(destino, 3)
        for n in range(1, 6):
            # a miniatura do item n tem a cor CORES[n % 7]; a célula n tem que ter essa cor no meio
            self.assertEqual(self.centro(f, n), CORES[n % len(CORES)], "célula %d com a miniatura errada" % n)
        self.assertIn("Folha de contato:", saida.getvalue())
        self.assertIn("o número de cada uma é o da lista", saida.getvalue())

    def test_o_selo_de_cada_celula_e_o_numero_do_item(self):
        itens = [item(self.srv, n) for n in (1, 2, 3, 4)]
        destino = self.pasta / "selos.png"
        with contextlib.redirect_stdout(io.StringIO()):
            mod.gerar_folha(itens, "openverse", str(destino))
        f = self.abrir(destino, 3)
        cw, ch = mod.FOLHA_CELULA
        m = mod.FOLHA_MARGEM
        for numero in (1, 2, 3, 4):
            idx = numero - 1
            x = m + (idx % 3) * (cw + m)
            y = m + (idx // 3) * (ch + m)
            selo = mod._numero_grande(numero)
            esperado = Image.new("RGB", selo.size, CORES[numero % len(CORES)])
            esperado.paste(selo, (0, 0), selo)
            recorte = f.img.crop((x, y, x + selo.width, y + selo.height))
            self.assertTrue(list(recorte.getdata()) == list(esperado.getdata()), "selo da célula %d não é o número %d" % (numero, numero))
        # e o selo do 2 não serve de selo do 1
        um = mod._numero_grande(1)
        dois = mod._numero_grande(2)
        self.assertTrue(um.tobytes() != dois.tobytes())

    def test_o_selo_desenha_numeros_diferentes_e_10_e_mais_largo_que_1(self):
        cinza = mod._numero_grande(1)
        dois = mod._numero_grande(2)
        dez = mod._numero_grande(10)
        self.assertNotEqual(cinza.tobytes(), dois.tobytes())
        self.assertGreater(dez.width, cinza.width)
        self.assertGreaterEqual(cinza.height, 28, "o número ficou pequeno demais para ler na folha")
        # tem tinta branca de verdade (não é um quadrado vazio)
        brancos = sum(1 for px in cinza.getdata() if px[0] > 200)
        self.assertGreater(brancos, 20)

    def test_grade_tem_o_tamanho_certo_para_6_e_para_8_itens(self):
        for total, cols in ((6, 3), (8, 4)):
            destino = self.pasta / ("g%d.png" % total)
            mod.gerar_folha([item(self.srv, n) for n in range(1, total + 1)], "openverse", str(destino))
            im = Image.open(destino)
            cw, ch = mod.FOLHA_CELULA
            m = mod.FOLHA_MARGEM
            linhas = (total + cols - 1) // cols
            self.assertEqual(im.size, (cols * (cw + m) + m, linhas * (ch + m) + m))

    def test_pausa_entre_chamadas_antes_de_cada_miniatura(self):
        mod.gerar_folha([item(self.srv, n) for n in (1, 2, 3)], "openverse", str(self.pasta / "p.png"))
        pausas = [s for s in self.sono if s == mod.PAUSA_MINIATURA]
        self.assertEqual(len(pausas), 3, self.sono)

    def test_miniatura_da_commons_usa_a_pausa_longa_e_o_user_agent_da_commons(self):
        chamadas = []

        def abrir(req, timeout=20):
            chamadas.append((req.full_url, dict(req.header_items())))
            raise urllib.error.URLError("sem rede no teste")

        with unittest.mock.patch.object(mod, "_abrir_url", abrir):
            dados, motivo = mod._baixar_miniatura("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/X.jpg/500px-X.jpg")
        self.assertIsNone(dados)
        self.assertIn(mod.PAUSA_MINIATURA_COMMONS, self.sono)
        self.assertGreaterEqual(mod.PAUSA_MINIATURA_COMMONS, 1.0)
        self.assertEqual(chamadas[0][1].get("User-agent"), mod.COMMONS_USER_AGENT)

    def test_http_429_espera_o_retry_after_e_tenta_uma_vez(self):
        self.srv.falhas["/m/1.png"] = [(429, {"Retry-After": "7"})]
        dados, motivo = mod._baixar_miniatura(self.srv.url(1))
        self.assertTrue(dados and dados[:4] == b"\x89PNG", motivo)
        self.assertIn(7, self.sono)
        self.assertEqual(self.srv.pedidos.count("/m/1.png"), 2)

    def test_http_429_respeita_o_teto_de_espera_e_nao_insiste_mais_de_uma_vez(self):
        self.srv.falhas["/m/2.png"] = [(429, {"Retry-After": "9999"}), (429, {"Retry-After": "9999"}), (429, {})]
        dados, motivo = mod._baixar_miniatura(self.srv.url(2))
        self.assertIsNone(dados)
        self.assertIn("429", motivo)
        self.assertIn(mod.TETO_ESPERA_COMMONS, self.sono)
        self.assertEqual(self.srv.pedidos.count("/m/2.png"), 2, "só uma retentativa")

    def test_miniatura_que_falha_vira_celula_numerada_e_a_folha_sai_mesmo_assim(self):
        itens = [item(self.srv, 1), item(self.srv, 2), item(self.srv, 3)]
        itens[1]["thumbnail"] = "http://127.0.0.1:%d/nao-existe.png" % self.srv.porta
        destino = self.pasta / "f.png"
        err = io.StringIO()
        out = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            mod.gerar_folha(itens, "openverse", str(destino))
        self.assertTrue(destino.exists())
        self.assertIn("sem miniatura no item 2", err.getvalue())
        self.assertIn("Sem miniatura nos números: 2", out.getvalue())
        f = self.abrir(destino, 3)
        self.assertEqual(self.centro(f, 1), CORES[1])
        self.assertEqual(self.centro(f, 3), CORES[3])
        self.assertNotEqual(self.centro(f, 2), CORES[2])

    def test_urls_por_tipo(self):
        self.assertEqual(mod.urls_das_miniaturas([{"src": {"medium": "m", "large": "l"}}], "pexels-foto"), ["m"])
        self.assertEqual(mod.urls_das_miniaturas([{"video_pictures": [{"picture": "v"}]}], "pexels-video"), ["v"])
        self.assertEqual(mod.urls_das_miniaturas([{"thumbnail": "t", "url": "u"}, {"thumbnail": "", "url": "u2"}], "openverse"), ["t", "u2"])

    def test_main_com_folha_nao_muda_o_texto_da_busca_e_acrescenta_a_linha_da_folha(self):
        itens = [item(self.srv, n) for n in (1, 2, 3)]

        def roda(extra):
            out = io.StringIO()
            argv = ["assets-search.py", "mesa de madeira", "--type", "commons"] + extra
            with unittest.mock.patch.object(mod, "search_commons", lambda *a, **k: itens), \
                    unittest.mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(out):
                mod.main()
            return out.getvalue()

        sem = roda([])
        destino = self.pasta / "main.png"
        com = roda(["--folha", str(destino)])
        self.assertTrue(com.startswith(sem), "o texto da busca mudou com --folha")
        resto = com[len(sem):]
        self.assertIn("Folha de contato:", resto)
        self.assertTrue(destino.exists())
        for n in (1, 2, 3):
            self.assertIn("  %d. Foto %d" % (n, n), sem)

    def test_sem_resultado_nao_monta_folha_e_avisa(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            mod.gerar_folha([], "openverse", str(self.pasta / "vazia.png"))
        self.assertFalse((self.pasta / "vazia.png").exists())
        self.assertIn("não devolveu resultados", err.getvalue())


class Acentos(unittest.TestCase):
    """Achado A9: a saída imprimia "credito", "condicao" e "saida" sem acento."""

    PROIBIDAS = re.compile(r"\b(credito|creditos|condicao|saida|CREDITO|OBRIGATORIO|ATRIBUICAO|atribuicao|obrigacao|dimensao|disponiveis)\b")

    def _item(self):
        return {"id": "1", "titulo": "Mesa", "url": "http://x/y.jpg", "thumbnail": "", "autor": "Ana", "autor_url": "",
                "licenca": "CC BY 4.0", "licenca_url": "", "largura": 0, "altura": 0, "pagina_origem": "", "exige_credito": True,
                "credito": "x"}

    def test_a_lista_de_texto_sai_com_acento(self):
        texto = mod.format_openverse([self._item()], "mesa")
        self.assertIsNone(self.PROIBIDAS.search(texto), self.PROIBIDAS.search(texto) and self.PROIBIDAS.search(texto).group(0))
        for esperado in ("CRÉDITO OBRIGATÓRIO", "ATRIBUIÇÃO", "condição da licença", "crédito"):
            self.assertIn(esperado, texto)

    def test_aviso_de_fallback_e_a_licenca_sem_url_saem_com_acento(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            mod.print_aviso_fallback_openverse("teste")
        self.assertIn("saída", err.getvalue())
        self.assertIsNone(self.PROIBIDAS.search(err.getvalue()))
        sem_url = self._item()
        sem_url["licenca_url"] = ""
        self.assertIn("licença CC BY 4.0", mod._monta_credito(sem_url))

    def test_pexels_e_recursos_sem_chave_saem_com_acento(self):
        video = {"id": 1, "url": "u", "duration": 3, "width": 10, "height": 10, "user": {"name": "A"}, "video_files": [], "video_pictures": []}
        for texto in (mod.format_videos([video], "q"), mod.show_sem_chave_resources(),
                      mod.show_lottie_resources(""), mod.show_illustration_resources(""), mod.show_icon_resources(),
                      mod.show_background_resources()):
            achado = self.PROIBIDAS.search(texto)
            self.assertIsNone(achado, achado and achado.group(0))


if __name__ == "__main__":
    unittest.main()
