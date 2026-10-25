"""Hash no lugar da data do arquivo (corte 5 da auditoria de velocidade, achado A1).

O que a auditoria mediu: `montar-dist.py` regravava a `index.html` em toda rodada de gates, mesmo
com o conteúdo igual. A data do arquivo mudava, o `pacote-auditoria.py` julgava as capturas
"anteriores à dist" e dizia PACOTE VELHO nos 4 itens, e o `gate-relatorio.py` fazia o mesmo com a
medida citada. Refazer a prova custa 191,7 s de máquina mais as voltas do modelo.

Regra nova, provada aqui:
  1. `montar-dist.py` só grava o arquivo cujo conteúdo mudou; a data de quem não mudou fica.
  2. `montar-dist.py` registra em `gates/_dist-hash.json` QUANDO o conteúdo da dist mudou de verdade.
  3. O pacote e o gate do relatório julgam a captura pelo hash: captura feita com a dist de HOJE
     vale; captura feita com outro conteúdo é velha, mesmo que a data do arquivo diga o contrário.
  4. Sem registro (projeto antigo) ou com a dist mexida à mão, vale a regra antiga da data.
"""
import contextlib
import importlib.util
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
URL = "http://localhost:8765/"


def carregar(nome, arquivo=None):
    spec = importlib.util.spec_from_file_location(nome.replace("-", "_"), AQUI / (arquivo or f"{nome}.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def dist_hash():
    sys.path.insert(0, str(AQUI))
    try:
        return carregar("dist_hash")
    finally:
        sys.path.remove(str(AQUI))


def escrever(caminho, texto, t=None):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(texto if isinstance(texto, bytes) else texto.encode("utf-8"))
    if t is not None:
        os.utime(caminho, (t, t))


def montar(proj, *extra):
    r = subprocess.run([sys.executable, str(AQUI / "montar-dist.py"), "--projeto", str(proj), *extra],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


HTML = """<!doctype html><html><head><link rel="stylesheet" href="estilo.css"></head>
<body><img src="imagens/a.webp" alt="x"></body></html>"""


def projeto_minimo(raiz):
    escrever(raiz / "index.html", HTML)
    escrever(raiz / "estilo.css", "body{color:#111}")
    escrever(raiz / "imagens/a.webp", b"RIFFwebp-a")
    return raiz


def montar_pacote_completo(raiz, t_prova):
    escrever(raiz / "evidencias/briefing.md", "briefing")
    escrever(raiz / "evidencias/sustentacao.md", "| frase | linha |")
    escrever(raiz / "PLANO.md", "plano")
    escrever(raiz / "referencias/sintese.md", "sintese")
    escrever(raiz / "referencias/a-dobra.png", b"\x89PNG")
    for nome in ("provas/prova-desktop.png", "provas/prova-mobile.png", "videos/prancha-desktop.png", "videos/prancha-mobile.png"):
        escrever(raiz / nome, b"\x89PNG", t_prova)


def pacote(raiz):
    r = subprocess.run([sys.executable, str(AQUI / "pacote-auditoria.py"), "--projeto", str(raiz), "--url", URL,
                        "--briefing-reflete-pedido", "sim"], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


class HashDaPasta(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.raiz = pathlib.Path(t.name)
        self.dh = dist_hash()

    def test_mesmo_conteudo_com_data_diferente_da_o_mesmo_hash(self):
        escrever(self.raiz / "a/index.html", "<p>oi</p>", 1_000_000)
        antes = self.dh.hash_pasta(self.raiz / "a")
        os.utime(self.raiz / "a/index.html", (2_000_000, 2_000_000))
        self.assertEqual(self.dh.hash_pasta(self.raiz / "a"), antes)

    def test_um_byte_trocado_muda_o_hash(self):
        escrever(self.raiz / "a/index.html", "<p>oi</p>")
        antes = self.dh.hash_pasta(self.raiz / "a")
        escrever(self.raiz / "a/index.html", "<p>oj</p>")
        self.assertNotEqual(self.dh.hash_pasta(self.raiz / "a"), antes)

    def test_arquivo_novo_ou_renomeado_muda_o_hash(self):
        escrever(self.raiz / "a/index.html", "<p>oi</p>")
        escrever(self.raiz / "a/x.css", "b{}")
        base = self.dh.hash_pasta(self.raiz / "a")
        os.rename(self.raiz / "a/x.css", self.raiz / "a/y.css")
        renomeado = self.dh.hash_pasta(self.raiz / "a")
        self.assertNotEqual(renomeado, base)
        escrever(self.raiz / "a/z.css", "c{}")
        self.assertNotEqual(self.dh.hash_pasta(self.raiz / "a"), renomeado)

    def test_a_ordem_de_criacao_nao_importa(self):
        escrever(self.raiz / "a/1.txt", "um")
        escrever(self.raiz / "a/2.txt", "dois")
        escrever(self.raiz / "b/2.txt", "dois")
        escrever(self.raiz / "b/1.txt", "um")
        self.assertEqual(self.dh.hash_pasta(self.raiz / "a"), self.dh.hash_pasta(self.raiz / "b"))

    def test_o_mesmo_texto_em_outro_arquivo_nao_confunde(self):
        # "ab" + "c" e "a" + "bc" não podem dar o mesmo hash
        escrever(self.raiz / "a/x", "ab")
        escrever(self.raiz / "a/y", "c")
        escrever(self.raiz / "b/x", "a")
        escrever(self.raiz / "b/y", "bc")
        self.assertNotEqual(self.dh.hash_pasta(self.raiz / "a"), self.dh.hash_pasta(self.raiz / "b"))

    def test_o_hash_do_python_e_o_do_node_sao_o_mesmo(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("PULADO: sem Node nesta máquina")
        escrever(self.raiz / "d/index.html", "<p>çã</p>")
        escrever(self.raiz / "d/imagens/a.webp", b"\x00\x01\x02binario")
        escrever(self.raiz / "d/fonts/f.woff2", b"fonte")
        r = subprocess.run([node, str(AQUI / "gates-cache.mjs"), "--hash-pasta", str(self.raiz / "d")],
                           capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip(), self.dh.hash_pasta(self.raiz / "d"))


class RegistroDeQuandoMudou(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.raiz = pathlib.Path(t.name)
        self.dh = dist_hash()
        escrever(self.raiz / "dist/index.html", "<p>A</p>")

    def test_registrar_duas_vezes_o_mesmo_conteudo_guarda_a_primeira_data(self):
        h1, mudou1 = self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        h2, mudou2 = self.dh.registrar(self.raiz, self.raiz / "dist", agora=5000.0)
        self.assertTrue(mudou1)
        self.assertFalse(mudou2)
        self.assertEqual(h1, h2)
        hist = self.dh.carregar_registro(self.raiz)["historico"]
        self.assertEqual([(e["hash"], e["desde"]) for e in hist], [(h1, 1000.0)])

    def test_conteudo_novo_abre_uma_entrada_nova(self):
        h1, _ = self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        escrever(self.raiz / "dist/index.html", "<p>B</p>")
        h2, mudou = self.dh.registrar(self.raiz, self.raiz / "dist", agora=2000.0)
        self.assertTrue(mudou)
        self.assertNotEqual(h1, h2)
        hist = self.dh.carregar_registro(self.raiz)["historico"]
        self.assertEqual([e["desde"] for e in hist], [1000.0, 2000.0])

    def test_captura_feita_com_o_mesmo_conteudo_e_fresca_mesmo_com_a_data_da_dist_nova(self):
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        os.utime(self.raiz / "dist/index.html", (9000.0, 9000.0))     # data nova, conteúdo igual
        fresca, _ = self.dh.captura_fresca(self.raiz, self.raiz / "dist", 1500.0)
        self.assertTrue(fresca)

    def test_captura_anterior_a_mudanca_de_conteudo_e_velha(self):
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        escrever(self.raiz / "dist/index.html", "<p>B</p>")
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=2000.0)
        fresca, motivo = self.dh.captura_fresca(self.raiz, self.raiz / "dist", 1500.0)
        self.assertFalse(fresca)
        self.assertIn("conteúdo", motivo)
        fresca2, _ = self.dh.captura_fresca(self.raiz, self.raiz / "dist", 2500.0)
        self.assertTrue(fresca2)

    def test_volta_ao_conteudo_antigo_torna_fresca_a_captura_daquela_epoca(self):
        # A -> B -> A: quem foi capturado enquanto a dist era A mostra o A de hoje
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        escrever(self.raiz / "dist/index.html", "<p>B</p>")
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=2000.0)
        escrever(self.raiz / "dist/index.html", "<p>A</p>")
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=3000.0)
        self.assertTrue(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 1500.0)[0])
        self.assertFalse(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 2500.0)[0])

    def test_dist_mexida_a_mao_sem_passar_pelo_montar_dist_vale_pela_data(self):
        self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        escrever(self.raiz / "dist/index.html", "<p>editada à mão</p>", 5000.0)
        self.assertFalse(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 4000.0)[0])
        self.assertTrue(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 6000.0)[0])

    def test_sem_registro_nenhum_vale_a_regra_antiga_da_data(self):
        escrever(self.raiz / "dist/index.html", "<p>A</p>", 5000.0)
        self.assertFalse(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 4000.0)[0])
        self.assertTrue(self.dh.captura_fresca(self.raiz, self.raiz / "dist", 6000.0)[0])

    def test_registro_corrompido_nao_derruba_nada(self):
        escrever(self.raiz / "gates/_dist-hash.json", "{ isto não é json")
        self.assertEqual(self.dh.carregar_registro(self.raiz)["historico"], [])
        h, mudou = self.dh.registrar(self.raiz, self.raiz / "dist", agora=1000.0)
        self.assertTrue(mudou)


class MontarDistSoGravaOQueMudou(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.proj = projeto_minimo(pathlib.Path(t.name))

    def congelar_datas(self, t=1_000_000):
        for p in (self.proj / "dist").rglob("*"):
            if p.is_file():
                os.utime(p, (t, t))

    def test_segunda_montagem_sem_mudanca_nao_mexe_na_data_de_nenhum_arquivo(self):
        self.assertEqual(montar(self.proj)[0], 0)
        self.congelar_datas()
        code, saida = montar(self.proj)
        self.assertEqual(code, 0, saida)
        for p in (self.proj / "dist").rglob("*"):
            if p.is_file():
                self.assertEqual(int(p.stat().st_mtime), 1_000_000, f"{p.name} foi regravado com o conteúdo igual")

    def test_a_index_nova_e_o_arquivo_trocado_sao_gravados_e_o_resto_fica(self):
        montar(self.proj)
        self.congelar_datas()
        escrever(self.proj / "estilo.css", "body{color:#222}")
        code, saida = montar(self.proj)
        self.assertEqual(code, 0, saida)
        dist = self.proj / "dist"
        self.assertEqual((dist / "estilo.css").read_text(encoding="utf-8"), "body{color:#222}")
        self.assertEqual(int((dist / "index.html").stat().st_mtime), 1_000_000)
        self.assertEqual(int((dist / "imagens/a.webp").stat().st_mtime), 1_000_000)
        self.assertGreater(int((dist / "estilo.css").stat().st_mtime), 1_000_000 - 1)

    def test_a_index_com_conteudo_novo_e_regravada(self):
        montar(self.proj)
        self.congelar_datas()
        escrever(self.proj / "index.html", HTML.replace("x", "y"))
        montar(self.proj)
        self.assertIn('alt="y"', (self.proj / "dist/index.html").read_text(encoding="utf-8"))

    def test_o_que_a_pagina_deixou_de_usar_sai_da_dist(self):
        montar(self.proj)
        escrever(self.proj / "dist/sobra.txt", "lixo")
        escrever(self.proj / "dist/pasta-velha/x.txt", "lixo")
        montar(self.proj)
        self.assertFalse((self.proj / "dist/sobra.txt").exists())
        self.assertFalse((self.proj / "dist/pasta-velha").exists())

    def test_arquivo_da_dist_que_virou_pasta_ou_o_contrario_nao_quebra(self):
        montar(self.proj)
        (self.proj / "dist/imagens/a.webp").unlink()
        (self.proj / "dist/imagens").rmdir()
        escrever(self.proj / "dist/imagens", "agora sou um arquivo")
        code, saida = montar(self.proj)
        self.assertEqual(code, 0, saida)
        self.assertEqual((self.proj / "dist/imagens/a.webp").read_bytes(), b"RIFFwebp-a")

    def test_a_mensagem_dist_refeita_continua_e_diz_que_nada_mudou(self):
        montar(self.proj)
        code, saida = montar(self.proj)
        self.assertRegex(saida, r"dist refeita")
        self.assertIn("servidor", saida)
        self.assertRegex(saida, r"inalterad", "tem que dizer que nada mudou")

    def test_registra_o_hash_no_projeto(self):
        montar(self.proj)
        reg = json.loads((self.proj / "gates/_dist-hash.json").read_text(encoding="utf-8"))
        dh = dist_hash()
        self.assertEqual(reg["historico"][-1]["hash"], dh.hash_pasta(self.proj / "dist"))
        n = len(reg["historico"])
        montar(self.proj)
        reg2 = json.loads((self.proj / "gates/_dist-hash.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reg2["historico"]), n, "montar sem mudança não abre entrada nova")
        escrever(self.proj / "estilo.css", "body{color:#333}")
        montar(self.proj)
        reg3 = json.loads((self.proj / "gates/_dist-hash.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reg3["historico"]), n + 1)

    def test_a_dist_publicada_nao_ganha_arquivo_extra(self):
        # o registro mora em gates/, nunca dentro da dist (o gate-publicacao reprova arquivo que a página não usa)
        montar(self.proj)
        nomes = sorted(p.relative_to(self.proj / "dist").as_posix() for p in (self.proj / "dist").rglob("*") if p.is_file())
        self.assertEqual(nomes, ["estilo.css", "imagens/a.webp", "index.html"])


class PacoteJulgaPeloHash(unittest.TestCase):
    """O erro medido: remontar a dist idêntica deixava as 4 capturas VELHAS."""

    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.proj = projeto_minimo(pathlib.Path(t.name))
        self.dh = dist_hash()
        # a dist foi montada há 200 s; as provas foram capturadas há 100 s, depois dela
        self.agora = time.time()
        montar(self.proj)
        for p in (self.proj / "dist").rglob("*"):
            if p.is_file():
                os.utime(p, (self.agora - 200, self.agora - 200))
        reg = json.loads((self.proj / "gates/_dist-hash.json").read_text(encoding="utf-8"))
        reg["historico"][-1]["desde"] = self.agora - 200
        escrever(self.proj / "gates/_dist-hash.json", json.dumps(reg))
        montar_pacote_completo(self.proj, self.agora - 100)

    def test_pacote_completo_antes_de_remontar(self):
        code, saida = pacote(self.proj)
        self.assertEqual(code, 0, saida)

    def test_remontar_a_dist_identica_nao_deixa_o_pacote_velho(self):
        code, saida = montar(self.proj)
        self.assertEqual(code, 0, saida)
        code, saida = pacote(self.proj)
        self.assertEqual(code, 0, "PACOTE VELHO com a dist idêntica (achado A1):\n" + saida)
        self.assertNotIn("VELHO", saida)

    def test_mudar_a_pagina_de_verdade_deixa_o_pacote_velho(self):
        escrever(self.proj / "estilo.css", "body{color:#999}")
        montar(self.proj)
        code, saida = pacote(self.proj)
        self.assertEqual(code, 1, saida)
        self.assertIn("PACOTE VELHO", saida)
        for nome in ("prova-desktop.png", "prova-mobile.png", "prancha-desktop.png", "prancha-mobile.png"):
            self.assertRegex(saida, rf"\[VELHO \] {nome}")

    def test_o_manifesto_leva_o_hash_da_dist(self):
        pacote(self.proj)
        m = json.loads((self.proj / "auditoria/pacote.json").read_text(encoding="utf-8"))
        self.assertEqual(m.get("dist_hash"), self.dh.hash_pasta(self.proj / "dist"))

    def test_sem_registro_o_pacote_volta_a_regra_da_data(self):
        (self.proj / "gates/_dist-hash.json").unlink()
        os.utime(self.proj / "dist/index.html", (self.agora, self.agora))   # a dist ficou mais nova que as capturas
        code, saida = pacote(self.proj)
        self.assertEqual(code, 1, saida)
        self.assertIn("PACOTE VELHO", saida)


class GateDoRelatorioJulgaPeloHash(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.proj = projeto_minimo(pathlib.Path(t.name))
        self.agora = time.time()
        montar(self.proj)
        for p in (self.proj / "dist").rglob("*"):
            if p.is_file():
                os.utime(p, (self.agora - 200, self.agora - 200))
        reg = json.loads((self.proj / "gates/_dist-hash.json").read_text(encoding="utf-8"))
        reg["historico"][-1]["desde"] = self.agora - 200
        escrever(self.proj / "gates/_dist-hash.json", json.dumps(reg))
        escrever(self.proj / "gates/lighthouse.txt", "Lighthouse 100\ncarregou em 1,2 s\n", self.agora - 100)
        self.gate = carregar("gate-relatorio")

    def checar(self):
        escrever(self.proj / "relatorio.md", "- Lighthouse 100 em desempenho (`gates/lighthouse.txt`)\n")
        return self.gate.checar(self.proj / "relatorio.md", base=self.proj, dist=self.proj / "dist")

    def test_medida_feita_com_a_dist_de_hoje_vale(self):
        self.assertEqual(self.checar(), [])

    def test_dist_remontada_igual_nao_invalida_a_medida(self):
        montar(self.proj)
        self.assertEqual(self.checar(), [], "gate do relatório acusou 'anterior à dist/' com a dist idêntica")

    def test_dist_com_conteudo_novo_invalida_a_medida(self):
        escrever(self.proj / "estilo.css", "body{color:#999}")
        montar(self.proj)
        p = self.checar()
        self.assertTrue(any("anterior à dist/ final" in x for x in p), p)


if __name__ == "__main__":
    unittest.main(verbosity=2)
