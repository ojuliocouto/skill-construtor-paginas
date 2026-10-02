# Protocolo de Auditoria de Animações

Animações corretas aumentam conversão e percepção de qualidade. Animações erradas distraem, causam tontura e prejudicam performance. Este protocolo define como verificar se as animações de uma página estão corretas.

---

## Princípios Fundamentais

**Animações servem o conteúdo, não o oposto.**
Se uma animação chama mais atenção do que o elemento que ela anima, ela está errada.

**Regra dos 3 propósitos:**
Toda animação deve ter um dos 3 propósitos:
1. **Guiar o olhar** (scroll reveal direciona para onde olhar)
2. **Comunicar estado** (hover = interativo, loading = aguarde)
3. **Refletir personalidade da marca** (suave = premium, energético = jovem)

---

## AUDITORIA DE SCROLL REVEAL

### Checklist por seção

Para cada seção da página, verificar:

- [ ] **Entrada da seção:** Tem scroll reveal? (fade + translateY)
- [ ] **Cards/grid:** Cada card entra com stagger? (0.07-0.1s entre cada)
- [ ] **Texto + imagem side-by-side:** Entram separados (texto de um lado, imagem do outro)?
- [ ] **Headlines de seção:** Entram antes dos elementos filhos?
- [ ] **Numeros/stats:** NumberTicker animado (não só aparece estático)?

### Configuração padrão de scroll reveal

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

### O que verificar na prática

| Elemento | Deve ter | Como verificar |
|----------|----------|----------------|
| Hero headline | Stagger: badge → headline → sub → CTA | Recarregar página, observar sequência |
| Stats/numeros | NumberTicker contando de 0 ao valor | Scroll até a seção, ver contador |
| Cards 3-col | Entrada em stagger (0.07s) | Scroll devagar, cards devem entrar um após o outro |
| Imagem hero | Fade + leve translateX ou scale | Recarregar, imagem não deve "pular" |
| Seção CTA | Entrance animado com delay | Scroll até o fim, CTA deve ter entrada |
| Depoimentos | Stagger no grid | Scroll devagar, cards de depoimento em cascata |

---

## AUDITORIA DE HOVER STATES

### Todo elemento interativo DEVE ter hover state

| Elemento | Hover esperado | Como verificar |
|----------|---------------|----------------|
| Botões primários | Scale 1.02 + brightness ou translateY -2px | Hover lento sobre o botão |
| Botões secundarios/outline | Fundo preenche ou borda intensifica | Hover sobre botão outline |
| Cards clicáveis | Scale 1.02 + shadow + border-color | Hover sobre card |
| Links de navegação | Cor muda + underline slide-in | Hover sobre link de nav |
| FAQ accordion | Fundo muda levemente | Hover sobre item de FAQ |
| Logos (marquee) | Grayscale → colorido | Hover sobre logo |
| Imagens com overlay | Overlay aparece ou imagem escala | Hover sobre imagem |
| Ícones | Cor muda + leve scale | Hover sobre ícone |

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

## AUDITORIA DE EFEITOS CONTÍNUOS

### Animações que rodam em loop

| Efeito | Quando usar | Configuração correta |
|--------|-------------|---------------------|
| Marquee de logos | Logo wall | Velocidade uniforme, pausa no hover |
| Marquee de depoimentos | Grid de testimonials | Dupla fila (cima normal, baixo reverse) |
| Orbiting circles | Hero visual técnico | duration 15-25s, sem bounce |
| Blob animation | Hero background | duration 7-10s, very slow |
| Float suave | Elemento decorativo | translateY de -10px a +10px, 3-4s |
| Gradient animado | Background premium | Shift lento de posição, 8-12s |

### Verificar performance de loops

```
TESTE: Abrir DevTools → Performance → gravar 5s com scroll
BUSCAR: animações que causam "layout shift" ou "paint storm"
APROVADO: GPU layers apenas (transform, opacity)
REPROVADO: animações que movem layout (width, height, top, left, fora de transform)
```

---

## AUDITORIA DO HERO ENTRANCE

O hero e a primeira coisa vista. A animação de entrada deve ser:
- Rápida (completa em < 1s)
- Sequencial (elementos entram um após o outro, não tudo junto)
- Suave (ease-out, não bounce ou spring agressivo)

### Sequência ideal de entrada do hero

```
0ms     - Página carrega, tudo invisível
0-200ms - Badge/label aparece (fade + scale)
100-400ms - Headline entra (fade + translateY)
200-500ms - Subheadline entra (fade + translateY, delay 100ms após headline)
300-600ms - CTA aparece (fade + translateY)
400-700ms - Social proof micro (avatar stack, número) aparece
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

## AUDITORIA DE CONSISTÊNCIA

### Easing consistente

Toda a página deve usar a mesma curva de easing como "assinatura visual":

| Tipo de marca | Easing recomendado | Sensação |
|--------------|-------------------|----------|
| Premium/Luxury | `[0.21, 0.47, 0.32, 0.98]` | Suave, refinado |
| Energia/Desafio | `[0.34, 1.56, 0.64, 1]` (leve spring) | Vivo, dinâmico |
| Corporativo/SaaS | `easeOut` | Limpo, profissional |
| Pessoal/Intimo | `easeInOut` | Calmo, acolhedor |

**PROIBIDO:** misturar easings opostos (spring em alguns elementos, linear em outros).

### Duration consistente

| Tipo de animação | Duration recomendada |
|-----------------|---------------------|
| Micro-interacao (hover) | 0.15-0.25s |
| Entrada de elemento | 0.4-0.6s |
| Stagger entre filhos | 0.07-0.1s |
| Transição de página | 0.3-0.4s |
| Loop contínuo | 3s+ |

---

## CHECKLIST FINAL DE ANIMAÇÕES

Antes de entregar, verificar item por item:

**Scroll Reveal:**
- [ ] Hero tem sequência de entrada animada
- [ ] Todas as seções tem scroll reveal (nenhuma seção "aparece" estaticamente)
- [ ] Cards em grid tem stagger
- [ ] Numeros/stats tem NumberTicker ou counter animado

**Hover States:**
- [ ] Todos os botões tem hover (scale ou translateY)
- [ ] Todos os cards clicáveis tem hover
- [ ] Links de navegação tem hover
- [ ] FAQ items tem hover
- [ ] Logos tem hover (grayscale → color)

**Performance:**
- [ ] Nenhuma animação usa propriedades que causam reflow (width, height, top, left)
- [ ] will-change aplicado apenas onde necessário
- [ ] Animações de loop não causam paint storm
- [ ] Mobile: animações reduzidas ou desativadas via `prefers-reduced-motion`

**Consistência:**
- [ ] Mesmo easing em todos os elementos de entrada
- [ ] Duration dentro dos ranges recomendados
- [ ] Animações de herança de marca (premium = suave, energia = dinâmico)

**Não distrai:**
- [ ] Nenhuma animação compete com o CTA principal
- [ ] Background animations tem opacidade adequada (não distraem do texto)
- [ ] Loops não são rápidos demais (causam tontura)
