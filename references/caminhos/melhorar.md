# Caminho MELHORAR: a mesma página, só que melhor (inclui VARIANTE VISUAL)

Objetivo: elevar sem destruir o que já funciona. O erro clássico é "melhorar" trocando tudo e
derrubando a conversão que existia.

## 1. Baseline primeiro, obrigatório

Antes de tocar em qualquer coisa, print desktop e celular do estado atual e Lighthouse, se
houver Chromium:

`node <dir-da-skill>/scripts/screenshot-prova.js "<URL>" <dir>/baseline --sem-identidade`

Sem baseline não existe "melhorou", existe "ficou diferente". Medir sempre COM compressão
(`scripts/servidor-gzip.py` para build local): sem gzip a versão nova pode aparecer pior só por
causa do servidor. Celular de verdade é Playwright com `isMobile` e escala 2x, nunca janela
estreita de navegador de desktop.

## 2. Diagnóstico com evidência

Rode as 9 lentes de `references/auditores.md` sobre a página ATUAL e liste os problemas com
severidade e evidência. Para a lente `comparacao-referencias`, faça a pesquisa de referências
do CRIAR (`references/pesquisa-de-referencias.md`): ela mostra até onde a página pode chegar.

## 3. Priorizar por impacto

Hierarquia e espaçamento primeiro (maior alavanca), depois a primeira dobra, depois imagem,
depois movimento. Cosmético por último. O que já converte não se mexe sem motivo declarado.
Identidade só muda com pedido explícito.

## 4. Plano e lotes

Mudança visual relevante passa pelo plano visual da `frontend-design` (passo c do CRIAR), com
a página atual como ponto de partida. Aplique em lotes revisáveis, do maior impacto para o
menor.

## 5. Gate de melhoria (não regressão, somado aos gates do CRIAR)

Antes e depois lado a lado (`scripts/lado-a-lado.py`), com a nota de cada lente nos dois
estados. Regressão confirmada por medida = não entrega. Lighthouse entra só se houve baseline:
o novo tem que ser igual ou melhor. Depois, gates mecânicos, auditores e prova do CRIAR (passos
f, g, h), com `--caminho melhorar` no wave.

---

## Variante visual (mesmo conteúdo, outra linguagem)

Sinal: a página existe e o pedido é outra LINGUAGEM para o mesmo conteúdo ("a mesma ideia, só
que mais tecnológica", "uma versão dark", "uma mais sóbria pra mostrar pro cliente").

**Travado:** copy palavra por palavra, contato, identidade de marca, ordem das seções, âncoras
do menu, destino do lead. **Muda:** terreno, grade, escala, densidade, movimento, acabamento.

Fluxo: herda a copy e a identidade, refaz a pesquisa de referências para a linguagem nova e o
plano visual inteiro, constrói e roda gates e auditores completos, com `--caminho variante`.

Gate próprio:
1. As duas versões lado a lado, na mesma escala.
2. Por escrito: **as duas leem como duas direções legítimas, ou como uma boa e uma pior?**
   Variante pior que a anterior é regressão com outro nome.
3. O que foi PRESERVADO, item a item.
4. O que foi REJEITADO da direção nova, e por quê (ex.: neon e glitch numa empresa de segurança
   do trabalho).

Armadilha medida: forma que pede conteúdo que a fonte não tem. Uma variante "técnica" de copy
institucional curta ficou com 55% de tabela vazia, porque linguagem de dado pede dado. Antes de
escolher a linguagem, pergunte se o conteúdo a sustenta.
