#!/usr/bin/env python3
"""Gate de rastreamento: a dist/ tem o pixel e os eventos que o PLANO pediu.

Uso:
  node scripts/py.mjs gate-rastreamento.py --dist <dir>/dist --plano <dir>/PLANO.md
  node scripts/py.mjs gate-rastreamento.py --dist <dir>/dist --pedido meta,ga4     (ou meta, ga4, nenhum)

Com "Pixel pedido: nenhum", passa sem olhar a página. Senão reprova (exit 1) se faltar o
bloco window.RASTREIO, o carregador de cada ferramenta pedida, o ouvinte de [data-evento], os
marcos de rolagem 50 e 90, data-evento="clique_whatsapp" em cada link de WhatsApp,
data-evento="clique_cta" em pelo menos um botão principal ou data-evento="envio_formulario"
em cada formulário. ID vazio no window.RASTREIO só avisa: a página funciona e não mede.
Snippet e eventos: references/rastreamento.md.
"""
import argparse
import pathlib
import re
import sys
from html.parser import HTMLParser


class Elementos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.forms, self.ctas = [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        ev = a.get("data-evento", "")
        if ev == "clique_cta":
            self.ctas += 1
        if tag == "a" and re.search(r"wa\.me/|api\.whatsapp\.com|whatsapp://", a.get("href") or ""):
            self.links.append((a.get("href"), ev))
        if tag == "form":
            self.forms.append(ev)


def pedido_do_plano(plano):
    m = re.search(r"(?mi)^pixel pedido:\s*(.+)$", pathlib.Path(plano).read_text(encoding="utf-8-sig"))
    if not m:
        return None
    v = m.group(1).lower()
    if re.search(r"nenhum|n[aã]o", v):
        return set()
    return {f for f in ("meta", "ga4") if f in v}


def checar(dist, pedido):
    erros, avisos = [], []
    paginas = sorted(pathlib.Path(dist).rglob("*.html"))
    if not paginas:
        return [f"nenhum HTML em {dist}"], avisos
    for p in paginas:
        t = p.read_text(encoding="utf-8", errors="replace")
        nome = p.relative_to(dist).as_posix()
        if "window.RASTREIO" not in t:
            erros.append(f"{nome}: falta o bloco window.RASTREIO (references/rastreamento.md)")
        else:
            cfg = re.search(r"window\.RASTREIO\s*=\s*\{([^}]*)\}", t)
            if cfg:
                for chave, ferramenta in (("metaPixel", "meta"), ("ga4", "ga4")):
                    if ferramenta in pedido and re.search(rf'{chave}\s*:\s*["\']\s*["\']', cfg.group(1)):
                        avisos.append(f"{nome}: {chave} vazio; a página publica e não mede até o aluno preencher")
        if "meta" in pedido and not ("fbq(" in t and "connect.facebook.net" in t):
            erros.append(f"{nome}: Meta Pixel pedido e o carregador (connect.facebook.net + fbq) não está na página")
        if "ga4" in pedido and not ("gtag(" in t and "googletagmanager.com/gtag/js" in t):
            erros.append(f"{nome}: GA4 pedido e o carregador (googletagmanager.com/gtag/js + gtag) não está na página")
        if "data-evento" not in t or not re.search(r"closest\(\s*['\"]\[data-evento\]", t):
            erros.append(f"{nome}: falta o ouvinte de cliques em [data-evento]")
        for ev in ("rolagem_50", "rolagem_90"):
            if ev not in t:
                erros.append(f"{nome}: falta o marco de rolagem {ev}")
        el = Elementos()
        el.feed(t)
        for href, ev in el.links:
            if ev != "clique_whatsapp":
                erros.append(f"{nome}: link de WhatsApp sem data-evento=\"clique_whatsapp\" ({href[:50]})")
        if el.ctas == 0:
            erros.append(f"{nome}: nenhum botão principal com data-evento=\"clique_cta\"")
        for ev in el.forms:
            if ev != "envio_formulario":
                erros.append(f"{nome}: formulário sem data-evento=\"envio_formulario\"")
    return erros, avisos


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dist", required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plano")
    g.add_argument("--pedido")
    a = ap.parse_args()
    if a.plano:
        pedido = pedido_do_plano(a.plano)
        if pedido is None:
            print("REPROVA: o PLANO.md não tem a linha 'Pixel pedido:' (rode o gate-plano.py)")
            return 1
    else:
        v = a.pedido.lower()
        pedido = set() if v in ("nenhum", "nao", "não") else {f.strip() for f in v.split(",") if f.strip()}
    if not pedido:
        print("PASSA: o plano não pediu rastreamento; nada a conferir.")
        return 0
    erros, avisos = checar(a.dist, pedido)
    for av in avisos:
        print(f"AVISO: {av}")
    if erros:
        print(f"REPROVA: {len(erros)} problema(s) de rastreamento ({', '.join(sorted(pedido))})")
        for e in erros:
            print(f"  - {e}")
        return 1
    print(f"PASSA: {', '.join(sorted(pedido))} e os 5 eventos ligados na dist/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
