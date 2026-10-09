"""O texto da skill também tem gate: o que o aluno copia e cola precisa rodar.

Os testes nasceram das travadas do teste com aluno (02/10/2026) e da v3 (mesmo dia): a skill
depende só da `frontend-design`, dos auditores e da pesquisa de referências, o SKILL.md só
roteia, e cada caminho mora no próprio arquivo. Texto não roda sozinho, então o que dá para
medir no texto vira asserção aqui.
"""
import importlib.util
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"
REF = RAIZ / "references"
CAMINHOS = REF / "caminhos"
CRIAR = CAMINHOS / "criar.md"
LOCAIS = {"preferencias-dono-ea.md", "desafio-ia-patterns.md"}  # gitignored, nunca vão pro repo
OPCIONAIS = ("21st", "Stitch", "Higgsfield", "nanobanana", "brandkit", "design-taste-frontend", "animate",
             "high-end-visual-design", "magicui", "Magic UI", "shadcn", "Pexels")


def ler(p):
    return p.read_text(encoding="utf-8")


def textos(*globs):
    for g in globs:
        for p in sorted(RAIZ.glob(g)):
            partes = set(p.parts)
            if {"__pycache__", "sessions", "projects", "arquivo"} & partes or p.name in LOCAIS:
                continue
            yield p, ler(p)


def wave():
    spec = importlib.util.spec_from_file_location("wave", RAIZ / "scripts" / "wave.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class Estrutura(unittest.TestCase):
    def test_v3_skill_curta_versionada_e_so_roteia(self):
        s = ler(SKILL)
        self.assertLessEqual(len(s.splitlines()), 420, "SKILL.md passou de ~400 linhas")
        self.assertRegex(s[:600], r"(?m)^version: 3\.\d+\.\d+$")
        for nome in ("criar", "clonar", "clonar-elevar", "melhorar", "editar"):
            arq = CAMINHOS / f"{nome}.md"
            self.assertTrue(arq.exists(), f"falta {arq.name}")
            self.assertIn(f"references/caminhos/{nome}.md", s, f"SKILL.md não roteia para {nome}")

    def test_v3_tres_dependencias_no_topo(self):
        topo = ler(SKILL)[:2500].lower()
        for d in ("frontend-design", "auditores", "referências reais"):
            self.assertIn(d, topo, d)

    def test_v3_opcionais_so_na_secao_do_fim(self):
        s = ler(SKILL)
        i = s.index("## Ferramentas opcionais")
        antes = s[:i]
        achados = [o for o in OPCIONAIS if re.search(rf"\b{re.escape(o)}\b", antes, re.I)]
        self.assertEqual(achados, [], "ferramenta opcional citada no caminho principal do SKILL.md")
        depois = s[i:]
        for o in ("21st", "Stitch", "Higgsfield", "nanobanana", "brandkit", "shadcn"):
            self.assertIn(o.lower(), depois.lower(), o)

    def test_v3_caminho_criar_sem_ferramenta_opcional(self):
        c = ler(CRIAR)
        achados = [o for o in OPCIONAIS if o != "Pexels" and re.search(rf"\b{re.escape(o)}\b", c, re.I)]
        self.assertEqual(achados, [])

    def test_v3_caminho_criar_em_etapas_na_ordem(self):
        c = ler(CRIAR)
        etapas = ["## a. Briefing", "## b. Pesquisa de referências", "## c. Plano visual", "## d. Copy",
                  "## e. Construção", "## f. Gates mecânicos", "## g. Auditores", "## h. Prova"]
        pos = [c.find(e) for e in etapas]
        self.assertNotIn(-1, pos, [e for e, p in zip(etapas, pos) if p < 0])
        self.assertEqual(pos, sorted(pos), "etapas fora de ordem")
        ordem = ["checar-ferramentas.py", "registrar 0", "capturar-referencias.mjs", "gate-referencias.py",
                 "registrar 1", "frontend-design", "plano-visual.md", "registrar 2", "copy-servico-local.md",
                 "registrar 3", "tailwindcss", "screenshot-prova.js", "registrar 4", "servidor-gzip.py",
                 "gate-sem-kicker.py", "gate-classes-mortas.py", "gate-responsivo.mjs", "gate-oclusao.mjs",
                 "uso-ferramentas.py --projeto <dir> checar", "wave.py --projeto <dir> registrar",
                 "wave.py --projeto <dir> checar", "wave.py --projeto <dir> rodada", "registrar 5"]
        p, ultimo = [], -1
        for o in ordem:
            achado = c.find(o, ultimo + 1)
            p.append(achado)
            if achado >= 0:
                ultimo = achado
        self.assertNotIn(-1, p, [o for o, x in zip(ordem, p) if x < 0])

    def test_v3_gate_de_referencias_bloqueia_antes_do_plano(self):
        c = ler(CRIAR)
        b = c[c.index("## b."):c.index("## c.")]
        self.assertIn("6", b)
        self.assertRegex(b.lower(), r"n[aã]o come[cç]a")
        self.assertIn("lido", b)

    def test_v3_frontend_design_acionada_de_verdade_e_banco_opcional(self):
        c = ler(CRIAR)
        plano = c[c.index("## c."):c.index("## d.")]
        self.assertRegex(plano, r"Skill tool")
        self.assertRegex(plano.lower(), r"search\.py.{0,200}(opcional|nunca decide)|(opcional|nunca decide).{0,200}search\.py")

    def test_a26_a27_texto_do_briefing_e_da_regra_de_referencias(self):
        aud = ler(REF / "auditores.md")
        criar = ler(REF / "caminhos" / "criar.md")
        for trecho in ("briefing-do-auditor.md", "15 minutos", "30 chamadas", "8 minutos", "15 chamadas", "Proibido recapturar",
                       "6 capturas próprias", "não verificado", "--duracao-min", "--chamadas"):
            self.assertIn(trecho, aud, trecho)
        for trecho in ("briefing-do-auditor.md", "15 minutos", "30 chamadas", "8 minutos", "6 capturas próprias", "--eixos-abaixo"):
            self.assertIn(trecho, criar, trecho)
        self.assertNotRegex(criar + aud, r"(?i)reprovada\s*=\s*volta ao passo c")
        self.assertIn("ciclo novo", criar)
        self.assertIn("ciclo novo", aud)

    def test_v3_auditores_subagente_ou_sequencial_e_nona_lente(self):
        a = ler(REF / "auditores.md")
        self.assertRegex(a.lower(), r"subagente")
        self.assertRegex(a.lower(), r"sequ[eê]ncia")
        self.assertIn("comparacao-referencias", a)
        self.assertRegex(a.lower(), r"eixos abaixo")
        w = wave()
        self.assertIn("comparacao-referencias", w.LENTES)
        for lente in w.LENTES:
            self.assertIn(lente, a, lente)
            self.assertIn(lente, ler(RAIZ / "README.md"), f"README sem a lente {lente}")

    def test_v3_nenhum_link_quebrado_nos_arquivos_do_fluxo(self):
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md", "references/caminhos/*.md"):
            for alvo in set(re.findall(r"references/[A-Za-z0-9_./-]+\.(?:md|yaml)", t)):
                if not (RAIZ / alvo).exists():
                    ruins.append(f"{p.name}: {alvo}")
            for alvo in set(re.findall(r"scripts/[A-Za-z0-9_.-]+\.(?:py|mjs|cjs|js)", t)):
                if not (RAIZ / alvo).exists():
                    ruins.append(f"{p.name}: {alvo}")
        self.assertEqual(ruins, [])

    def test_v3_nenhuma_referencia_orfa_no_topo(self):
        # Tudo que mora em references/ (fora de arquivo/, projects/, sessions/ e dos locais) tem
        # que ser citado pelo SKILL.md ou por um caminho. Órfão vai para references/arquivo/.
        citados = ler(SKILL) + "".join(ler(p) for p in CAMINHOS.glob("*.md"))
        orfaos = [p.name for p in REF.glob("*.md") if p.name not in LOCAIS and p.name not in citados]
        self.assertEqual(orfaos, [])
        self.assertTrue((REF / "arquivo" / "README.md").exists())

    def test_v3_projetos_e_sessoes_fora_do_git(self):
        gi = ler(RAIZ / ".gitignore")
        self.assertIn("references/projects/*", gi)
        self.assertIn("references/sessions/*", gi)
        self.assertIn("references/preferencias-dono-ea.md", gi)

    def test_registro_de_sessao_vai_na_pasta_do_projeto_nunca_na_da_skill(self):
        """3.5.9 (N25): SKILL.md e criar.md mandavam gravar em references/sessions/, e gate-etapas.md proíbe dado de cliente na pasta da skill."""
        textos = {"SKILL.md": ler(SKILL), "caminhos/criar.md": ler(CAMINHOS / "criar.md")}
        for nome, t in textos.items():
            self.assertNotRegex(t, r"(?i)(registre|salve|grave|atualize)[^\n.]*`references/(sessions|projects)/(AAAA|<projeto>)", nome)
            self.assertIn("<projeto>/sessoes/", t, nome)
        self.assertRegex(ler(REF / "gate-etapas.md"), r"Nunca use a pasta da skill para\s+guardar dados de cliente")

    def test_v3_readme_em_ingles_e_changelog(self):
        r = ler(RAIZ / "README.md")
        self.assertRegex(r, r"(?i)what it is")
        self.assertRegex(r, r"(?i)what it is not")
        self.assertRegex(r, r"(?i)install")
        self.assertRegex(r, r"(?i)prerequisites")
        self.assertIn("frontend-design", r)
        ch = ler(RAIZ / "CHANGELOG.md")
        self.assertIn("3.0.0", ch)
        self.assertRegex(ch, r"(?i)v2.{0,10}v3|2\.0\.0.{0,40}3\.0\.0")

    def test_zero_travessao(self):
        ruins = [p.name for p, t in textos("SKILL.md", "README.md", "CHANGELOG.md", "references/*.md",
                                           "references/caminhos/*.md") if re.search("[—–]", t)]
        self.assertEqual(ruins, [])

    # Auditoria da v3 (02/10/2026): o que a nota 5,5 ensinou precisa estar escrito no caminho.
    def test_v31_foto_publico_logo_e_nada_por_cima_de_pessoa(self):
        c = ler(CRIAR).lower()
        self.assertIn("público -> foto escolhida -> por quê", c)
        self.assertRegex(c, r"logo de terceiro")
        self.assertRegex(c, r"atravessa rosto ou corpo")

    def test_v31_auditor_independente_e_autoavaliacao_nao_libera(self):
        for t in (ler(CRIAR), ler(REF / "auditores.md"), ler(SKILL)):
            t = re.sub(r"\s+", " ", t)
            self.assertRegex(t.lower(), r"subagente auditor independente")
            self.assertRegex(t.lower(), r"autoavalia[cç][aã]o n[aã]o libera entrega")

    # v3.5.4 (08/10/2026): um auditor para as nove lentes, pacote de evidência pronto, teto de 2 rodadas
    # e segunda rodada de conferência. O dono perguntou "esses 9 revisores são necessários?" e a regra
    # dele é teto de 2 rodadas de corrigir e auditar.
    def _compacto(self, p):
        return re.sub(r"\s+", " ", ler(p))

    def test_v354_um_auditor_para_as_nove_lentes_e_o_padrao(self):
        for p in (REF / "auditores.md", CRIAR, SKILL):
            t = self._compacto(p).lower()
            self.assertRegex(t, r"um (único )?subagente auditor", p.name)
            self.assertRegex(t, r"uma passada", p.name)
        a = self._compacto(REF / "auditores.md").lower()
        self.assertRegex(a, r"uma lente por subagente.{0,200}(opcional|só quando|somente quando).{0,200}profunda")
        self.assertRegex(a, r"auditoria profunda")

    def test_v354_nenhum_texto_manda_nove_subagentes_nem_teto_de_quatro(self):
        proibidos = (r"teto de 4 rodadas", r"4 rodadas", r"quatro rodadas", r"9 lentes por subagente",
                     r"nove lentes por subagente", r"um subagente por lente")
        for p, t in textos("SKILL.md", "README.md", "references/*.md", "references/caminhos/*.md"):
            t = re.sub(r"\s+", " ", t).lower()
            for pr in proibidos:
                self.assertNotRegex(t, pr, f"{p.name}: {pr}")
            for m in re.finditer(r"uma lente por subagente", t):
                contexto = t[max(0, m.start() - 250): m.end() + 250]
                self.assertRegex(contexto, r"opcional|profunda|deixa de ser o padr", f"{p.name}: 'uma lente por subagente' sem ser modo opcional")

    def test_v354_registro_continua_um_por_lente_com_origem(self):
        a = self._compacto(REF / "auditores.md").lower()
        self.assertRegex(a, r"registro.{0,200}(um por lente|cada lente)")
        self.assertIn("--origem subagente", a)
        self.assertRegex(a, r"autoavalia[cç][aã]o n[aã]o libera entrega")

    def test_v354_pacote_de_evidencia_com_lista_e_comando(self):
        for p in (REF / "auditores.md", CRIAR):
            t = self._compacto(p)
            self.assertIn("py.mjs pacote-auditoria.py", t, p.name)
            for item in ("dist/", "PLANO.md", "prancha-desktop.png", "prancha-mobile.png", "referencias/", "briefing"):
                self.assertIn(item, t, f"{p.name}: pacote sem {item}")
            self.assertRegex(t.lower(), r"n[aã]o captura(m)? de novo|n[aã]o capturam? (as telas )?de novo|sem capturar de novo", p.name)
        self.assertTrue((RAIZ / "scripts" / "pacote-auditoria.py").is_file())
        self.assertTrue((RAIZ / "scripts" / "test-pacote-auditoria.py").is_file())

    def test_v354_teto_de_duas_rodadas_e_ressalvas(self):
        for p in (REF / "auditores.md", CRIAR, SKILL):
            t = self._compacto(p)
            self.assertRegex(t.lower(), r"teto de 2 rodadas", p.name)
        a = self._compacto(REF / "auditores.md")
        for item in ("ENTREGA COM RESSALVAS", "NÃO ENTREGAR: crítico aberto", "--rodada-extra-pedida"):
            self.assertIn(item, a, item)
        self.assertRegex(a.lower(), r"nunca pede (a )?terceira rodada sozinh")
        self.assertEqual(wave().TETO_RODADAS, 2)

    def test_v354_rodada_2_e_conferencia_com_schema(self):
        a = self._compacto(REF / "auditores.md")
        i = a.index("Rodada 2")
        trecho = a[i:i + 2500].lower()
        for item in ("conferência", "corrigido", "não corrigido", "regressão", "evidência", "achado", "estado"):
            self.assertIn(item, trecho, item)
        self.assertRegex(trecho, r"n[aã]o reabre as 9 lentes")
        self.assertRegex(trecho, r"mais nada")
        self.assertIn("```json", ler(REF / "auditores.md").split("Rodada 2", 1)[1])

    def test_v354_versao_e_registro_de_mudancas(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.13$")
        self.assertIn("## 3.5.4", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("## 3.5.5", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.5", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.6", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.6", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.7", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.7", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.8", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.8", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.9", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.9", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.10", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.10", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.11", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.11", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.12", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.12", ler(RAIZ / "README.md"))
        self.assertIn("## 3.5.13", ler(RAIZ / "CHANGELOG.md"))
        self.assertIn("3.5.13", ler(RAIZ / "README.md"))
        self.assertIn("pacote-auditoria.py", ler(RAIZ / "README.md"))
        self.assertIn("pacote-auditoria.py", ler(SKILL))

    def test_v354_zero_travessao_nos_textos_da_skill(self):
        for p, t in textos("SKILL.md", "README.md", "CHANGELOG.md", "references/*.md", "references/caminhos/*.md"):
            self.assertNotIn("\u2014", t, p.name)
        for f in ("pacote-auditoria.py", "test-pacote-auditoria.py", "wave.py"):
            self.assertNotIn("\u2014", ler(RAIZ / "scripts" / f), f)

    def test_v31_jornal_de_filetes_e_tell(self):
        a = ler(REF / "anti-vibe-coding.md")
        self.assertRegex(a, r"V16 \| \*\*\"Jornal de filetes\"")
        self.assertIn("jornal de filetes", re.sub(r"\s+", " ", ler(CRIAR)).lower())

    def test_v31_deploy_so_da_dist_e_tabela_de_sustentacao(self):
        c = ler(CRIAR)
        self.assertIn("montar-dist.py", c)
        self.assertIn("gate-publicacao.py", c)
        self.assertIn("evidencias/sustentacao.md", c)
        self.assertIn("gate-verdade.py", c)


    # Etapa PLANO (03/10/2026): "seria bom se essa skill desse opções de visual e tipos de seções
    # pro cara, inclusive uma etapa de planejamento pra copy, pixel, código, referências".
    def test_v34_plano_entre_referencias_e_construcao(self):
        c = ler(CRIAR)
        b, p, cc, e = c.find("## b."), c.find("## b2. PLANO"), c.find("## c."), c.find("## e.")
        self.assertTrue(0 < b < p < cc < e, (b, p, cc, e))
        trecho = c[p:cc]
        for item in ("references/plano.md", "PLANO.md", "previa-direcoes.mjs", "gate-plano.py", "obrigat"):
            self.assertIn(item, trecho, item)
        self.assertIn("gate-plano.py", c[c.find("## e."):c.find("## f.")])
        self.assertIn("gate-rastreamento.py", c[c.find("## f."):c.find("## g.")])
        s = ler(SKILL)
        for item in ("references/plano.md", "PLANO", "gate-plano.py", "gate-rastreamento.py", "previa-direcoes.mjs"):
            self.assertIn(item, s, item)
        self.assertRegex(s[:600], r"(?m)^version: 3\.[45]\.\d+$")
        self.assertIn("3.4.0", ler(RAIZ / "CHANGELOG.md"))

    def test_v34_plano_tem_as_sete_secoes(self):
        pl = ler(REF / "plano.md")
        for sec in ("Referências", "Visual", "Seções", "Copy", "Pixel e rastreamento", "Código e publicação", "Aprovação"):
            self.assertIn(sec, pl, sec)
        for item in ("frontend-design", "references/secoes/README.md", "references/rastreamento.md", "noindex"):
            self.assertIn(item, pl, item)
        r = ler(REF / "rastreamento.md")
        for ev in ("clique_whatsapp", "clique_cta", "rolagem_50", "rolagem_90", "envio_formulario", "data-evento"):
            self.assertIn(ev, r, ev)
        self.assertNotRegex(r, r"\bG-(?!X+\b)[A-Z0-9]{8,12}\b")
        self.assertNotRegex(r, r"\b\d{15,16}\b")


    # Padrão da v7 (04/10/2026): o que fez a v7 sair melhor que a v6 virou regra e gate, e o
    # SKILL.md continua curto: o detalhe mora nas references.
    def test_v35_skill_na_versao_e_curta(self):
        s = ler(SKILL)
        self.assertRegex(s[:600], r"(?m)^version: 3\.5\.\d+$")
        self.assertLessEqual(len(s.splitlines()), 330, "SKILL.md passou de ~330 linhas: o detalhe vai para references")
        for item in ("gate-ritmo.mjs", "gate-animacao.py", "anim.mjs", "prancha.py", "sobreposicao.mjs", "Momento assinatura",
                     "references/imagem.md", "references/ritmo-e-animacao.md", "references/densidade-servico-local.md",
                     "references/vh-estavel.md", "references/sticky-e-sobreposicao.md", "references/texto-em-linhas.md"):
            self.assertIn(item, s, item)
        self.assertIn("3.5.0", ler(RAIZ / "CHANGELOG.md"))

    def test_v35_plano_e_caminho_criar_cobram_o_padrao_da_v7(self):
        pl, c = ler(REF / "plano.md"), ler(CRIAR)
        for item in ("Momento assinatura:", "Composição por seção", "Material da cliente pedido:", "Seção | Desktop | Celular | Animação"):
            self.assertIn(item, pl, item)
        for item in ("Momento assinatura", "gate-ritmo.mjs", "anim.mjs", "prancha.py", "gate-animacao.py", "data-assimetrico",
                     "sobreposicao.mjs", "--vh", "references/imagem.md", "references/densidade-servico-local.md"):
            self.assertIn(item, c, item)
        self.assertIn("gate-ritmo", c[c.find("## f."):c.find("## g.")])
        self.assertIn("gate-animacao", c[c.find("## f."):c.find("## g.")])
        self.assertIn("anim.mjs", c[c.find("## e."):c.find("## f.")] + c[c.find("## f."):c.find("## g.")])

    def test_v35_references_curtas_existem_e_dizem_o_essencial(self):
        esperado = {
            "imagem.md": ("foto real", "ilustração", "60%", "pHash", "2,5", "RELATIVA", "--trafego-real", "primeira tela", "mesmo gênero", "data-ilustracao-ok"),
            "densidade-servico-local.md": ("nome e formação", "passo a passo", "para quem é", "para quem não é", "horários", "faixa de preço", "onde fica", "o que levar"),
            "vh-estavel.md": ("--vh", "innerHeight", "scroll-behavior", "fullPage"),
            "sticky-e-sobreposicao.md": ("sticky", "largura total", "sobreposicao.mjs", "grid"),
            "texto-em-linhas.md": ("li > span", "gate-texto", "data-linhas"),
            "ritmo-e-animacao.md": ("Momento assinatura", "gate-ritmo.mjs", "secoes.json", "anim.mjs", "prancha.py", "gate-animacao.py", "2%", "assinatura"),
        }
        for arq, itens in esperado.items():
            t = ler(REF / arq)
            self.assertLessEqual(len(t.splitlines()), 90, f"{arq} deveria ser curta")
            for item in itens:
                self.assertIn(item, t, f"{arq}: {item}")

    def test_v35_preferencias_e_readme_mencionam_o_novo(self):
        pref = ler(REF / "preferencias-de-design.md")
        for item in ("data-assimetrico", "foto real", "gate-ritmo.mjs"):
            self.assertIn(item, pref, item)
        r = ler(RAIZ / "README.md")
        for item in ("gate-ritmo.mjs", "gate-animacao.py", "anim.mjs", "test-animacao.py", "test-gates-v35.cjs"):
            self.assertIn(item, r, item)


class Travadas(unittest.TestCase):
    """As travadas do teste com aluno que continuam valendo na v3."""

    def test_t4_nenhum_comando_em_variavel_que_o_zsh_nao_roda(self):
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md", "references/caminhos/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.match(r'\s*[A-Z]+="(py|python|node|npx)\b', linha) or re.search(r'\$[A-Z]+ (registrar|gate|checar|rodada|dispensar)\b', linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])

    def test_t19_nenhum_caminho_fixo_na_pasta_do_dono(self):
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md", "references/caminhos/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"(~|\$HOME)/\.claude/skills/", linha) and not re.search(r"git clone|skills add", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
                if re.search(r"^SKILL=", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])

    def test_t19_dir_da_skill_explicado(self):
        self.assertRegex(ler(SKILL)[:6000], r"<dir-da-skill>.{0,40}(pasta|diret)")

    def test_t6_preferencias_genericas_existem_e_nao_citam_pessoa(self):
        pref = REF / "preferencias-de-design.md"
        self.assertTrue(pref.exists())
        texto = ler(pref)
        for nome in ("Júlio", "Julio", "Thales", "MaestrIA", "AutonomIA", "EA", "Operação Claude Code", "Laude"):
            self.assertNotRegex(texto, rf"\b{re.escape(nome)}\b", nome)
        for regra in ("kicker", "01/02/03", "número gigante", "inteira", "pricing", "lado a lado", "vermelho"):
            self.assertIn(regra.lower(), texto.lower(), regra)

    def test_t6_skill_e_scripts_falam_de_toda_pagina(self):
        ruins = []
        for p, t in textos("SKILL.md", "references/caminhos/*.md", "scripts/*.py", "scripts/*.js", "scripts/*.mjs", "hooks/*.py"):
            if p.name.startswith("test-"):
                continue
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"J[uú]lio|MaestrIA|preferencias-dono-ea|\(ex: EA\)", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])

    def test_t8_tipo_servico_local_com_stack_definida(self):
        pt = ler(REF / "page-types.md").lower()
        self.assertIn("servico-local", pt)
        self.assertRegex(pt, r"(?s)### servi[cç]o local.{0,500}stack definida: html \+ tailwind compilado")
        self.assertRegex(ler(CRIAR).lower(), r"stack padr[aã]o: html \+ tailwind compilado")

    def test_t16_modelo_curto_de_copy_para_servico_local(self):
        m = ler(REF / "copy-servico-local.md").lower()
        for parte in ("headline", "subt", "3 dores", "mecanismo", "como agendar", "formas", "dúvidas", "chamada final"):
            self.assertIn(parte, m, parte)
        d = ler(CRIAR)
        d = d[d.index("## d."):d.index("## e.")]
        self.assertIn("references/copy-servico-local.md", d)

    def test_t17_sem_cliente_ainda_diz_o_que_mostra_e_o_que_oculta(self):
        c = ler(CRIAR)
        i = c.find("Sem cliente ainda")
        self.assertGreater(i, 0)
        trecho = c[i:i + 900].lower()
        for item in ("mostra", "oculta", "hidden", "credencial", "foto", "cnpj", "placeholder"):
            self.assertIn(item, trecho, item)
        self.assertIn("sem cliente ainda", ler(REF / "copy-servico-local.md").lower())

    def test_t14_seo_abaixo_de_90_sob_noindex_e_esperado(self):
        f = ler(CRIAR)
        f = f[f.index("## f."):f.index("## g.")].lower()
        self.assertRegex(f, r"(?s)seo.{0,200}noindex")
        self.assertIn("esperado", f)
        self.assertIn("is-crawlable", f)

    def test_t15_movimento_em_css_por_padrao(self):
        e = ler(CRIAR)
        e = e[e.index("## e."):e.index("## f.")].lower()
        self.assertIn("movimento em css", e)
        self.assertNotRegex(ler(SKILL), r"(?i)higgsfield[^\n]{0,40}passo esperado")

    def test_t18_reregistrar_construcao_depois_dos_auditores_e_esperado(self):
        g = ler(REF / "gate-etapas.md").lower()
        self.assertRegex(g, r"(?s)etapa 4.{0,400}auditores.{0,400}esperado")
        self.assertIn("evidência mudou", g)

    def test_t21_acentuacao_no_texto_sem_tocar_em_codigo(self):
        sem = {"nao", "pagina", "paginas", "secao", "secoes", "voce", "tambem", "ja", "ate", "entao", "usuario",
               "codigo", "numero", "titulo", "botao", "preco", "conteudo", "obrigatorio", "padrao", "decisao",
               "direcao", "acao", "versao", "sessao", "video", "proprio", "unica", "unico", "visivel", "minimo",
               "maximo", "ultimo", "critico", "rapido", "publico", "trafego", "referencia", "pendencia", "regressao",
               "medicao", "composicao", "animacao", "atencao", "comecar", "servico", "estudio", "clinica",
               "consultorio", "saude", "facil", "possivel", "dificil", "necessario", "horario", "analise",
               "referencias", "construcao", "licenca"}
        fence_codigo = re.compile(r"\s*```\s*([\w+-]+)")
        ruins = []
        for p, t in textos("SKILL.md", "references/*.md", "references/caminhos/*.md"):
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


class RegrasDoTesteReal358(unittest.TestCase):
    """Achados N17, N18 e N20 do teste de página do zero (3.5.8): o que o texto do caminho `criar` não dizia."""

    def test_edicao_por_script_encadeia_com_e_comercial_duplo_antes_dos_gates(self):
        criar = ler(CRIAR)
        i = criar.index("edição por script")
        self.assertRegex(criar[i:i + 900], r"&&", "a edição por script tem que ser ligada aos gates com && (se o assert falha, os gates não rodam)")
        self.assertRegex(criar[i:i + 900], r"p[aá]gina velha")

    def test_roteiro_proprio_diz_os_limites_antes_de_gravar(self):
        criar = ler(CRIAR)
        for trecho in ("Roteiro próprio", "1 a 45", "10 a 90", "300 a 3000", "roteiro-demo-receitas.json"):
            self.assertIn(trecho, criar, f"criar.md: falta '{trecho}' na explicação do roteiro próprio")

    def test_clique_de_prova_em_link_externo_esta_explicado(self):
        criar = ler(CRIAR)
        self.assertRegex(criar, r"(?s)--click.*link (de WhatsApp|externo).*n[aã]o sai da p[aá]gina")


if __name__ == "__main__":
    unittest.main(verbosity=2)
