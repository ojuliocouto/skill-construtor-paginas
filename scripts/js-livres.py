# -*- coding: utf-8 -*-
"""Identificadores livres de um trecho de JavaScript, por varredura (sem parser).

Serve ao `test-receitas.py` (achado A12): o trecho de JS de uma receita não pode usar nome que ele
próprio não define, nem que o "contexto" (a base mínima de `receitas-de-movimento.md`) não defina.
No teste, a receita `assinatura-em-tres-estados` chamava `colunas.rolagem` sem criar `colunas`.

Como funciona: troca comentário, string, template e regex por marcas; junta o que o trecho declara
(`var/let/const`, funções, parâmetros, `catch`, setas); lista o resto dos nomes que não são
propriedade (`a.b`), chave de objeto (`{ b: 1 }`), palavra reservada nem global do navegador.
Não é um parser: serve para este repertório, de trechos curtos e sem módulos nem classes.
"""
import re
PALAVRAS = set("""break case catch class const continue debugger default delete do else export extends finally for function
if import in instanceof let new return super switch this throw try typeof var void while with yield async await of true false null undefined NaN Infinity arguments""".split())
GLOBAIS = set("""window document location history navigator console Math JSON Array Object String Number Boolean Date RegExp Error Promise Set Map
parseFloat parseInt isNaN isFinite setTimeout clearTimeout setInterval clearInterval requestAnimationFrame cancelAnimationFrame
IntersectionObserver ResizeObserver MutationObserver getComputedStyle matchMedia performance Element Node Event CustomEvent
HTMLElement SVGElement CSS fetch URL decodeURIComponent encodeURIComponent""".split())

def limpa(src):
    """Troca comentários, strings, templates e regex literais por espaços/marcas, mantendo o resto."""
    out, i, n, ult = [], 0, len(src), ""
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i); j = n if j < 0 else j
            out.append(" " * (j - i)); i = j; continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2); j = n if j < 0 else j + 2
            out.append(" " * (j - i)); i = j; continue
        if c in "'\"`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            out.append('""'); i = j + 1; ult = '"'; continue
        if c == "/" and (ult in "(=,:!&|?{};[" or ult == "" or re.search(r"(?:return|typeof)$", "".join(out).rstrip())):
            j = i + 1; cls = False
            while j < n and (src[j] != "/" or cls):
                if src[j] == "\\": j += 1
                elif src[j] == "[": cls = True
                elif src[j] == "]": cls = False
                j += 1
            j += 1
            while j < n and src[j].isalpha(): j += 1
            out.append("0"); i = j; ult = "0"; continue
        out.append(c)
        if not c.isspace(): ult = c
        i += 1
    return "".join(out)

ID = r"[A-Za-z_$][\w$]*"
def declarados(s):
    d = set()
    for m in re.finditer(r"\bfunction\s*(%s)?\s*\(([^)]*)\)" % ID, s):
        if m.group(1): d.add(m.group(1))
        d.update(re.findall(ID, m.group(2)))
    for m in re.finditer(r"\bcatch\s*\(\s*(%s)\s*\)" % ID, s): d.add(m.group(1))
    for m in re.finditer(r"\(([^()]*)\)\s*=>", s): d.update(re.findall(ID, m.group(1)))
    for m in re.finditer(r"(?<![\w$.])(%s)\s*=>" % ID, s): d.add(m.group(1))
    for m in re.finditer(r"\b(?:var|let|const)\b", s):
        i, prof = m.end(), 0
        while i < len(s):
            ch = s[i]
            if ch in "([{": prof += 1
            elif ch in ")]}":
                if prof == 0: break
                prof -= 1
            elif ch == ";" and prof == 0: break
            elif ch == "\n" and prof == 0 and not re.search(r"[,=+\-*/?:&|]\s*$", s[m.end():i]) : break
            i += 1
        trecho = s[m.end():i]
        prof = 0; ini = 0; partes = []
        for k, ch in enumerate(trecho):
            if ch in "([{": prof += 1
            elif ch in ")]}": prof -= 1
            elif ch == "," and prof == 0: partes.append(trecho[ini:k]); ini = k + 1
        partes.append(trecho[ini:])
        for p in partes:
            mm = re.match(r"\s*(%s)" % ID, p)
            if mm: d.add(mm.group(1))
    return d

def usados(s):
    achados = {}
    for m in re.finditer(ID, s):
        a, b = m.start(), m.end()
        if a > 0 and (s[a - 1].isdigit() or s[a - 1] in ".$_"): continue   # 1e9, .5s
        antes = s[:a].rstrip()
        if antes.endswith(".") and not antes.endswith(".."): continue   # propriedade
        depois = s[b:].lstrip()
        if depois.startswith(":") and (antes.endswith("{") or antes.endswith(",")): continue  # chave de objeto
        achados.setdefault(m.group(0), a)
    return achados

def livres(js, contexto=()):
    s = limpa(js)
    d = declarados(s) | set(contexto)
    return sorted(k for k in usados(s) if k not in d and k not in PALAVRAS and k not in GLOBAIS)
