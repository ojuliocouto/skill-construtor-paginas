# Tailwind CSS Patterns

### Breakpoints Responsivos (Mobile-First)
- `sm:` 640px+, `md:` 768px+, `lg:` 1024px+, `xl:` 1280px+, `2xl:` 1536px+

### Layouts Essenciais

**Flexbox**:
```html
<div class="flex flex-col md:flex-row gap-4">
  <div class="flex-1">Item 1</div>
  <div class="flex-1">Item 2</div>
</div>
```

**Grid Responsivo**:
```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
  <div>Item</div>
</div>
```

**Bento Grid**:
```html
<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
  <div class="col-span-2 row-span-2">Grande</div>
  <div class="col-span-1">Pequeno</div>
  <div class="col-span-1">Pequeno</div>
  <div class="col-span-2">Medio</div>
</div>
```

**Container**:
```html
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">Conteudo</div>
```

### Dark Mode
```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <p class="text-gray-600 dark:text-gray-400">Texto secundario</p>
</div>
```

### Transicoes e Animacoes
```html
<button class="bg-blue-500 hover:bg-blue-700 transition duration-300">Hover</button>
<div class="hover:-translate-y-1 hover:shadow-xl transition-all">Lift</div>
<div class="animate-pulse">Pulsando</div>
```

### Tailwind v4.1+ CSS-First Config
```css
@import "tailwindcss";
@theme {
  --color-brand-500: #3b82f6;
  --font-display: "Inter", system-ui, sans-serif;
  --animate-fade-in: fadeIn 0.5s ease-in-out;
}
```

---
