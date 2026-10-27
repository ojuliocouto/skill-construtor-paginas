"""3.6.0 (25/10/2026): velocidade (cache de gate, hash no lugar da data, paralelo, tempo-limite de 10 min) e
brechas de cara de IA (filete, enfeite de título, motivo repetido, profissão, lente curta do herói) precisam estar
nos textos que o aluno e o agente leem, e a versão tem que ser a 3.6.0. Os gates têm testes próprios."""
import pathlib
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL, README, CHANGELOG = RAIZ / "SKILL.md", RAIZ / "README.md", RAIZ / "CHANGELOG.md"
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"


def ler(p):
    return p.read_text(encoding="utf-8")


class Versao360(unittest.TestCase):
    def test_versao_nos_tres_lugares(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.8\.0$")
        self.assertIn("router (v3.8.0)", ler(README))
        self.assertIn("\n## 3.6.0", ler(CHANGELOG))  # a atual é a 3.6.1
        self.assertIn("## What is new in 3.6.0", ler(README))

    def test_criar_manda_a_lente_do_heroi_como_conselho(self):
        t = ler(CRIAR)
        self.assertIn("gosto-heroi.py --projeto <dir> --heroi", t)
        self.assertIn("conselho, não trava", t)

    def test_criar_manda_rodar_gates_em_primeiro_plano_com_10_minutos(self):
        self.assertIn("600000", ler(CRIAR))

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)


if __name__ == "__main__":
    unittest.main(verbosity=2)
