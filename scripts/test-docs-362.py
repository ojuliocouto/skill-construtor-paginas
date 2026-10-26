"""3.6.2 (25/10/2026): os consertos do teste de aluno da 3.6.1 precisam estar nos textos que o aluno e o agente leem.
O código de cada conserto tem teste próprio (test-wave.py, test-responsivo-362.cjs, test-gate-verdade.py, test-provar.cjs);
aqui se prova que o texto manda o que o código faz. Por variável de ambiente, SKILL_RAIZ aponta para outra cópia da skill
(serve para provar que estes testes reprovam contra a 3.6.1)."""
import os
import pathlib
import re
import unittest

RAIZ = pathlib.Path(os.environ.get("SKILL_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
REFS = RAIZ / "references"
SKILL = RAIZ / "SKILL.md"


def ler(p):
    return p.read_text(encoding="utf-8")


class Consertos362(unittest.TestCase):
    def test_regressao_sem_gate_tem_a_regra_o_comando_e_o_exemplo(self):
        c = ler(CRIAR)
        self.assertIn("--regressao-trivial-sem-gate", c)
        self.assertRegex(c, r"(?s)Regressão sem gate também não fecha o ciclo.{0,2500}print NOVO")
        self.assertRegex(c, r"--regressao-trivial-sem-gate \"coluna sozinha no celular:medio:prints/celular-depois\.png\"")
        self.assertIn("Crítico e alto continuam fechando o ciclo", c)
        self.assertIn("MESMO `wave.py rodada`", c)

    def test_servidor_pede_porta_livre_e_nenhuma_porta_fixa_fica_nos_comandos(self):
        c = ler(CRIAR)
        self.assertRegex(c, r"servidor-gzip\.py <dir> 0")
        for arq in (CRIAR, *sorted(REFS.glob("*.md"))):
            self.assertNotIn("localhost:8765", ler(arq), arq.name)
        self.assertNotIn("8765", c)

    def test_lente_do_heroi_passa_o_celular(self):
        c = ler(CRIAR)
        self.assertRegex(c, r"gosto-heroi\.py --projeto <dir> --heroi <dir>/prova-hero/prova-desktop\.png --celular <dir>/prova-hero/prova-mobile\.png")

    def test_botao_em_320_tem_tolerancia_so_nessa_tela(self):
        c = ler(CRIAR)
        self.assertRegex(c, r"Botão do herói em 320x568 \(3\.6\.2\):[^\n]*12 px")
        self.assertIn("em 390 (844 e 664), 360, 430 e no desktop o botão cortado reprova como sempre", c)

    def test_a_dobra_do_celular_e_uma_janela_so(self):
        c = ler(CRIAR)
        self.assertIn("--salvar-dobra", c)
        self.assertRegex(c, r"Nunca recorte as primeiras\s+linhas do print de página inteira")
        self.assertRegex(c, r"a dobra do celular NÃO é o recorte do topo deles")

    def test_nao_afirmar_casa_no_comeco_da_palavra(self):
        c = ler(CRIAR)
        self.assertRegex(c, r"`cura` pega \"cura\" e \"curar\" e não pega \"procura\"")

    def test_prova_de_animacao_se_refaz_com_o_provar(self):
        c = ler(CRIAR)
        self.assertIn("provar.mjs --projeto <dir> --so animacao", c)

    def test_sem_travessao_nem_meia_risca_nos_textos_novos(self):
        for arq in (CRIAR, SKILL):
            self.assertNotRegex(ler(arq), "[—–]", arq.name)

    def test_skill_md_nao_passa_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)


if __name__ == "__main__":
    unittest.main(verbosity=2)
