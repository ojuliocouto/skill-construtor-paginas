"""Prova de animação (padrão da v7, 04/10/2026): a prancha mede quantos pixels mudam entre o início e
o fim de cada seção, e o gate reprova seção parada (menos de 2%) e mais de 2 seções com o mesmo tipo
de animação. Na v6 tudo entrava com o mesmo fade; na v7 cada seção anima o próprio conteúdo.
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

import numpy as np
from PIL import Image

AQUI = pathlib.Path(__file__).resolve().parent
PRANCHA = AQUI / "prancha.py"
GATE = AQUI / "gate-animacao.py"


def quadro(caminho, preenchido, tamanho=(400, 300)):
    """Quadro branco com `preenchido` (fração de 0 a 1) das linhas em preto, de cima para baixo."""
    w, h = tamanho
    a = np.full((h, w, 3), 255, dtype=np.uint8)
    a[: int(h * preenchido), :, :] = 0
    caminho.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(a).save(caminho)


def quadros_da_secao(pasta, nome, fracoes_desk, fracoes_mob):
    q = pasta / "quadros"
    for i, f in enumerate(fracoes_desk, 1):
        quadro(q / f"{nome}-desk-{i}.png", f, (400, 300))
    for i, f in enumerate(fracoes_mob, 1):
        quadro(q / f"{nome}-mob-{i}.png", f, (200, 400))


class Prancha(unittest.TestCase):
    def rodar(self, pasta, secoes):
        (pasta / "secoes.json").write_text(json.dumps(secoes), encoding="utf-8")
        return subprocess.run([sys.executable, str(PRANCHA), "--pasta", str(pasta), "--secoes", str(pasta / "secoes.json")],
                              capture_output=True, text=True)

    def test_mede_o_percentual_de_pixels_que_mudaram(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = pathlib.Path(t)
            quadros_da_secao(pasta, "01-anima", (0, 0.5, 1), (0, 0.25, 0.5))
            quadros_da_secao(pasta, "02-parada", (0.3, 0.3, 0.3), (0.3, 0.3, 0.3))
            r = self.rodar(pasta, [{"nome": "01-anima", "titulo": "Anima", "tipo": "abertura da foto"},
                                   {"nome": "02-parada", "titulo": "Parada", "tipo": "revelação por linha"}])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            m = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
            s1, s2 = m["secoes"]
            self.assertAlmostEqual(s1["desk"]["ini_fim"], 100.0, places=1)
            self.assertAlmostEqual(s1["desk"]["ini_meio"], 50.0, places=1)
            self.assertAlmostEqual(s1["mob"]["ini_fim"], 50.0, places=1)
            self.assertEqual(s2["desk"]["ini_fim"], 0.0)
            self.assertEqual(s1["tipo"], "abertura da foto")
            self.assertTrue((pasta / "01-anima.png").is_file() and (pasta / "02-parada.png").is_file())

    def test_variacao_abaixo_de_12_niveis_nao_conta(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = pathlib.Path(t)
            q = pasta / "quadros"
            q.mkdir()
            base = np.full((300, 400, 3), 200, dtype=np.uint8)
            for tela, tam in (("desk", (400, 300)), ("mob", (200, 400))):
                for i, delta in enumerate((0, 6, 11), 1):
                    Image.fromarray(np.full((tam[1], tam[0], 3), 200 + delta, dtype=np.uint8)).save(q / f"x-{tela}-{i}.png")
            r = self.rodar(pasta, [{"nome": "x", "titulo": "X", "tipo": "t"}])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            m = json.loads((pasta / "medidas.json").read_text(encoding="utf-8"))
            self.assertEqual(m["secoes"][0]["desk"]["ini_fim"], 0.0)

    def test_quadro_faltando_reprova_com_o_nome(self):
        with tempfile.TemporaryDirectory() as t:
            pasta = pathlib.Path(t)
            quadros_da_secao(pasta, "a", (0, 0.5, 1), (0, 0.5, 1))
            (pasta / "quadros" / "a-mob-3.png").unlink()
            r = self.rodar(pasta, [{"nome": "a", "titulo": "A", "tipo": "t"}])
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("a-mob-3.png", r.stdout + r.stderr)


def medidas(pasta, secoes):
    """secoes: lista de (nome, tipo, ini_fim_desk, ini_fim_mob)."""
    corpo = {"limiar_nivel": 12, "secoes": []}
    for nome, tipo, d, m in secoes:
        corpo["secoes"].append({"nome": nome, "titulo": nome, "tipo": tipo,
                                "desk": {"ini_meio": d / 2, "meio_fim": d / 2, "ini_fim": d},
                                "mob": {"ini_meio": m / 2, "meio_fim": m / 2, "ini_fim": m}})
    (pasta / "medidas.json").write_text(json.dumps(corpo), encoding="utf-8")


class GateAnimacao(unittest.TestCase):
    def rodar(self, secoes, extra=(), plano=None):
        with tempfile.TemporaryDirectory() as t:
            pasta = pathlib.Path(t)
            medidas(pasta, secoes)
            args = [sys.executable, str(GATE), "--pasta", str(pasta), *extra]
            if plano is not None:
                (pasta / "PLANO.md").write_text(plano, encoding="utf-8")
                args += ["--plano", str(pasta / "PLANO.md")]
            r = subprocess.run(args, capture_output=True, text=True)
            return r.returncode, r.stdout + r.stderr

    def test_todas_animam_e_tipos_variados_passa(self):
        code, out = self.rodar([("topo", "abertura da foto", 30, 22), ("dor", "frases em sequência", 8, 6),
                                ("turma", "vagas que se preenchem", 12, 9)])
        self.assertEqual(code, 0, out)
        self.assertIn("PASSA", out)

    def test_secao_parada_no_desktop_reprova(self):
        code, out = self.rodar([("topo", "abertura da foto", 30, 22), ("dor", "frases em sequência", 1.4, 6)])
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"dor.*desktop 1440.*1[.,]4%")

    def test_secao_parada_no_celular_reprova(self):
        code, out = self.rodar([("topo", "abertura da foto", 30, 22), ("dor", "frases em sequência", 8, 0.0)])
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"dor.*celular 390")

    def test_exatamente_2_por_cento_passa(self):
        code, out = self.rodar([("topo", "abertura da foto", 2.0, 2.0)])
        self.assertEqual(code, 0, out)

    def test_tres_secoes_com_o_mesmo_tipo_reprova(self):
        code, out = self.rodar([("a", "fade", 20, 20), ("b", "fade", 20, 20), ("c", "fade", 20, 20), ("d", "barras", 20, 20)])
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"3 seções.*fade")

    def test_duas_secoes_com_o_mesmo_tipo_passa(self):
        code, out = self.rodar([("a", "fade", 20, 20), ("b", "fade", 20, 20), ("c", "barras", 20, 20)])
        self.assertEqual(code, 0, out)

    def test_tipo_assinatura_fica_fora_da_contagem(self):
        # o momento assinatura aparece em 3 seções por regra do plano
        code, out = self.rodar([("topo", "assinatura", 20, 20), ("avaliacao", "assinatura", 20, 20), ("fecho", "assinatura", 20, 20), ("dor", "linhas", 20, 20)])
        self.assertEqual(code, 0, out)

    def test_tipo_nao_declarado_reprova(self):
        code, out = self.rodar([("a", "", 20, 20)])
        self.assertEqual(code, 1, out)
        self.assertIn("tipo", out)

    def test_minimo_configuravel(self):
        code, out = self.rodar([("a", "t", 3, 3)], extra=("--minimo", "5"))
        self.assertEqual(code, 1, out)

    def test_plano_com_mais_secoes_que_pranchas_reprova(self):
        plano = ("| Seção | Desktop | Celular | Animação |\n|---|---|---|---|\n"
                 "| Topo | x | y | abertura da foto: z |\n| Dor | x | y | linhas: z |\n| Fecho | x | y | barras: z |\n")
        code, out = self.rodar([("topo", "abertura da foto", 20, 20), ("dor", "linhas", 20, 20)], plano=plano)
        self.assertEqual(code, 1, out)
        self.assertRegex(out, r"3 seções.*2 pranchas|2 pranchas.*3 seções")

    def test_plano_com_o_mesmo_numero_de_secoes_passa(self):
        plano = ("| Seção | Desktop | Celular | Animação |\n|---|---|---|---|\n"
                 "| Topo | x | y | abertura da foto: z |\n| Dor | x | y | linhas: z |\n")
        code, out = self.rodar([("topo", "abertura da foto", 20, 20), ("dor", "linhas", 20, 20)], plano=plano)
        self.assertEqual(code, 0, out)

    def test_sem_medidas_reprova(self):
        with tempfile.TemporaryDirectory() as t:
            r = subprocess.run([sys.executable, str(GATE), "--pasta", t], capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout)
            self.assertIn("prancha.py", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
