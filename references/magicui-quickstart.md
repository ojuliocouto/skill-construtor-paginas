# Magic UI - Animacoes


> **ATENCAO (anti-vibe):** varios efeitos deste arquivo (glow em botao, border glow, aurora, floating orbs, gradiente indigo+roxo) sao tells VISUAIS de IA (V1-V15 de `anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Usar apenas quando o usuario pedir explicitamente esse look. Nos exemplos abaixo, trocar as cores hardcoded pela paleta REAL do projeto (CSS vars) e preferir micro-interacao sobria no CTA (mudanca de tom + elevacao sutil).
Componentes animados para landing pages SaaS. Instalacao: `npx magicui-cli@latest add [componente]`

**Dependencias**: `npm install framer-motion clsx tailwind-merge`

### Componentes Disponiveis

| Categoria | Componentes |
|-----------|-------------|
| Texto | number-ticker, typing-animation, word-rotate, flip-text, morphing-text |
| Botoes | shimmer-button, rainbow-button, pulsating-button, shiny-button |
| Patterns | dot-pattern, grid-pattern, retro-grid, particles, meteors |
| Mockups | iphone-15-pro, safari, android |
| Layout | bento-grid, marquee, dock, animated-list, file-tree |
| Efeitos | orbiting-circles, animated-beam, border-beam, confetti, globe |

### Exemplos Rapidos
```tsx
'use client'
// Number Ticker (stats animados)
<NumberTicker value={10000} className="text-4xl font-bold" />

// Marquee (carrossel de logos)
<Marquee pauseOnHover className="[--duration:20s]">
  {logos.map(logo => <img key={logo.name} src={logo.img} />)}
</Marquee>

// Word Rotate (headline dinamica)
<h1>Construa apps <WordRotate words={["rapidos", "bonitos", "modernos"]} /></h1>

// Safari Mockup
<Safari url="seuapp.com" src="/screenshot.png" />

// Shimmer Button
<ShimmerButton shimmerColor="var(--brand-accent)" background="linear-gradient(to right, var(--brand-1), var(--brand-2))">
  Comece Agora
</ShimmerButton>
```

### SSR (Next.js)
```tsx
'use client' // Sempre adicionar
import dynamic from 'next/dynamic'
const Globe = dynamic(() => import('@/components/magicui/globe'), { ssr: false })
```

---
