"""Controles do gate do relatório: número de medida só com o arquivo que o gravou.

Auditoria da v4 (02/10/2026): o relatório do construtor tinha 10 afirmações que o auditor
refutou, entre elas "fatos alinhados à base da foto" (eram 53 px abaixo), "no máximo 2 linhas
em 768" (os h3 quebravam), "3 links wa.me" (eram 2) e "Lighthouse 100" com um JSON anterior à
dist/ final.
"""
import importlib.util
import os
import pathlib
import tempfile
import time
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate_relatorio", AQUI / "gate-relatorio.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateRelatorio(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.raiz = pathlib.Path(t.name)
        (self.raiz / "gates").mkdir()
        (self.raiz / "gates" / "simetria.txt").write_text("títulos com 147 px de diferença\nespaço fixo de 152px (18.0% da tela)\n")
        (self.raiz / "dist").mkdir()
        (self.raiz / "dist" / "index.html").write_text("<html></html>")

    def checar(self, texto, dist=True):
        rel = self.raiz / "relatorio.md"
        rel.write_text(texto, encoding="utf-8")
        return gate.checar(rel, base=self.raiz, dist=self.raiz / "dist" if dist else None)

    def test_medida_citada_e_presente_no_arquivo(self):
        self.assertEqual(self.checar("| Duas formas | títulos a 147 px | `gates/simetria.txt` |\n", dist=False), [])

    def test_virgula_decimal_casa_com_ponto(self):
        self.assertEqual(self.checar("- Fixo somava 18,0% da tela (`gates/simetria.txt`)\n", dist=False), [])

    def test_medida_sem_arquivo_reprova(self):
        p = self.checar("- Hero com os fatos alinhados, 0 px de diferença.\n", dist=False)
        self.assertTrue(p and "sem citar" in p[0], p)

    def test_numero_que_nao_esta_no_arquivo_reprova(self):
        p = self.checar("- Títulos a 12 px (`gates/simetria.txt`)\n", dist=False)
        self.assertTrue(p and "12 px" in p[0] and "não aparece" in p[0], p)

    def test_limite_de_regra_nao_e_medida(self):
        self.assertEqual(self.checar("- Regra nova: fixo somado até 15% da tela e foto com pelo menos 35% da altura.\n", dist=False), [])

    def test_lighthouse_anterior_a_dist_reprova(self):
        lh = self.raiz / "gates" / "lighthouse.json"
        lh.write_text('{"performance": 100}')
        antigo = time.time() - 3600
        os.utime(lh, (antigo, antigo))
        p = self.checar("- Lighthouse 100 em desempenho (`gates/lighthouse.json`)\n")
        self.assertTrue(any("anterior" in x for x in p), p)

    def test_medida_de_outra_versao_fora_do_projeto_nao_e_comparada_com_a_dist(self):
        # v5: o relatório cita a medida da v4 (outra pasta) para provar o defeito; ela é mais
        # antiga que a dist/ da v5 por definição e não é medida da versão entregue.
        outra = pathlib.Path(tempfile.mkdtemp()) / "v4-simetria.txt"
        self.addCleanup(lambda: outra.unlink(missing_ok=True))
        outra.write_text("títulos com 147 px de diferença")
        antigo = time.time() - 3600
        os.utime(outra, (antigo, antigo))
        self.assertEqual(self.checar(f"- Na v4, títulos a 147 px (`{outra}`)\n"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
