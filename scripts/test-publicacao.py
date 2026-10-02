"""Controles da pasta de publicação: só o que é página vai para o ar.

Auditoria da v3 (02/10/2026): a pasta da página tinha 94 arquivos e 18 MB, dos quais 17 eram
entrega. Publicada como estava, iam junto prints de 10 sites de terceiros, o briefing com as
pendências da cliente, a folha de contato das fotos, as fotos de origem, os gates e os JSON de
auditoria.
"""
import importlib.util
import io
import contextlib
import pathlib
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent


def carregar(nome):
    spec = importlib.util.spec_from_file_location(nome.replace("-", "_"), AQUI / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


montar = carregar("montar-dist")
gate = carregar("gate-publicacao")

HTML = """<!doctype html><html><head>
<link rel="icon" type="image/png" href="favicon.png">
<meta property="og:image" content="og-image.jpg">
<link rel="preload" href="fonts/f.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="estilo.css">
</head><body>
<img src="imagens/hero-640.webp" srcset="imagens/hero-640.webp 640w, imagens/hero-960.webp 960w" alt="x">
</body></html>"""


def projeto(raiz):
    r = pathlib.Path(raiz)
    arquivos = {
        "index.html": HTML,
        "estilo.css": "@font-face{src:url('fonts/f.woff2')}body{background:url(imagens/fundo.webp)}",
        "favicon.png": "png", "og-image.jpg": "jpg", "robots.txt": "User-agent: *",
        "fonts/f.woff2": "font", "imagens/hero-640.webp": "a", "imagens/hero-960.webp": "b",
        "imagens/fundo.webp": "c",
        # o que NUNCA pode subir
        "referencias/01-site-dobra.png": "print de terceiro", "referencias/referencias.json": "{}",
        "evidencias/briefing.md": "pendências da cliente", "gates/lighthouse-mobile.json": "{}",
        "imagens/_hero-src.jpg": "origem", "imagens/contato.jpg": "folha de contato",
        "imagens/LICENCAS.md": "licenças", "tailwind.config.js": "module.exports={}",
        "_input.css": "@tailwind base;", ".wave-auditoria.json": "{}", "prova/prova-desktop.png": "p",
    }
    for nome, conteudo in arquivos.items():
        p = r / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(conteudo, encoding="utf-8")
    return r


def rodar_gate(pasta):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        code = gate.main(["--dist", str(pasta)])
    return code, saida.getvalue()


class Publicacao(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.proj = projeto(self.tmp.name)

    def test_montar_dist_leva_so_o_referenciado(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(montar.main(["--projeto", str(self.proj)]), 0)
        dist = self.proj / "dist"
        tem = sorted(str(p.relative_to(dist)) for p in dist.rglob("*") if p.is_file())
        self.assertEqual(tem, sorted(["index.html", "estilo.css", "favicon.png", "og-image.jpg", "robots.txt",
                                      "fonts/f.woff2", "imagens/hero-640.webp", "imagens/hero-960.webp",
                                      "imagens/fundo.webp"]))
        code, out = rodar_gate(dist)
        self.assertEqual(code, 0, out)

    def test_gate_reprova_a_pasta_do_projeto_inteira(self):
        code, out = rodar_gate(self.proj)
        self.assertEqual(code, 1)
        for item in ("referencias", "evidencias", "gates", "prova", "briefing", ".json", "_hero-src.jpg",
                     "contato.jpg", "tailwind.config.js", ".wave-auditoria.json"):
            self.assertIn(item, out, item)

    def test_gate_reprova_arquivo_que_a_pagina_nao_usa(self):
        with contextlib.redirect_stdout(io.StringIO()):
            montar.main(["--projeto", str(self.proj)])
        (self.proj / "dist" / "imagens" / "sobra.png").write_text("x")
        code, out = rodar_gate(self.proj / "dist")
        self.assertEqual(code, 1)
        self.assertIn("sobra.png", out)

    def test_gate_reprova_sem_dist(self):
        code, out = rodar_gate(self.proj / "dist")
        self.assertEqual(code, 1)
        self.assertIn("não existe", out)

    def test_css_em_linha_remove_o_bloqueio_e_reescreve_url(self):
        (self.proj / "css").mkdir()
        (self.proj / "css" / "a.css").write_text("body{background:url('../imagens/fundo.webp')}")
        (self.proj / "index.html").write_text(HTML.replace("estilo.css", "css/a.css"))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(montar.main(["--projeto", str(self.proj), "--css-em-linha"]), 0)
        html = (self.proj / "dist" / "index.html").read_text()
        self.assertNotIn('rel="stylesheet"', html)
        self.assertIn("<style>", html)
        self.assertIn("url('imagens/fundo.webp')", html)
        self.assertTrue((self.proj / "dist" / "imagens" / "fundo.webp").exists())
        self.assertFalse((self.proj / "dist" / "css" / "a.css").exists())
        code, out = rodar_gate(self.proj / "dist")
        self.assertEqual(code, 0, out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
