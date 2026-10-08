"""Biblioteca de formatos de seção (etapa PLANO, 03/10/2026).

Cada formato do cardápio tem um arquivo curto (quando usar, estrutura, armadilha) e um HTML
mínimo de exemplo que passa no próprio gate de tells da skill: o cardápio não pode ensinar o
kicker e o 01/02/03 que os gates reprovam depois.
"""
import pathlib
import re
import subprocess
import sys
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SECOES = RAIZ / "references" / "secoes"
OBJETIVOS = ("Primeira dobra", "Dor", "Mecanismo ou diferencial", "Prova", "Oferta", "Como funciona",
             "FAQ", "Fecho")


def formatos():
    return sorted(p for p in SECOES.glob("*.md") if p.name != "README.md")


class Biblioteca(unittest.TestCase):
    def test_existe_e_tem_formatos(self):
        self.assertTrue((SECOES / "README.md").exists())
        self.assertGreaterEqual(len(formatos()), 12)

    def test_cada_formato_tem_as_tres_partes_e_o_html(self):
        for p in formatos():
            t = p.read_text(encoding="utf-8")
            for parte in ("Quando usar", "Estrutura", "Armadilha"):
                self.assertIn(f"## {parte}", t, f"{p.name} sem {parte}")
            self.assertLessEqual(len(t.splitlines()), 40, f"{p.name} longo demais")
            self.assertTrue(p.with_suffix(".html").exists(), f"{p.name} sem HTML de exemplo")

    def test_cardapio_cobre_cada_objetivo_com_2_ou_3_formatos(self):
        r = (SECOES / "README.md").read_text(encoding="utf-8")
        nomes = {p.stem for p in formatos()}
        for obj in OBJETIVOS:
            m = re.search(rf"(?ms)^### {re.escape(obj)}\n(.*?)(?=^### |\Z)", r)
            self.assertIsNotNone(m, f"cardápio sem {obj}")
            citados = set(re.findall(r"`([a-z0-9-]+)`", m.group(1))) & nomes
            self.assertTrue(2 <= len(citados) <= 3, f"{obj}: {sorted(citados)}")
        for n in nomes:
            self.assertIn(f"`{n}`", r, f"formato {n} fora do cardápio")

    def test_cada_formato_no_cardapio_tem_quando_usar(self):
        r = (SECOES / "README.md").read_text(encoding="utf-8")
        for n in {p.stem for p in formatos()}:
            linhas = [l for l in r.splitlines() if f"`{n}`" in l]
            self.assertTrue(any(re.search(r":\s*\S.{10,}", l.split(f"`{n}`", 1)[1]) for l in linhas), n)

    def test_html_de_exemplo_sem_tells(self):
        for h in sorted(SECOES.glob("*.html")):
            r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "gate-sem-kicker.py"), str(h)],
                               capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(r.returncode, 0, f"{h.name}: {r.stdout}")

    def test_html_em_portugues_sem_travessao_sem_cdn_tailwind(self):
        for h in sorted(SECOES.glob("*.html")):
            t = h.read_text(encoding="utf-8")
            self.assertIn('lang="pt-BR"', t, h.name)
            self.assertNotRegex(t, "[—–]", h.name)
            self.assertNotIn("cdn.tailwindcss.com", t, h.name)
            self.assertNotRegex(t, r">\s*0[1-9]\s*<", h.name)

    def test_md_sem_travessao(self):
        for p in SECOES.glob("*.md"):
            self.assertNotRegex(p.read_text(encoding="utf-8"), "[—–]", p.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
