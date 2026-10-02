# Checklist Mobile Detalhado

70%+ do tráfego de infoprodutos brasileiros vem de mobile (principalmente Instagram e WhatsApp). Uma página que falha no mobile falha na maioria dos visitantes.

---

## CRÍTICO: Verificar no Dispositivo Real (ou DevTools 375px)

Abrir DevTools → Toggle Device Toolbar → iPhone SE (375px) como referência base. Verificar cada item abaixo.

---

## BLOCO 1: Acima do Fold (375px)

- [ ] **CTA visível sem scroll**: o botão de ação principal esta visível na primeira tela sem precisar rolar
- [ ] **H1 legível**: tamanho mínimo 32px no mobile, idealmente 36-44px
- [ ] **Subheadline legível**: mínimo 16px, máximo 2-3 linhas no mobile
- [ ] **Imagem hero não bloqueia o texto**: no mobile a imagem vai para baixo do texto (não ao lado)
- [ ] **Spacing adequado do topo**: se tiver navbar fixa, conteúdo não fica colado na navbar

---

## BLOCO 2: Tipografia e Legibilidade

- [ ] **Body text ≥ 16px**: abaixo de 16px o iOS faz zoom automático no formulário
- [ ] **Line-height body ≥ 1.6**: texto apertado e difícil de ler em tela pequena
- [ ] **Parágrafos curtos**: máximo 4-5 linhas por parágrafo no mobile
- [ ] **Sem texto em mais de 90% da largura**: sempre padding horizontal mínimo de 16-20px
- [ ] **Contraste adequado**: texto principal vs fundo: mínimo 4.5:1 (verificar com DevTools)

---

## BLOCO 3: Touch Targets

- [ ] **Botões ≥ 44px de altura**: regra Apple HIG. Botões de menos de 44px são difíceis de tocar
- [ ] **CTA primário full-width no mobile**: botão ocupa 100% da largura disponível
- [ ] **Links de texto ≥ 44px de área clicável**: adicionar padding vertical se necessário
- [ ] **Espaçamento entre botões próximos ≥ 8px**: evitar toque acidental
- [ ] **Items de FAQ/accordion ≥ 60px de altura**: cabeça do dedo precisa de espaço

---

## BLOCO 4: Layout e Grid

- [ ] **Zero scroll horizontal**: abrir o DevTools, nenhum elemento vai além de 375px
- [ ] **Grid colapsa corretamente**: grids de 3-4 colunas viram 1 ou 2 colunas no mobile
- [ ] **Side-by-side vira stacked**: layouts split desktop viram coluna única no mobile
- [ ] **Imagens responsivas**: nenhuma imagem ultrapassa a largura do viewport
- [ ] **Tabelas responsivas**: se houver tabelas, tem scroll horizontal ou layout alternativo

---

## BLOCO 5: Formulários

- [ ] **Labels visíveis**: formulário sem label visível confunde usuários mobile
- [ ] **Altura dos campos ≥ 48px**: fácil de tocar
- [ ] **Tipo de input correto:**
  - Email: `type="email"` (abre teclado com @)
  - Telefone: `type="tel"` (abre teclado numérico)
  - Número: `type="number"` ou `inputmode="numeric"`
- [ ] **Autocomplete habilitado**: `autocomplete="name"`, `autocomplete="email"`, etc.
- [ ] **CTA de submit visível**: botão de envio nunca fica "embaixo do teclado"
- [ ] **Mensagem de erro legível**: erros de validação em font ≥ 14px, cor adequada

---

## BLOCO 6: Navegação

- [ ] **Hamburger funciona**: menu mobile abre e fecha corretamente
- [ ] **Menu fecha ao clicar fora**: ou ao clicar em link
- [ ] **Links do menu tem área de toque adequada**: ≥ 44px de altura por item
- [ ] **Sem navbar que cobre conteúdo**: se navbar e fixed, conteúdo tem padding-top adequado
- [ ] **Smooth scroll funciona**: CTAs "ir para seção" scrollam suavemente

---

## BLOCO 7: Performance Mobile

- [ ] **LCP mobile < 2.5s**: verificar com Lighthouse no modo Mobile
- [ ] **Imagens hero não são as mesmas do desktop**: usar `srcset` ou `picture` para imagens menores no mobile
- [ ] **Vídeos com `loading="lazy"`**: não carregam todos de uma vez
- [ ] **Fontes carregam rápido**: usar `font-display: swap` para não bloquear render
- [ ] **Sem scripts bloqueantes**: verificar que JS não bloqueia o render inicial

---

## BLOCO 8: Elementos Específicos do Mercado BR

- [ ] **Botão flutuante de WhatsApp**: presente e posicionado no canto inferior direito (bottom: 80px para não colidir com navegação do iOS)
- [ ] **CTAs direcionam para WhatsApp quando relevante**: link `https://wa.me/...`
- [ ] **Countdown timer funciona no mobile**: verificar que relógio aparece e conta corretamente
- [ ] **Vídeos de depoimento carregam**: verificar embed (YouTube/Vimeo) em mobile
- [ ] **Checkout link funciona**: link para Hotmart/Kiwify abre corretamente

---

## BLOCO 9: iOS/Safari Específicos

- [ ] **Sem `position: fixed` dentro de `overflow: hidden`**: causa bug no Safari iOS
- [ ] **Input font-size ≥ 16px**: previne zoom automático no Safari
- [ ] **Sem `vh` units para elementos críticos**: usar `dvh` ou `svh` no iOS moderno
- [ ] **`-webkit-tap-highlight-color: transparent`**: remove flash azul/cinza em elementos interativos
- [ ] **Imagens PNG com fundo transparente**: verificar que aparecem correto em modo escuro iOS

---

## BLOCO 10: Animações no Mobile

- [ ] **Animações reduzidas em `prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
- [ ] **Parallax desabilitado no mobile**: parallax causa tontura em mobile e e pesado
- [ ] **Scroll reveal não é muito agressivo**: `translateY` max 20px no mobile (não 40px do desktop)

---

## Teste Rápido de 2 Minutos

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

| Critério | Nota |
|----------|------|
| CTA acima do fold (375px) | +2 |
| Todos touch targets ≥ 44px | +2 |
| Zero scroll horizontal | +2 |
| LCP mobile < 2.5s | +2 |
| Tipografia correta (≥16px body) | +1 |
| Formulário com tipos corretos | +1 |

**Total máximo: 10/10**
