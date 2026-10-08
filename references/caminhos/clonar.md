# Caminho CLONAR: reproduzir com fidelidade (URL ao vivo ou PDF)

Aqui a copy e a identidade JÁ EXISTEM. Não se escreve copy nova, não se inventa cor nem fonte,
não se pesquisa referência de outro site: a referência é a própria original. Inventar aqui é
defeito. Se o pedido traz clone E melhoria ("clona e deixa foda"), o caminho é outro:
`references/caminhos/clonar-elevar.md`.

`<dir-da-skill>` = a pasta desta skill; `<dir>` = a pasta do projeto.

## 1. Extrair o real, nunca olhar e chutar

URL ao vivo:

`node <dir-da-skill>/scripts/extrai-identidade.mjs "<URL>"`

Devolve em JSON a paleta real ordenada por uso, as variáveis CSS da marca, o h1 e o botão com
estilo computado, a lista de seções e as imagens. O logo se BAIXA do site, nunca se recria. O
script acha o Playwright do projeto, do `NODE_PATH` ou do npm global; nunca crave caminho
absoluto de `node_modules`.

PDF: leia o arquivo inteiro (Read, em blocos de até 20 páginas), mapeie seção por seção, tire a
paleta e a tipografia do próprio PDF e extraia as imagens dele. Fonte que não dá para
identificar: a mais próxima disponível, declarada na entrega como aproximação.

Print da original para o gate final:
`node <dir-da-skill>/scripts/screenshot-prova.js "<URL>" <dir>/original --sem-identidade`

## 2. Inventariar e declarar o delta

Seções na ordem, componentes, pontos de quebra, interações. Depois escreva o que vai ficar
idêntico e o que muda, e por quê. Sem pedido explícito, o padrão é ZERO mudança de identidade.

## 3. Construir

Mesma construção do CRIAR (`references/caminhos/criar.md`, passo e): HTML + Tailwind compilado
ou a stack do projeto destino, imagens otimizadas, identidade da página e `noindex` fora do
domínio final.

## 4. Gate de fidelidade

`python3 <dir-da-skill>/scripts/lado-a-lado.py <dir>/original/prova-desktop.png <dir>/prova/prova-desktop.png <dir>/comparativo.jpg --rotulos "Original,Clone"`

Olhe a imagem e confira cor a cor, fonte, hierarquia, ordem das seções e o celular. Divergiu
sem estar no delta declarado: volta.

## 5. Gates e auditores

Os gates mecânicos do passo f do CRIAR e as 9 lentes de `references/auditores.md`, passadas por
UM auditor independente com o pacote de evidência (`pacote-auditoria.py --caminho clonar`, que
não exige PLANO nem briefing) e teto de 2 rodadas, com `--caminho clonar` no wave (o gate de
referências não se aplica; a lente `comparacao-referencias` compara com a original):

`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> --caminho clonar checar`
`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> --caminho clonar rodada --criticos <N> --altos <N> --regressoes <N>`

## 6. Prova e entrega

Passo h do CRIAR: prints lidos com os próprios olhos, interação clicada, bloco de entrega.
