# Acessibilidade (WCAG 2.1 AA)

### Contraste de Cores (OBRIGATÓRIO)

| Tipo | Ratio Mínimo |
|------|-------------|
| Texto normal (<18px) | 4.5:1 |
| Texto grande (>=18px bold ou >=24px) | 3:1 |
| Componentes UI | 3:1 |
| Indicadores de foco | 3:1 |

**Combinações seguras**: gray-700+ em branco, branco em gray-900/blue-600/green-700
**Proibido**: gray-400 em branco (2.6:1 FALHA), branco em amarelo

### Botões - SEMPRE devem ter
- Background visível OU borda visível (min 1px)
- Texto com contraste contra o background
- Altura mínima 44px
- Padding mínimo px-4 py-2

### Focus States (OBRIGATÓRIO em todo elemento interativo)
```tsx
className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
```

### Screen Readers
```tsx
// Botoes com icone precisam de label
<button aria-label="Fechar menu"><XIcon className="w-6 h-6" /></button>

// Skip link
<a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4">
  Pular para conteudo principal
</a>

// Conteudo dinamico
<div role="status" aria-live="polite">{message}</div>
```

### Movimento
```html
<div class="animate-pulse motion-reduce:animate-none">
  Respeita preferencia de movimento reduzido
</div>
```

---
