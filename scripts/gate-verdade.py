#!/usr/bin/env python3
"""Gate de verdade: toda promessa da página tem uma linha do briefing que a sustenta.

Por que existe (02/10/2026, auditoria da v3, achado ALTO). A página dizia "Você chega, faz a
avaliação postural e começa" e a meta description dizia "Aula experimental gratuita, com
avaliação postural", quando o briefing deixava em aberto se a avaliação é gratuita e se é no
mesmo dia. O copy.md do construtor afirmava "texto não afirma o mesmo dia, só a ordem". Era o
crítico da v1 voltando, e a autoavaliação aprovou. Afirmação sem fonte não se pega lendo a
própria copy: pega-se cruzando cada frase com a linha da fonte.

Entradas (no projeto):
  index.html                 a página (texto visível, title, meta description, og:*, alt)
  evidencias/briefing.md     a fonte dos fatos
  evidencias/sustentacao.md  produzida no passo d (copy):
      | Frase da página | Linha do briefing que sustenta |
      |---|---|
      | A aula experimental é gratuita. | "Oferta: aula experimental gratuita" |
      | Você se reconhece? | interpretação: público do briefing |
      ## Não afirmar (pendências)
      - Avaliação grátis ou no mesmo dia: `gratuit\\w*[^.]{0,80}avalia|mesmo dia`

Reprova (exit 1) se:
  1. frase com marca de promessa (grátis, gratuita, garantia, número, preço, prazo, resultado,
     desconto, vaga, credencial) não tem linha na tabela;
  2. title, meta description, og:title ou og:description têm frase fora da tabela (a prévia
     do link no WhatsApp também promete);
  3. a linha citada não está no briefing, ou está numa frase do briefing marcada PENDENTE;
  4. promessa sustentada só por "interpretação";
  5. alguma frase da página casa um padrão de "Não afirmar";
  6. o briefing tem mais frases PENDENTE do que padrões em "Não afirmar" (cada pendência
     precisa dizer o que a página não pode insinuar).

Uso: python3 scripts/gate-verdade.py --projeto <dir> [--html index.html]
"""
import argparse
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

PROMESSA = re.compile(
    r"gr[aá]tis|gratuit|garant|sem custo|sem compromisso|mesmo dia|na hora|imediat|resultado|r\$|\d|"
    r"desconto|vaga|[uú]ltim|s[oó] hoje|certificad|crefito|registro no conselho|reembolso", re.I)
BLOCOS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "dt", "dd", "summary", "figcaption", "a", "button",
          "td", "th", "div", "section", "label", "header", "footer", "main", "article", "figure", "ul", "ol",
          "dl", "details", "blockquote", "span", "strong"}
VAZIOS = {"img", "br", "meta", "link", "input", "source", "hr", "wbr", "area", "base", "col", "embed", "track"}
OCULTOS = {"script", "style", "noscript", "template", "svg"}


def norm(t):
    t = unicodedata.normalize("NFC", t or "").lower()
    t = re.sub(r"[*_`\"“”'’«»]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.strip(" .!?;:,")


def frases(texto):
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", texto or "").strip()) if f.strip()]


class Leitor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.blocos, self.buf, self.metas, self.alts = [], [], [], {}, []
        self.titulo, self._no_title = "", False

    def _oculto(self):
        return any(o for _, o in self.pilha)

    def _descarrega(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if t:
            self.blocos.append(t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            chave = (a.get("name") or a.get("property") or "").lower()
            if chave in ("description", "og:title", "og:description", "twitter:description"):
                self.metas[chave] = a.get("content") or ""
            return
        if tag == "img" and a.get("alt") and not self._oculto():
            self.alts.append(a["alt"])
        if tag in VAZIOS:
            return
        if tag == "title":
            self._no_title = True
        oculto = tag in OCULTOS or "hidden" in a or a.get("aria-hidden") == "true"
        if tag in BLOCOS:
            self._descarrega()
        self.pilha.append((tag, oculto))

    def handle_endtag(self, tag):
        if tag == "title":
            self._no_title = False
        if tag in VAZIOS:
            return
        if tag in BLOCOS:
            self._descarrega()
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self._no_title:
            self.titulo += data
            return
        if not self._oculto():
            self.buf.append(data)


def ler_tabela(texto):
    linhas = []
    for l in texto.splitlines():
        if not l.strip().startswith("|"):
            continue
        # "\|" é a barra escapada do Markdown (o title costuma ter "Marca | Assunto").
        cel = [c.strip().replace("\x00", "|") for c in l.strip().replace("\\|", "\x00").strip("|").split("|")]
        if len(cel) < 2 or set(cel[0]) <= set("-: ") or norm(cel[0]).startswith("frase da p"):
            continue
        linhas.append((cel[0], cel[1]))
    return linhas


def ler_padroes(texto):
    i = texto.lower().find("## não afirmar")
    if i < 0:
        i = texto.lower().find("## nao afirmar")
    if i < 0:
        return []
    fim = texto.find("\n## ", i + 3)
    bloco = texto[i:] if fim < 0 else texto[i:fim]
    return re.findall(r"`([^`]+)`", bloco)


def sentencas_do_briefing(texto):
    out = []
    for linha in texto.splitlines():
        out.extend(f for f in re.split(r"(?<=[.;])\s+", linha) if f.strip())
    return out


def checar(projeto, html_nome="index.html"):
    r = Path(projeto)
    problemas = []
    faltam = [n for n in (html_nome, "evidencias/briefing.md", "evidencias/sustentacao.md") if not (r / n).is_file()]
    if faltam:
        return [f"arquivo ausente: {n}" for n in faltam]
    briefing = (r / "evidencias" / "briefing.md").read_text(encoding="utf-8")
    sust = (r / "evidencias" / "sustentacao.md").read_text(encoding="utf-8")
    tabela = ler_tabela(sust)
    padroes = ler_padroes(sust)
    if not tabela:
        return ["evidencias/sustentacao.md sem a tabela 'Frase da página | Linha do briefing que sustenta'"]

    leitor = Leitor()
    leitor.feed((r / html_nome).read_text(encoding="utf-8"))
    leitor._descarrega()
    visiveis = [f for b in leitor.blocos for f in frases(b)] + [f for a in leitor.alts for f in frases(a)]
    metas = [("title", f) for f in frases(leitor.titulo)] + [(k, f) for k, v in leitor.metas.items() for f in frases(v)]

    def linha_da(frase):
        n = norm(frase)
        for fr, s in tabela:
            nf = norm(fr)
            if nf and (nf == n or (len(nf) >= 12 and nf in n) or (len(n) >= 12 and n in nf)):
                return fr, s
        return None

    sent_brief = sentencas_do_briefing(briefing)
    nb = [norm(s) for s in sent_brief]
    vistos = set()
    for origem, frase in [("texto", f) for f in visiveis] + metas:
        chave = (origem if origem != "texto" else "", norm(frase))
        if chave in vistos:
            continue
        vistos.add(chave)
        promessa = bool(PROMESSA.search(frase))
        par = linha_da(frase)
        if origem != "texto" and not par:
            problemas.append(f"{origem}: \"{frase}\" sem linha de sustentação na tabela (a prévia do link também promete)")
            continue
        if promessa and not par:
            problemas.append(f"promessa sem linha de sustentação: \"{frase}\"")
            continue
        if par and promessa:
            fonte = par[1]
            if norm(fonte).startswith(("interpreta", "suposi", "estrutura")):
                problemas.append(f"interpretação não sustenta promessa: \"{frase}\" -> {fonte}")
                continue
            citada = re.findall(r"[\"“]([^\"”]+)[\"”]", fonte) or [fonte]
            for c in citada:
                nc = norm(c)
                onde = [s for s, n in zip(sent_brief, nb) if nc and nc in n]
                if not onde:
                    problemas.append(f"linha citada não está no briefing: \"{c}\" (para \"{frase}\")")
                elif all("PENDENTE" in s.upper() for s in onde):
                    problemas.append(f"linha citada é PENDENTE no briefing: \"{onde[0].strip()}\" (para \"{frase}\")")

    for p in padroes:
        try:
            rx = re.compile(p, re.I)
        except re.error as e:
            problemas.append(f"padrão inválido em Não afirmar: `{p}` ({e})")
            continue
        for origem, frase in [("texto", f) for f in visiveis] + metas:
            if rx.search(frase):
                problemas.append(f"afirma o que está pendente (`{p}`) em {origem}: \"{frase}\"")

    pendentes = [s for s in sent_brief if "PENDENTE" in s.upper()]
    if len(padroes) < len(pendentes):
        problemas.append(f"o briefing tem {len(pendentes)} frase(s) PENDENTE e 'Não afirmar' tem {len(padroes)} "
                         "padrão(ões): cada pendência precisa dizer o que a página não pode insinuar")
    return problemas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", required=True)
    ap.add_argument("--html", default="index.html")
    a = ap.parse_args(argv)
    problemas = checar(a.projeto, a.html)
    print(f"\nGATE DE VERDADE (frase da página -> linha do briefing)  {a.projeto}\n" + "=" * 76)
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        print(f"\n  REPROVA: {len(problemas)} frase(s) sem sustentação ou afirmando pendência. Corrija a copy")
        print("  (e a meta description) ou peça o fato à cliente; nunca a tabela para caber na página.\n")
        return 1
    print("  PASSA: toda promessa tem linha no briefing e nenhuma frase insinua pendência.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
