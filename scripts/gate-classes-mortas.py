#!/usr/bin/env python3
"""
GATE DE CLASSE MORTA: classe que existe no codigo-fonte e nao existe no CSS gerado.

============================ POR QUE ESTE GATE EXISTE ============================
Framework de utilitario (Tailwind e parentes) nao reclama de classe invalida. Ela
fica no HTML, o build sai verde, e o navegador simplesmente ignora. O resultado e
um estilo que o autor jura ter aplicado e que nunca chegou na tela.

Custos medidos num unico projeto (08/2026), quatro ocorrencias:
  bg-<cor>/97       -> a barra fixa ficou SEM FUNDO em 92% da rolagem, com o texto
                       da pagina atravessando os links do menu
  bg-<cor>/12       -> o disco da seta do CTA ficou sem preenchimento
  border-<cor>/12   -> o fio do rodape caiu no cinza padrao do framework, virando
                       a coisa mais clara de uma pagina inteiramente verde
  outline-3         -> os campos do formulario ficaram SEM anel de foco, porque o
                       `focus:outline-none` matou a regra global e o `outline-3`,
                       que nao existe, nao repos nada

Numa segunda pagina do mesmo projeto, `shadow-lift` (token que existia num tema e
nao no outro) deixou o unico controle sobre as fotos sem separacao do fundo.

O que torna esta familia de defeito especialmente traicoeira:
1. o build passa;
2. o gate visual quase nunca pega, porque a diferenca e sutil em screenshot
   reduzido (um fio de 1px, um fundo que falta atras de uma barra);
3. quem escreveu conferiu o ARQUIVO (o assert da troca passou) e ninguem conferiu
   o PIXEL.

REGRA QUE SAI DAQUI, e vale alem deste script: `assert` de troca prova que o
ARQUIVO mudou. So medicao no navegador prova que o PIXEL mudou. Toda edicao de
classe utilitaria precisa das duas.
=================================================================================

USO
    node scripts/py.mjs gate-classes-mortas.py [--projeto DIR] [--css DIR] [--fonte DIR]

    --projeto  raiz do projeto (padrao: diretorio atual)
    --css      onde procurar o CSS gerado (padrao: <projeto>/dist; sem dist/, a raiz do
               projeto, que e o caso da pagina HTML + Tailwind compilado)
    --fonte    onde procurar o codigo (padrao: <projeto>/src mais os .html da raiz)

Sai com codigo 1 se achar classe morta.
"""

import argparse
import pathlib
import re
import sys

# Prefixos de utilitario que aceitam sufixo de escala ou de opacidade e que,
# quando o valor nao existe, morrem em silencio.
PREFIXOS = (
    'bg', 'text', 'border', 'ring', 'outline', 'shadow', 'fill', 'stroke',
    'from', 'to', 'via', 'divide', 'decoration', 'accent', 'caret', 'placeholder',
)

# Classe com barra de opacidade (bg-marca/97) ou com numero de escala (outline-3).
RE_OPACIDADE = re.compile(r'\b(?:' + '|'.join(PREFIXOS) + r')-[a-zA-Z0-9-]+/\d{1,3}\b')
RE_ESCALA = re.compile(r'\b(?:outline|ring|border|divide)-\d{1,3}\b')
# Token nomeado do tema (shadow-lift, shadow-alta): nao tem numero nem barra.
RE_TOKEN = re.compile(r'\b(?:shadow|ring)-[a-z][a-zA-Z]{2,}\b')

# Utilitarios nomeados que SEMPRE existem no framework: nao sao candidatos.
CONHECIDOS = {
    'shadow-sm', 'shadow-md', 'shadow-lg', 'shadow-xl', 'shadow-none', 'shadow-inner',
    'ring-inset', 'ring-offset', 'shadow-transparent', 'shadow-current',
}


def limpar_comentarios(t: str) -> str:
    """Comentario que MENCIONA uma classe nao e uso dela.

    Sem isto o gate acusa a propria documentacao: um comentario explicando que
    `backdrop-blur` foi removido conta como uso de `backdrop-blur`.
    """
    t = re.sub(r'/\*.*?\*/', '', t, flags=re.S)          # bloco JS/CSS e JSX {/* */}
    t = re.sub(r'^\s*//.*$', '', t, flags=re.M)          # linha JS
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)         # HTML
    return t


def escapar(classe: str) -> str:
    """Como a classe aparece no CSS gerado: / e . vao escapados com barra."""
    return classe.replace('/', r'\/').replace('.', r'\.')


def regras_simples(css: str) -> dict:
    """Quantas regras de classe única (seletor exatamente `.x`) o CSS tem, por classe. Vale dentro de @media também."""
    import re as _re
    contagem = {}
    for sel in _re.findall(r'([^{}]+)\{', limpar_comentarios(css)):
        for parte in sel.split(','):
            m = _re.fullmatch(r'\s*\.((?:\\.|[A-Za-z0-9_-])+)\s*', parte)
            if m:
                c = m.group(1).replace('\\', '')
                contagem[c] = contagem.get(c, 0) + 1
    return contagem


def classes_nos_seletores(css: str) -> set:
    """As classes que a CSS do autor usa em algum seletor (fora de @media, @font-face e das declarações)."""
    import re as _re
    achadas = set()
    for sel in _re.findall(r'([^{}]+)\{', limpar_comentarios(css)):
        if sel.strip().startswith('@'):
            continue
        achadas |= set(_re.findall(r'\.(-?[A-Za-z_][A-Za-z0-9_-]*)', sel))
    return achadas


def _decls(bloco: str) -> set:
    return {d.strip().replace(' ', '').lower() for d in bloco.split(';') if ':' in d}


def _familias(decls) -> set:
    """A família de cada propriedade (`background-image` e `background` são a mesma; `margin-top` e `margin` também), sem os
    prefixos de navegador que o autoprefixer acrescenta: o minificador reescreve atalho e valor, mas não inventa propriedade."""
    out = set()
    for d in decls:
        prop = d.split(':', 1)[0]
        if prop.startswith('-') and not prop.startswith('--'):
            continue
        out.add(prop if prop.startswith('--') else prop.split('-')[0])
    return out


def regras(css: str):
    """(seletor, declarações) de cada regra com declarações, inclusive dentro de @media."""
    import re as _re
    return [(sel.strip(), corpo) for sel, corpo in _re.findall(r'([^{}]+)\{([^{}]*)\}', limpar_comentarios(css)) if not sel.strip().startswith('@')]


def colisoes_do_clone(raiz: pathlib.Path, css_gerado: str):
    """3.7.0, CLONAR: classe da ORIGINAL que o Tailwind também transformou em utilitário. No teste de aluno da 3.6.3 a classe
    `list-item` da original virou `.list-item{display:list-item}` e pôs bolinhas ao lado dos logos. O autor é o `_input.css`
    sem as diretivas @tailwind (a CSS da original). Colisão: no CSS gerado, uma regra de classe única `.x{...}` traz uma
    propriedade que NENHUMA regra do autor que cita `.x` define (por família: `background-image` conta como `background`).
    Comparar propriedades (e não contar regras nem valores) aguenta o minificador, que junta regras e reescreve atalhos. Devolve (lista de (classe, declarações a mais), aviso ou None)."""
    import re as _re
    entrada = raiz / '_input.css'
    if not entrada.is_file():
        return [], 'sem _input.css: não há CSS do autor para comparar com o utilitário do Tailwind'
    autor = _re.sub(r'@tailwind\s+[a-z]+\s*;', '', entrada.read_text(encoding='utf-8', errors='replace'))
    if '@tailwind' not in entrada.read_text(encoding='utf-8', errors='replace'):
        return [], None
    html = '\n'.join(h.read_text(encoding='utf-8', errors='replace') for h in sorted(raiz.glob('*.html')))
    no_html = set()
    for attr in _re.findall(r'class\s*=\s*"([^"]*)"', html) + _re.findall(r"class\s*=\s*'([^']*)'", html):
        no_html |= set(attr.split())
    do_autor = {}
    for sel, corpo in regras(autor):
        for c in set(_re.findall(r'\.(-?[A-Za-z_][A-Za-z0-9_-]*)', sel)):
            do_autor.setdefault(c, set()).update(_decls(corpo))
    achadas = {}
    for sel, corpo in regras(css_gerado):
        for parte in sel.split(','):
            m = _re.fullmatch(r'\s*\.((?:\\.|[A-Za-z0-9_-])+)\s*', parte)
            if not m:
                continue
            c = m.group(1).replace('\\', '')
            if c not in do_autor or c not in no_html:
                continue
            do_c = _familias(do_autor[c])
            a_mais = sorted(d for d in _decls(corpo) if _familias([d]) and not (_familias([d]) & do_c))
            if a_mais:
                achadas.setdefault(c, set()).update(a_mais)
    return [(c, ';'.join(sorted(d))[:60]) for c, d in sorted(achadas.items())], None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--projeto', default='.')
    ap.add_argument('--css', default=None)
    ap.add_argument('--fonte', default=None)
    ap.add_argument('--clone', action='store_true',
                    help='caminho CLONAR (3.7.0): reprova também a classe da original que o Tailwind virou utilitário')
    args = ap.parse_args()

    raiz = pathlib.Path(args.projeto).resolve()
    # Pagina HTML + Tailwind compilado (sem Vite) nao tem dist/: o CSS gerado mora na raiz.
    # Antes disto o gate dizia "nenhum .css em dist" e o aluno so passava lendo o codigo
    # (teste com aluno, 02/10/2026).
    if args.css:
        dir_css = pathlib.Path(args.css)
    elif (raiz / 'dist').is_dir():
        dir_css = raiz / 'dist'
    else:
        dir_css = raiz
    dir_fonte = pathlib.Path(args.fonte) if args.fonte else raiz / 'src'

    css_arquivos = sorted(p for p in dir_css.rglob('*.css') if 'node_modules' not in p.parts)
    # dist/ montada com CSS em linha (montar-dist.py --css-em-linha): o CSS gerado mora nos
    # <style> do HTML publicado, e é ele que vale.
    em_linha = []
    if not css_arquivos:
        import re as _re
        for h in sorted(dir_css.glob('*.html')):
            blocos = _re.findall(r'<style[^>]*>(.*?)</style>', h.read_text(encoding='utf-8', errors='replace'), _re.S)
            if blocos:
                em_linha.append((h, '\n'.join(blocos)))
        css_arquivos = [h for h, _ in em_linha]
    if not css_arquivos:
        print(f'  ERRO: nenhum .css encontrado em {dir_css}.')
        print('  Rode o build ANTES do gate: o CSS gerado e a fonte da verdade aqui.')
        print('  Página HTML com Tailwind: compile com npx tailwindcss@3 -i _input.css -o tailwind-compiled.css')
        return 1
    css = '\n'.join(b for _, b in em_linha) if em_linha else \
        '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in css_arquivos)

    fontes = sorted(dir_fonte.rglob('*.jsx')) + sorted(dir_fonte.rglob('*.tsx')) \
        + sorted(dir_fonte.rglob('*.js')) + sorted(dir_fonte.rglob('*.ts')) \
        + sorted(dir_fonte.rglob('*.vue')) + sorted(dir_fonte.rglob('*.svelte')) \
        + sorted(raiz.glob('*.html'))
    if not fontes:
        print(f'  ERRO: nenhum arquivo de código em {dir_fonte}.')
        return 1

    mortas = {}
    for f in fontes:
        texto = limpar_comentarios(f.read_text(encoding='utf-8', errors='replace'))
        candidatas = set(RE_OPACIDADE.findall(texto)) \
            | set(RE_ESCALA.findall(texto)) \
            | set(RE_TOKEN.findall(texto))
        for c in candidatas - CONHECIDOS:
            if escapar(c) not in css:
                mortas.setdefault(c, []).append(f.relative_to(raiz).as_posix())

    print('GATE DE CLASSE MORTA')
    print('=' * 72)
    print(f'  CSS lido:    {", ".join(p.name for p in css_arquivos)}')
    print(f'  arquivos:    {len(fontes)}')

    colisoes = []
    if args.clone:
        gerado = css if em_linha else '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in css_arquivos if p.name != '_input.css')
        colisoes, aviso = colisoes_do_clone(raiz, gerado)
        if aviso:
            print(f'  AVISO (clone): {aviso}')
        if colisoes:
            print()
            print(f'  REPROVA (clone): {len(colisoes)} classe(s) da ORIGINAL viraram utilitário do Tailwind, com estilo que a original não tem:')
            for c, decl in colisoes:
                print(f'    .{c}{{{decl}}}')
            print('  No clone a CSS da original vence. Se a original não usa Tailwind, tire `@tailwind utilities;` (e base e components)')
            print('  do _input.css; se você precisa dele, ponha `prefix: "tw-"` no tailwind.config.js. Recompile e meça o pixel.')

    if not mortas:
        if colisoes:
            return 1
        print('  PASSA: nenhuma classe do código está ausente do CSS gerado.')
        return 0

    print()
    print(f'  REPROVA: {len(mortas)} classe(s) existem no código e NÃO existem no CSS.')
    print('  Elas não produzem estilo nenhum, e o build não reclama.')
    print()
    for classe, arquivos in sorted(mortas.items()):
        print(f'    {classe}')
        for a in sorted(set(arquivos)):
            print(f'        em {a}')
    print()
    print('  Causa quase sempre a mesma: valor fora da escala do framework')
    print('  (opacidade /97 quando a escala vai de 5 em 5, outline-3 quando a escala')
    print('  e 0/1/2/4/8) ou token de tema que existe em OUTRO projeto e não neste.')
    print()
    print('  Depois de corrigir, MEÇA O PIXEL, não só o arquivo: getComputedStyle no')
    print('  elemento, ou recorte da região. Foi confiar no assert da troca que deixou')
    print('  uma barra fixa sem fundo passar por uma auditoria inteira.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
