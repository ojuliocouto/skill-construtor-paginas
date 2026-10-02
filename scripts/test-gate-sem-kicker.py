"""Gate de tells (sem kicker, sem numeração decorativa): mutantes têm que reprovar.

O mutante Tailwind do relatório do aluno (02/10/2026) passou com "ok" na versão antiga:
o gate só lia regra CSS dentro do HTML e classe com nome label/kicker/eyebrow. Este teste
garante que o caso mais comum (Tailwind) e o número gigante em card reprovam.
"""
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name('gate-sem-kicker.py')

LIMPA = """<!doctype html><html><body>
<section><h2 class="text-3xl font-bold">Duas formas de praticar</h2>
<article class="rounded-2xl p-6"><h3>Em grupo</h3><p>Até 4 pessoas por turma.</p></article>
<article class="rounded-2xl p-6"><h3>Encontro 01</h3><p class="uppercase">PIX</p></article>
</section></body></html>"""


class GateTells(unittest.TestCase):
    def rodar(self, html, css=None, nome='index.html'):
        with tempfile.TemporaryDirectory() as pasta:
            raiz = pathlib.Path(pasta)
            (raiz / nome).write_text(html, encoding='utf-8')
            if css is not None:
                (raiz / 'estilo.css').write_text(css, encoding='utf-8')
            r = subprocess.run([sys.executable, str(SCRIPT), str(raiz / nome)], capture_output=True, text=True)
            return r.returncode, r.stdout

    def test_pagina_limpa_passa(self):
        code, out = self.rodar(LIMPA)
        self.assertEqual(code, 0, out)

    def test_mutante_tailwind_do_relatorio_reprova(self):
        code, out = self.rodar('<section><p class="text-[12px] uppercase tracking-[0.2em]">Para você</p><h2>Título</h2></section>')
        self.assertEqual(code, 1, out)

    def test_tracking_widest_reprova(self):
        code, out = self.rodar('<div><span class="uppercase tracking-widest text-xs">Método</span>\n  <h1>Título</h1></div>')
        self.assertEqual(code, 1, out)

    def test_jsx_classname_reprova(self):
        code, out = self.rodar('<p className="tracking-wider uppercase">Para quem é</p><h3>Título</h3>', nome='Hero.html')
        self.assertEqual(code, 1, out)

    def test_css_externo_do_projeto_reprova(self):
        html = '<p class="sobre">Para você</p><h2>Título</h2>'
        css = '.sobre{text-transform:uppercase;letter-spacing:.2em;font-size:12px}'
        code, out = self.rodar(html, css)
        self.assertEqual(code, 1, out)

    def test_tracking_tight_nao_e_kicker(self):
        code, out = self.rodar('<p class="uppercase tracking-tight">Ok</p><h2>Título</h2>')
        self.assertEqual(code, 0, out)


if __name__ == '__main__':
    unittest.main(verbosity=2)
