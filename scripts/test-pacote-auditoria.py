"""pacote-auditoria.py: o auditor recebe a evidência pronta, e o comando diz o que falta.

Cada teste é um jeito real de chamar o auditor com pacote incompleto ou velho (v3.5.4).
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent / "pacote-auditoria.py"
URL = "http://localhost:8765/"


def tocar(caminho, texto="x", t=None):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto if isinstance(texto, bytes) else texto.encode("utf-8"))
    if t:
        os.utime(caminho, (t, t))


def montar_completo(raiz, t=1_000_000):
    tocar(raiz / "dist/index.html", "<html></html>", t)
    tocar(raiz / "evidencias/briefing.md", "briefing", t)
    tocar(raiz / "evidencias/sustentacao.md", "| frase | linha |", t)
    tocar(raiz / "PLANO.md", "plano", t)
    tocar(raiz / "plano-visual.md", "visual", t)
    tocar(raiz / "referencias/sintese.md", "sintese", t)
    tocar(raiz / "referencias/a-dobra.png", b"\x89PNG", t)
    tocar(raiz / "referencias/b-dobra.png", b"\x89PNG", t)
    tocar(raiz / "provas/prova-desktop.png", b"\x89PNG", t + 10)
    tocar(raiz / "provas/prova-mobile.png", b"\x89PNG", t + 10)
    tocar(raiz / "videos/prancha-desktop.png", b"\x89PNG", t + 10)
    tocar(raiz / "videos/prancha-mobile.png", b"\x89PNG", t + 10)


def rodar(raiz, *extra, url=URL):
    args = [sys.executable, str(SCRIPT), "--projeto", str(raiz)]
    if url:
        args += ["--url", url]
    r = subprocess.run(args + list(extra), capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


class Pacote(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.raiz = pathlib.Path(self.t.name)

    def test_pacote_completo_sai_zero_e_grava_manifesto(self):
        montar_completo(self.raiz)
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 0, saida)
        m = json.loads((self.raiz / "auditoria/pacote.json").read_text(encoding="utf-8"))
        self.assertEqual(m["url"], URL)
        self.assertEqual(m["rodada"], 1)
        self.assertTrue(m["completo"])
        self.assertIn("videos/prancha-desktop.png", m["itens"])

    def test_gera_o_briefing_do_auditor_com_os_caminhos_e_o_orcamento(self):
        # A27: o auditor levou 51 min e 113 chamadas porque ninguém lhe deu orçamento nem lhe disse o que NÃO fazer
        montar_completo(self.raiz)
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 0, saida)
        b = (self.raiz / "auditoria/briefing-do-auditor.md").read_text(encoding="utf-8")
        for trecho in ("15 minutos", "30 chamadas", "Proibido recapturar", "6 capturas próprias", "não verificado",
                       "schema", URL, "`provas/prova-desktop.png`", "`videos/prancha-mobile.png`", "--duracao-min", "--chamadas"):
            self.assertIn(trecho, b, trecho)
        self.assertNotIn("RODADA 2", b)
        self.assertIn("briefing-do-auditor.md", saida)

    def test_briefing_da_rodada_2_tem_orcamento_menor_e_e_so_conferencia(self):
        montar_completo(self.raiz)
        tocar(self.raiz / "auditoria/achados-rodada-1.json", "{}", 1_000_100)
        code, saida = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 0, saida)
        b = (self.raiz / "auditoria/briefing-do-auditor.md").read_text(encoding="utf-8")
        self.assertIn("8 minutos", b)
        self.assertIn("15 chamadas", b)
        self.assertIn("RODADA 2", b)
        self.assertIn("Não reabra as 9 lentes", b)

    def test_pacote_incompleto_tambem_grava_o_briefing_mas_nao_manda_chamar(self):
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 1)
        self.assertNotIn("Cole auditoria/briefing", saida)

    def test_sem_prancha_do_video_falha_e_diz_qual(self):
        montar_completo(self.raiz)
        (self.raiz / "videos/prancha-mobile.png").rename(self.raiz / "videos/outro.png")
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 1)
        self.assertIn("FALTA", saida)
        self.assertIn("prancha-mobile.png", saida)

    def test_cada_item_obrigatorio_derruba_o_pacote(self):
        itens = ["dist/index.html", "evidencias/briefing.md", "evidencias/sustentacao.md", "PLANO.md",
                 "referencias/sintese.md", "provas/prova-desktop.png", "provas/prova-mobile.png",
                 "videos/prancha-desktop.png", "referencias/a-dobra.png"]
        for item in itens:
            with self.subTest(item=item):
                with tempfile.TemporaryDirectory() as d:
                    raiz = pathlib.Path(d)
                    montar_completo(raiz)
                    if item == "referencias/a-dobra.png":
                        (raiz / "referencias/b-dobra.png").unlink()
                    (raiz / item).unlink()
                    code, saida = rodar(raiz)
                    self.assertEqual(code, 1, saida)
                    self.assertIn("FALTA", saida)

    def test_sem_url_falha(self):
        montar_completo(self.raiz)
        code, _ = rodar(self.raiz, url=None)
        self.assertNotEqual(code, 0)

    def test_url_que_nao_e_http_falha(self):
        montar_completo(self.raiz)
        code, _ = rodar(self.raiz, url="localhost:8765")
        self.assertEqual(code, 1)

    def test_print_mais_velho_que_a_dist_e_pacote_velho(self):
        montar_completo(self.raiz)
        tocar(self.raiz / "dist/index.html", "<html>novo</html>", 2_000_000)
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 1)
        self.assertIn("VELHO", saida)

    def test_arquivo_vazio_nao_conta(self):
        montar_completo(self.raiz)
        tocar(self.raiz / "videos/prancha-desktop.png", b"", 1_000_010)
        code, saida = rodar(self.raiz)
        self.assertEqual(code, 1)
        self.assertIn("prancha-desktop.png", saida)

    def test_rodada_2_exige_a_lista_de_achados_da_rodada_1(self):
        montar_completo(self.raiz)
        code, saida = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 1)
        self.assertIn("achados-rodada-1", saida)
        tocar(self.raiz / "auditoria/achados-rodada-1.json", "[]", 1_000_020)
        code, saida = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 0, saida)

    def test_clonar_nao_exige_plano_nem_sustentacao_nem_briefing(self):
        montar_completo(self.raiz)
        for f in ("PLANO.md", "evidencias/sustentacao.md", "evidencias/briefing.md", "referencias/sintese.md"):
            (self.raiz / f).unlink()
        code, saida = rodar(self.raiz, "--caminho", "clonar")
        self.assertEqual(code, 0, saida)
        code, _ = rodar(self.raiz)
        self.assertEqual(code, 1)

    def test_nao_olha_dentro_da_dist_nem_de_node_modules(self):
        montar_completo(self.raiz)
        (self.raiz / "provas/prova-mobile.png").unlink()
        tocar(self.raiz / "dist/prova-mobile.png", b"\x89PNG", 1_000_010)
        tocar(self.raiz / "node_modules/x/prova-mobile.png", b"\x89PNG", 1_000_010)
        code, _ = rodar(self.raiz)
        self.assertEqual(code, 1)

    def test_nao_modifica_nada_fora_da_pasta_auditoria(self):
        montar_completo(self.raiz)
        antes = {p: p.stat().st_mtime for p in self.raiz.rglob("*") if p.is_file()}
        rodar(self.raiz)
        depois = {p: p.stat().st_mtime for p in self.raiz.rglob("*") if p.is_file() and "auditoria" not in p.parts}
        for p, t in depois.items():
            self.assertEqual(antes[p], t, p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
