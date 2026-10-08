# Ritmo, animação própria e momento assinatura

O que separou a v7 do estúdio da v6 (a "correta e genérica" que o dono reprovou) foi a página
sair do molde: cada seção com esqueleto, composição de celular e animação próprios, e um elemento
que atravessa a página e muda de estado. Tudo isso entra no PLANO e vira medida.

## Momento assinatura (campo do PLANO)

Um elemento ligado ao assunto, que aparece em 3 ou mais seções (começo, meio e fim) e muda de
estado ao longo da página. Na v7, a coluna vertebral em SVG: torta no topo, alinhando vértebra por
vértebra na avaliação, terminando alinhada no fecho. No PLANO:

`Momento assinatura: a coluna vertebral em SVG; seções: topo, avaliação, fecho; estados: torta -> alinhada`

Ela mora AO LADO de foto de gente, nunca por cima. O `gate-plano.py` cobra o campo; a prova é a
prancha das seções listadas, no tipo `assinatura`, com mudança de pixels entre o primeiro e o
último estado.

## Esqueleto de cada seção (`gate-ritmo.mjs`)

Esqueleto = posição do título x tipo de corpo (cartões, assimétrico, split com foto ou com
desenho, faixa de fotos, lista, texto). Duas seções VIZINHAS nunca têm o mesmo esqueleto, e no
máximo 1 seção é "título centralizado + cartões" (o molde de template). Cartões são blocos de
peso parecido lado a lado; largo contra estreito é assimétrico e quebra o molde. Exceção
declarada: `data-ritmo-ok="motivo"` na seção. Assimetria pedida no plano leva
`data-assimetrico="motivo"` (o `gate-simetria.mjs` vira aviso).

`node <dir-da-skill>/scripts/gate-ritmo.mjs --url http://localhost:8765/`

## Composição e animação por seção (tabela do PLANO)

`| Seção | Desktop | Celular | Animação |`, uma linha por seção, nenhuma célula vazia. A animação
começa com o tipo, antes dos dois pontos ("barras que crescem: do horário de abertura ao de
fechamento"), ligada ao conteúdo da seção. No máximo 2 seções com o mesmo tipo; `assinatura` fica
fora da conta.

**Escolha no repertório.** O tipo de cada linha é o nome de uma receita de
`references/receitas-de-movimento.md` (HTML, CSS e JS da v7, com reserva sem script e com
movimento reduzido; a página `references/receitas/demo.html` mostra todas funcionando). Se
nenhuma serve, a linha declara `criação nova: <motivo>` e a prova de pixels vale igual. A
gramática de base do repertório (uma curva, uma escala de duração, cada item entrando quando ele
chega na tela, estado escondido só atrás de `.js`) vale também para a criação nova.

## Prova de animação: três quadros por seção

1. Escreva o `secoes.json` (nome, seletor, modo e tipo de cada seção; o formato está no cabeçalho
   do `anim.mjs`). Modos: `heroi` (a partir da carga), `entrada` (rola até a seção) e `rolagem`
   (seção com elemento fixo que muda com a rolagem).
2. `node <dir-da-skill>/scripts/anim.mjs --url http://localhost:8765/ --saida <dir>/prova/anim --secoes <dir>/prova/anim/secoes.json`
   grava início, meio e fim em 1440 e em 390.
3. `node <dir-da-skill>/scripts/py.mjs prancha.py --pasta <dir>/prova/anim --secoes <dir>/prova/anim/secoes.json`
   monta a prancha de cada seção e mede a porcentagem de pixels que mudou.
4. `node <dir-da-skill>/scripts/py.mjs gate-animacao.py --pasta <dir>/prova/anim --plano <dir>/PLANO.md`
   reprova seção com menos de 2% de pixels mudando entre o início e o fim (em 1440 ou em 390), mais
   de 2 seções com o mesmo tipo e menos pranchas que linhas da tabela.

Abra as pranchas (Read): a porcentagem diz que mudou, o olho diz se mudou o que devia.
Movimento reduzido desliga tudo; conteúdo nunca depende de animação para aparecer.
