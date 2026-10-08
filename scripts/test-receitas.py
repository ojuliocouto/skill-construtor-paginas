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
            for campo in ("**Quando usar:**", "**Quando NÃO usar:**", "**Reserva:**", "**Custo no celular:**"):
                self.assertIn(campo, corpo, f"{nome}: falta {campo}")
            achada = re.search(r"\*\*Origem (?:na v7|no protótipo v8):\*\*[^\n]*(?:\n[^\n*][^\n]*)*", corpo)
            self.assertTrue(achada, f"{nome}: falta a origem")
            self.assertRegex(achada.group(0), r"_(app\.js|input\.css|heroi\.html|efeitos\.js):\d+", f"{nome}: origem sem arquivo:linha")
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
            self.assertRegex(self.html, rf'data-receita="{nome}"[^>]*data-gatilho="(carga|entrar|rolagem|clique|hover|navegacao)"', nome)

    def test_cada_bloco_mostra_o_nome_da_receita(self):
        for nome in receitas():
            trecho = self.html[self.html.index(f'data-receita="{nome}"'):]
            trecho = trecho[:trecho.index("</section>")]
            self.assertTrue(re.search(r"<h[12][^>]*>[^<]+</h[12]>", trecho), nome)

    def test_autocontido_sem_biblioteca_nem_dado_externo(self):
        self.assertNotRegex(self.html, r"<script[^>]+src=")
        self.assertNotRegex(self.html, r'<link[^>]+rel="stylesheet"')
        self.assertNotRegex(self.html, r'(?:src|href)="https?://(?!exemplo\.invalid/)')  # só o link externo de prova, em domínio reservado
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
        self.assertRegex(self.html, r"classList\.replace\('no-js',\s*'js'\)")
        # A28: o demo usa a rede de segurança (temporizador que retira .js se o principal não confirmar) e o principal confirma
        self.assertRegex(self.html, r"setTimeout\(function \(\) \{ if \(!d\.hasAttribute\('data-js-ok'\)\) d\.classList\.replace\('js', 'no-js'\)")
        self.assertIn("setAttribute('data-js-ok', '')", self.html)

    def test_sem_kicker_nem_numero_decorativo(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "gate-sem-kicker.py"), str(DEMO)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_assinatura_vem_no_html_para_a_pagina_sem_script(self):
        self.assertGreaterEqual(len(re.findall(r'class="peca"', self.html)), 24)


class Travessao(unittest.TestCase):
    def test_nenhum_arquivo_novo_tem_travessao(self):
        novos = [MD, DEMO, SCRIPTS / "provar-receitas.mjs", SCRIPTS / "test-receitas.py", SCRIPTS / "test-receitas-navegador.cjs", SCRIPTS / "provar-painel.mjs", SCRIPTS / "test-painel.cjs", SCRIPTS / "test-linhas.cjs", SCRIPTS / "fixtures" / "linhas-v7.js"]
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


# ----- v3.5.6 (achados A11 e A12 do teste de ponta a ponta, 08/10/2026) -----
def carregar_js_livres():
    import importlib.util
    spec = importlib.util.spec_from_file_location("js_livres", SCRIPTS / "js-livres.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def blocos(corpo, linguagem):
    return re.findall(r"```%s\n(.*?)```" % linguagem, corpo, re.S)


def sem_blocos(corpo):
    return re.sub(r"```\w*\n.*?```", "", corpo, flags=re.S)


class JsDasReceitas(unittest.TestCase):
    """Todo trecho de JS de receita usa só nome que ele (ou a base mínima) define."""

    @classmethod
    def setUpClass(cls):
        cls.js = carregar_js_livres()
        topo = ler(MD).split("## Receita: ", 1)[0]
        cls.contexto = set()
        for b in blocos(topo, "js"):
            cls.contexto |= cls.js.declarados(cls.js.limpa(b))

    def test_o_verificador_pega_nome_sem_definicao(self):
        self.assertEqual(self.js.livres("var a = 1; aplicar(colunas.rolagem, a);"), ["aplicar", "colunas"])
        self.assertEqual(self.js.livres("var colunas = {}; function aplicar(c, p) { return c[p]; } aplicar(colunas, 1);"), [])
        self.assertEqual(self.js.livres("each(x.querySelectorAll('.a'), function (n) { n.classList.add('v'); });", {"each"}), ["x"])
        self.assertEqual(self.js.livres("var o = { chave: 1, outra: 2 }; var m = 1e9 + o.chave; // quadro()"), [])

    def test_nenhum_trecho_de_js_usa_nome_indefinido(self):
        ruins = {}
        for nome, corpo in receitas().items():
            livres = self.js.livres("\n".join(blocos(corpo, "js")), self.contexto)
            if livres:
                ruins[nome] = livres
        self.assertEqual(ruins, {}, "trecho de receita usa nome que nem ele nem a base mínima definem")

    def test_assinatura_traz_o_montar_e_o_colunas_iguais_aos_do_demo(self):
        corpo = receitas()["assinatura-em-tres-estados"]
        js = "\n".join(blocos(corpo, "js"))
        demo = ler(DEMO)
        colapsa = lambda s: re.sub(r"\s+", " ", s)
        montar_demo = re.search(r"function montar\(svg\) \{.*?\n  \}\n", demo, re.S).group(0)
        self.assertIn(colapsa(montar_demo.replace("\n  ", "\n")), colapsa(js), "montar() da receita difere do demo")
        for linha in ("var colunas = {};",
                      "colunas[svg.getAttribute('data-coluna')] = montar(svg);",
                      "if (colunas.rolagem) aplicar(colunas.rolagem, reduz ? 1 : 0);"):
            self.assertIn(linha, js, f"falta na receita: {linha}")


class NumerosDoTexto(unittest.TestCase):
    """O número do texto bate com a constante do código (achado A11: 0,45 s no texto, SEGURA = 150)."""

    # Número em prosa que não é constante do código: teto/limite, valor derivado, origem no protótipo.
    ISENTO = re.compile(r"(no máximo|até|teto de|cerca de|custa|mais de|menos de|abaixo de|acima de|=)\s*$", re.I)

    def numeros(self, corpo):
        achados = []
        for linha in sem_blocos(corpo).splitlines():
            if linha.startswith("**Origem"):
                continue
            for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s*(ms|s)\b", linha):
                if self.ISENTO.search(linha[:m.start()]):
                    continue
                v = float(m.group(1).replace(",", "."))
                achados.append((m.group(0), round(v * 1000 if m.group(2) == "s" else v)))
        return achados

    def no_codigo(self, corpo):
        js = "\n".join(blocos(corpo, "js") + blocos(corpo, "css") + blocos(corpo, "html"))
        achados = set()
        for m in re.finditer(r"(?<![\w.])(\d*\.?\d+)(ms|s)?\b", js):
            v = float(m.group(1))
            achados.add(round(v * 1000) if m.group(2) == "s" else round(v))
            if m.group(2) is None:
                achados.add(round(v * 1000))
        return achados

    def test_todo_tempo_dito_no_texto_existe_no_codigo_da_receita(self):
        ruins = []
        for nome, corpo in receitas().items():
            codigo = self.no_codigo(corpo)
            for texto, ms in self.numeros(corpo):
                if ms > 0 and ms not in codigo:
                    ruins.append(f"{nome}: o texto diz {texto} e o código não tem {ms} ms")
        self.assertEqual(ruins, [], "\n" + "\n".join(ruins))

    def test_painel_de_cor_soma_o_que_o_texto_diz(self):
        corpo = receitas()["painel-de-cor"]
        js = "\n".join(blocos(corpo, "js"))
        c = {k: int(re.search(r"\b%s = (\d+)" % k, js).group(1)) for k in ("SOBE", "SEGURA", "SAI")}
        total = (c["SOBE"] + c["SEGURA"] + c["SAI"]) / 1000
        self.assertEqual(total, 1.75, c)
        prosa = sem_blocos(corpo)
        fmt = lambda ms: f"{ms / 1000:.2f}".replace(".", ",").rstrip("0").rstrip(",") + " s"
        self.assertIn(f"em {fmt(c['SOBE'])}", prosa)
        self.assertIn(f"pausa de {fmt(c['SEGURA'])}", prosa)
        self.assertIn(f"cerca de {total:.1f} s".replace(".", ","), prosa)
        self.assertNotIn("2,1 s", prosa)
        self.assertNotIn("0,45 s", prosa)


class RedeDeSeguranca(unittest.TestCase):
    """A28: a receita-base traz a rede de segurança pronta."""

    def test_regras_gerais_trazem_o_head_com_temporizador_e_o_onerror(self):
        topo = ler(MD).split("## Receita: ", 1)[0]
        self.assertIn("data-js-ok", topo)
        self.assertIn("setTimeout(function () { if (!d.hasAttribute('data-js-ok'))", topo)
        self.assertIn("onerror=\"document.documentElement.classList.replace('js','no-js')\"", topo)
        self.assertIn("script bloqueado", topo)
        self.assertIn("script que demora 7 s", topo)


class EstadoFinalDaEntrada(unittest.TestCase):
    """A entrada `forwards` recomeça quando o navegador refaz o estilo (achado A13, atualização)."""

    def test_abertura_do_topo_fixa_o_estado_final_com_pronto(self):
        corpo = receitas()["abertura-do-topo"]
        self.assertIn(".js .abertura-entra.pronto { opacity: 1; transform: none; animation: none; }", corpo)
        self.assertIn("animationend", corpo)
        self.assertIn("classList.add('pronto')", corpo)

    def test_demo_traz_o_mesmo_estado_final(self):
        demo = ler(DEMO)
        self.assertIn(".js .abertura-entra.pronto { opacity: 1; transform: none; animation: none; }", demo)
        self.assertIn("classList.add('pronto')", demo)


class AssimetriaDeclarada(unittest.TestCase):
    """O par "título + lista vertical" que as receitas pedem declara `data-assimetrico` (achado A12)."""

    def test_receitas_que_pedem_o_par_dizem_que_ele_usa_data_assimetrico(self):
        for nome in ("assinatura-em-tres-estados", "titulo-fixo"):
            self.assertIn("data-assimetrico", receitas()[nome], f"{nome}: falta dizer que o par declara data-assimetrico")
        linha = (REF / "secoes" / "linha-do-tempo.md")
        self.assertIn("data-assimetrico", ler(linha), "linha-do-tempo.md: falta data-assimetrico")

    def test_a_regra_de_design_aponta_a_excecao_declarada(self):
        regra = ler(REF / "preferencias-de-design.md")
        i = regra.index("título à esquerda + lista vertical à direita")
        self.assertIn("data-assimetrico", regra[i - 400:i + 700], "a regra reprova o par sem dizer a saída declarada")

    def test_o_gate_de_simetria_le_o_atributo_na_lista_ao_lado_do_titulo(self):
        gate = ler(SCRIPTS / "gate-simetria.mjs")
        self.assertRegex(gate, r"reg\(out\.ladoTitulo,[^\n]*marcado\(")


class RegrasDoTesteReal358(unittest.TestCase):
    """Achados N15 e N16 do teste de página do zero (3.5.8): o que a receita não dizia e custou rodadas de 191 s do gate."""

    def test_abertura_do_topo_manda_o_que_cai_abaixo_da_dobra_do_celular_para_revela(self):
        corpo = receitas()["abertura-do-topo"]
        self.assertRegex(corpo, r"(?s)abaixo da dobra no celular.*`revela`.*n[aã]o `abertura-entra`")
        self.assertIn("320", corpo, "a regra tem que citar o 320 px, onde o texto e os fatos descem")

    def test_regra_geral_proibe_animation_delay_longo(self):
        texto = ler(MD)
        self.assertRegex(texto, r"(?s)(?=.*nunca `animation-delay`)(?=.*quadro-chave parad[oa] no come[cç]o)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
