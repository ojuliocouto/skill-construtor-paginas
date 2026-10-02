# Design System & UI/UX Intelligence

### Princípios de Design

1. **Hierarquia Visual**: Ação primária bold e alto contraste, secundária sutil, terciaria mínima
2. **Sistema de Espaçamento (8px grid)**: xs=4px, sm=8px, md=16px, lg=24px, xl=32px, 2xl=48px
3. **Tipografia**: Máximo 3-4 tamanhos de fonte por página, máximo 2 famílias
4. **Cores**: Paleta limitada (2-3 cores max), usar design tokens

### Escala Tipográfica
```typescript
const typography = {
  hero: 'text-4xl md:text-5xl font-bold tracking-tight',
  heading: 'text-2xl md:text-3xl font-semibold',
  subheading: 'text-lg md:text-xl font-medium',
  body: 'text-base leading-relaxed',
  caption: 'text-sm text-gray-500',
};
```

### Cores Semânticas
```typescript
const colors = {
  primary: 'bg-blue-600 hover:bg-blue-700',
  secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-900',
  danger: 'bg-red-600 hover:bg-red-700',
  success: 'bg-green-600 hover:bg-green-700',
  background: 'bg-gray-50 dark:bg-gray-950',
  surface: 'bg-white dark:bg-gray-900',
  elevated: 'bg-white dark:bg-gray-800 shadow-lg',
  textPrimary: 'text-gray-900 dark:text-white',
  textSecondary: 'text-gray-600 dark:text-gray-400',
};
```

### Gradientes Modernos
```tsx
// Mesh gradient premium
const meshGradient = "bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950";

// Hero vibrante
const heroGradient = "bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600";

// Radial glow sutil
const radialGlow = "bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-200/40 via-transparent to-transparent";
```

### Regras Obrigatórias de UI Profissional

| Regra | Fazer | Não Fazer |
|-------|-------|-----------|
| Ícones | Hugeicons (landing pages premium) ou Lucide (UI/dashboards) | Emojis como ícones de UI |
| Hover | Color/opacity transitions | Scale que desloca layout |
| Logos | SVG oficial (Simple Icons) | Chutar paths de logo |
| Cursor | `cursor-pointer` em tudo clicável | Cursor padrão em elementos interativos |
| Transições | `transition-colors duration-200` | Mudanças instantâneas ou >500ms |
| Glass light mode | `bg-white/80` ou mais | `bg-white/10` (transparente demais) |
| Texto light | `#0F172A` (slate-900) | `#94A3B8` (slate-400) |
| Navbar flutuante | `top-4 left-4 right-4` | `top-0 left-0 right-0` colado |

### Princípios UX (Nielsen)
1. Visibilidade do estado do sistema
2. Correspondência com o mundo real
3. Controle e liberdade do usuário
4. Consistência e padrões
5. Prevenção de erros
6. Reconhecer ao invés de lembrar
7. Flexibilidade e eficiência
8. Design estético e minimalista
9. Ajudar usuários a reconhecer e recuperar de erros
10. Ajuda e documentação

### Animações
- **Com propósito**: animação transmite mudança de estado
- **Rápida**: 200-500ms
- **Natural**: curvas de easing simulando física
- **Moderada**: evitar excesso de animação
- Respeitar `prefers-reduced-motion`

---
