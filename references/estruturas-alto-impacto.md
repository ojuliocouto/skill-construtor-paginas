# Estruturas de Alto Impacto Visual

### Hero Sections: Templates Prontos

**Hero SaaS Dark (mais impactante)**
```tsx
export default function HeroSaaSDark() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden bg-slate-950">
      {/* Camadas de background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(120,119,198,0.35),transparent)]" />
      <DotPattern className="absolute inset-0 opacity-[0.15] [mask-image:radial-gradient(ellipse_at_center,white_40%,transparent_80%)]" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 lg:px-8 py-24 grid lg:grid-cols-2 gap-20 items-center">
        {/* Coluna texto */}
        <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8 }}>
          {/* Badge animado */}
          <motion.div
            initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-purple-300 mb-8 backdrop-blur-sm"
          >
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Novo: Integracao com IA
            <ChevronRight className="w-3 h-3" />
          </motion.div>

          {/* Titulo epico */}
          <motion.h1
            initial={{ opacity: 0, y: 20, filter: "blur(8px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{ delay: 0.2, duration: 0.9 }}
            className="text-5xl md:text-7xl font-black tracking-tight leading-[1.05] text-white mb-6"
          >
            Construa apps{' '}
            <span className="animated-gradient-text">absurdamente</span>
            {' '}rapidos
          </motion.h1>

          {/* Subtitulo */}
          <motion.p
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.7 }}
            className="text-lg text-gray-400 leading-relaxed mb-10 max-w-lg"
          >
            Elimine todo o trabalho manual. Foque no que importa.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55 }}
            className="flex flex-col sm:flex-row gap-4 mb-10"
          >
            <ShimmerButton shimmerColor="#a855f7" background="rgb(99,102,241)" className="px-8 py-4 text-base font-semibold">
              Comecar Gratis
            </ShimmerButton>
            <button className="group flex items-center gap-2 px-8 py-4 text-gray-300 hover:text-white transition-colors">
              Ver demo <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>

          {/* Social proof */}
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.7 }}
            className="flex items-center gap-4"
          >
            <div className="flex -space-x-2">
              {[1,2,3,4,5].map(i => (
                <div key={i} className="w-8 h-8 rounded-full border-2 border-slate-950 bg-gradient-to-br from-purple-400 to-pink-400" />
              ))}
            </div>
            <p className="text-sm text-gray-400">
              <span className="text-white font-semibold">+2.400</span> times ja usam
            </p>
          </motion.div>
        </motion.div>

        {/* Coluna mockup */}
        <motion.div
          initial={{ opacity: 0, x: 40, rotateY: -5 }}
          animate={{ opacity: 1, x: 0, rotateY: 0 }}
          transition={{ delay: 0.3, duration: 1 }}
          className="relative"
        >
          <div className="absolute -inset-6 bg-gradient-to-r from-purple-500/20 to-pink-500/20 blur-3xl rounded-3xl" />
          <Safari url="seuapp.com/dashboard" src="/screenshots/app.png" className="relative w-full" />
        </motion.div>
      </div>
    </section>
  )
}
```

**Hero Minimal Light (elegante)**
```tsx
<section className="relative min-h-[90vh] flex items-center bg-white overflow-hidden">
  {/* Grid pattern sutil */}
  <GridPattern className="absolute inset-0 opacity-[0.04] stroke-gray-900" />
  <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(99,102,241,0.08),transparent)]" />

  <div className="relative max-w-5xl mx-auto px-6 text-center py-32">
    {/* Titulo */}
    <motion.h1
      initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
      className="text-6xl md:text-8xl font-black tracking-tight text-gray-950 mb-6 leading-[1.02]"
    >
      Design{' '}
      <span className="relative">
        bonito
        <span className="absolute -bottom-2 left-0 right-0 h-[4px] bg-indigo-500 rounded-full" />
      </span>
      {' '}e rapido
    </motion.h1>
    <motion.p
      initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
      className="text-xl text-gray-500 max-w-2xl mx-auto mb-12"
    >
      Sua descricao aqui com 15 a 25 palavras que explicam o valor.
    </motion.p>
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
      <button className="px-10 py-5 bg-gray-950 text-white font-bold rounded-full text-lg
        shadow-[0_0_0_0_rgba(0,0,0,0.1)] hover:shadow-[0_20px_60px_rgba(0,0,0,0.15)]
        transition-all duration-300 hover:-translate-y-1">
        Comecar Gratis
      </button>
    </motion.div>
  </div>
</section>
```

### Titulos Epicos: Padroes

```tsx
// 1. Gradient text bicolor
<h1 className="text-7xl font-black">
  <span className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 bg-clip-text text-transparent">
    Transforma
  </span>
  {' '}
  <span className="text-gray-950 dark:text-white">tudo</span>
</h1>

// 2. Outline + filled (contraste brutal)
<h1 className="text-7xl font-black text-white">
  Build{' '}
  <span className="[-webkit-text-stroke:2px_rgb(99,102,241)] text-transparent">faster</span>
</h1>

// 3. Pill badge + titulo
<div className="space-y-4">
  <div className="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-400 px-4 py-2 rounded-full text-sm font-semibold">
    <Sparkles className="w-4 h-4" /> Powered by AI
  </div>
  <h1 className="text-6xl font-black">Seu Produto Aqui</h1>
</div>

// 4. Linha decorativa entre titulo e subtitulo
<div className="flex items-center gap-4 my-6">
  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent dark:via-gray-700" />
  <span className="text-sm text-gray-400 tracking-widest uppercase">Novo 2025</span>
  <div className="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent dark:via-gray-700" />
</div>

// 5. Numero de destaque (para stats ou precos)
<div className="text-8xl font-black tabular-nums">
  <span className="text-3xl font-bold text-gray-400 align-top mt-4 inline-block">R$</span>
  <NumberTicker value={97} className="text-gray-950 dark:text-white" />
  <span className="text-2xl font-medium text-gray-400">/mes</span>
</div>
```

### Botoes de Alto Impacto

```tsx
// 1. Glow CTA (mais elegante)
<button className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-full
  shadow-[0_0_20px_rgba(99,102,241,0.5)] hover:shadow-[0_0_50px_rgba(99,102,241,0.9)]
  transition-all duration-300 hover:-translate-y-0.5 cursor-pointer">
  Comecar Agora
</button>

// 2. Magnetic Button (segue o cursor suavemente)
'use client'
import { motion, useMotionValue, useSpring } from 'framer-motion'

function MagneticButton({ children, className = '' }) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const springX = useSpring(x, { stiffness: 300, damping: 20 })
  const springY = useSpring(y, { stiffness: 300, damping: 20 })

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    x.set((e.clientX - rect.left - rect.width / 2) * 0.35)
    y.set((e.clientY - rect.top - rect.height / 2) * 0.35)
  }

  return (
    <motion.button
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouseMove}
      onMouseLeave={() => { x.set(0); y.set(0) }}
      className={`px-8 py-4 bg-indigo-600 text-white font-bold rounded-full hover:bg-indigo-500 transition-colors cursor-pointer ${className}`}
    >
      {children}
    </motion.button>
  )
}

// 3. Outlined dashed animado
<button className="relative px-8 py-4 text-indigo-400 font-semibold rounded-full
  border-2 border-dashed border-indigo-500/40 hover:border-indigo-400
  hover:text-indigo-300 hover:bg-indigo-950/50 transition-all duration-300">
  Saiba Mais
</button>

// 4. CTA com icone animado
<button className="group flex items-center gap-3 px-8 py-4 bg-gray-950 text-white font-bold rounded-full
  hover:gap-4 transition-all duration-300">
  Comecar Gratis
  <div className="w-5 h-5 bg-white/10 rounded-full flex items-center justify-center
    group-hover:bg-indigo-500 group-hover:scale-110 transition-all duration-300">
    <ArrowRight className="w-3 h-3" />
  </div>
</button>
```

### Mockups: Uso Correto

```tsx
// Safari mockup com glow
<div className="relative">
  {/* glow atras */}
  <div className="absolute -inset-8 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 blur-3xl" />
  <Safari
    url="seuapp.com"
    src="/screenshots/dashboard.png"
    className="relative w-full max-w-4xl mx-auto"
  />
</div>

// iPhone com float animation
<div className="animate-float relative mx-auto w-fit">
  <div className="absolute -inset-4 bg-indigo-500/20 blur-2xl" />
  <Iphone15Pro src="/screenshots/mobile.png" className="relative h-[500px]" />
</div>

// Dois mockups sobrepostos (desktop + mobile)
<div className="relative mx-auto max-w-3xl">
  <Safari src="/screenshots/desktop.png" className="w-full" />
  <div className="absolute -bottom-8 -right-8 w-1/4">
    <Iphone15Pro src="/screenshots/mobile.png" />
  </div>
</div>
```

### Wave Dividers entre Secoes

```tsx
// Wave suave
function WaveDown({ color = "#f9fafb" }: { color?: string }) {
  return (
    <div className="relative h-16 overflow-hidden">
      <svg viewBox="0 0 1440 64" className="absolute bottom-0 w-full" preserveAspectRatio="none">
        <path fill={color} d="M0,32 C240,64 480,0 720,32 C960,64 1200,0 1440,32 L1440,64 L0,64 Z" />
      </svg>
    </div>
  )
}

// Gradient fade entre secoes (mais moderno)
<div className="h-32 bg-gradient-to-b from-slate-950 to-white dark:to-gray-900" />
```

### Features Section Premium

```tsx
<section className="py-24 bg-gray-50 dark:bg-gray-950">
  <div className="max-w-7xl mx-auto px-6">
    {/* Header da secao */}
    <motion.div
      initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="text-center mb-16"
    >
      <div className="inline-flex items-center gap-2 text-indigo-500 bg-indigo-50 dark:bg-indigo-950/50 px-4 py-2 rounded-full text-sm font-semibold mb-4">
        <Zap className="w-4 h-4" /> Funcionalidades
      </div>
      <h2 className="text-4xl md:text-5xl font-black tracking-tight mb-4">
        Tudo que voce precisa
      </h2>
      <p className="text-gray-500 max-w-2xl mx-auto text-lg">
        Uma plataforma completa para construir produtos incriveis.
      </p>
    </motion.div>

    {/* Grid de features */}
    <motion.div
      className="grid md:grid-cols-2 lg:grid-cols-3 gap-6"
      variants={{ visible: { transition: { staggerChildren: 0.08 } } }}
      initial="hidden" whileInView="visible" viewport={{ once: true }}
    >
      {features.map(f => (
        <motion.div
          key={f.title}
          variants={{ hidden: { opacity: 0, y: 24 }, visible: { opacity: 1, y: 0 } }}
          className="group p-8 rounded-3xl bg-white dark:bg-gray-900
            border border-gray-100 dark:border-white/[0.06]
            hover:border-indigo-500/30 hover:shadow-xl hover:shadow-indigo-500/10
            transition-all duration-300 hover:-translate-y-1.5"
        >
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center mb-6
            group-hover:scale-110 group-hover:bg-indigo-100 dark:group-hover:bg-indigo-900 transition-all duration-300">
            <f.icon className="w-6 h-6 text-indigo-600" />
          </div>
          <h3 className="text-lg font-bold mb-2">{f.title}</h3>
          <p className="text-gray-500 leading-relaxed text-sm">{f.description}</p>
        </motion.div>
      ))}
    </motion.div>
  </div>
</section>
```

### Stats Section Dramatica

```tsx
<section className="relative py-24 overflow-hidden">
  <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-700" />
  <RetroGrid className="absolute inset-0 opacity-20" />
  <div className="relative max-w-5xl mx-auto px-6">
    <motion.div
      className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center text-white"
      variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
      initial="hidden" whileInView="visible" viewport={{ once: true }}
    >
      {[
        { value: 2400, suffix: "+", label: "Usuarios Ativos" },
        { value: 98,   suffix: "%", label: "Satisfacao" },
        { value: 150,  suffix: "ms", label: "Tempo de Resposta" },
        { value: 99.9, suffix: "%", label: "Uptime" },
      ].map(stat => (
        <motion.div
          key={stat.label}
          variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
        >
          <div className="text-5xl font-black mb-2 tabular-nums">
            <NumberTicker value={stat.value} className="text-white" />{stat.suffix}
          </div>
          <p className="text-white/70 text-sm font-medium tracking-wider uppercase">{stat.label}</p>
        </motion.div>
      ))}
    </motion.div>
  </div>
</section>
```

### Testimonials com Marquee Duplo

```tsx
<section className="py-24 bg-gray-50 dark:bg-gray-950 overflow-hidden">
  <div className="flex gap-6 overflow-hidden">
    <Marquee vertical className="h-[700px] [--duration:25s]" pauseOnHover>
      {testimonials.slice(0, 5).map(t => <TestimonialCard key={t.id} {...t} />)}
    </Marquee>
    <Marquee vertical reverse className="h-[700px] [--duration:30s] hidden md:flex" pauseOnHover>
      {testimonials.slice(5, 10).map(t => <TestimonialCard key={t.id} {...t} />)}
    </Marquee>
    <Marquee vertical className="h-[700px] [--duration:20s] hidden lg:flex" pauseOnHover>
      {testimonials.slice(10).map(t => <TestimonialCard key={t.id} {...t} />)}
    </Marquee>
  </div>
</section>

function TestimonialCard({ text, name, role, avatar }) {
  return (
    <div className="mb-4 p-6 rounded-2xl bg-white dark:bg-gray-900
      border border-gray-100 dark:border-white/[0.06] shadow-sm max-w-xs">
      <div className="flex gap-1 mb-3">
        {[...Array(5)].map((_, i) => <Star key={i} className="w-4 h-4 fill-amber-400 text-amber-400" />)}
      </div>
      <p className="text-gray-600 dark:text-gray-400 text-sm leading-relaxed mb-4">"{text}"</p>
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-400 to-purple-400" />
        <div>
          <p className="font-semibold text-sm">{name}</p>
          <p className="text-xs text-gray-400">{role}</p>
        </div>
      </div>
    </div>
  )
}
```

**Referencia completa de padroes:** `references/visual-excellence.md`

---
