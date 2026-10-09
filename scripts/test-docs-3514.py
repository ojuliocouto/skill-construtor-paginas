"""3.5.14: os consertos dos achados baixos 10, 11 e 12 da auditoria da 3.5.11 e da 3.5.12 (mensagem certa para a mesma foto do estado,
fechamentos implícitos do HTML no parser do gate de imagens, asserções exatas) precisam estar nos textos que o aluno e o agente leem,
e a versão tem que ser a 3.5.14. O gate tem teste próprio (test-imagens.py)."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL, README, CHANGELOG = RAIZ / "SKILL.md", RAIZ / "README.md", RAIZ / "CHANGELOG.md"
GATE = RAIZ / "scripts" / "gate-imagens.py"


def ler(p):
    return p.read_text(encoding="utf-8")


def plano(t):
    return re.sub(r"\s+", " ", t)


class Versao3514(unittest.TestCase):
    def test_versao_nos_tres_lugares(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.14$")
        self.assertIn("router (v3.5.14)", ler(README))
        self.assertNotIn("router (v3.5.13)", ler(README))
        self.assertTrue(ler(CHANGELOG).startswith("# Changelog\n\n## 3.5.14"))
        self.assertIn("## What is new in 3.5.14", ler(README))

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_nenhum_travessao(self):
        for p in (SKILL, README, CHANGELOG, GATE, pathlib.Path(__file__)):
            self.assertNotIn("\u2014", ler(p), p.name)

    def test_changelog_diz_o_que_resolve_e_o_que_nao_foi_provado(self):
        t = ler(CHANGELOG)
        sec = plano(t[t.index("## 3.5.14"):t.index("## 3.5.13")])
        for item in ("Achado 10", "Achado 11", "Achado 12", "achado 9", "test_estado_zero_reprova", "fechamentos implícitos", "MESMA foto",
                     "Não foi provado"):
            self.assertIn(item, sec, item)

    def test_gate_documenta_o_conserto_no_cabecalho(self):
        self.assertIn("3.5.14", ler(GATE))


if __name__ == "__main__":
    unittest.main()
