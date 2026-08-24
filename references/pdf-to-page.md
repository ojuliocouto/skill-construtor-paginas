# PDF to Page: Guia de Analise Visual e Conversao

Referencia completa para analisar PDFs de paginas web e converter em codigo HTML/Tailwind ou React.

---

## Mapeamento de Cores: Visual → Tailwind

### Pretos e Cinzas (backgrounds escuros)

| Visual observado | Classe Tailwind | Hex |
|-----------------|-----------------|-----|
| Preto puro | `bg-black` / `bg-gray-950` | #000 / #030712 |
| Preto azulado (SaaS dark) | `bg-slate-950` | #020617 |
| Preto com tom roxo | `bg-[#0a0118]` ou `bg-slate-950` | custom |
| Cinza muito escuro | `bg-gray-900` | #111827 |
| Cinza escuro | `bg-gray-800` | #1f2937 |
| Cinza medio escuro | `bg-gray-700` | #374151 |

### Brancos e Cinzas (backgrounds claros)

| Visual observado | Classe Tailwind | Hex |
|-----------------|-----------------|-----|
| Branco puro | `bg-white` | #fff |
| Off-white quente | `bg-gray-50` | #f9fafb |
| Off-white frio | `bg-slate-50` | #f8fafc |
| Cinza claro (secoes alternadas) | `bg-gray-100` | #f3f4f6 |
| Cinza medio | `bg-gray-200` | #e5e7eb |

### Cores Primarias Comuns em Landing Pages

| Visual observado | Classes Tailwind |
|-----------------|-----------------|
| Azul vibrante (tech) | `bg-blue-600` / `text-blue-600` |
| Azul escuro (corporativo) | `bg-blue-800` / `bg-blue-900` |
| Indigo (SaaS moderno) | `bg-indigo-600` / `text-indigo-600` |
| Roxo (criativo/tech) | `bg-purple-600` / `text-purple-600` |
| Violeta (premium) | `bg-violet-600` |
| Rosa (feminino/moderno) | `bg-pink-500` / `bg-rose-500` |
| Verde (saude/fintech) | `bg-green-600` / `bg-emerald-600` |
| Amarelo/Laranja (energia) | `bg-amber-500` / `bg-orange-500` |
| Vermelho (urgencia) | `bg-red-600` |
| Ciano (tech limpo) | `bg-cyan-500` / `bg-teal-500` |

### Gradientes Comuns

| Visual observado | Classe Tailwind |
|-----------------|-----------------|
| Roxo → Rosa | `bg-gradient-to-r from-purple-600 to-pink-600` |
| Azul → Roxo | `bg-gradient-to-r from-blue-600 to-purple-600` |
| Indigo → Violeta | `bg-gradient-to-r from-indigo-500 to-violet-500` |
| Verde → Ciano | `bg-gradient-to-r from-green-500 to-cyan-500` |
| Laranja → Vermelho | `bg-gradient-to-r from-orange-500 to-red-500` |
| Roxo → Azul → Ciano | `bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-500` |
| Escuro diagonal | `bg-gradient-to-br from-gray-900 via-gray-950 to-black` |
| Glow radial roxo (SaaS) | `bg-[radial-gradient(ellipse_at_top,rgba(120,119,198,0.3),transparent)]` |

---

## Mapeamento de Tipografia: Visual → Tailwind

### Tamanhos (estimativa visual)

| Se o texto parece... | Mobile | Desktop | Classe Tailwind |
|---------------------|--------|---------|-----------------|
| Headline gigante (hero) | ~36px | ~72px+ | `text-4xl md:text-7xl` |
| Headline grande | ~30px | ~60px | `text-3xl md:text-6xl` |
| Headline medio | ~28px | ~48px | `text-3xl md:text-5xl` |
| Titulo de secao | ~24px | ~36px | `text-2xl md:text-4xl` |
| Subtitulo/lead | ~18px | ~20px | `text-lg md:text-xl` |
| Corpo de texto | ~16px | ~16px | `text-base` |
| Texto pequeno | ~14px | ~14px | `text-sm` |
| Caption/legal | ~12px | ~12px | `text-xs` |

### Pesos

| Se o texto parece... | Classe Tailwind |
|---------------------|-----------------|
| Muito fino (light) | `font-light` |
| Normal | `font-normal` |
| Medio (semi-destacado) | `font-medium` |
| Negrito | `font-semibold` |
| Muito negrito | `font-bold` |
| Extra negrito (hero) | `font-extrabold` |
| Ultra negrito (impacto) | `font-black` |

### Espacamento entre letras

| Se o texto parece... | Classe Tailwind |
|---------------------|-----------------|
| Letras juntas (titulos grandes) | `tracking-tight` ou `tracking-tighter` |
| Normal | (padrao, nao precisa classe) |
| Letras afastadas (labels/badges) | `tracking-wide` ou `tracking-widest` |
| Uppercase espacado (categorias) | `uppercase tracking-widest text-xs` |

### Altura de linha

| Se o texto parece... | Classe Tailwind |
|---------------------|-----------------|
| Linhas coladas (titulos) | `leading-tight` ou `leading-none` |
| Espacamento normal | `leading-normal` |
| Espacamento confortavel (body) | `leading-relaxed` |
| Espacamento generoso | `leading-loose` |

---

## Mapeamento de Espacamento: Visual → Tailwind

### Padding de secoes

| Se a secao tem... | Classe Tailwind |
|------------------|-----------------|
| Pouco espaco vertical | `py-12` ou `py-16` |
| Espaco medio (padrao) | `py-20` ou `py-24` |
| Muito espaco (respirado) | `py-32` ou `py-40` |

### Gap entre elementos

| Se os elementos estao... | Classe Tailwind |
|-------------------------|-----------------|
| Bem juntinhos | `gap-2` ou `gap-3` |
| Espacamento normal | `gap-4` ou `gap-6` |
| Bem separados | `gap-8` ou `gap-10` |
| Muito separados | `gap-12` ou `gap-16` |

### Container width

| Se o conteudo parece... | Classe Tailwind |
|------------------------|-----------------|
| Estreito (blog, texto) | `max-w-3xl mx-auto` |
| Medio (landing page) | `max-w-5xl mx-auto` |
| Largo (dashboard) | `max-w-7xl mx-auto` |
| Full width | `w-full` |

---

## Mapeamento de Componentes Visuais Comuns

### Botoes

| Visual no PDF | Implementacao |
|--------------|---------------|
| Botao solido colorido | `bg-[cor]-600 text-white px-6 py-3 rounded-lg font-semibold` |
| Botao outline | `border-2 border-[cor]-600 text-[cor]-600 px-6 py-3 rounded-lg` |
| Botao arredondado (pill) | `rounded-full px-8 py-3` |
| Botao com sombra/glow | Adicionar `shadow-lg shadow-[cor]-500/25` |
| Botao com icone → | Adicionar `flex items-center gap-2` + icone Lucide |

### Cards

| Visual no PDF | Implementacao |
|--------------|---------------|
| Card com borda sutil | `border border-gray-200 dark:border-gray-800 rounded-2xl p-6` |
| Card com sombra | `shadow-lg rounded-2xl p-6 bg-white` |
| Card glass (transparente) | `backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-6` |
| Card com hover elevation | Adicionar `hover:shadow-xl hover:-translate-y-1 transition-all` |
| Card com icone no topo | Icone Lucide em `div` com `bg-[cor]-50 rounded-xl p-3 mb-4` |

### Badges/Tags

| Visual no PDF | Implementacao |
|--------------|---------------|
| Badge pill colorido | `inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-[cor]-100 text-[cor]-700` |
| Badge com dot (status) | Adicionar `<span class="w-2 h-2 rounded-full bg-green-400 animate-pulse" />` |
| Badge outline | `border border-[cor]-200 text-[cor]-600 px-3 py-1 rounded-full text-xs` |

### Navegacao

| Visual no PDF | Implementacao |
|--------------|---------------|
| Navbar transparente | `fixed top-0 w-full bg-transparent backdrop-blur-md z-50` |
| Navbar solida | `fixed top-0 w-full bg-white shadow-sm z-50` |
| Navbar flutuante | `fixed top-4 left-4 right-4 bg-white/80 backdrop-blur-xl rounded-2xl shadow-lg z-50` |
| Navbar dark | `bg-gray-950 border-b border-gray-800` |

---

## Reconhecimento de Fontes Populares

### Por Aparencia Visual

| Se a fonte parece... | Provavel fonte | Google Fonts |
|---------------------|---------------|--------------|
| Geometrica limpa, moderna | Inter | `family=Inter` |
| Geometrica com personalidade | DM Sans | `family=DM+Sans` |
| Humanista arredondada | Plus Jakarta Sans | `family=Plus+Jakarta+Sans` |
| Humanista classica | Nunito | `family=Nunito` |
| Monoespacada tech | JetBrains Mono | `family=JetBrains+Mono` |
| Serif elegante | Playfair Display | `family=Playfair+Display` |
| Serif moderna | Lora | `family=Lora` |
| Ultra moderna (Vercel) | Geist | Precisa instalar npm |
| Muito condensada | Oswald | `family=Oswald` |
| Futurista/tech | Space Grotesk | `family=Space+Grotesk` |
| Suave e amigavel | Poppins | `family=Poppins` |
| Profissional corporativa | Source Sans 3 | `family=Source+Sans+3` |

### Como Adicionar Google Fonts

```html
<!-- No <head> do HTML -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
```

```css
/* No CSS/Tailwind */
body { font-family: 'Inter', system-ui, sans-serif; }

/* Ou no Tailwind config */
@theme {
  --font-sans: 'Inter', system-ui, sans-serif;
}
```

---

## Padroes de Layout Comuns em PDFs

### Hero Layouts

```
LAYOUT A, Texto Esquerda + Imagem Direita (mais comum)
+------------------------+-------------------+
|  Badge                 |                   |
|  Titulo Grande         |   [Mockup/App     |
|  Subtitulo             |    Screenshot]    |
|  [CTA]  [CTA2]        |                   |
|  Social proof          |                   |
+------------------------+-------------------+
→ grid lg:grid-cols-2 gap-12 items-center

LAYOUT B, Centralizado (elegante/minimal)
+------------------------------------------+
|           Badge                           |
|      Titulo Grande Centralizado           |
|     Subtitulo centralizado curto          |
|       [CTA]     [CTA2]                   |
|    [Mockup centralizado abaixo]           |
+------------------------------------------+
→ text-center max-w-4xl mx-auto

LAYOUT C, Full Image Background
+------------------------------------------+
|  [Background Image/Video]                 |
|                                           |
|      Titulo Sobre a Imagem                |
|      [CTA]                                |
|                                           |
+------------------------------------------+
→ relative + absolute inset-0 bg-cover + overlay
```

### Secoes de Features

```
LAYOUT A, Grid 3 colunas (mais comum)
+----------+----------+----------+
| [Icon]   | [Icon]   | [Icon]   |
| Titulo   | Titulo   | Titulo   |
| Desc     | Desc     | Desc     |
+----------+----------+----------+
→ grid md:grid-cols-3 gap-8

LAYOUT B, Alternado (texto/imagem)
+------------------+-----------------+
| Texto descritivo | [Imagem]        |
+------------------+-----------------+
| [Imagem]         | Texto descritivo|
+------------------+-----------------+
→ grid lg:grid-cols-2, imagem alterna lados

LAYOUT C, Bento Grid (moderno)
+----------+---------------------+
| Grande   |  Medio    | Pequeno |
|          +-----------+---------+
|          |  Pequeno  | Medio   |
+----------+-----------+---------+
→ grid grid-cols-4 com col-span/row-span
```

### Pricing

```
LAYOUT A, 3 colunas, destaque no meio
+--------+-----------+--------+
| Basic  | Pro ★     | Ent.   |
| $9/mo  | $29/mo    | Custom |
| feat1  | feat1     | feat1  |
| feat2  | feat2     | feat2  |
|        | feat3     | feat3  |
| [CTA]  | [CTA]     | [CTA]  |
+--------+-----------+--------+
→ Meio com scale-105, border-[cor], shadow-xl
```

---

## Checklist de Analise de PDF

Usar este checklist ao receber qualquer PDF para converter:

```
□ ESTRUTURA
  □ Quantas secoes tem a pagina?
  □ Qual a ordem das secoes?
  □ Tem navbar? Que tipo?
  □ Tem footer? Que conteudo?

□ CORES
  □ Cor de fundo principal (dark/light?)
  □ Cor primaria (CTAs, destaques)
  □ Cor de texto principal
  □ Cor de texto secundario
  □ Tem gradientes? Quais cores?
  □ Tem glow/blur effects?

□ TIPOGRAFIA
  □ Fonte principal (sans/serif/mono?)
  □ Tamanho do titulo hero
  □ Peso dos titulos (bold/black?)
  □ Texto todo uppercase em algum lugar?

□ LAYOUT
  □ Hero: centralizado ou split?
  □ Container: estreito ou largo?
  □ Cards: grid de quantas colunas?
  □ Spacing: apertado ou generoso?

□ ELEMENTOS ESPECIAIS
  □ Badges/tags
  □ Icones (que tipo?)
  □ Imagens/mockups
  □ Social proof (logos, avatares, numeros)
  □ Formularios
  □ Divisores entre secoes

□ CONTEUDO
  □ Todos os textos copiados fielmente
  □ CTAs com texto exato
  □ Links de navegacao
  □ Dados de contato/rodape
```

---

## Extrair os ASSETS REAIS do PDF (nao usar imagem generica)

Quando o PDF tem fotos/equipamentos/logo reais (folder, catalogo, deck), USE-OS. E o
contraste entre pagina "de verdade" e template generico. Receita validada num projeto real (jun/2026):

```bash
# 1. Extrair todas as imagens embutidas no PDF
pdfimages -all arquivo.pdf /tmp/extr/img      # gera img-000.ppm/png/jpg...

# 2. Muitas vezes o equipamento esta DENTRO de um slide com texto por cima.
#    Recortar so o objeto limpo, com Python/PIL:
python3 - <<'PY'
from PIL import Image
im = Image.open("/tmp/extr/img-005.png")
crop = im.crop((x0, y0, x1, y1))     # ajustar caixa pra pegar so o equipamento
crop.save("/projeto/assets/equip.webp", "WEBP", quality=82)
PY

# 3. Converter o resto pra WebP (leve)
for f in /tmp/extr/*.png; do cwebp -q 82 "$f" -o "${f%.png}.webp"; done
```

Regras:
- **Conferir cada recorte com os proprios olhos** (abrir a imagem). Refazer se pegar texto ou ficar torto. Num projeto real o recorte de uma foto foi refeito ~4x.
- **Logo:** se a versao extraida vier com fundo ruim ou baixa resolucao, recriar como **SVG vetorial** (escala em qualquer tamanho, funciona em fundo claro/escuro).
- Isso alimenta o `assets-auditor` do Step 4: pagina com asset real do cliente passa; pagina so com SVG generico reprova.
