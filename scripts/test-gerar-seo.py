"""Controles do gerar-seo.py: cria robots.txt, sitemap.xml e 404.html na raiz do domínio, sem nunca sobrescrever.

Por que existe (27/10/2026, auditoria de SEO da sales.juliocouto.com.br): o robots.txt, o sitemap.xml e
qualquer URL inexistente devolviam a home com 200, porque os três arquivos não existiam. O gate-seo.py
cobra os três; este script os cria para quem ainda não os tem. O resultado tem que passar nas regras 13 a 15
do gate.
"""
import contextlib
import datetime
import importlib.util
import io
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent


def carregar(nome):
    spec = importlib.util.spec_from_file_location(nome.replace("-", "_"), AQUI / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


gerar = carregar("gerar-seo")
gate = carregar("gate-seo")
modelo = carregar("test-gate-seo")   # a página boa e as constantes do teste do gate

URL = "https://exemplo.com.br/"
EN_DASH, EM_DASH = chr(0x2013), chr(0x2014)   # por chr(): o hook de travessão barra o caractere escrito no arquivo


def rodar(argv):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        code = gerar.main(argv)
    return code, saida.getvalue()


class GerarSeo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dist = pathlib.Path(self.tmp.name) / "dist"
        self.dist.mkdir()
        (self.dist / "index.html").write_text(modelo.PAGINA_BOA, encoding="utf-8")

    def ler(self, nome, pasta=None):
        return ((pasta or self.dist) / nome).read_text(encoding="utf-8")

    def test_cria_os_tres_arquivos_e_passam_nas_regras_13_a_15_do_gate(self):
        code, out = rodar(["--dist", str(self.dist), "--url-final", URL])
        self.assertEqual(code, 0, out)
        for nome in ("robots.txt", "sitemap.xml", "404.html"):
            self.assertTrue((self.dist / nome).is_file(), nome)
            self.assertIn(f"criado: {self.dist / nome}", out)
        res = gate.Resultado()
        gate.checar_robots(self.dist, URL, res)
        gate.checar_sitemap(self.dist, URL, res)
        gate.checar_404(self.dist, URL, res)
        self.assertEqual(res.reprovas, [])
        self.assertEqual(res.pendencias, [])

    def test_a_dist_inteira_passa_no_gate_no_modo_dominio(self):
        for nome, conteudo in (("foto.webp", b"w"), ("og-image.jpg", b"j"), ("favicon.png", b"p")):
            (self.dist / nome).write_bytes(conteudo)
        self.assertEqual(rodar(["--dist", str(self.dist), "--url-final", URL])[0], 0)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = gate.main(["--dist", str(self.dist), "--url-final", URL])
        self.assertEqual(code, 0, saida.getvalue())

    def test_robots_libera_tudo_e_aponta_o_sitemap_absoluto(self):
        rodar(["--dist", str(self.dist), "--url-final", "https://exemplo.com.br/sobrai/"])
        txt = self.ler("robots.txt")
        self.assertIn("User-agent: *", txt)
        self.assertIn("Allow: /", txt)
        self.assertNotIn("Disallow: /\n", txt)
        self.assertIn("Sitemap: https://exemplo.com.br/sitemap.xml", txt)   # o sitemap fica na raiz do domínio

    def test_sitemap_tem_a_url_final_e_o_lastmod_de_hoje(self):
        rodar(["--dist", str(self.dist), "--url-final", URL])
        xml = self.ler("sitemap.xml")
        self.assertIn("<loc>https://exemplo.com.br/</loc>", xml)
        self.assertIn(f"<lastmod>{datetime.date.today().isoformat()}</lastmod>", xml)
        self.assertTrue(xml.startswith('<?xml version="1.0" encoding="UTF-8"?>'))

    def test_lastmod_vem_do_parametro_hoje(self):
        gerar.gerar(self.dist, URL, hoje="2026-10-27")
        self.assertIn("<lastmod>2026-10-27</lastmod>", self.ler("sitemap.xml"))

    def test_url_com_e_comercial_sai_escapada_no_xml(self):
        rodar(["--dist", str(self.dist), "--url-final", "https://exemplo.com.br/?a=1&b=2"])
        self.assertIn("a=1&amp;b=2", self.ler("sitemap.xml"))
        res = gate.Resultado()
        gate.checar_sitemap(self.dist, "https://exemplo.com.br/?a=1&b=2", res)
        self.assertEqual(res.reprovas, [])

    def test_404_curto_com_noindex_lang_titulo_e_link_para_a_home(self):
        rodar(["--dist", str(self.dist), "--url-final", URL])
        h = self.ler("404.html")
        self.assertIn('<html lang="pt-BR">', h)
        self.assertRegex(h, r'<meta name="robots" content="noindex')
        self.assertIn('<a href="/">', h)
        self.assertIn("<h1>Página não encontrada</h1>", h)
        self.assertLess(len(h), 2500)
        self.assertNotIn("<!--", h)           # o gate de publicação reprova comentário no HTML publicado

    def test_404_herda_a_marca_do_titulo_da_pagina_e_o_idioma(self):
        rodar(["--dist", str(self.dist), "--url-final", URL])
        self.assertIn("<title>Página não encontrada | Exemplo</title>", self.ler("404.html"))
        outra = pathlib.Path(self.tmp.name) / "outra"
        outra.mkdir()
        (outra / "index.html").write_text('<!doctype html><html lang="en"><head><title>Acme Studio</title></head><body></body></html>', encoding="utf-8")
        rodar(["--dist", str(outra), "--url-final", URL])
        h = self.ler("404.html", outra)
        self.assertIn('<html lang="en">', h)
        self.assertIn("<title>Página não encontrada | Acme Studio</title>", h)

    def test_404_sem_separador_longo_demais_ou_sem_titulo_fica_so_com_o_nome_da_pagina(self):
        outra = pathlib.Path(self.tmp.name) / "outra"
        outra.mkdir()
        (outra / "index.html").write_text("<html><head><title>" + "Um título comprido que não parece nome de marca nenhuma " * 2 + "</title></head></html>", encoding="utf-8")
        rodar(["--dist", str(outra), "--url-final", URL])
        self.assertIn("<title>Página não encontrada</title>", self.ler("404.html", outra))
        vazia = pathlib.Path(self.tmp.name) / "vazia"
        vazia.mkdir()
        rodar(["--dist", str(vazia), "--url-final", URL])
        self.assertIn("<title>Página não encontrada</title>", self.ler("404.html", vazia))
        self.assertIn('<html lang="pt-BR">', self.ler("404.html", vazia))

    def test_404_marca_com_html_e_com_travessao_sai_limpa(self):
        (self.dist / "index.html").write_text("<html lang='pt-BR'><head><title>Slogan que não é a marca " + EN_DASH + " Barros &amp; Filhos" + EM_DASH + "Oficina</title></head></html>", encoding="utf-8")
        rodar(["--dist", str(self.dist), "--url-final", URL])
        h = self.ler("404.html")
        self.assertNotIn(EM_DASH, h)
        self.assertNotIn(EN_DASH, h)
        self.assertIn("Oficina", h)

    def test_nunca_sobrescreve_e_diz_o_que_pulou(self):
        (self.dist / "robots.txt").write_text("User-agent: *\nDisallow: /privado\n", encoding="utf-8")
        (self.dist / "404.html").write_text("<h1>meu 404</h1>", encoding="utf-8")
        code, out = rodar(["--dist", str(self.dist), "--url-final", URL])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.ler("robots.txt"), "User-agent: *\nDisallow: /privado\n")
        self.assertEqual(self.ler("404.html"), "<h1>meu 404</h1>")
        self.assertIn(f"pulado, já existe: {self.dist / 'robots.txt'}", out)
        self.assertIn(f"pulado, já existe: {self.dist / '404.html'}", out)
        self.assertIn(f"criado: {self.dist / 'sitemap.xml'}", out)

    def test_rodar_duas_vezes_nao_muda_nada(self):
        rodar(["--dist", str(self.dist), "--url-final", URL])
        antes = {n: self.ler(n) for n in ("robots.txt", "sitemap.xml", "404.html")}
        code, out = rodar(["--dist", str(self.dist), "--url-final", URL])
        self.assertEqual(code, 0, out)
        self.assertEqual({n: self.ler(n) for n in antes}, antes)
        self.assertEqual(len(re.findall(r"pulado, já existe", out)), 3)

    def test_raiz_separada_da_dist(self):
        raiz = pathlib.Path(self.tmp.name) / "site-principal"
        raiz.mkdir()
        code, out = rodar(["--dist", str(self.dist), "--url-final", "https://exemplo.com.br/sobrai/", "--raiz", str(raiz)])
        self.assertEqual(code, 0, out)
        for nome in ("robots.txt", "sitemap.xml", "404.html"):
            self.assertTrue((raiz / nome).is_file(), nome)
            self.assertFalse((self.dist / nome).exists(), nome)

    def test_erros_de_uso_saem_com_2(self):
        self.assertEqual(rodar(["--dist", str(self.dist), "--url-final", "http://exemplo.com.br/"])[0], 2)
        self.assertEqual(rodar(["--dist", str(self.dist), "--url-final", "exemplo.com.br"])[0], 2)
        self.assertEqual(rodar(["--dist", "/pasta/que/nao/existe/mesmo", "--url-final", URL])[0], 2)
        self.assertEqual(rodar(["--dist", str(self.dist), "--url-final", URL, "--raiz", "/pasta/que/nao/existe/mesmo"])[0], 2)

    def test_pelo_lancador_de_verdade(self):
        r = subprocess.run([sys.executable, str(AQUI / "gerar-seo.py"), "--dist", str(self.dist), "--url-final", URL],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.dist / "sitemap.xml").is_file())
        sem = subprocess.run([sys.executable, str(AQUI / "gerar-seo.py"), "--dist", str(self.dist)],
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(sem.returncode, 2, sem.stdout + sem.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
