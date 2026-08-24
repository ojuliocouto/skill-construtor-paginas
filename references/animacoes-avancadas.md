# Animacoes Avancadas: Referencia Completa

Framer Motion, CSS Animations, Scroll Effects, Parallax, Spring Physics.

## Setup

```bash
npm install framer-motion
```

---

## Framer Motion: Fundamentos

### Variants (reutilizaveis)

```tsx
// Copiar e reutilizar em qualquer projeto
export const variants = {
  // Entradas
  fadeUp:   { hidden: { opacity: 0, y: 40 },        visible: { opacity: 1, y: 0 }        },
  fadeDown: { hidden: { opacity: 0, y: -40 },       visible: { opacity: 1, y: 0 }        },
  fadeLeft: { hidden: { opacity: 0, x: -40 },       visible: { opacity: 1, x: 0 }        },
  fadeRight:{ hidden: { opacity: 0, x: 40 },        visible: { opacity: 1, x: 0 }        },
  fadeIn:   { hidden: { opacity: 0 },               visible: { opacity: 1 }              },
  zoomIn:   { hidden: { opacity: 0, scale: 0.88 },  visible: { opacity: 1, scale: 1 }    },
  zoomOut:  { hidden: { opacity: 0, scale: 1.12 },  visible: { opacity: 1, scale: 1 }    },
  blurUp:   { hidden: { opacity: 0, y: 20, filter: "blur(12px)" },
              visible: { opacity: 1, y: 0,  filter: "blur(0px)" }                        },
  flipX:    { hidden: { opacity: 0, rotateX: -90 }, visible: { opacity: 1, rotateX: 0 } },

  // Transicoes
  spring:   { type: "spring", stiffness: 300, damping: 25 },
  smooth:   { duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] },
  snappy:   { duration: 0.4, ease: [0.16, 1, 0.3, 1]       },
  gentle:   { duration: 1.0, ease: "easeOut"                },

  // Stagger containers
  stagger05: { hidden: {}, visible: { transition: { staggerChildren: 0.05 } } },
  stagger10: { hidden: {}, visible: { transition: { staggerChildren: 0.10 } } },
  stagger15: { hidden: {}, visible: { transition: { staggerChildren: 0.15 } } },
}
```

### Scroll Reveal: Uso Basico

```tsx
'use client'
import { motion } from 'framer-motion'

// Elemento simples
<motion.div
  initial={{ opacity: 0, y: 40 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] }}
  viewport={{ once: true, margin: "-80px" }}
>
  {/* conteudo */}
</motion.div>

// Grid com stagger (MAIS USADO em features/cards)
<motion.div
  className="grid grid-cols-3 gap-6"
  variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.1 } } }}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, margin: "-60px" }}
>
  {items.map(item => (
    <motion.div
      key={item.id}
      variants={{
        hidden:   { opacity: 0, y: 24 },
        visible:  { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
      }}
    >
      {/* card */}
    </motion.div>
  ))}
</motion.div>
```

### Sequencia de Entrada do Hero

```tsx
// Cada elemento entra apos o anterior com delay crescente
const HeroSection = () => (
  <>
    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.0, duration: 0.5 }}>
      {/* badge */}
    </motion.div>
    <motion.h1 initial={{ opacity: 0, y: 20, filter: "blur(8px)" }} animate={{ opacity: 1, y: 0, filter: "blur(0px)" }} transition={{ delay: 0.15, duration: 0.9, ease: [0.21, 0.47, 0.32, 0.98] }}>
      {/* titulo */}
    </motion.h1>
    <motion.p initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35, duration: 0.6 }}>
      {/* subtitulo */}
    </motion.p>
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
      {/* ctas */}
    </motion.div>
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7, duration: 0.8 }}>
      {/* social proof */}
    </motion.div>
    <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3, duration: 1.0 }}>
      {/* mockup */}
    </motion.div>
  </>
)
```

---

## Split Text: Animacao Letra por Letra

```tsx
'use client'
import { motion } from 'framer-motion'

// Versao simples (palavra por palavra)
function WordsReveal({ text, className = '', delay = 0 }) {
  return (
    <motion.span
      className={className}
      initial="hidden"
      animate="visible"
      aria-label={text}
    >
      {text.split(' ').map((word, i) => (
        <motion.span
          key={i}
          className="inline-block mr-[0.25em]"
          variants={{
            hidden:  { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0, transition: { delay: delay + i * 0.05, duration: 0.5, ease: "easeOut" } },
          }}
        >
          {word}
        </motion.span>
      ))}
    </motion.span>
  )
}

// Versao sofisticada (letra por letra com rotacao)
function LetterFlip({ text, className = '', delay = 0 }) {
  return (
    <span className={`inline-flex overflow-hidden ${className}`} aria-label={text}>
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          className="inline-block"
          initial={{ opacity: 0, y: '100%' }}
          animate={{ opacity: 1, y: '0%' }}
          transition={{ delay: delay + i * 0.03, duration: 0.4, ease: [0.33, 1, 0.68, 1] }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </span>
  )
}

// Versao 3D (flip 3D)
function FlipReveal({ text, className = '' }) {
  return (
    <motion.h1 className={`perspective-[1000px] ${className}`} initial="hidden" animate="visible">
      {text.split('').map((char, i) => (
        <motion.span
          key={i}
          className="inline-block origin-bottom"
          variants={{
            hidden:  { opacity: 0, rotateX: -80, y: 20 },
            visible: { opacity: 1, rotateX: 0,   y: 0,
              transition: { delay: i * 0.035, duration: 0.5, ease: "backOut" } },
          }}
        >
          {char === ' ' ? '\u00A0' : char}
        </motion.span>
      ))}
    </motion.h1>
  )
}
```

---

## Magnetic Button

```tsx
'use client'
import { useRef } from 'react'
import { motion, useMotionValue, useSpring } from 'framer-motion'

function MagneticButton({ children, className = '', strength = 0.35 }) {
  const ref = useRef(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 300, damping: 20 })
  const springY = useSpring(y, { stiffness: 300, damping: 20 })

  const handleMouseMove = (e) => {
    const rect = ref.current.getBoundingClientRect()
    x.set((e.clientX - rect.left - rect.width  / 2) * strength)
    y.set((e.clientY - rect.top  - rect.height / 2) * strength)
  }
  const handleMouseLeave = () => { x.set(0); y.set(0) }

  return (
    <motion.button
      ref={ref}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      className={className}
    >
      {children}
    </motion.button>
  )
}
```

---

## Hover Card com Tilt 3D

```tsx
'use client'
import { useRef } from 'react'
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion'

function TiltCard({ children, className = '' }) {
  const ref = useRef(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [8, -8]), { stiffness: 300, damping: 30 })
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-8, 8]), { stiffness: 300, damping: 30 })

  const handleMouseMove = (e) => {
    const rect = ref.current.getBoundingClientRect()
    x.set((e.clientX - rect.left) / rect.width  - 0.5)
    y.set((e.clientY - rect.top)  / rect.height - 0.5)
  }

  return (
    <motion.div
      ref={ref}
      style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      className={`cursor-pointer ${className}`}
    >
      {children}
    </motion.div>
  )
}

// Uso:
<TiltCard className="rounded-2xl border p-8 bg-white dark:bg-gray-900">
  {/* card content */}
</TiltCard>
```

---

## Parallax Scroll

```tsx
'use client'
import { useRef } from 'react'
import { useScroll, useTransform, motion } from 'framer-motion'

// Parallax simples (elemento se move mais rapido/devagar que o scroll)
function ParallaxElement({ children, speed = 0.3, className = '' }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  })
  const y = useTransform(scrollYProgress, [0, 1], [`${-speed * 50}%`, `${speed * 50}%`])

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`}>
      <motion.div style={{ y }}>
        {children}
      </motion.div>
    </div>
  )
}

// Hero com parallax de fundo
function ParallaxHero() {
  const { scrollY } = useScroll()
  const bgY    = useTransform(scrollY, [0, 600], [0, 200])
  const textY  = useTransform(scrollY, [0, 600], [0, -80])
  const opacity= useTransform(scrollY, [0, 400], [1, 0])

  return (
    <div className="relative h-screen overflow-hidden">
      <motion.div style={{ y: bgY }} className="absolute inset-0 scale-110">
        <img src="/hero-bg.jpg" className="w-full h-full object-cover" alt="" />
      </motion.div>
      <div className="absolute inset-0 bg-black/50" />
      <motion.div style={{ y: textY, opacity }} className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-7xl font-black text-white text-center">...</h1>
      </motion.div>
    </div>
  )
}
```

---

## Page Transitions (Next.js App Router)

```tsx
// components/page-transition.tsx
'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { usePathname } from 'next/navigation'

const pageVariants = {
  initial: { opacity: 0, y: 20, filter: "blur(4px)" },
  enter:   { opacity: 1, y: 0,  filter: "blur(0px)", transition: { duration: 0.5, ease: [0.21, 0.47, 0.32, 0.98] } },
  exit:    { opacity: 0, y: -10, transition: { duration: 0.3 } },
}

export function PageTransition({ children }) {
  const pathname = usePathname()
  return (
    <AnimatePresence mode="wait">
      <motion.div key={pathname} variants={pageVariants} initial="initial" animate="enter" exit="exit">
        {children}
      </motion.div>
    </AnimatePresence>
  )
}

// No layout.tsx:
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <PageTransition>{children}</PageTransition>
      </body>
    </html>
  )
}
```

---

## Scroll Progress Indicator

```tsx
'use client'
import { useScroll, useSpring, motion } from 'framer-motion'

export function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30 })

  return (
    <motion.div
      style={{ scaleX, transformOrigin: "0%" }}
      className="fixed top-0 left-0 right-0 h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 z-50"
    />
  )
}
```

---

## Contador Animado (sem Magic UI)

```tsx
'use client'
import { useEffect, useRef, useState } from 'react'
import { useInView } from 'framer-motion'

function CountUp({ end, duration = 1800, prefix = '', suffix = '', decimals = 0 }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  useEffect(() => {
    if (!isInView) return
    let start = 0
    const step = end / (duration / 16)
    const timer = setInterval(() => {
      start = Math.min(start + step, end)
      setCount(parseFloat(start.toFixed(decimals)))
      if (start >= end) clearInterval(timer)
    }, 16)
    return () => clearInterval(timer)
  }, [isInView, end, duration, decimals])

  return (
    <span ref={ref} className="tabular-nums">
      {prefix}{count.toLocaleString('pt-BR', { minimumFractionDigits: decimals })}{suffix}
    </span>
  )
}

// Uso:
<CountUp end={2400} suffix="+" />          // 2.400+
<CountUp end={98.7} decimals={1} suffix="%" /> // 98,7%
<CountUp end={99.9} decimals={1} suffix="%" prefix="" /> // 99,9%
```

---

## CSS Animations Avancadas

```css
/* globals.css, adicionar antes do :root */

/* ===== GRADIENT TEXT ===== */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50%       { background-position: 100% 50%; }
}
.animated-gradient-text {
  background: linear-gradient(270deg, #6366f1, #a855f7, #ec4899, #f43f5e, #6366f1);
  background-size: 300% 300%;
  animation: gradientShift 5s ease infinite;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* ===== FLOAT ===== */
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50%       { transform: translateY(-18px); }
}
.animate-float { animation: float 4s ease-in-out infinite; }

/* ===== GLOW PULSE ===== */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,0.4); }
  50%       { box-shadow: 0 0 50px rgba(99,102,241,0.9), 0 0 80px rgba(168,85,247,0.3); }
}
.animate-glow { animation: glowPulse 2.5s ease-in-out infinite; }

/* ===== FADE IN UP ===== */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in-up { animation: fadeInUp 0.6s ease forwards; }

/* ===== SHIMMER BG ===== */
@keyframes shimmerBg {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.shimmer-bg {
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmerBg 3s ease-in-out infinite;
}

/* ===== SPIN SLOW ===== */
.animate-spin-slow { animation: spin 8s linear infinite; }

/* ===== BOUNCE SUBTLE ===== */
@keyframes bounceSoft {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-6px); }
}
.animate-bounce-soft { animation: bounceSoft 2s ease-in-out infinite; }

/* ===== AURORA BACKGROUND ===== */
@keyframes aurora {
  0%, 100% { background-position: 0% 50%; }
  25%       { background-position: 100% 0%; }
  50%       { background-position: 100% 100%; }
  75%       { background-position: 0% 100%; }
}
.aurora-bg {
  background: linear-gradient(135deg, #667eea, #764ba2, #f093fb, #f5576c, #4facfe, #00f2fe);
  background-size: 400% 400%;
  animation: aurora 12s ease infinite;
}

/* ===== RESPEIT MOTION PREFERENCE ===== */
@media (prefers-reduced-motion: reduce) {
  .animated-gradient-text,
  .animate-float,
  .animate-glow,
  .animate-fade-in-up,
  .shimmer-bg,
  .aurora-bg {
    animation: none !important;
    transition: none !important;
  }
}
```

---

## Intersection Observer (sem Framer Motion)

```tsx
// Hook puro para scroll reveal
import { useEffect, useRef, useState } from 'react'

function useInViewOnce(threshold = 0.15) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setInView(true); observer.unobserve(el) } },
      { threshold, rootMargin: "-60px" }
    )
    observer.observe(el)
    return () => observer.disconnect()
  }, [threshold])

  return { ref, inView }
}

// Uso com CSS classes
function RevealSection({ children, delay = 0 }) {
  const { ref, inView } = useInViewOnce()
  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ${inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
      style={{ transitionDelay: `${delay}ms` }}
    >
      {children}
    </div>
  )
}
```

---

## Componentes de Animação Reutilizáveis (Biblioteca Interna)

Padrões validados em produção. Copiar e adaptar brand tokens, nunca reinventar.

---

### BlurReveal: Entrada premium para headings

Uso: h1, h2, badges, qualquer elemento que precisa de entrada de alto impacto.

```tsx
'use client'
import { motion } from 'framer-motion'
import { useInView } from 'framer-motion'
import { useRef } from 'react'

function BlurReveal({
  children,
  delay = 0,
  className = '',
  once = true,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
  once?: boolean
}) {
  const ref = useRef(null)
  const inView = useInView(ref, { once, margin: '-80px' })

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y: 16, filter: 'blur(20px)' }}
      animate={inView ? { opacity: 1, y: 0, filter: 'blur(0px)' } : {}}
      transition={{ duration: 1.0, ease: [0.21, 0.47, 0.32, 0.98], delay }}
    >
      {children}
    </motion.div>
  )
}
// Uso:
// <BlurReveal delay={0}><h1>Título</h1></BlurReveal>
// <BlurReveal delay={0.15}><p>Subtítulo</p></BlurReveal>
// <BlurReveal delay={0.3}><div>CTAs</div></BlurReveal>
```

---

### StaggerGrid + StaggerItem: Grid animado com entrada escalonada

Uso: qualquer grid de cards, features, benefícios, testimonials.

```tsx
'use client'
import { motion, useInView } from 'framer-motion'
import { useRef } from 'react'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.09 } },
}

const itemVariants = {
  hidden: { opacity: 0, y: 28, filter: 'blur(4px)' },
  visible: {
    opacity: 1, y: 0, filter: 'blur(0px)',
    transition: { duration: 0.6, ease: [0.21, 0.47, 0.32, 0.98] },
  },
}

function StaggerGrid({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin: '-60px' })
  return (
    <motion.div
      ref={ref}
      className={className}
      variants={containerVariants}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
    >
      {children}
    </motion.div>
  )
}

function StaggerItem({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div className={className} variants={itemVariants}>
      {children}
    </motion.div>
  )
}

// Uso:
// <StaggerGrid className="grid grid-cols-1 md:grid-cols-3 gap-6">
//   <StaggerItem><Card /></StaggerItem>
//   <StaggerItem><Card /></StaggerItem>
//   <StaggerItem><Card /></StaggerItem>
// </StaggerGrid>
```

---

### FloatingOrbs: Orbs radial-gradient animados no fundo

Uso: hero sections, seções de destaque. Efeito atmosférico premium sem impacto de performance.

```tsx
// CSS (globals.css ou index.css)
// @keyframes ia-float-1 {
//   0%, 100% { transform: translate(0px, 0px) scale(1); }
//   33% { transform: translate(-22px, -28px) scale(1.06); }
//   66% { transform: translate(14px, 16px) scale(0.94); }
// }
// @keyframes ia-float-2 {
//   0%, 100% { transform: translate(0px, 0px) scale(1); }
//   40% { transform: translate(28px, -22px) scale(1.08); }
//   70% { transform: translate(-12px, 18px) scale(0.94); }
// }
// @keyframes ia-float-3 {
//   0%, 100% { transform: translate(0px, 0px) scale(1); }
//   50% { transform: translate(-16px, -24px) scale(1.05); }
// }

function FloatingOrbs({ color = '#7F41F9' }: { color?: string }) {
  const orb = (cls: string, size: string, pos: string) => (
    <div
      className={`absolute pointer-events-none rounded-full opacity-10 blur-3xl ${cls}`}
      style={{
        width: size, height: size,
        background: `radial-gradient(circle, ${color} 0%, transparent 70%)`,
        ...Object.fromEntries(pos.split(' ').map((v, i) => [['top','left','bottom','right'][i], v])),
      }}
    />
  )
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      {orb('ia-float-1', '520px', '-10% -8%')}
      {orb('ia-float-2', '420px', '-5% auto -5% auto')}  {/* ajustar posição por projeto */}
      {orb('ia-float-3', '380px', 'auto auto -8% -5%')}
    </div>
  )
}
// NOTA: Adaptar posições e cores aos brand tokens do projeto.
// Duração recomendada: 6s, 8s, 10s (já definidas nos keyframes CSS)
```

---

### ScrollProgress: Barra de progresso de leitura

Uso: em TODAS as páginas longas (landing pages, artigos, sales pages).

```tsx
'use client'
import { motion, useScroll } from 'framer-motion'

function ScrollProgress({ color = '#7F41F9' }: { color?: string }) {
  const { scrollYProgress } = useScroll()
  return (
    <motion.div
      className="fixed top-0 left-0 right-0 z-[100] origin-left"
      style={{
        height: 2,
        background: color,
        scaleX: scrollYProgress,
        boxShadow: `0 0 8px ${color}, 0 0 16px ${color}80`,
      }}
    />
  )
}
// Adicionar no root da página, antes de qualquer seção
```

---

### Shimmer Streak: Efeito de brilho em CTAs

Uso: botões primários de CTA, elementos que precisam chamar atenção.

```tsx
'use client'
import { motion } from 'framer-motion'

// Envolver o botão com position: relative overflow-hidden
// Inserir este span como filho do botão

function ShimmerStreak() {
  return (
    <motion.span
      className="absolute top-0 left-0 h-full w-1/3 pointer-events-none rounded-full"
      style={{
        background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.22), transparent)',
      }}
      animate={{ x: ['-150%', '400%'] }}
      transition={{
        duration: 2.2,
        repeat: Infinity,
        repeatDelay: 2.5,
        ease: 'easeInOut',
      }}
    />
  )
}

// Uso em botão CTA:
// <button className="relative overflow-hidden px-8 py-4 bg-purple-600 ...">
//   <ShimmerStreak />
//   Começar Agora
// </button>
```

---

### CSS Keyframes: Gradient Text Animado

Uso: palavras-chave no hero, highlights em headings, palavras que precisam de destaque dinâmico.

```css
/* globals.css / index.css */
@keyframes ia-gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.ia-gradient-text {
  background: linear-gradient(270deg, #7F41F9, #C4A8FF, #9B6EFF, #B87EFF, #7F41F9);
  background-size: 300% 100%;
  animation: ia-gradient-shift 5s ease infinite;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline;
  padding-right: 0.08em; /* fix: italic corta a última letra sem isso */
}

/* Adaptar cores do gradiente aos brand tokens do projeto */
```

---

### CSS Keyframes: Scan Line + Pulse Ring

Uso: scan line em mockups de dashboard/UI, pulse ring em indicadores de status ao vivo.

```css
/* Scan line, para mockups de dashboard */
@keyframes ia-scan {
  0%   { top: 8%;  opacity: 0; }
  5%   { opacity: 1; }
  90%  { opacity: 1; }
  100% { top: 92%; opacity: 0; }
}
.ia-scan-line {
  position: absolute;
  left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(127,65,249,0.6), transparent);
  animation: ia-scan 3s ease-in-out infinite;
  animation-delay: 2s;
  pointer-events: none;
}

/* Pulse ring, indicadores de status, "ao vivo", notificações */
@keyframes ia-pulse-ring {
  0%   { transform: scale(0.8); opacity: 0.6; }
  100% { transform: scale(1.8); opacity: 0; }
}
.ia-pulse-ring {
  animation: ia-pulse-ring 2s ease-out infinite;
}

/* Uso do pulse ring:
<div class="relative">
  <div class="w-3 h-3 rounded-full bg-green-400"></div>
  <div class="absolute inset-0 rounded-full bg-green-400 ia-pulse-ring"></div>
</div>
*/
```

---

## Performance: Regras de Ouro

```tsx
// 1. Sempre usar will-change para elementos que animam muito
<motion.div style={{ willChange: "transform" }} animate={{ x: 100 }} />

// 2. Usar transform/opacity apenas (composited layers, nao causa reflow)
// BOM:  opacity, transform (translate, scale, rotate)
// RUIM: width, height, top, left, margin, padding (causam layout)

// 3. Dynamic import para componentes pesados
import dynamic from 'next/dynamic'
const Globe = dynamic(() => import('@/components/magicui/globe'), { ssr: false })
const HeavyAnimation = dynamic(() => import('./HeavyAnimation'), { ssr: false })

// 4. Mounted check para evitar hydration mismatch
const [mounted, setMounted] = useState(false)
useEffect(() => setMounted(true), [])
if (!mounted) return <div className="h-[400px]" /> // skeleton placeholder

// 5. Pausar animacoes quando tab nao esta visivel
useEffect(() => {
  const handleVisibility = () => {
    if (document.hidden) controls.pause()
    else controls.start("visible")
  }
  document.addEventListener('visibilitychange', handleVisibility)
  return () => document.removeEventListener('visibilitychange', handleVisibility)
}, [controls])
```
