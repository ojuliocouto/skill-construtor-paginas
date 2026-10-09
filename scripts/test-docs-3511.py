"""3.5.11: a variante de 3 fotos do momento assinatura (P5) precisa estar nos textos que o aluno e o agente leem, e a versão
tem que ser a 3.5.11 onde a 3.5.10 era a atual (a 3.5.12 já é a atual: os testes de versão olham o histórico). O gate e a receita têm testes próprios (test-imagens.py, test-receitas.py)."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL, README, CHANGELOG = RAIZ / "SKILL.md", RAIZ / "README.md", RAIZ / "CHANGELOG.md"
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
RITMO = RAIZ / "references" / "ritmo-e-animacao.md"
MD = RAIZ / "references" / "receitas-de-movimento.md"


def ler(p):
    return p.read_text(encoding="utf-8")


def plano(t):
    return re.sub(r"\s+", " ", t)


class Versao3511(unittest.TestCase):
    def test_versao_nos_tres_lugares(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.14$")
        self.assertIn("router (v3.5.14)", ler(README))
        self.assertIn("\n## 3.5.11 (09/10/2026)", ler(CHANGELOG))
        self.assertIn("## What is new in 3.5.11", ler(README))

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_nenhum_travessao(self):
        for p in (SKILL, README, CHANGELOG, CRIAR, RITMO, MD):
            self.assertNotIn("—", ler(p), p.name)

    def test_changelog_diz_o_que_resolve_e_o_que_nao_foi_provado(self):
        t = ler(CHANGELOG)
        sec = t[t.index("## 3.5.11"):t.index("## 3.5.10")]
        for item in ("P5", "data-assinatura-estado", "regra 13", "Torra Clara", "continua reprovando", "Não foi provado", "17 receitas"):
            self.assertIn(item, plano(sec), item)


class TextosDaVariante(unittest.TestCase):
    def test_skill_md_cita_a_sequencia_na_linha_do_gate_de_imagens(self):
        linhas = [l for l in ler(SKILL).splitlines() if l.startswith("| `gate-imagens.py`")]
        self.assertEqual(len(linhas), 1)
        self.assertIn("data-assinatura-estado", linhas[0])

    def test_criar_md_ensina_a_variante_e_proibe_data_assinatura_simples_em_fotos_diferentes(self):
        t = plano(ler(CRIAR))
        self.assertIn("variante de 3 fotos", t)
        self.assertIn('data-assinatura-estado="1"', t)
        self.assertRegex(t, r"nunca `data-assinatura` simples em fotos diferentes")
        i = t.index("gate-imagens.py --projeto")
        self.assertIn("data-assinatura-estado", t[i:i + 900], "a linha do gate no criar.md cita a exceção")

    def test_ritmo_e_animacao_explica_a_regra_13(self):
        t = plano(ler(RITMO))
        self.assertIn("a sequência de estados (3.5.11)", t)
        for item in ("regra 13", "de 2 a 4 estados", "sem buraco", "um momento assinatura só", "produto-em-estados"):
            self.assertIn(item, t, item)

    def test_a_docstring_do_gate_documenta_a_regra_13(self):
        g = (RAIZ / "scripts" / "gate-imagens.py").read_text(encoding="utf-8")[:9000]
        self.assertIn("13. SEQUÊNCIA DE ESTADOS", g)
        self.assertIn("data-assinatura-estado", g)


if __name__ == "__main__":
    unittest.main(verbosity=2)
