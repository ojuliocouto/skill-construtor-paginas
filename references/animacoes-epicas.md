# Animacoes Epicas & Scroll Effects


> **ATENCAO (anti-vibe):** varios efeitos deste arquivo (glow em botao, border glow, aurora, floating orbs, gradiente indigo+roxo) sao tells VISUAIS de IA (V1-V15 de `anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Usar apenas quando o usuario pedir explicitamente esse look. Nos exemplos abaixo, trocar as cores hardcoded pela paleta REAL do projeto (CSS vars) e preferir micro-interacao sobria no CTA (mudanca de tom + elevacao sutil).
Setup: `npm install framer-motion`

### Scroll Reveal: Padrao Universal

**Aplicar em TODAS as secoes e cards. Nunca deixar nada estatico.**

```tsx
'use client'
import { motion } from 'framer-motion'

// Fade + slide-up (mais usado)
<motion.div
  initial={{ opacity: 0, y: 40 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] }}
  viewport={{ once: true, margin: "-80px" }}
>
  {/* qualquer elemento */}
</motion.div>

// Zoom in (cards, features)
<motion.div
  initial={{ opacity: 0, scale: 0.92 }}
  whileInView={{ opacity: 1, scale: 1 }}
  transition={{ duration: 0.5, ease: "backOut" }}
  viewport={{ once: true }}
/>

// Slide da esquerda (texto)
<motion.div
  initial={{ opacity: 0, x: -40 }}
  whileInView={{ opacity: 1, x: 0 }}
  transition={{ duration: 0.7 }}
  viewport={{ once: true }}
/>

// Slide da direita (mockup/imagem)
<motion.div
  initial={{ opacity: 0, x: 40 }}
  whileInView={{ opacity: 1, x: 0 }}
  transition={{ duration: 0.7, delay: 0.2 }}
  viewport={{ once: true }}
/>
```

### Stagger em Grids e Listas

```tsx
'use client'
import { motion } from 'framer-motion'

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
}
const itemVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: "easeOut" } },
}

<motion.div
  className="grid grid-cols-1 md:grid-cols-3 gap-6"
  variants={containerVariants}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, margin: "-60px" }}
>
  {items.map(item => (
    <motion.div key={item.id} variants={itemVariants} className="...">
      {/* card */}
    </motion.div>
  ))}
</motion.div>
```

### Titulos com Blur Reveal (entrada premium)

```tsx
'use client'
import { motion } from 'framer-motion'

// Blur + fade (Vercel/Linear style)
<motion.h1
  initial={{ opacity: 0, filter: "blur(12px)", y: 20 }}
  animate={{ opacity: 1, filter: "blur(0px)", y: 0 }}
  transition={{ duration: 0.9, ease: [0.21, 0.47, 0.32, 0.98] }}
  className="text-6xl md:text-8xl font-black tracking-tight"
>
  Titulo Absolutamente{' '}
  <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
    Impactante
  </span>
</motion.h1>

// Sequencia escalonada: badge → titulo → sub → cta
const heroSequence = [
  { delay: 0 },    // badge
  { delay: 0.15 }, // titulo linha 1
  { delay: 0.25 }, // titulo linha 2
  { delay: 0.4 },  // subtitulo
  { delay: 0.55 }, // ctas
  { delay: 0.7 },  // social proof
]
```

### Split Text Letter by Letter

```tsx
'use client'
import { motion } from 'framer-motion'

function SplitText({ text, className = '', delay = 0 }) {
  const words = text.split(' ')
  return (
    <motion.span
      className={`inline-flex flex-wrap gap-x-[0.25em] ${className}`}
      initial="hidden"
      animate="visible"
      aria-label={text}
    >
      {words.map((word, wi) =>
        word.split('').map((char, ci) => (
          <motion.span
            key={`${wi}-${ci}`}
            className="inline-block"
            variants={{
              hidden: { opacity: 0, y: 40, rotateX: -90 },
              visible: {
                opacity: 1, y: 0, rotateX: 0,
                transition: { delay: delay + (wi * word.length + ci) * 0.025, duration: 0.4, ease: "backOut" }
              },
            }}
          >
            {char}
          </motion.span>
        ))
      )}
    </motion.span>
  )
}
```

### Spotlight Card (cursor glow)

```tsx
'use client'
import { useRef, useState } from 'react'

function SpotlightCard({ children, className = '', spotlightColor = 'rgba(120,119,198,0.15)' }) {
  const divRef = useRef(null)
  const [pos, setPos] = useState({ x: 0, y: 0 })
  const [opacity, setOpacity] = useState(0)

  return (
    <div
      ref={divRef}
      onMouseMove={e => {
        const rect = divRef.current.getBoundingClientRect()
        setPos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
      }}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px transition-opacity duration-300 rounded-[inherit]"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${pos.x}px ${pos.y}px, ${spotlightColor}, transparent 40%)`,
        }}
      />
      {children}
    </div>
  )
}
```

### Parallax Scroll

```tsx
'use client'
import { useScroll, useTransform, motion } from 'framer-motion'
import { useRef } from 'react'

function ParallaxSection({ children, speed = 0.3 }) {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] })
  const y = useTransform(scrollYProgress, [0, 1], ["0%", `${speed * 100}%`])
  return (
    <div ref={ref} className="relative overflow-hidden">
      <motion.div style={{ y }}>{children}</motion.div>
    </div>
  )
}
```

### CSS-Only Animations (sem JS)

```css
/* globals.css */

/* Gradient text animado */
@keyframes gradientShift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
.animated-gradient-text {
  background: linear-gradient(270deg, #6366f1, #a855f7, #ec4899, #f43f5e, #6366f1);
  background-size: 300% 300%;
  animation: gradientShift 5s ease infinite;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Float suave */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50%       { transform: translateY(-16px); }
}
.animate-float { animation: float 4s ease-in-out infinite; }

/* Glow pulsante */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 20px rgba(99,102,241,0.4); }
  50%       { box-shadow: 0 0 50px rgba(99,102,241,0.9), 0 0 80px rgba(168,85,247,0.4); }
}
.animate-glow { animation: glowPulse 2.5s ease-in-out infinite; }

/* Shimmer de fundo */
@keyframes shimmerBg {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
.shimmer-bg {
  background: linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%);
  background-size: 200% 100%;
  animation: shimmerBg 3s ease infinite;
}
```

**Referencia completa:** `references/animacoes-avancadas.md`

---
