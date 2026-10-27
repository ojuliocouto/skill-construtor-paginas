"""Controles do gate de SEO: o que um buscador, um buscador de IA e um link compartilhado leem sem executar JavaScript.

Auditoria de SEO de 27/10/2026 em duas páginas reais da IAutomate (sales.juliocouto.com.br e
juliocouto.com.br/sobrai/): as duas aparecem aqui em miniatura ("sales antes" e "SobrAI antes") e
têm que reprovar com a mensagem certa. A página boa passa em modo DOMÍNIO, o mais exigente.

Portátil: só biblioteca padrão do Python, nenhum navegador. As páginas são montadas em código,
numa pasta temporária.
"""
import base64
import contextlib
import importlib.util
import io
import json
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


gate = carregar("gate-seo")

URL = "https://exemplo.com.br/"
BASE = "automação atendimento clientes mensagem resultado agenda equipe processo tempo venda".split()


def palavras(n, marca="p"):
    """n palavras visíveis, todas diferentes entre si (a conta é por palavra, não por frase)."""
    return " ".join(f"{BASE[i % len(BASE)]}{marca}{i}" for i in range(n))


LD_BOM = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Organization", "name": "Exemplo"},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": "Quanto custa a automação?",
             "acceptedAnswer": {"@type": "Answer", "text": "A partir de R$ 9.997 por ano."}}]},
        {"@type": "Product", "name": "Plano anual",
         "offers": {"@type": "Offer", "price": "9997", "priceCurrency": "BRL"}},
    ],
}

RODAPE = '<footer><a href="/privacidade.html">Política de privacidade</a></footer>'
RODAPE_SEM_PRIVACIDADE = '<footer><a href="/termos.html">Termos de uso</a></footer>'

PAGINA_BOA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atendimento no WhatsApp para clínicas | Exemplo</title>
<meta name="description" content="Automatize o primeiro atendimento da sua clínica no WhatsApp e agende consultas sem perder nenhum paciente.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="@@URL@@">
<meta property="og:title" content="Atendimento no WhatsApp para clínicas">
<meta property="og:url" content="@@URL@@">
<meta property="og:image" content="@@URL@@og-image.jpg">
<link rel="icon" href="favicon.png">
<script type="application/ld+json">@@LD@@</script>
</head>
<body>
<h1>Atendimento no WhatsApp que agenda sozinho</h1>
<p>@@P1@@</p>
<h2>Como funciona</h2>
<p>@@P2@@</p>
<h3>Primeiro passo</h3>
<p>@@P3@@</p>
<h2>Perguntas frequentes</h2>
<details><summary>Quanto custa a automação?</summary><p>A partir de R$ 9.997 por ano.</p></details>
<img src="foto.webp" alt="Equipe da clínica" width="800" height="600">
@@RODAPE@@
</body>
</html>
""".replace("@@LD@@", json.dumps(LD_BOM, ensure_ascii=False)).replace("@@RODAPE@@", RODAPE) \
   .replace("@@P1@@", palavras(120, "a")).replace("@@P2@@", palavras(120, "b")).replace("@@P3@@", palavras(120, "c")) \
   .replace("@@URL@@", URL)

ROBOTS_BOM = "User-agent: *\nAllow: /\nSitemap: https://exemplo.com.br/sitemap.xml\n"
SITEMAP_BOM = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               '<url><loc>https://exemplo.com.br/</loc><lastmod>2026-10-27</lastmod></url></urlset>\n')
P404_BOM = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Página não encontrada | Exemplo</title>'
            '<meta name="robots" content="noindex"></head><body><h1>Página não encontrada</h1><a href="/">Voltar</a></body></html>\n')


def escrever(pasta, arquivos):
    for nome, conteudo in arquivos.items():
        p = pathlib.Path(pasta) / nome
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(conteudo, bytes):
            p.write_bytes(conteudo)
        else:
            p.write_text(conteudo, encoding="utf-8")


def rodar(argv):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        code = gate.main(argv)
    return code, saida.getvalue()


def tira_ld(h):
    return re.sub(r'<script type="application/ld\+json">.*?</script>', "", h, flags=re.S)


def troca_ld(h, novo):
    return re.sub(r'(<script type="application/ld\+json">).*?(</script>)', lambda m: m.group(1) + novo + m.group(2), h, flags=re.S)


def troca_description(h, texto):
    return re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + texto, h)


class Base(unittest.TestCase):
    """Uma dist boa por teste; cada teste estraga UMA coisa e confere a mensagem."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dist = pathlib.Path(self.tmp.name) / "dist"
        escrever(self.dist, {
            "index.html": PAGINA_BOA, "foto.webp": b"w" * 2000, "og-image.jpg": b"j" * 2000, "favicon.png": b"p" * 100,
            "robots.txt": ROBOTS_BOM, "sitemap.xml": SITEMAP_BOM, "404.html": P404_BOM,
        })

    def html(self, f):
        """Troca o index.html pelo resultado de f(html)."""
        p = self.dist / "index.html"
        p.write_text(f(p.read_text(encoding="utf-8")), encoding="utf-8")

    def gate(self, url=URL, extra=()):
        argv = ["--dist", str(self.dist), *extra]
        if url:
            argv += ["--url-final", url]
        return rodar(argv)

    def linhas(self, out, prefixo):
        return [l for l in out.splitlines() if l.startswith(prefixo)]

    def reprova(self, *trechos, **kw):
        """Sai 1 e existe UMA linha REPROVA: com todos os trechos."""
        code, out = self.gate(**kw)
        self.assertEqual(code, 1, out)
        achadas = [l for l in self.linhas(out, "REPROVA:") if all(t in l for t in trechos)]
        self.assertTrue(achadas, f"nenhuma linha REPROVA: com {trechos!r}\n{out}")
        return out

    def passa(self, **kw):
        code, out = self.gate(**kw)
        self.assertEqual(code, 0, out)
        return out


class PaginaBoa(Base):
    def test_pagina_boa_passa_no_modo_dominio(self):
        out = self.passa()
        self.assertEqual(self.linhas(out, "REPROVA:"), [])
        resumo = self.linhas(out, "SEO: gate-seo")
        self.assertEqual(len(resumo), 1, out)
        self.assertIn("passa no modo domínio", resumo[0])
        self.assertIn("palavras no HTML cru 386", resumo[0])  # 360 do corpo + títulos, pergunta, resposta e rodapé
        self.assertIn("pendências: nenhuma", resumo[0])

    def test_a_linha_de_contagem_nao_usa_a_frase_da_reprovacao(self):
        # a linha "Conserto:" do rodar-gates procura "palavras visíveis" no laudo: a contagem de uma página BOA não pode disparar o conserto de pré-render
        out = self.passa()
        self.assertIn("index.html: 386 palavras no HTML cru", out)
        self.assertNotIn("palavras visíveis", out)

    def test_pagina_boa_passa_no_modo_previa_sem_url_final(self):
        out = self.passa(url=None)
        self.assertIn("passa no modo prévia", out)


class HtmlCru(Base):
    def sem_corpo(self, h):
        return h.replace(palavras(120, "a"), "pouco texto").replace(palavras(120, "b"), "").replace(palavras(120, "c"), "")

    def test_regra1_menos_de_300_palavras_reprova_com_o_numero(self):
        self.html(self.sem_corpo)
        out = self.reprova("palavras visíveis", "mínimo 300", "index.html")
        self.assertRegex(out, r"REPROVA: HTML cru com \d+ palavras visíveis")

    def test_regra1_script_style_noscript_e_template_nao_contam(self):
        lixo = palavras(500, "z")
        self.html(lambda h: self.sem_corpo(h).replace(
            "</body>", f"<script>var a='{lixo}'</script><style>/*{lixo}*/</style><noscript>{lixo}</noscript><template>{lixo}</template></body>"))
        self.reprova("palavras visíveis")

    def test_regra1_spa_com_root_vazio_cita_o_root(self):
        self.html(lambda h: h.split("<body>")[0] + '<body><div id="root"></div><script src="/app.js"></script></body></html>')
        self.reprova("SPA com #root vazio")

    def test_regra1_app_vazio_tambem(self):
        self.html(lambda h: h.split("<body>")[0] + '<body><div id="app"> </div></body></html>')
        self.reprova("SPA com #root vazio")

    def test_regra1_o_titulo_da_head_nao_conta_como_texto_visivel(self):
        self.html(self.sem_corpo)
        code, out = self.gate()
        n = int(re.search(r"(\d+) palavras visíveis", out).group(1))
        self.assertLess(n, 40, out)


class MetaDoHead(Base):
    TITULO = "Atendimento no WhatsApp para clínicas | Exemplo"

    def test_regra2_sem_lang_reprova(self):
        self.html(lambda h: h.replace('<html lang="pt-BR">', "<html>"))
        self.reprova("<html lang>")

    def test_regra3_titulo_ausente(self):
        self.html(lambda h: h.replace(f"<title>{self.TITULO}</title>", ""))
        self.reprova("<title> ausente")

    def test_regra3_titulo_curto_e_longo_citam_o_tamanho(self):
        self.html(lambda h: h.replace(self.TITULO, "Curto"))
        out = self.reprova("<title>")
        self.assertIn("5 caracteres", out)
        self.setUp()
        self.html(lambda h: h.replace(self.TITULO, "T" * 66))
        out = self.reprova("<title>")
        self.assertIn("66 caracteres", out)

    def test_regra3_limites_de_15_e_65_passam(self):
        for n in (15, 65):
            self.setUp()
            self.html(lambda h: h.replace(self.TITULO, "T" * n))
            self.passa()

    def test_regra4_description_ausente(self):
        self.html(lambda h: re.sub(r'<meta name="description"[^>]*>', "", h))
        self.reprova("meta description ausente")

    def test_regra4_description_curta_e_longa_citam_o_tamanho(self):
        self.html(lambda h: troca_description(h, "curta demais"))
        out = self.reprova("meta description")
        self.assertIn("12 caracteres", out)
        self.setUp()
        self.html(lambda h: troca_description(h, "d" * 161))
        out = self.reprova("meta description")
        self.assertIn("161 caracteres", out)

    def test_regra4_limites_de_70_e_160_passam(self):
        for n in (70, 160):
            self.setUp()
            self.html(lambda h: troca_description(h, "d" * n))
            self.passa()

    def test_regra5_noindex_e_nofollow_reprovam_no_dominio(self):
        self.html(lambda h: h.replace("index, follow", "noindex, nofollow"))
        out = self.reprova("meta robots", "noindex")
        self.assertIn("nofollow", out)

    def test_regra5_so_nofollow_tambem_reprova(self):
        self.html(lambda h: h.replace("index, follow", "index, nofollow"))
        self.reprova("meta robots", "nofollow")

    def test_regra5_noindex_na_previa_e_pendencia_que_sai_no_dominio_final(self):
        self.html(lambda h: h.replace("index, follow", "noindex, nofollow"))
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        pend = self.linhas(out, "PENDÊNCIA:")
        self.assertTrue(any("noindex" in l and "domínio final" in l for l in pend), out)


class Canonical(Base):
    CANON = f'<link rel="canonical" href="{URL}">'

    def test_regra6_sem_canonical_reprova_no_dominio_e_e_pendencia_na_previa(self):
        self.html(lambda h: h.replace(self.CANON, ""))
        self.reprova("canonical ausente")
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("canonical" in l for l in self.linhas(out, "PENDÊNCIA:")), out)

    def test_regra6_canonical_relativo_ou_http_reprova(self):
        self.html(lambda h: h.replace(self.CANON, '<link rel="canonical" href="/">'))
        self.reprova("canonical", "https://")
        self.setUp()
        self.html(lambda h: h.replace(self.CANON, '<link rel="canonical" href="http://exemplo.com.br/">'))
        self.reprova("canonical", "https://")

    def test_regra6_canonical_diferente_da_url_final_reprova(self):
        self.html(lambda h: h.replace(self.CANON, '<link rel="canonical" href="https://outro.com.br/">'))
        out = self.reprova("diferente da URL final")
        self.assertIn("outro.com.br", out)

    def test_regra6_so_a_barra_final_difere_e_passa(self):
        self.html(lambda h: h.replace(self.CANON, '<link rel="canonical" href="https://exemplo.com.br">'))
        self.html(lambda h: h.replace(f'<meta property="og:url" content="{URL}">', '<meta property="og:url" content="https://exemplo.com.br">'))
        self.passa()

    def test_regra6_og_url_diferente_do_canonical_reprova(self):
        self.html(lambda h: h.replace(f'<meta property="og:url" content="{URL}">', '<meta property="og:url" content="https://exemplo.com.br/outra">'))
        self.reprova("og:url")

    def test_regra6_sem_og_url_passa(self):
        self.html(lambda h: h.replace(f'<meta property="og:url" content="{URL}">', ""))
        self.passa()

    def test_regra7_og_image_ausente_reprova_no_dominio_e_na_previa(self):
        self.html(lambda h: h.replace(f'<meta property="og:image" content="{URL}og-image.jpg">', ""))
        self.reprova("og:image ausente")
        code, out = self.gate(url=None)
        self.assertEqual(code, 1, out)
        self.assertIn("og:image ausente", out)

    def test_regra7_og_image_relativa_reprova_no_dominio_e_e_pendencia_na_previa(self):
        self.html(lambda h: h.replace(f'content="{URL}og-image.jpg"', 'content="og-image.jpg"'))
        self.reprova("og:image", "https://")
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("og:image" in l for l in self.linhas(out, "PENDÊNCIA:")), out)

    def test_regra7_og_image_em_http_reprova(self):
        self.html(lambda h: h.replace(f'content="{URL}og-image.jpg"', 'content="http://exemplo.com.br/og-image.jpg"'))
        self.reprova("og:image", "https://")


class Titulos(Base):
    def test_regra8_dois_h1(self):
        self.html(lambda h: h.replace("<h2>Como funciona</h2>", "<h1>Outro título</h1>"))
        self.reprova("mais de um <h1>", "2 encontrados")

    def test_regra8_nenhum_h1_ou_h1_vazio(self):
        self.html(lambda h: h.replace("<h1>Atendimento no WhatsApp que agenda sozinho</h1>", ""))
        self.reprova("nenhum <h1> com texto")
        self.setUp()
        self.html(lambda h: h.replace("<h1>Atendimento no WhatsApp que agenda sozinho</h1>", "<h1> </h1>"))
        self.reprova("nenhum <h1> com texto")

    def test_regra8_salto_h2_para_h4_cita_a_sequencia_e_o_ponto(self):
        self.html(lambda h: h.replace("<h3>Primeiro passo</h3>", "<h4>Primeiro passo</h4>"))
        out = self.reprova("h2→h4")
        self.assertIn("h1 h2 h4", out)
        self.assertIn("Primeiro passo", out)

    def test_regra8_salto_h1_para_h3(self):
        self.html(lambda h: h.replace("<h2>Como funciona</h2>", "<h3>Como funciona</h3>"))
        self.reprova("h1→h3")

    def test_regra8_subir_de_nivel_e_livre(self):
        self.html(lambda h: h.replace("<h2>Perguntas frequentes</h2>", "<h4>x</h4><h2>Perguntas frequentes</h2>").replace(
            "<h3>Primeiro passo</h3>", "<h3>Primeiro passo</h3><h4>Detalhe</h4>"))
        self.passa()


class JsonLd(Base):
    def test_regra9_sem_json_ld_reprova(self):
        self.html(tira_ld)
        self.reprova("JSON-LD ausente")

    def test_regra9_json_invalido_reprova(self):
        self.html(lambda h: troca_ld(h, '{"@type": "Organization", }'))
        self.reprova("JSON-LD inválido")

    def test_regra9_json_valido_sem_type_reprova(self):
        self.html(lambda h: troca_ld(h, '{"name": "x"}'))
        self.reprova("JSON-LD sem @type")

    def test_regra9_aceita_type_solto_sem_graph(self):
        self.html(lambda h: troca_ld(h, '{"@context":"https://schema.org","@type":"Organization","name":"Exemplo"}'))
        self.passa()

    def test_regra9_pergunta_do_faq_ausente_no_texto_visivel_reprova(self):
        self.html(lambda h: h.replace("<summary>Quanto custa a automação?</summary>", "<summary>Quanto custa?</summary>"))
        out = self.reprova("FAQPage")
        self.assertIn("Quanto custa a automação?", out)

    def test_regra9_pergunta_com_espaco_nao_separavel_casa(self):
        self.html(lambda h: h.replace("<summary>Quanto custa a automação?</summary>", "<summary>Quanto&nbsp;custa  a\n automação?</summary>"))
        self.passa()

    def test_regra9_pergunta_so_dentro_de_noscript_nao_conta(self):
        self.html(lambda h: h.replace("<summary>Quanto custa a automação?</summary>", "<summary>Preço</summary><noscript>Quanto custa a automação?</noscript>"))
        self.reprova("FAQPage")

    def test_regra9_preco_do_offer_ausente_reprova(self):
        self.html(lambda h: h.replace("R$ 9.997", "R$ 8.000"))
        out = self.reprova("Offer.price")
        self.assertIn("9997", out)

    def test_regra9_preco_casa_em_forma_brasileira(self):
        for texto in ("R$ 9.997", "R$ 9997", "R$ 9.997,00", "R$9.997"):
            self.setUp()
            self.html(lambda h: h.replace("R$ 9.997", texto))
            self.passa()

    def test_regra9_preco_1500_casa_com_1_500(self):
        self.html(lambda h: h.replace('"price": "9997"', '"price": "1500"').replace("R$ 9.997", "R$ 1.500"))
        self.passa()

    def test_regra9_preco_numero_no_json_tambem(self):
        self.html(lambda h: h.replace('"price": "9997"', '"price": 9997'))
        self.passa()

    def test_regra9_preco_9997_nao_casa_dentro_de_19997(self):
        self.html(lambda h: h.replace("R$ 9.997", "R$ 19.997"))
        self.reprova("Offer.price")

    def test_regra9_preco_com_centavos(self):
        self.html(lambda h: h.replace('"price": "9997"', '"price": "1499.90"').replace("R$ 9.997", "R$ 1.499,90"))
        self.passa()
        self.html(lambda h: h.replace("R$ 1.499,90", "R$ 1.499"))
        self.reprova("Offer.price")

    def test_regra9_preco_que_nao_e_numero_reprova(self):
        self.html(lambda h: h.replace('"price": "9997"', '"price": "sob consulta"'))
        self.reprova("Offer.price", "sob consulta")


class Imagens(Base):
    def test_regra10_img_sem_alt(self):
        self.html(lambda h: h.replace('alt="Equipe da clínica" ', ""))
        self.reprova("<img> sem alt", "foto.webp")

    def test_regra10_img_sem_width_ou_sem_height(self):
        self.html(lambda h: h.replace(' width="800" height="600"', ""))
        self.reprova("sem width e height", "foto.webp")
        self.setUp()
        self.html(lambda h: h.replace(' height="600"', ""))
        self.reprova("sem width e height", "falta: height")

    def test_regra10_alt_vazio_e_valido_para_imagem_decorativa(self):
        self.html(lambda h: h.replace('alt="Equipe da clínica"', 'alt=""'))
        self.passa()

    def test_regra10_data_uri_acima_de_20kb_reprova_com_o_tamanho(self):
        grande = base64.b64encode(b"\x89PNG" + b"a" * 30000).decode()
        self.html(lambda h: h.replace("</body>", f'<img src="data:image/png;base64,{grande}" alt="" width="10" height="10"></body>'))
        out = self.reprova("data URI")
        self.assertIn("29,3 KB", out)

    def test_regra10_data_uri_pequeno_e_unico_passa(self):
        pequeno = base64.b64encode(b"\x89PNG" + b"a" * 3000).decode()
        self.html(lambda h: h.replace("</body>", f'<img src="data:image/png;base64,{pequeno}" alt="" width="10" height="10"></body>'))
        self.passa()

    def test_regra10_mesmo_data_uri_repetido_cita_os_bytes(self):
        medio = base64.b64encode(b"\x89PNG" + b"b" * 12000).decode()  # 11,7 KB: abaixo do limite de um só
        tag = f'<img src="data:image/png;base64,{medio}" alt="" width="10" height="10">'
        self.html(lambda h: h.replace("</body>", tag * 3 + "</body>"))
        out = self.reprova("repetido 3 vezes")
        self.assertIn("11,7 KB cada", out)
        self.assertIn("35,2 KB no total", out)

    def test_regra10_data_uri_no_css_em_linha_conta_igual(self):
        grande = base64.b64encode(b"\x89PNG" + b"a" * 30000).decode()
        self.html(lambda h: h.replace("</head>", f"<style>.a{{background:url(data:image/png;base64,{grande})}}</style></head>"))
        self.reprova("data URI")


class Peso(Base):
    def test_regra11_index_acima_de_300kb_reprova(self):
        self.html(lambda h: h.replace("</body>", "<!--" + "x" * 310_000 + "--></body>"))
        out = self.reprova("limite de 300 KB")
        self.assertRegex(out, r"3\d\d,\d KB")

    def test_regra11_imagem_local_acima_de_500kb_reprova_mesmo_em_webp(self):
        (self.dist / "foto.webp").write_bytes(b"w" * 600_000)
        self.reprova("foto.webp", "limite de 500 KB")

    def test_regra11_png_entre_200_e_500kb_so_avisa_para_converter(self):
        (self.dist / "foto.png").write_bytes(b"p" * 300_000)
        self.html(lambda h: h.replace('src="foto.webp"', 'src="foto.png"'))
        code, out = self.gate()
        self.assertEqual(code, 0, out)
        avisos = self.linhas(out, "AVISO:")
        self.assertTrue(any("foto.png" in l and "WebP/AVIF" in l for l in avisos), out)

    def test_regra11_png_acima_de_500kb_reprova_e_manda_converter(self):
        (self.dist / "foto.png").write_bytes(b"p" * 600_000)
        self.html(lambda h: h.replace('src="foto.webp"', 'src="foto.png"'))
        self.reprova("foto.png", "limite de 500 KB", "WebP/AVIF")

    def test_regra11_imagem_pelo_srcset_poster_e_og_image_local_entram_na_conta(self):
        (self.dist / "grande.webp").write_bytes(b"g" * 600_000)
        self.html(lambda h: h.replace('<img src="foto.webp"', '<img srcset="grande.webp 1200w, foto.webp 400w" src="foto.webp"'))
        self.reprova("grande.webp", "limite de 500 KB")
        self.setUp()
        (self.dist / "capa.jpg").write_bytes(b"c" * 600_000)
        self.html(lambda h: h.replace("</body>", '<video poster="capa.jpg" muted></video></body>'))
        self.reprova("capa.jpg", "limite de 500 KB")
        self.setUp()
        (self.dist / "og-local.jpg").write_bytes(b"o" * 600_000)
        self.html(lambda h: h.replace(f'content="{URL}og-image.jpg"', 'content="og-local.jpg"'))
        self.reprova("og-local.jpg", "limite de 500 KB")

    def test_regra11_video_acima_de_1mb_com_autoplay_sem_preload_none_reprova(self):
        (self.dist / "hero.mp4").write_bytes(b"v" * 3_800_000)
        self.html(lambda h: h.replace("</body>", '<video src="hero.mp4" autoplay muted loop playsinline></video></body>'))
        out = self.reprova("vídeo", "hero.mp4", "3,6 MB")
        self.assertIn("LCP no celular", out)
        self.assertIn("sales 27/10", out)

    def test_regra11_video_com_preload_none_sem_autoplay_ou_pequeno_passa(self):
        (self.dist / "hero.mp4").write_bytes(b"v" * 3_800_000)
        self.html(lambda h: h.replace("</body>", '<video src="hero.mp4" autoplay muted preload="none"></video></body>'))
        self.passa()
        self.setUp()
        (self.dist / "hero.mp4").write_bytes(b"v" * 3_800_000)
        self.html(lambda h: h.replace("</body>", '<video src="hero.mp4" controls></video></body>'))
        self.passa()
        self.setUp()
        (self.dist / "hero.mp4").write_bytes(b"v" * 900_000)
        self.html(lambda h: h.replace("</body>", '<video autoplay muted><source src="hero.mp4" type="video/mp4"></video></body>'))
        self.passa()

    def test_regra11_video_pelo_source_dentro_do_video_tambem(self):
        (self.dist / "hero.mp4").write_bytes(b"v" * 3_800_000)
        self.html(lambda h: h.replace("</body>", '<video autoplay muted><source src="hero.mp4" type="video/mp4"></video></body>'))
        self.reprova("vídeo", "hero.mp4")


class Fontes(Base):
    FONTE = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">'

    def test_regra12_google_fonts_bloqueante_so_avisa(self):
        self.html(lambda h: h.replace("</head>", self.FONTE + "</head>"))
        code, out = self.gate()
        self.assertEqual(code, 0, out)
        self.assertTrue(any("Google Fonts" in l and "render-blocking" in l for l in self.linhas(out, "AVISO:")), out)

    def test_regra12_media_print_com_onload_ou_preload_nao_avisa(self):
        carregada = self.FONTE.replace(">", ' media="print" onload="this.media=\'all\'">', 1)
        self.html(lambda h: h.replace("</head>", carregada + "</head>"))
        self.assertEqual(self.linhas(self.passa(), "AVISO:"), [])
        self.setUp()
        pre = '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap">'
        self.html(lambda h: h.replace("</head>", pre + self.FONTE + "</head>"))
        self.assertEqual(self.linhas(self.passa(), "AVISO:"), [])


class ArquivosDaRaiz(Base):
    def test_regra13_sem_robots_reprova(self):
        (self.dist / "robots.txt").unlink()
        self.reprova("robots.txt ausente")

    def test_regra13_robots_que_e_html_reprova(self):
        (self.dist / "robots.txt").write_text(PAGINA_BOA, encoding="utf-8")
        self.reprova("robots.txt é HTML")

    def test_regra13_disallow_total_para_todos_reprova_no_dominio_e_e_pendencia_na_previa(self):
        (self.dist / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
        self.reprova("Disallow: /")
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("Disallow: /" in l for l in self.linhas(out, "PENDÊNCIA:")), out)

    def test_regra13_disallow_de_pasta_ou_de_outro_robo_passa(self):
        (self.dist / "robots.txt").write_text(ROBOTS_BOM + "User-agent: *\nDisallow: /admin\nUser-agent: GPTBot\nDisallow: /\n", encoding="utf-8")
        self.passa()

    def test_regra13_allow_raiz_junto_do_disallow_nao_e_sozinho(self):
        (self.dist / "robots.txt").write_text("User-agent: *\nDisallow: /\nAllow: /\nSitemap: https://exemplo.com.br/sitemap.xml\n", encoding="utf-8")
        self.passa()

    def test_regra13_sem_linha_sitemap_absoluta_reprova_no_dominio_mas_nao_na_previa(self):
        (self.dist / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
        self.reprova("Sitemap:")
        (self.dist / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: /sitemap.xml\n", encoding="utf-8")
        self.reprova("Sitemap:")
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)

    def test_regra14_sem_sitemap_reprova_no_dominio_e_e_pendencia_na_previa(self):
        (self.dist / "sitemap.xml").unlink()
        self.reprova("sitemap.xml ausente")
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("sitemap.xml" in l for l in self.linhas(out, "PENDÊNCIA:")), out)

    def test_regra14_sitemap_html_ou_xml_quebrado_ou_sem_urlset_reprova(self):
        (self.dist / "sitemap.xml").write_text(PAGINA_BOA, encoding="utf-8")
        self.reprova("sitemap.xml não é XML válido")
        (self.dist / "sitemap.xml").write_text("<urlset><url></urlset>", encoding="utf-8")
        self.reprova("sitemap.xml não é XML válido")
        (self.dist / "sitemap.xml").write_text('<?xml version="1.0"?><feed><loc>https://exemplo.com.br/</loc></feed>', encoding="utf-8")
        self.reprova("sitemap.xml sem <urlset>")

    def test_regra14_sitemap_sem_a_url_final_reprova_no_dominio(self):
        (self.dist / "sitemap.xml").write_text(SITEMAP_BOM.replace("https://exemplo.com.br/", "https://outro.com.br/"), encoding="utf-8")
        out = self.reprova("não tem a URL final")
        self.assertIn("https://exemplo.com.br/", out)

    def test_regra14_url_final_sem_barra_no_loc_passa(self):
        (self.dist / "sitemap.xml").write_text(SITEMAP_BOM.replace("https://exemplo.com.br/<", "https://exemplo.com.br<"), encoding="utf-8")
        self.passa()

    def test_regra14_sitemap_com_doctype_reprova(self):
        (self.dist / "sitemap.xml").write_text('<?xml version="1.0"?><!DOCTYPE urlset [<!ENTITY x "y">]><urlset><url><loc>https://exemplo.com.br/</loc></url></urlset>', encoding="utf-8")
        self.reprova("DOCTYPE")

    def test_regra15_sem_404_reprova_no_dominio_e_e_pendencia_na_previa(self):
        (self.dist / "404.html").unlink()
        out = self.reprova("404.html ausente")
        self.assertIn("soft 404", out)
        code, out = self.gate(url=None)
        self.assertEqual(code, 0, out)
        self.assertTrue(any("404.html" in l for l in self.linhas(out, "PENDÊNCIA:")), out)

    def test_regra15_404_sem_noindex_reprova(self):
        (self.dist / "404.html").write_text(P404_BOM.replace('<meta name="robots" content="noindex">', ""), encoding="utf-8")
        self.reprova("404.html sem noindex")

    def test_o_404_html_nao_e_julgado_como_pagina(self):
        # curto, sem description e sem JSON-LD de propósito: as regras de página não valem para ele
        self.passa()

    def test_raiz_separada_da_dist_pagina_em_subcaminho(self):
        raiz = pathlib.Path(self.tmp.name) / "site-principal"
        escrever(raiz, {"robots.txt": ROBOTS_BOM, "sitemap.xml": SITEMAP_BOM, "404.html": P404_BOM})
        for nome in ("robots.txt", "sitemap.xml", "404.html"):
            (self.dist / nome).unlink()
        code, out = self.gate(extra=["--raiz", str(raiz)])
        self.assertEqual(code, 0, out)
        (raiz / "robots.txt").unlink()
        code, out = self.gate(extra=["--raiz", str(raiz)])
        self.assertEqual(code, 1, out)
        self.assertIn(str(raiz), out)


class OutrasPaginas(Base):
    def test_outros_html_da_pasta_seguem_as_regras_de_pagina(self):
        escrever(self.dist, {"obrigado.html": PAGINA_BOA.replace('<meta name="description"', '<meta name="x"')})
        out = self.reprova("meta description ausente", "obrigado.html")
        self.assertNotIn("REPROVA: meta description ausente (" + str(self.dist / "index.html"), out)

    def test_outra_pagina_tem_canonical_proprio_no_mesmo_dominio(self):
        outra = PAGINA_BOA.replace(f'<link rel="canonical" href="{URL}">', f'<link rel="canonical" href="{URL}obrigado.html">') \
                          .replace(f'<meta property="og:url" content="{URL}">', f'<meta property="og:url" content="{URL}obrigado.html">')
        escrever(self.dist, {"obrigado.html": outra})
        self.passa()
        escrever(self.dist, {"obrigado.html": outra.replace(f'href="{URL}obrigado.html"', 'href="https://outro.com.br/x"')})
        self.reprova("canonical", "domínio diferente")


class Formulario(Base):
    FORM = '<form action="/enviar"><input type="email" name="email"><button>Enviar</button></form>'

    def sem_privacidade(self, h):
        return h.replace(RODAPE, RODAPE_SEM_PRIVACIDADE)

    def test_regra16_form_sem_link_de_privacidade_reprova(self):
        self.html(lambda h: self.sem_privacidade(h).replace("</body>", self.FORM + "</body>"))
        self.reprova("privacidade")

    def test_regra16_input_solto_sem_form_tambem_conta(self):
        self.html(lambda h: self.sem_privacidade(h).replace("</body>", '<input type="text" name="nome"></body>'))
        self.reprova("privacidade")

    def test_regra16_link_por_texto_por_href_ou_em_ingles_passa(self):
        self.html(lambda h: h.replace("</body>", self.FORM + "</body>"))
        self.passa()
        self.setUp()
        self.html(lambda h: h.replace(RODAPE, '<footer><a href="/lgpd">Privacy policy</a></footer>').replace("</body>", self.FORM + "</body>"))
        self.passa()
        self.setUp()
        self.html(lambda h: h.replace(RODAPE, '<footer><a href="/Privacidade">Seus dados</a></footer>').replace("</body>", self.FORM + "</body>"))
        self.passa()

    def test_regra16_quiz_so_de_botoes_nao_pede_privacidade(self):
        self.html(lambda h: self.sem_privacidade(h).replace("</body>", "<button>Sim</button><button>Não</button></body>"))
        self.passa()

    def test_regra16_input_hidden_e_submit_nao_contam_como_coleta(self):
        self.html(lambda h: self.sem_privacidade(h).replace("</body>", '<input type="hidden" name="a"><input type="submit"></body>'))
        self.passa()


class UrlFinalDoPlano(Base):
    def plano(self, texto):
        p = pathlib.Path(self.tmp.name) / "PLANO.md"
        p.write_text(texto, encoding="utf-8")
        return p

    def test_url_final_vem_da_linha_dominio_final_da_secao_f(self):
        p = self.plano("# PLANO\n\n## e. Pixel\n\nDomínio final: https://errado.com.br/\n\n## f. Código e publicação\n\nHTML.\nDomínio final: https://exemplo.com.br/\n\n## g. Aprovação\n")
        code, out = rodar(["--dist", str(self.dist), "--plano", str(p)])
        self.assertEqual(code, 0, out)
        self.assertIn("modo domínio", out)

    def test_url_final_aceita_o_rotulo_url_final_e_marcacao_de_lista(self):
        p = self.plano("## f. Código\n\n- **URL final:** `https://exemplo.com.br/`\n")
        code, out = rodar(["--dist", str(self.dist), "--plano", str(p)])
        self.assertEqual(code, 0, out)
        self.assertIn("modo domínio", out)

    def test_a_definir_ou_modelo_nao_trocado_e_modo_previa(self):
        for valor in ("a definir", "<https://dominio-do-cliente.com.br ou a definir>", ""):
            p = self.plano(f"## f. Código\n\nDomínio final: {valor}\n")
            code, out = rodar(["--dist", str(self.dist), "--plano", str(p)])
            self.assertEqual(code, 0, out)
            self.assertIn("modo prévia", out, valor)

    def test_plano_sem_a_linha_ou_plano_que_nao_existe_e_previa(self):
        p = self.plano("## f. Código\n\nSem domínio ainda.\n")
        self.assertIn("modo prévia", rodar(["--dist", str(self.dist), "--plano", str(p)])[1])
        self.assertIn("modo prévia", rodar(["--dist", str(self.dist), "--plano", str(pathlib.Path(self.tmp.name) / "nao-existe.md")])[1])

    def test_o_argumento_url_final_vence_o_plano(self):
        p = self.plano("## f. Código\n\nDomínio final: https://errado.com.br/\n")
        code, out = rodar(["--dist", str(self.dist), "--plano", str(p), "--url-final", URL])
        self.assertEqual(code, 0, out)

    def test_url_final_em_http_no_plano_e_erro_de_uso(self):
        p = self.plano("## f. Código\n\nDomínio final: http://exemplo.com.br/\n")
        code, out = rodar(["--dist", str(self.dist), "--plano", str(p)])
        self.assertEqual(code, 2, out)
        self.assertIn("https://", out)


class CodigosDeSaida(unittest.TestCase):
    def test_dist_que_nao_existe_e_erro_de_uso_exit_2(self):
        code, out = rodar(["--dist", "/pasta/que/nao/existe/mesmo"])
        self.assertEqual(code, 2, out)

    def test_url_final_que_nao_e_https_e_erro_de_uso(self):
        with tempfile.TemporaryDirectory() as t:
            escrever(t, {"index.html": PAGINA_BOA})
            code, out = rodar(["--dist", t, "--url-final", "exemplo.com.br"])
            self.assertEqual(code, 2, out)

    def test_dist_sem_index_html_reprova(self):
        with tempfile.TemporaryDirectory() as t:
            code, out = rodar(["--dist", t, "--url-final", URL])
            self.assertEqual(code, 1, out)
            self.assertIn("index.html", out)

    def test_pelo_lancador_de_verdade_os_codigos_de_saida_chegam(self):
        with tempfile.TemporaryDirectory() as t:
            escrever(t, {"index.html": PAGINA_BOA, "robots.txt": ROBOTS_BOM, "sitemap.xml": SITEMAP_BOM, "404.html": P404_BOM,
                         "foto.webp": b"w", "og-image.jpg": b"j", "favicon.png": b"p"})
            cmd = [sys.executable, str(AQUI / "gate-seo.py")]
            ok = subprocess.run([*cmd, "--dist", t, "--url-final", URL], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            (pathlib.Path(t) / "robots.txt").unlink()
            ruim = subprocess.run([*cmd, "--dist", t, "--url-final", URL], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(ruim.returncode, 1, ruim.stdout + ruim.stderr)
            uso = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(uso.returncode, 2, uso.stdout + uso.stderr)


class PaginasReaisEmMiniatura(unittest.TestCase):
    """As duas páginas da auditoria de 27/10/2026, reduzidas ao que o gate precisa pegar."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dist = pathlib.Path(self.tmp.name)

    def test_sales_antes(self):
        """sales.juliocouto.com.br: robots e sitemap devolviam a home com 200, sem description, canonical e JSON-LD,
        logo em base64 3 vezes (281 KB de 364 KB), h2 seguido de h4."""
        logo = base64.b64encode(b"\x89PNG" + b"L" * 70000).decode()
        tag = f'<img src="data:image/png;base64,{logo}" alt="logo" width="120" height="40">'
        home = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
                "<title>IAutomate: atendimento no WhatsApp com IA</title>"
                '<meta property="og:image" content="https://sales.exemplo.com.br/og.png"></head><body>'
                f"<h1>Atendimento que vende sozinho</h1>{tag}<h2>Como funciona</h2><h4>Passo um</h4><p>{palavras(320)}</p>{tag}{tag}"
                "</body></html>")
        escrever(self.dist, {"index.html": home, "robots.txt": home, "sitemap.xml": home})
        code, out = rodar(["--dist", str(self.dist), "--url-final", "https://sales.exemplo.com.br/"])
        self.assertEqual(code, 1, out)
        reprovas = "\n".join(l for l in out.splitlines() if l.startswith("REPROVA:"))
        for trecho in ("meta description ausente", "canonical ausente", "JSON-LD ausente", "repetido 3 vezes",
                       "h2→h4", "robots.txt é HTML", "sitemap.xml não é XML válido", "404.html ausente"):
            self.assertIn(trecho, reprovas, f"faltou {trecho!r}\n{out}")
        self.assertRegex(reprovas, r"68,4 KB cada, 205,\d KB no total")  # o logo repetido, em KB

    def test_sobrai_antes(self):
        """juliocouto.com.br/sobrai/: noindex esquecido e SPA com o #root vazio (HTML cru de 1,8 KB, 0 palavras)."""
        spa = ('<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>SobrAI: recupere vendas no WhatsApp</title>'
               '<meta name="description" content="O SobrAI recupera vendas perdidas e faz o primeiro atendimento no WhatsApp da sua empresa, sem equipe extra.">'
               '<meta name="robots" content="noindex, nofollow">'
               '<link rel="canonical" href="https://juliocouto.com.br/sobrai/">'
               '<meta property="og:image" content="https://juliocouto.com.br/sobrai/og.png">'
               '<script type="module" src="/sobrai/assets/index.js"></script></head>'
               '<body><div id="root"></div></body></html>')
        escrever(self.dist, {"index.html": spa})
        code, out = rodar(["--dist", str(self.dist), "--url-final", "https://juliocouto.com.br/sobrai/"])
        self.assertEqual(code, 1, out)
        reprovas = "\n".join(l for l in out.splitlines() if l.startswith("REPROVA:"))
        self.assertIn("SPA com #root vazio", reprovas)
        self.assertIn("0 palavras", reprovas)
        self.assertIn("noindex", reprovas)
        self.assertIn("JSON-LD ausente", reprovas)
        # na prévia o noindex sozinho não reprova: vira pendência
        code, out = rodar(["--dist", str(self.dist)])
        self.assertTrue(any("noindex" in l for l in out.splitlines() if l.startswith("PENDÊNCIA:")), out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
