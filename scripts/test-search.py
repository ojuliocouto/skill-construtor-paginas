"""Banco de design: busca em português tem que achar resultado.

Relatório do aluno (02/10/2026): "estudio de pilates acolhedor" devolvia 0 resultados,
porque os CSVs são indexados em inglês. O search.py agora traduz os termos comuns.
"""
import importlib.util
import pathlib
import subprocess
import sys
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("core", AQUI / "core.py")
core = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(AQUI))
spec.loader.exec_module(core)


class BuscaPortugues(unittest.TestCase):
    def test_consulta_do_aluno_acha_estilo(self):
        r = core.search("estudio de pilates acolhedor", "style")
        self.assertGreater(r["count"], 0, r)

    def test_termos_de_negocio_local_acham_paleta(self):
        for termo in ("pilates", "estúdio", "clínica", "consultório", "academia", "restaurante", "advocacia"):
            with self.subTest(termo=termo):
                r = core.search(termo, "color")
                self.assertGreater(r["count"], 0, r)

    def test_ingles_continua_igual(self):
        self.assertEqual(core.search("dark premium", "style")["count"],
                         core.search("dark premium", "style")["count"])
        self.assertGreater(core.search("dark premium", "style")["count"], 0)

    def test_cli_mostra_a_traducao(self):
        r = subprocess.run([sys.executable, str(AQUI / "search.py"), "clínica acolhedora", "--domain", "color"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("clinic", r.stdout.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
