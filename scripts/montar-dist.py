#!/usr/bin/env python3
"""Monta a pasta de publicação (`dist/`) só com o que a página usa.

Por que existe (02/10/2026, auditoria da v3): a pasta do projeto mistura a página com a casa
(prints de referências de terceiros, briefing com as pendências da cliente, evidências, gates,
JSON de auditoria, fotos de origem). Publicar a pasta do projeto leva tudo isso para o ar. O
deploy sai SEMPRE de `dist/`, montada por este script e conferida pelo `gate-publicacao.py`.

O que entra: `index.html` e todo arquivo local que ele referencia (src, href, srcset,
imagesrcset, og:image relativa, url() dos CSS e dos estilos em linha), mais robots.txt,
sitemap.xml, 404.html, _headers e _redirects quando existirem. Nada mais.

O 404.html entra aqui porque nenhuma página o referencia, e é a existência dele que faz a hospedagem
(Cloudflare Pages) responder 404 a uma URL inexistente em vez de devolver a home com 200 (soft 404,
auditoria de SEO da sales.juliocouto.com.br, 27/10/2026). `gerar-seo.py` cria o arquivo.

`--css-em-linha` troca cada `<link rel="stylesheet">` local por um `<style>` com o conteúdo
(as url() reescritas para a raiz): tira o CSS do caminho crítico, que no celular custava 1,3 s
de bloqueio de renderização na v3.

Uso: node scripts/py.mjs montar-dist.py --projeto <dir> [--saida dist] [--css-em-linha]
"""
import argparse
import filecmp
import os
import re
import shutil
import sys
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dist_hash  # noqa: E402  (hash do conteúdo da dist e o registro de quando ela mudou de verdade)

EXTRAS = ("robots.txt", "sitemap.xml", "404.html", "_headers", "_redirects", "_routes.json", "favicon.ico")
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


def sincronizar(raiz, saida, usados, html_bytes):
    """Deixa `saida` com exatamente os arquivos de `usados`, gravando SÓ o que mudou.

    Achado A1 da auditoria de velocidade: esvaziar a pasta e copiar tudo de novo mudava a data de todos os arquivos
    (e da index.html, sempre), e o pacote do auditor e o gate do relatório julgavam toda captura "anterior à dist".
    Aqui o arquivo de conteúdo igual fica como está, com a data de antes. A pasta nunca é apagada: servidor ou
    terminal que está "dentro" da dist perde o chão se a pasta some (P11 da 3.5.10).
    Devolve (lista dos gravados, quantidade de iguais mantidos)."""
    desejados = set(usados) | {"index.html"}
    pastas = {pai.as_posix() for rel in desejados for pai in PurePosixPath(rel).parents if pai.as_posix() != "."}
    # 1. tira o que a página não usa mais (arquivo, pasta, link, e o arquivo que virou pasta ou o contrário)
    for atual, subpastas, nomes in os.walk(saida, topdown=True, followlinks=False):
        base = Path(atual)
        rel_base = base.relative_to(saida).as_posix()
        for nome in list(subpastas):
            rel = nome if rel_base == "." else f"{rel_base}/{nome}"
            p = base / nome
            if p.is_symlink():
                p.unlink()
                subpastas.remove(nome)
            elif rel in desejados or rel not in pastas:
                shutil.rmtree(p)
                subpastas.remove(nome)
        for nome in nomes:
            rel = nome if rel_base == "." else f"{rel_base}/{nome}"
            p = base / nome
            if rel not in desejados or p.is_symlink() or rel in pastas:
                p.unlink()
    # 2. grava o que mudou
    gravados, iguais = [], 0
    for rel in sorted(desejados):
        destino = saida / rel
        if rel == "index.html":
            igual = destino.is_file() and destino.read_bytes() == html_bytes
        else:
            igual = destino.is_file() and filecmp.cmp(raiz / rel, destino, shallow=False)
        if igual:
            iguais += 1
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        if rel == "index.html":
            destino.write_bytes(html_bytes)
        else:
            shutil.copy2(raiz / rel, destino)
        gravados.append(rel)
    return gravados, iguais


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
    refeita = saida.exists()
    saida.mkdir(parents=True, exist_ok=True)
    gravados, iguais = sincronizar(raiz, saida, usados, html.encode("utf-8"))
    total = sum(p.stat().st_size for p in saida.rglob("*") if p.is_file())
    print(f"dist montada: {len(usados)} arquivo(s), {total / 1024:.1f} KiB em {saida}")
    if refeita:
        print(f"dist refeita: o conteúdo de {saida} foi trocado e a pasta foi mantida. Um servidor que serve esta pasta segue no ar "
              "e entrega a versão nova; se ele caiu, suba de novo com servidor-gzip.py (ele imprime a URL).")
        print(f"  {len(gravados)} arquivo(s) gravado(s), {iguais} igual(is) mantido(s) com a data de antes"
              + ("; dist inalterada: nenhum arquivo mudou." if not gravados else "."))
    if saida.parent == raiz:
        # O registro do hash mora no projeto (gates/), nunca dentro da dist: o gate-publicacao reprova arquivo que a página não usa.
        h, mudou = dist_hash.registrar(raiz, saida)
        print(f"  conteúdo da dist: {h[:12]} ({'mudou' if mudou else 'o mesmo da montagem anterior'})")
    for rel in sorted(usados):
        print(f"  {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
