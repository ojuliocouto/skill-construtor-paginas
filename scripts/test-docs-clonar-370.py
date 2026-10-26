"""3.7.0 (26/10/2026), teste de aluno do CLONAR na 3.6.3: o clonar.md mandava "mesma construção do CRIAR, passo e" (156
linhas) sem dizer o que vale num clone, fazia a pergunta dos EIXOS de elevação, apontava para `prova/` quando o provar.mjs grava
em `provas/`, e não tinha medida de fidelidade nem rota de saída dos gates. Aqui se prova que o clonar.md diz cada coisa."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CLONAR = (RAIZ / "references" / "caminhos" / "clonar.md").read_text(encoding="utf-8")


class ClonarMd(unittest.TestCase):
    def test_diz_o_que_do_passo_e_vale_num_clone(self):
        self.assertIn("lente curta de gosto no herói", CLONAR.lower())
        self.assertRegex(CLONAR, r"[Ff]oto da original[^.\n]*não pede licença")
        self.assertNotIn("Mesma construção do CRIAR (`references/caminhos/criar.md`, passo e): HTML", CLONAR)

    def test_tailwind_nao_vence_a_css_da_original(self):
        self.assertIn("@tailwind utilities", CLONAR)
        self.assertIn('prefix: "tw-"', CLONAR)

    def test_gate_de_fidelidade_no_lugar_de_olhar_cor_a_cor(self):
        self.assertIn("gate-fidelidade.mjs", CLONAR)
        self.assertNotIn("confira cor a cor", CLONAR)
        self.assertIn("--modo fiel", CLONAR)
        self.assertNotIn("EIXOS", CLONAR)

    def test_uma_pasta_de_prova_so(self):
        self.assertNotRegex(CLONAR, r"<dir>/prova/")
        self.assertIn("<dir>/provas/prova-desktop.png", CLONAR)

    def test_gates_do_clone_com_rota_de_saida(self):
        self.assertIn("rodar-gates.mjs --projeto <dir> --caminho clonar", CLONAR)
        self.assertIn("ressalva por fidelidade", CLONAR)
        for g in ("verdade", "rastreamento", "plano", "referencias"):
            self.assertIn(f"`{g}`", CLONAR)

    def test_original_gravada_para_o_gate(self):
        self.assertIn("<dir>/original/identidade.json", CLONAR)

    def test_sem_travessao(self):
        self.assertIsNone(re.search("[\\u2013\\u2014]", CLONAR))


if __name__ == "__main__":
    unittest.main()
