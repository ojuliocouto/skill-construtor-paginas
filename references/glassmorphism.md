# Glassmorphism & Efeitos Visuais

### Glass Card Base
```tsx
const GlassCard = ({ children, className = '' }) => (
  <div className={`backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl shadow-xl shadow-black/5 ${className}`}>
    {children}
  </div>
);
```

### Variantes
```tsx
// Light mode glass
"backdrop-blur-xl bg-white/70 border border-white/50 shadow-lg shadow-gray-200/50"

// Dark mode glass
"backdrop-blur-xl bg-gray-900/70 border border-white/10 shadow-xl shadow-black/20"

// Frosted sidebar
"backdrop-blur-2xl bg-gradient-to-b from-white/80 to-white/60 border-r border-white/30"

// Floating action
"backdrop-blur-md bg-white/90 rounded-full shadow-lg shadow-black/10 border border-white/50"
```

### Quando Usar/Nao Usar
- **Usar**: Hero com imagem, cards flutuantes, modais, navbar sutil
- **Nao usar**: Todo card (mata o efeito), areas com muito texto, formularios, tabelas

---
