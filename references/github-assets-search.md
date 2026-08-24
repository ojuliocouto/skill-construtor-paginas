# Busca no GitHub - Templates & Inspiracao

Antes de construir do zero, busque templates e paginas ja criadas no GitHub como referencia ou ponto de partida.

### Como Usar

```bash
# Busca por repositorios (padrao)
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "landing page tailwind"

# Usar preset (queries otimizadas)
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py landing-nextjs

# Filtrar por linguagem
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "saas template" --lang tsx

# Minimo de stars (qualidade)
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "portfolio template" --stars 200

# Mais resultados
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py dashboard -n 20

# Ordenar por mais recente
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "nextjs starter" --sort updated

# Buscar CODIGO especifico (componentes, secoes)
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "hero section tailwind" --type code --lang tsx
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "pricing table component" --type code --lang tsx
```

### Presets Disponiveis

| Preset | Busca |
|--------|-------|
| `landing` | landing page template |
| `landing-tailwind` | landing page tailwind template |
| `landing-nextjs` | landing page nextjs template |
| `landing-react` | landing page react template |
| `saas` | saas template website |
| `saas-nextjs` | saas nextjs starter template |
| `portfolio` | portfolio template developer |
| `portfolio-nextjs` | portfolio nextjs template |
| `dashboard` | dashboard template admin panel |
| `dashboard-nextjs` | dashboard nextjs shadcn |
| `ecommerce` | ecommerce template storefront |
| `blog` | blog template minimal |
| `blog-nextjs` | blog nextjs mdx template |
| `components` | ui components library tailwind |
| `hero` | hero section component landing |
| `pricing` | pricing page component template |
| `auth` | authentication page login template |
| `dark-mode` | dark mode template website |
| `glassmorphism` | glassmorphism ui template |
| `bento` | bento grid layout template |
| `animation` | animated landing page framer motion |
| `startup` | startup landing page template |
| `agency` | agency website template |
| `minimal` | minimal website template clean |

### Busca de Assets Visuais (videos, fotos, lottie, ilustracoes)

```bash
# Videos de fundo para hero (requer PEXELS_API_KEY gratuita)
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py "dark abstract tech"
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py tech-dark          # preset
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py waves-light        # preset light

# Fotos para hero ou secoes
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py "office modern" --type photo

# Lottie animations (loading, success, rocket, etc.)
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py "loading" --type lottie

# Ilustracoes SVG (undraw, storyset)
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py --type illustrations "team work"

# Icones animados (LordIcon, Lucide)
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py --type icons

# Backgrounds SVG, patterns, noise textures
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py --type backgrounds

# Ver todos os presets de video
python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py --presets
```

**Setup da API Pexels (gratuita, 20.000 req/mes):**
```bash
# 1. Criar conta gratis em: https://www.pexels.com/api/
# 2. Copiar API key
export PEXELS_API_KEY="sua-chave-aqui"
# Para persistir: echo 'export PEXELS_API_KEY="sua-chave"' >> ~/.zshrc
```

**Presets de video disponiveis:**
`tech-dark`, `tech-blue`, `tech-purple`, `particles`, `waves-dark`, `neon`, `space`, `circuit`, `minimal-white`, `waves-light`, `liquid`, `nature`, `ocean`, `city`, `office`, `hero-dark`, `hero-gradient` e mais.

**Referencia completa de integracao:** `references/visual-assets.md`

---

### Workflow Recomendado com GitHub

1. **Buscar inspiracao**: `python3 .../github-search.py landing-nextjs --stars 100`
2. **Clonar template**: `gh repo clone <repo>`
3. **Estudar estrutura**: Ler os arquivos do template clonado
4. **Adaptar**: Usar como base e customizar com as guidelines desta skill
5. **Buscar componentes**: `python3 .../github-search.py "pricing section" --type code --lang tsx`

### Apos Encontrar um Repo

```bash
# Ver detalhes do repo
gh repo view <owner/repo>

# Abrir no navegador
gh repo view <owner/repo> --web

# Clonar para usar como base
gh repo clone <owner/repo>

# Ver conteudo de um arquivo especifico
gh api repos/<owner/repo>/contents/<path> --jq '.content' | base64 -d

# Listar arquivos do repo
gh api repos/<owner/repo>/git/trees/main --jq '.tree[].path'
```

---
