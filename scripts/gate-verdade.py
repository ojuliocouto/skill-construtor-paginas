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
     precisa dizer o que a página não pode insinuar);
  7. (auditoria da v5, 03/10/2026) o briefing nomeia quem é o dono ou a profissional do
     negócio (linha "Dono:", "Dona do negócio:", "Responsável:", "Profissional citada no
     briefing:" ou "Fundadora:") e o nome só aparece no rodapé, ou em lugar nenhum: quem cuida
     é argumento de venda de serviço e vai no corpo da página. A v5 citava a fisioterapeuta
     Carla Mendes só no rodapé.

Desde a 3.5.6 (achados do teste de ponta a ponta, 08/10/2026):
  - sem index.html (passo d, a copy), o gate confere só a tabela contra o briefing e avisa que a
    página ainda não existe; o gate de verdade roda de novo no passo f, com a página;
  - a citação é comparada com o texto do briefing inteiro, espaços e quebras de linha colapsados:
    atravessar ponto, ponto e vírgula ou quebra de linha não a derruba, mas citação que não está
    no briefing continua reprovando;
  - crédito de imagem não é promessa: texto dentro de um bloco marcado como crédito
    (`data-credito`, `id="creditos"` ou classe `creditos`/`credito`) e linha que seja só o
    identificador de uma licença (`CC0 1.0`, `CC BY 2.0`, `CC BY-SA 4.0`) ficam de fora;
  - quando falta linha, a saída imprime a linha pronta pra colar, agrupada por seção da página;
  - aviso (não reprova) quando a tabela da seção d do PLANO.md e a sustentacao.md divergem.

Uso: node scripts/py.mjs gate-verdade.py --projeto <dir> [--html index.html]
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


# Rótulo curto: só número e unidade ("5 anos", "30 dias", "1 ano").
ROTULO = re.compile(r"\d+(?:[.,]\d+)?\s+[a-zçãõáéíóúâêô]+")


def e_credito(attrs):
    """O elemento é um bloco de crédito de imagem: `data-credito`, id ou classe `creditos`/`credito`."""
    if "data-credito" in attrs:
        return True
    if (attrs.get("id") or "").lower() in ("credito", "creditos", "creditos-de-imagem"):
        return True
    return any(re.fullmatch(r"cr[eé]ditos?(?:-[\w-]+)?", c.lower()) for c in (attrs.get("class") or "").split())


# Linha que é só o identificador de uma licença (nada além dele): não promete nada.
SO_LICENCA = re.compile(r"cc(?:0|[ -]by(?:[ -](?:sa|nc|nd))*)\s*\d(?:\.\d)?", re.I)


class Leitor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pilha, self.blocos, self.buf, self.metas, self.alts = [], [], [], {}, []
        self.titulo, self._no_title = "", False
        self.secao, self.secoes = "", []

    def _oculto(self):
        return any(o for _, o, _c in self.pilha)

    def _credito(self):
        return any(c for _, _o, c in self.pilha)

    def _descarrega(self):
        t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        if t:
            self.blocos.append(t)
            self.secoes.append(self.secao)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            chave = (a.get("name") or a.get("property") or "").lower()
            if chave in ("description", "og:title", "og:description", "twitter:description"):
                self.metas[chave] = a.get("content") or ""
            return
        if tag == "img" and a.get("alt") and not self._oculto() and not self._credito():
            self.alts.append(a["alt"])
        if tag in VAZIOS:
            return
        if tag == "title":
            self._no_title = True
        oculto = tag in OCULTOS or "hidden" in a or a.get("aria-hidden") == "true"
        if tag in BLOCOS:
            self._descarrega()
        self.pilha.append((tag, oculto, e_credito(a)))

    def handle_endtag(self, tag):
        if tag == "title":
            self._no_title = False
        if tag in VAZIOS:
            return
        if tag in BLOCOS:
            self._descarrega()
        if re.fullmatch(r"h[1-4]", tag) and self.blocos and not self._credito():
            self.secao = self.blocos[-1]
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                del self.pilha[i:]
                break

    def handle_data(self, data):
        if self._no_title:
            self.titulo += data
            return
        if not self._oculto() and not self._credito():
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


def limpa(t):
    """Como `norm`, mas sem aparar as pontas: serve para montar o texto inteiro do briefing."""
    t = unicodedata.normalize("NFC", t or "").lower()
    return re.sub(r"\s+", " ", re.sub(r"[*_`\"“”'’«»]", "", t))


def briefing_corrido(sentencas):
    """Texto do briefing inteiro (espaços e quebras colapsados) e o intervalo de cada sentença nele."""
    partes, intervalos, pos = [], [], 0
    for s in sentencas:
        c = limpa(s).strip()
        if not c:
            continue
        if partes:
            pos += 1
        intervalos.append((pos, pos + len(c), s))
        partes.append(c)
        pos += len(c)
    return " ".join(partes), intervalos


def onde_no_briefing(citacao, corrido, intervalos):
    """Uma lista por ocorrência da citação no briefing, com as sentenças que ela toca ([] se não está)."""
    nc = norm(citacao)
    if not nc:
        return []
    grupos, ini = [], corrido.find(nc)
    while ini >= 0:
        fim = ini + len(nc)
        grupos.append([s for a, b, s in intervalos if a < fim and b > ini])
        ini = corrido.find(nc, ini + 1)
    return grupos


def checa_citacao(c, frase, corrido, intervalos, problemas):
    grupos = onde_no_briefing(c, corrido, intervalos)
    if not grupos:
        problemas.append(f"linha citada não está no briefing: \"{c}\" (para \"{frase}\")")
    elif all(any("PENDENTE" in s.upper() for s in g) for g in grupos):
        pend = next(s for s in grupos[0] if "PENDENTE" in s.upper())
        problemas.append(f"linha citada é PENDENTE no briefing: \"{pend.strip()}\" (para \"{frase}\")")


def tabela_do_plano(texto):
    """Linhas `| Seção | Frase | Linha ... |` da seção d do PLANO.md: lista de (seção, frase)."""
    out = []
    for l in texto.splitlines():
        if not l.strip().startswith("|"):
            continue
        cel = [c.strip() for c in l.strip().replace("\\|", "\x00").strip("|").split("|")]
        if len(cel) < 3 or set(cel[0]) <= set("-: ") or norm(cel[0]) == "seção" or norm(cel[0]) == "secao":
            continue
        out.append((cel[0], cel[1].replace("\x00", "|")))
    return out


def avisos_plano_x_sustentacao(r, tabela):
    """Aviso (não reprova): a tabela do PLANO e a sustentacao.md se afastam ao longo da construção."""
    plano = r / "PLANO.md"
    if not plano.is_file():
        return []
    doc = plano.read_text(encoding="utf-8-sig")
    k = re.search(r"(?im)^##\s*d\.", doc)
    if not k:
        return []
    fim = re.search(r"(?m)^##\s", doc[k.end():])
    linhas = tabela_do_plano(doc[k.start(): k.end() + fim.start()] if fim else doc[k.start():])
    if not linhas:
        return []
    no_plano = {norm(f) for _, f in linhas}
    na_sust = {norm(f) for f, _ in tabela}
    so_sust = [f for f, _ in tabela if norm(f) not in no_plano]
    so_plano = [f for _, f in linhas if norm(f) not in na_sust]
    avisos = []
    if so_sust:
        avisos.append(f"{len(so_sust)} linha(s) da sustentacao.md não estão na tabela da seção d do PLANO "
                      f"(copy final, FAQ e rótulos entram na sustentacao.md; atualize o PLANO se a copy mudou), "
                      f"ex.: \"{so_sust[0]}\"")
    if so_plano:
        avisos.append(f"{len(so_plano)} frase(s) da tabela do PLANO não estão na sustentacao.md (a copy mudou "
                      f"depois do plano?), ex.: \"{so_plano[0]}\"")
    return avisos


DONO = re.compile(r"(?im)^\s*[-*]?\s*(?:dono|dona|respons[aá]vel|profissional|fundador|fundadora|propriet[aá]ri[ao])"
                  r"[^:\n]{0,40}:\s*([A-ZÀ-Ý][\wÀ-ÿ']+(?:\s+(?:d[aeo]s?\s+)?[A-ZÀ-Ý][\wÀ-ÿ']+)+)")


def texto_do_corpo(pagina):
    """Texto visível fora do <head>, do <footer> e do que não é texto (script, style, svg)."""
    t = re.sub(r"(?is)<(head|footer|script|style|svg|noscript|template)\b.*?</\1>", " ", pagina)
    t = re.sub(r"(?is)<[^>]*\bhidden\b[^>]*>.*?</(section|div|p)>", " ", t)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t))


def conferir_tabela(tabela, corrido, intervalos, problemas):
    """Cada linha da tabela: promessa não se apoia em interpretação e a citação está no briefing."""
    for frase, fonte in tabela:
        if not PROMESSA.search(frase):
            continue
        if norm(fonte).startswith(("interpreta", "suposi", "estrutura")):
            problemas.append(f"interpretação não sustenta promessa: \"{frase}\" -> {fonte}")
            continue
        for c in re.findall(r"[\"“]([^\"”]+)[\"”]", fonte) or [fonte]:
            checa_citacao(c, frase, corrido, intervalos, problemas)


def linha_pronta(frase):
    return '| "' + frase.replace("|", "\\|") + '" | <linha do briefing entre aspas> |'


def checar(projeto, html_nome="index.html", relatorio=None):
    """Devolve a lista de problemas. `relatorio` (dict) recebe `modo`, `avisos` e `prontas`."""
    r = Path(projeto)
    rel = relatorio if relatorio is not None else {}
    rel.update(modo="pagina", avisos=[], prontas=[])
    problemas = []
    sem_pagina = not (r / html_nome).is_file()
    faltam = [n for n in ("evidencias/briefing.md", "evidencias/sustentacao.md") if not (r / n).is_file()]
    if faltam:
        return [f"arquivo ausente: {n}" for n in faltam] + ([f"arquivo ausente: {html_nome}"] if sem_pagina else [])
    briefing = (r / "evidencias" / "briefing.md").read_text(encoding="utf-8-sig")
    sust = (r / "evidencias" / "sustentacao.md").read_text(encoding="utf-8-sig")
    tabela = ler_tabela(sust)
    padroes = ler_padroes(sust)
    if not tabela:
        return ["evidencias/sustentacao.md sem a tabela 'Frase da página | Linha do briefing que sustenta'"]
    sent_brief = sentencas_do_briefing(briefing)
    corrido, intervalos = briefing_corrido(sent_brief)
    rel["avisos"] = avisos_plano_x_sustentacao(r, tabela)

    if sem_pagina:
        rel["modo"] = "tabela"
        conferir_tabela(tabela, corrido, intervalos, problemas)
        for p in padroes:
            try:
                rx = re.compile(p, re.I)
            except re.error as e:
                problemas.append(f"padrão inválido em Não afirmar: `{p}` ({e})")
                continue
            for frase, _ in tabela:
                if rx.search(frase):
                    problemas.append(f"afirma o que está pendente (`{p}`) na tabela: \"{frase}\"")
        pendentes = [s for s in sent_brief if "PENDENTE" in s.upper()]
        if len(padroes) < len(pendentes):
            problemas.append(f"o briefing tem {len(pendentes)} frase(s) PENDENTE e 'Não afirmar' tem {len(padroes)} "
                             "padrão(ões): cada pendência precisa dizer o que a página não pode insinuar")
        return problemas

    leitor = Leitor()
    leitor.feed((r / html_nome).read_text(encoding="utf-8-sig"))
    leitor._descarrega()
    visiveis, secao_da = [], {}
    for b, sec in zip(leitor.blocos, leitor.secoes):
        for f in frases(b):
            visiveis.append(f)
            secao_da.setdefault(norm(f), sec)
    visiveis += [f for a in leitor.alts for f in frases(a)]
    metas = [("title", f) for f in frases(leitor.titulo)] + [(k, f) for k, v in leitor.metas.items() for f in frases(v)]

    def linha_da(frase):
        n = norm(frase)
        for fr, s in tabela:
            nf = norm(fr)
            if nf and (nf == n or (len(nf) >= 12 and nf in n) or (len(n) >= 12 and n in nf)):
                return fr, s
        return None

    def falta(frase, origem, msg):
        problemas.append(msg)
        rel["prontas"].append((secao_da.get(norm(frase)) or ("meta da página" if origem != "texto" else "sem seção"),
                               linha_pronta(frase if origem == "texto" else f"{origem}: {frase}")))

    vistos, sustentadas, rotulos = set(), [], []
    for origem, frase in [("texto", f) for f in visiveis] + metas:
        chave = (origem if origem != "texto" else "", norm(frase))
        if chave in vistos:
            continue
        vistos.add(chave)
        promessa = bool(PROMESSA.search(frase)) and not SO_LICENCA.fullmatch(norm(frase).replace("’", ""))
        par = linha_da(frase)
        if origem != "texto" and not par:
            falta(frase, origem, f"{origem}: \"{frase}\" sem linha de sustentação na tabela (a prévia do link também promete)")
            continue
        if promessa and not par:
            if origem == "texto" and ROTULO.fullmatch(norm(frase)):
                rotulos.append(frase)  # decide depois de ver as promessas sustentadas da mesma seção
                continue
            falta(frase, origem, f"promessa sem linha de sustentação: \"{frase}\"")
            continue
        if par and promessa:
            fonte = par[1]
            if norm(fonte).startswith(("interpreta", "suposi", "estrutura")):
                problemas.append(f"interpretação não sustenta promessa: \"{frase}\" -> {fonte}")
                continue
            antes = len(problemas)
            for c in re.findall(r"[\"“]([^\"”]+)[\"”]", fonte) or [fonte]:
                checa_citacao(c, frase, corrido, intervalos, problemas)
            if len(problemas) == antes and origem == "texto":
                sustentadas.append((secao_da.get(norm(frase), ""), norm(frase)))

    # Rótulo curto ("5 anos" numa barra) herda a sustentação de uma promessa JÁ sustentada na MESMA
    # seção que traga o mesmo número com a mesma unidade, palavra inteira. Número diferente, ou
    # a mesma frase em outra seção, continua pedindo a própria linha.
    for rot in rotulos:
        sec = secao_da.get(norm(rot), "")
        nr = norm(rot)
        if any((s == sec or nf == norm(sec)) and re.search(rf"(?<![\w,.]){re.escape(nr)}(?![\w,.])", nf)
               for s, nf in sustentadas if sec):
            continue
        falta(rot, "texto", f"promessa sem linha de sustentação: \"{rot}\"")

    for p in padroes:
        try:
            rx = re.compile(p, re.I)
        except re.error as e:
            problemas.append(f"padrão inválido em Não afirmar: `{p}` ({e})")
            continue
        for origem, frase in [("texto", f) for f in visiveis] + metas:
            if rx.search(frase):
                problemas.append(f"afirma o que está pendente (`{p}`) em {origem}: \"{frase}\"")

    pagina = (r / html_nome).read_text(encoding="utf-8-sig")
    corpo_n = norm(texto_do_corpo(pagina))
    for nome in dict.fromkeys(m.group(1).strip() for m in DONO.finditer(briefing)):
        if norm(nome) not in corpo_n:
            onde = "só no rodapé" if norm(nome) in norm(re.sub(r"<[^>]+>", " ", pagina)) else "em lugar nenhum da página"
            problemas.append(f"o briefing nomeia {nome} e a página o cita {onde}: quem é o dono ou a profissional "
                             "aparece no corpo, com o que o briefing permite dizer (sem inventar credencial)")

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
    rel = {}
    problemas = checar(a.projeto, a.html, rel)
    print(f"\nGATE DE VERDADE (frase da página -> linha do briefing)  {a.projeto}\n" + "=" * 76)
    for av in rel.get("avisos", []):
        print("  AVISO: " + av)
    so_tabela = rel.get("modo") == "tabela"
    if problemas:
        for p in problemas:
            print("  FALHA: " + p)
        if rel.get("prontas"):
            print("\n  Linhas prontas pra colar em evidencias/sustentacao.md (troque o segundo campo pela linha do")
            print("  briefing entre aspas; se o briefing não tem a linha, corte a frase da página ou peça o fato):")
            atual = None
            for sec, linha in rel["prontas"]:
                if sec != atual:
                    print(f"\n  [seção: {sec}]")
                    atual = sec
                print("  " + linha)
        if so_tabela:
            print("\n  página ainda não existe: conferi só a tabela; rode de novo no passo f.")
        print(f"\n  REPROVA: {len(problemas)} frase(s) sem sustentação ou afirmando pendência. Corrija a copy")
        print("  (e a meta description) ou peça o fato à cliente; nunca a tabela para caber na página.\n")
        return 1
    if so_tabela:
        print("  PASSA (só a tabela): toda promessa da tabela tem linha no briefing.")
        print("  página ainda não existe: conferi só a tabela; rode de novo no passo f, com o index.html pronto.\n")
        return 0
    print("  PASSA: toda promessa tem linha no briefing e nenhuma frase insinua pendência.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
