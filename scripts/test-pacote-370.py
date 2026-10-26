"""3.7.0: o pacote do auditor para o passo g caber em 12 minutos (teste de aluno da 3.6.2: 35 min, 47% da página).

Rodada 1: 758 s e 21 chamadas. Rodada 2: 662 s e 10 chamadas, só para dizer "corrigido ou não". Aqui se prova:
  1. o briefing da rodada 1 traz o teto novo (8 min, 12 chamadas) e proíbe capturar qualquer coisa nova;
  2. a lente coberta por gate verde recebe o laudo do gate e a ordem de procurar só o que o gate não mede;
  3. a rodada 1 guarda a foto da dist auditada, e a rodada 2 recebe o diff dela;
  4. a rodada 2 é conferência dirigida: só os achados críticos e altos, numerados, com o print novo de cada um; sem nota nova;
  5. sem crítico nem alto na rodada 1 não há rodada 2 de auditor.
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent / "pacote-auditoria.py"
URL = "http://127.0.0.1:5000/"
try:
    import PIL  # noqa: F401
    TEM_PIL = True
except ImportError:
    TEM_PIL = False

def _png_1x1():
    import struct
    import zlib

    def bloco(tipo, dados):
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            + bloco(b"IDAT", zlib.compress(b"\x00\xff\x00\x00")) + bloco(b"IEND", b""))


PNG = _png_1x1()


def tocar(caminho, conteudo="x", t=None):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(conteudo if isinstance(conteudo, bytes) else conteudo.encode("utf-8"))
    if t:
        os.utime(caminho, (t, t))


def montar(raiz, t=1_000_000):
    tocar(raiz / "dist/index.html", "<html><body>\n<h1>Antes</h1>\n<p>texto que fica</p>\n</body></html>", t)
    tocar(raiz / "dist/app.js", "console.log(1)", t)
    tocar(raiz / "evidencias/briefing.md", "briefing", t)
    tocar(raiz / "evidencias/sustentacao.md", "| frase | linha |", t)
    tocar(raiz / "PLANO.md", "plano", t)
    tocar(raiz / "referencias/sintese.md", "sintese", t)
    tocar(raiz / "referencias/a-dobra.png", PNG, t)
    for n in ("provas/prova-desktop.png", "provas/prova-mobile.png", "videos/prancha-desktop.png", "videos/prancha-mobile.png"):
        tocar(raiz / n, PNG, t + 10)


def gates_na_wave(raiz, verdes=("responsivo", "oclusao", "movimento", "imagens", "verdade"), vermelhos=("simetria",)):
    gates = {}
    for g in verdes:
        tocar(raiz / f"gates/{g}-r4.txt", f"PASSA {g}")
        gates[g] = {"exit": 0, "quando": "2026-10-26T01:00:00", "detalhe": f"rodar-gates r4: PASSA em 10 s (gates/{g}-r4.txt)"}
    for g in vermelhos:
        tocar(raiz / f"gates/{g}-r4.txt", f"REPROVA {g}")
        gates[g] = {"exit": 1, "quando": "2026-10-26T01:00:00", "detalhe": f"rodar-gates r4: REPROVA (saída 1) em 10 s (gates/{g}-r4.txt)"}
    (raiz / ".wave-auditoria.json").write_text(json.dumps({"lentes": {}, "gates": gates}), encoding="utf-8")


def rodar(raiz, *extra):
    args = [sys.executable, str(SCRIPT), "--projeto", str(raiz), "--url", URL, "--briefing-reflete-pedido", "sim", *extra]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def achados_rodada_1(raiz, t=1_000_100, com_alto=True):
    blocos = [
        {"lente": "responsive-auditor", "aprovado": False, "score": 7.5, "achados": [
            {"item": "Menu com alvo de toque de 30 px em 768", "severidade": "critico", "evidencia": "nav a 30 px", "fix": "44 px"},
            {"item": "Respiro curto no rodapé", "severidade": "baixo", "evidencia": "12 px", "fix": "24 px"}]},
        {"lente": "content-auditor", "aprovado": False, "score": 7.0, "achados": [
            {"item": "Regra inventada procure o médico", "severidade": "alto" if com_alto else "medio", "evidencia": "linha 210", "fix": "tirar"},
            {"item": "Legenda com 12 px", "severidade": "medio", "evidencia": "legenda", "fix": "14 px"}]},
    ]
    if not com_alto:
        blocos[0]["achados"][0]["severidade"] = "medio"
    tocar(raiz / "auditoria/achados-rodada-1.json", json.dumps(blocos, ensure_ascii=False), t)


class Rodada1(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.raiz = pathlib.Path(self.t.name)
        montar(self.raiz)

    def briefing(self):
        return (self.raiz / "auditoria/briefing-do-auditor.md").read_text(encoding="utf-8")

    def test_teto_de_8_minutos_e_12_chamadas_sem_captura_nova(self):
        code, out = rodar(self.raiz)
        self.assertEqual(code, 0, out)
        b = self.briefing()
        for trecho in ("8 minutos", "12 chamadas", "Não capture nada", "não verificado", "--duracao-min"):
            self.assertIn(trecho, b, trecho)
        self.assertNotIn("6 capturas próprias", b)
        self.assertNotIn("15 minutos", b)

    def test_lente_coberta_por_gate_verde_recebe_o_laudo_e_so_procura_o_que_o_gate_nao_mede(self):
        gates_na_wave(self.raiz)
        code, out = rodar(self.raiz)
        self.assertEqual(code, 0, out)
        b = self.briefing()
        self.assertIn("O que os gates verdes já mediram", b)
        bloco = b.split("O que os gates verdes já mediram")[1].split("\n## ")[0]
        linha_resp = next(l for l in bloco.splitlines() if l.startswith("- `responsive-auditor`"))
        self.assertIn("`gates/responsivo-r4.txt`", linha_resp)
        self.assertIn("`gates/oclusao-r4.txt`", linha_resp)
        self.assertIn("hierarquia, gosto, coerência com o briefing e cara de IA", b)
        # gate vermelho não cobre: a lente que dependia dele é auditada inteira
        linha_vis = next(l for l in bloco.splitlines() if l.startswith("- `visual-auditor`"))
        self.assertIn("simetria", linha_vis)
        self.assertIn("vermelho", linha_vis)
        linha_a11y = next(l for l in bloco.splitlines() if l.startswith("- `a11y-auditor`"))
        self.assertIn("lente inteira", linha_a11y)
        m = json.loads((self.raiz / "auditoria/pacote.json").read_text(encoding="utf-8"))
        self.assertIn("gates/responsivo-r4.txt", m["itens"])

    def test_rodada_1_guarda_a_foto_da_dist_auditada(self):
        code, out = rodar(self.raiz)
        self.assertEqual(code, 0, out)
        self.assertTrue((self.raiz / "auditoria/dist-rodada-1/index.html").is_file())
        self.assertTrue((self.raiz / "auditoria/dist-rodada-1/_hashes.json").is_file())


class Rodada2(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.raiz = pathlib.Path(self.t.name)
        montar(self.raiz)
        code, out = rodar(self.raiz)              # rodada 1: guarda a dist auditada
        self.assertEqual(code, 0, out)
        achados_rodada_1(self.raiz)
        tocar(self.raiz / "dist/index.html", "<html><body>\n<h1>Depois</h1>\n<p>texto que fica</p>\n</body></html>", 1_000_200)

    def correcoes(self, t=1_000_300, sem_print=False):
        itens = [{"n": 1, "print": "" if sem_print else "prints/menu-768.png", "o_que_mudou": "nav a com min-height 44px"},
                 {"n": 2, "print": "prints/regra.png", "o_que_mudou": "bloco removido"}]
        for nome in ("prints/menu-768.png", "prints/regra.png"):
            tocar(self.raiz / nome, PNG, t)
        tocar(self.raiz / "auditoria/correcoes-rodada-1.json", json.dumps(itens, ensure_ascii=False), t)

    def briefing(self):
        return (self.raiz / "auditoria/briefing-do-auditor.md").read_text(encoding="utf-8")

    def test_sem_correcoes_grava_o_modelo_numerado_e_nao_manda_chamar(self):
        code, out = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 1, out)
        modelo = json.loads((self.raiz / "auditoria/correcoes-rodada-1.json").read_text(encoding="utf-8"))
        self.assertEqual([m["n"] for m in modelo], [1, 2])
        self.assertEqual({m["severidade"] for m in modelo}, {"critico", "alto"})
        self.assertIn("print", out)
        abertos = json.loads((self.raiz / "auditoria/abertos-rodada-1.json").read_text(encoding="utf-8"))["abertos"]
        self.assertEqual(len(abertos), 2)

    def test_conferencia_dirigida_so_criticos_e_altos_com_print_e_diff(self):
        self.correcoes()
        code, out = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 0, out)
        b = self.briefing()
        for trecho in ("3 minutos", "4 chamadas", "Sem nota nova", "Menu com alvo de toque", "Regra inventada",
                       "`prints/menu-768.png`", "auditoria/diff-dist.txt", '"estado"'):
            self.assertIn(trecho, b, trecho)
        self.assertNotIn("Legenda com 12 px", b)          # médio não vai para a conferência
        self.assertNotIn("Respiro curto", b)
        self.assertNotIn('"score"', b)
        diff = (self.raiz / "auditoria/diff-dist.txt").read_text(encoding="utf-8")
        self.assertIn("-<h1>Antes</h1>", diff)
        self.assertIn("+<h1>Depois</h1>", diff)
        self.assertNotIn("app.js", diff.split("Arquivos")[0] if "Arquivos" in diff else "")

    def test_print_de_antes_da_correcao_nao_vale(self):
        self.correcoes(t=1_000_150)   # depois da rodada 1, mas antes da dist mudar
        code, out = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 1, out)
        self.assertIn("prints/menu-768.png", out)

    def test_achado_sem_print_fica_faltando(self):
        self.correcoes(sem_print=True)
        code, out = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 1, out)
        self.assertIn("n=1", out)

    @unittest.skipUnless(TEM_PIL, "sem Pillow a prancha da conferência não é montada (o briefing lista os prints)")
    def test_prancha_junta_os_prints_numa_imagem_so(self):
        from PIL import Image
        (self.raiz / "prints").mkdir(exist_ok=True)
        for nome in ("prints/menu-768.png", "prints/regra.png"):
            Image.new("RGB", (800, 600), (200, 30, 30)).save(self.raiz / nome)
        itens = [{"n": 1, "print": "prints/menu-768.png", "recorte": "0,0,400,300", "o_que_mudou": "44 px"},
                 {"n": 2, "print": "prints/regra.png", "o_que_mudou": "bloco removido"}]
        tocar(self.raiz / "auditoria/correcoes-rodada-1.json", json.dumps(itens), None)
        for nome in ("prints/menu-768.png", "prints/regra.png", "auditoria/correcoes-rodada-1.json"):
            os.utime(self.raiz / nome, (1_000_300, 1_000_300))
        code, out = rodar(self.raiz, "--rodada", "2")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.raiz / "auditoria/conferencia/prancha.jpg").is_file())
        self.assertIn("auditoria/conferencia/prancha.jpg", self.briefing())


class RotuloDaPrancha(unittest.TestCase):
    @unittest.skipUnless(TEM_PIL, "sem Pillow não há prancha")
    def test_rotulo_usa_fonte_com_acento_quando_a_maquina_tem(self):
        # Na prova de 26/10 o rótulo saiu "Rodap? sem Termos": a fonte padrão do Pillow não tem acento.
        import importlib.util
        from PIL import ImageFont
        spec = importlib.util.spec_from_file_location("conf370", pathlib.Path(__file__).with_name("conferencia.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        lado = importlib.util.spec_from_file_location("lado370", pathlib.Path(__file__).with_name("lado-a-lado.py"))
        ll = importlib.util.module_from_spec(lado)
        lado.loader.exec_module(ll)
        esperado = ll.fonte(18)
        self.assertEqual(type(m.fonte_do_rotulo(18)), type(esperado))
        if isinstance(esperado, ImageFont.FreeTypeFont):
            self.assertIsInstance(m.fonte_do_rotulo(18), ImageFont.FreeTypeFont)


class SemRodada2(unittest.TestCase):
    def test_rodada_1_sem_critico_nem_alto_nao_tem_rodada_2(self):
        with tempfile.TemporaryDirectory() as d:
            raiz = pathlib.Path(d)
            montar(raiz)
            achados_rodada_1(raiz, com_alto=False)
            code, out = rodar(raiz, "--rodada", "2")
            self.assertEqual(code, 1, out)
            self.assertIn("não há rodada 2", out)


if __name__ == "__main__":
    unittest.main()
