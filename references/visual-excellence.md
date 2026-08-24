# Visual Excellence: Referencia Completa

Backgrounds epicos, Navbar premium, Pricing, FAQ, CTA sections, Noise textures, Aurora gradients.

---

## Gradient Text: Regras Criticas

### background-clip: text com fonte italica: BUG DE CORTE

**Problema:** `background-clip: text` pinta o gradiente EXATAMENTE nos limites do bounding box do span.
Texto italico inclina as letras para a direita, fazendo a ultima letra vazar alem da borda direita e ser cortada.

**Sintoma:** ultima letra do span parece "cortada" no lado direito (ex: "o" de "tudo" com metade visivel).

**Fix obrigatorio:** sempre adicionar `padding-right: 0.15em` no span com gradiente italico:

```html
<!-- ERRADO, ultimo caractere cortado em italico -->
<span class="gradient-text" style="font-style:italic;">diferente de tudo</span>

<!-- CORRETO, padding-right evita o corte -->
<span class="gradient-text" style="font-style:italic; padding-right:0.15em;">diferente de tudo</span>
```

```css
/* Classe padrao para gradient text */
.gradient-text {
  background: linear-gradient(to right, #FF6B2B 0%, #F94E03 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent; /* fallback */
}
/* NUNCA usar gradiente 135deg em texto italico, cria corte diagonal esquisito */
/* SEMPRE usar "to right" para texto, flui naturalmente no sentido da leitura */
```

**Regra:** toda vez que aplicar `background-clip: text` + `font-style: italic`, adicionar `padding-right: 0.1em` a `0.2em` no span.

---

## Backgrounds de Alto Impacto

### Aurora / Mesh Gradient

```tsx
// Aurora dark (hero SaaS premium)
<div className="absolute inset-0">
  <div className="absolute inset-0 bg-slate-950" />
  <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_60%_at_50%_-10%,rgba(120,119,198,0.4),transparent)]" />
  <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/20 blur-[120px] rounded-full" />
  <div className="absolute top-0 right-1/4 w-80 h-80 bg-blue-500/15 blur-[100px] rounded-full" />
</div>

// Aurora light (hero elegante)
<div className="absolute inset-0">
  <div className="absolute inset-0 bg-white" />
  <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_0%,rgba(99,102,241,0.08),transparent)]" />
  <div className="absolute top-0 left-1/3 w-64 h-64 bg-indigo-100/60 blur-3xl rounded-full" />
  <div className="absolute top-10 right-1/3 w-48 h-48 bg-violet-100/40 blur-2xl rounded-full" />
</div>

// Multi-color blob (Stripe style)
<div className="absolute inset-0 overflow-hidden">
  <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-purple-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-[blob_7s_infinite]" />
  <div className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-yellow-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-[blob_7s_infinite_2s]" />
  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-pink-300/30 rounded-full mix-blend-multiply filter blur-3xl animate-[blob_7s_infinite_4s]" />
</div>

/* @keyframes blob { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(30px,-50px) scale(1.1)} 66%{transform:translate(-20px,20px) scale(0.9)} } */
```

### Patterns como Background

```tsx
// DotPattern com mask radial (MagicUI)
<DotPattern
  width={20} height={20} cr={1}
  className="absolute inset-0 opacity-[0.15]
    [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,white,transparent)]"
/>

// GridPattern com fade
<GridPattern
  width={40} height={40}
  className="absolute inset-0 stroke-gray-200/60 dark:stroke-white/[0.04]
    [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]"
/>

// RetroGrid (perspectiva, ótimo para hero dark)
<RetroGrid angle={65} className="opacity-30" />

// CSS Grid pattern puro (sem dependencia)
.bg-grid-slate-900 {
  background-image:
    linear-gradient(to right, rgb(15 23 42 / 0.05) 1px, transparent 1px),
    linear-gradient(to bottom, rgb(15 23 42 / 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
}

// Noise texture (premiumidade sutil)
.noise-bg::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,..."); /* ou /noise.png */
}
```

---

## Navbar Premium

### Floating Navbar (nao cola no topo)

```tsx
'use client'
import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

export function FloatingNav() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handle = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handle)
    return () => window.removeEventListener('scroll', handle)
  }, [])

  return (
    <motion.header
      className={`fixed top-4 left-4 right-4 z-50 transition-all duration-300
        ${scrolled
          ? 'backdrop-blur-xl bg-white/80 dark:bg-gray-950/80 border border-gray-200/50 dark:border-white/10 shadow-lg shadow-gray-900/10'
          : 'bg-transparent border border-transparent'
        } rounded-2xl`}
      initial={{ y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.3, duration: 0.6, ease: [0.21, 0.47, 0.32, 0.98] }}
    >
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="font-black text-xl tracking-tight">
          <span className="text-indigo-600">Logo</span>
        </Link>

        {/* Links */}
        <div className="hidden md:flex items-center gap-8">
          {['Produto', 'Precos', 'Blog', 'Docs'].map(item => (
            <Link
              key={item}
              href={`/${item.toLowerCase()}`}
              className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors font-medium"
            >
              {item}
            </Link>
          ))}
        </div>

        {/* CTA */}
        <div className="flex items-center gap-3">
          <Link href="/login" className="text-sm font-medium text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
            Entrar
          </Link>
          <Link href="/signup" className="px-5 py-2.5 bg-gray-950 dark:bg-white text-white dark:text-gray-950 text-sm font-semibold rounded-full hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors">
            Comecar
          </Link>
        </div>
      </nav>
    </motion.header>
  )
}
```

---

## Pricing Section Premium

```tsx
const plans = [
  { name: "Starter",   price: 0,   period: "mes", popular: false, cta: "Comecar Gratis",
    features: ["5 projetos", "1GB storage", "Suporte email"] },
  { name: "Pro",       price: 97,  period: "mes", popular: true,  cta: "Comecar Agora",
    features: ["Projetos ilimitados", "50GB storage", "Suporte 24/7", "Dominios customizados", "Analytics avancado"] },
  { name: "Enterprise",price: 297, period: "mes", popular: false, cta: "Falar com equipe",
    features: ["Tudo do Pro", "SLA 99.99%", "Onboarding dedicado", "SSO / SAML", "Suporte prioritario"] },
]

export function PricingSection() {
  return (
    <section className="py-24 bg-gray-50 dark:bg-gray-950">
      <div className="max-w-6xl mx-auto px-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-black mb-4">Planos simples e transparentes</h2>
          <p className="text-gray-500 text-lg">Sem surpresas. Cancele quando quiser.</p>
        </motion.div>

        <motion.div
          className="grid md:grid-cols-3 gap-6 items-start"
          variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
          initial="hidden" whileInView="visible" viewport={{ once: true }}
        >
          {plans.map(plan => (
            <motion.div
              key={plan.name}
              variants={{ hidden: { opacity: 0, y: 24 }, visible: { opacity: 1, y: 0 } }}
              className={`relative rounded-3xl p-8 ${
                plan.popular
                  ? 'bg-gray-950 dark:bg-white text-white dark:text-gray-950 shadow-2xl shadow-gray-900/30 scale-105'
                  : 'bg-white dark:bg-gray-900 border border-gray-200 dark:border-white/[0.06]'
              }`}
            >
              {plan.popular && (
                <span className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-bold px-4 py-1.5 rounded-full">
                  MAIS POPULAR
                </span>
              )}

              <h3 className="text-lg font-bold mb-2">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-3xl font-black tabular-nums">
                  {plan.price === 0 ? 'Gratis' : `R$${plan.price}`}
                </span>
                {plan.price > 0 && <span className="text-sm opacity-60">/{plan.period}</span>}
              </div>

              <ul className="space-y-3 mb-8">
                {plan.features.map(f => (
                  <li key={f} className="flex items-center gap-3 text-sm">
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 ${
                      plan.popular ? 'bg-white/20' : 'bg-indigo-50 dark:bg-indigo-950'
                    }`}>
                      <Check className={`w-3 h-3 ${plan.popular ? 'text-white' : 'text-indigo-600'}`} />
                    </div>
                    {f}
                  </li>
                ))}
              </ul>

              <button className={`w-full py-3 rounded-2xl font-semibold transition-all duration-200 ${
                plan.popular
                  ? 'bg-white dark:bg-gray-950 text-gray-950 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
                  : 'bg-gray-950 dark:bg-white text-white dark:text-gray-950 hover:bg-gray-800 dark:hover:bg-gray-100'
              }`}>
                {plan.cta}
              </button>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
```

---

## FAQ com Accordion Animado

```tsx
'use client'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'

const faqs = [
  { q: "Como funciona o periodo de teste?", a: "Voce tem 14 dias de teste gratuito sem precisar de cartao de credito. Cancele a qualquer momento." },
  { q: "Posso mudar de plano depois?", a: "Sim! Voce pode fazer upgrade ou downgrade do seu plano a qualquer momento." },
  { q: "Quais formas de pagamento sao aceitas?", a: "Aceitamos todos os cartoes de credito, PIX e boleto bancario." },
]

export function FAQ() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <section className="py-24">
      <div className="max-w-3xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="text-4xl font-black mb-4">Perguntas frequentes</h2>
        </motion.div>

        <div className="space-y-3">
          {faqs.map((faq, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.07 }} viewport={{ once: true }}
              className="rounded-2xl border border-gray-200 dark:border-white/[0.07] bg-white dark:bg-gray-900 overflow-hidden"
            >
              <button
                onClick={() => setOpen(open === i ? null : i)}
                className="w-full flex items-center justify-between p-6 text-left font-semibold hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
              >
                {faq.q}
                <motion.div animate={{ rotate: open === i ? 180 : 0 }} transition={{ duration: 0.25 }}>
                  <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
                </motion.div>
              </button>
              <AnimatePresence>
                {open === i && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                  >
                    <p className="px-6 pb-6 text-gray-500 dark:text-gray-400 leading-relaxed">{faq.a}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
```

---

## CTA Section Final

```tsx
// CTA dramatico (dark)
export function CTASection() {
  return (
    <section className="relative py-32 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-purple-700 to-pink-600" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_50%,rgba(0,0,0,0.3),transparent)]" />
      <RetroGrid className="absolute inset-0 opacity-20" />

      <motion.div
        initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="relative text-center text-white max-w-4xl mx-auto px-6"
      >
        <h2 className="text-5xl md:text-7xl font-black tracking-tight mb-6">
          Pronto para comecar?
        </h2>
        <p className="text-xl text-white/75 mb-12 max-w-2xl mx-auto">
          Junte-se a mais de 2.400 times que ja usam nossa plataforma.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button className="px-10 py-5 bg-white text-gray-950 font-bold rounded-full text-lg
            hover:bg-gray-100 shadow-2xl shadow-black/30 hover:shadow-white/25
            transition-all duration-300 hover:-translate-y-1">
            Comecar Gratis
          </button>
          <button className="px-10 py-5 border-2 border-white/30 text-white font-bold rounded-full text-lg
            hover:border-white/70 hover:bg-white/10 transition-all duration-300">
            Falar com equipe
          </button>
        </div>
        <p className="text-white/50 text-sm mt-6">Sem cartao de credito. Cancele quando quiser.</p>
      </motion.div>
    </section>
  )
}
```

---

## Logo Wall (Social Proof)

```tsx
// Marquee de logos com fade nas bordas
export function LogoWall({ logos }) {
  return (
    <section className="py-12 bg-gray-50 dark:bg-gray-950">
      <p className="text-center text-sm text-gray-400 dark:text-gray-600 font-medium tracking-widest uppercase mb-8">
        Usado por times de empresas como
      </p>
      <div className="relative">
        {/* Fade lateral */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-50 dark:from-gray-950 to-transparent z-10 pointer-events-none" />
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-50 dark:from-gray-950 to-transparent z-10 pointer-events-none" />

        <Marquee pauseOnHover className="[--duration:35s]">
          {logos.map(logo => (
            <div key={logo.name} className="mx-12 flex items-center opacity-40 hover:opacity-70 grayscale hover:grayscale-0 transition-all duration-300">
              <img src={logo.src} alt={logo.name} className="h-8 w-auto" />
            </div>
          ))}
        </Marquee>
      </div>
    </section>
  )
}
```

---

## Footer Elegante

```tsx
export function Footer() {
  return (
    <footer className="border-t border-gray-200 dark:border-white/[0.06] bg-white dark:bg-gray-950">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-12 mb-12">
          {/* Brand */}
          <div className="col-span-2">
            <span className="text-xl font-black text-indigo-600 block mb-4">Logo</span>
            <p className="text-gray-500 dark:text-gray-400 text-sm leading-relaxed max-w-xs">
              A plataforma mais rapida para construir produtos incriveis.
            </p>
          </div>

          {/* Links */}
          {[
            { title: "Produto",  links: ["Funcionalidades", "Precos", "Changelog", "Roadmap"] },
            { title: "Empresa",  links: ["Sobre", "Blog", "Carreiras", "Imprensa"] },
            { title: "Suporte",  links: ["Docs", "Status", "Comunidade", "Contato"] },
          ].map(col => (
            <div key={col.title}>
              <h4 className="font-semibold text-sm mb-4 text-gray-900 dark:text-white">{col.title}</h4>
              <ul className="space-y-3">
                {col.links.map(l => (
                  <li key={l}>
                    <a href="#" className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors">
                      {l}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-gray-200 dark:border-white/[0.06] flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-gray-400">© 2025 Logo. Todos os direitos reservados.</p>
          <div className="flex items-center gap-6">
            {["Privacidade", "Termos", "Cookies"].map(l => (
              <a key={l} href="#" className="text-sm text-gray-400 hover:text-gray-600 transition-colors">{l}</a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
```

---

## Orbiting Circles: Hero Integration (MagicUI)

```tsx
// Hero com orbiting circles como elemento visual
<div className="relative h-[500px] w-[500px] mx-auto">
  {/* Centro */}
  <div className="absolute inset-0 flex items-center justify-center">
    <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-indigo-500/40">
      <Logo className="w-10 h-10 text-white" />
    </div>
  </div>

  {/* Orbita interna */}
  <OrbitingCircles radius={120} duration={15}>
    <div className="w-10 h-10 rounded-xl bg-white shadow-lg flex items-center justify-center">
      <Github className="w-5 h-5" />
    </div>
  </OrbitingCircles>
  <OrbitingCircles radius={120} duration={15} delay={5}>
    <div className="w-10 h-10 rounded-xl bg-white shadow-lg flex items-center justify-center">
      <Slack className="w-5 h-5" />
    </div>
  </OrbitingCircles>
  <OrbitingCircles radius={120} duration={15} delay={10}>
    <div className="w-10 h-10 rounded-xl bg-white shadow-lg flex items-center justify-center">
      <Figma className="w-5 h-5" />
    </div>
  </OrbitingCircles>

  {/* Orbita externa */}
  <OrbitingCircles radius={200} duration={25} reverse>
    <img src="/logos/vercel.svg" className="w-8 h-8" />
  </OrbitingCircles>
  <OrbitingCircles radius={200} duration={25} reverse delay={8}>
    <img src="/logos/nextjs.svg" className="w-8 h-8" />
  </OrbitingCircles>
</div>
```

---

## Bento Grid Premium (MagicUI)

```tsx
const features = [
  {
    Icon: Zap,
    name: "Velocidade extrema",
    description: "Deploy em segundos. Infraestrutura edge em 40+ regioes.",
    className: "col-span-3 lg:col-span-1",
    href: "#",
    cta: "Saber mais",
    background: (
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 to-purple-500/10">
        <RetroGrid className="opacity-30" />
      </div>
    ),
  },
  {
    Icon: Globe,
    name: "Alcance global",
    description: "CDN distribuido em 300+ pontos de presenca ao redor do mundo.",
    className: "col-span-3 lg:col-span-2",
    href: "#",
    cta: "Ver cobertura",
    background: (
      <Globe className="absolute right-4 top-4 opacity-30" config={{ width: 300, height: 300 }} />
    ),
  },
  {
    Icon: Shield,
    name: "Seguranca enterprise",
    description: "SOC2, GDPR, ISO 27001. Seus dados protegidos.",
    className: "col-span-3 lg:col-span-2",
    href: "#",
    cta: "Ver conformidade",
    background: (
      <OrbitingCircles radius={80} duration={10} className="absolute right-0 top-0 opacity-20">
        <Shield className="w-4 h-4" />
      </OrbitingCircles>
    ),
  },
  {
    Icon: BarChart3,
    name: "Analytics em tempo real",
    description: "Monitore performance, erros e usuarios ao vivo.",
    className: "col-span-3 lg:col-span-1",
    href: "#",
    cta: "Ver demo",
    background: <div className="absolute inset-0 bg-gradient-to-t from-amber-500/10 to-transparent" />,
  },
]

<BentoGrid className="lg:grid-rows-2 max-w-6xl mx-auto">
  {features.map(f => (
    <BentoCard key={f.name} {...f} />
  ))}
</BentoGrid>
```

---

## Cards com Gradiente de Borda

```tsx
// Border gradient card (CSS trick)
<div className="p-[1px] rounded-2xl bg-gradient-to-br from-indigo-500/50 via-purple-500/30 to-pink-500/50">
  <div className="rounded-2xl bg-white dark:bg-gray-950 p-8">
    {/* conteudo */}
  </div>
</div>

// Com hover effect
<div className="relative p-[1px] rounded-2xl group">
  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
  <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-gray-200 to-gray-300 dark:from-white/[0.07] dark:to-white/[0.03]" />
  <div className="relative rounded-2xl bg-white dark:bg-gray-950 p-8">
    {/* conteudo */}
  </div>
</div>
```

---

## Imagem com Tratamento Premium

```tsx
// Imagem com blur placeholder e lazy load
<div className="relative overflow-hidden rounded-2xl">
  <img
    src="/hero-image.jpg"
    alt="Descricao"
    loading="lazy"
    className="w-full h-full object-cover transition-transform duration-700 hover:scale-105"
  />
  {/* Overlay gradiente no bottom */}
  <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent" />
</div>

// Avatar stack (social proof)
<div className="flex -space-x-3">
  {users.map((user, i) => (
    <div
      key={user.id}
      className="w-10 h-10 rounded-full border-2 border-white dark:border-gray-950 overflow-hidden"
      style={{ zIndex: users.length - i }}
    >
      <img src={user.avatar} alt={user.name} className="w-full h-full object-cover" />
    </div>
  ))}
  <div className="w-10 h-10 rounded-full border-2 border-white dark:border-gray-950 bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-xs font-bold text-indigo-600">
    +{extraCount}
  </div>
</div>
```

---

## Decisao: Qual Padrao Usar?

| Situacao | Padrao Recomendado |
|----------|-------------------|
| Hero SaaS dark | Aurora + DotPattern + Mockup Safari |
| Hero produto light | Radial glow + GridPattern + Imagem |
| Features | Bento Grid ou card grid com stagger |
| Stats | Section colorida + NumberTicker |
| Testimonials | Marquee vertical duplo |
| Logos | Marquee horizontal com grayscale |
| Pricing | 3 planos com destaque no central |
| FAQ | Accordion com AnimatePresence |
| CTA Final | Gradient colorido + RetroGrid |
| Footer | Grid 5 colunas + border top |
