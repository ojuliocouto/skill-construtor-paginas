"""Servidor estatico COM gzip, pra medir Lighthouse de forma honesta.

O `http.server` simples do Python nao comprime nada, e o Lighthouse acusou ~2700ms de
economia possivel so em compressao de texto. Isso inflava o LCP das duas
versoes e escondia a diferenca real entre elas. Cloudflare Pages (onde a pagina
vive) serve com Brotli/gzip, entao medir sem compressao compara um cenario que
nao existe.
"""
import argparse
import functools
import gzip
import http.server
import io
import os
import socket
import socketserver
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lancador import comando  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(
        description="Servidor estatico com gzip, para medir Lighthouse de forma honesta.",
        epilog=f"Exemplo: {comando('servidor-gzip.py')} ./public 8900",
    )
    p.add_argument("raiz", nargs="?", default=".", help="diretório a servir (default: .)")
    p.add_argument("porta", nargs="?", default="8900",
                   help="porta TCP preferida (default: 8900); se estiver ocupada o servidor escolhe outra e imprime a URL")
    args = p.parse_args()
    try:
        porta = int(args.porta)
    except ValueError:
        p.error(f"porta inválida: '{args.porta}' (precisa ser um número inteiro)")
    return args.raiz, porta


RAIZ, PORTA = parse_args()

COMPRIMIVEIS = (".html", ".css", ".js", ".json", ".svg", ".txt", ".map")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "public, max-age=3600")
        super().end_headers()

    def do_GET(self):
        caminho = self.translate_path(self.path)
        if os.path.isdir(caminho):
            caminho = os.path.join(caminho, "index.html")

        aceita_gzip = "gzip" in self.headers.get("Accept-Encoding", "")
        if not (aceita_gzip and os.path.isfile(caminho) and caminho.endswith(COMPRIMIVEIS)):
            return super().do_GET()

        with open(caminho, "rb") as f:
            bruto = f.read()

        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=6) as gz:
            gz.write(bruto)
        corpo = buf.getvalue()

        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(caminho))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def log_message(self, *args):
        pass


def abrir(handler, porta):
    """Abre o servidor na porta pedida; se ela estiver ocupada, deixa o sistema escolher uma livre.

    Porta fixa foi o P11 do teste de ponta a ponta (3.5.10): com outras sessoes na mesma maquina a 8765
    estava ocupada ou o servidor dela caia, e os gates estouravam com ERR_CONNECTION_REFUSED. Devolve
    (servidor, porta_em_uso, porta_pedida_ocupada_ou_None).
    """
    try:
        if porta != 0 and alguem_responde(porta):
            raise OSError(f"porta {porta} ocupada")
        return socketserver.TCPServer(("", porta), handler), porta, None
    except OSError:
        if porta == 0:
            raise
        httpd = socketserver.TCPServer(("", 0), handler)
        return httpd, httpd.server_address[1], porta


def alguem_responde(porta):
    """Ha um servidor ouvindo em 127.0.0.1:porta? Abrir a porta so no bind nao basta: no macOS e no Linux um servidor
    em 0.0.0.0 consegue abrir a MESMA porta de outro que ouve em 127.0.0.1, e o trafego do navegador vai para o outro."""
    try:
        with socket.create_connection(("127.0.0.1", porta), timeout=0.5):
            return True
    except OSError:
        return False


def dizer(texto):
    print(texto, flush=True)   # com pipe o Python guardaria a linha no buffer e quem le a URL esperaria para sempre


if __name__ == "__main__":
    # Sem SO_REUSEADDR de proposito: com ele dois processos conseguem abrir a mesma porta (no Windows sempre; no macOS e no
    # Linux quando um ouve em 127.0.0.1 e o outro em 0.0.0.0) e o segundo roubaria o trafego do primeiro. Porta que ainda
    # nao foi liberada pelo sistema (TIME_WAIT) cai no mesmo caminho da ocupada: outra porta, e a URL impressa.
    socketserver.TCPServer.allow_reuse_address = False
    handler = functools.partial(Handler, directory=RAIZ)
    httpd, porta_em_uso, ocupada = abrir(handler, PORTA)
    with httpd:
        if ocupada is not None:
            dizer(f"a porta {ocupada} esta ocupada por outro processo: servindo na porta {porta_em_uso}")
        dizer(f"servindo {RAIZ} com gzip na porta {porta_em_uso}")
        dizer(f"URL: http://127.0.0.1:{porta_em_uso}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
