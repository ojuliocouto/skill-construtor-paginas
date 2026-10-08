#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera o `secoes.json` da prova de animação (anim.mjs) a partir da tabela "Composição por seção" do PLANO.md.

Por que existe (achado A23, teste de ponta a ponta de 08/10/2026): o plano diz que a tabela de composição "vira" o
`secoes.json`, mas nada o gerava; o aluno escreveu 9 entradas à mão e as ajustou por tentativa.

Uso:
    node <dir-da-skill>/scripts/py.mjs plano-para-secoes.py --projeto <dir> [--html index.html] [--saida plano/secoes.json]

O que ele infere (e o que NÃO infere):
  - nome        `NN-<titulo em minúsculas, sem acento>` na ordem da tabela
  - titulo      a coluna Seção
  - tipo        o que vem antes dos dois pontos da coluna Animação (`assinatura-em-tres-estados` vira `assinatura`)
  - modo        `heroi` para `abertura-do-topo`; `rolagem` para a assinatura quando o texto fala em estado 2 ou rolagem;
                senão o padrão (`entrada`) e o campo nem aparece
  - clique      `<seletor> summary` para `pergunta-que-abre` (a FAQ abre no clique)
  - seletor     SÓ se você der o `--html` e ele tiver o mesmo número de `<section>` que a tabela: `#id` da seção, ou a
                primeira classe quando não há id. Sem isso, o campo sai `PREENCHER: seletor da seção` e o `anim.mjs`
                recusa o arquivo até você trocar. Nunca adivinha seletor.
  - rolarHorizontal  NÃO infere (precisa do seletor do carrossel): quando o Celular fala em carrossel, avisa.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", sem_acento(s).lower()).strip("-")


def linhas_da_tabela(plano):
    m = re.search(r"(?mi)^#{2,4}\s*Composi[cç][aã]o por se[cç][aã]o\s*$", plano)
    if not m:
        raise ValueError("o PLANO.md não tem a tabela 'Composição por seção' (### Composição por seção, com Seção | Desktop | Celular | Animação)")
    linhas = []
    for l in plano[m.end():].splitlines():
        if not l.strip():
            if linhas:
                break
            continue
        if not l.strip().startswith("|"):
            if linhas:
                break
            continue
        cel = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cel) < 4 or set(cel[0]) <= set("-: ") or sem_acento(cel[0]).lower() == "secao":
            continue
        linhas.append(cel[:4])
    if not linhas:
        raise ValueError("a tabela 'Composição por seção' está vazia")
    return linhas


def seletores_do_html(html):
    """Seletor de cada <section> na ordem: #id, ou .primeira-classe."""
    out = []
    for m in re.finditer(r"<section\b([^>]*)>", html or "", re.I):
        attrs = m.group(1)
        i = re.search(r'\bid="([^"]+)"', attrs)
        c = re.search(r'\bclass="([^"]+)"', attrs)
        if i:
            out.append("#" + i.group(1))
        elif c and c.group(1).split():
            out.append("." + c.group(1).split()[0])
        else:
            out.append(None)
    return out


def gerar(plano, html=None):
    """Devolve (lista de seções, avisos)."""
    linhas = linhas_da_tabela(plano)
    avisos = []
    seletores = seletores_do_html(html) if html else []
    casa = bool(html) and len(seletores) == len(linhas) and all(seletores)
    if html and not casa:
        avisos.append(f"o HTML tem {len(seletores)} <section> (ou algum sem id nem classe) e a tabela tem {len(linhas)} linhas: "
                      "não são o mesmo número, então não adivinhei os seletores; preencha cada PREENCHER")
    if not html:
        avisos.append("sem --html, os seletores ficam PREENCHER: dê o --html para eu casar as seções pela ordem")
    lista = []
    for n, (secao, _desk, cel, anim) in enumerate(linhas, 1):
        tipo = sem_acento(anim.split(":", 1)[0]).strip().lower().replace(" ", "-")
        texto = sem_acento(anim).lower()
        if tipo.startswith("assinatura"):
            tipo = "assinatura"
        item = {"nome": f"{n:02d}-{slug(secao)}", "seletor": seletores[n - 1] if casa else "PREENCHER: seletor da seção",
                "titulo": secao, "tipo": tipo}
        if tipo == "abertura-do-topo":
            item["modo"] = "heroi"
        elif tipo == "assinatura" and re.search(r"estado 2|rolagem", texto):
            item["modo"] = "rolagem"
        if tipo == "pergunta-que-abre":
            base = item["seletor"]
            item["clique"] = (base + " summary") if not base.startswith("PREENCHER") else "PREENCHER: seletor do que se clica (summary)"
        if re.search(r"carross", sem_acento(cel).lower()):
            avisos.append(f"'{secao}' tem carrossel no celular: acrescente `rolarHorizontal` com o seletor dele no JSON "
                          "(o anim.mjs rola 330 px de lado antes do último quadro)")
        lista.append(item)
    return lista, avisos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projeto", type=Path, required=True)
    ap.add_argument("--html", default=None, help="página para casar as seções pela ordem (ex.: index.html)")
    ap.add_argument("--saida", type=Path, default=None, help="padrão: <projeto>/plano/secoes.json")
    a = ap.parse_args(argv)
    raiz = a.projeto.resolve()
    try:
        plano = (raiz / "PLANO.md").read_text(encoding="utf-8-sig")
        html = (raiz / a.html).read_text(encoding="utf-8-sig") if a.html else None
        lista, avisos = gerar(plano, html)
    except (OSError, ValueError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    saida = a.saida or (raiz / "plano" / "secoes.json")
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(lista, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"gerei {len(lista)} seções em {saida.as_posix()}")
    pend = sum(1 for s in lista for v in s.values() if isinstance(v, str) and v.startswith("PREENCHER"))
    for av in avisos:
        print("  AVISO: " + av)
    if pend:
        print(f"  {pend} campo(s) PREENCHER para você trocar antes de rodar o anim.mjs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
