# Etapa PLANO: o aluno aprova a página antes do código

Decisão do dono (03/10/2026): *"seria bom se essa skill desse opções de visual e tipos de
seções pro cara, inclusive uma etapa de planejamento pra copy, pixel, código, referências"*.

A etapa roda logo depois do briefing (a) e da pesquisa de referências (b), e termina num
documento único, `<dir>/PLANO.md`, que o aluno lê, marca e aprova. **Sem o PLANO aprovado,
nenhuma linha de código** (`gate-plano.py`). O plano é o lugar barato de errar: trocar de
direção aqui custa uma conversa; depois do código, custa a página.

## Como produzir

1. **Referências (a):** reuse os prints do passo b. Para cada uma, uma linha com o print e "o
   que essa faz bem" (o princípio, não a frase). O aluno marca com `[x]` as que gosta.
2. **Visual (b):** acione a skill `frontend-design` (Skill tool) com o briefing e a síntese das
   referências e peça **3 direções BEM diferentes entre si**. Diferentes quer dizer que mudam
   ao mesmo tempo a tipografia, a paleta, o jeito como a imagem entra e o ritmo; trocar só a
   cor não conta. Os três visuais padrão de IA (creme com serifa e terracota; quase preto com
   um acento ácido; jornal de filetes) não entram, a menos que o briefing peça. Para cada
   direção, escreva a primeira dobra real em HTML (`<dir>/plano/direcoes/a.html`, `b.html`,
   `c.html`), com a copy do briefing, e grave as prévias:
   `node <dir-da-skill>/scripts/previa-direcoes.mjs --saida <dir>/plano <dir>/plano/direcoes/a.html <dir>/plano/direcoes/b.html <dir>/plano/direcoes/c.html`
   Sai `direcao-a.png` (1440), `direcao-a-celular.png` (390), idem b e c, e `direcoes.png`
   com as três lado a lado. **Abra o `direcoes.png` (Read)** e confira se as três são de fato
   diferentes; se duas parecem a mesma página com outra cor, refaça uma delas.
3. **Seções (c):** grave as miniaturas do cardápio e cole no plano a lista por objetivo, com a
   linha "quando usar" de `references/secoes/README.md`:
   `node <dir-da-skill>/scripts/previa-direcoes.mjs --miniaturas <dir-da-skill>/references/secoes --saida <dir>/plano/miniaturas`
   Marque com uma sugestão o formato que você recomendaria para cada objetivo, e por quê. O
   aluno monta a `### Ordem escolhida`.
   Depois da ordem, a `### Composição por seção` (v3.5): uma tabela
   `| Seção | Desktop | Celular | Animação |`, uma linha por seção da ordem, sem célula vazia. A
   animação começa com o tipo, antes dos dois pontos, e é ligada ao conteúdo da seção; no
   máximo 2 seções com o mesmo tipo (`references/ritmo-e-animacao.md`). **O tipo vem do
   repertório** (`references/receitas-de-movimento.md`: use o nome da receita) **ou declara
   `criação nova: <motivo>`**; uma seção sem receita nem motivo volta para o plano.
   O PLANO também nomeia o **momento assinatura** (v3.5): um elemento ligado ao assunto, que
   aparece em 3 ou mais seções e muda de estado ao longo da página.
4. **Copy (d):** o texto de cada seção da ordem escolhida, na tabela
   `| Seção | Frase | Linha do briefing que sustenta |`. A sustentação é a linha do briefing
   entre aspas; o que o briefing não tem vira `PENDENTE: <o quê>` e entra em
   `### Pendências do cliente`. Essa tabela vira depois o `evidencias/sustentacao.md` do passo d.
   Ela é o ponto de partida, não a fonte final: no passo d ela vira a `evidencias/sustentacao.md`, que
   é a tabela VIVA. A copy final, as respostas da FAQ e os rótulos entram na `sustentacao.md` quando
   entram na página, e o `gate-verdade.py` avisa (sem reprovar) quando as duas tabelas se afastam.
   A linha `Material da cliente pedido:` (v3.5) lista o que só a cliente tem: foto real da
   profissional, número do WhatsApp, depoimentos com autorização, registro no conselho.
5. **Pixel e rastreamento (e):** pergunte se a página vai receber anúncio. A linha
   `Pixel pedido: Meta e GA4` (ou `Meta`, `GA4`, `nenhum`) fica no topo do plano; a seção diz
   onde o aluno pega cada ID e o que fazer se não tiver, e lista os eventos (`clique_whatsapp`,
   `clique_cta`, `rolagem_50`, `rolagem_90`, `envio_formulario`). Tudo em
   `references/rastreamento.md`. **Nada de ID real no plano:** o gate reprova.
6. **Código e publicação (f):** tecnologia (HTML + Tailwind compilado, o padrão), onde publica,
   o domínio e o que muda no domínio final: sai o `noindex`, o `robots.txt` deixa de bloquear,
   a `og:image` vira endereço absoluto e o `canonical` aponta para o domínio.
7. **Aprovação (g):** uma caixa por seção. Sessão interativa: mostre o plano e o `direcoes.png`
   e espere o aluno marcar. Sessão não interativa: marque, e liste na entrega cada escolha que
   o aluno deveria ter feito.

`node <dir-da-skill>/scripts/py.mjs gate-plano.py --projeto <dir>`

## O modelo do PLANO.md

Os títulos `## a.` a `## g.` são lidos pelo gate. Imagens com caminho relativo à pasta do plano.

```markdown
# PLANO: <nome do negócio>

Pixel pedido: Meta e GA4

Momento assinatura: <o elemento, em uma frase>; seções: <3 ou mais, separadas por vírgula>; estados: <de -> para>

Ícone do site: <o que o favicon desenha em 32 px, ligado ao assunto>

Material da cliente pedido:
- <foto real da profissional>
- <número do WhatsApp>
- <depoimentos com autorização>

## a. Referências

Marque com [x] as que você gosta.

- [ ] <nome> (<mesmo negócio | design>): ![<nome>](referencias/<arquivo>-dobra.png) O que essa faz bem: <princípio>.

## b. Visual

### Direção A: <nome curto>
![Direção A](plano/direcao-a.png)
Tipografia: <display e corpo>. Paleta: <4 a 6 hex>. Imagem: <como entra>. Ritmo: <denso ou arejado>.
Celular: ![Direção A no celular](plano/direcao-a-celular.png)

### Direção B: <nome curto>
(idem)

### Direção C: <nome curto>
(idem)

As três lado a lado: ![Comparação](plano/direcoes.png)

Escolha: [ ] A  [ ] B  [ ] C  [ ] misturar: <o quê de cada>

## c. Seções

### Primeira dobra
- dobra-split-imagem: ![dobra-split-imagem](plano/miniaturas/dobra-split-imagem.png) Quando usar: <linha do cardápio>.
(um bloco por objetivo: dor, mecanismo ou diferencial, prova, oferta, como funciona, FAQ, fecho)

### Ordem escolhida
1. Primeira dobra: <formato>
2. <objetivo>: <formato>

### Composição por seção

| Seção | Desktop | Celular | Animação |
|---|---|---|---|
| Primeira dobra | <como se compõe em 1440> | <como se compõe em 390> | <tipo>: <o que anima> |

## d. Copy

| Seção | Frase | Linha do briefing que sustenta |
|---|---|---|
| Primeira dobra | <título> | "<linha do briefing>" |

### Pendências do cliente
- <o que só o cliente tem>

## e. Pixel e rastreamento

<onde pegar cada ID, o que fazer sem ele, e os 5 eventos>

## f. Código e publicação

<tecnologia, onde publica, domínio; noindex, robots e og:image absoluta no domínio final>

## g. Aprovação

- [ ] a. Referências
- [ ] b. Visual
- [ ] c. Seções
- [ ] d. Copy
- [ ] e. Pixel e rastreamento
- [ ] f. Código e publicação
```

## O que o gate cobra

`scripts/gate-plano.py` reprova com exit 1: seção `## a.` a `## g.` faltando ou fora de
ordem; referência sem print real ou sem "faz bem", ou nenhuma marcada; menos de 3 direções,
direção sem prévia PNG, falta do `direcoes.png` ou nenhuma escolha marcada; menos de 10
miniaturas no cardápio ou sem `### Ordem escolhida` com 3 seções; tabela de copy sem a coluna
de sustentação, frase sem sustentação ou `PENDENTE` sem a lista de pendências; sem a linha
`Pixel pedido:`, evento faltando quando há pixel, ID real de Meta Pixel ou GA4 no texto; código
sem `noindex`, `robots` ou `og:image`; e qualquer caixa da aprovação desmarcada. Desde a 3.5, também:
sem `Momento assinatura:` (elemento, 3 ou mais seções e os estados com `->`), sem `Ícone do site:` (3.5.6), sem a tabela
`Composição por seção` (uma linha por seção da ordem, célula vazia, mais de 2 seções com o mesmo
tipo de animação) e sem `Material da cliente pedido:` (`nenhum` só com o motivo).

## Depois do PLANO

A tabela de composição vira o `secoes.json` da prova de animação (passo f) e o momento assinatura
é a coluna `assinatura` dela. O passo c (plano visual) detalha a direção escolhida, sem reabrir as outras; o passo d copia a
copy aprovada para `evidencias/copy.md` e `evidencias/sustentacao.md`; o passo e constrói a
ordem escolhida com os formatos de `references/secoes/` e, se houver pixel, o snippet de
`references/rastreamento.md`; o passo f roda o `gate-rastreamento.py` na `dist/`.
