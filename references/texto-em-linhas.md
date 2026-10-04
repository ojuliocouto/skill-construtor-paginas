# Texto dividido em linhas: compatível com o gate-texto

A revelação linha por linha (o título sobe uma linha depois da outra) divide o texto em
`span`s por JavaScript. Duas armadilhas da v7 custaram retrabalho.

## 1. A linha é texto direto, dentro de um contêiner de frase

Marque o contêiner com `data-linhas` e deixe o script pôr o texto direto no elemento da linha,
sem `span` interno, e só dentro de `h1`, `h2`, `strong` ou `p`. Se a divisão cair numa lista, o
`gate-texto.mjs` lê cada linha como um item que começa com minúscula e reprova.

```html
<h2 data-linhas>A dor nas costas costuma chegar assim.</h2>
```

**Como medir:** o `gate-texto.mjs` passa com a divisão em linhas ligada, rodado sobre a `dist/`
servida (não sobre o HTML cru, que ainda não tem as linhas).

## 2. `li > span`, nunca `li span`

Em CSS, quando um script injeta `span`s, o seletor de descendente genérico `li span` pega também
as linhas injetadas e quebra a divisão em palavras. Use o filho direto:

```css
.dor-lista li > span { display: block; }
```

**Como medir:** depois da divisão, conte as linhas por título. Uma frase de 10 palavras que
sai em 10 linhas reprova (aconteceu duas vezes na v7).

```js
[...document.querySelectorAll('[data-linhas]')].map((n) => [n.textContent.trim().split(/\s+/).length, n.children.length])
```

Compare palavras e linhas por título: linhas perto do número de palavras é divisão quebrada.
