"""3.7.0 (26/10/2026), teste de aluno do CLONAR na 3.6.3: clone de pocketbase.io com 0,054% de pixels diferentes em 1440,
e `wave.py --caminho clonar checar` deu ENTREGA BLOQUEADA com 8 gates vermelhos (movimento, responsivo, imagens, texto,
verdade, rastreamento, plano, referencias).

Aqui se prova, no wave.py:
  1. no clone, verdade, rastreamento, plano e referencias não são exigidos, e o registro vermelho deles não bloqueia;
  2. movimento, responsivo, texto e imagens vermelhos viram RESSALVA por fidelidade: não bloqueiam e entram nas ressalvas da entrega;
  3. o gate de fidelidade é exigido no clone e só nele (o CRIAR não muda);
  4. fidelidade, oclusão, classes mortas e publicação vermelhos continuam bloqueando no clone.
"""
import argparse
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wave_clonar", pathlib.Path(__file__).with_name("wave.py"))
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)

VERMELHOS_DO_ALUNO = ("movimento", "responsivo", "imagens", "texto", "verdade", "rastreamento", "plano", "referencias")


class Clonar(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def montar(self, vermelhos=VERMELHOS_DO_ALUNO, sem=()):
        lentes = {n: {"nota": 8.5, "veredito": "aprovado", "origem": "subagente", "gosto": "bonito",
                      "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES}
        gates = {n: {"exit": 1 if n in vermelhos else 0, "detalhe": f"rodar-gates r4: {'REPROVA' if n in vermelhos else 'PASSA'}",
                     "quando": "2026-10-26T13:30:00"} for n in wave.GATES if n not in sem}
        wave.salvar(self.projeto, {"lentes": lentes, "gates": gates})

    def checar(self, caminho):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_checar(argparse.Namespace(projeto=self.projeto, caminho=caminho))
        return code, saida.getvalue()

    def test_os_8_vermelhos_do_aluno_nao_bloqueiam_o_clone(self):
        self.montar()
        code, out = self.checar("clonar")
        self.assertEqual(code, 0, out)
        self.assertIn("RESSALVA", out)
        for g in ("movimento", "responsivo", "imagens", "texto"):
            self.assertIn(g, out)

    def test_os_mesmos_vermelhos_bloqueiam_o_criar(self):
        self.montar(sem=("fidelidade",))
        code, out = self.checar("criar")
        self.assertEqual(code, 1, out)
        self.assertIn("BLOQUEIA", out)

    def test_fora_do_clone_nao_e_exigido(self):
        exig = wave.gates_exigidos("clonar")
        for g in ("verdade", "rastreamento", "plano", "referencias"):
            self.assertNotIn(g, exig, g)

    def test_fidelidade_so_no_clone(self):
        self.assertIn("fidelidade", wave.gates_exigidos("clonar"))
        for c in ("criar", "clonar-elevar", "melhorar", "variante"):
            self.assertNotIn("fidelidade", wave.gates_exigidos(c), c)

    def test_clone_sem_fidelidade_registrada_bloqueia(self):
        self.montar(sem=("fidelidade",))
        code, out = self.checar("clonar")
        self.assertEqual(code, 1, out)
        self.assertIn("fidelidade", out)

    def test_comando_que_destrava_o_clone_leva_o_caminho(self):
        self.montar(sem=("fidelidade",))
        code, out = self.checar("clonar")
        self.assertEqual(code, 1, out)
        self.assertIn("--caminho clonar", out)

    def test_gates_que_bloqueiam_no_clone(self):
        for g in ("fidelidade", "oclusao", "classes-mortas", "publicacao"):
            self.montar(vermelhos=VERMELHOS_DO_ALUNO + (g,))
            code, out = self.checar("clonar")
            self.assertEqual(code, 1, f"{g}: {out}")

    def test_rodada_entrega_com_as_ressalvas_por_fidelidade(self):
        self.montar()
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(io.StringIO()):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, caminho="clonar", criticos=0, altos=0,
                                                      regressoes=0, pendencias_do_usuario=0))
        self.assertEqual(code, 0, saida.getvalue())
        self.assertIn("ENTREGA", saida.getvalue())
        ultima = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertTrue(ultima["desfecho"].startswith("ENTREGA"), ultima)
        texto = " ".join(ultima.get("ressalvas") or [])
        for g in ("movimento", "responsivo", "imagens", "texto"):
            self.assertIn(f"gate {g} vermelho, ressalva por fidelidade", texto)
        self.assertIn("--caminho clonar", saida.getvalue())   # o comando da rodada completa é o do clone


if __name__ == "__main__":
    unittest.main()
