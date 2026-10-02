#!/usr/bin/env python3
"""Regenera references/index.yaml (seção do SKILL.md -> linha) a partir dos títulos.

O índice antigo era escrito à mão, parava no meio (\"consultar_banco_design: 1240\", sem
quebra de linha) e envelhecia a cada edição. Rode depois de mexer no SKILL.md:

    python3 <dir-da-skill>/scripts/gerar-index.py
"""
import pathlib
import re
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def chave(titulo):
    t = "".join(c for c in unicodedata.normalize("NFD", titulo) if unicodedata.category(c) != "Mn").lower()
    palavras = re.findall(r"[a-z0-9]+", t)[:6]
    return "_".join(palavras) or "secao"


def gerar():
    linhas = (RAIZ / "SKILL.md").read_text(encoding="utf-8").splitlines()
    saida, vistas, dentro = [], {}, False
    for n, linha in enumerate(linhas, 1):
        if linha.lstrip().startswith("```"):
            dentro = not dentro
            continue
        m = re.match(r"(#{2,3}) (.+)", linha)
        if dentro or not m:
            continue
        k = chave(m.group(2))
        vistas[k] = vistas.get(k, 0) + 1
        if vistas[k] > 1:
            k = f"{k}_{vistas[k]}"
        saida.append(f"  {k}: {n}")
    texto = ("# Mapeamento seção -> linha do SKILL.md\n"
             "# Gerado por scripts/gerar-index.py; não editar à mão.\n\nsections:\n" + "\n".join(saida) + "\n")
    (RAIZ / "references" / "index.yaml").write_text(texto, encoding="utf-8")
    return len(saida)


if __name__ == "__main__":
    print(f"{gerar()} seções em references/index.yaml")
