#!/usr/bin/env python3
"""Cria robots.txt, sitemap.xml e 404.html na raiz do domínio, para a página passar nas regras 13 a 15 do gate-seo.py.

Por que existe (27/10/2026, auditoria de SEO da sales.juliocouto.com.br): o robots.txt, o sitemap.xml e
qualquer URL inexistente devolviam a home com 200 (soft 404). A causa era a mesma nos três: os arquivos não
existiam. No Cloudflare Pages a existência do 404.html é o que faz a URL inexistente dar 404 em vez de
devolver a home. Este script cria os três quando a URL final do domínio já se conhece.

O que cria (e só se o arquivo ainda não existir; NUNCA sobrescreve, e imprime o que pulou):
  - robots.txt: `User-agent: *`, `Allow: /` e `Sitemap:` absoluto, na raiz do domínio da URL final;
  - sitemap.xml: a URL final, com `lastmod` de hoje;
  - 404.html: curto, com `noindex`, `lang` da página, link para "/", título "Página não encontrada" e, quando o
    `<title>` da index.html tem uma marca depois de `|`, `·`, hífen ou travessão, o título leva a marca.

Uso: node scripts/py.mjs gerar-seo.py --dist <dir> --url-final <https://...> [--raiz <dir>]
  --raiz: pasta que vai na raiz do domínio (padrão: --dist). Página em subcaminho (/sobrai/) usa a do site principal.
Saída: 0 criou ou pulou, 2 erro de uso.
"""
import argparse
import datetime
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

EN_DASH, EM_DASH = chr(0x2013), chr(0x2014)   # por chr(): o hook de travessão barra o caractere escrito no arquivo
TRAVESSOES = EN_DASH + EM_DASH
SEPARADOR_DE_MARCA = re.compile(r"\s+[|·" + TRAVESSOES + r"-]\s+|\s*\|\s*")
MARCA_MAX = 40


def ler(caminho):
    return Path(caminho).read_text(encoding="utf-8-sig", errors="replace")


def marca_e_idioma(dist):
    """A marca (último pedaço do <title> da index.html) e o idioma da página. Sem index.html: ("", "pt-BR")."""
    index = Path(dist) / "index.html"
    if not index.is_file():
        return "", "pt-BR"
    texto = ler(index)
    lang = re.search(r"""<html\b[^>]*\blang\s*=\s*["']?([A-Za-z-]+)""", texto, re.I)
    titulo = re.search(r"<title[^>]*>(.*?)</title>", texto, re.I | re.S)
    marca = ""
    if titulo:
        bruto = " ".join(html.unescape(titulo.group(1)).split())
        pedacos = SEPARADOR_DE_MARCA.split(bruto)
        marca = pedacos[-1] if len(pedacos) > 1 else bruto
        marca = re.sub(rf"\s*[{TRAVESSOES}]\s*", ", ", marca).strip()
        if not 0 < len(marca) <= MARCA_MAX:
            marca = ""
    return marca, (lang.group(1) if lang else "pt-BR")


def texto_do_robots(url_final):
    p = urlparse(url_final)
    return f"User-agent: *\nAllow: /\n\nSitemap: {p.scheme}://{p.netloc}/sitemap.xml\n"


def texto_do_sitemap(url_final, hoje):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"  <url>\n    <loc>{html.escape(url_final, quote=False)}</loc>\n    <lastmod>{hoje}</lastmod>\n  </url>\n"
            "</urlset>\n")


def texto_do_404(marca, lang):
    titulo = "Página não encontrada" + (f" | {html.escape(marca)}" if marca else "")
    return ("<!doctype html>\n"
            f'<html lang="{html.escape(lang)}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{titulo}</title>\n"
            '<meta name="robots" content="noindex">\n'
            "<style>body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;"
            "font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a;background:#fff;text-align:center}"
            "h1{font-size:1.75rem;margin:0 0 12px}p{margin:0 0 20px;color:#555}"
            "a{color:#1a1a1a;font-weight:600}</style>\n"
            "</head>\n<body>\n<main>\n<h1>Página não encontrada</h1>\n"
            "<p>O endereço que você abriu não existe ou mudou de lugar.</p>\n"
            '<a href="/">Voltar para o início</a>\n</main>\n</body>\n</html>\n')


def gerar(dist, url_final, raiz=None, hoje=None):
    """Cria o que falta. Devolve a lista de linhas para imprimir (`criado: ...` ou `pulado, já existe: ...`)."""
    raiz = Path(raiz) if raiz else Path(dist)
    hoje = hoje or datetime.date.today().isoformat()
    marca, lang = marca_e_idioma(dist)
    conteudos = (("robots.txt", texto_do_robots(url_final)),
                 ("sitemap.xml", texto_do_sitemap(url_final, hoje)),
                 ("404.html", texto_do_404(marca, lang)))
    linhas = []
    for nome, texto in conteudos:
        alvo = raiz / nome
        if alvo.exists():
            linhas.append(f"pulado, já existe: {alvo}")
            continue
        alvo.write_text(texto, encoding="utf-8")
        linhas.append(f"criado: {alvo}")
    return linhas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", required=True)
    ap.add_argument("--url-final", required=True)
    ap.add_argument("--raiz")
    a = ap.parse_args(argv)
    if not a.url_final.lower().startswith("https://") or not urlparse(a.url_final).netloc:
        print(f"ERRO: a URL final precisa começar com https:// e ter o domínio (veio {a.url_final}).")
        return 2
    if not Path(a.dist).is_dir():
        print(f"ERRO: a pasta {a.dist} não existe.")
        return 2
    if a.raiz and not Path(a.raiz).is_dir():
        print(f"ERRO: a pasta da raiz {a.raiz} não existe.")
        return 2
    for linha in gerar(a.dist, a.url_final, a.raiz):
        print(linha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
