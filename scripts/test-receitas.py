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
            achada = re.search(r"\*\*Origem (?:na v7|no protótipo v8|no teste real da 3\.5\.8):\*\*[^\n]*(?:\n[^\n*][^\n]*)*", corpo)
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


class FotoQueSeMonta(unittest.TestCase):
    """N21 (3.5.8): o momento assinatura de produto físico é FOTO REAL, nunca desenho. Palavras do dono: "visual real conta mais que qualquer outra coisa"."""

    def test_receita_e_so_transform_opacity_e_clip_path_com_reserva_e_instantaneo(self):
        r = receitas()["foto-que-se-monta"]
        css = r[r.index("```css"):]
        css = css[:css.index("```", 6)]
        for prop in re.findall(r"(?m)^[^{}/]*\{([^}]*)\}", css):
            for nome in re.findall(r"([a-z-]+)\s*:", prop):
                self.assertIn(nome, {"position", "inset", "display", "opacity", "transform", "transition", "transition-delay", "clip-path",
                                     "background", "background-image", "aspect-ratio", "overflow", "border-radius", "width", "height", "object-fit",
                                     "margin", "margin-top", "padding", "font-size", "color", "line-height", "max-width", "will-change",
                                     "animation", "pointer-events", "left", "right", "top", "bottom", "z-index", "--i", "--n", "--dy", "--foto",
                                     "background-size", "background-position", "background-repeat", "gap"}, f"propriedade {nome} fora da gramática")
        self.assertIn("clip-path: inset(", r)
        self.assertIn(".instantaneo", r)
        self.assertRegex(r, r"(?s)\*\*Reserva:\*\*.*sem script.*foto inteira")
        self.assertRegex(r, r"(?i)movimento reduzido.*foto inteira|foto inteira.*movimento reduzido")
        self.assertRegex(r, r"(?i)foto real")
        self.assertRegex(r, r"(?i)r[oó]tulo|cota")

    def test_a_regra_do_momento_assinatura_manda_foto_real_em_produto_fisico(self):
        t = re.sub(r"\s+", " ", ler(MD))
        i = t.index("## Escolha do momento assinatura")
        regra = t[i:t.index("## Receita:", i)]
        for item in ("produto físico", "móveis", "comida", "imóvel", "moda", "obra", "carro", "foto real do produto", "nunca desenho",
                     "serviço abstrato", "software", "tela real do produto", "foto-que-se-monta"):
            self.assertIn(item, regra, item)

    def test_demo_traz_o_bloco_com_foto_raster_embutida_e_sem_fonte_de_sistema_nova(self):
        demo = ler(DEMO)
        i = demo.index('data-receita="foto-que-se-monta"')
        bloco = demo[i:demo.index("</section>", i)]
        self.assertRegex(demo, r"data:image/jpeg;base64,[A-Za-z0-9+/=]{4000,}")
        self.assertIn('class="monta-peca"', bloco)
        self.assertNotIn("<use", bloco)
        self.assertEqual(len(re.findall(r'class="monta-peca"', bloco)), 5)

    def test_gate_de_composicao_avisa_desenho_no_lugar_da_foto_so_com_a_marca_de_produto_fisico(self):
        g = ler(SCRIPTS / "gate-composicao.mjs")
        self.assertIn("--produto-fisico", g)
        self.assertRegex(g, r"AVISO")
        self.assertIn("foto real do produto", g)


class RegrasDoTesteReal358(unittest.TestCase):
    """Achados N15 e N16 do teste de página do zero (3.5.8): o que a receita não dizia e custou rodadas de 191 s do gate."""

    def test_abertura_do_topo_manda_o_que_cai_abaixo_da_dobra_do_celular_para_revela(self):
        corpo = receitas()["abertura-do-topo"]
        self.assertRegex(corpo, r"(?s)abaixo da dobra no celular.*`revela`.*n[aã]o `abertura-entra`")
        self.assertIn("320", corpo, "a regra tem que citar o 320 px, onde o texto e os fatos descem")

    def test_regra_geral_proibe_animation_delay_longo(self):
        texto = ler(MD)
        self.assertRegex(texto, r"(?s)(?=.*nunca `animation-delay`)(?=.*quadro-chave parad[oa] no come[cç]o)")



class AchadosDaTorraClara3510(unittest.TestCase):
    """3.5.10 (frente C): P5, P12, P13b, P14, P19 e P20 do teste da Torra Clara (3.5.8). O que a receita não dizia e virou
    defeito real; a prova no navegador é do test-visibilidade-movimento.cjs e do test-receitas-navegador.cjs."""

    def setUp(self):
        self.md = ler(MD)
        self.base = self.md[self.md.index("## Gramática de base"):self.md.index("## Escolha do momento assinatura")]
        self.demo = ler(DEMO)

    def test_p12_clip_path_de_entrada_vai_no_filho_nunca_no_alvo_do_observador(self):
        b = re.sub(r"\s+", " ", self.base)
        self.assertIn("clip-path de entrada vai no filho, nunca no alvo do observador", b)
        self.assertIn("threshold", b)
        self.assertIn("gate-movimento.mjs", b)

    def test_p13b_a_primeira_tela_entra_na_carga(self):
        b = re.sub(r"\s+", " ", self.base).lower()
        self.assertIn("a primeira tela entra na carga", b)
        self.assertIn("primeiraTela", self.base, "a base mínima traz o código")
        self.assertIn("primeiraTela", self.demo, "o demo usa o código da base")

    def test_p14_ja_passou_e_estado_final_na_base_e_no_demo(self):
        b = re.sub(r"\s+", " ", self.base).lower()
        self.assertIn("já passou = estado final", b)
        for texto in (self.base, self.demo):
            self.assertIn("jaPassou", texto)
            self.assertRegex(texto, r"getBoundingClientRect\(\)\.bottom\s*<=\s*0")
            self.assertRegex(texto, r"addEventListener\('scroll'")

    def test_p19_painel_de_cor_diz_quantos_botoes_levam_data_painel(self):
        corpo = re.sub(r"\s+", " ", receitas()["painel-de-cor"])
        self.assertIn("no máximo 3 botões com `data-painel`", corpo)
        self.assertNotIn("e em mais nenhum", corpo, "a frase ambígua saiu")
        self.assertLessEqual(self.demo.count("data-painel>") + self.demo.count("data-painel "), 3)

    def test_p20_barra_fixa_cobre_a_oferta_longa(self):
        corpo = re.sub(r"\s+", " ", receitas()["barra-fixa-do-celular"])
        self.assertIn("oferta longa", corpo)
        self.assertIn("data-barra-rotulo", corpo)
        self.assertIn("data-barra-rotulo", self.demo)
        self.assertIn("2 telas", corpo)

    def test_p5_produto_em_estados_atravessa_as_secoes_com_a_mesma_foto(self):
        r = receitas()
        self.assertIn("produto-em-estados", r)
        corpo = re.sub(r"\s+", " ", r["produto-em-estados"])
        for item in ("mesma foto", "3 seções", "data-assinatura", "sticky", "gate-imagens", "foto-que-se-monta"):
            self.assertIn(item, corpo, item)
        monta = re.sub(r"\s+", " ", r["foto-que-se-monta"])
        self.assertIn("produto-em-estados", monta, "a foto-que-se-monta aponta a saída quando a assinatura atravessa seções")
        escolha = re.sub(r"\s+", " ", self.md[self.md.index("## Escolha do momento assinatura"):self.md.index("## Receita: abertura-do-topo")])
        self.assertIn("produto-em-estados", escolha)
        self.assertIn('data-receita="produto-em-estados"', self.demo)


class VarianteDeTresFotos3511(unittest.TestCase):
    """3.5.11 (P5 que a 3.5.10 deixou pela metade): produto que muda de FOTO (grão cru, torrado, na xícara) é uma sequência declarada
    com data-assinatura-estado; o gate-imagens.py a aceita (test-imagens.py) e esta receita ensina a fazer a sequência ler como
    continuação. A prova no navegador é do test-receitas-navegador.cjs."""

    def setUp(self):
        self.md = ler(MD)
        self.rec = re.sub(r"\s+", " ", receitas()["produto-em-estados"])
        self.variante = self.rec[self.rec.index("Variante de 3 fotos (3.5.11"):]
        self.demo = ler(DEMO)

    def test_continua_17_receitas_a_variante_mora_dentro_de_produto_em_estados(self):
        self.assertEqual(len(receitas()), 17)
        self.assertEqual(self.md.count("## Receita: produto-em-estados"), 1)

    def test_a_receita_nao_manda_mais_esperar_a_3511(self):
        self.assertNotIn("proposta registrada para a 3.5.11", self.rec)
        self.assertIn("variante de 3 fotos", self.rec.split("Variante de 3 fotos (3.5.11")[0])

    def test_a_variante_declara_o_que_o_gate_aceita(self):
        for item in ("data-assinatura-estado", "data-assinatura-grupo", "gate-imagens.py", "regra 13", "de 2 a 4 estados", "sem buraco",
                     "um momento assinatura só por página", "continuam reprovando"):
            self.assertIn(item, self.variante, item)

    def test_a_variante_explica_porque_sao_uma_sequencia_e_nao_tres_fotos_soltas(self):
        for item in ("mesmo quadro", "mesma âncora", "--ancora", "object-position", "por baixo", "aria-hidden", "trilha",
                     "aria-current", "não precisam ser vizinhas", "do estado anterior"):
            self.assertIn(item, self.variante, item)

    def test_a_cortina_escreve_o_clip_path_final_e_o_recorte_vai_na_imagem(self):
        self.assertIn("clip-path: inset(0 0 0 0)", self.variante)
        self.assertRegex(self.variante, r"(?s)\.js \.efotos:not\(\.visivel\) \.efotos-atual \{ clip-path: inset\(0 100% 0 0\)")
        self.assertIn("nunca na figure que o observador olha", self.variante)

    def test_a_variante_tem_reserva_movimento_reduzido_e_prova(self):
        for item in ("Fora da janela", "Reserva", "sem script", "Movimento reduzido", "provar-receitas.mjs", "mesma largura, altura e posição"):
            self.assertIn(item, self.variante, item)

    def test_a_escolha_do_momento_assinatura_aponta_a_variante(self):
        escolha = re.sub(r"\s+", " ", self.md[self.md.index("## Escolha do momento assinatura"):self.md.index("## Receita: abertura-do-topo")])
        self.assertIn("data-assinatura-estado", escolha)

    def test_todo_seletor_da_variante_do_md_existe_no_demo(self):
        css_md = re.search(r"(?s)```css\n(\.efotos-secao.*?)```", self.md).group(1)
        classes = set(re.findall(r"\.(efotos[a-z-]*)", css_md))
        self.assertTrue({"efotos", "efotos-quadro", "efotos-atual", "efotos-trilha", "efotos-n"} <= classes, classes)
        for c in sorted(classes):
            self.assertIn(c, self.demo, c)

    def test_o_demo_traz_os_3_estados_com_a_cobertura_da_base(self):
        figuras = re.findall(r'<figure class="efotos" data-assinatura-grupo="graos" data-assinatura-estado="(\d)"', self.demo)
        self.assertEqual(figuras, ["1", "2", "3"])
        fantasmas = re.findall(r'<img class="efotos-antes"[^>]*alt=""[^>]*aria-hidden="true"[^>]*data-assinatura-estado="(\d)"', self.demo)
        self.assertEqual(fantasmas, ["1", "2"], "a cópia por baixo leva o número do estado anterior")
        self.assertEqual(self.demo.count(".estados-secao, .efotos'"), 2, "observar e o else do navegador sem observador")
        self.assertRegex(self.demo, r"\.js \.efotos-atual \{ clip-path: inset\(0 0 0 0\);")
        self.assertRegex(self.demo, r"\.js \.efotos:not\(\.visivel\) \.efotos-atual \{ clip-path: inset\(0 100% 0 0\)")
        movimento = self.demo[self.demo.rindex("@media (prefers-reduced-motion: reduce) {\n  .js .revela"):]
        self.assertIn(".efotos", self.demo[self.demo.index("/* produto-em-estados, variante de 3 fotos */"):self.demo.index("@media (prefers-reduced-motion: reduce) {\n  .js .revela")])
        self.assertIn("data-assimetrico", self.demo[self.demo.index('class="efotos-seq"') - 10:self.demo.index('class="efotos-seq"') + 200])

    def test_a_prova_do_navegador_mede_a_mesma_posicao_a_cortina_e_o_movimento_reduzido(self):
        prova = ler(SCRIPTS / "provar-receitas.mjs")
        for item in ("estados_fotos", "mesma_posicao", "getAnimations", "reducedMotion: 'reduce'"):
            self.assertIn(item, prova, item)
        nav = ler(SCRIPTS / "test-receitas-navegador.cjs")
        self.assertIn("estados_fotos", nav)

    def test_zero_travessao(self):
        self.assertNotIn("\u2014", self.md)
        self.assertNotIn("\u2014", self.demo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
