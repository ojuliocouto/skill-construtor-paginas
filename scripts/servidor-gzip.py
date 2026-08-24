"""Servidor estatico COM gzip, pra medir Lighthouse de forma honesta.

O `python3 -m http.server` nao comprime nada, e o Lighthouse acusou ~2700ms de
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
import socketserver
import sys


def parse_args():
    p = argparse.ArgumentParser(
        description="Servidor estatico com gzip, para medir Lighthouse de forma honesta.",
        epilog="Exemplo: python3 servidor-gzip.py ./public 8900",
    )
    p.add_argument("raiz", nargs="?", default=".", help="diretorio a servir (default: .)")
    p.add_argument("porta", nargs="?", default="8900", help="porta TCP (default: 8900)")
    args = p.parse_args()
    try:
        porta = int(args.porta)
    except ValueError:
        p.error(f"porta invalida: '{args.porta}' (precisa ser um numero inteiro)")
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


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    handler = functools.partial(Handler, directory=RAIZ)
    with socketserver.TCPServer(("", PORTA), handler) as httpd:
        print(f"servindo {RAIZ} com gzip na porta {PORTA}")
        httpd.serve_forever()
