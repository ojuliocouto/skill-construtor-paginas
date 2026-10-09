"""3.5.12: o conserto do gate-ritmo (configurador e colunas de perguntas não são cartões; "ao lado" exige sobreposição vertical)
precisa estar nos textos que o aluno e o agente leem, e a 3.5.12 é história (a atual é a 3.5.14, test-docs-3514.py). O gate tem teste próprio (test-ritmo-3512.cjs)."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL, README, CHANGELOG = RAIZ / "SKILL.md", RAIZ / "README.md", RAIZ / "CHANGELOG.md"
RITMO = RAIZ / "references" / "ritmo-e-animacao.md"
GATE = RAIZ / "scripts" / "gate-ritmo.mjs"
RODAR = RAIZ / "scripts" / "rodar-testes.mjs"


def ler(p):
    return p.read_text(encoding="utf-8")


def plano(t):
    return re.sub(r"\s+", " ", t)


class Versao3512(unittest.TestCase):
    def test_versao_nos_tres_lugares(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.5\.14$")
        self.assertIn("router (v3.5.14)", ler(README))
        self.assertNotIn("router (v3.5.13)", ler(README))
        self.assertIn("\n## 3.5.12 (09/10/2026)", ler(CHANGELOG))
        self.assertIn("## What is new in 3.5.12", ler(README))

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_nenhum_travessao(self):
        for p in (SKILL, README, CHANGELOG, RITMO, GATE):
            self.assertNotIn("—", ler(p), p.name)

    def test_changelog_diz_o_que_resolve_e_o_que_nao_foi_provado(self):
        t = ler(CHANGELOG)
        sec = plano(t[t.index("## 3.5.12"):t.index("## 3.5.11")])
        for item in ("configurador", "lista", "663", "486", "0,73", "sobreposição vertical", "P18", "Torra Clara", "continuam reprovando",
                     "Não foi provado", "test-ritmo-3512.cjs", "gate antigo"):
            self.assertIn(item, sec, item)


class Textos(unittest.TestCase):
    def test_linha_do_gate_na_skill_cita_os_tipos_de_corpo(self):
        linhas = [l for l in ler(SKILL).splitlines() if l.startswith("| `gate-ritmo.mjs`")]
        self.assertEqual(len(linhas), 1)
        self.assertIn("configurador", linhas[0])

    def test_referencia_de_ritmo_explica_configurador_lista_e_ao_lado(self):
        t = plano(ler(RITMO))
        for item in ("configurador", "4 ou mais controles", "`details`", "lista", "mesma altura", "ABAIXO de um título curto"):
            self.assertIn(item, t, item)

    def test_o_teste_novo_esta_registrado_na_suite(self):
        self.assertIn("test-ritmo-3512.cjs", ler(RODAR))

    def test_gate_documenta_os_dois_conserto_no_cabecalho(self):
        t = ler(GATE)
        self.assertIn("configurador (3.5.12", t)
        self.assertIn("sobreposição vertical de pelo menos 24 px", plano(t))


if __name__ == "__main__":
    unittest.main()
