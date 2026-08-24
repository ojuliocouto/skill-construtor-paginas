# Visual Assets: Integracao Completa

Videos de fundo, Lottie, Ilustracoes, Icones animados, Backgrounds.

---

## Videos de Fundo: Integracao

### Video Background Basico

```tsx
// Hero com video de fundo (padrao mais impactante)
export function VideoHero() {
  return (
    <section className="relative h-screen overflow-hidden">
      {/* Video de fundo */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover"
        poster="/hero-poster.jpg"  {/* imagem enquanto video carrega */}
      >
        <source src="/videos/hero.mp4"  type="video/mp4" />
        <source src="/videos/hero.webm" type="video/webm" />
      </video>

      {/* Overlay para legibilidade do texto */}
      <div className="absolute inset-0 bg-black/55" />

      {/* Conteudo sobre o video */}
      <div className="relative z-10 flex flex-col items-center justify-center h-full text-white text-center px-6">
        <motion.h1
          initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
          className="text-6xl md:text-8xl font-black tracking-tight"
        >
          Headline Aqui
        </motion.h1>
      </div>
    </section>
  )
}
```

### Video Hero com Gradiente (mais elegante que overlay solido)

```tsx
<section className="relative h-screen overflow-hidden">
  <video autoPlay loop muted playsInline
    className="absolute inset-0 w-full h-full object-cover scale-105">
    <source src="/videos/hero.mp4" type="video/mp4" />
  </video>

  {/* Gradiente direcional, muito mais premium que bg-black/50 */}
  <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/40 to-transparent" />
  {/* Fade no rodape */}
  <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-gray-950 to-transparent" />

  <div className="relative z-10 max-w-7xl mx-auto px-6 h-full flex items-center">
    <div className="max-w-2xl">
      <h1 className="text-7xl font-black text-white mb-6">...</h1>
      <p className="text-xl text-white/75">...</p>
    </div>
  </div>
</section>
```

### Video em Secao (nao fullscreen)

```tsx
{/* Video em card/mockup */}
<div className="relative rounded-3xl overflow-hidden aspect-video max-w-4xl mx-auto">
  <video autoPlay loop muted playsInline className="w-full h-full object-cover">
    <source src="/videos/product-demo.mp4" type="video/mp4" />
  </video>
  {/* Overlay sutil de glass */}
  <div className="absolute inset-0 rounded-3xl ring-1 ring-inset ring-white/10" />
</div>

{/* Video como background de uma feature card */}
<div className="relative rounded-2xl overflow-hidden group">
  <video autoPlay loop muted playsInline
    className="absolute inset-0 w-full h-full object-cover opacity-30 group-hover:opacity-50 transition-opacity duration-500">
    <source src="/videos/feature-bg.mp4" type="video/mp4" />
  </video>
  <div className="relative p-8 z-10">
    {/* conteudo do card */}
  </div>
</div>
```

### Parar video quando fora da viewport (performance)

```tsx
'use client'
import { useRef, useEffect } from 'react'

function LazyVideo({ src, className = '' }) {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) video.play().catch(() => {})
        else video.pause()
      },
      { threshold: 0.25 }
    )
    observer.observe(video)
    return () => observer.disconnect()
  }, [])

  return (
    <video ref={videoRef} loop muted playsInline className={className}>
      <source src={src} type="video/mp4" />
    </video>
  )
}
```

### Otimizacao de Video

```bash
# Comprimir com ffmpeg (instalar: brew install ffmpeg)
# MP4 otimizado para web (alvo: < 5MB para hero, < 2MB para secoes)
ffmpeg -i input.mp4 \
  -vcodec libx264 -crf 28 -preset slow \
  -vf "scale=1920:-2" \
  -an \
  output.mp4

# WebM (melhor compressao, compativel com Chrome/Firefox)
ffmpeg -i input.mp4 \
  -c:v libvpx-vp9 -crf 35 -b:v 0 \
  -vf "scale=1920:-2" \
  -an \
  output.webm

# Gerar poster image (thumbnail para loading)
ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 poster.jpg
```

---

## Lottie Animations

### Setup

```bash
npm install @lottiefiles/react-lottie-player
# ou mais leve:
npm install lottie-react
```

### Onde Encontrar

- **LottieFiles Free**: https://lottiefiles.com/free-animations
- **LottieFiles Search**: https://lottiefiles.com/search?q=...

### Uso com react-lottie-player

```tsx
'use client'
import { Player } from '@lottiefiles/react-lottie-player'

// URL direta do LottieFiles
<Player
  autoplay
  loop
  src="https://assets10.lottiefiles.com/packages/lf20_XXXXX.json"
  style={{ width: 300, height: 300 }}
/>

// Arquivo local (baixe o .json em public/animations/)
<Player
  autoplay
  loop
  src="/animations/hero.json"
  style={{ width: 400, height: 400 }}
  className="mx-auto"
/>

// Controle de play (ex: ao entrar na viewport)
'use client'
import { useRef } from 'react'
import { Player } from '@lottiefiles/react-lottie-player'

function AnimatedOnView() {
  const playerRef = useRef(null)
  const { ref, inView } = useInView()

  useEffect(() => {
    if (inView) playerRef.current?.play()
  }, [inView])

  return (
    <div ref={ref}>
      <Player ref={playerRef} src="/animations/rocket.json" style={{ width: 200 }} />
    </div>
  )
}
```

### Uso com lottie-react (mais leve, sem deps extras)

```tsx
'use client'
import Lottie from 'lottie-react'
import animationData from '@/public/animations/success.json'

// Loop
<Lottie animationData={animationData} loop className="w-48 h-48 mx-auto" />

// Play once (success state)
<Lottie animationData={animationData} loop={false} className="w-32 h-32" />

// Com controle de velocidade
<Lottie
  animationData={animationData}
  loop={true}
  speed={0.8}
  className="w-64 h-64"
/>
```

### Casos de Uso por Secao

| Secao | Lottie Ideal | Query no LottieFiles |
|-------|-------------|---------------------|
| Hero | Rocket, launch, abstract wave | "rocket launch", "abstract wave" |
| Features | Ícone animado por feature | "security shield", "speed fast", "cloud" |
| Loading state | Spinner, dots | "loading spinner minimal" |
| Success state | Checkmark, confetti | "success checkmark", "celebration" |
| Empty state | Empty box, search | "empty state", "no results" |
| 404 | Robot, astronaut | "404 error page", "lost astronaut" |
| Onboarding | Person, guide | "onboarding welcome" |

---

## Ilustracoes SVG

### unDraw (gratuito, open source)

```tsx
// 1. Buscar em: https://undraw.co/illustrations
// 2. Escolher cor primaria (ex: #6366f1 para indigo)
// 3. Baixar SVG
// 4. Salvar em public/illustrations/nome.svg

import Image from 'next/image'

<Image
  src="/illustrations/hero-team.svg"
  alt="Time trabalhando junto"
  width={500}
  height={400}
  className="w-full max-w-lg"
/>

// Com animacao de entrada
<motion.div
  initial={{ opacity: 0, scale: 0.9, y: 20 }}
  animate={{ opacity: 1, scale: 1, y: 0 }}
  transition={{ duration: 0.8, ease: "backOut" }}
>
  <Image src="/illustrations/hero.svg" alt="..." width={500} height={400} />
</motion.div>
```

### unDraw API (mudar cor dinamicamente)

```tsx
// URL com cor customizavel
const color = "6366f1"  // hex sem #
const illustration = "team-work"

<img
  src={`https://undraw.co/api/illustrations?q=${illustration}&color=${color}`}
  alt="Team working"
  className="w-full max-w-md mx-auto"
/>
```

### Storyset (animadas com CSS)

```tsx
// Storyset fornece SVGs que animam via CSS classes
// Baixe o SVG animado e inclua o CSS deles

<img
  src="/illustrations/storyset-hero.svg"
  alt="..."
  className="w-full max-w-xl"
/>
```

### Ilustracao em Hero (lado a lado)

```tsx
<section className="min-h-screen flex items-center py-24">
  <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
    {/* Texto */}
    <motion.div initial={{ opacity: 0, x: -30 }} animate={{ opacity: 1, x: 0 }}>
      <h1 className="text-6xl font-black mb-6">Headline</h1>
      <p className="text-xl text-gray-500 mb-10">Subheadline</p>
      <button className="...">CTA</button>
    </motion.div>

    {/* Ilustracao */}
    <motion.div
      initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.2 }}
      className="relative"
    >
      {/* Blob decorativo atras */}
      <div className="absolute inset-0 bg-indigo-100 dark:bg-indigo-950/30 rounded-full blur-3xl scale-90" />
      <Image
        src="/illustrations/hero.svg"
        alt="..."
        width={600} height={500}
        className="relative w-full"
      />
    </motion.div>
  </div>
</section>
```

---

## Icones Animados

### LordIcon (Lottie icons, free tier generoso)

```tsx
// 1. Adicionar script no layout.tsx (uma vez so)
import Script from 'next/script'
<Script src="https://cdn.lordicon.com/lordicon.js" strategy="lazyOnload" />

// 2. Usar em qualquer lugar
<lord-icon
  src="https://cdn.lordicon.com/XXXXX.json"
  trigger="hover"
  colors="primary:#6366f1,secondary:#a855f7"
  style={{ width: 64, height: 64 }}
/>

// Triggers disponiveis:
// hover, click, loop, loop-on-hover, morph, morph-two-way, sequence

// TypeScript fix
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'lord-icon': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        src?: string; trigger?: string; colors?: string; target?: string
      }
    }
  }
}
```

### Feature Cards com Icone Animado

```tsx
{features.map(f => (
  <div key={f.title} className="group p-8 rounded-3xl border hover:border-indigo-500/30 transition-all">
    {/* Icone anima ao hover do card */}
    <lord-icon
      src={f.lordIconSrc}
      trigger="hover"
      target=".group"
      colors="primary:#6366f1"
      style={{ width: 56, height: 56 }}
    />
    <h3 className="text-xl font-bold mt-4 mb-2">{f.title}</h3>
    <p className="text-gray-500">{f.description}</p>
  </div>
))}
```

### Lucide com Hover Animation (sem dependencia extra)

```tsx
// Icone que gira no hover
<div className="group p-4 rounded-2xl bg-indigo-50 dark:bg-indigo-950 w-fit">
  <Zap className="w-8 h-8 text-indigo-600
    group-hover:rotate-12 group-hover:scale-110
    transition-transform duration-300" />
</div>

// Icone que "salta" no hover do card pai
<div className="group p-8 rounded-3xl border hover:-translate-y-1 transition-all">
  <div className="w-12 h-12 rounded-2xl bg-indigo-50 flex items-center justify-center mb-4
    group-hover:scale-110 group-hover:bg-indigo-100 transition-all duration-300">
    <Shield className="w-6 h-6 text-indigo-600" />
  </div>
  ...
</div>

// Icone de seta que avanca no hover do botao
<button className="group flex items-center gap-2 text-indigo-600 font-semibold hover:gap-3 transition-all">
  Saiba mais
  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
</button>
```

---

## Backgrounds SVG e Patterns

### SVG Background Inline (zero dependencia, zero HTTP request)

```tsx
// Dots pattern customizavel
function DotsBg({ color = "#6366f1", opacity = 0.15, size = 20 }) {
  const svgCode = encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
      <circle cx="${size/2}" cy="${size/2}" r="1.5" fill="${color}" />
    </svg>
  `)
  return (
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: `url("data:image/svg+xml,${svgCode}")`,
        backgroundSize: `${size}px ${size}px`,
        opacity,
      }}
    />
  )
}

// Lines diagonal pattern
function DiagonalLines({ color = "#6366f1", opacity = 0.08 }) {
  const svg = encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">
      <line x1="0" y1="40" x2="40" y2="0" stroke="${color}" stroke-width="1"/>
    </svg>
  `)
  return (
    <div className="absolute inset-0"
      style={{ backgroundImage: `url("data:image/svg+xml,${svg}")`, backgroundSize: "40px 40px", opacity }} />
  )
}

// Grid crosshatch
function GridBg({ color = "#e2e8f0", opacity = 1 }) {
  return (
    <div
      className="absolute inset-0"
      style={{
        backgroundImage: `
          linear-gradient(${color} 1px, transparent 1px),
          linear-gradient(90deg, ${color} 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
        opacity,
      }}
    />
  )
}
```

### Noise Texture Premium

```tsx
// Gerar noise.png em: https://grainy-gradients.vercel.app
// Salvar em public/textures/noise.png

// Aplicar como pseudo-elemento global (globals.css)
/*
body::after {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.03;
  background-image: url('/textures/noise.png');
}
*/

// Ou em componente especifico
<div className="relative">
  <div
    className="absolute inset-0 opacity-[0.04] pointer-events-none mix-blend-overlay"
    style={{ backgroundImage: "url('/textures/noise.png')" }}
  />
  {/* conteudo */}
</div>
```

### Haikei: Waves SVG

```tsx
// Gerar em: https://app.haikei.app
// Tipo: Wave, Blob, Low Poly, Stacked Waves, etc.
// Exportar como SVG e salvar em public/

// Wave entre secoes
<div className="relative h-24 overflow-hidden">
  <img
    src="/dividers/wave-light.svg"
    alt=""
    className="absolute bottom-0 w-full"
    aria-hidden="true"
  />
</div>

// Blob decorativo
<div className="absolute top-0 right-0 w-1/2 h-1/2 opacity-20 pointer-events-none">
  <img src="/decorations/blob-indigo.svg" alt="" aria-hidden="true" />
</div>
```

---

## Workflow Completo: Assets para Uma Pagina

### Ordem de decisao

```
1. VIDEO ou IMAGEM no hero?
   ├── Video: python3 assets-search.py "tech dark abstract"
   └── Imagem: python3 assets-search.py "hero dark minimal" --type photo

2. ILUSTRACAO ou MOCKUP na secao de produto?
   ├── App/SaaS: Safari ou iPhone15Pro mockup (MagicUI) com screenshot real
   └── Servico/conceito: Ilustracao unDraw em /illustrations/

3. ICONES das features?
   ├── Simples: Lucide (ja instalado com shadcn)
   └── Animados: LordIcon (hover trigger no card)

4. BACKGROUND das secoes secundarias?
   ├── Hero: aurora gradient (CSS puro, zero HTTP)
   ├── Features: DotPattern ou GridPattern (MagicUI)
   └── Stats/CTA: RetroGrid ou gradient colorido

5. ANIMACOES de transicao?
   ├── Loading/success: Lottie de LottieFiles
   └── Icones: LordIcon ou Lucide com CSS transition
```

### Checklist de Assets

- [ ] Video/imagem hero baixado e otimizado (< 5MB video, < 200KB imagem)
- [ ] Poster image do video gerado (previne flash branco)
- [ ] Ilustracao SVG em public/illustrations/ se necessario
- [ ] Lottie .json em public/animations/ se necessario
- [ ] Noise texture em public/textures/noise.png
- [ ] Todos os assets com lazy loading
- [ ] alt text em todas as imagens decorativas (pode ser "")
- [ ] Video com autoPlay muted playsInline (obrigatorio para autoplay mobile)
