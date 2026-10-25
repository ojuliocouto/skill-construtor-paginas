"""Lente curta de gosto no herói (auditoria de 25/10/2026): o script monta a prancha e o briefing.

Precisa de Pillow. O julgamento é de um subagente; aqui se prova a prancha (2 referências e o herói na
mesma escala), o briefing (orçamento, perguntas, schema, caminho da prancha) e os erros claros.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
SCRIPT = AQUI / "gosto-heroi.py"


def png(caminho, w, h, cor):
    Image.new("RGB", (w, h), cor).save(caminho)
    return caminho


def rodar(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, encoding="utf-8")


class GostoHeroi(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix="gosto-heroi-"))
        (self.tmp / "referencias").mkdir()
        (self.tmp / "evidencias").mkdir()
        (self.tmp / "evidencias" / "briefing.md").write_text("3. **Para quem:** advogados criminalistas.\n", encoding="utf-8")
        png(self.tmp / "referencias" / "01-a-dobra.png", 1440, 900, (200, 0, 0))
        png(self.tmp / "referencias" / "01-a-meio.png", 1440, 900, (0, 0, 0))
        png(self.tmp / "referencias" / "02-b-dobra.png", 1440, 900, (0, 200, 0))
        png(self.tmp / "referencias" / "03-c-dobra.png", 1440, 900, (0, 0, 200))
        self.heroi = png(self.tmp / "heroi-1440.png", 1440, 900, (10, 20, 30))
        self.cel = png(self.tmp / "heroi-390.png", 390, 844, (30, 20, 10))

    def test_prancha_com_as_duas_primeiras_dobras_e_o_heroi(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi, "--celular", self.cel)
        self.assertEqual(r.returncode, 0, r.stderr)
        prancha = self.tmp / "auditoria" / "gosto-heroi" / "prancha.jpg"
        img = Image.open(prancha).convert("RGB")
        self.assertEqual(img.size, (1470, 1010))
        # referência 1 (vermelha) em cima à esquerda, referência 2 (verde) em cima à direita: a 3 não entra, nem o "meio"
        self.assertGreater(img.getpixel((360, 245))[0], 150)
        self.assertGreater(img.getpixel((750 + 360, 245))[1], 150)
        # o herói embaixo à esquerda, o celular embaixo à direita
        self.assertLess(sum(img.getpixel((360, 520 + 40 + 200))), 120)
        self.assertGreater(img.getpixel((750 + 50, 520 + 40 + 200))[0], 20)

    def test_briefing_tem_orcamento_perguntas_schema_publico_e_a_prancha(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi, "--saida", self.tmp / "fora")
        self.assertEqual(r.returncode, 0, r.stderr)
        b = (self.tmp / "fora" / "briefing.md").read_text(encoding="utf-8")
        self.assertIn("Orçamento: 5 minutos e até 6", b)
        self.assertIn(str((self.tmp / "fora" / "prancha.jpg").resolve()), b)
        self.assertIn("advogados criminalistas", b)
        self.assertIn("bonito, só correto ou genérico", b)
        self.assertIn("não manda reconstruir a página", b)
        esquema = b[b.index("{\"gosto\""):b.index("}", b.index("{\"gosto\"")) + 1]
        self.assertEqual(sorted(json.loads(esquema)), sorted(["gosto", "tells", "eixos_abaixo", "gente_no_topo", "mesma_pasta", "uma_mudanca", "duracao_min", "chamadas"]))
        self.assertIn("orçamento: 5 min", r.stdout)

    def test_publico_vem_do_etapa_0_antes_do_briefing(self):
        (self.tmp / "evidencias" / "etapa-0.json").write_text(json.dumps({"briefing": {"publico": "Adultos que passam café em casa"}}), encoding="utf-8")
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi)
        self.assertEqual(r.returncode, 0, r.stderr)
        b = (self.tmp / "auditoria" / "gosto-heroi" / "briefing.md").read_text(encoding="utf-8")
        self.assertIn("Público do briefing: Adultos que passam café em casa", b)

    def test_refs_explicitas_valem(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi, "--refs", f"{self.tmp / 'referencias' / '03-c-dobra.png'},{self.tmp / 'referencias' / '02-b-dobra.png'}")
        self.assertEqual(r.returncode, 0, r.stderr)
        img = Image.open(self.tmp / "auditoria" / "gosto-heroi" / "prancha.jpg").convert("RGB")
        self.assertGreater(img.getpixel((360, 245))[2], 150)

    def test_sem_duas_referencias_sai_2_com_mensagem(self):
        for p in (self.tmp / "referencias").glob("0[23]-*"):
            p.unlink()
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi)
        self.assertEqual(r.returncode, 2)
        self.assertIn("faltam referências", r.stderr)

    def test_heroi_inexistente_sai_2(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.tmp / "nao-existe.png")
        self.assertEqual(r.returncode, 2)
        self.assertIn("imagem não encontrada", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
