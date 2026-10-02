#!/usr/bin/env python3
"""Gate: toda página sai sem supratítulo (kicker) em caixa alta abrindo seção.

Preferência de gosto medida em correção real e repetida ("dá uma puta cara de IA"). Roda
ANTES de qualquer deploy de página:

    python3 <dir-da-skill>/scripts/gate-sem-kicker.py <arquivo.html|pasta>

Sai com código 1 se achar:
  1. regra CSS com text-transform: uppercase E letter-spacing >= 0.1em (a receita do kicker),
     no <style> da página OU em qualquer .css do projeto (fora de node_modules);
  2. elemento curto (<= 60 caracteres) imediatamente antes de <h1>/<h2>/<h3> que seja kicker:
     - em Tailwind: classe `uppercase` junto com `tracking-*` positivo (tracking-wide, -wider,
       -widest, tracking-[0.2em], tracking-[2px]); vale `class` e `className`;
     - por nome: classe que casa com label|kicker|eyebrow|overline|supra|tag.
Falso positivo conhecido: rótulo DENTRO de card ("Encontro 01") é permitido; o gate só olha
o que vem logo antes de um título.

Por que lê Tailwind e .css externo (relatório do aluno, 02/10/2026): o mutante
`<p class="text-[12px] uppercase tracking-[0.2em]">Para você</p><h2>` passava com "ok",
porque a versão antiga só olhava CSS dentro do HTML e classe com nome de kicker. A skill
manda Tailwind em toda página, então o gate era cego justamente para o caso mais comum.
"""
import re
import sys
from pathlib import Path

CSS_RULE = re.compile(r'([^{}]+)\{([^{}]*text-transform\s*:\s*uppercase[^{}]*)\}', re.I | re.S)
LS = re.compile(r'letter-spacing\s*:\s*(-?[0-9.]+)\s*(em|px|rem)', re.I)
# elemento curto + (comentários/espaço) + título. Grupo "attrs" traz os atributos do elemento.
CURTO_ANTES_DE_TITULO = re.compile(
    r'<(?P<tag>p|span|div|small|strong|em|b)\b(?P<attrs>[^>]*)>(?P<texto>[^<]{1,60})</(?P=tag)>'
    r'(?:\s|<!--.*?-->|\{/\*.*?\*/\})*<h[123]\b',
    re.I | re.S)
CLASSE = re.compile(r'\bclass(?:Name)?\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\{\s*[`"\']([^`"\']*)[`"\']\s*\})', re.I)
NOME_KICKER = re.compile(r'(?:^|[\s_-])(label|kicker|eyebrow|overline|supra|tag)(?:$|[\s_-])', re.I)
TRACKING_ARB = re.compile(r'^tracking-\[(-?[0-9.]+)(em|px|rem)\]$')
TRACKING_POSITIVO = {'tracking-wide', 'tracking-wider', 'tracking-widest'}

EXT_FONTE = ('*.html', '*.htm', '*.jsx', '*.tsx', '*.vue', '*.svelte', '*.astro')
IGNORAR = ('node_modules', '.git')


def _ignorado(p: Path) -> bool:
    return any(parte in IGNORAR for parte in p.parts)


def espacamento_de_kicker(valor: float, unidade: str) -> bool:
    unidade = unidade.lower()
    if unidade in ('em', 'rem'):
        return valor >= 0.1
    return valor >= 1.5


def tracking_positivo(token: str) -> bool:
    base = token.split(':')[-1]  # md:tracking-widest
    if base in TRACKING_POSITIVO:
        return True
    m = TRACKING_ARB.match(base)
    return bool(m) and float(m.group(1)) > 0


def classes(attrs: str) -> list[str]:
    m = CLASSE.search(attrs)
    if not m:
        return []
    return (m.group(1) or m.group(2) or m.group(3) or '').split()


def checar_css(css: str, nome: str) -> list[str]:
    achados = []
    for sel, corpo in CSS_RULE.findall(css):
        m = LS.search(corpo)
        if not m:
            continue
        val, un = float(m.group(1)), m.group(2)
        if espacamento_de_kicker(val, un):
            achados.append(f'{nome}: CSS "{sel.strip()[:60]}" é receita de kicker '
                           f'(uppercase + letter-spacing {val}{un.lower()})')
    return achados


def checar(html: str, nome: str) -> list[str]:
    achados = checar_css(html, nome)
    for m in CURTO_ANTES_DE_TITULO.finditer(html):
        cls = classes(m.group('attrs'))
        texto = m.group('texto').strip()
        if not texto:
            continue
        bases = [c.split(':')[-1] for c in cls]
        if 'uppercase' in bases and any(tracking_positivo(c) for c in cls):
            achados.append(f'{nome}: "{texto}" (Tailwind uppercase + tracking) abre seção antes de um título')
            continue
        nomeado = next((c for c in cls if NOME_KICKER.search(c)), None)
        if nomeado:
            achados.append(f'{nome}: "{texto}" (classe {nomeado}) abre seção antes de um título')
    return achados


def coletar(alvo: Path) -> tuple[list[Path], list[Path]]:
    if alvo.is_file():
        fontes = [alvo]
        base = alvo.parent
    else:
        base = alvo
        fontes = sorted({p for ext in EXT_FONTE for p in alvo.rglob(ext) if not _ignorado(p)})
    css = sorted(p for p in base.rglob('*.css') if not _ignorado(p))
    return fontes, css


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    alvo = Path(sys.argv[1]).expanduser()
    if not alvo.exists():
        print(f'não existe: {alvo}')
        return 2
    fontes, css = coletar(alvo)
    if not fontes:
        print(f'nenhum arquivo de página em {alvo}')
        return 2
    achados = []
    for f in fontes:
        achados += checar(f.read_text(encoding='utf-8', errors='replace'), str(f))
    for f in css:
        achados += checar_css(f.read_text(encoding='utf-8', errors='replace'), str(f))
    if achados:
        print('REPROVADO (kicker em caixa alta abrindo seção):')
        for a in achados:
            print('  -', a)
        print('Conserto: a seção abre direto no título. Rótulo curto em caixa alta com espaçamento')
        print('largo antes do h1/h2/h3 é a assinatura de página gerada por IA.')
        return 1
    print(f'ok: {len(fontes)} arquivo(s) de página e {len(css)} .css sem kicker')
    return 0


if __name__ == '__main__':
    sys.exit(main())
