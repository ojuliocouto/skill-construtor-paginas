# Checklist Mobile Detalhado

70%+ do trafego de infoprodutos brasileiros vem de mobile (principalmente Instagram e WhatsApp). Uma pagina que falha no mobile falha na maioria dos visitantes.

---

## CRITICO: Verificar no Dispositivo Real (ou DevTools 375px)

Abrir DevTools → Toggle Device Toolbar → iPhone SE (375px) como referencia base. Verificar cada item abaixo.

---

## BLOCO 1: Acima do Fold (375px)

- [ ] **CTA visivel sem scroll**: o botao de acao principal esta visivel na primeira tela sem precisar rolar
- [ ] **H1 legivel**: tamanho minimo 32px no mobile, idealmente 36-44px
- [ ] **Subheadline legivel**: minimo 16px, maximo 2-3 linhas no mobile
- [ ] **Imagem hero nao bloqueia o texto**: no mobile a imagem vai para baixo do texto (nao ao lado)
- [ ] **Spacing adequado do topo**: se tiver navbar fixa, conteudo nao fica colado na navbar

---

## BLOCO 2: Tipografia e Legibilidade

- [ ] **Body text ≥ 16px**: abaixo de 16px o iOS faz zoom automatico no formulario
- [ ] **Line-height body ≥ 1.6**: texto apertado e dificil de ler em tela pequena
- [ ] **Paragrafos curtos**: maximo 4-5 linhas por paragrafo no mobile
- [ ] **Sem texto em mais de 90% da largura**: sempre padding horizontal minimo de 16-20px
- [ ] **Contraste adequado**: texto principal vs fundo: minimo 4.5:1 (verificar com DevTools)

---

## BLOCO 3: Touch Targets

- [ ] **Botoes ≥ 44px de altura**: regra Apple HIG. Botoes de menos de 44px sao dificeis de tocar
- [ ] **CTA primario full-width no mobile**: botao ocupa 100% da largura disponivel
- [ ] **Links de texto ≥ 44px de area clicavel**: adicionar padding vertical se necessario
- [ ] **Espacamento entre botoes proximos ≥ 8px**: evitar toque acidental
- [ ] **Items de FAQ/accordion ≥ 60px de altura**: cabeca do dedo precisa de espaco

---

## BLOCO 4: Layout e Grid

- [ ] **Zero scroll horizontal**: abrir o DevTools, nenhum elemento vai alem de 375px
- [ ] **Grid colapsa corretamente**: grids de 3-4 colunas viram 1 ou 2 colunas no mobile
- [ ] **Side-by-side vira stacked**: layouts split desktop viram coluna unica no mobile
- [ ] **Imagens responsivas**: nenhuma imagem ultrapassa a largura do viewport
- [ ] **Tabelas responsivas**: se houver tabelas, tem scroll horizontal ou layout alternativo

---

## BLOCO 5: Formularios

- [ ] **Labels visiveis**: formulario sem label visivel confunde usuarios mobile
- [ ] **Altura dos campos ≥ 48px**: facil de tocar
- [ ] **Tipo de input correto:**
  - Email: `type="email"` (abre teclado com @)
  - Telefone: `type="tel"` (abre teclado numerico)
  - Numero: `type="number"` ou `inputmode="numeric"`
- [ ] **Autocomplete habilitado**: `autocomplete="name"`, `autocomplete="email"`, etc.
- [ ] **CTA de submit visivel**: botao de envio nunca fica "embaixo do teclado"
- [ ] **Mensagem de erro legivel**: erros de validacao em font ≥ 14px, cor adequada

---

## BLOCO 6: Navegacao

- [ ] **Hamburger funciona**: menu mobile abre e fecha corretamente
- [ ] **Menu fecha ao clicar fora**: ou ao clicar em link
- [ ] **Links do menu tem area de toque adequada**: ≥ 44px de altura por item
- [ ] **Sem navbar que cobre conteudo**: se navbar e fixed, conteudo tem padding-top adequado
- [ ] **Smooth scroll funciona**: CTAs "ir para secao" scrollam suavemente

---

## BLOCO 7: Performance Mobile

- [ ] **LCP mobile < 2.5s**: verificar com Lighthouse no modo Mobile
- [ ] **Imagens hero nao sao as mesmas do desktop**: usar `srcset` ou `picture` para imagens menores no mobile
- [ ] **Videos com `loading="lazy"`**: nao carregam todos de uma vez
- [ ] **Fontes carregam rapido**: usar `font-display: swap` para nao bloquear render
- [ ] **Sem scripts bloqueantes**: verificar que JS nao bloqueia o render inicial

---

## BLOCO 8: Elementos Especificos do Mercado BR

- [ ] **Botao flutuante de WhatsApp**: presente e posicionado no canto inferior direito (bottom: 80px para nao colidir com navegacao do iOS)
- [ ] **CTAs direcionam para WhatsApp quando relevante**: link `https://wa.me/...`
- [ ] **Countdown timer funciona no mobile**: verificar que relogio aparece e conta corretamente
- [ ] **Videos de depoimento carregam**: verificar embed (YouTube/Vimeo) em mobile
- [ ] **Checkout link funciona**: link para Hotmart/Kiwify abre corretamente

---

## BLOCO 9: iOS/Safari Especificos

- [ ] **Sem `position: fixed` dentro de `overflow: hidden`**: causa bug no Safari iOS
- [ ] **Input font-size ≥ 16px**: previne zoom automatico no Safari
- [ ] **Sem `vh` units para elementos criticos**: usar `dvh` ou `svh` no iOS moderno
- [ ] **`-webkit-tap-highlight-color: transparent`**: remove flash azul/cinza em elementos interativos
- [ ] **Imagens PNG com fundo transparente**: verificar que aparecem correto em modo escuro iOS

---

## BLOCO 10: Animacoes no Mobile

- [ ] **Animacoes reduzidas em `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
- [ ] **Parallax desabilitado no mobile**: parallax causa tontura em mobile e e pesado
- [ ] **Scroll reveal nao e muito agressivo**: `translateY` max 20px no mobile (nao 40px do desktop)

---

## Teste Rapido de 2 Minutos

```bash
# 1. Abrir Chrome DevTools → Device Toolbar → iPhone SE (375px)
# 2. Rolar a pagina inteira, verificar visualmente
# 3. Clicar todos os CTAs
# 4. Preencher o formulario (se houver)
# 5. Abrir o menu hamburger
# 6. Verificar Lighthouse Mobile Score (deve ser ≥ 85 Performance)
```

---

## Score Mobile (integrado ao scoring-system.md)

| Criterio | Nota |
|----------|------|
| CTA acima do fold (375px) | +2 |
| Todos touch targets ≥ 44px | +2 |
| Zero scroll horizontal | +2 |
| LCP mobile < 2.5s | +2 |
| Tipografia correta (≥16px body) | +1 |
| Formulario com tipos corretos | +1 |

**Total maximo: 10/10**
