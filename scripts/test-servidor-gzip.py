"""P11 (3.5.10): o servidor local não pode depender de porta fixa nem cair calado.

O teste de ponta a ponta da Torra Clara (3 h 15 min) perdeu rodadas inteiras de gates porque o roteiro
usava a porta 8765 e outras sessões, na mesma máquina, ocupavam ou derrubavam o servidor. Aqui:
  1. porta livre: serve nela e imprime a URL;
  2. porta ocupada: escolhe outra, diz isso e imprime a URL que funciona (a ocupada fica com o dono);
  3. a saída chega mesmo com o pipe (sem esperar o buffer encher);
  4. o gzip continua funcionando;
  5. o `montar-dist.py` refaz o CONTEÚDO da dist sem apagar a pasta, e um servidor que serve essa pasta
     (cwd dentro dela) segue entregando a página nova.
"""
import gzip
import http.client
import os
import pathlib
import queue
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
SERVIDOR = AQUI / "servidor-gzip.py"
MONTAR = AQUI / "montar-dist.py"
PROCS = []


def porta_livre():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def subir(pasta, porta):
    env = dict(os.environ, PYTHONUTF8="1")
    p = subprocess.Popen([sys.executable, str(SERVIDOR), str(pasta), str(porta)], stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, encoding="utf-8", env=env)
    PROCS.append(p)
    return p


def ler_url(p, limite=10):
    """Lê as linhas do servidor até achar a URL (com prazo: sem a saída, o teste reprova em vez de travar)."""
    fila = queue.Queue()

    def leitor():
        for linha in p.stdout:
            fila.put(linha)

    threading.Thread(target=leitor, daemon=True).start()
    fim = time.time() + limite
    texto = ""
    while time.time() < fim:
        try:
            linha = fila.get(timeout=0.2)
        except queue.Empty:
            continue
        texto += linha
        m = re.search(r"(http://127\.0\.0\.1:(\d+)/)", linha)
        if m:
            return m.group(1), texto
    return None, texto


def get(url, gz=False):
    m = re.match(r"http://([^:/]+):(\d+)(/.*)", url)
    c = http.client.HTTPConnection(m.group(1), int(m.group(2)), timeout=5)
    c.request("GET", m.group(3), headers={"Accept-Encoding": "gzip"} if gz else {})
    r = c.getresponse()
    corpo = r.read()
    enc = r.getheader("Content-Encoding")
    c.close()
    return r.status, enc, corpo


def pasta_com_pagina(texto="ola"):
    d = pathlib.Path(tempfile.mkdtemp(prefix="srv "))
    (d / "index.html").write_text(f"<html><body>{texto}</body></html>", encoding="utf-8")
    return d


class Servidor(unittest.TestCase):
    def tearDown(self):
        while PROCS:
            p = PROCS.pop()
            p.kill()
            p.wait()
            if p.stdout:
                p.stdout.close()

    def test_porta_livre_serve_nela_e_imprime_a_url(self):
        d = pasta_com_pagina("pagina um")
        porta = porta_livre()
        p = subir(d, porta)
        url, texto = ler_url(p)
        self.assertEqual(url, f"http://127.0.0.1:{porta}/", texto)
        st, _, corpo = get(url)
        self.assertEqual(st, 200)
        self.assertIn(b"pagina um", corpo)

    def test_porta_ocupada_escolhe_outra_diz_e_imprime_a_url(self):
        d = pasta_com_pagina("pagina dois")
        dono = socket.socket()
        dono.bind(("127.0.0.1", 0))
        dono.listen(1)
        ocupada = dono.getsockname()[1]
        try:
            p = subir(d, ocupada)
            url, texto = ler_url(p)
            self.assertIsNotNone(url, f"o servidor não imprimiu a URL: {texto!r}")
            porta_nova = int(re.search(r":(\d+)/", url).group(1))
            self.assertNotEqual(porta_nova, ocupada, "serviu na porta ocupada por outro processo")
            self.assertIn(str(ocupada), texto, "não disse qual porta estava ocupada")
            self.assertRegex(texto, r"ocupad", "não disse que a porta estava ocupada")
            st, _, corpo = get(url)
            self.assertEqual(st, 200)
            self.assertIn(b"pagina dois", corpo)
        finally:
            dono.close()

    def test_a_saida_chega_pelo_pipe_sem_esperar_o_buffer(self):
        # ler_url tem limite de 10 s: se a linha ficasse presa no buffer do pipe, a URL nunca chegaria
        d = pasta_com_pagina()
        p = subir(d, porta_livre())
        url, texto = ler_url(p, limite=10)
        self.assertIsNotNone(url, f"a URL ficou presa no buffer: {texto!r}")

    def test_gzip_continua(self):
        d = pasta_com_pagina("comprimida")
        p = subir(d, porta_livre())
        url, _ = ler_url(p)
        st, enc, corpo = get(url, gz=True)
        self.assertEqual((st, enc), (200, "gzip"))
        self.assertIn(b"comprimida", gzip.decompress(corpo))

    def test_porta_invalida_continua_dando_erro_claro(self):
        r = subprocess.run([sys.executable, str(SERVIDOR), ".", "abc"], capture_output=True, text=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("porta inválida", r.stderr)


class MontarDist(unittest.TestCase):
    def tearDown(self):
        while PROCS:
            p = PROCS.pop()
            p.kill()
            p.wait()
            if p.stdout:
                p.stdout.close()

    def montar(self, proj):
        return subprocess.run([sys.executable, str(MONTAR), "--projeto", str(proj)], capture_output=True, text=True,
                              encoding="utf-8", env=dict(os.environ, PYTHONUTF8="1"))

    def test_refazer_a_dist_mantem_a_pasta_e_o_servidor_dentro_dela_entrega_a_pagina_nova(self):
        proj = pathlib.Path(tempfile.mkdtemp(prefix="proj "))
        (proj / "index.html").write_text("<html><body>versao A</body></html>", encoding="utf-8")
        r = self.montar(proj)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dist = proj / "dist"
        inode_antes = dist.stat().st_ino
        porta = porta_livre()
        # servidor que serve o diretório corrente (cwd = dist): é o que o aluno faz com `python -m http.server`
        srv = subprocess.Popen([sys.executable, "-m", "http.server", str(porta), "--bind", "127.0.0.1"], cwd=dist,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        PROCS.append(srv)
        url = f"http://127.0.0.1:{porta}/index.html"
        for _ in range(50):
            try:
                st, _, corpo = get(url)
                break
            except OSError:
                time.sleep(0.1)
        self.assertIn(b"versao A", corpo)
        (proj / "index.html").write_text("<html><body>versao B</body></html>", encoding="utf-8")
        (dist / "sobra-velha.txt").write_text("lixo da montagem anterior", encoding="utf-8")
        r = self.montar(proj)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(dist.stat().st_ino, inode_antes, "a pasta dist foi apagada e recriada: quem estava dentro dela perdeu o chão")
        self.assertFalse((dist / "sobra-velha.txt").exists(), "a dist refeita tem que sair só com o que a página usa")
        st, _, corpo = get(url)
        self.assertEqual(st, 200)
        self.assertIn(b"versao B", corpo, "o servidor que serve a dist não entregou a página nova")

    def test_avisa_que_a_dist_servida_foi_refeita_quando_ela_ja_existia(self):
        proj = pathlib.Path(tempfile.mkdtemp(prefix="proj "))
        (proj / "index.html").write_text("<html><body>x</body></html>", encoding="utf-8")
        primeira = self.montar(proj)
        self.assertNotIn("refeita", primeira.stdout, "primeira montagem não tem o que avisar")
        segunda = self.montar(proj)
        self.assertRegex(segunda.stdout, r"dist refeita", segunda.stdout)
        self.assertIn("servidor", segunda.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
