# Receitas de movimento

Repertório de animações que já passaram pelo olho do dono. Todas saem da v7 do estúdio de pilates
(a página que ele aprovou com "as animações ficaram fodas, todas as páginas criadas com essa skill
têm que ser criativas assim"), sem biblioteca: CSS mais um script curto. A página
`references/receitas/demo.html` mostra cada receita funcionando, um bloco por receita, e o
`scripts/provar-receitas.mjs` prova no navegador que cada bloco se move.

**Como usar no PLANO:** a coluna Animação de cada seção escolhe uma receita daqui, pelo nome, ou
declara uma criação nova com o motivo (`criação nova: <motivo>`). Copiar a receita e trocar os
nomes neutros pelos do assunto é o caminho curto; o que não pode mudar é a gramática de base.

## Gramática de base (vale para toda receita)

- **Uma curva quase única:** `cubic-bezier(.2,.8,.2,1)` (sai rápido, assenta devagar). Exceções
  da v7: a pergunta que fecha (`cubic-bezier(.4,0,.2,1)`, 320 ms) e o contorno que se desenha
  (`cubic-bezier(.4,.1,.2,1)`). Fora isso, `ease` só em cor e opacidade curtas.
- **Uma escala de duração:** de 0,25 s a 2,0 s. Hover e cor: 0,25 a 0,45 s. Revelações ao entrar:
  0,7 a 1,6 s (a v7 usa 0,8 s no item comum e 1,1 a 1,6 s na foto). Só o alinhamento da
  assinatura passa de 1,6 s, em 2,0 s.
- **Cada item entra quando ELE chega na tela**, nunca o grupo inteiro de uma vez. Observador
  (`IntersectionObserver`) com `threshold: 0.18` e `rootMargin: '0px 0px -6% 0px'`; ao entrar, o
  item ganha a classe `visivel` e deixa de ser observado.
- **Todo estado escondido fica atrás de `.js`.** O `<html>` nasce `class="no-js"` e um script de
  uma linha no `<head>` troca por `js`. Sem script, a página inteira aparece. Regra do gate:
  `opacity: 0`, `transform` de entrada e `clip-path` só em seletor que começa com `.js`.
- **Bloco de movimento reduzido** (`@media (prefers-reduced-motion: reduce)`) devolve cada
  receita ao estado final, e o script lê `matchMedia` e pula o que não é só CSS. Texto igual,
  só sem o movimento. `scroll-behavior: smooth` volta a `auto` ali.
- **Propriedades:** `transform`, `opacity` e `clip-path` à vontade; altura, largura e sombra só
  quando a receita pede, em elemento pequeno.
- **Movimento não é enfeite:** cada receita liga o movimento ao conteúdo da seção (barras que
  crescem para horários, traço que desenha uma marca de "sim"). O mesmo fade em tudo reprova
  (`references/anti-vibe-coding.md`, sinal 2).

Base mínima, comum a todas:

```html
<html lang="pt-BR" class="no-js">
<head>
  <script>document.documentElement.classList.replace('no-js','js')</script>
```

```css
html { scroll-behavior: smooth; }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
```

```js
var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var each = function (lista, f) { Array.prototype.forEach.call(lista, f); };
var io = new IntersectionObserver(function (es) {
  es.forEach(function (e) {
    if (!e.isIntersecting) return;
    e.target.classList.add('visivel');
    io.unobserve(e.target);
  });
}, { threshold: 0.18, rootMargin: '0px 0px -6% 0px' });
```

Cada receita abaixo lista o que ela observa (`io.observe(...)`). O `demo.html` junta tudo num
script só, com o `else` para navegador sem observador (`classList.add('visivel')` em tudo).

Lista das receitas: abertura-do-topo, paralaxe-da-foto, assinatura-em-tres-estados,
texto-em-linhas, titulo-fixo, revelar-ao-entrar, foto-que-desliza, vagas-que-se-preenchem,
traco-que-se-desenha, faixa-de-figuras, barras-que-crescem, pergunta-que-abre, botao-com-seta,
barra-fixa-do-celular.

---

## Receita: abertura-do-topo

`data-receita`: `abertura-do-topo`. Nome: **Abertura do topo** (entrada em escada e foto que abre).

**Quando usar:** primeira tela de toda página. Título, subtítulo, botão e fatos sobem em escada, e
a foto se abre de cima para baixo.
**Quando NÃO usar:** em seção abaixo da dobra (use `revelar-ao-entrar`); em mais de uma foto por
tela; em foto que é o maior elemento do LCP sem `fetchpriority="high"` (a animação não pode atrasar
a imagem).
**Origem na v7:** `_input.css:408-412` (escada e `abreFoto`), `_heroi.html:20-31`.

```html
<h1 class="abertura-entra">Título da página</h1>
<p class="abre abertura-entra d1">Subtítulo.</p>
<div class="acoes abertura-entra d2"><a class="botao" href="#x">Botão</a></div>
<ul class="fatos abertura-entra d3"><li>Fato curto</li></ul>
<figure class="abertura-foto"><div class="cena-quadro"><img src="foto.webp" alt="..." width="780" height="780" fetchpriority="high"></div></figure>
```

```css
.js .abertura-entra { opacity: 0; transform: translateY(22px); animation: sobe .9s cubic-bezier(.2,.8,.2,1) forwards; }
.js .abertura-entra.d1 { animation-delay: .12s; } .js .abertura-entra.d2 { animation-delay: .26s; } .js .abertura-entra.d3 { animation-delay: .4s; }
.js .abertura-foto .cena-quadro { animation: abreFoto 1.3s cubic-bezier(.2,.8,.2,1) both; }
@keyframes sobe { to { opacity: 1; transform: none; } }
@keyframes abreFoto { from { clip-path: inset(0 0 100% 0); } to { clip-path: inset(0 0 0 0); } }
```

Sem JS: roda só com CSS, na carga (não precisa de observador). Atrasos: 0, 0,12, 0,26 e 0,4 s.
**Reserva:** sem script o `.js` nunca liga e tudo aparece parado. Movimento reduzido:
`.js .abertura-entra { opacity: 1; transform: none; animation: none; }` e
`.js .abertura-foto .cena-quadro { clip-path: none; animation: none; }`.
**Custo no celular:** baixo (`opacity`, `transform` e `clip-path` só na carga). Em celular fraco,
o `clip-path` de 1,3 s sobre foto grande é o item mais caro: se travar, use só a escada.

---

## Receita: paralaxe-da-foto

`data-receita`: `paralaxe-da-foto`. Nome: **Paralaxe da foto**.

**Quando usar:** foto grande no topo ou no meio, para dar profundidade com a rolagem.
**Quando NÃO usar:** em foto de pessoa com texto por cima; em mais de uma foto por tela; no
celular fraco com várias imagens (corte pelo `matchMedia`).
**Origem na v7:** `_app.js:207-221`. A v7 usa `scrollY * 0.1` porque a foto está no topo; aqui a
conta é pela distância ao centro da tela, para valer em qualquer seção, com um limite para o
quadro nunca mostrar fundo.

```html
<div class="paralaxe-quadro"><img src="foto.webp" alt="..." data-paralaxe></div>
```

```css
.paralaxe-quadro { overflow: hidden; border-radius: 22px; aspect-ratio: 16 / 10; }
.paralaxe-quadro img { width: 100%; height: 100%; object-fit: cover; will-change: transform; }
```

```js
var fotoPar = document.querySelector('[data-paralaxe]'), pedido = false;
function quadro() {
  pedido = false;
  if (fotoPar && !reduz) {
    var r = fotoPar.parentNode.getBoundingClientRect(), d = window.innerHeight / 2 - (r.top + r.height / 2);
    var lim = r.height * 0.03, desloc = Math.max(-lim, Math.min(lim, -d * 0.1));
    fotoPar.style.transform = 'translate3d(0,' + desloc.toFixed(1) + 'px,0) scale(1.06)';
  }
}
function aoRolar() { if (!pedido) { pedido = true; window.requestAnimationFrame(quadro); } }
window.addEventListener('scroll', aoRolar, { passive: true });
if (fotoPar && !reduz) fotoPar.style.transform = 'scale(1.06)';
quadro();
```

Contínua, presa à rolagem: 10% do deslocamento, escala 1,06 (a v7 grava `scale(1.06)` já na
carga).
**Reserva:** sem script a foto fica parada e sem escala. Movimento reduzido: o script não mexe
(`!reduz`).
**Custo no celular:** médio. Um `scroll` com `requestAnimationFrame` e `translate3d` (composto
na GPU). Um só alvo por página.

---

## Receita: assinatura-em-tres-estados

`data-receita`: `assinatura-em-tres-estados`. Nome: **Assinatura em três estados**.

**Quando usar:** quando o plano declara o Momento assinatura (um elemento do assunto em 3 ou mais
seções). Estado 1: as peças entram uma a uma e ficam tortas. Estado 2: a coluna fixa se alinha
peça a peça com a rolagem, a região acende, o marco do passo ativa e a linha enche. Estado 3: ao
entrar no fecho, ela se alinha sozinha em 2,0 s.
**Quando NÃO usar:** se o assunto não tem um objeto que muda de estado (não invente: use outra
receita); por cima de foto de pessoa (fica AO LADO); em mais de uma assinatura por página.
**Origem na v7:** `_app.js:8-14, 30, 44` (estado 1), `55-66, 93-116` (estado 2), `231-239`
(estado 3); `_input.css:104-109, 116-117, 173, 180-181, 200, 371`. Na v7 as peças eram vértebras
montadas pelo script; aqui elas já vêm no HTML (`data-dx`, `data-rot`, `data-cy`), então a página
sem script mostra a pilha, e o script só inclina e alinha.

```html
<svg class="coluna entra-pecas" data-coluna="rolagem" viewBox="0 0 120 232" role="img" aria-label="...">
  <polyline class="fio" points=""/>
  <g class="peca" data-dx="6.23" data-rot="15.26" data-cy="11.5"><g class="peca-dentro" style="--i:0"><rect x="43" y="6" width="34" height="11" rx="4.6"/></g></g>
  <!-- uma .peca por peça; data-dx e data-rot são o desvio e a inclinação do estado torto -->
</svg>
<ol class="passos"><li class="passo"><span class="marco"></span><h3>Passo</h3><p>Texto.</p></li></ol>
```

```css
.assin-coluna { position: sticky; top: calc(var(--vh, 1vh) * 12); height: calc(var(--vh, 1vh) * 70); }
.coluna .peca rect { fill: #33403a; stroke: #a9bcb0; stroke-width: 1.2; transition: fill .45s ease; }
.coluna .peca.alinhada rect { fill: var(--verde); }
.coluna .fio { fill: none; stroke: #a9bcb0; stroke-width: 1.4; stroke-dasharray: 2 5; opacity: .7; }
.peca-dentro { transform-box: fill-box; transform-origin: center; }
.js .coluna.entra-pecas .peca-dentro { opacity: 0; }
.js .coluna.entra-pecas.visivel .peca-dentro { animation: pecaEntra .7s cubic-bezier(.2,.8,.2,1) forwards; animation-delay: calc(.45s + var(--i) * .05s); }
@keyframes pecaEntra { from { opacity: 0; transform: translateY(-14px); } to { opacity: 1; transform: none; } }
.passos::before { content: ""; position: absolute; left: 7px; top: 14px; width: 1.5px; height: var(--altura-linha, 0px); background: rgba(216,227,220,.25); }
.passos::after { content: ""; position: absolute; left: 7px; top: 14px; width: 1.5px; background: var(--claro); height: calc(var(--altura-linha, 0px) * var(--enche, 0)); }
.passo .marco { transition: background-color .4s ease, border-color .4s ease, transform .4s ease; }
.passo.ativo .marco { background: var(--claro); border-color: var(--claro); transform: scale(1.15); }
```

```js
function montar(svg) {
  var grupos = [];
  each(svg.querySelectorAll('.peca'), function (g) {
    grupos.push({ g: g, cy: parseFloat(g.getAttribute('data-cy')), dx: parseFloat(g.getAttribute('data-dx')), rot: parseFloat(g.getAttribute('data-rot')) });
  });
  return { svg: svg, grupos: grupos, fio: svg.querySelector('.fio') };
}
function aplicar(c, p) { // p de 0 (torto) a 1 (alinhado)
  var n = c.grupos.length, pts = [];
  c.grupos.forEach(function (o, i) {
    var local = Math.min(1, Math.max(0, (p * (n + 2.2) - i) / 2.2));
    var e = 1 - Math.pow(1 - local, 3);
    var dx = o.dx * (1 - e), r = o.rot * (1 - e);
    o.g.setAttribute('transform', 'translate(' + dx.toFixed(2) + ' 0) rotate(' + r.toFixed(2) + ' 60 ' + o.cy.toFixed(1) + ')');
    if (local >= 1) o.g.classList.add('alinhada'); else o.g.classList.remove('alinhada');
    pts.push((60 + dx).toFixed(2) + ',' + o.cy.toFixed(1));
  });
  c.fio.setAttribute('points', pts.join(' '));
}
// Estado 2: presa à rolagem dos passos
var passos = document.querySelector('.passos'), listaPassos = passos.querySelectorAll('.passo');
function progressoAssinatura() {
  var vh = window.innerHeight, p = 1;
  if (!reduz) { var r = passos.getBoundingClientRect(); p = Math.min(1, Math.max(0, (vh * 0.62 - r.top) / Math.max(1, r.height - vh * 0.3))); }
  aplicar(colunas.rolagem, p);
  passos.style.setProperty('--enche', p.toFixed(3));
  each(listaPassos, function (s) { if (reduz || s.getBoundingClientRect().top < vh * 0.62) s.classList.add('ativo'); else s.classList.remove('ativo'); });
}
// Altura da linha: até o centro do último marco
var marcos = passos.querySelectorAll('.marco'), ultimo = marcos[marcos.length - 1];
passos.style.setProperty('--altura-linha', Math.max(0, ultimo.offsetTop + ultimo.parentNode.offsetTop - 14) + 'px');
// A medida depende da fonte: refaça quando ela chegar (o mesmo defeito do texto em linhas)
if (document.fonts) document.fonts.ready.then(function () { /* repita as duas linhas acima e chame quadro() */ });
// Estado 3: ao entrar na tela, alinha sozinha em 2,0 s (curva 1 - (1 - k)^2)
function alinharSozinha(col) {
  if (!col || reduz) return;
  var t0 = null;
  var passo = function (ts) { if (!t0) t0 = ts; var k = Math.min(1, (ts - t0) / 2000); aplicar(col, 1 - Math.pow(1 - k, 2)); if (k < 1) window.requestAnimationFrame(passo); };
  window.requestAnimationFrame(passo);
}
// Chame progressoAssinatura() dentro do quadro() da rolagem, io.observe(svg.entra-pecas) e io.observe(bloco do estado 3)
```

**Reserva:** sem script a pilha aparece alinhada e sem inclinação (as peças estão no HTML) e a
linha do tempo fica vazia, o que não esconde texto. Movimento reduzido: `progressoAssinatura`
aplica `p = 1` (tudo alinhado, todo passo ativo) e o estado 3 não anima.
**Custo no celular:** médio a alto: 14 `setAttribute` por quadro de rolagem e 25 na v7. Ganho
barato: atualizar só quando `p` mudou mais de 0,002, e manter menos de 30 peças.

---

## Receita: texto-em-linhas

`data-receita`: `texto-em-linhas`. Nome: **Texto em linhas**.

**Quando usar:** título e frase de destaque (até 9 elementos por página), para cada linha subir
na sua vez. Já documentada em `references/texto-em-linhas.md` (regras de quebra e gate).
**Quando NÃO usar:** em parágrafo longo; em texto que o `gate-texto.mjs` não consegue medir;
dentro de `li > span` sem o CSS do arquivo de regras.
**Cuidado (defeito medido na v7, 06/10/2026):** o script da v7 dividia o texto uma vez, antes de a
fonte da página chegar, e nunca media de novo. Em 1440 px, em 3 cargas seguidas, o item "Você parou
a academia porque doeu, e ficou com medo de voltar." saía em 3 trechos, mas o primeiro ("Você parou
a academia porque") não cabia nos 515 px reais e quebrava de novo, deixando "porque" sozinho numa
linha. A receita abaixo corrige: (1) divide de novo quando a fonte termina de carregar
(`document.fonts.ready` e o evento `loadingdone`); (2) divide de novo quando a LARGURA do elemento
muda (`ResizeObserver`, com espera de 150 ms), restaurando o texto original antes de medir; (3)
confere que cada trecho gerado tem uma linha visual só e, se não tem, divide mais uma vez e, em
último caso, volta ao texto inteiro sem movimento. A prova é o `scripts/test-linhas.cjs`
(vermelho com o código da v7, verde com este) em 1440, 390 e 360 px.
**Origem na v7:** `_app.js:118-147`, `_input.css:333-334`.

```html
<h2 data-linhas>Título que quebra em duas ou três linhas.</h2>
<ul data-escada>
  <li class="revela"><strong data-linhas>Frase em destaque.</strong><span>Apoio.</span></li>
</ul>
```

```css
.js [data-linhas].dividido .linha { display: block; opacity: 0; transform: translateY(.45em); clip-path: inset(0 0 100% 0); transition: opacity .7s ease, transform .95s cubic-bezier(.2,.8,.2,1), clip-path .95s cubic-bezier(.2,.8,.2,1); transition-delay: var(--d, 0s); }
.js [data-linhas].dividido.visivel .linha { opacity: 1; transform: none; clip-path: inset(-10% 0 -25% 0); }
```

```js
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var nos = Array.prototype.slice.call(document.querySelectorAll('[data-linhas]'));
  var originais = [], larguras = [], tempo = null;
  function linhasVisuais(el) {
    var r = document.createRange(), tops = [];
    r.selectNodeContents(el);
    Array.prototype.forEach.call(r.getClientRects(), function (c) { if (c.width > 0 && !tops.some(function (t) { return Math.abs(t - c.top) < 4; })) tops.push(c.top); });
    return tops.length;
  }
  function dividir(n, k) {
    if (originais[k] === undefined) originais[k] = n.textContent.trim();
    n.classList.remove('dividido');
    n.textContent = '';
    var palavras = originais[k].split(/\s+/), spans = [];
    palavras.forEach(function (w, i) { var sp = document.createElement('span'); sp.textContent = w; n.appendChild(sp); spans.push(sp); if (i < palavras.length - 1) n.appendChild(document.createTextNode(' ')); });
    var grupos = [], topo = null;
    spans.forEach(function (sp) { var t = sp.offsetTop; if (topo === null || Math.abs(t - topo) > 4) { grupos.push([]); topo = t; } grupos[grupos.length - 1].push(sp.textContent); });
    n.textContent = '';
    var item = n.closest('[data-escada] > *'), base = item ? Array.prototype.indexOf.call(item.parentNode.children, item) * 0.45 : 0;
    grupos.forEach(function (g, i) {
      var l = document.createElement('span'); l.className = 'linha';
      l.textContent = g.join(' '); l.style.setProperty('--d', (base + i * 0.14) + 's');
      n.appendChild(l); if (i < grupos.length - 1) n.appendChild(document.createTextNode(' '));
    });
    n.classList.add('dividido');
  }
  function cabe(n) { return Array.prototype.every.call(n.querySelectorAll('.linha'), function (l) { return linhasVisuais(l) === 1; }); }
  function dividirTodas() {
    nos.forEach(function (n, k) {
      var visivel = n.classList.contains('visivel');
      dividir(n, k);
      if (!cabe(n)) dividir(n, k);
      if (!cabe(n)) { n.classList.remove('dividido'); n.textContent = originais[k]; }
      if (visivel) n.classList.add('visivel');
      larguras[k] = n.offsetWidth;
    });
  }
  function agendar() { clearTimeout(tempo); tempo = setTimeout(dividirTodas, 150); }
  dividirTodas();
  if (document.fonts) {
    document.fonts.ready.then(dividirTodas);
    document.fonts.addEventListener('loadingdone', agendar);
  }
  if (window.ResizeObserver) {
    var ro = new ResizeObserver(function () { if (nos.some(function (n, k) { return n.offsetWidth !== larguras[k]; })) agendar(); });
    nos.forEach(function (n) { ro.observe(n); });
  } else window.addEventListener('resize', agendar);
})();
```

Duração 0,95 s por linha, 0,14 s entre linhas, 0,45 s entre itens da lista.
**Reserva:** sem script e com movimento reduzido o texto nunca é dividido, então o `.dividido`
(que esconde) nunca existe. Texto inteiro, no lugar, sem movimento.
**Custo no celular:** baixo depois de dividido; a divisão mede `offsetTop` de cada palavra
(reflow), então roda na carga, quando a fonte chega e quando a largura muda, nunca a cada rolagem.

---

## Receita: titulo-fixo

`data-receita`: `titulo-fixo`. Nome: **Título fixo** (sticky).

**Quando usar:** em tela larga, seção com título curto ao lado de uma lista longa: o título fica
preso enquanto os itens passam.
**Quando NÃO usar:** no celular (coluna única, sem fixo); dentro de grid que termina depois do
bloco de largura total (o título nunca solta). Regras e medidas em
`references/sticky-e-sobreposicao.md`.
**Origem na v7:** `_input.css:135`.

```html
<div class="fixo-grade"><h2>Título</h2><ul class="fixo-lista"><li>Item</li></ul></div>
```

```css
@media (min-width: 1024px) {
  .fixo-grade { display: grid; grid-template-columns: 4fr 7fr; gap: 64px; }
  .fixo-grade h2 { position: sticky; top: calc(var(--vh, 1vh) * 15); align-self: start; }
}
```

Sem JS e sem duração. Usa `--vh` medido (`references/vh-estavel.md`).
**Reserva:** sem script o `top` cai em `1vh` se `--vh` não existir (declare o valor padrão como
no exemplo); é CSS puro. Movimento reduzido não muda nada: não há movimento próprio.
**Custo no celular:** nenhum (nem roda abaixo de 1024 px).

---

## Receita: revelar-ao-entrar

`data-receita`: `revelar-ao-entrar`. Nome: **Revelar ao entrar** (a base de todas).

**Quando usar:** cartão, passo, pergunta, parágrafo-chave: cada item sobe e aparece quando ELE
entra na tela. É a revelação comum da v7 (24 elementos). Itens vizinhos podem ter atraso
(`transition-delay`) para virar escada, com no máximo 0,9 s.
**Quando NÃO usar:** como único movimento da página, em tudo igual e sem ligação com o conteúdo
(é o defeito do sinal 2 do `anti-vibe-coding.md`); em elemento acima da dobra (use
`abertura-do-topo`).
**Origem na v7:** `_input.css:404, 437-438`, `_app.js:223-243`.

```html
<ul><li class="revela">Item</li><li class="revela">Item</li></ul>
```

```css
.js .revela { opacity: 0; transform: translateY(26px); transition: opacity .8s ease, transform .8s cubic-bezier(.2,.8,.2,1); }
.js .revela.visivel { opacity: 1; transform: none; }
.js .dor-lista li.revela:nth-child(2) { transition-delay: .45s; }
```

```js
each(document.querySelectorAll('.revela'), function (n) { io.observe(n); });
// sem IntersectionObserver: each(document.querySelectorAll('.revela'), function (n) { n.classList.add('visivel'); });
```

**Reserva:** sem script nada fica escondido (`.js`). Movimento reduzido:
`.js .revela { opacity: 1; transform: none; transition: none; }`.
**Custo no celular:** baixo; 24 elementos no observador custam pouco.

---

## Receita: foto-que-desliza

`data-receita`: `foto-que-desliza`. Nome: **Foto que desliza**.

**Quando usar:** foto no meio da página (a diferença do serviço, a pessoa): o quadro abre 12% de
baixo para cima, a imagem assenta de 1,08 a 1 e o bloco sobe 30 px.
**Quando NÃO usar:** na foto do topo (use `abertura-do-topo`); em mais de duas fotos por página.
**Origem na v7:** `_input.css:344-347, 406-407`.

```html
<figure class="arco revela-foto desliza"><div class="quadro"><img src="foto.webp" alt="..." loading="lazy"></div><figcaption>Legenda</figcaption></figure>
```

```css
.js .desliza { transform: translateY(30px); transition: transform 1.1s cubic-bezier(.2,.8,.2,1); }
.js .desliza.visivel { transform: none; }
.js .revela-foto img { transform: scale(1.08); transition: transform 1.6s cubic-bezier(.2,.8,.2,1); }
.js .revela-foto.visivel img { transform: none; }
.js .revela-foto .quadro { clip-path: inset(12% 0 0 0); transition: clip-path 1.1s cubic-bezier(.2,.8,.2,1); }
.js .revela-foto.visivel .quadro { clip-path: inset(0 0 0 0); }
```

```js
each(document.querySelectorAll('.revela-foto'), function (n) { io.observe(n); });
```

Durações: 1,1 s (quadro e bloco) e 1,6 s (imagem).
**Reserva:** sem script a foto aparece inteira. Movimento reduzido:
`.js .revela-foto .quadro { clip-path: none; transition: none; }` e
`.js .revela-foto img, .js .desliza { transform: none; transition: none; }`.
**Custo no celular:** médio: `clip-path` e `transform` na mesma foto. Em foto grande, escolha um
dos dois.

---

## Receita: vagas-que-se-preenchem

`data-receita`: `vagas-que-se-preenchem`. Nome: **Vagas que se preenchem**.

**Quando usar:** quando há um número pequeno e real (vagas da turma, passos do método, pessoas por
grupo): as marcas se preenchem uma a uma e o número pulsa no fim. O número do texto TEM que ser o
mesmo da quantidade de marcas.
**Quando NÃO usar:** com número inventado ou que muda (contador falso é o sinal 1 do
`anti-vibe-coding.md`); com mais de 8 marcas.
**Origem na v7:** `_app.js:169-180`, `_input.css:338-340, 453-454`.

```html
<p data-vagas>Até <span class="contador" data-contador>4</span> pessoas por turma.</p>
<div class="vagas" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
```

```css
.vagas { display: flex; gap: 10px; margin-top: 24px; }
.vagas i { width: 46px; height: 14px; border-radius: 7px; border: 1.5px solid var(--verde); background: transparent; transition: background-color .35s ease, transform .35s ease; }
.vagas i.cheia, .no-js .vagas i { background: var(--verde); }
.vagas i.cheia { transform: scaleY(1.15); }
.contador { display: inline-block; }
.contador.pulsa { animation: pulsa .7s cubic-bezier(.2,.8,.2,1); color: var(--verde); transition: color .6s ease; }
@keyframes pulsa { 0% { transform: scale(1); } 40% { transform: scale(1.22); } 100% { transform: scale(1); } }
```

```js
function contar(h) {
  var alvo = h.querySelector('[data-contador]'), vagas = document.querySelectorAll('.vagas i');
  if (reduz) { each(vagas, function (v) { v.classList.add('cheia'); }); return; }
  var n = 0;
  var tick = function () {
    if (vagas[n]) vagas[n].classList.add('cheia');
    n += 1;
    if (n < vagas.length) setTimeout(tick, 300); else if (alvo) { alvo.classList.add('pulsa'); }
  };
  setTimeout(tick, 250);
}
// no observador: if (e.target.hasAttribute('data-vagas')) contar(e.target);   e   io.observe(o título com data-vagas)
```

300 ms entre marcas, pulso de 0,7 s.
**Reserva:** `.no-js .vagas i` pinta todas as marcas cheias. Movimento reduzido: `contar` enche
tudo de uma vez e `.contador.pulsa { animation: none; }`.
**Custo no celular:** baixo.

---

## Receita: traco-que-se-desenha

`data-receita`: `traco-que-se-desenha`. Nome: **Traço que se desenha**.

**Quando usar:** marca de "sim" (check) em lista de itens e contorno de foto que se traça: o
`stroke-dashoffset` vai ao zero em escada de 0,2 s entre itens.
**Quando NÃO usar:** em ícone de biblioteca padrão (o `gate-composicao.mjs` reprova); em lista
longa (mais de 6 marcas).
**Origem na v7:** `_input.css:157-158, 364-367, 349-352`.

```html
<ul class="marcas"><li><svg viewBox="0 0 24 24" fill="none" stroke="#4f7a63" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path class="traco" d="M4 12l5 5 11-12"/></svg>Item.</li></ul>
<div class="contorno"><svg class="arco-traco" viewBox="0 0 100 125" preserveAspectRatio="none" aria-hidden="true"><path d="M2 125 V50 A48 48 0 0 1 98 50 V110 Q98 123 85 123 H15" pathLength="1" fill="none" stroke="#4f7a63" stroke-width="1.5" vector-effect="non-scaling-stroke"/></svg></div>
```

```css
.marcas .traco { stroke-dasharray: 30; stroke-dashoffset: 30; transition: stroke-dashoffset .7s ease; }
.marcas li:nth-child(2) .traco { transition-delay: .2s; } .marcas li:nth-child(3) .traco { transition-delay: .4s; } .marcas li:nth-child(4) .traco { transition-delay: .6s; }
.marcas.visivel .traco, .no-js .marcas .traco { stroke-dashoffset: 0; }
.arco-traco path { stroke-dasharray: 1; stroke-dashoffset: 0; }
.js .contorno .arco-traco path { stroke-dashoffset: 1; transition: stroke-dashoffset 1.8s cubic-bezier(.4,.1,.2,1) .3s; }
.js .contorno.visivel .arco-traco path { stroke-dashoffset: 0; }
```

```js
each(document.querySelectorAll('.marcas, .contorno'), function (n) { io.observe(n); });
```

Atenção: o escondido do traço (`stroke-dashoffset: 30`) fica sem `.js` na v7, com a reserva
`.no-js`; copie as duas linhas juntas.
**Reserva:** `.no-js .marcas .traco { stroke-dashoffset: 0; }` e, no contorno, o `.js` (só
escondido com script). Movimento reduzido: `.marcas .traco { stroke-dashoffset: 0; transition: none; }`.
**Custo no celular:** baixo.

---

## Receita: faixa-de-figuras

`data-receita`: `faixa-de-figuras`. Nome: **Faixa de figuras**.

**Quando usar:** 3 a 6 fotos de aparelhos, ambientes ou produtos. Cada figura sobe 48 px com
escala 0,97, com 0,16 s entre elas. No celular vira carrossel com `scroll-snap` e pontos que
acompanham a rolagem lateral.
**Quando NÃO usar:** com mais de 6 figuras; se a página já tem outro carrossel na mesma tela.
**Origem na v7:** `_input.css:356-359`, `_app.js:159-167`.

```html
<div class="faixa" data-faixa tabindex="0" aria-label="Fotos, role para o lado">
  <figure class="revela-lado"><img src="a.webp" alt="..." loading="lazy"><figcaption>Legenda</figcaption></figure>
</div>
<div class="faixa-pontos" aria-hidden="true"><i class="ativo"></i><i></i><i></i></div>
```

```css
.faixa { display: flex; gap: 16px; overflow-x: auto; scroll-snap-type: x mandatory; }
.faixa figure { flex: none; width: min(72vw, 280px); scroll-snap-align: start; }
.faixa-pontos i { width: 22px; height: 4px; border-radius: 2px; background: rgba(79,122,99,.3); transition: background-color .3s ease, width .3s ease; }
.faixa-pontos i.ativo { background: var(--verde); width: 40px; }
@media (min-width: 1024px) { .faixa { overflow: visible; } .faixa figure { flex: 1 1 0; width: auto; } .faixa-pontos { display: none; } }
.js .revela-lado { opacity: 0; transform: translateY(48px) scale(.97); transition: opacity .9s ease, transform 1.1s cubic-bezier(.2,.8,.2,1); transition-delay: var(--d, 0s); }
.js .revela-lado.visivel { opacity: 1; transform: none; }
```

```js
each(document.querySelectorAll('.faixa .revela-lado'), function (f, i) { f.style.setProperty('--d', (i * 0.16) + 's'); });
var faixa = document.querySelector('[data-faixa]'), pontos = document.querySelectorAll('.faixa-pontos i');
faixa.addEventListener('scroll', function () {
  var figs = faixa.querySelectorAll('figure'), melhor = 0, menor = 1e9, base = faixa.getBoundingClientRect().left;
  each(figs, function (f, i) { var d = Math.abs(f.getBoundingClientRect().left - base - 16); if (d < menor) { menor = d; melhor = i; } });
  each(pontos, function (pt, i) { pt.classList.toggle('ativo', i === melhor); });
}, { passive: true });
// observe a faixa; ao entrar, marque cada .revela-lado com visivel
```

**Reserva:** sem script as figuras aparecem. Movimento reduzido: `.js .revela-lado { transform: none; opacity: 1; transition: none; }`.
**Custo no celular:** médio: várias fotos animando juntas; use `loading="lazy"` e fotos de até
780 px.

---

## Receita: barras-que-crescem

`data-receita`: `barras-que-crescem`. Nome: **Barras que crescem**.

**Quando usar:** quadro de horários, de preços por faixa ou de comparação em que a largura
significa algo (as horas abertas por dia). Cresce da esquerda em 0,9 s.
**Quando NÃO usar:** barra sem dado real por trás (enfeite); em gráfico com mais de 8 linhas.
**Origem na v7:** `_input.css:262-264`.

```html
<div class="quadro-horas"><dl class="qh-linhas"><div class="qh-linha"><dt>Seg</dt><dd><i style="left:0%;width:50%"></i></dd></div></dl></div>
```

```css
.qh-linha dd i { position: absolute; top: 3px; bottom: 3px; border-radius: 5px; background: var(--verde); transform-origin: left center; transition: transform .9s cubic-bezier(.2,.8,.2,1); }
.js .quadro-horas:not(.visivel) .qh-linha dd i { transform: scaleX(0); }
```

```js
each(document.querySelectorAll('.quadro-horas'), function (n) { io.observe(n); });
```

**Reserva:** sem script as barras aparecem cheias (o escondido só existe com `.js`). Movimento
reduzido: `.js .quadro-horas:not(.visivel) .qh-linha dd i { transform: none; }`.
**Custo no celular:** baixo (`scaleX`, não largura).

---

## Receita: pergunta-que-abre

`data-receita`: `pergunta-que-abre`. Nome: **Pergunta que abre**.

**Quando usar:** FAQ com `details`. A resposta abre em 420 ms e fecha em 320 ms, com altura e
opacidade pela API de animação, e o ícone de mais gira 45 graus.
**Quando NÃO usar:** em acordeão com conteúdo interativo pesado dentro (formulário); em
`details` sem `summary` clicável.
**Origem na v7:** `_app.js:182-197`, `_input.css:289-290`.

```html
<details><summary>Pergunta?<svg viewBox="0 0 26 26" aria-hidden="true"><path d="M13 6v14M6 13h14" stroke="#4f7a63" stroke-width="1.8" stroke-linecap="round"/></svg></summary><div class="resposta"><p>Resposta.</p></div></details>
```

```css
.faq summary svg { transition: transform .35s ease; }
.faq details[open] summary svg { transform: rotate(45deg); }
.faq .resposta { overflow: hidden; }
```

```js
each(document.querySelectorAll('.faq details'), function (d) {
  var sum = d.querySelector('summary'), resp = d.querySelector('.resposta');
  sum.addEventListener('click', function (e) {
    if (reduz || !resp.animate) return;
    e.preventDefault();
    if (d.open) {
      var h = resp.offsetHeight;
      var a = resp.animate([{ height: h + 'px', opacity: 1 }, { height: '0px', opacity: 0 }], { duration: 320, easing: 'cubic-bezier(.4,0,.2,1)' });
      a.onfinish = function () { d.open = false; };
    } else {
      d.open = true;
      var alt = resp.offsetHeight;
      resp.animate([{ height: '0px', opacity: 0 }, { height: alt + 'px', opacity: 1 }], { duration: 420, easing: 'cubic-bezier(.2,.8,.2,1)' });
    }
  });
});
```

**Reserva:** sem script o `details` abre e fecha do jeito nativo, sem animação. Movimento
reduzido: o script sai logo (`if (reduz ...) return`) e vale o nativo; `.faq summary svg { transition: none; }`.
**Custo no celular:** baixo (animação de altura em um elemento por vez).

---

## Receita: botao-com-seta

`data-receita`: `botao-com-seta`. Nome: **Botão com seta**.

**Quando usar:** todo botão principal. Ao passar o mouse ou focar, sobe 2 px, ganha sombra e a seta
anda 4 px.
**Quando NÃO usar:** com brilho colorido, levitar exagerado ou rotação (sinais V9 e V12 do
`anti-vibe-coding.md`).
**Origem na v7:** `_input.css:33-38`.

```html
<a href="#x" class="botao">Rótulo <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 10h12M11 5l5 5-5 5"/></svg></a>
```

```css
.botao { transition: background-color .25s ease, transform .25s ease, box-shadow .25s ease; box-shadow: 0 1px 0 rgba(31,38,34,.2); }
.botao svg { width: 20px; height: 20px; transition: transform .3s cubic-bezier(.2,.8,.2,1); }
.botao:hover, .botao:focus-visible { background: #3a4a41; transform: translateY(-2px); box-shadow: 0 10px 24px -12px rgba(31,38,34,.55); }
.botao:hover svg, .botao:focus-visible svg { transform: translateX(4px); }
@media (prefers-reduced-motion: reduce) { .botao, .botao svg { transition: none; } }
```

Sem JS. 0,25 s no botão, 0,3 s na seta.
**Reserva:** CSS puro; sem script funciona igual. Movimento reduzido: sem transição.
**Custo no celular:** nenhum no toque (o `:hover` quase não dispara).

---

## Receita: barra-fixa-do-celular

`data-receita`: `barra-fixa-do-celular`. Nome: **Barra fixa do celular**.

**Quando usar:** página com ação única (agendar, comprar) em celular: depois que o topo sai da
tela, e enquanto nenhum botão da página está à vista, a barra entra de baixo em 0,35 s.
**Quando NÃO usar:** com botão no cabeçalho ao mesmo tempo (nunca os dois); com mais de 15% da
tela fixa em 390 e 320.
**Origem na v7:** `_app.js:199-206`, `_input.css:326-328`. Em página real acrescente
`@media (min-width: 768px) { .barra { display: none; } }`; no demo ela aparece em tela larga só
para a prova.

```html
<div class="barra" data-barra><a href="#x" class="botao">Rótulo</a></div>
```

```css
.barra { position: fixed; left: 0; right: 0; bottom: 0; z-index: 50; padding: 10px 16px calc(10px + env(safe-area-inset-bottom)); transform: translateY(110%); visibility: hidden; transition: none; }
.barra.mostra { transform: none; visibility: visible; transition: transform .35s ease, visibility 0s; }
```

```js
var barra = document.querySelector('[data-barra]'), topo = document.querySelector('#topo section');
var botoesPagina = document.querySelectorAll('main .botao');
function barraFixa() {
  var vh = window.innerHeight, passou = topo.getBoundingClientRect().bottom < 0, algum = false;
  each(botoesPagina, function (bt) { var r = bt.getBoundingClientRect(); if (r.bottom > 0 && r.top < vh + 40) algum = true; });
  if (passou && !algum) barra.classList.add('mostra'); else barra.classList.remove('mostra');
}
// chame barraFixa() dentro do quadro() da rolagem
```

**Reserva:** sem script a barra fica escondida (`visibility: hidden`) e a página usa os botões do
corpo. Movimento reduzido: `.barra { transition: none; }` (aparece sem deslizar).
**Custo no celular:** baixo; lê a posição de poucos botões por quadro.
