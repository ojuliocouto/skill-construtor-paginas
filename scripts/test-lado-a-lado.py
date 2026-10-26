"""3.7.0 (teste de aluno do CLONAR na 3.6.3): o lado-a-lado do clone fiel fazia a pergunta dos EIXOS de elevação (que é do
CLONAR + ELEVAR) e reduzia a imagem para 760 px por coluna. Com `--modo fiel` ele sai em tamanho real e pergunta pela fidelidade."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("PULADO: precisa do Pillow")
    sys.exit(0)

SCRIPT = pathlib.Path(__file__).with_name("lado-a-lado.py")


class LadoALado(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.d = pathlib.Path(self.t.name)
        Image.new("RGB", (1440, 900), (200, 220, 230)).save(self.d / "o.png")
        Image.new("RGB", (1440, 900), (200, 220, 231)).save(self.d / "c.png")

    def rodar(self, *extra):
        r = subprocess.run([sys.executable, str(SCRIPT), str(self.d / "o.png"), str(self.d / "c.png"), str(self.d / "s.png"), *extra],
                           capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def test_modo_fiel_sai_em_tamanho_real_e_pergunta_pela_fidelidade(self):
        code, out = self.rodar("--modo", "fiel", "--rotulos", "Original,Clone")
        self.assertEqual(code, 0, out)
        self.assertEqual(Image.open(self.d / "s.png").width, 1440 * 2 + 24)
        self.assertNotIn("EIXOS", out)
        self.assertIn("delta declarado", out)
        self.assertIn("gate-fidelidade", out)

    def test_padrao_continua_o_de_elevacao(self):
        code, out = self.rodar()
        self.assertEqual(code, 0, out)
        self.assertEqual(Image.open(self.d / "s.png").width, 760 * 2 + 24)
        self.assertIn("EIXOS", out)


if __name__ == "__main__":
    unittest.main()
