"""As receitas de movimento da v7 precisam estar na skill, completas e com uma demonstração.

Por que existe (06/10/2026): a página aprovada pelo dono ficou boa pelo movimento, e esse movimento
não morava em nenhum arquivo da skill; cada página nova reinventava tudo. Este teste cobra:
cada receita do `references/receitas-de-movimento.md` tem os campos obrigatórios, tem um bloco
`data-receita` na página `references/receitas/demo.html`, o demo respeita a regra de que todo estado
escondido fica atrás de `.js`, tem bloco de movimento reduzido e não traz travessão.

A prova no navegador (cada bloco muda de pixel, sem script, movimento reduzido) é do
`test-receitas-navegador.cjs`.

`RECEITAS_RAIZ` aponta outra pasta de skill (usado só para registrar o vermelho contra a versão
anterior).
"""
import os
import pathlib
import re
import subprocess
import sys
import unittest

RAIZ = pathlib.Path(os.environ.get("RECEITAS_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
REF = RAIZ / "references"
MD = REF / "receitas-de-movimento.md"
DEMO = REF / "receitas" / "demo.html"
SCRIPTS = pathlib.Path(__file__).resolve().parent


def ler(p):
    return p.read_text(encoding="utf-8")


def receitas():
    texto = ler(MD)
    partes = re.split(r"(?m)^## Receita: ", texto)[1:]
    return {p.split("\n", 1)[0].strip(): p for p in partes}


class Receitas(unittest.TestCase):
    def test_arquivos_existem(self):
        self.assertTrue(MD.exists(), "falta references/receitas-de-movimento.md")
        self.assertTrue(DEMO.exists(), "falta references/receitas/demo.html")

    def test_de_12_a_17_receitas(self):
        n = len(receitas())
        self.assertTrue(12 <= n <= 17, f"{n} receitas")

    def test_toda_receita_tem_os_campos_obrigatorios(self):
        for nome, corpo in receitas().items():
            self.assertIn(f"`data-receita`: `{nome}`", corpo, f"{nome}: identificador")
            for campo in ("**Quando usar:**", "**Quando NÃO usar:**", "**Origem na v7:**", "**Reserva:**", "**Custo no celular:**"):
                self.assertIn(campo, corpo, f"{nome}: falta {campo}")
            origem = re.search(r"\*\*Origem na v7:\*\*[^\n]*(?:\n[^\n*][^\n]*)*", corpo).group(0)
            self.assertRegex(origem, r"_(app\.js|input\.css|heroi\.html):\d+", f"{nome}: origem sem arquivo:linha")
            self.assertIn("```html", corpo, f"{nome}: sem HTML mínimo")
            self.assertIn("```css", corpo, f"{nome}: sem CSS")
            self.assertTrue("```js" in corpo or "Sem JS" in corpo, f"{nome}: sem JS nem a declaração 'Sem JS'")
            reserva = re.sub(r"\s+", " ", corpo[corpo.index("**Reserva:**"):])
            self.assertRegex(reserva, r"(?i)sem script|no-js", f"{nome}: reserva sem script")
            self.assertRegex(reserva, r"(?i)movimento reduzido", f"{nome}: reserva de movimento reduzido")

    def test_gramatica_de_base_aberta_com_os_numeros_da_v7(self):
        t = ler(MD)
        for item in ("cubic-bezier(.2,.8,.2,1)", "0,25 s a 2,0 s", "0,7 a 1,6 s", "threshold: 0.18", "-6%", ".js", "no-js",
                     "prefers-reduced-motion: reduce"):
            self.assertIn(item, t, item)
        self.assertLess(t.index("## Gramática de base"), t.index("## Receita:"))

    def test_curva_e_duracoes_das_receitas_sao_as_da_v7(self):
        r = receitas()
        self.assertIn(".7s cubic-bezier(.2,.8,.2,1)", r["abertura-do-topo"] + r["assinatura-em-tres-estados"])
        self.assertIn("animation-delay: .12s", r["abertura-do-topo"])
        self.assertIn("transition: opacity .8s ease, transform .8s cubic-bezier(.2,.8,.2,1)", r["revelar-ao-entrar"])
        self.assertIn("clip-path .95s cubic-bezier(.2,.8,.2,1)", r["texto-em-linhas"])
        self.assertIn("setTimeout(tick, 300)", r["vagas-que-se-preenchem"])
        self.assertIn("duration: 420", r["pergunta-que-abre"])
        self.assertIn("duration: 320", r["pergunta-que-abre"])
        self.assertIn("/ 2000", r["assinatura-em-tres-estados"])


class TextoEmLinhas(unittest.TestCase):
    """O defeito da v7 (trecho gerado que quebra de novo) não pode voltar na receita nem no demo."""

    def test_receita_e_demo_medem_depois_da_fonte_e_na_mudanca_de_largura(self):
        r = receitas()["texto-em-linhas"]
        d = ler(DEMO)
        for texto in (r, d):
            for item in ("document.fonts.ready", "loadingdone", "ResizeObserver", "getClientRects"):
                self.assertIn(item, texto, item)
        for item in ("515 px", "porque", "defeito medido na v7", "test-linhas.cjs"):
            self.assertIn(item, re.sub(r"\s+", " ", r), item)
        self.assertIn("**Cuidado", r)

    def test_fixture_da_v7_e_a_fonte_sintetica_existem(self):
        for nome in ("linhas-v7.js", "larga.ttf"):
            self.assertTrue((SCRIPTS / "fixtures" / nome).exists(), nome)


class Demo(unittest.TestCase):
    def setUp(self):
        self.html = ler(DEMO)

    def test_todo_bloco_do_md_tem_bloco_no_demo_e_vice_versa(self):
        no_md = set(receitas())
        no_demo = set(re.findall(r'data-receita="([^"]+)"', self.html))
        self.assertEqual(sorted(no_md - no_demo), [], "receita sem bloco no demo")
        self.assertEqual(sorted(no_demo - no_md), [], "bloco no demo sem receita no md")
        for nome in no_demo:
            self.assertRegex(self.html, rf'data-receita="{nome}"[^>]*data-gatilho="(carga|entrar|rolagem|clique|hover)"', nome)

    def test_cada_bloco_mostra_o_nome_da_receita(self):
        for nome in receitas():
            trecho = self.html[self.html.index(f'data-receita="{nome}"'):]
            trecho = trecho[:trecho.index("</section>")]
            self.assertTrue(re.search(r"<h[12][^>]*>[^<]+</h[12]>", trecho), nome)

    def test_autocontido_sem_biblioteca_nem_dado_externo(self):
        self.assertNotRegex(self.html, r"<script[^>]+src=")
        self.assertNotRegex(self.html, r'<link[^>]+rel="stylesheet"')
        self.assertNotRegex(self.html, r'(?:src|href)="https?://')
        self.assertNotIn("@import", self.html)

    def test_bloco_de_movimento_reduzido(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.html)
        self.assertIn("matchMedia('(prefers-reduced-motion: reduce)')", self.html)

    def test_estado_escondido_so_atras_de_js(self):
        css = re.search(r"<style>(.*?)</style>", self.html, re.S).group(1)
        css = re.sub(r"@keyframes\s+\w+\s*\{(?:[^{}]|\{[^{}]*\})*\}", "", css)
        css = re.sub(r"@media \(prefers-reduced-motion: reduce\)\s*\{(?:[^{}]|\{[^{}]*\})*\}", "", css)
        ruins = []
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            seletor, corpo = m.group(1).strip(), m.group(2)
            if re.search(r"opacity:\s*0\s*;|scaleX\(0\)|clip-path:\s*inset\((?!0 0 0 0)[^)]*\)|translateY\(110%\)", corpo) and ".js" not in seletor and "barra" not in seletor:
                ruins.append(seletor[-60:])
        self.assertEqual(ruins, [], "estado escondido fora de .js")
        self.assertIn('class="no-js"', self.html)
        self.assertIn("replace('no-js','js')", self.html)

    def test_sem_kicker_nem_numero_decorativo(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "gate-sem-kicker.py"), str(DEMO)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_assinatura_vem_no_html_para_a_pagina_sem_script(self):
        self.assertGreaterEqual(len(re.findall(r'class="peca"', self.html)), 24)


class Travessao(unittest.TestCase):
    def test_nenhum_arquivo_novo_tem_travessao(self):
        novos = [MD, DEMO, SCRIPTS / "provar-receitas.mjs", SCRIPTS / "test-receitas.py", SCRIPTS / "test-receitas-navegador.cjs", SCRIPTS / "test-linhas.cjs", SCRIPTS / "fixtures" / "linhas-v7.js"]
        ruins = [p.name for p in novos if p.exists() and re.search("[\u2014\u2013]", ler(p))]
        self.assertEqual(ruins, [])


class LenteDeMovimento(unittest.TestCase):
    """Fatia B: a lente de movimento e o sinal 2 dizem o que a v7 aprovada faz de fato."""

    def arquivos(self):
        for q in sorted(RAIZ.glob("**/*.md")):
            if {".git", "arquivo", "sessions", "projects"} & set(q.relative_to(RAIZ).parts):
                continue
            yield q, ler(q)

    def test_nenhum_arquivo_manda_revelar_so_2_a_4_secoes(self):
        ruins = [f"{q.name}" for q, t in self.arquivos() if re.search(r"2 a 4\s+(revela|seç)|nunca em todo elemento|Animar só o que tem hierarquia", re.sub(r"\s+", " ", t))]
        self.assertEqual(ruins, [])

    def test_lente_de_movimento_cita_a_v7_com_os_numeros(self):
        a = re.sub(r"\s+", " ", ler(REF / "auditores.md"))
        trecho = a[a.index("### 4. motion-auditor"):a.index("### 5. responsive-auditor")]
        for item in ("24 elementos", "ELE chega na tela", "0,18", "-6%", "cubic-bezier(.2,.8,.2,1)", "0,25 a 2,0 s", "momentos próprios", "MESMO fade", "receitas-de-movimento.md"):
            self.assertIn(item, trecho, item)
        self.assertIn("Quantidade de itens revelados não reprova", trecho)

    def test_sinal_2_condena_o_fade_igual_e_nao_a_quantidade(self):
        a = ler(REF / "anti-vibe-coding.md")
        linha = [l for l in a.splitlines() if l.startswith("| 2 |")][0]
        for item in ("MESMO fade", "tudo entra junto", "sem ligação com o conteúdo", "24", "ELE entra na tela", "MAIS momentos próprios"):
            self.assertIn(item, linha, item)
        self.assertNotIn("Cada card, cada parágrafo animando", linha)


class Ligacao(unittest.TestCase):
    """O repertório só serve se o fluxo manda escolher dele."""

    def test_ritmo_plano_e_criar_mandam_escolher_no_repertorio(self):
        for caminho in (REF / "ritmo-e-animacao.md", REF / "plano.md", REF / "caminhos" / "criar.md"):
            t = re.sub(r"\s+", " ", ler(caminho))
            self.assertIn("receitas-de-movimento.md", t, caminho.name)
            self.assertRegex(t, r"criação nova", f"{caminho.name}: falta a saída 'criação nova' com motivo")

    def test_skill_md_aponta_o_repertorio_e_cabe_no_teto(self):
        s = ler(RAIZ / "SKILL.md")
        self.assertIn("references/receitas-de-movimento.md", s)
        self.assertLessEqual(len(s.splitlines()), 330)


if __name__ == "__main__":
    unittest.main(verbosity=2)
