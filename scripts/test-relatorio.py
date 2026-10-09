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
        (self.raiz / "gates" / "simetria.txt").write_text("títulos com 147 px de diferença\nespaço fixo de 152px (18.0% da tela)\n", encoding="utf-8")
        (self.raiz / "dist").mkdir()
        (self.raiz / "dist" / "index.html").write_text("<html></html>", encoding="utf-8")

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
        lh.write_text('{"performance": 100}', encoding="utf-8")
        antigo = time.time() - 3600
        os.utime(lh, (antigo, antigo))
        p = self.checar("- Lighthouse 100 em desempenho (`gates/lighthouse.json`)\n")
        self.assertTrue(any("anterior" in x for x in p), p)

    def test_medida_de_outra_versao_fora_do_projeto_nao_e_comparada_com_a_dist(self):
        # v5: o relatório cita a medida da v4 (outra pasta) para provar o defeito; ela é mais
        # antiga que a dist/ da v5 por definição e não é medida da versão entregue.
        outra = pathlib.Path(tempfile.mkdtemp()) / "v4-simetria.txt"
        self.addCleanup(lambda: outra.unlink(missing_ok=True))
        outra.write_text("títulos com 147 px de diferença", encoding="utf-8")
        antigo = time.time() - 3600
        os.utime(outra, (antigo, antigo))
        self.assertEqual(self.checar(f"- Na v4, títulos a 147 px (`{outra}`)\n"), [])


    # 3.5.10 (achado P21 da página Torra Clara): a medida da rodada 1 é história, não o estado entregue.
    # Marcador explícito no começo da linha (ou da célula) isenta só da regra "anterior à dist/"; o número
    # continua precisando estar no arquivo citado, e quem afirma o estado atual continua cobrado.
    def velho(self, nome="rodada1-simetria.txt", conteudo="títulos com 147 px de diferença\n"):
        arq = self.raiz / "gates" / nome
        arq.write_text(conteudo, encoding="utf-8")
        antigo = time.time() - 3600
        os.utime(arq, (antigo, antigo))
        return f"gates/{nome}"

    def test_medida_historica_com_marcador_de_rodada_passa(self):
        arq = self.velho()
        self.assertEqual(self.checar(f"- rodada 1: títulos a 147 px de diferença (`{arq}`)\n"), [])

    def test_marcadores_antes_e_historico_e_negrito_e_tabela_passam(self):
        arq = self.velho()
        for linha in (f"- Antes: títulos a 147 px (`{arq}`)",
                      f"- **Rodada 1:** títulos a 147 px (`{arq}`)",
                      f"- histórico: títulos a 147 px (`{arq}`)",
                      f"| rodada anterior: títulos a 147 px | `{arq}` |",
                      f"| Duas formas | rodada 1: 147 px | `{arq}` |"):
            self.assertEqual(self.checar(linha + "\n"), [], linha)

    def test_o_mesmo_arquivo_velho_sem_marcador_continua_reprovando(self):
        arq = self.velho()
        p = self.checar(f"- Títulos a 147 px de diferença (`{arq}`)\n")
        self.assertTrue(any("anterior à dist" in x for x in p), p)

    def test_marcador_no_meio_da_frase_nao_isenta(self):
        arq = self.velho()
        p = self.checar(f"- Títulos a 147 px de diferença (rodada 1: `{arq}`)\n")
        self.assertTrue(any("anterior à dist" in x for x in p), p)

    def test_marcador_com_afirmacao_do_estado_atual_na_mesma_linha_nao_isenta(self):
        arq = self.velho(conteudo="títulos com 147 px de diferença\ne 0 px depois\n")
        for linha in (f"- rodada 1: 147 px; agora 0 px (`{arq}`)",
                      f"- antes: 147 px, na versão atual 0 px (`{arq}`)",
                      f"- rodada 1: 147 px, final 0 px (`{arq}`)"):
            p = self.checar(linha + "\n")
            self.assertTrue(any("anterior à dist" in x for x in p), linha + " " + str(p))

    def test_historico_continua_exigindo_o_arquivo_e_o_numero(self):
        arq = self.velho()
        sem_arquivo = self.checar("- rodada 1: títulos a 147 px de diferença\n")
        self.assertTrue(sem_arquivo and "sem citar" in sem_arquivo[0], sem_arquivo)
        numero_errado = self.checar(f"- rodada 1: títulos a 12 px de diferença (`{arq}`)\n")
        self.assertTrue(numero_errado and "não aparece" in numero_errado[0], numero_errado)

    def test_marcador_numa_linha_nao_isenta_a_linha_vizinha(self):
        arq = self.velho()
        p = self.checar(f"- rodada 1: títulos a 147 px (`{arq}`)\n- Títulos a 147 px (`{arq}`)\n")
        self.assertEqual(len(p), 1, p)
        self.assertIn("linha 2", p[0])

    def test_o_relatorio_lista_as_linhas_tratadas_como_historico(self):
        arq = self.velho()
        rel = self.raiz / "relatorio.md"
        rel.write_text(f"- rodada 1: títulos a 147 px (`{arq}`)\n", encoding="utf-8")
        historicas = []
        gate.checar(rel, base=self.raiz, dist=self.raiz / "dist", historicas=historicas)
        self.assertEqual(len(historicas), 1)
        self.assertIn("rodada 1", historicas[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
