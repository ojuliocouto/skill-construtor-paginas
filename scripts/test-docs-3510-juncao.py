"""3.5.10, junção das frentes A, B, C e do P11: o texto proposto por cada frente tem que estar no SKILL.md, no criar.md,
no README e no CHANGELOG, e a versão tem que ser a 3.5.10 em todos os lugares onde a 3.5.9 era a atual.

Texto não roda sozinho: o que dá para medir no texto vira asserção. O teto de 330 linhas do SKILL.md não se afrouxa
(o que não coube foi para o criar.md).
"""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
README = RAIZ / "README.md"
CHANGELOG = RAIZ / "CHANGELOG.md"


def ler(p):
    return p.read_text(encoding="utf-8")


def linha_da_tabela(texto, script):
    achadas = [l for l in texto.splitlines() if l.startswith(f"| `{script}`")]
    assert len(achadas) == 1, (script, achadas)
    return achadas[0]


def trecho(texto, ini, fim):
    i = texto.index(ini)
    return texto[i:texto.index(fim, i + 1)]


class SkillMd(unittest.TestCase):
    def test_teto_de_330_linhas_nao_se_afrouxa(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_b_gate_plano_confere_o_tipo_da_animacao(self):
        l = linha_da_tabela(ler(SKILL), "gate-plano.py")
        self.assertRegex(l, r"(?i)tipo da anima")
        self.assertIn("criação nova", l)
        self.assertRegex(l, r"(?i)receita")

    def test_b_gate_relatorio_aceita_marcador_de_historico(self):
        l = linha_da_tabela(ler(SKILL), "gate-relatorio.py")
        self.assertIn("rodada 1:", l)
        self.assertIn("antes:", l)

    def test_c_gate_responsivo_mede_a_primeira_tela_visivel(self):
        l = linha_da_tabela(ler(SKILL), "gate-responsivo.mjs")
        for item in ("primeira tela visível", "390x664", "360x616", "375x553", "manchete", "texto de apoio", "botão", "20%"):
            self.assertIn(item, l, item)

    def test_c_gate_oclusao_mede_por_linha(self):
        l = linha_da_tabela(ler(SKILL), "gate-oclusao.mjs")
        self.assertRegex(l, r"linha recortada|linha a linha")

    def test_c_gate_movimento_mede_texto_invisivel(self):
        l = linha_da_tabela(ler(SKILL), "gate-movimento.mjs")
        for item in ("invisível", "4 s", "salto", "--so-visibilidade"):
            self.assertIn(item, l, item)

    def test_p11_servidor_escolhe_porta_livre_e_gate_diz_servidor_fora(self):
        l = linha_da_tabela(ler(SKILL), "servidor-gzip.py")
        self.assertRegex(l, r"(?i)porta (ocupada|livre)")
        self.assertIn("URL:", l)
        self.assertIn("servidor fora do ar", ler(SKILL))


class CriarMd(unittest.TestCase):
    def setUp(self):
        self.c = ler(CRIAR)
        self.f = trecho(self.c, "## f. Gates mecânicos", "\n## g.")

    def test_p11_passo_f_porta_e_url_impressa_e_servidor_fora(self):
        for item in ("URL: http://127.0.0.1:", "servidor fora do ar em", "saída 3", "porta ocupada"):
            self.assertIn(item, self.f, item)
        # o servidor sobe antes da lista de comandos e diz que 8765 é só o exemplo
        self.assertRegex(self.f, r"(?is)8765[^\n]*(exemplo|preferência)|(exemplo|preferência)[^\n]*8765")

    def test_p11_passo_f_montar_dist_nao_derruba_o_servidor(self):
        self.assertRegex(self.f, r"(?is)montar-dist[^\n]*\n?[^\n]*(mant[eé]m a pasta|n[ãa]o apaga|segue no ar)")

    def test_b_gate_relatorio_historia_do_trabalho(self):
        i = self.c.index("**Relatório só com medida gravada:**")
        t = self.c[i:i + 2500]
        self.assertIn("rodada N:", t)
        self.assertIn("antes:", t)
        self.assertRegex(t, r"(?i)n[ãa]o cobra a `dist/`|n[ãa]o pode falar do estado atual")

    def test_b_plano_coluna_animacao_comeca_pelo_nome_da_receita(self):
        i = self.c.index("## b2. PLANO")
        t = self.c[i:self.c.index("## c.", i)]
        self.assertIn("coluna Animação", t)
        self.assertIn("criação nova: <motivo", t)
        self.assertIn("assinatura", t)

    def test_b_revalidar_grava_as_anteriores(self):
        i = self.c.index("## Mudança de briefing no meio do trabalho")
        t = self.c[i:]
        self.assertRegex(t, r"(?i)bloquear numa etapa, as anteriores ficam gravadas")

    def test_c_topo_do_celular_na_area_que_a_pessoa_ve(self):
        self.assertIn("Topo do celular na área que a pessoa vê", self.c)
        self.assertIn("390x664", self.c)
        self.assertNotIn("**Foto do herói na primeira tela do celular** com\n   pelo menos 35% da altura", self.c)
        self.assertRegex(self.c, r"(?i)o texto ganha")

    def test_c_responsivo_so_primeira_tela(self):
        l = [x for x in self.f.splitlines() if "gate-responsivo.mjs --url" in x]
        self.assertEqual(len(l), 1, l)
        self.assertIn("3 primeiras telas visíveis", l[0])
        self.assertIn("--so-primeira-tela", l[0])

    def test_c_movimento_invisivel_e_base_minima(self):
        l = [x for x in self.f.splitlines() if "gate-movimento.mjs --url" in x]
        self.assertEqual(len(l), 1, l)
        for item in ("invisível", "primeiraTela", "jaPassou", "--so-visibilidade"):
            self.assertIn(item, l[0], item)
        i = self.c.index("3. **Movimento em CSS:**")
        t = self.c[i:i + 4500]
        for item in ("`revelar`", "`primeiraTela`", "`jaPassou`", "`observar`", "clip-path", "produto-em-estados"):
            self.assertIn(item, t, item)


class Readme(unittest.TestCase):
    def test_a_readme_nao_diz_que_a_captura_nunca_clica_em_cookies(self):
        t = ler(README)
        self.assertNotRegex(t, r"never clicks cookie")
        linha = [l for l in t.splitlines() if l.startswith("- The reference capture")]
        self.assertEqual(len(linha), 1, linha)
        self.assertRegex(linha[0], r"(?i)declin")
        self.assertRegex(linha[0], r"(?i)last resort")
        self.assertRegex(linha[0], r"(?i)left the screen")

    def test_readme_versao_e_novidades(self):
        t = ler(README)
        self.assertIn("router (v3.5.13)", t)
        self.assertNotIn("router (v3.5.11)", t)
        self.assertNotIn("router (v3.5.10)", t)
        self.assertIn("## What is new in 3.5.10", t)
        self.assertNotIn("router (v3.5.9)", t)
        self.assertRegex(t, r"17 motion recipes")
        sec = trecho(t, "## What is new in 3.5.10", "## What is new in 3.5.9")
        for item in ("visible first screen", "664", "servidor-gzip", "not proven"):
            self.assertIn(item, sec.lower(), item)


class Versao(unittest.TestCase):
    def test_skill_na_3_5_13_a_3_5_10_virou_historia(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.13$")

    def test_changelog_3_5_10_junta_as_frentes_e_diz_o_que_nao_foi_provado(self):
        t = ler(CHANGELOG)
        self.assertTrue(t.startswith("# Changelog\n\n## 3.5.13"), t[:80])
        self.assertIn("\n## 3.5.10 (09/10/2026)", t)
        sec = trecho(t, "## 3.5.10", "## 3.5.9")
        for item in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17",
                     "P18", "P19", "P20", "P21", "G22"):
            self.assertRegex(sec, rf"\b{item}\b", item)
        i = sec.index("Não foi provado")
        nao = sec[i:]
        for item in ("664", "Playwright", "Omsom", "v7"):
            self.assertIn(item, nao, item)

    def test_nenhum_travessao(self):
        for p in (SKILL, README, CHANGELOG, CRIAR):
            self.assertNotIn("—", ler(p), p.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
