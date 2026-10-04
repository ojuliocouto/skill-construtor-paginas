# Elemento fixo (sticky) não divide o grid com bloco de largura total

Na v7, o título fixo da seção da dor vivia no mesmo grid da frase de impacto em largura total.
Ao rolar, o título passava por cima da frase. O auditor achou (crítico) e o `gate-oclusao.mjs`
não pegou, porque mede a página parada.

## A regra

O elemento `position: sticky` vive num grid que TERMINA antes do próximo bloco de largura
total. A frase de impacto, a faixa e o fecho ficam fora desse grid, em irmão dele.

```html
<section>
  <div class="grade"><h2 class="fixo">Título</h2><ul>...</ul></div>
  <p class="impacto">Frase em largura total.</p>
</section>
```

Errado: `.impacto` como terceiro filho de `.grade`, com `grid-column: 1 / -1`. O sticky anda
dentro da área do grid inteira, e essa área inclui a linha da frase.

## Como medir

Varredura de rolagem em 1024, 1280, 1440 e 1920, medindo a interseção entre o fixo e o bloco:

`node <dir-da-skill>/scripts/sobreposicao.mjs --url http://localhost:8765/ --fixo "#titulo-dor" --contra ".dor-fecho"`

Sai com 1 se alguma tela passar de 0 px². `--contra` aceita vários seletores separados por vírgula
e `--telas 1024x768,1440x900` troca as telas. Rode para cada elemento fixo da página.
