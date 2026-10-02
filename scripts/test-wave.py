"""Controles do ciclo com entradas reais do registro, sem serviços externos."""
import argparse
import contextlib
import importlib.util
import io
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("wave", pathlib.Path(__file__).with_name("wave.py"))
wave = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wave)


class Ciclo(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.projeto = self.temp.name

    def executar(self, nota=8, criticos=0, regressoes=0, gates=True, altos=1, pendencias=0):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": nota, "veredito": "aprovado", "achados": "Inspeção da página com evidência de teste"} for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES} if gates else {},
        })
        with contextlib.redirect_stdout(io.StringIO()):
            return wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=criticos, altos=altos,
                                                      regressoes=regressoes, pendencias_do_usuario=pendencias))

    def test_positivo_piso(self):
        self.assertEqual(self.executar(), 0)

    def test_negativo_critico(self):
        self.assertEqual(self.executar(criticos=1), 1)

    def test_negativo_regressao(self):
        self.assertEqual(self.executar(regressoes=1), 1)

    def test_primeira_rodada_baixa_orienta_sem_excecao(self):
        self.assertEqual(self.executar(nota=6), 1)

    def test_nota_infinita_nao_aprova(self):
        self.assertNotEqual(self.executar(nota=float("inf")), 0)

    def test_contagem_negativa_nao_aprova(self):
        self.assertNotEqual(self.executar(criticos=-1), 0)

    def test_alto_que_depende_do_cliente_nao_segura_o_ciclo(self):
        # Relatorio do aluno: numero do WhatsApp e prova social so a cliente tem. Sem o campo,
        # "zero alto" nunca fica verdadeiro e so o teto de 4 rodadas solta.
        self.assertEqual(self.executar(nota=6, altos=2, pendencias=2), 0)

    def test_pendencia_do_usuario_nao_apaga_alto_de_verdade(self):
        self.assertEqual(self.executar(nota=6, altos=3, pendencias=2), 1)

    def test_pendencia_maior_que_altos_e_erro(self):
        self.assertNotEqual(self.executar(nota=6, altos=1, pendencias=2), 0)

    def test_pendencia_vai_para_o_historico(self):
        self.executar(nota=6, altos=2, pendencias=2)
        rodada = wave.carregar(self.projeto)["rodadas"][-1]
        self.assertEqual(rodada.get("pendencias_do_usuario"), 2)

    def test_sem_gates_nao_entrega(self):
        self.assertNotEqual(self.executar(gates=False), 0)

    # v3: a nona lente compara a página com as referências printadas no passo b.
    def test_nona_lente_comparacao_com_referencias_existe(self):
        self.assertIn("comparacao-referencias", wave.LENTES)
        self.assertEqual(len(wave.LENTES), 9)
        self.assertIn("referencias", wave.GATES)

    def test_abaixo_das_referencias_volta_pro_plano_mesmo_com_nota_alta(self):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": 9, "veredito": "aprovado", "achados": "Inspeção da página com evidência de teste"}
                       for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES},
        })
        d = wave.carregar(self.projeto)
        d["lentes"]["comparacao-referencias"]["veredito"] = "reprovado"
        wave.salvar(self.projeto, d)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            code = wave.cmd_rodada(argparse.Namespace(projeto=self.projeto, criticos=0, altos=0,
                                                      regressoes=0, pendencias_do_usuario=0))
        self.assertEqual(code, 1)
        self.assertIn("plano visual", saida.getvalue().lower())

    def test_comparacao_com_referencias_nao_aceita_nao_aplicavel(self):
        with contextlib.redirect_stderr(io.StringIO()):
            code = wave.cmd_registrar(argparse.Namespace(projeto=self.projeto, lente="comparacao-referencias",
                                                         veredito="nao_aplicavel", nota=None,
                                                         achados="Não comparei porque não tinha referência"))
        self.assertEqual(code, 2)

    def test_caminho_clonar_nao_exige_gate_de_referencias(self):
        wave.salvar(self.projeto, {
            "lentes": {n: {"nota": 9, "veredito": "aprovado", "achados": "Inspeção da página com evidência de teste"}
                       for n in wave.LENTES},
            "gates": {n: {"exit": 0, "detalhe": "Controle positivo"} for n in wave.GATES if n != "referencias"},
        })
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wave.cmd_checar(argparse.Namespace(projeto=self.projeto, caminho="clonar")), 0)
            self.assertEqual(wave.cmd_checar(argparse.Namespace(projeto=self.projeto, caminho="criar")), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
