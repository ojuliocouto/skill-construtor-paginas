#!/usr/bin/env python3
"""Monta a pasta de publicação (`dist/`) só com o que a página usa.

Por que existe (02/10/2026, auditoria da v3): a pasta do projeto mistura a página com a casa
(prints de referências de terceiros, briefing com as pendências da cliente, evidências, gates,
JSON de auditoria, fotos de origem). Publicar a pasta do projeto leva tudo isso para o ar. O
deploy sai SEMPRE de `dist/`, montada por este script e conferida pelo `gate-publicacao.py`.

O que entra: `index.html` e todo arquivo local que ele referencia (src, href, srcset,
imagesrcset, og:image relativa, url() dos CSS e dos estilos em linha), mais robots.txt,
sitemap.xml, _headers e _redirects quando existirem. Nada mais.

`--css-em-linha` troca cada `<link rel="stylesheet">` local por um `<style>` com o conteúdo
(as url() reescritas para a raiz): tira o CSS do caminho crítico, que no celular custava 1,3 s
de bloqueio de renderização na v3.

Uso: node scripts/py.mjs montar-dist.py --projeto <dir> [--saida dist] [--css-em-linha]
"""
import argparse
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path

EXTRAS = ("robots.txt", "sitemap.xml", "_headers", "_redirects", "_routes.json", "favicon.ico")
URL_CSS = re.compile(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)")


def local(ref):
    ref = (ref or "").strip()
    if not ref or ref.startswith(("#", "data:", "mailto:", "tel:", "javascript:", "//")) or re.match(r"^[a-z][a-z0-9+.-]*:", ref, re.I):
        return None
    return ref.split("#")[0].split("?")[0] or None


class Coletor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.estilos, self.css = [], [], []
        self._em_style = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for chave in ("src", "href", "poster", "data-src"):
            if a.get(chave):
                self.refs.append(a[chave])
                if tag == "link" and chave == "href" and "stylesheet" in (a.get("rel") or ""):
                    self.css.append(a[chave])
        for chave in ("srcset", "imagesrcset", "data-srcset"):
            for parte in (a.get(chave) or "").split(","):
                if parte.strip():
                    self.refs.append(parte.strip().split()[0])
        if tag == "meta" and (a.get("property") or a.get("name") or "").lower() in ("og:image", "twitter:image"):
            self.refs.append(a.get("content") or "")
        if a.get("style"):
            self.estilos.append(a["style"])
        self._em_style = tag == "style"

    def handle_endtag(self, tag):
        if tag == "style":
            self._em_style = False

    def handle_data(self, data):
        if self._em_style:
            self.estilos.append(data)


def referenciados(raiz):
    """Conjunto de caminhos relativos (POSIX) que a página usa, a partir do index.html."""
    raiz = Path(raiz).resolve()
    html = (raiz / "index.html").read_text(encoding="utf-8-sig")
    c = Coletor()
    c.feed(html)
    usados = {"index.html"}
    pendentes = [(r, raiz) for r in c.refs] + [(m.group(2), raiz) for s in c.estilos for m in URL_CSS.finditer(s)]
    while pendentes:
        ref, base = pendentes.pop()
        ref = local(ref)
        if not ref:
            continue
        alvo = (base / ref.lstrip("/")) if not ref.startswith("/") else (raiz / ref.lstrip("/"))
        alvo = Path(os.path.normpath(alvo))
        try:
            rel = alvo.relative_to(raiz)
        except ValueError:
            continue  # fora da pasta da página: nunca entra
        rel = rel.as_posix()
        if rel in usados or not alvo.is_file():
            continue
        usados.add(rel)
        if alvo.suffix.lower() == ".css":
            for m in URL_CSS.finditer(alvo.read_text(encoding="utf-8-sig")):
                pendentes.append((m.group(2), alvo.parent))
    for extra in EXTRAS:
        if (raiz / extra).is_file():
            usados.add(extra)
    return usados


def css_em_linha(raiz, html, usados):
    """Troca <link rel=stylesheet href=local> por <style>, com url() reescritas para a raiz."""
    def trocar(m):
        tag = m.group(0)
        href = re.search(r'href\s*=\s*["\']([^"\']+)', tag)
        ref = local(href.group(1)) if href else None
        if not ref or not (raiz / ref).is_file():
            return tag
        arquivo = raiz / ref
        texto = arquivo.read_text(encoding="utf-8-sig")

        def raiz_url(u):
            alvo = local(u.group(2))
            if not alvo:
                return u.group(0)
            novo = Path(os.path.normpath(arquivo.parent / alvo)).relative_to(raiz).as_posix()
            return f"url('{novo}')"
        usados.discard(ref)
        return "<style>" + URL_CSS.sub(raiz_url, texto) + "</style>"
    return re.sub(r"<link\b[^>]*rel\s*=\s*[\"']stylesheet[\"'][^>]*>", trocar, html, flags=re.I)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--saida", default="dist")
    ap.add_argument("--css-em-linha", action="store_true")
    a = ap.parse_args(argv)
    raiz = Path(a.projeto).resolve()
    if not (raiz / "index.html").is_file():
        print(f"ERRO: {raiz}/index.html não existe.")
        return 2
    saida = Path(a.saida) if Path(a.saida).is_absolute() else raiz / a.saida
    if saida.resolve() == raiz:
        print("ERRO: a saída não pode ser a própria pasta do projeto.")
        return 2
    usados = referenciados(raiz)
    html = (raiz / "index.html").read_text(encoding="utf-8-sig")
    if a.css_em_linha:
        html = css_em_linha(raiz, html, usados)
        # o CSS em linha pode ter trazido url() que antes só o .css citava: já estão em `usados`
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir(parents=True)
    for rel in sorted(usados):
        if rel == "index.html":
            continue
        destino = saida / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(raiz / rel, destino)
    (saida / "index.html").write_text(html, encoding="utf-8")
    total = sum(p.stat().st_size for p in saida.rglob("*") if p.is_file())
    print(f"dist montada: {len(usados)} arquivo(s), {total / 1024:.1f} KiB em {saida}")
    for rel in sorted(usados):
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
