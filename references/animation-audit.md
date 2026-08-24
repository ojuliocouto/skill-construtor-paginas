# Protocolo de Auditoria de Animacoes

Animacoes corretas aumentam conversao e percepção de qualidade. Animacoes erradas distraem, causam tontura e prejudicam performance. Este protocolo define como verificar se as animacoes de uma pagina estao corretas.

---

## Principios Fundamentais

**Animacoes servem o conteudo, nao o oposto.**
Se uma animacao chama mais atencao do que o elemento que ela anima, ela esta errada.

**Regra dos 3 propositos:**
Toda animacao deve ter um dos 3 propositos:
1. **Guiar o olhar** (scroll reveal direciona para onde olhar)
2. **Comunicar estado** (hover = interativo, loading = aguarde)
3. **Refletir personalidade da marca** (suave = premium, energetico = jovem)

---

## AUDITORIA DE SCROLL REVEAL

### Checklist por secao

Para cada secao da pagina, verificar:

- [ ] **Entrada da secao:** Tem scroll reveal? (fade + translateY)
- [ ] **Cards/grid:** Cada card entra com stagger? (0.07-0.1s entre cada)
- [ ] **Texto + imagem side-by-side:** Entram separados (texto de um lado, imagem do outro)?
- [ ] **Headlines de secao:** Entram antes dos elementos filhos?
- [ ] **Numeros/stats:** NumberTicker animado (nao so aparece estatico)?

### Configuracao padrao de scroll reveal

```tsx
// PADRAO APROVADO, usar em todos os elementos de entrada
const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.21, 0.47, 0.32, 0.98] } }
}

// Para containers com stagger em filhos
const container = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.08, delayChildren: 0.1 } }
}

// Sempre usar viewport={{ once: true }} para nao repetir ao rolar de volta
<motion.div
  variants={container}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, margin: "-100px" }}
>
```

### O que verificar na pratica

| Elemento | Deve ter | Como verificar |
|----------|----------|----------------|
| Hero headline | Stagger: badge → headline → sub → CTA | Recarregar pagina, observar sequencia |
| Stats/numeros | NumberTicker contando de 0 ao valor | Scroll ate a secao, ver contador |
| Cards 3-col | Entrada em stagger (0.07s) | Scroll devagar, cards devem entrar um apos o outro |
| Imagem hero | Fade + leve translateX ou scale | Recarregar, imagem nao deve "pular" |
| Secao CTA | Entrance animado com delay | Scroll ate o fim, CTA deve ter entrada |
| Depoimentos | Stagger no grid | Scroll devagar, cards de depoimento em cascata |

---

## AUDITORIA DE HOVER STATES

### Todo elemento interativo DEVE ter hover state

| Elemento | Hover esperado | Como verificar |
|----------|---------------|----------------|
| Botoes primarios | Scale 1.02 + brightness ou translateY -2px | Hover lento sobre o botao |
| Botoes secundarios/outline | Fundo preenche ou borda intensifica | Hover sobre botao outline |
| Cards clicaveis | Scale 1.02 + shadow + border-color | Hover sobre card |
| Links de navegacao | Cor muda + underline slide-in | Hover sobre link de nav |
| FAQ accordion | Fundo muda levemente | Hover sobre item de FAQ |
| Logos (marquee) | Grayscale → colorido | Hover sobre logo |
| Imagens com overlay | Overlay aparece ou imagem escala | Hover sobre imagem |
| Icones | Cor muda + leve scale | Hover sobre icone |

### Timing correto de hover

```css
/* CORRETO: rapido o suficiente para parecer responsivo */
transition: all 0.2s ease-out;  /* para scale e color */
transition: all 0.3s ease-out;  /* para shadows e backgrounds */

/* ERRADO: muito lento (parece quebrado) */
transition: all 0.8s ease;

/* ERRADO: sem transicao (jarring) */
/* nenhuma propriedade transition */
```

---

## AUDITORIA DE EFEITOS CONTINUOS

### Animacoes que rodam em loop

| Efeito | Quando usar | Configuracao correta |
|--------|-------------|---------------------|
| Marquee de logos | Logo wall | Velocidade uniforme, pausa no hover |
| Marquee de depoimentos | Grid de testimonials | Dupla fila (cima normal, baixo reverse) |
| Orbiting circles | Hero visual tecnico | duration 15-25s, sem bounce |
| Blob animation | Hero background | duration 7-10s, very slow |
| Float suave | Elemento decorativo | translateY de -10px a +10px, 3-4s |
| Gradient animado | Background premium | Shift lento de posicao, 8-12s |

### Verificar performance de loops

```
TESTE: Abrir DevTools → Performance → gravar 5s com scroll
BUSCAR: animacoes que causam "layout shift" ou "paint storm"
APROVADO: GPU layers apenas (transform, opacity)
REPROVADO: animacoes que movem layout (width, height, top, left, fora de transform)
```

---

## AUDITORIA DO HERO ENTRANCE

O hero e a primeira coisa vista. A animacao de entrada deve ser:
- Rapida (completa em < 1s)
- Sequencial (elementos entram um apos o outro, nao tudo junto)
- Suave (ease-out, nao bounce ou spring agressivo)

### Sequencia ideal de entrada do hero

```
0ms     - Pagina carrega, tudo invisivel
0-200ms - Badge/label aparece (fade + scale)
100-400ms - Headline entra (fade + translateY)
200-500ms - Subheadline entra (fade + translateY, delay 100ms apos headline)
300-600ms - CTA aparece (fade + translateY)
400-700ms - Social proof micro (avatar stack, numero) aparece
500-900ms - Elemento visual (foto, mockup) entra (fade + leve scale ou translateX)
600ms+  - Background effects aparecem (aurora, blobs, particles)
```

### Framer Motion: Hero entrance correto

```tsx
const heroVariants = {
  badge:    { hidden: { opacity: 0, scale: 0.8 }, visible: { opacity: 1, scale: 1, transition: { duration: 0.3, delay: 0.1 } } },
  headline: { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5, delay: 0.2, ease: [0.21,0.47,0.32,0.98] } } },
  sub:      { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5, delay: 0.35 } } },
  cta:      { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4, delay: 0.5 } } },
  image:    { hidden: { opacity: 0, x: 30 }, visible: { opacity: 1, x: 0, transition: { duration: 0.6, delay: 0.3, ease: "easeOut" } } },
}
```

---

## AUDITORIA DE CONSISTENCIA

### Easing consistente

Toda a pagina deve usar a mesma curva de easing como "assinatura visual":

| Tipo de marca | Easing recomendado | Sensacao |
|--------------|-------------------|----------|
| Premium/Luxury | `[0.21, 0.47, 0.32, 0.98]` | Suave, refinado |
| Energia/Desafio | `[0.34, 1.56, 0.64, 1]` (leve spring) | Vivo, dinamico |
| Corporativo/SaaS | `easeOut` | Limpo, profissional |
| Pessoal/Intimo | `easeInOut` | Calmo, acolhedor |

**PROIBIDO:** misturar easings opostos (spring em alguns elementos, linear em outros).

### Duration consistente

| Tipo de animacao | Duration recomendada |
|-----------------|---------------------|
| Micro-interacao (hover) | 0.15-0.25s |
| Entrada de elemento | 0.4-0.6s |
| Stagger entre filhos | 0.07-0.1s |
| Transicao de pagina | 0.3-0.4s |
| Loop continuo | 3s+ |

---

## CHECKLIST FINAL DE ANIMACOES

Antes de entregar, verificar item por item:

**Scroll Reveal:**
- [ ] Hero tem sequencia de entrada animada
- [ ] Todas as secoes tem scroll reveal (nenhuma secao "aparece" estaticamente)
- [ ] Cards em grid tem stagger
- [ ] Numeros/stats tem NumberTicker ou counter animado

**Hover States:**
- [ ] Todos os botoes tem hover (scale ou translateY)
- [ ] Todos os cards clicaveis tem hover
- [ ] Links de navegacao tem hover
- [ ] FAQ items tem hover
- [ ] Logos tem hover (grayscale → color)

**Performance:**
- [ ] Nenhuma animacao usa propriedades que causam reflow (width, height, top, left)
- [ ] will-change aplicado apenas onde necessario
- [ ] Animacoes de loop nao causam paint storm
- [ ] Mobile: animacoes reduzidas ou desativadas via `prefers-reduced-motion`

**Consistencia:**
- [ ] Mesmo easing em todos os elementos de entrada
- [ ] Duration dentro dos ranges recomendados
- [ ] Animacoes de heranca de marca (premium = suave, energia = dinamico)

**Nao distrai:**
- [ ] Nenhuma animacao compete com o CTA principal
- [ ] Background animations tem opacidade adequada (nao distraem do texto)
- [ ] Loops nao sao rapidos demais (causam tontura)
