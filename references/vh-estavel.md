# vh estável: altura de layout medida, não esticada

Altura em `vh` que dimensiona o layout (herói, coluna fixa, passos) muda quando o navegador
mexe na janela. Dois casos reais da v7:

1. No celular, a barra de endereço some e volta, e `vh` salta no meio da rolagem.
2. O `fullPage` do Playwright aumenta a janela até a altura da página, e tudo que está em `vh`
   estica: o topo ganhou uma faixa vazia e os passos dobraram de altura no print.

## A regra

A altura de layout em `vh` vira uma variável `--vh` medida no carregamento e recalculada só
quando a LARGURA muda. O CSS usa `calc(var(--vh, 1vh) * 100)` em vez de `100vh`.

```html
<script>
(function () {
  var largura = 0;
  function medir() {
    if (window.innerWidth === largura) return;
    largura = window.innerWidth;
    document.documentElement.style.setProperty('--vh', window.innerHeight / 100 + 'px');
  }
  medir();
  window.addEventListener('resize', medir);
})();
</script>
```

```css
.heroi { min-height: calc(var(--vh, 1vh) * 100); }
.coluna-fixa { position: sticky; top: calc(var(--vh, 1vh) * 12); height: calc(var(--vh, 1vh) * 76); }
```

O script vai sem comentário (`gate-publicacao.py` reprova comentário interno na `dist/`).

## Como medir

O mesmo elemento tem a mesma altura no print de viewport e no de página inteira. O script de
print desliga `scroll-behavior: smooth` antes de rolar; sem isso o `scrollTo(0,0)` para no meio
(scrollY de 29). `screenshot-prova.js` já faz as duas coisas.
