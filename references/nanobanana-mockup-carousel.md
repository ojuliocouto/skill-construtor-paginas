# Nanobanana + Mockup Carousel: Geração de Imagens + Device Showcase

Workflow completo: gerar screenshots de app com Nanobanana → inserir em mockups de device → carousel premium com Framer Motion.

---

## Quando Usar

| Situação | Usar | Alternativa |
|----------|------|-------------|
| Mostrar interface de um app/SaaS | ✅ iPhone15Pro ou Safari mockup | Screenshot bruto |
| Hero de landing page de produto digital | ✅ Mockup em perspectiva 3D | Imagem plana |
| Múltiplas funcionalidades | ✅ Carousel de mockups | Grid estático |
| Sem screenshot real do produto | ✅ Nanobanana gera o visual | Placeholder vazio |
| Curso ou infoproduto | ✅ Mockup mostrando a plataforma | Capa do eBook |
| Testimonials com foto de resultado | ⚠️ Captura de tela real preferível |: |

---

## Step 1: Gerar Imagens com Nanobanana

### Setup rápido

```bash
# Verificar se skill está disponível
ls ~/.claude/skills/nanobanana/

# Config com GEMINI_API_KEY
cat ~/.claude/skills/nanobanana/config.json
```

### Script de geração de mockup de app

Antes de rodar o pipeline abaixo, salve o bloco de código a seguir como
`scripts/generate-app-mockup.py` (o script não vem pronto no repo):

```bash
mkdir -p scripts
# cole o conteúdo do bloco Python abaixo em scripts/generate-app-mockup.py
```

```python
#!/usr/bin/env python3
"""
generate-app-mockup.py
Gera screenshot de interface de app com Nanobanana (Gemini 3 Pro Image)
"""

import os
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

def get_api_key():
    config_path = Path.home() / '.claude' / 'skills' / 'nanobanana' / 'config.json'
    key = os.environ.get('GEMINI_API_KEY') or (
        json.loads(config_path.read_text()).get('GEMINI_API_KEY') if config_path.exists() else None
    )
    if not key:
        raise ValueError("GEMINI_API_KEY não encontrada")
    return key

def generate_mockup(prompt: str, output_name: str = 'mockup', aspect: str = '9:16') -> Path:
    """
    aspect: '9:16' para mobile, '16:9' para desktop/tablet, '1:1' para ícone
    """
    api_key = get_api_key()

    # Aspect ratio para width/height
    ratio_map = {
        '9:16': {'width': 1080, 'height': 1920},
        '16:9': {'width': 1920, 'height': 1080},
        '4:3':  {'width': 1600, 'height': 1200},
        '1:1':  {'width': 1024, 'height': 1024},
    }
    dims = ratio_map.get(aspect, ratio_map['9:16'])

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={api_key}"

    payload = json.dumps({
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "candidateCount": 1,
        }
    }).encode()

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')

    with urllib.request.urlopen(req, timeout=120) as response:
        result = json.loads(response.read())

    # Extrair imagem base64
    for part in result['candidates'][0]['content']['parts']:
        if part.get('inlineData'):
            image_data = part['inlineData']['data']
            mime_type = part['inlineData']['mimeType']
            ext = 'png' if 'png' in mime_type else 'jpg'

            timestamp = datetime.now().strftime('%H%M%S')
            output_path = Path(f'/tmp/{output_name}-{timestamp}.{ext}')
            output_path.write_bytes(base64.b64decode(image_data))
            print(f"✅ Imagem: {output_path} ({output_path.stat().st_size // 1024}KB)")
            return output_path

    raise ValueError("Sem imagem na resposta")

# ============================================================
# PROMPTS PRONTOS, Copy e adapte ao produto
# ============================================================

# Mobile app UI
PROMPT_MOBILE_DARK = """
Professional mobile app UI screenshot, dark mode, showing a WhatsApp automation dashboard.
Interface elements: chat list with status indicators, quick reply buttons, active bot toggle,
message templates panel. Purple and dark navy color scheme. Clean modern design, iOS style,
high resolution 1080x1920, realistic UI, no text on outside, app screen only, centered.
"""

PROMPT_MOBILE_ANALYTICS = """
Mobile analytics app screenshot, dark mode. Shows daily revenue graph in purple/green gradient,
conversion rate donut chart, recent transactions list with green checkmarks. Bottom navigation
bar. Professional fintech aesthetic. iOS design, high resolution, centered, realistic.
"""

PROMPT_DESKTOP_SAAS = """
SaaS dashboard screenshot, dark mode. Left sidebar with navigation icons, main content area
with data visualizations, top header with user avatar. Purple accent colors (#7F41F9),
dark background (#0f0f1a). Glassmorphism cards with gradient borders. High resolution 1920x1080.
Professional software UI, no lorem ipsum, realistic data, centered.
"""

PROMPT_COURSE_PLATFORM = """
Online course platform interface, clean modern design. Shows lesson list on left, video player
in center (dark thumbnail), lesson description below, progress bar at top showing 65% complete.
Orange accent colors, white background. Professional e-learning aesthetic. 1920x1080.
"""

if __name__ == '__main__':
    import sys
    prompt_text = sys.argv[1] if len(sys.argv) > 1 else PROMPT_MOBILE_DARK
    name = sys.argv[2] if len(sys.argv) > 2 else 'app-screenshot'
    aspect = sys.argv[3] if len(sys.argv) > 3 else '9:16'

    path = generate_mockup(prompt_text, name, aspect)
    print(f"\nPróximo passo: converter para WebP")
    print(f"  cwebp -q 88 '{path}' -o '{path.stem}.webp'")
```

### Converter para WebP após gerar

```bash
# Single
cwebp -q 88 /tmp/mockup-123456.png -o /tmp/mockup.webp

# Batch (todos os PNGs)
for f in /tmp/mockup-*.png; do
  cwebp -q 88 "$f" -o "${f%.png}.webp" && echo "✅ ${f%.png}.webp"
done
```

---

## Step 2: Inserir em Device Mockups (Magic UI)

### Instalação

```bash
# iPhone 15 Pro
npx magicui-cli@latest add iphone-15-pro

# Safari browser frame
npx magicui-cli@latest add safari

# Android
npx magicui-cli@latest add android
```

### iPhone 15 Pro: Uso correto

```tsx
import { Iphone15Pro } from '@/components/magicui/iphone-15-pro'

// Básico
<Iphone15Pro
  src="/images/app-screenshot.webp"
  width={433}
  height={882}
/>

// Com animação de entrada
<motion.div
  initial={{ opacity: 0, y: 40, rotateX: 15 }}
  animate={{ opacity: 1, y: 0, rotateX: 0 }}
  transition={{ delay: 0.3, duration: 1, ease: [0.21, 0.47, 0.32, 0.98] }}
  style={{ transformPerspective: 800 }}
>
  <Iphone15Pro
    src="/images/app-screenshot.webp"
    width={300}
    height={610}
    className="drop-shadow-2xl"
  />
</motion.div>

// Flutuando
<div className="animate-float relative">
  <div className="absolute -inset-4 bg-purple-500/20 blur-2xl" />
  <Iphone15Pro src="/images/screen.webp" className="relative" />
</div>
```

### Safari (browser frame): Para mostrar web apps/dashboards

```tsx
import { Safari } from '@/components/magicui/safari'

<Safari
  url="app.seusite.com"
  src="/images/dashboard.webp"
  width={1200}
  height={750}
  className="w-full"
/>

// Com glow
<div className="relative">
  <div className="absolute -inset-8 bg-gradient-to-r from-purple-500/20 to-orange-500/20 blur-3xl rounded-3xl" />
  <Safari
    url="app.seusite.com.br/dashboard"
    src="/images/dashboard.webp"
    className="relative w-full max-w-4xl mx-auto drop-shadow-2xl"
  />
</div>
```

### Dois mockups sobrepostos (desktop + mobile)

```tsx
<div className="relative mx-auto max-w-5xl">
  {/* Safari principal */}
  <Safari
    url="seuapp.com"
    src="/images/dashboard.webp"
    className="w-full"
  />
  {/* iPhone sobreposto no canto inferior direito */}
  <div className="absolute -bottom-8 -right-4 md:-right-12 w-1/4">
    <Iphone15Pro
      src="/images/mobile.webp"
      className="drop-shadow-2xl"
    />
  </div>
</div>
```

---

## Step 3: Carousel Premium com Framer Motion

### Carousel básico com swipe

```tsx
'use client'
import { useState, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion'
import { Iphone15Pro } from '@/components/magicui/iphone-15-pro'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface MockupSlide {
  id: string
  src: string
  title: string
  description: string
  tag?: string
}

interface MockupCarouselProps {
  slides: MockupSlide[]
  device?: 'iphone' | 'safari'
  height?: number
}

export function MockupCarousel({ slides, device = 'iphone', height = 600 }: MockupCarouselProps) {
  const [current, setCurrent] = useState(0)
  const [direction, setDirection] = useState(0)

  const navigate = (dir: 1 | -1) => {
    setDirection(dir)
    setCurrent(prev => (prev + dir + slides.length) % slides.length)
  }

  const variants = {
    enter: (dir: number) => ({
      x: dir > 0 ? 200 : -200,
      opacity: 0,
      scale: 0.92,
    }),
    center: { x: 0, opacity: 1, scale: 1 },
    exit: (dir: number) => ({
      x: dir > 0 ? -200 : 200,
      opacity: 0,
      scale: 0.92,
    }),
  }

  return (
    <div className="relative select-none">
      {/* Mockup */}
      <div className="relative flex items-center justify-center" style={{ height }}>
        <AnimatePresence custom={direction} mode="wait">
          <motion.div
            key={slides[current].id}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.4, ease: [0.21, 0.47, 0.32, 0.98] }}
            className="absolute"
          >
            {device === 'iphone' ? (
              <Iphone15Pro
                src={slides[current].src}
                width={280}
                height={570}
                className="drop-shadow-2xl"
              />
            ) : (
              <Safari
                url="seuapp.com"
                src={slides[current].src}
                className="w-[600px]"
              />
            )}
          </motion.div>
        </AnimatePresence>
      </div>

      {/* Texto descritivo */}
      <AnimatePresence mode="wait">
        <motion.div
          key={`text-${slides[current].id}`}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          className="text-center mt-6 px-4"
        >
          {slides[current].tag && (
            <span className="inline-block px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-semibold mb-2">
              {slides[current].tag}
            </span>
          )}
          <h3 className="text-xl font-bold text-white mb-2">{slides[current].title}</h3>
          <p className="text-gray-400 text-sm max-w-sm mx-auto">{slides[current].description}</p>
        </motion.div>
      </AnimatePresence>

      {/* Controles */}
      <div className="flex items-center justify-center gap-6 mt-6">
        <button
          onClick={() => navigate(-1)}
          className="w-10 h-10 rounded-full border border-white/10 bg-white/5 flex items-center justify-center
            hover:bg-white/10 hover:border-white/20 transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-white" />
        </button>

        {/* Dots */}
        <div className="flex gap-2">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => { setDirection(i > current ? 1 : -1); setCurrent(i) }}
              className={`h-2 rounded-full transition-all duration-300 ${
                i === current ? 'w-6 bg-purple-500' : 'w-2 bg-white/20 hover:bg-white/40'
              }`}
            />
          ))}
        </div>

        <button
          onClick={() => navigate(1)}
          className="w-10 h-10 rounded-full border border-white/10 bg-white/5 flex items-center justify-center
            hover:bg-white/10 hover:border-white/20 transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-white" />
        </button>
      </div>
    </div>
  )
}
```

### Carousel 3D (perspectiva: 3 cards visíveis)

```tsx
'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Iphone15Pro } from '@/components/magicui/iphone-15-pro'

export function Carousel3D({ slides }: { slides: MockupSlide[] }) {
  const [active, setActive] = useState(0)

  const getProps = (index: number) => {
    const total = slides.length
    const pos = ((index - active + total) % total)
    const normalized = pos > total / 2 ? pos - total : pos // -1, 0, 1, 2...

    return {
      x: normalized * 200,
      scale: normalized === 0 ? 1 : 0.75,
      zIndex: normalized === 0 ? 10 : 5 - Math.abs(normalized),
      opacity: Math.abs(normalized) > 1 ? 0 : normalized === 0 ? 1 : 0.5,
      rotateY: normalized * -20,
      filter: normalized === 0 ? 'brightness(1)' : 'brightness(0.6)',
    }
  }

  return (
    <div className="relative h-[600px] flex items-center justify-center" style={{ perspective: '1200px' }}>
      {slides.map((slide, i) => {
        const props = getProps(i)
        return (
          <motion.div
            key={slide.id}
            animate={{
              x: props.x,
              scale: props.scale,
              zIndex: props.zIndex,
              opacity: props.opacity,
              rotateY: props.rotateY,
              filter: props.filter,
            }}
            transition={{ duration: 0.5, ease: [0.21, 0.47, 0.32, 0.98] }}
            onClick={() => setActive(i)}
            className="absolute cursor-pointer"
            style={{ transformStyle: 'preserve-3d' }}
          >
            <Iphone15Pro src={slide.src} width={260} height={530} className="drop-shadow-2xl" />
          </motion.div>
        )
      })}

      {/* Navegação */}
      <div className="absolute bottom-0 left-0 right-0 flex justify-center gap-3">
        {slides.map((_, i) => (
          <button
            key={i}
            onClick={() => setActive(i)}
            className={`w-2 h-2 rounded-full transition-all ${i === active ? 'bg-purple-500 w-6' : 'bg-white/20'}`}
          />
        ))}
      </div>
    </div>
  )
}
```

### Carousel Auto-play com pausa no hover

```tsx
'use client'
import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export function AutoCarousel({ slides, interval = 3000 }: { slides: MockupSlide[], interval?: number }) {
  const [current, setCurrent] = useState(0)
  const [paused, setPaused] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval>>()

  useEffect(() => {
    if (!paused) {
      timerRef.current = setInterval(() => {
        setCurrent(prev => (prev + 1) % slides.length)
      }, interval)
    }
    return () => clearInterval(timerRef.current)
  }, [paused, slides.length, interval])

  return (
    <div
      className="relative"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={slides[current].id}
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -30 }}
          transition={{ duration: 0.4 }}
        >
          <Iphone15Pro src={slides[current].src} width={300} height={610} />
        </motion.div>
      </AnimatePresence>

      {/* Barra de progresso */}
      <div className="mt-4 h-1 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-purple-500 rounded-full"
          initial={{ width: '0%' }}
          animate={{ width: '100%' }}
          transition={{ duration: interval / 1000, ease: 'linear' }}
          key={current}
        />
      </div>
    </div>
  )
}
```

---

## Step 4: Montar Seção Completa de Produto

```tsx
// Seção completa: Feature showcase com mockup carousel
const featureSlides = [
  {
    id: 'automacao',
    src: '/images/screen-automacao.webp',
    title: 'Automação de WhatsApp',
    description: 'Configure respostas automáticas, funis e campanhas em minutos',
    tag: 'WhatsApp',
  },
  {
    id: 'dashboard',
    src: '/images/screen-dashboard.webp',
    title: 'Dashboard em Tempo Real',
    description: 'Monitore conversas, taxas de abertura e conversões ao vivo',
    tag: 'Analytics',
  },
  {
    id: 'instagram',
    src: '/images/screen-instagram.webp',
    title: 'Instagram DM Automation',
    description: 'Responda comentários e DMs automaticamente com IA',
    tag: 'Instagram',
  },
]

function ProductShowcaseSection() {
  return (
    <section className="py-24 bg-slate-950 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_70%_50%,rgba(127,65,249,0.12),transparent)]" />

      <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-16 items-center">
        {/* Texto */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7 }}
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full
            bg-purple-500/20 text-purple-300 text-sm font-semibold mb-6">
            ✦ Plataforma All-in-One
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white tracking-tight leading-tight mb-6">
            Tudo que você precisa
            <span className="block bg-gradient-to-r from-purple-400 to-orange-400 bg-clip-text text-transparent">
              em um só lugar
            </span>
          </h2>
          <p className="text-gray-400 text-lg leading-relaxed mb-8">
            Configure, automatize e monitore todas as suas automações
            de marketing digital sem precisar de código.
          </p>

          {/* Feature list */}
          <ul className="space-y-3">
            {['WhatsApp Bot em 5 minutos', 'Instagram DM automático', 'Analytics em tempo real', 'Integrações nativas'].map(f => (
              <li key={f} className="flex items-center gap-3 text-gray-300">
                <div className="w-5 h-5 rounded-full bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                  <div className="w-2 h-2 rounded-full bg-purple-400" />
                </div>
                {f}
              </li>
            ))}
          </ul>
        </motion.div>

        {/* Mockup Carousel */}
        <motion.div
          initial={{ opacity: 0, x: 30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="relative flex justify-center"
        >
          {/* Glow atrás do mockup */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
            w-64 h-64 bg-purple-600/30 blur-3xl rounded-full pointer-events-none" />

          <MockupCarousel slides={featureSlides} device="iphone" height={580} />
        </motion.div>
      </div>
    </section>
  )
}
```

---

## Prompts de Mockup por Tipo de Produto

### WhatsApp Automation SaaS

```
Mobile app screenshot, dark mode, showing WhatsApp Business automation dashboard.
UI shows: list of active chatbot flows (icons + names), message templates panel,
contact segments with green/yellow status dots, large "Bot Ativo" toggle at top,
response time metrics card. Purple (#7F41F9) and dark navy (#0f0f1a) color scheme.
iOS UI style, high quality, no lorem ipsum, realistic data, no faces.
Resolution: portrait 1080x1920.
```

### Dashboard Analytics (versão desktop)

```
SaaS analytics dashboard screenshot, dark mode desktop interface. Shows:
- Left sidebar: navigation with icons, purple active state
- Main area: line chart showing revenue growth (upward trend), key metrics row
  (users, revenue, conversion rate), recent activity list
- Top header: search bar, notification bell, user avatar
Color scheme: dark (#0f0f1a) with purple (#7F41F9) accents, white text.
Glassmorphism cards. Professional software UI. 1920x1080.
```

### Curso/Plataforma de Ensino

```
Online learning platform UI screenshot, clean modern design.
Shows: top navigation with progress bar (65% complete), lesson grid with
video thumbnails (dark thumbnails), sidebar with module list showing checkmarks
for completed lessons, current lesson highlighted in orange, quiz completion badge.
Warm color scheme: orange (#F97316) accent on white background.
Professional e-learning aesthetic. 1920x1080.
```

### App Mobile Financeiro

```
Fintech mobile app screenshot, dark mode.
Shows: monthly income/expense summary with colorful donut chart (green/red),
recent transactions list with category icons and amounts, quick action buttons
(Pagar, Receber, Transferir), total balance prominently displayed at top.
Color scheme: dark background, green (#10B981) for income, coral (#EF4444) for expense.
Modern fintech design. iOS UI. Portrait 1080x1920. No faces, realistic data.
```

---

## Pipeline Completo: Do zero ao carousel na página

```bash
# 1. Gerar screenshots com nanobanana
python3 ~/.claude/skills/construtor-paginas/scripts/generate-app-mockup.py \
  "WhatsApp automation dashboard, dark mode, purple theme" \
  "screen-whatsapp" "9:16"

# 2. Converter para WebP
cwebp -q 88 /tmp/screen-whatsapp-*.png -o public/images/screen-whatsapp.webp

# 3. Repetir para cada slide do carousel (3-5 imagens)
# 4. Copiar para public/images/
# 5. Usar MockupCarousel no componente com os paths

# Performance check:
# - Cada imagem WebP deve ser < 300KB para mockup mobile
# - Total do carousel < 1.5MB
# - Usar loading="lazy" nas imagens dentro dos mockups (não o primeiro)
```

---

## Checklist de Qualidade

```
Geração:
[ ] Prompt inclui: estilo (dark/light), cor principal, tipo de UI, resolução, "no faces, no lorem ipsum"
[ ] Pelo menos 3 variações geradas, escolher a melhor
[ ] Imagem mostra UI realista, não vazia

Otimização:
[ ] Convertida para WebP (cwebp -q 88)
[ ] Cada imagem < 300KB (mobile) ou < 500KB (desktop)
[ ] Poster WebP para lazy loading

Mockup:
[ ] Usando componente Magic UI (iPhone15Pro ou Safari), não SVG manual
[ ] Width/height definidos explicitamente (evita CLS)
[ ] Drop shadow para profundidade

Carousel:
[ ] 3-5 slides máximo (mais = confuso)
[ ] Cada slide tem título + descrição curta
[ ] Navegação por dots E setas
[ ] Touch/swipe funciona no mobile
[ ] Auto-play pausa ao hover
[ ] Primeira imagem NÃO é lazy (é acima do fold geralmente)

Seção:
[ ] Layout side-by-side no desktop (texto + mockup)
[ ] Mockup com glow/blur decorativo atrás
[ ] Scroll reveal na seção inteira (Framer Motion)
[ ] Mobile: carousel full-width, texto acima
```
