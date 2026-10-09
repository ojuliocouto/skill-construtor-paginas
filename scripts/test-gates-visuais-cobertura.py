"""3.5.7: o antigo test-gates-visuais.cjs (1200 s no macOS do CI) virou três arquivos por família de gate.

Este teste (portátil, sem navegador) garante que NENHUM controle sumiu na divisão: todo controle da lib cai em exatamente uma
família, nenhuma família ficou sem arquivo, os arquivos não repetem prefixo e o total de controles não é menor que os 85 que
existiam antes da divisão.
"""
import pathlib
import re
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
ANTES_DA_DIVISAO = 85
MINIMO_3_5_8 = 101  # 12 controles novos na 3.5.8 (N13 a N17 e N21) e 4 na 3.5.9 (N26): a contagem só sobe


def ler(p):
    return p.read_text(encoding="utf-8")


def controles():
    lib = ler(AQUI / "gates-visuais-lib.cjs")
    corpo = lib[lib.index("const casos = ["):]
    return re.findall(r"^\s+\['([a-z0-9-]+)',", corpo, re.M)


def familias():
    out = {}
    for arq in sorted(AQUI.glob("test-gates-visuais-*.cjs")):
        m = re.search(r"\.iniciar\(\[([^\]]*)\]\)", ler(arq))
        assert m, f"{arq.name} não chama iniciar([...])"
        out[arq.name] = re.findall(r'"([a-z0-9]+)"', m.group(1))
    return out


class Cobertura(unittest.TestCase):
    def test_nenhum_controle_sumiu(self):
        self.assertGreaterEqual(len(controles()), ANTES_DA_DIVISAO, "a lib tem menos controles que antes da divisão")

    def test_a_contagem_da_3_5_8_nao_cai(self):
        self.assertGreaterEqual(len(controles()), MINIMO_3_5_8, "a lib tem menos controles que a 3.5.8")

    def test_todo_controle_cai_em_exatamente_uma_familia(self):
        fam = familias()
        donos = {}
        for arq, prefixos in fam.items():
            for pref in prefixos:
                self.assertNotIn(pref, donos, f"o prefixo {pref} está em {donos.get(pref)} e em {arq}")
                donos[pref] = arq
        sem_dono = sorted({c for c in controles() if c.split("-")[0] not in donos and not c.startswith("dash-")})
        self.assertEqual(sem_dono, [], "controle sem família: nenhum arquivo o roda")
        contados = sum(1 for c in controles() if c.split("-")[0] in donos)
        self.assertEqual(contados, len(controles()), "soma das famílias difere do total de controles")

    def test_tres_arquivos_e_o_antigo_nao_existe_mais(self):
        self.assertEqual(sorted(familias()), ["test-gates-visuais-composicao.cjs", "test-gates-visuais-movimento.cjs", "test-gates-visuais-responsivo.cjs"])
        self.assertFalse((AQUI / "test-gates-visuais.cjs").exists())

    def test_rodar_testes_conhece_os_tres_como_de_navegador(self):
        rodar = ler(AQUI / "rodar-testes.mjs")
        for nome in familias():
            self.assertIn(f"'{nome}'", rodar, f"{nome} falta na tabela de testes que precisam de navegador")
        self.assertNotIn("'test-gates-visuais.cjs'", rodar)


if __name__ == "__main__":
    unittest.main(verbosity=2)
