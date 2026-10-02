#!/usr/bin/env python3
"""Gate de tells: toda página sai sem kicker em caixa alta e sem número decorativo.

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
  3. NÚMERO DECORATIVO (tell V2 de references/anti-vibe-coding.md):
     - número gigante sozinho num elemento ("4", "1", "01") com fonte >= 48px, seja por
       Tailwind (text-5xl a text-9xl, text-[72px], text-[4rem]), por style inline ou por
       regra de um .css do projeto;
     - numeração 01/02/03: dois ou mais elementos cujo texto inteiro é "01", "02"...
Falso positivo conhecido: rótulo DENTRO de card ("Encontro 01") é permitido; o gate só olha
o que vem logo antes de um título, e número no meio de frase ("até 4 pessoas") não conta.

Por que lê Tailwind e .css externo (relatório do aluno, 02/10/2026): o mutante
`<p class="text-[12px] uppercase tracking-[0.2em]">Para você</p><h2>` passava com "ok",
porque a versão antiga só olhava CSS dentro do HTML e classe com nome de kicker. A skill
manda Tailwind em toda página, então o gate era cego justamente para o caso mais comum.
O número gigante entrou no mesmo dia: os numerais "4" e "1" em card de "formas de praticar"
passaram por todos os gates e só caíram no olho do dono.
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

# Número sozinho no elemento: "4", "01", "1." ou "2)". Número dentro de frase não casa.
SO_NUMERO = re.compile(
    r'<(?P<tag>p|span|div|small|strong|em|b|i|dt|dd|li)\b(?P<attrs>[^>]*)>\s*(?P<num>0?\d{1,2}[.)]?)\s*</(?P=tag)>',
    re.I)
TEXTO_GIGANTE = {f'text-{n}xl' for n in range(5, 10)}
TAMANHO_ARB = re.compile(r'^text-\[([0-9.]+)(px|rem|em)\]$')
FONT_SIZE = re.compile(r'font-size\s*:\s*([0-9.]+)\s*(px|rem|em)', re.I)
REGRA_CLASSE = re.compile(r'\.([A-Za-z_][\w-]*)\s*\{([^{}]*)\}')


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


def gigante(valor: float, unidade: str) -> bool:
    return valor >= (48 if unidade.lower() == 'px' else 3)


def classes_gigantes(css: str) -> set[str]:
    """Classes simples (.marca-num {...}) cujo font-size é de número decorativo."""
    saida = set()
    for nome, corpo in REGRA_CLASSE.findall(css):
        m = FONT_SIZE.search(corpo)
        if m and gigante(float(m.group(1)), m.group(2)):
            saida.add(nome)
    return saida


def checar_numeros(html: str, nome: str, gigantes_css: set[str]) -> list[str]:
    achados, zeros = [], set()
    for m in SO_NUMERO.finditer(html):
        num = m.group('num')
        if len(num) >= 2 and num[0] == '0':
            zeros.add(num.rstrip('.)'))
        cls = classes(m.group('attrs'))
        bases = [c.split(':')[-1] for c in cls]
        motivo = None
        if TEXTO_GIGANTE & set(bases):
            motivo = next(b for b in bases if b in TEXTO_GIGANTE)
        for b in bases:
            a = TAMANHO_ARB.match(b)
            if a and gigante(float(a.group(1)), a.group(2)):
                motivo = b
        estilo = re.search(r'style\s*=\s*"([^"]*)"', m.group('attrs'), re.I)
        if estilo:
            f = FONT_SIZE.search(estilo.group(1))
            if f and gigante(float(f.group(1)), f.group(2)):
                motivo = f'style font-size {f.group(1)}{f.group(2)}'
        css_hit = next((c for c in bases if c in gigantes_css), None)
        if css_hit:
            motivo = f'classe {css_hit} do CSS'
        if motivo:
            achados.append(f'{nome}: número gigante decorativo "{num}" ({motivo}). '
                           'Número solto em fonte grande é tell V2: tire o número ou deixe o título carregar')
    if len(zeros) >= 2:
        achados.append(f'{nome}: numeração decorativa {", ".join(sorted(zeros))} (tell V2). '
                       'Passo e card não levam 01/02/03')
    return achados


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
    textos_css = {f: f.read_text(encoding='utf-8', errors='replace') for f in css}
    gigantes_css = set()
    for texto in textos_css.values():
        gigantes_css |= classes_gigantes(texto)
    for f in fontes:
        html = f.read_text(encoding='utf-8', errors='replace')
        achados += checar(html, str(f))
        achados += checar_numeros(html, str(f), gigantes_css | classes_gigantes(html))
    for f, texto in textos_css.items():
        achados += checar_css(texto, str(f))
    if achados:
        print('REPROVADO (tell de IA: kicker em caixa alta ou número decorativo):')
        for a in achados:
            print('  -', a)
        print('Conserto: a seção abre direto no título. Rótulo curto em caixa alta com espaçamento')
        print('largo antes do h1/h2/h3 é a assinatura de página gerada por IA.')
        return 1
    print(f'ok: {len(fontes)} arquivo(s) de página e {len(css)} .css sem kicker e sem número decorativo')
    return 0


if __name__ == '__main__':
    sys.exit(main())
