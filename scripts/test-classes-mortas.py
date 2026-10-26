"""O CSS gerado decide o resultado, inclusive quando o build não existe."""
import pathlib
import subprocess
import sys
import tempfile
import unittest

class ColisaoNoClone(unittest.TestCase):
    """3.7.0 (teste de aluno do CLONAR na 3.6.3): a classe "list-item" da original virou utilitário do Tailwind
    (display:list-item) e pôs bolinhas ao lado dos 5 logos. No clone, a CSS da original vence o utilitário."""

    def montar(self, pasta, entrada):
        raiz = pathlib.Path(pasta)
        (raiz / 'index.html').write_text('<ul class="logos-list"><li class="list-item">Flutter</li></ul>', encoding='utf-8')
        (raiz / '_input.css').write_text(entrada, encoding='utf-8')
        autor = entrada.replace('@tailwind base;', '').replace('@tailwind components;', '').replace('@tailwind utilities;', '')
        gerado = ('.list-item{display:list-item}' if '@tailwind utilities' in entrada else '') + autor
        (raiz / 'tailwind-compiled.css').write_text(gerado, encoding='utf-8')
        return raiz

    def rodar(self, pasta, *extra):
        script = pathlib.Path(__file__).with_name('gate-classes-mortas.py')
        r = subprocess.run([sys.executable, str(script), '--projeto', pasta, *extra], capture_output=True, text=True, encoding='utf-8')
        return r.returncode, r.stdout + r.stderr

    def test_utilitario_do_tailwind_com_classe_da_original_reprova_no_clone(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.montar(pasta, '@tailwind utilities;\n.logos-list .list-item{width:20%;background:url(fonts/x.woff2)}')
            code, out = self.rodar(pasta, '--clone')
            self.assertEqual(code, 1, out)
            self.assertIn('list-item', out)
            self.assertIn('display:list-item', out)
            code, out = self.rodar(pasta)
            self.assertEqual(code, 0, out)   # fora do clone o gate não muda

    def test_sem_tailwind_utilities_passa_no_clone(self):
        with tempfile.TemporaryDirectory() as pasta:
            self.montar(pasta, '.logos-list .list-item{width:20%}')
            code, out = self.rodar(pasta, '--clone')
            self.assertEqual(code, 0, out)


class Classes(unittest.TestCase):
    def test_css_presente_ausente_e_classe_morta(self):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = pathlib.Path(pasta)
            (raiz / 'dist').mkdir()
            (raiz / 'index.html').write_text('<p class="bg-marca/97">Controle</p>', encoding="utf-8")
            script = pathlib.Path(__file__).with_name('gate-classes-mortas.py')
            for css, esperado in [(None, 1), ('.outra{color:red}', 1), ('.bg-marca\\/97{background:red}', 0)]:
                if css is not None:
                    (raiz / 'dist/app.css').write_text(css, encoding="utf-8")
                r = subprocess.run([sys.executable, str(script), '--projeto', pasta], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, esperado, r.stdout)

    def test_pagina_html_sem_dist_le_css_da_raiz(self):
        # Relatorio do aluno: pagina HTML + Tailwind compilado na raiz dava "nenhum .css em dist".
        script = pathlib.Path(__file__).with_name('gate-classes-mortas.py')
        for css, esperado in [(None, 1), ('.outra{color:red}', 1), ('.bg-marca\\/97{background:red}', 0)]:
            with self.subTest(css=css), tempfile.TemporaryDirectory() as pasta:
                raiz = pathlib.Path(pasta)
                (raiz / 'index.html').write_text('<p class="bg-marca/97">Controle</p>', encoding="utf-8")
                if css is not None:
                    (raiz / 'tailwind-compiled.css').write_text(css, encoding="utf-8")
                r = subprocess.run([sys.executable, str(script), '--projeto', pasta], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, esperado, r.stdout)

    def test_dist_com_css_em_linha(self):
        # v3.1 (02/10/2026): montar-dist.py --css-em-linha põe o CSS num <style> do index.html da
        # dist/, e o gate dizia "nenhum .css em dist" para uma página com o CSS presente.
        script = pathlib.Path(__file__).with_name('gate-classes-mortas.py')
        for css, esperado in [('.outra{color:red}', 1), ('.bg-marca\\/97{background:red}', 0)]:
            with self.subTest(css=css), tempfile.TemporaryDirectory() as pasta:
                raiz = pathlib.Path(pasta)
                (raiz / 'dist').mkdir()
                (raiz / 'index.html').write_text('<p class="bg-marca/97">Controle</p>', encoding="utf-8")
                (raiz / 'dist' / 'index.html').write_text(f'<style>{css}</style><p class="bg-marca/97">Controle</p>', encoding="utf-8")
                r = subprocess.run([sys.executable, str(script), '--projeto', pasta], capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(r.returncode, esperado, r.stdout)

    def test_wave_aceita_o_gate(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('wave', pathlib.Path(__file__).with_name('wave.py'))
        wave = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(wave)
        self.assertIn('classes-mortas', wave.GATES)


if __name__ == '__main__':
    unittest.main(verbosity=2)
