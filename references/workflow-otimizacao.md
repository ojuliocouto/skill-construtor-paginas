# Workflow de Otimização de Páginas Existentes


> **ATENÇÃO (anti-vibe):** vários efeitos deste arquivo (glow em botão, border glow, aurora, floating orbs, gradiente indigo+roxo) são tells VISUAIS de IA (V1-V15 de `anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Usar apenas quando o usuário pedir explicitamente esse look. Nos exemplos abaixo, trocar as cores hardcoded pela paleta REAL do projeto (CSS vars) e preferir micro-interacao sobria no CTA (mudança de tom + elevação sutil).
Quando o usuário tem uma página já existente e quer melhorar, reformular ou deixar visual impactante:

### Passo 1: Leitura e Auditoria Completa

**SEMPRE ler os arquivos antes de qualquer mudança:**
```bash
# Identificar todos os componentes/paginas do projeto
# Usar Glob e Read para ler todos os arquivos relevantes antes de sugerir qualquer mudanca
```

**Auditar 5 dimensões:**
1. **Impacto Visual**: A hero section prende atenção em 3 segundos? Há um elemento visual forte (mockup, vídeo, ilustração)?
2. **Hierarquia Tipográfica**: Títulos se destacam com peso, tamanho e gradiente? Body e legível?
3. **Paleta e Coerência**: Cores harmônicas? Gradientes consistentes? Dark mode funciona?
4. **Animações**: Há feedback visual? Elementos entram animados? Cards reagem ao hover?
5. **Micro-interacoes**: Botões tem hover elaborado? Links transitam suavemente?

### Passo 2: Diagnóstico por Severidade

**Alta Prioridade (impacto imediato):**
- Hero sem animação de entrada → adicionar fade/slide-up com Framer Motion
- Fundo plano/branco → substituir por mesh gradient ou gradiente radial
- Títulos sem hierarquia → aumentar tamanho, peso e adicionar gradient text
- Botões genéricos → CTA com cor de marca sólida + hover de tom + elevação sutil (ShimmerButton SÓ se o look foi pedido; glow colorido = tell V9)
- Cards sem hover elevation → adicionar hover shadow neutra + translate (sem border glow colorido: tell V9)

**Média Prioridade (polimento visual):**
- Seções sem separação visual → adicionar wave SVG dividers ou gradient fade
- Features sem scroll reveal → envolver em Framer Motion whileInView
- Stats estáticos → substituir por NumberTicker
- Logos repetindo → usar Marquee animado
- Imagens sem tratamento → adicionar blur placeholder + lazy load

**Baixa Prioridade (refinamento):**
- Falta de noise texture no background (sutileza premium)
- Loading skeleton em listas e cards
- Page transitions suaves

### Passo 3: Aplicar Upgrades por Camada

**Camada 1, Background & Atmosfera**
```tsx
// Substituir fundo liso por mesh gradient atmosferico
const heroBg = "bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950"
const radialGlow = "bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(var(--brand-1-rgb),0.18),transparent)]"

// Adicionar pattern (DotPattern ou GridPattern do MagicUI)
<div className="relative">
  <div className={`absolute inset-0 ${heroBg}`} />
  <div className={`absolute inset-0 ${radialGlow}`} />
  <DotPattern className="absolute inset-0 opacity-20 [mask-image:radial-gradient(ellipse_at_center,white,transparent)]" />
  <div className="relative z-10">{/* conteudo */}</div>
</div>
```

**Camada 2, Typography Upgrade**
```tsx
// Antes: titulo plano
<h1 className="text-4xl font-bold">Nosso Produto</h1>

// Depois: titulo com gradiente + tracking + leading otimizados
<h1 className="text-5xl md:text-7xl font-black tracking-tight leading-[1.05]">
  <span className="bg-gradient-to-r from-white via-purple-200 to-white bg-clip-text text-transparent">
    Nosso
  </span>{' '}
  <span className="relative text-white">
    Produto
    {/* underline decorativo */}
    <span className="absolute -bottom-2 left-0 right-0 h-[3px] bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" />
  </span>
</h1>
```

**Camada 3, Cards Upgrade**
```tsx
// Antes: card plano
<div className="bg-white rounded-lg p-6 shadow">

// Depois: card premium com spotlight hover
<div className="group relative rounded-2xl p-6
  bg-white dark:bg-gray-900/60
  border border-gray-200/60 dark:border-white/[0.06]
  hover:border-purple-500/30 dark:hover:border-purple-500/20
  shadow-sm hover:shadow-2xl hover:shadow-purple-500/10
  transition-all duration-300 hover:-translate-y-1.5 overflow-hidden">
  {/* glow interno no hover */}
  <div className="absolute inset-0 bg-gradient-to-br from-purple-500/[0.07] to-pink-500/[0.07]
    opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-2xl" />
  <div className="relative z-10">{/* conteudo */}</div>
</div>
```

**Camada 4, Botões Upgrade**
```tsx
// CTA principal: ShimmerButton (MagicUI)
<ShimmerButton shimmerColor="var(--brand-accent)" background="linear-gradient(to right, var(--brand-1), var(--brand-2))" className="px-8 py-4 text-base font-semibold">
  Comecar Agora
</ShimmerButton>

// Ou glow button CSS puro
<button className="relative px-8 py-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-full
  shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_50px_rgba(99,102,241,0.8)]
  transition-all duration-300 cursor-pointer">
  Comecar Agora
</button>
```

**Camada 5, Animar TUDO com Framer Motion**
```tsx
// Scroll reveal padrao, envolver TODAS as secoes
import { motion } from 'framer-motion'

<motion.div
  initial={{ opacity: 0, y: 40 }}
  whileInView={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] }}
  viewport={{ once: true, margin: "-80px" }}
>
  {/* qualquer secao ou componente */}
</motion.div>

// Stagger em listas/grids
<motion.div
  variants={{ visible: { transition: { staggerChildren: 0.1 } } }}
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true }}
>
  {items.map(item => (
    <motion.div
      key={item.id}
      variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
    >
      {/* card */}
    </motion.div>
  ))}
</motion.div>
```

### Checklist de Otimização Visual

- [ ] Hero tem animação de entrada (Framer Motion fade/slide-up)
- [ ] Fundo tem gradiente mesh, gradiente radial ou pattern
- [ ] Título principal usa gradient text ou decoração
- [ ] CTA tem cor de marca + micro-interacao sobria (sem glow colorido difuso)
- [ ] Cards tem hover: elevation + translate-y (borda 1px, sem glow)
- [ ] Features usam scroll reveal whileInView
- [ ] Stats usam NumberTicker animado
- [ ] Social proof/logos usam Marquee
- [ ] Mockup de produto visível (Safari ou iPhone15Pro)
- [ ] Separadores entre seções (wave SVG ou gradient fade)

---
