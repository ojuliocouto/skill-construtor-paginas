# Efeitos Avançados: Catálogo de Código Copy-Paste


> **ATENCAO (anti-vibe):** varios efeitos deste arquivo (glow em botao, border glow, aurora, floating orbs, gradiente indigo+roxo) sao tells VISUAIS de IA (V1-V15 de `anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Usar apenas quando o usuario pedir explicitamente esse look. Nos exemplos abaixo, trocar as cores hardcoded pela paleta REAL do projeto (CSS vars) e preferir micro-interacao sobria no CTA (mudanca de tom + elevacao sutil).
Efeitos que transformam páginas funcionais em páginas **fodas**. Todos testados, todos copy-paste ready.

---

## Índice

1. [3D Card Tilt (Framer Motion Springs)](#1-3d-card-tilt)
2. [Text Scramble (Embaralhamento de caracteres)](#2-text-scramble)
3. [Magnetic Cursor](#3-magnetic-cursor)
4. [Animated Gradient Border (@property CSS)](#4-animated-gradient-border)
5. [Noise Texture (SVG data URI)](#5-noise-texture)
6. [SVG Blob Morphing](#6-svg-blob-morphing)
7. [Confetti no CTA](#7-confetti-no-cta)
8. [CSS Scroll-Timeline (nativo, sem JS)](#8-css-scroll-timeline)
9. [Aurora Background](#9-aurora-background)
10. [Glassmorphism com Spotlight](#10-glassmorphism-com-spotlight)
11. [Typing Effect com Cursor Piscando](#11-typing-effect-com-cursor-piscando)
12. [Parallax Multicamada](#12-parallax-multicamada)
13. [Hover Reveal (imagem aparece ao hover)](#13-hover-reveal)
14. [Counter Animado com Easing Custom](#14-counter-animado)
15. [Floating Orbs Animados (CSS puro)](#15-floating-orbs)

---

## Regras de Uso

| Situação | Usar | Não usar |
|----------|------|----------|
| Cards de features/planos | 3D Tilt + Spotlight | Blob morphing |
| Hero headline | Text Scramble + Blur Reveal | Magnetic cursor |
| CTA principal | Confetti + Magnetic | Noise texture |
| Seção escura de fundo | Aurora + Floating Orbs | Gradient border |
| Cards de depoimentos | Glassmorphism | 3D Tilt |
| Seções de stats | Counter Animado | Confetti |
| Qualquer seção | Noise Texture (sutil) | Tudo junto |

**Regra de ouro:** Máximo **2 efeitos por seção**. Um efeito de fundo + um de interação.

---

## 1. 3D Card Tilt

**Quando usar:** Cards de features, planos de preço, testimonials premium.
**Dependência:** `framer-motion`

```tsx
'use client'
import { useRef, useState } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

interface TiltCardProps {
  children: React.ReactNode
  className?: string
  tiltStrength?: number // 0-20, padrão 10
  glowColor?: string
}

export function TiltCard({
  children,
  className = '',
  tiltStrength = 10,
  glowColor = 'rgba(127,65,249,0.4)'
}: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null)

  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const springConfig = { stiffness: 300, damping: 30, mass: 0.5 }
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [tiltStrength, -tiltStrength]), springConfig)
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-tiltStrength, tiltStrength]), springConfig)

  const glowX = useTransform(x, [-0.5, 0.5], ['0%', '100%'])
  const glowY = useTransform(y, [-0.5, 0.5], ['0%', '100%'])

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    x.set((e.clientX - rect.left) / rect.width - 0.5)
    y.set((e.clientY - rect.top) / rect.height - 0.5)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
        transformPerspective: 1000,
      }}
      className={`relative overflow-hidden ${className}`}
    >
      {/* Glow que segue o mouse */}
      <motion.div
        className="pointer-events-none absolute inset-0 rounded-[inherit] opacity-0 transition-opacity duration-300 group-hover:opacity-100"
        style={{
          background: `radial-gradient(circle at ${glowX} ${glowY}, ${glowColor} 0%, transparent 60%)`,
        }}
      />
      {/* Brilho 3D na borda */}
      <div
        className="pointer-events-none absolute inset-0 rounded-[inherit]"
        style={{
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%, rgba(0,0,0,0.1) 100%)',
        }}
      />
      <div style={{ transform: 'translateZ(20px)' }}>
        {children}
      </div>
    </motion.div>
  )
}

// Uso:
// <TiltCard className="p-8 rounded-2xl bg-gray-900 border border-white/10 group" glowColor="rgba(127,65,249,0.3)">
//   <FeatureContent />
// </TiltCard>
```

---

## 2. Text Scramble

**Quando usar:** Hero headline, títulos de seção importantes, elementos de destaque.
**Dependência:** nenhuma (JavaScript puro)

```tsx
'use client'
import { useEffect, useRef, useState } from 'react'

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%'

interface TextScrambleProps {
  text: string
  className?: string
  trigger?: 'mount' | 'hover' | 'inview'
  duration?: number // ms por caractere, padrão 30
  delay?: number // delay inicial em ms
}

export function TextScramble({
  text,
  className = '',
  trigger = 'mount',
  duration = 30,
  delay = 0,
}: TextScrambleProps) {
  const [displayText, setDisplayText] = useState(trigger === 'mount' ? '' : text)
  const [isScrambling, setIsScrambling] = useState(false)
  const frameRef = useRef<number>(0)

  const scramble = () => {
    if (isScrambling) return
    setIsScrambling(true)

    const totalFrames = text.length * 3 + 20
    let frame = 0

    const animate = () => {
      const progress = frame / totalFrames

      const result = text.split('').map((char, i) => {
        if (char === ' ') return ' '
        const charRevealFrame = (i / text.length) * totalFrames * 0.7
        if (frame >= charRevealFrame + text.length * 2) return char
        return CHARS[Math.floor(Math.random() * CHARS.length)]
      }).join('')

      setDisplayText(result)
      frame++

      if (frame < totalFrames) {
        frameRef.current = requestAnimationFrame(animate)
      } else {
        setDisplayText(text)
        setIsScrambling(false)
      }
    }

    setTimeout(() => {
      frameRef.current = requestAnimationFrame(animate)
    }, delay)
  }

  useEffect(() => {
    if (trigger === 'mount') scramble()
    return () => cancelAnimationFrame(frameRef.current)
  }, [text])

  if (trigger === 'hover') {
    return (
      <span
        className={`cursor-default ${className}`}
        onMouseEnter={scramble}
      >
        {displayText}
      </span>
    )
  }

  return <span className={className}>{displayText}</span>
}

// Versão com IntersectionObserver (trigger='inview')
export function TextScrambleInView({ text, className = '', delay = 0 }: Omit<TextScrambleProps, 'trigger'>) {
  const ref = useRef<HTMLSpanElement>(null)
  const [triggered, setTriggered] = useState(false)
  const [displayText, setDisplayText] = useState(text)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !triggered) {
        setTriggered(true)
      }
    }, { threshold: 0.5 })

    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (!triggered) return

    const totalFrames = text.length * 3 + 20
    let frame = 0
    let raf: number

    const animate = () => {
      const result = text.split('').map((char, i) => {
        if (char === ' ') return ' '
        const reveal = (i / text.length) * totalFrames * 0.7
        if (frame >= reveal + text.length * 2) return char
        return CHARS[Math.floor(Math.random() * CHARS.length)]
      }).join('')

      setDisplayText(result)
      frame++
      if (frame < totalFrames) raf = requestAnimationFrame(animate)
      else setDisplayText(text)
    }

    const t = setTimeout(() => { raf = requestAnimationFrame(animate) }, delay)
    return () => { clearTimeout(t); cancelAnimationFrame(raf) }
  }, [triggered])

  return <span ref={ref} className={className}>{displayText}</span>
}

// Uso:
// <h1 className="text-7xl font-black">
//   <TextScramble text="Automatize Tudo" className="text-white" trigger="mount" delay={300} />
// </h1>
// <h2 onMouseEnter={...}>
//   <TextScramble text="Hover para ativar" trigger="hover" />
// </h2>
```

---

## 3. Magnetic Cursor

**Quando usar:** CTAs principais, botões hero, links importantes. Efeito "wow" que impressiona.
**Dependência:** `framer-motion`

```tsx
'use client'
import { useRef, useState } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'

interface MagneticProps {
  children: React.ReactNode
  strength?: number // 0.3-0.5 para sutil, 0.5-0.8 para forte
  className?: string
}

export function Magnetic({ children, strength = 0.4, className = '' }: MagneticProps) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 200, damping: 15 })
  const springY = useSpring(y, { stiffness: 200, damping: 15 })

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    const cx = rect.left + rect.width / 2
    const cy = rect.top + rect.height / 2
    x.set((e.clientX - cx) * strength)
    y.set((e.clientY - cy) * strength)
  }

  const handleMouseLeave = () => {
    x.set(0)
    y.set(0)
  }

  return (
    <motion.div
      ref={ref}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// Cursor customizado que expande ao hover
export function CustomCursor() {
  const cursorX = useMotionValue(-100)
  const cursorY = useMotionValue(-100)
  const [isHovering, setIsHovering] = useState(false)

  useEffect(() => {
    const move = (e: MouseEvent) => {
      cursorX.set(e.clientX - 16)
      cursorY.set(e.clientY - 16)
    }

    const handleOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      setIsHovering(!!target.closest('a, button, [data-magnetic]'))
    }

    window.addEventListener('mousemove', move)
    window.addEventListener('mouseover', handleOver)
    return () => {
      window.removeEventListener('mousemove', move)
      window.removeEventListener('mouseover', handleOver)
    }
  }, [])

  return (
    <motion.div
      className="pointer-events-none fixed left-0 top-0 z-[9999] rounded-full mix-blend-difference bg-white"
      style={{ x: cursorX, y: cursorY }}
      animate={{
        width: isHovering ? 48 : 32,
        height: isHovering ? 48 : 32,
        x: isHovering ? cursorX.get() - 8 : cursorX.get(),
        y: isHovering ? cursorY.get() - 8 : cursorY.get(),
      }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    />
  )
}

// Uso:
// <Magnetic strength={0.4}>
//   <button className="px-8 py-4 bg-indigo-600 text-white rounded-full font-bold">
//     Começar Agora
//   </button>
// </Magnetic>
//
// No layout root:
// <CustomCursor />
// <style>{`* { cursor: none !important; }`}</style>
```

---

## 4. Animated Gradient Border

**Quando usar:** Cards de destaque, badges premium, CTAs especiais. Efeito de borda rotativa com CSS puro.
**Dependência:** nenhuma (CSS puro, `@property` Chrome 85+)

```css
/* Adicionar ao globals.css */
@property --angle {
  syntax: '<angle>';
  initial-value: 0deg;
  inherits: false;
}

@keyframes borderRotate {
  to { --angle: 360deg; }
}

.gradient-border {
  position: relative;
  border-radius: 16px;
  background: linear-gradient(#0f0f1a, #0f0f1a) padding-box,
    conic-gradient(from var(--angle), #7F41F9, #F94E03, #7F41F9) border-box;
  border: 2px solid transparent;
  animation: borderRotate 3s linear infinite;
}

/* Variante mais sutil (pausa no hover) */
.gradient-border-hover {
  animation: borderRotate 4s linear infinite paused;
}
.gradient-border-hover:hover {
  animation-play-state: running;
}

/* Variante arco-íris */
.gradient-border-rainbow {
  background: linear-gradient(#0f0f1a, #0f0f1a) padding-box,
    conic-gradient(from var(--angle), #f59e0b, #ef4444, #8b5cf6, #06b6d4, #10b981, #f59e0b) border-box;
  border: 2px solid transparent;
  animation: borderRotate 4s linear infinite;
}

/* Versão com glow externo */
.gradient-border-glow {
  position: relative;
}
.gradient-border-glow::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: 20px;
  background: conic-gradient(from var(--angle), #7F41F9, #F94E03, #7F41F9);
  filter: blur(12px);
  opacity: 0.6;
  animation: borderRotate 3s linear infinite;
  z-index: -1;
}
```

```tsx
// Componente React com suporte a fallback
function GradientBorderCard({ children, className = '' }) {
  return (
    <div className={`gradient-border p-6 ${className}`}>
      {children}
    </div>
  )
}

// Uso puro HTML (mais performático):
// <div className="gradient-border p-6 rounded-2xl bg-gray-950">
//   Conteúdo aqui
// </div>
```

### Variante 4b: Border Beam (feixe único viajante)

Validado num clone real (jun/2026), recriando o reel "Gradient Border Effect" do @code_wars_official.
Diferença pra 4 acima: aqui NÃO gira a borda inteira; um **único arco de luz percorre o perímetro**.
Vantagens: (1) funciona sobre QUALQUER elemento sem reestruturar (não usa o truque padding-box/border-box,
usa máscara de anel), então **não tinge o conteúdo nem o bg** do card; (2) cor adaptável à marca via `--beam-c`.

```css
/* @property + keyframes (uma vez no globals) */
@property --beam-angle { syntax: '<angle>'; inherits: false; initial-value: 0deg; }
@keyframes beam-spin { to { --beam-angle: 360deg; } }

.beam { position: relative; }
.beam::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;          /* respeita o raio do elemento (0 = cantos retos) */
  padding: var(--beam-w, 1.6px);   /* espessura do anel */
  background: conic-gradient(
    from var(--beam-angle),
    transparent 0deg 250deg,
    var(--beam-c, #e8132c) 296deg,  /* cor da MARCA, não roxo/ciano genérico */
    #ffffff 320deg,                 /* pico claro = "feixe" */
    var(--beam-c, #e8132c) 344deg,
    transparent 360deg
  );
  /* máscara de anel: mostra só a borda, não o miolo */
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  animation: beam-spin var(--beam-d, 4s) linear infinite;
  pointer-events: none;
}
.beam-light::before {  /* variante p/ superfícies vermelhas/escuras: feixe branco */
  background: conic-gradient(from var(--beam-angle), transparent 0deg 250deg,
    rgba(255,255,255,.4) 296deg, #fff 320deg, rgba(255,255,255,.4) 344deg, transparent 360deg);
}
.beam-hover::before { opacity: 0; transition: opacity .35s ease; }
.beam-hover:hover::before { opacity: 1; }
@media (prefers-reduced-motion: reduce) { .beam::before { animation: none; } }
```

Uso: `class="beam"` (sempre on), `class="beam beam-hover"` (só no hover, ótimo em card de produto),
`class="beam beam-light"` (feixe branco em botão vermelho/escuro). Aplicar em **poucos itens** (CTA
principal, card no hover, 1 botão de destaque), espalhar mata o efeito.

**Gotchas validados:**
- `@property` precisa de Chromium 85+/Safari 16.4+ (Edge ok). Sem ele, animar a CSS var não interpola.
- Anel sutil sobre superfície vermelha (feixe branco 1.6px) fica discreto; em card branco com feixe
  vermelho no hover é onde mais aparece.
- Verificar a render: `getComputedStyle(el, '::before').backgroundImage` deve mostrar `conic-gradient(from <angulo vivo>deg...)` (ângulo mudando = animação ok).

### Variante 4c: Border Glow que SEGUE O CURSOR (o efeito FIEL do reel)

Este é o efeito exato do reel "Gradient Border Effect" do @code_wars_official ("Wherever you go,
the cursor follows. One event listener powers it all"). Diferença pra 4b: o brilho NÃO gira sozinho,
ele **acende a borda na posição do mouse** e acompanha o cursor. UM único listener `mousemove` no
container alimenta TODOS os cards (escalável). É mais "vivo" e premium que o auto-beam.

```jsx
import { useRef } from 'react'

// 1 listener no wrapper atualiza --mx/--my de todos os .glow-card (o "one event listener")
export function GlowGrid({ children, className = '' }) {
  const ref = useRef(null)
  const onMove = (e) => {
    const cards = ref.current?.querySelectorAll('.glow-card')
    if (!cards) return
    for (const card of cards) {
      const r = card.getBoundingClientRect()
      card.style.setProperty('--mx', `${e.clientX - r.left}px`)
      card.style.setProperty('--my', `${e.clientY - r.top}px`)
    }
  }
  return <div ref={ref} onMouseMove={onMove} className={`glow-group ${className}`}>{children}</div>
}
// Uso: <GlowGrid className="grid grid-cols-3 gap-4"> <a className="glow-card ...">...</a> ... </GlowGrid>
```

```css
.glow-card { position: relative; }
/* anel da borda que acende perto do cursor */
.glow-card::before {
  content: '';
  position: absolute; inset: 0;
  border-radius: inherit;
  padding: var(--glow-w, 1.5px);
  background: radial-gradient(
    180px circle at var(--mx, -200px) var(--my, -200px),
    var(--glow-c, #e8132c),   /* cor da MARCA */
    transparent 65%
  );
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  opacity: 0;
  transition: opacity .35s ease;
  pointer-events: none;
  z-index: 5;
}
/* acende quando o mouse está sobre QUALQUER card do grupo (igual ao reel) */
.glow-group:hover .glow-card::before { opacity: 1; }

/* OPCIONAL: spotlight sutil no MIOLO do card seguindo o cursor (camada de luz interna) */
.glow-card::after {
  content: '';
  position: absolute; inset: 0;
  border-radius: inherit;
  background: radial-gradient(220px circle at var(--mx, -200px) var(--my, -200px),
    rgba(232,19,44,.08), transparent 60%);
  opacity: 0; transition: opacity .35s ease; pointer-events: none;
}
.glow-card:hover::after { opacity: 1; }
```

**Quando usar 4b vs 4c:**
- **4c (segue o cursor)** = grid de cards interativo (produtos, planos, features). É o efeito do reel. Mais "wow".
- **4b (auto-beam)** = 1 item de destaque sempre animado (CTA, badge) sem precisar de mouse (mobile também vê).

**Gotchas:** mobile não tem cursor, em telas touch o 4c não acende (ok; usar 4b no CTA pra ter algo no mobile).
O `radial-gradient at var(--mx)` NÃO precisa de `@property` (interpola sozinho). Inicializar `--mx/--my`
fora da tela (`-200px`) pra não acender no canto antes do primeiro mousemove.

---

## 5. Noise Texture

**Quando usar:** Praticamente qualquer background para adicionar profundidade e "material". Sutil mas faz muita diferença.
**Dependência:** nenhuma (SVG data URI inline)

```css
/* globals.css, adicionar ao body ou seções específicas */

/* Noise sutil (mais usado) */
.noise-subtle::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px;
  z-index: 1;
}

/* Noise mais visível (dark sections) */
.noise-medium::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.06;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-size: 256px;
  z-index: 1;
}
```

```tsx
// Componente React, aplica noise em qualquer seção
function NoisySection({ children, className = '', intensity = 'subtle' }: {
  children: React.ReactNode
  className?: string
  intensity?: 'subtle' | 'medium' | 'strong'
}) {
  const opacityMap = { subtle: 0.03, medium: 0.06, strong: 0.1 }
  const opacity = opacityMap[intensity]

  return (
    <div className={`relative ${className}`}>
      {/* Noise layer */}
      <div
        className="pointer-events-none absolute inset-0 z-[1]"
        style={{
          opacity,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
          backgroundRepeat: 'repeat',
          backgroundSize: '200px',
        }}
      />
      <div className="relative z-[2]">{children}</div>
    </div>
  )
}

// Uso:
// <NoisySection className="bg-slate-950 py-24" intensity="medium">
//   <HeroContent />
// </NoisySection>

// Versão Tailwind inline (mais simples):
// <section className="relative bg-slate-950 py-24">
//   <div className="pointer-events-none absolute inset-0 opacity-[0.04]"
//     style={{backgroundImage: `url("data:image/svg+xml,...")`, backgroundSize:'200px'}} />
//   <div className="relative z-10">...</div>
// </section>
```

---

## 6. SVG Blob Morphing

**Quando usar:** Elementos decorativos de hero, backgrounds de destaque. Visual orgânico e premium.
**Dependência:** `framer-motion`

```tsx
'use client'
import { motion } from 'framer-motion'

// Blob que anima entre formas
const blobPaths = [
  "M50,10 C70,5 90,20 85,45 C80,70 65,85 45,80 C25,75 5,60 10,40 C15,20 30,15 50,10Z",
  "M55,8 C75,12 92,30 88,52 C84,74 68,88 48,85 C28,82 8,65 12,42 C16,19 35,4 55,8Z",
  "M45,12 C68,8 88,25 84,50 C80,75 60,90 38,82 C16,74 2,55 8,32 C14,9 22,16 45,12Z",
  "M52,6 C74,10 95,28 90,55 C85,82 65,92 42,88 C19,84 1,62 6,38 C11,14 30,2 52,6Z",
]

interface BlobProps {
  size?: number
  color?: string
  speed?: number // segundos por ciclo
  className?: string
}

export function AnimatedBlob({
  size = 400,
  color = '#7F41F9',
  speed = 8,
  className = ''
}: BlobProps) {
  return (
    <motion.svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
    >
      <motion.path
        d={blobPaths[0]}
        fill={color}
        animate={{ d: [...blobPaths, blobPaths[0]] }}
        transition={{
          duration: speed,
          repeat: Infinity,
          ease: 'easeInOut',
          times: [0, 0.25, 0.5, 0.75, 1],
        }}
      />
    </motion.svg>
  )
}

// Blob com gradiente interno
export function GradientBlob({
  size = 500,
  fromColor = '#7F41F9',
  toColor = '#F94E03',
  speed = 10,
  opacity = 0.4,
  className = ''
}: {
  size?: number
  fromColor?: string
  toColor?: string
  speed?: number
  opacity?: number
  className?: string
}) {
  return (
    <motion.svg
      viewBox="0 0 100 100"
      width={size}
      height={size}
      className={className}
      style={{ opacity }}
    >
      <defs>
        <linearGradient id="blobGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={fromColor} />
          <stop offset="100%" stopColor={toColor} />
        </linearGradient>
      </defs>
      <motion.path
        d={blobPaths[0]}
        fill="url(#blobGrad)"
        animate={{ d: [...blobPaths, blobPaths[0]] }}
        transition={{ duration: speed, repeat: Infinity, ease: 'easeInOut' }}
      />
    </motion.svg>
  )
}

// Uso típico, blob de background no hero:
// <div className="relative overflow-hidden min-h-screen bg-slate-950">
//   <GradientBlob
//     className="absolute -top-20 -left-20 blur-3xl opacity-30"
//     size={600}
//     fromColor="#7F41F9"
//     toColor="#4338CA"
//     speed={12}
//   />
//   <GradientBlob
//     className="absolute -bottom-20 -right-20 blur-3xl opacity-20"
//     size={500}
//     fromColor="#F94E03"
//     toColor="#DC2626"
//     speed={15}
//   />
//   <div className="relative z-10">...</div>
// </div>
```

---

## 7. Confetti no CTA

**Quando usar:** Botão principal de conversão, momento de "parabéns" após formulário.
**Dependência:** `npm install canvas-confetti`

```tsx
'use client'
import { useRef } from 'react'
import confetti from 'canvas-confetti'

interface ConfettiButtonProps {
  children: React.ReactNode
  className?: string
  onClick?: () => void
  variant?: 'burst' | 'shower' | 'stars' | 'side-cannons'
}

export function ConfettiButton({
  children,
  className = '',
  onClick,
  variant = 'burst'
}: ConfettiButtonProps) {
  const buttonRef = useRef<HTMLButtonElement>(null)

  const fire = () => {
    const rect = buttonRef.current?.getBoundingClientRect()
    const originX = rect ? (rect.left + rect.width / 2) / window.innerWidth : 0.5
    const originY = rect ? (rect.top + rect.height / 2) / window.innerHeight : 0.5

    const variants = {
      burst: () => confetti({
        particleCount: 100,
        spread: 70,
        origin: { x: originX, y: originY },
        colors: ['#7F41F9', '#F94E03', '#ffffff', '#a855f7', '#f59e0b'],
        scalar: 1.2,
      }),
      shower: () => {
        const end = Date.now() + 2000
        const interval = setInterval(() => {
          if (Date.now() > end) return clearInterval(interval)
          confetti({
            particleCount: 10,
            angle: 60,
            spread: 55,
            origin: { x: 0 },
            colors: ['#7F41F9', '#F94E03', '#ffffff'],
          })
          confetti({
            particleCount: 10,
            angle: 120,
            spread: 55,
            origin: { x: 1 },
            colors: ['#7F41F9', '#F94E03', '#ffffff'],
          })
        }, 100)
      },
      stars: () => confetti({
        particleCount: 80,
        spread: 360,
        startVelocity: 30,
        shapes: ['star'],
        colors: ['#FFD700', '#FFA500', '#FF6347', '#7F41F9'],
        origin: { x: originX, y: originY },
        scalar: 1.5,
      }),
      'side-cannons': () => {
        confetti({ particleCount: 60, angle: 60, spread: 50, origin: { x: 0, y: 0.6 }, colors: ['#7F41F9', '#fff'] })
        confetti({ particleCount: 60, angle: 120, spread: 50, origin: { x: 1, y: 0.6 }, colors: ['#F94E03', '#fff'] })
      },
    }

    variants[variant]()
    onClick?.()
  }

  return (
    <button ref={buttonRef} onClick={fire} className={className}>
      {children}
    </button>
  )
}

// Uso:
// <ConfettiButton
//   variant="side-cannons"
//   className="px-8 py-4 bg-indigo-600 text-white font-bold rounded-full"
//   onClick={() => router.push('/checkout')}
// >
//   Quero Começar Agora!
// </ConfettiButton>
```

---

## 8. CSS Scroll-Timeline

**Quando usar:** Barras de progresso de leitura, animações que acompanham o scroll.
**Dependência:** nenhuma (CSS nativo, Chrome 115+, Safari 15.4+)

```css
/* globals.css */

/* Barra de progresso de leitura no topo da página */
@keyframes progress {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}

.reading-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, #7F41F9, #F94E03);
  transform-origin: left;
  animation: progress linear;
  animation-timeline: scroll(root);
  z-index: 9999;
}

/* Fade-in de elementos ao entrar na viewport */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(40px); }
  to   { opacity: 1; transform: translateY(0); }
}

.scroll-reveal {
  animation: fadeInUp linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 30%;
}

/* Slide da esquerda */
.scroll-reveal-left {
  animation: slideInLeft linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 25%;
}

@keyframes slideInLeft {
  from { opacity: 0; transform: translateX(-60px); }
  to   { opacity: 1; transform: translateX(0); }
}

/* Scale up */
.scroll-reveal-scale {
  animation: scaleUp linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 20%;
}

@keyframes scaleUp {
  from { opacity: 0; transform: scale(0.85); }
  to   { opacity: 1; transform: scale(1); }
}

/* Stagger em elementos filhos */
.scroll-stagger > *:nth-child(1) { animation-delay: 0ms; }
.scroll-stagger > *:nth-child(2) { animation-delay: 80ms; }
.scroll-stagger > *:nth-child(3) { animation-delay: 160ms; }
.scroll-stagger > *:nth-child(4) { animation-delay: 240ms; }
.scroll-stagger > *:nth-child(5) { animation-delay: 320ms; }
.scroll-stagger > *:nth-child(6) { animation-delay: 400ms; }

/* Fallback para browsers sem suporte */
@supports not (animation-timeline: scroll()) {
  .scroll-reveal,
  .scroll-reveal-left,
  .scroll-reveal-scale {
    opacity: 1;
    transform: none;
  }
}
```

```html
<!-- Barra de progresso de leitura -->
<div class="reading-progress"></div>

<!-- Elementos com scroll reveal nativo -->
<section>
  <div class="scroll-stagger grid grid-cols-3 gap-6">
    <div class="scroll-reveal card">Card 1</div>
    <div class="scroll-reveal card">Card 2</div>
    <div class="scroll-reveal card">Card 3</div>
  </div>
</section>
```

---

## 9. Aurora Background

**Quando usar:** Hero sections premium, seções de CTA finais, dark headers.
**Dependência:** nenhuma (CSS puro)

```css
/* globals.css */

@keyframes aurora1 {
  0%, 100% { transform: translate(0%, 0%) scale(1); opacity: 0.5; }
  33%       { transform: translate(5%, -10%) scale(1.1); opacity: 0.8; }
  66%       { transform: translate(-5%, 5%) scale(0.9); opacity: 0.6; }
}
@keyframes aurora2 {
  0%, 100% { transform: translate(0%, 0%) scale(1.1); opacity: 0.4; }
  33%       { transform: translate(-8%, 12%) scale(0.95); opacity: 0.7; }
  66%       { transform: translate(8%, -8%) scale(1.05); opacity: 0.5; }
}
@keyframes aurora3 {
  0%, 100% { transform: translate(0%, 0%) scale(0.9); opacity: 0.6; }
  50%       { transform: translate(10%, -5%) scale(1.1); opacity: 0.3; }
}

.aurora-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.aurora-bg::before,
.aurora-bg::after,
.aurora-bg .aurora-3 {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.aurora-bg::before {
  width: 60%;
  height: 60%;
  top: -20%;
  left: -10%;
  background: radial-gradient(ellipse, rgba(127,65,249,0.4) 0%, transparent 70%);
  animation: aurora1 15s ease-in-out infinite;
}

.aurora-bg::after {
  width: 50%;
  height: 50%;
  bottom: -20%;
  right: -10%;
  background: radial-gradient(ellipse, rgba(249,78,3,0.3) 0%, transparent 70%);
  animation: aurora2 18s ease-in-out infinite;
}

.aurora-bg .aurora-3 {
  width: 40%;
  height: 40%;
  top: 30%;
  left: 40%;
  background: radial-gradient(ellipse, rgba(99,102,241,0.3) 0%, transparent 70%);
  animation: aurora3 12s ease-in-out infinite;
}
```

```tsx
// Componente React
function AuroraBackground({ children, className = '' }: {
  children: React.ReactNode
  className?: string
}) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div className="aurora-bg" aria-hidden>
        <div className="aurora-3" />
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  )
}

// Uso:
// <AuroraBackground className="min-h-screen bg-slate-950 flex items-center">
//   <HeroContent />
// </AuroraBackground>

// Versão inline (sem CSS global):
// <section className="relative overflow-hidden bg-slate-950">
//   <div className="pointer-events-none absolute -top-32 -left-20 w-[500px] h-[500px] rounded-full
//     bg-purple-600/30 blur-[120px] animate-[aurora1_15s_ease-in-out_infinite]" />
//   <div className="pointer-events-none absolute -bottom-32 -right-20 w-[400px] h-[400px] rounded-full
//     bg-orange-500/20 blur-[120px] animate-[aurora2_18s_ease-in-out_infinite]" />
//   <div className="relative z-10">...</div>
// </section>
```

---

## 10. Glassmorphism com Spotlight

**Quando usar:** Cards de planos/preços, modais, CTAs flutuantes.
**Dependência:** nenhuma

```tsx
'use client'
import { useRef, useState, useCallback } from 'react'

interface GlassSpotlightCardProps {
  children: React.ReactNode
  className?: string
  spotlightColor?: string
  glassColor?: string // rgba
  borderColor?: string
}

export function GlassSpotlightCard({
  children,
  className = '',
  spotlightColor = 'rgba(127,65,249,0.15)',
  glassColor = 'rgba(255,255,255,0.05)',
  borderColor = 'rgba(255,255,255,0.1)',
}: GlassSpotlightCardProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [spotlight, setSpotlight] = useState({ x: 0, y: 0, opacity: 0 })

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    setSpotlight({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      opacity: 1,
    })
  }, [])

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => setSpotlight(s => ({ ...s, opacity: 0 }))}
      className={`relative overflow-hidden rounded-2xl ${className}`}
      style={{
        background: glassColor,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: `1px solid ${borderColor}`,
      }}
    >
      {/* Spotlight */}
      <div
        className="pointer-events-none absolute inset-0 rounded-2xl transition-opacity duration-300"
        style={{
          opacity: spotlight.opacity,
          background: `radial-gradient(400px circle at ${spotlight.x}px ${spotlight.y}px, ${spotlightColor}, transparent 40%)`,
        }}
      />
      {/* Borda gradient sutil */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl"
        style={{ background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, transparent 60%)' }} />
      <div className="relative z-10">{children}</div>
    </div>
  )
}

// Uso:
// <GlassSpotlightCard
//   className="p-8"
//   spotlightColor="rgba(127,65,249,0.2)"
//   glassColor="rgba(15,15,26,0.6)"
// >
//   <PricingContent />
// </GlassSpotlightCard>
```

---

## 11. Typing Effect com Cursor Piscando

**Quando usar:** Subtítulos do hero, chamadas para ação dinâmicas, apresentação de serviços.
**Dependência:** nenhuma

```tsx
'use client'
import { useEffect, useState } from 'react'

interface TypingEffectProps {
  words: string[]
  typingSpeed?: number // ms por caractere
  deletingSpeed?: number
  pauseTime?: number // ms entre palavras
  className?: string
  cursorColor?: string
}

export function TypingEffect({
  words,
  typingSpeed = 100,
  deletingSpeed = 50,
  pauseTime = 2000,
  className = '',
  cursorColor = '#7F41F9',
}: TypingEffectProps) {
  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const [currentText, setCurrentText] = useState('')
  const [isDeleting, setIsDeleting] = useState(false)
  const [isPaused, setIsPaused] = useState(false)

  useEffect(() => {
    if (isPaused) return

    const word = words[currentWordIndex]
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        setCurrentText(word.slice(0, currentText.length + 1))
        if (currentText.length + 1 === word.length) {
          setIsPaused(true)
          setTimeout(() => {
            setIsPaused(false)
            setIsDeleting(true)
          }, pauseTime)
        }
      } else {
        setCurrentText(word.slice(0, currentText.length - 1))
        if (currentText.length === 0) {
          setIsDeleting(false)
          setCurrentWordIndex((i) => (i + 1) % words.length)
        }
      }
    }, isDeleting ? deletingSpeed : typingSpeed)

    return () => clearTimeout(timeout)
  }, [currentText, isDeleting, isPaused, currentWordIndex, words, typingSpeed, deletingSpeed, pauseTime])

  return (
    <span className={className}>
      {currentText}
      <span
        className="animate-[blink_1s_step-end_infinite]"
        style={{ color: cursorColor }}
      >
        |
      </span>
    </span>
  )
}

// CSS necessário:
// @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }

// Uso:
// <h1 className="text-7xl font-black text-white">
//   Automatize{' '}
//   <TypingEffect
//     words={['WhatsApp', 'Instagram', 'E-mail', 'Tudo']}
//     className="text-purple-400"
//     cursorColor="#7F41F9"
//   />
// </h1>
```

---

## 12. Parallax Multicamada

**Quando usar:** Hero sections com múltiplos elementos, seções de produto com profundidade.
**Dependência:** `framer-motion`

```tsx
'use client'
import { useRef } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'

interface ParallaxLayerProps {
  children: React.ReactNode
  speed: number // positivo = mais lento que scroll, negativo = mais rápido
  className?: string
}

export function ParallaxLayer({ children, speed, className = '' }: ParallaxLayerProps) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  })
  const y = useTransform(scrollYProgress, [0, 1], [`${-speed * 50}%`, `${speed * 50}%`])

  return (
    <motion.div ref={ref} style={{ y }} className={className}>
      {children}
    </motion.div>
  )
}

// Hero com múltiplas camadas de parallax
export function ParallaxHero() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-slate-950">
      {/* Camada 1: mais lenta (fundo) */}
      <ParallaxLayer speed={0.5} className="absolute inset-0 flex items-center justify-center">
        <div className="w-[800px] h-[800px] rounded-full bg-purple-600/10 blur-3xl" />
      </ParallaxLayer>

      {/* Camada 2: velocidade normal */}
      <ParallaxLayer speed={0.2} className="absolute top-20 left-20">
        <div className="w-4 h-4 rounded-full bg-purple-500/60" />
      </ParallaxLayer>

      {/* Camada 3: mais rápida (frente) */}
      <ParallaxLayer speed={-0.3} className="absolute bottom-20 right-20">
        <div className="w-8 h-8 rounded-full bg-orange-500/40" />
      </ParallaxLayer>

      {/* Conteúdo principal (sem parallax) */}
      <div className="relative z-10 flex min-h-screen items-center">
        <div className="max-w-4xl mx-auto px-6">
          {/* Hero content */}
        </div>
      </div>
    </section>
  )
}
```

---

## 13. Hover Reveal

**Quando usar:** Cards de portfolio, antes/depois de produto, carrosséis de case study.
**Dependência:** nenhuma ou `framer-motion`

```tsx
'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface HoverRevealCardProps {
  image: string
  hoverImage?: string
  title: string
  description: string
  tag?: string
}

export function HoverRevealCard({ image, hoverImage, title, description, tag }: HoverRevealCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      className="group relative overflow-hidden rounded-2xl cursor-pointer aspect-[4/3]"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Imagem base */}
      <img
        src={image}
        alt={title}
        className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
      />

      {/* Imagem de hover (se fornecida) */}
      {hoverImage && (
        <AnimatePresence>
          {isHovered && (
            <motion.img
              src={hoverImage}
              alt={`${title} hover`}
              className="absolute inset-0 w-full h-full object-cover"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
            />
          )}
        </AnimatePresence>
      )}

      {/* Overlay gradiente sempre presente */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

      {/* Conteúdo que aparece no hover */}
      <AnimatePresence>
        {isHovered && (
          <motion.div
            className="absolute inset-x-0 bottom-0 p-6"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {tag && (
              <span className="inline-block px-3 py-1 rounded-full bg-purple-500/80 text-white text-xs font-semibold mb-2">
                {tag}
              </span>
            )}
            <h3 className="text-xl font-bold text-white mb-1">{title}</h3>
            <p className="text-sm text-gray-300">{description}</p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Conteúdo base (sempre visível) */}
      {!isHovered && (
        <div className="absolute inset-x-0 bottom-0 p-6">
          <h3 className="text-lg font-bold text-white">{title}</h3>
        </div>
      )}
    </motion.div>
  )
}
```

---

## 14. Counter Animado

**Quando usar:** Seções de stats/resultados. Muito mais impactante que números estáticos.
**Dependência:** nenhuma (ou Magic UI `NumberTicker` como alternativa)

```tsx
'use client'
import { useEffect, useRef, useState } from 'react'

interface CounterProps {
  end: number
  start?: number
  duration?: number // ms
  prefix?: string
  suffix?: string
  className?: string
  easing?: 'linear' | 'easeOut' | 'easeInOut'
  decimals?: number
}

function easeOut(t: number) { return 1 - Math.pow(1 - t, 3) }
function easeInOut(t: number) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2 }

export function Counter({
  end,
  start = 0,
  duration = 2000,
  prefix = '',
  suffix = '',
  className = '',
  easing = 'easeOut',
  decimals = 0,
}: CounterProps) {
  const [count, setCount] = useState(start)
  const ref = useRef<HTMLSpanElement>(null)
  const hasStarted = useRef(false)

  useEffect(() => {
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !hasStarted.current) {
        hasStarted.current = true
        const startTime = performance.now()
        const easeFn = easing === 'easeInOut' ? easeInOut : easeOut

        const animate = (currentTime: number) => {
          const elapsed = currentTime - startTime
          const progress = Math.min(elapsed / duration, 1)
          const easedProgress = easeFn(progress)
          setCount(Math.round((start + (end - start) * easedProgress) * 10 ** decimals) / 10 ** decimals)
          if (progress < 1) requestAnimationFrame(animate)
        }

        requestAnimationFrame(animate)
      }
    }, { threshold: 0.5 })

    if (ref.current) observer.observe(ref.current)
    return () => observer.disconnect()
  }, [end, start, duration])

  return (
    <span ref={ref} className={className}>
      {prefix}{count.toFixed(decimals)}{suffix}
    </span>
  )
}

// Uso:
// <div className="grid grid-cols-3 gap-8 text-center">
//   <div>
//     <Counter end={2400} suffix="+" className="text-5xl font-black text-white" />
//     <p className="text-gray-400">Clientes ativos</p>
//   </div>
//   <div>
//     <Counter end={98.7} decimals={1} suffix="%" className="text-5xl font-black text-white" />
//     <p className="text-gray-400">Satisfação</p>
//   </div>
//   <div>
//     <Counter end={150} suffix="ms" className="text-5xl font-black text-white" />
//     <p className="text-gray-400">Tempo médio de resposta</p>
//   </div>
// </div>
```

---

## 15. Floating Orbs

**Quando usar:** Backgrounds de hero dark, seções de destaque. CSS puro, zero dependência.
**Dependência:** nenhuma (CSS puro)

```css
/* globals.css */

@keyframes orbFloat1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25%       { transform: translate(30px, -40px) scale(1.05); }
  50%       { transform: translate(-20px, -20px) scale(0.95); }
  75%       { transform: translate(10px, 30px) scale(1.02); }
}
@keyframes orbFloat2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%       { transform: translate(-40px, 20px) scale(1.08); }
  66%       { transform: translate(20px, -30px) scale(0.92); }
}
@keyframes orbFloat3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  40%       { transform: translate(25px, 35px) scale(1.04); }
  80%       { transform: translate(-15px, -25px) scale(0.96); }
}

.floating-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  pointer-events: none;
}

.orb-1 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(127,65,249,0.35), transparent 70%);
  animation: orbFloat1 20s ease-in-out infinite;
  top: -100px;
  left: -100px;
}

.orb-2 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(249,78,3,0.25), transparent 70%);
  animation: orbFloat2 25s ease-in-out infinite;
  bottom: -80px;
  right: -80px;
}

.orb-3 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(99,102,241,0.3), transparent 70%);
  animation: orbFloat3 18s ease-in-out infinite;
  top: 40%;
  left: 60%;
}

/* Mobile: desabilitar para performance */
@media (max-width: 768px) {
  .floating-orb { display: none; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .floating-orb { animation: none; }
}
```

```tsx
// Componente React
function FloatingOrbs({ colors }: { colors?: [string, string, string] }) {
  const [c1, c2, c3] = colors ?? ['rgba(127,65,249,0.35)', 'rgba(249,78,3,0.25)', 'rgba(99,102,241,0.3)']

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      <div className="floating-orb orb-1" style={{ background: `radial-gradient(circle, ${c1}, transparent 70%)` }} />
      <div className="floating-orb orb-2" style={{ background: `radial-gradient(circle, ${c2}, transparent 70%)` }} />
      <div className="floating-orb orb-3" style={{ background: `radial-gradient(circle, ${c3}, transparent 70%)` }} />
    </div>
  )
}

// Uso:
// <section className="relative min-h-screen bg-slate-950 overflow-hidden">
//   <FloatingOrbs />
//   <div className="relative z-10 max-w-6xl mx-auto px-6">
//     <HeroContent />
//   </div>
// </section>
```

---

## Combinações Recomendadas por Tipo de Página

### Hero Premium Dark
```
FloatingOrbs + AuroraBackground + TextScramble/BlurReveal no título + Magnetic no CTA
```

### Cards de Features
```
TiltCard + GlassSpotlightCard + ScrollReveal (Framer Motion)
```

### Seção de Stats
```
Counter + NoiseTexture no background + ScrollTimeline fade-in
```

### Planos / Pricing
```
GradientBorder no plano destaque + GlassSpotlightCard + ConfettiButton no CTA
```

### Portfolio / Casos de Uso
```
HoverRevealCard + ParallaxLayer para imagens decorativas
```

### CTA Final
```
AuroraBackground + MagneticButton + ConfettiButton + TypingEffect no subtítulo
```

---

## Performance: Regras

| Efeito | Custo de performance | Cuidado |
|--------|---------------------|---------|
| FloatingOrbs (CSS) | Baixo | Desabilitar no mobile |
| AuroraBackground | Baixo | `blur()` caro, max 3 orbs |
| NoiseTexture | Mínimo | Apenas SVG, sem impact |
| ScrollTimeline | Mínimo | CSS nativo, sem JS |
| TiltCard | Baixo | Máx 6 cards por página |
| TextScramble | Baixo | Não usar em textos longos |
| GradientBorder (@property) | Baixo | 1-2 por página |
| BlobMorphing | Médio | Usar `blur()` para suavizar |
| ConfettiButton | Alto (momentâneo) | OK, dura <2s |
| Magnetic Cursor | Médio | Apenas desktop |
| Counter | Mínimo | IntersectionObserver |

**Regra geral:** `will-change: transform` nos elementos que animam com `transform`.
Nunca usar `will-change` em mais de 5 elementos simultâneos.
