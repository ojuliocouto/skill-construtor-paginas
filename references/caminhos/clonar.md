# Caminho CLONAR: reproduzir com fidelidade (URL ao vivo ou PDF)

Aqui a copy e a identidade JÁ EXISTEM. Não se escreve copy nova, não se inventa cor nem fonte,
não se pesquisa referência de outro site: a referência é a própria original. Inventar aqui é
defeito. Se o pedido traz clone E melhoria ("clona e deixa foda"), o caminho é outro:
`references/caminhos/clonar-elevar.md`.

`<dir-da-skill>` = a pasta desta skill; `<dir>` = a pasta do projeto. Uma pasta de prova só:
`<dir>/provas/`. É onde o `provar.mjs` grava e onde o pacote do auditor procura. A original fica
em `<dir>/original/`.

## 1. Extrair o real, nunca olhar e chutar

URL ao vivo:

`node <dir-da-skill>/scripts/extrai-identidade.mjs "<URL>" > <dir>/original/identidade.json`

O JSON traz a paleta real ordenada por uso e as variáveis CSS da marca. Traz o h1 e o botão com
estilo computado, a lista de seções e as imagens. O logo se BAIXA do site, nunca se recria. O
script acha o Playwright do projeto, do `NODE_PATH` ou do npm global; nunca crave caminho
absoluto de `node_modules`. O gate de fidelidade do passo 4 abre a original pelo campo `url`
desse arquivo.

O extrato é ponto de partida, não medida. O h1 que ele escolhe pode não ser o da página. Ele não
traz pontos de quebra, regras `@media` nem o fundo do herói. A medida elemento por elemento vem
do passo 4. Para os pontos de quebra, leia a CSS da original: baixe os `.css` que o HTML cita e
procure `@media`.

PDF: leia o arquivo inteiro (Read, em blocos de até 20 páginas) e mapeie seção por seção. Tire a
paleta, a tipografia e as imagens do próprio PDF. Fonte que não dá para identificar: a mais
próxima disponível, declarada na entrega como aproximação.

Print da original:
`node <dir-da-skill>/scripts/screenshot-prova.js "<URL>" <dir>/original --sem-identidade`

## 2. Inventariar e declarar o delta

Seções na ordem, componentes, pontos de quebra (da CSS da original), interações. Depois escreva
o que vai ficar idêntico e o que muda, e por quê (`<dir>/inventario.md`). Sem pedido explícito, o
padrão é ZERO mudança de identidade. Interação que não se clona (menu, abas, busca, script de
terceiro) entra no delta e na entrega.

## 3. Construir

HTML com a CSS da original, ou a stack do projeto destino. Do passo e do CRIAR
(`references/caminhos/criar.md`) vale só isto num clone:

| Passo e do CRIAR | No clone |
|---|---|
| `gate-plano.py` antes da primeira linha | não se aplica (não há PLANO) |
| 1. Lente curta de gosto no herói (`gosto-heroi.py`) | não se aplica: o herói é o da original. Construa o herói, rode o passo 4 só nele e siga |
| 2. Imagens | baixe as da original e otimize (WebP, `width` e `height`, `loading="lazy"` abaixo da dobra) sem trocar enquadramento nem recorte. Foto da original não pede licença nova nem "imagem ilustrativa": ela é da própria página. Banco de imagens, folha de contato e `LICENCAS.md` não se aplicam |
| 3. Movimento | o da original, nada além. Página sem animação continua sem animação. Copie a regra de `prefers-reduced-motion` se a original tiver |
| 3. Texto, botão no celular, barra fixa | o da original, mesmo quando a regra da skill pediria outro (viúva, alvo de toque, 2 botões por tela) |
| 3. Peso e fontes | vale: só os pesos usados, `woff2`, CSS em linha na publicação (`montar-dist.py --css-em-linha`) |
| 3b. Padrão da v7 | não se aplica |
| 4. Identidade da página | vale: `<title>`, description, favicon, `og:*` copiados da original (o favicon baixado, não gerado) |
| 5. `noindex` fora do domínio final | vale |
| 6. Rodapé e destinos | os da original; link que só funciona com o script dela (`mailto` montado no carregamento) se confere no HTML DEPOIS de carregado |
| 7. Rastreamento | não se aplica (o pixel da original não se copia) |
| 8. Nenhum comentário interno | vale |

**Tailwind no clone: a CSS da original vence.** Se a original não usa Tailwind, deixe as
diretivas `@tailwind utilities;` (e `base` e `components`) FORA do `_input.css`. A outra saída é
pôr `prefix: "tw-"` no `tailwind.config.js`. Com o Tailwind sem prefixo, a classe da original
que coincide com um utilitário ganha estilo que ela não tem. No teste de aluno da 3.6.3 a classe
`list-item` virou `display: list-item` e pôs bolinhas ao lado dos 5 logos. O gate de classes
mortas com `--caminho clonar` reprova isso.

Original feita com Tailwind: compile com a mesma versão e use as classes dela.

## 4. Gate de fidelidade (medida, não olho)

Sirva a dist e meça o clone contra a original, nas duas larguras:

`node <dir-da-skill>/scripts/py.mjs montar-dist.py --projeto <dir> --css-em-linha`
`node <dir-da-skill>/scripts/gate-fidelidade.mjs --url <url do clone servido> --projeto <dir>`

O gate abre a original e o clone em 1440x900 e 390x844, com a mesma espera e a mesma rolagem. A
URL da original vem de `<dir>/original/identidade.json`, ou de `--original <url>`. Ele mede:
- a altura da página;
- os elementos-chave (títulos, parágrafos, links, botões, itens, imagens, campos, cabeçalho,
  seções e rodapé), pareados pelo que são: tag e texto, ou o nome do arquivo da imagem;
- em cada par, a caixa (x, y, largura, altura) e o estilo que se vê (fonte, tamanho, peso,
  entrelinha, cor, fundo, canto, display);
- o diff de pixels da página inteira, com os retângulos onde ele está e o elemento da original
  que cada um cobre.

Cada linha `DIFERE` diz o elemento e o que mudou, cada linha `PIXELS` diz onde olhar. Diferença
de estilo sem nenhum pixel diferente na caixa é `AVISO` e não reprova. O gate reprova com altura
diferente (mais de 4 px) ou com mais de 1% dos pixels diferentes. Reprova também com elemento da
original sem par no clone, ou com par de caixa, texto ou estilo diferente. Ele grava em
`<dir>/gates/fidelidade/` o `lado-<largura>.png` (original à esquerda, em tamanho real), o
`diff-<largura>.png` (a diferença em vermelho sobre o clone) e o `laudo.json`. Ele também
registra o uso do Playwright.

Abra o lado e o diff das duas larguras. Divergiu sem estar no delta declarado: copie o valor da
original e rode de novo. No teste da 3.6.3 foram 2 voltas. A primeira achou o herói 708 contra
723 px (uma regra `@media`) e a margem 60 contra 45. A segunda achou ícones 10% maiores, porque o
`rem` da página é 14,5 px. A original
muda com o tempo (versão no cabeçalho, número do dia): o gate mostra o texto novo e o clone
acompanha.

Lado a lado para o olho, sem redução. O padrão do script reduz para 760 px e pergunta pelos
eixos de elevação, que são do CLONAR + ELEVAR; o `--modo fiel` não:

`node <dir-da-skill>/scripts/py.mjs lado-a-lado.py <dir>/original/prova-desktop.png <dir>/provas/prova-desktop.png <dir>/comparativo.png --rotulos "Original,Clone" --modo fiel`

## 5. Gates e auditor

Os gates do clone num comando só, com o conjunto do clone fiel:

`node <dir-da-skill>/scripts/rodar-gates.mjs --projeto <dir> --caminho clonar`

- Reprovam: `fidelidade` (o passo 4), `oclusao`, `classes-mortas` (com a colisão do Tailwind),
  `publicacao` e `uso-ferramentas`. No clone o `uso-ferramentas` cobra só o Playwright, e o gate
  de fidelidade registra esse uso sozinho.
- Não rodam: `verdade`, `rastreamento`, `plano` e `referencias`. Eles perguntam pelo briefing,
  pelo PLANO, pelo pixel e pelas 6 referências, que o clone não tem.
- Viram AVISO, ressalva por fidelidade: `movimento`, `responsivo`, `texto`, `imagens`,
  `simetria`, `composicao` e `sem-kicker`. Eles medem regra da skill que a original pode não
  seguir (animação, alvo de toque, viúva, licença da foto da própria página). Eles rodam, a wave
  recebe o exit real, e a saída da rodada fica 0.

Leia cada aviso. Se o defeito também está na original, não conserte: consertar trai a
fidelidade, e o aviso vai escrito na entrega. Se só o clone tem, é defeito de fidelidade e se
conserta.

A rodada completa registra o exit real de cada gate na wave. O `provar.mjs` do passo h do CRIAR
grava os prints em `<dir>/provas/` e registra a `identidade`. Ele reprova print com imagem
quebrada ou fonte que não carregou.

`node <dir-da-skill>/scripts/provar.mjs --projeto <dir>`

As 9 lentes de `references/auditores.md` passam por UM auditor independente, com o pacote de
evidência e teto de 2 rodadas. No clone o pacote não exige PLANO, briefing, referências do passo b
nem as pranchas do vídeo. Ele exige os prints da original (`<dir>/original/prova-desktop.png` e
`prova-mobile.png`) e os do clone (`<dir>/provas/prova-desktop.png` e `prova-mobile.png`). A
lente `comparacao-referencias` compara com a original.

`node <dir-da-skill>/scripts/py.mjs pacote-auditoria.py --projeto <dir> --url <url> --caminho clonar`
`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> --caminho clonar checar`
`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> --caminho clonar rodada --criticos <N> --altos <N> --regressoes <N>`

O `checar` do clone ignora os 4 gates que não se aplicam e mostra os avisos como RESSALVA. O
`rodada` grava cada ressalva por fidelidade no desfecho, para a entrega declarar.

## 6. Prova e entrega

Passo h do CRIAR: prints lidos com os próprios olhos, interação clicada, bloco de entrega. O
bloco traz os pixels diferentes em 1440 e 390 (do gate de fidelidade) e o delta declarado. Ele
traz também as ressalvas por fidelidade, uma por linha.
