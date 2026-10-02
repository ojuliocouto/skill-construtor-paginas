"""O texto da skill também tem gate: o que o aluno copia e cola precisa rodar.

Cada teste nasce de uma travada do teste com aluno (02/10/2026). Texto não roda sozinho,
então o que dá pra medir no texto vira asserção aqui.
"""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"


def textos(*globs):
    for g in globs:
        for p in sorted(RAIZ.glob(g)):
            if "__pycache__" in p.parts or "sessions" in p.parts or "projects" in p.parts:
                continue
            yield p, p.read_text(encoding="utf-8")


class Docs(unittest.TestCase):
    def test_t4_nenhum_comando_em_variavel_que_o_zsh_nao_roda(self):
        # W="python3 ..."; $W registrar -> zsh: "no such file or directory" (exit 127).
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.match(r'\s*[A-Z]+="(python3|node|npx)\b', linha) or re.search(r'\$[A-Z]+ (registrar|gate|checar|rodada|dispensar)\b', linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])


    def test_t19_nenhum_caminho_fixo_na_pasta_do_dono(self):
        # So funcionava porque o dono tem a skill em ~/.claude/skills. Instalacao (git clone,
        # skills add) e o unico lugar onde o destino aparece por extenso.
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"(~|\$HOME)/\.claude/skills/", linha) and not re.search(r"git clone|skills add", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
                if re.search(r"^SKILL=", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])

    def test_t19_dir_da_skill_explicado(self):
        self.assertRegex(SKILL.read_text(encoding="utf-8")[:6000], r"<dir-da-skill>.{0,40}(pasta|diret)")


    def test_t6_preferencias_genericas_existem_e_nao_citam_pessoa(self):
        pref = RAIZ / "references" / "preferencias-de-design.md"
        self.assertTrue(pref.exists(), "references/preferencias-de-design.md nao existe")
        texto = pref.read_text(encoding="utf-8")
        for nome in ("Júlio", "Julio", "Thales", "MaestrIA", "AutonomIA", "EA", "Operação Claude Code", "Laude"):
            self.assertNotRegex(texto, rf"\b{re.escape(nome)}\b", nome)
        for regra in ("kicker", "01/02/03", "número gigante", "inteira", "pricing", "lado a lado", "vermelho"):
            self.assertIn(regra.lower(), texto.lower(), regra)

    def test_t6_skill_e_scripts_falam_de_toda_pagina(self):
        ruins = []
        for p, t in textos("SKILL.md", "references/index.yaml", "scripts/*.py", "scripts/*.js", "scripts/*.mjs", "hooks/*.py"):
            if p.name.startswith("test-"):
                continue
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"J[uú]lio|MaestrIA|preferencias-dono-ea|\(ex: EA\)", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])


    def secao(self, inicio, fim):
        t = SKILL.read_text(encoding="utf-8")
        i = t.index(inicio)
        return t[i:t.index(fim, i)]

    def test_t7_precedencia_banco_x_skills_de_design_no_2_0(self):
        s = self.secao("### 2.0 Consultar o BANCO DE DESIGN", "### 2.1 ")
        self.assertRegex(s.lower(), r"ponto de partida")
        self.assertRegex(s.lower(), r"pr[oó]ximo resultado do banco")
        self.assertRegex(s.lower(), r"creme")
        self.assertRegex(s.lower(), r"motivo")


    def test_t8_tipo_servico_local_com_stack_definida(self):
        pt = (RAIZ / "references" / "page-types.md").read_text(encoding="utf-8").lower()
        self.assertIn("servico-local", pt)
        self.assertRegex(pt, r"(?s)### servi[cç]o local.{0,500}stack definida: html \+ tailwind compilado")
        s = SKILL.read_text(encoding="utf-8")
        tabela = self.secao("### DECISÃO DE TECH STACK", "**Se o projeto destino")
        self.assertRegex(tabela.lower(), r"servi[cç]o local.*html \+ tailwind compilado")
        proibido = self.secao("**PROIBIDO HTML/CSS PURO", "\n\n")
        self.assertRegex(proibido.lower(), r"servi[cç]o local")
        self.assertNotRegex(s, r"Obrigat[oó]ria no Step 1")


    def test_t16_modelo_curto_de_copy_para_servico_local(self):
        modelo = RAIZ / "references" / "copy-servico-local.md"
        self.assertTrue(modelo.exists())
        m = modelo.read_text(encoding="utf-8").lower()
        for parte in ("headline", "subt", "3 dores", "mecanismo", "como agendar", "formas", "dúvidas", "chamada final"):
            self.assertIn(parte, m, parte)
        s = self.secao("### 1.0 De onde vem a copy?", "### 1.1 ")
        self.assertIn("references/copy-servico-local.md", s)
        hero = self.secao("### 1.4 Copy Wireframe", "### 1.5 ")
        self.assertRegex(hero.lower(), r"micro-copy.{0,160}(opcional|nunca no hero)")


    def test_t17_sem_cliente_ainda_diz_o_que_mostra_e_o_que_oculta(self):
        s = SKILL.read_text(encoding="utf-8")
        i = s.find("SEM CLIENTE AINDA")
        self.assertGreater(i, 0, "paragrafo SEM CLIENTE AINDA ausente no SKILL.md")
        trecho = s[i:i + 2500].lower()
        for item in ("mostra", "oculta", "hidden", "credencial", "foto", "cnpj", "placeholder"):
            self.assertIn(item, trecho, item)
        modelo = (RAIZ / "references" / "copy-servico-local.md").read_text(encoding="utf-8").lower()
        self.assertIn("sem cliente ainda", modelo)


    def test_t9_audit_agents_e_readme_com_as_8_lentes_do_wave(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("wave", RAIZ / "scripts" / "wave.py")
        wave = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wave)
        aa = (RAIZ / "references" / "audit-agents.md").read_text(encoding="utf-8")
        for lente in wave.LENTES:
            self.assertIn(lente, aa, lente)
        for velho in ("mobile-auditor", "7 agentes", "Os 7", "os 7 verdicts", "libera APENAS", "score < 7"):
            self.assertNotIn(velho, aa, velho)
        self.assertIn("4.2f", aa)
        readme = (RAIZ / "README.md").read_text(encoding="utf-8")
        self.assertNotRegex(readme, r"\b7 parallel|\bmobile-auditor")
        for lente in wave.LENTES:
            self.assertIn(lente, readme, lente)


    def test_t14_seo_abaixo_de_90_sob_noindex_e_esperado(self):
        perf = self.secao("**Performance:**", "**Conteúdo:**").lower()
        self.assertRegex(perf, r"(?s)noindex.{0,300}seo|seo.{0,300}noindex")
        self.assertIn("esperado", perf)
        self.assertIn("is-crawlable", perf)


    def test_t15_movimento_rota_padrao_css_e_higgsfield_opcional_logo_no_inicio(self):
        s = SKILL.read_text(encoding="utf-8")
        self.assertNotRegex(s, r"(?i)higgsfield[^\n]{0,40}passo esperado|passo esperado, nao enfeite")
        i = s.index("### 3.2b MOVIMENTO")
        inicio = s[i:i + 700].lower()
        self.assertIn("css", inicio)
        self.assertIn("opcional", inicio)
        self.assertRegex(inicio, r"rota padr[aã]o")


    def test_t18_reregistrar_etapa_3_depois_da_wave_e_esperado(self):
        g = (RAIZ / "references" / "gate-etapas.md").read_text(encoding="utf-8").lower()
        self.assertRegex(g, r"(?s)etapa 3.{0,400}wave.{0,400}esperado", "gate-etapas.md nao explica a etapa 3 depois da wave")
        self.assertIn("evidência mudou", g)


    def test_t5_caminho_criar_em_uma_pagina_e_na_ordem(self):
        cc = RAIZ / "references" / "caminho-criar.md"
        self.assertTrue(cc.exists(), "references/caminho-criar.md nao existe")
        texto = cc.read_text(encoding="utf-8")
        self.assertLessEqual(len(texto.splitlines()), 110, "caminho-criar.md passou de uma pagina")
        ordem = ["checar-ferramentas.py", "registrar 0", "registrar 1", "search.py", "registrar 2",
                 "screenshot-prova.js", "tailwindcss", "registrar 3", "servidor-gzip.py", "gate-sem-kicker.py",
                 "gate-classes-mortas.py", "gate-responsivo.mjs", "gate-oclusao.mjs", "uso-ferramentas.py",
                 "wave.py --projeto <dir> checar", "wave.py --projeto <dir> rodada", "registrar 4"]
        pos = [texto.find(o) for o in ordem]
        self.assertNotIn(-1, pos, [o for o, p in zip(ordem, pos) if p < 0])
        self.assertEqual(pos, sorted(pos), "comandos fora de ordem no caminho-criar.md")
        runbook = self.secao("## RUNBOOK", "## MAPA DESTE ARQUIVO")
        self.assertIn("references/caminho-criar.md", runbook)

    def test_t5_ordem_4_2f_antes_de_4_2g_e_gate_4_em_lista(self):
        s = SKILL.read_text(encoding="utf-8")
        self.assertLess(s.index("### 4.2f "), s.index("### 4.2g "))
        gate = s[s.index(">>> GATE 4:"):s.index("**ENTREGA SEM DEPLOY")]
        self.assertGreaterEqual(len(re.findall(r"^- ", gate, flags=re.M)), 12, "GATE 4 ainda e paragrafo unico")


    def test_t21_acentuacao_no_texto_sem_tocar_em_codigo(self):
        # Fora de bloco de codigo com linguagem, de `inline`, de URL e de identificador
        # (palavra colada em - _ / . < > { }), estas palavras so existem com acento.
        sem = {"nao", "pagina", "paginas", "secao", "secoes", "voce", "tambem", "ja", "ate", "entao", "usuario",
               "codigo", "numero", "titulo", "botao", "preco", "conteudo", "obrigatorio", "padrao", "decisao",
               "direcao", "acao", "versao", "sessao", "video", "proprio", "unica", "unico", "visivel", "minimo",
               "maximo", "ultimo", "critico", "rapido", "publico", "trafego", "referencia", "pendencia", "regressao",
               "medicao", "composicao", "animacao", "atencao", "comecar", "servico", "estudio", "clinica",
               "consultorio", "saude", "facil", "possivel", "dificil", "necessario", "horario", "analise"}
        fence_codigo = re.compile(r"\s*```\s*([\w+-]+)")
        ruins = []
        for p, t in textos("SKILL.md", "references/*.md"):
            if p.name in ("preferencias-dono-ea.md", "desafio-ia-patterns.md"):
                continue
            dentro = codigo = False
            for n, linha in enumerate(t.splitlines(), 1):
                if linha.strip().startswith("```"):
                    m = fence_codigo.match(linha)
                    if not dentro:
                        dentro, codigo = True, bool(m) and m.group(1).lower() not in ("markdown", "md", "text", "txt")
                    else:
                        dentro = False
                    continue
                if dentro and codigo:
                    continue
                en = len(re.findall(r"\b(the|and|of|to|is|with|for|you|this|your|are|from|that|it|on|be|use)\b", linha, re.I))
                pt = len(re.findall(r"\b(de|que|nao|não|para|com|uma|um|se|do|da|no|na|os|as|em|por|ou|mais|sem|pagina|página)\b", linha, re.I))
                if en > pt:
                    continue
                limpa = re.sub(r"`[^`]*`|https?://\S+", " ", linha)
                for m in re.finditer(r"(?<![\w\-/.<{@#$])([A-Za-zÀ-ÿ]+)(?![\w\-/.>}])", limpa):
                    if m.group(1).lower() in sem:
                        ruins.append(f"{p.name}:{n}: {m.group(1)}")
        self.assertEqual(len(ruins), 0, f"{len(ruins)} palavras sem acento, ex.: {ruins[:8]}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
