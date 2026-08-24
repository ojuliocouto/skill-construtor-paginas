# Design Laws: Guardrails Obrigatórios

Extraído de: **impeccable** (design laws) + **huashu-design** (anti-AI slop) + **taste** (design traps).
Leia antes de construir qualquer página. Estas regras têm precedência sobre preferências estéticas.

---

## BANS ABSOLUTOS (nunca fazer por padrão)

### Do impeccable
- Side-stripe borders em cards (borda colorida na lateral esquerda)
- Gradient text como padrão: só se o usuário pedir explicitamente
- Glassmorphism como padrão: só se o usuário pedir explicitamente
- Hero-metric template (card centralizado com número grande + label + sparkline)
- Grade de cards idênticos em tamanho, peso e cor
- Modal-first thinking: não resolver problema de espaço com modal por padrão

### Do huashu-design (anti-AI slop)
- Gradiente roxo radical como "cara de tecnologia/IA": é a formula mais batida de 2022-2024
- Emoji como ícones de interface: sinal de falta de sistema de design
- Rounded card + left border accent colorido: combo mais genérico do Tailwind/Material
- SVG desenhado à mão substituindo imagens reais de pessoas ou produtos
- CSS silhuetas/formas genéricas no lugar de imagem real do produto
- Inter/Roboto/Arial para headings de display: fontes de corpo, não de título
- Cyberpunk neon / `#0D1117` dark blue (GitHub vibes) como estética padrão

### Do taste
- Box-shadow em tudo: sombra estabelece hierarquia de elevação, não é decoração
- Border-radius >50% em elementos que não são pills intencionais
- Gradiente de fundo como substituto de pensar no design
- Ilustrações vetoriais genéricas de pessoas com membros desproporcionais
- Grade de cards quando o conteúdo não é comparável/navegável
- Ícones de estilos misturados (outline + filled + duotone na mesma UI)
- Text cinza claro em fundo branco por "parecer limpo": ilegível

---

## REGRAS DE COR

### Espaço de cor
- Preferir **OKLCH** sobre HEX quando possível: perceptualmente uniforme, sem os artefatos de luminosidade do HSL
- Sintaxe: `oklch(lightness chroma hue)`: reduzir chroma ao se aproximar de branco/preto
- Não usar azul (hue 250) ou laranja quente (hue 60) por reflexo: são os defaults de IA mais óbvios

### Neutros
- **Cinza puro é morto.** Adicionar chroma mínimo (0.005-0.015) aos neutros, hueado para a cor da marca
- O tom de tintagem deve vir da marca do projeto, não de "warm = friendly, cool = tech"

### Estrutura de paleta
- **60%** neutros de fundo e espaço branco
- **30%** cor secundária: texto, bordas, estados inativos
- **10%** acento: CTAs, highlights, focus states
- Cor acento funciona *porque* é rara: sobreusar mata o poder dela

### Contraste mínimo (WCAG AA)
- Texto normal: 4.5:1
- Texto grande (18px+): 3:1
- Componentes UI e ícones: 3:1
- Placeholder text também precisa de 4.5:1

---

## REGRAS DE TIPOGRAFIA

### Medida e ritmo
- Body: `max-width: 65ch` (ideal), nunca ultrapassar 80ch
- Line-height body: 1.4-1.6
- Line-height headings: 1.1-1.3
- Texto claro em fundo escuro: aumentar line-height +0.05-0.1, adicionar letter-spacing 0.01-0.02em

### Hierarquia
- No máximo 2 typefaces por projeto: uma terceira quase nunca é justificada
- Hierarquia via escala + peso, ratio mínimo de 1.25x entre níveis
- Nunca usar Inter/Roboto/Arial/Helvetica para headings de display
- System font stack (`-apple-system, system-ui, sans-serif`) é underrated: considerar para apps onde performance > personalidade

### Proibido
- Parágrafos com `<p>` e indentação ao mesmo tempo: escolher um ou outro
- Mais de 5 tamanhos de fonte ativos simultaneamente
- Fontes decorativas em texto de interface

---

## REGRAS DE MOTION

### Duração (regra 100/300/500)
- 100-150ms: feedback instantâneo (press, toggle, mudança de cor)
- 200-300ms: mudanças de estado (menu, tooltip, hover)
- 300-500ms: mudanças de layout (accordion, modal, drawer)
- 500-800ms: animações de entrada (page load, hero reveals)
- Saídas = ~75% do tempo de entrada

### Easing
- Nunca usar `ease` genérico
- Entrada: `ease-out`: `cubic-bezier(0.16, 1, 0.3, 1)` (expo out)
- Saída: `ease-in`: `cubic-bezier(0.7, 0, 0.84, 0)`
- Toggle: `ease-in-out`: `cubic-bezier(0.65, 0, 0.35, 1)`
- Sem bounce e elastic curves: parecem 2015

### Regras hard
- **Nunca animar propriedades de layout** (`width`, `height`, `top`, `left`, margins): usar transform + FLIP
- Propriedades composited seguras: `transform`, `opacity`
- Blur/filter OK quando melhora experiência E é smooth: não como padrão decorativo
- Stagger: `animation-delay: calc(var(--i) * 50ms)`: limitar total em ~500ms
- **Sempre respeitar `prefers-reduced-motion`**: não como afterthought

---

## AI SLOP TEST (obrigatório antes de entregar)

Antes de finalizar qualquer página, responder as duas perguntas:

1. **"Isso parece ter sido gerado por IA?"**
   - Se a resposta for "sim" ou "talvez": identificar o elemento genérico e substituir
   - AI slop = média visual de todo o corpus de treinamento = sem identidade de marca

2. **"Tem algum detalhe que só alguém com gosto colocaria?"**
   - Se não houver: adicionar pelo menos um elemento intencional que não seria o default automático
   - Pode ser: escolha tipográfica inusual, breakpoint de espaçamento específico, animação calibrada com cuidado, uso de cor não-convencional mas correto

**Lógica:** O usuário contrata design para a marca ser reconhecida. AI slop = brand dilution.

---

## QUANDO GLASSMORPHISM E GRADIENT TEXT SÃO ACEITÁVEIS

Apesar dos bans acima, estes recursos existem no construtor e podem ser usados quando:
- O usuário pede explicitamente ("quero glassmorphism", "quero gradient no título")
- O ID Visual da marca já usa esses recursos consistentemente
- O contexto é um produto gaming, cripto ou entretenimento onde é parte do vernáculo visual

Nunca usar como default, apenas como resposta explícita a um brief.
