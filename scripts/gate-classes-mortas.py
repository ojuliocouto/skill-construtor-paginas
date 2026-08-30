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
    python3 gate-classes-mortas.py [--projeto DIR] [--css DIR] [--fonte DIR]

    --projeto  raiz do projeto (padrao: diretorio atual)
    --css      onde procurar o CSS gerado (padrao: <projeto>/dist)
    --fonte    onde procurar o codigo (padrao: <projeto>/src mais index.html)

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--projeto', default='.')
    ap.add_argument('--css', default=None)
    ap.add_argument('--fonte', default=None)
    args = ap.parse_args()

    raiz = pathlib.Path(args.projeto).resolve()
    dir_css = pathlib.Path(args.css) if args.css else raiz / 'dist'
    dir_fonte = pathlib.Path(args.fonte) if args.fonte else raiz / 'src'

    css_arquivos = sorted(dir_css.rglob('*.css'))
    if not css_arquivos:
        print(f'  ERRO: nenhum .css encontrado em {dir_css}.')
        print('  Rode o build ANTES do gate: o CSS gerado e a fonte da verdade aqui.')
        return 1
    css = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in css_arquivos)

    fontes = sorted(dir_fonte.rglob('*.jsx')) + sorted(dir_fonte.rglob('*.tsx')) \
        + sorted(dir_fonte.rglob('*.js')) + sorted(dir_fonte.rglob('*.ts')) \
        + sorted(dir_fonte.rglob('*.vue')) + sorted(dir_fonte.rglob('*.svelte')) \
        + sorted(raiz.glob('*.html'))
    if not fontes:
        print(f'  ERRO: nenhum arquivo de codigo em {dir_fonte}.')
        return 1

    mortas = {}
    for f in fontes:
        texto = limpar_comentarios(f.read_text(encoding='utf-8', errors='replace'))
        candidatas = set(RE_OPACIDADE.findall(texto)) \
            | set(RE_ESCALA.findall(texto)) \
            | set(RE_TOKEN.findall(texto))
        for c in candidatas - CONHECIDOS:
            if escapar(c) not in css:
                mortas.setdefault(c, []).append(str(f.relative_to(raiz)))

    print('GATE DE CLASSE MORTA')
    print('=' * 72)
    print(f'  CSS lido:    {", ".join(p.name for p in css_arquivos)}')
    print(f'  arquivos:    {len(fontes)}')

    if not mortas:
        print('  PASSA: nenhuma classe do codigo esta ausente do CSS gerado.')
        return 0

    print()
    print(f'  REPROVA: {len(mortas)} classe(s) existem no codigo e NAO existem no CSS.')
    print('  Elas nao produzem estilo nenhum, e o build nao reclama.')
    print()
    for classe, arquivos in sorted(mortas.items()):
        print(f'    {classe}')
        for a in sorted(set(arquivos)):
            print(f'        em {a}')
    print()
    print('  Causa quase sempre a mesma: valor fora da escala do framework')
    print('  (opacidade /97 quando a escala vai de 5 em 5, outline-3 quando a escala')
    print('  e 0/1/2/4/8) ou token de tema que existe em OUTRO projeto e nao neste.')
    print()
    print('  Depois de corrigir, MEÇA O PIXEL, nao so o arquivo: getComputedStyle no')
    print('  elemento, ou recorte da regiao. Foi confiar no assert da troca que deixou')
    print('  uma barra fixa sem fundo passar por uma auditoria inteira.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
