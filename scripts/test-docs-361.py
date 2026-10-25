"""3.6.1 (25/10/2026): os quatro cortes de volta do teste de aluno da 3.6.0 (lente do herói em uma rodada, regressão trivial,
primeira tela em 320, tabela de sustentação por fato) precisam estar nos textos que o aluno e o agente leem.
O código de cada corte tem teste próprio; aqui se prova que o texto manda o que o código faz."""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
AUDITORES = RAIZ / "references" / "auditores.md"
SKILL = RAIZ / "SKILL.md"


def ler(p):
    return p.read_text(encoding="utf-8")


class Cortes361(unittest.TestCase):
    def test_lente_do_heroi_roda_uma_vez_com_teto_de_5_minutos(self):
        for arq in (CRIAR, AUDITORES):
            t = ler(arq)
            self.assertIn("gosto-heroi.py --projeto <dir> --registrar", t, arq.name)
            self.assertRegex(t, r"(?i)1 vez e não volta|uma rodada só|1 rodada só", arq.name)
        c = ler(CRIAR)
        self.assertIn("5 minutos", c)
        self.assertIn("pendencias-do-heroi.md", c)
        self.assertNotRegex(c, r"rode a lente uma vez mais")
        self.assertNotRegex(ler(AUDITORES), r"rode a lente uma vez mais")

    def test_regressao_trivial_tem_definicao_e_comando(self):
        c = ler(CRIAR)
        self.assertIn("--regressao-trivial", c)
        self.assertIn("--registrar-conserto", c)
        self.assertRegex(c, r"(?s)Regressão trivial não fecha o ciclo.{0,1500}não é achado crítico nem alto")
        self.assertIn("Crítico ou alto do auditor continua fechando o ciclo", c)
        self.assertIn("--regressao-trivial", ler(AUDITORES))

    def test_primeira_tela_em_320_e_a_tolerancia_estao_no_texto(self):
        c = ler(CRIAR)
        self.assertRegex(c, r"320x568 \(3\.6\.1\)")
        self.assertIn("tolerância de 0,5 ponto", c)
        self.assertIn("320x568", ler(SKILL))

    def test_tabela_de_sustentacao_e_uma_linha_por_fato_com_o_trecho_que_promete(self):
        c = ler(CRIAR)
        self.assertIn("uma linha por FATO", c)
        self.assertIn("TRECHO que\npromete", c)
        self.assertRegex(c, r"outro número, preço ou \"grátis\" na mesma frase ganha a própria linha")

    def test_sem_travessao_nem_meia_risca_nos_textos_novos(self):
        for arq in (CRIAR, AUDITORES, SKILL):
            self.assertNotRegex(ler(arq), "[—–]", arq.name)

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)


if __name__ == "__main__":
    unittest.main(verbosity=2)
