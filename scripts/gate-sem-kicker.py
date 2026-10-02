#!/usr/bin/env python3
"""Gate: página do Júlio/EA não leva supratítulo (kicker) em caixa alta abrindo seção.

Correção repetida dele (31/08/2026 e 01/10/2026, "dá uma puta cara de IA"). Roda ANTES de
qualquer deploy de página: `python3 ~/.claude/scripts/gate-sem-kicker.py <arquivo.html|dist/>`.
Sai com código 1 se achar:
  1. regra CSS com text-transform: uppercase E letter-spacing >= 0.1em (a receita do kicker);
  2. elemento <p>/<span>/<div> curto (<= 60 chars) imediatamente antes de <h1>/<h2>/<h3>,
     com classe que casa com label|kicker|eyebrow|overline|supra|tag.
Falso positivo conhecido: rótulo DENTRO de card ("Encontro 01") é permitido; o gate só olha
o que vem logo antes de um título.
"""
import re
import sys
from pathlib import Path

CSS_RULE = re.compile(r'([^{}]+)\{([^{}]*text-transform\s*:\s*uppercase[^{}]*)\}', re.I | re.S)
LS = re.compile(r'letter-spacing\s*:\s*([0-9.]+)\s*(em|px)', re.I)
KICKER_ANTES_DE_TITULO = re.compile(
    r'<(p|span|div)\b[^>]*class="[^"]*\b(label|kicker|eyebrow|overline|supra|tag)\b[^"]*"[^>]*>([^<]{1,60})</\1>\s*<h[123]\b',
    re.I | re.S)


def checar(html: str, nome: str) -> list[str]:
    achados = []
    for sel, corpo in CSS_RULE.findall(html):
        m = LS.search(corpo)
        if not m:
            continue
        val, un = float(m.group(1)), m.group(2).lower()
        if (un == 'em' and val >= 0.1) or (un == 'px' and val >= 1.5):
            achados.append(f'{nome}: CSS "{sel.strip()[:60]}" é receita de kicker (uppercase + letter-spacing {val}{un})')
    for m in KICKER_ANTES_DE_TITULO.finditer(html):
        achados.append(f'{nome}: "{m.group(3).strip()}" (classe {m.group(2)}) abre seção antes de um título')
    return achados


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    alvo = Path(sys.argv[1]).expanduser()
    arquivos = [alvo] if alvo.is_file() else sorted(alvo.rglob('*.html'))
    if not arquivos:
        print(f'nenhum .html em {alvo}')
        return 2
    achados = []
    for f in arquivos:
        achados += checar(f.read_text(encoding='utf-8', errors='replace'), str(f))
    if achados:
        print('REPROVADO (kicker em caixa alta, correção repetida do Júlio):')
        for a in achados:
            print('  -', a)
        return 1
    print(f'ok: {len(arquivos)} arquivo(s) sem kicker')
    return 0


if __name__ == '__main__':
    sys.exit(main())
