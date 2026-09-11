"""O CSS gerado decide o resultado, inclusive quando o build não existe."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

class Classes(unittest.TestCase):
    def test_css_presente_ausente_e_classe_morta(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = pathlib.Path(pasta)
            (raiz / 'dist').mkdir()
            (raiz / 'index.html').write_text('<p class="bg-marca/97">Controle</p>')
            script = pathlib.Path(__file__).with_name('gate-classes-mortas.py')
            for css, esperado in [(None, 1), ('.outra{color:red}', 1), ('.bg-marca\\/97{background:red}', 0)]:
                if css is not None:
                    (raiz / 'dist/app.css').write_text(css)
                r = subprocess.run([sys.executable, str(script), '--projeto', pasta], capture_output=True, text=True)
                self.assertEqual(r.returncode, esperado, r.stdout)

if __name__ == '__main__':
    unittest.main(verbosity=2)
