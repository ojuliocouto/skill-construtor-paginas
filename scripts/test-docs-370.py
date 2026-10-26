"""3.7.0 (26/10/2026): o passo g mais rápido precisa estar nos textos que o agente lê.

O código de cada item tem teste próprio (test-wave-370.py, test-pacote-370.py, test-rodar-gates-370.cjs, test-etapa5-370.py,
test-gosto-heroi.py, test-responsivo-362.cjs); aqui se prova que o texto manda o que o código faz. SKILL_RAIZ aponta para outra
cópia da skill (serve para provar que estes testes reprovam contra a 3.6.3)."""
import os
import pathlib
import unittest

RAIZ = pathlib.Path(os.environ.get("SKILL_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
AUD = RAIZ / "references" / "auditores.md"


def ler(p):
    return p.read_text(encoding="utf-8")


def secao(texto, inicio, fim):
    return texto[texto.index(inicio):texto.index(fim, texto.index(inicio))]


class Docs370(unittest.TestCase):
    def test_orcamento_novo_nos_dois_textos(self):
        for arq in (CRIAR, AUD):
            t = ler(arq)
            for trecho in ("8 minutos", "12 chamadas", "3 minutos", "4 chamadas"):
                self.assertIn(trecho, t, f"{arq.name}: {trecho}")
            self.assertNotIn("15 minutos e 30 chamadas", t, arq.name)
            self.assertNotIn("6 capturas próprias", t, arq.name)

    def test_rodada_1_le_o_pacote_e_nao_captura(self):
        a = ler(AUD)
        self.assertIn("Não capture nada", a)
        self.assertRegex(a, r"(?s)gate verde.{0,400}só o que o gate não mede")
        self.assertIn("hierarquia, gosto, coerência com o briefing e cara de IA", a)

    def test_rodada_2_e_conferencia_dirigida_sem_nota(self):
        a = ler(AUD)
        r2 = secao(a, "## Rodada 2", "## As 9 lentes")
        for trecho in ("críticos e altos", "print novo", "diff da dist", "Sem nota nova", "wave.py --projeto <dir> conferencia",
                       "auditoria/correcoes-rodada-1.json"):
            self.assertIn(trecho, r2, trecho)
        c = ler(CRIAR)
        g = secao(c, "## g. Auditores", "## h. Prova")
        self.assertIn("conferencia --arquivo auditoria/resposta-rodada-2.json", g)
        self.assertIn("pacote-auditoria.py --projeto <dir> --url <url> --rodada 2", g)

    def test_sem_critico_nem_alto_nao_ha_rodada_2(self):
        for arq in (CRIAR, AUD):
            t = ler(arq)
            self.assertRegex(t, r"(?i)sem (achado )?crítico nem alto.{0,200}(não há|sem) rodada 2", arq.name)

    def test_movimento_so_na_primeira_e_na_final(self):
        c = ler(CRIAR)
        f = secao(c, "## f. Gates", "## g. Auditores")
        self.assertIn("--sem-movimento", f)
        self.assertRegex(f, r"(?s)--sem-movimento.{0,600}rodada final")
        h = secao(c, "## h. Prova", "## Depois da entrega")
        self.assertRegex(h, r"(?is)sem .--sem-movimento.|sem a flag")

    def test_lente_do_heroi_4_chamadas_e_a_construcao_nao_espera(self):
        a = ler(AUD)
        heroi = secao(a, "## Lente curta de gosto no herói", "## Passe de gosto")
        self.assertIn("até 4 chamadas", heroi)
        self.assertIn("não espera", heroi)
        c = ler(CRIAR)
        e = secao(c, "## e.", "## f. Gates")
        self.assertIn("até 4 chamadas", e)
        self.assertIn("não espera", e)

    def test_dobra_de_1440_sai_do_mesmo_comando(self):
        c = ler(CRIAR)
        self.assertIn("dobra-1440x900.png", c)


if __name__ == "__main__":
    unittest.main()
