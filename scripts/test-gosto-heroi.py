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
        self.assertIn("Orçamento: 5 minutos e até 4 chamadas", b)   # 3.7.0: 4 chamadas (a 3.6.2 gastou 6 e 6,4 min)
        self.assertIn(str((self.tmp / "fora" / "prancha.jpg").resolve()), b)
        self.assertIn("advogados criminalistas", b)
        self.assertIn("bonito, só correto ou genérico", b)
        self.assertIn("não manda reconstruir a página", b)
        esquema = b[b.index("{\"gosto\""):b.index("}", b.index("{\"gosto\"")) + 1]
        self.assertEqual(sorted(json.loads(esquema)), sorted(["gosto", "tells", "eixos_abaixo", "gente_no_topo", "mesma_pasta", "uma_mudanca", "depende_do_cliente", "duracao_min", "chamadas"]))
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

    # --- 3.6.1, corte 1: a lente roda UMA rodada, com teto de 5 minutos escrito no prompt do auditor -----------------------
    # Medido no teste de aluno da 3.6.0 (Studio Equilíbrio): duas rodadas de 9,3 e 7,9 min contra o orçamento de 5, as duas
    # com "generico" pelo mesmo motivo (foto de banco, que só a cliente resolve).

    def test_briefing_escreve_o_teto_de_5_minutos_e_a_rodada_unica(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi)
        self.assertEqual(r.returncode, 0, r.stderr)
        b = (self.tmp / "auditoria" / "gosto-heroi" / "briefing.md").read_text(encoding="utf-8")
        self.assertIn("TETO DE 5 MINUTOS", b)
        self.assertIn("ÚNICA rodada", b)
        self.assertIn("No minuto 4", b)
        self.assertNotIn("rodar esta lente uma vez mais", b)
        self.assertIn("depende_do_cliente", b)

    # --- 3.7.0, item 3: a lente cabe no teto (no teste de aluno da 3.6.2: 6,4 min e 6 chamadas contra 5 min) e a construção não espera
    def test_teto_de_4_chamadas_com_o_roteiro_e_a_construcao_nao_espera(self):
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi)
        self.assertEqual(r.returncode, 0, r.stderr)
        b = (self.tmp / "auditoria" / "gosto-heroi" / "briefing.md").read_text(encoding="utf-8")
        self.assertIn("até 4 chamadas", b)
        self.assertIn("1 chamada para a prancha", b)
        self.assertNotIn("antes de\nconstruir as outras seções", b)
        self.assertIn("a construção das outras seções NÃO espera", b)
        self.assertIn("até 4 chamadas", r.stdout)
        self.assertIn("não espere", r.stdout)

    def resultado(self, **campos):
        base = {"gosto": "generico", "tells": ["V15: marca pequena"], "eixos_abaixo": ["imagem"], "gente_no_topo": True,
                "mesma_pasta": False, "uma_mudanca": "Trocar o enquadramento do herói.", "depende_do_cliente": [],
                "duracao_min": 4.5, "chamadas": 5}
        base.update(campos)
        pasta = self.tmp / "auditoria" / "gosto-heroi"
        pasta.mkdir(parents=True, exist_ok=True)
        (pasta / "resultado.json").write_text(json.dumps(base, ensure_ascii=False), encoding="utf-8")
        return pasta / "resultado.json"

    def test_segunda_rodada_depois_do_resultado_e_recusada(self):
        self.assertEqual(rodar("--projeto", self.tmp, "--heroi", self.heroi).returncode, 0)
        self.resultado()
        r = rodar("--projeto", self.tmp, "--heroi", self.heroi)
        self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
        self.assertIn("1 rodada só", r.stderr)
        self.assertIn("não roda de novo", r.stderr)

    def test_remontar_antes_do_resultado_e_a_mesma_rodada(self):
        # o auditor caiu sem devolver o JSON: montar de novo não gasta uma segunda rodada
        self.assertEqual(rodar("--projeto", self.tmp, "--heroi", self.heroi).returncode, 0)
        self.assertEqual(rodar("--projeto", self.tmp, "--heroi", self.heroi).returncode, 0)

    def test_registrar_generico_que_depende_da_cliente_vira_pendencia_e_nao_manda_rodar_de_novo(self):
        self.resultado(depende_do_cliente=["foto real da Carla Mendes com a aluna"])
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PENDÊNCIA DA CLIENTE", r.stdout)
        self.assertIn("não rode a lente de novo", r.stdout)
        pend = (self.tmp / "evidencias" / "pendencias-do-heroi.md").read_text(encoding="utf-8")
        self.assertIn("foto real da Carla Mendes com a aluna", pend)

    def test_registrar_reconhece_o_motivo_de_cliente_mesmo_sem_o_campo(self):
        # o auditor esqueceu o campo, mas a mudança pedida é uma foto real que só a cliente tem
        self.resultado(uma_mudanca="Entra uma foto real da Carla guiando uma aluna. Outra imagem ilustrativa não resolve.")
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PENDÊNCIA DA CLIENTE", r.stdout)
        self.assertTrue((self.tmp / "evidencias" / "pendencias-do-heroi.md").is_file())

    def test_registrar_generico_que_o_construtor_resolve_aplica_no_heroi_sem_segunda_rodada(self):
        self.resultado()
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Trocar o enquadramento do herói.", r.stdout)
        self.assertIn("sem segunda rodada", r.stdout)
        self.assertFalse((self.tmp / "evidencias" / "pendencias-do-heroi.md").exists())

    def test_registrar_bonito_nao_pede_nada(self):
        self.resultado(gosto="bonito")
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("bonito", r.stdout)
        self.assertFalse((self.tmp / "evidencias" / "pendencias-do-heroi.md").exists())

    def test_registrar_avisa_quando_o_auditor_passou_do_teto(self):
        self.resultado(duracao_min=9.3)
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("passou do teto de 5 min", r.stdout)

    def test_registrar_sem_resultado_sai_2(self):
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("resultado.json", r.stderr)

    def test_registrar_resultado_sem_gosto_valido_sai_2(self):
        self.resultado(gosto="otimo")
        r = rodar("--projeto", self.tmp, "--registrar")
        self.assertEqual(r.returncode, 2)
        self.assertIn("gosto", r.stderr)

    def test_registrar_duas_vezes_nao_duplica_a_pendencia(self):
        self.resultado(depende_do_cliente=["logo da clínica"])
        rodar("--projeto", self.tmp, "--registrar")
        rodar("--projeto", self.tmp, "--registrar")
        pend = (self.tmp / "evidencias" / "pendencias-do-heroi.md").read_text(encoding="utf-8")
        self.assertEqual(pend.count("logo da clínica"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
