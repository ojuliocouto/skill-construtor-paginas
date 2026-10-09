"""3.5.13: os consertos da auditoria da 3.5.11 e da 3.5.12 (configurador visível em grupos, lista com caixa é cartão, "ao lado" só com
coluna irmã, sequência de estados amarrada ao PLANO.md) precisam estar nos textos que o aluno e o agente leem, e a versão tem que ser
a 3.5.13. Os gates têm testes próprios (test-ritmo-3513.cjs, test-imagens.py)."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL, README, CHANGELOG = RAIZ / "SKILL.md", RAIZ / "README.md", RAIZ / "CHANGELOG.md"
RITMO = RAIZ / "references" / "ritmo-e-animacao.md"
RECEITAS = RAIZ / "references" / "receitas-de-movimento.md"
RODAR = RAIZ / "scripts" / "rodar-testes.mjs"
GATES = [RAIZ / "scripts" / "gate-ritmo.mjs", RAIZ / "scripts" / "gate-imagens.py"]


def ler(p):
    return p.read_text(encoding="utf-8")


def plano(t):
    return re.sub(r"\s+", " ", t)


class Versao3513(unittest.TestCase):
    def test_versao_nos_tres_lugares(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.13$")
        self.assertIn("router (v3.5.13)", ler(README))
        self.assertNotIn("router (v3.5.12)", ler(README))
        self.assertTrue(ler(CHANGELOG).startswith("# Changelog\n\n## 3.5.13"))
        self.assertIn("## What is new in 3.5.13", ler(README))

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_nenhum_travessao(self):
        for p in (SKILL, README, CHANGELOG, RITMO, RECEITAS, RAIZ / "scripts" / "test-ritmo-3513.cjs", *GATES):
            self.assertNotIn("\u2014", ler(p), p.name)

    def test_changelog_diz_o_que_resolve_e_o_que_nao_foi_provado(self):
        t = ler(CHANGELOG)
        sec = plano(t[t.index("## 3.5.13"):t.index("## 3.5.12")])
        for item in ("Achado 1", "Achado 2", "Achados 4 e 5", "Achado 3", "Achado 6", "achado 7", "PLANO.md", "test-ritmo-3513.cjs",
                     "Torra Clara", "Não foi provado", "reproduziram"):
            self.assertIn(item, sec, item)


class Textos(unittest.TestCase):
    def test_referencia_de_ritmo_explica_as_tres_regras(self):
        t = plano(ler(RITMO))
        for item in ("VISÍVEIS", "só uma coluna", "caixa própria", "coluna irmã", "`PLANO.md` declara", "ordem crescente"):
            self.assertIn(item, t, item)

    def test_receita_diz_que_o_plano_declara_os_estados(self):
        self.assertIn("`PLANO.md` precisa declarar o `Momento assinatura`", plano(ler(RECEITAS)))

    def test_o_teste_novo_esta_registrado_na_suite(self):
        self.assertIn("test-ritmo-3513.cjs", ler(RODAR))

    def test_gates_documentam_o_conserto_no_cabecalho(self):
        self.assertIn("3.5.13", ler(GATES[0]))
        self.assertIn("3.5.13", ler(GATES[1]))


if __name__ == "__main__":
    unittest.main()
