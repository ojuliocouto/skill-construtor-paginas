# Escala Tipografica: Valores Numericos e Regras

Sistema tipografico para paginas de marketing e vendas. Valores concretos, nao aproximacoes.

---

## Escala de Tamanhos (Desktop / Mobile)

| Nivel | Desktop | Mobile | Peso | Uso |
|-------|---------|--------|------|-----|
| **Display** | 80-96px | 48-56px | 900 | Headline hero impactante, numeros grandes |
| **H1** | 56-72px | 36-44px | 800 | Headline principal de cada secao |
| **H2** | 40-52px | 28-36px | 700-800 | Sub-headline ou titulo de secao |
| **H3** | 28-36px | 22-28px | 600-700 | Titulo de card, item de lista |
| **H4** | 22-26px | 18-22px | 600 | Label de secao, titulo pequeno |
| **Body Large** | 18-20px | 16-18px | 400 | Paragrafo principal, subheadlines |
| **Body** | 16px | 15-16px | 400 | Texto corrido, descricao |
| **Small** | 14px | 13-14px | 400-500 | Microcopy, labels de input |
| **Caption** | 12px | 11-12px | 500 | Legendas, notas de rodape |

**Regra fundamental:** Nunca usar texto corrido abaixo de 16px. Causa zoom automatico no iOS (< 16px em input = zoom).

---

## Ratios de Escala

A razao minima entre niveis adjacentes e **1.25x**. Razao recomendada para impacto: **1.333x** (Perfect Fourth).

```
Display:  96px
H1:       72px   (96 / 1.33)
H2:       54px   (72 / 1.33)
H3:       40px   (54 / 1.33)
H4:       30px   (40 / 1.33)
Body:     16px   (base)
Small:    12px
```

---

## Line Height por Nivel

| Nivel | Line Height | Motivo |
|-------|-------------|--------|
| Display / H1 | 1.0 - 1.15 | Headlines grandes precisam de pouco espacamento |
| H2 / H3 | 1.2 - 1.35 | Titulos medios, ainda densos |
| H4 | 1.3 - 1.5 | Transicao para leitura |
| Body Large | 1.6 - 1.7 | Leitura confortavel de paragrafos |
| Body | 1.6 - 1.75 | Maxima legibilidade de texto corrido |
| Small / Caption | 1.4 - 1.6 | Texto pequeno precisa de respiracao |

---

## Letter Spacing por Peso

| Peso | Letter Spacing | Uso |
|------|---------------|-----|
| 900 (Black) | -0.02em a -0.04em | Headlines impactantes: tracking negativo = poder |
| 800 (ExtraBold) | -0.02em a -0.03em | H1 de vendas |
| 700 (Bold) | -0.01em a -0.02em | H2 e H3 |
| 600 (SemiBold) | 0 a -0.01em | Titulos medios |
| 400 (Regular) | 0 a 0.01em | Texto corrido: tracking neutro |
| 500 em CAPS | 0.08em a 0.15em | Labels em uppercase (SEMPRE tracking positivo em maiusculas) |

**Regra critica:** uppercase + peso alto + sem tracking = ilegível. Todo texto em MAIUSCULAS precisa de `letter-spacing: 0.08em+`.

---

## Font Pairings Aprovados (por Tom Visual)

### Premium / High-Ticket Dark
```css
--font-heading: 'Syne', sans-serif;          /* 700-900, geometrica, autoridade */
--font-body: 'Inter', sans-serif;            /* 400-500, maxima legibilidade */

/* Alternativa: */
--font-heading: 'Space Grotesk', sans-serif; /* moderno, tech */
--font-body: 'Inter', sans-serif;
```

### Energia / Desafio / Lancamento
```css
--font-heading: 'Bebas Neue', sans-serif;    /* Display only, impacto maximo */
--font-body: 'Barlow', sans-serif;           /* 400-600, energia sem agressividade */

/* Alternativa: */
--font-heading: 'Montserrat', sans-serif;    /* 800-900 */
--font-body: 'Open Sans', sans-serif;
```

### Educacional / Clean / Light Mode
```css
--font-heading: 'Plus Jakarta Sans', sans-serif; /* amigavel, moderno */
--font-body: 'Inter', sans-serif;

/* Alternativa: */
--font-heading: 'Outfit', sans-serif;
--font-body: 'DM Sans', sans-serif;
```

### Elegante / Personal Brand
```css
--font-heading: 'Cormorant Garamond', serif; /* 600-700, sofisticado */
--font-body: 'Lato', sans-serif;             /* 300-400, contraste suave */

/* Alternativa: */
--font-heading: 'Playfair Display', serif;   /* editorial */
--font-body: 'Source Sans 3', sans-serif;
```

### SaaS / Tech / Institucional
```css
--font-heading: 'Geist', sans-serif;         /* Clean, tech, moderno */
--font-body: 'Inter', sans-serif;

/* Alternativa: */
--font-heading: 'Cal Sans', sans-serif;
--font-body: 'Inter', sans-serif;
```

---

## Regras de Peso na Hierarquia

| Situacao | Peso correto |
|----------|-------------|
| Headline do hero | 800-900 (impacto maximo) |
| Headline de secao | 700-800 |
| Titulo de card | 600-700 |
| Body / paragrafo | 400 |
| Label uppercase | 500-600 (nunca 400 em caps: muito fino) |
| Preco principal | 800-900 (numero grande) |
| Preco riscado | 400-500 |
| Microcopy abaixo do CTA | 400 |
| Numeracao de modulo (01, 02) | 800-900 + cor accent |

**Regra:** Maximo 3 pesos diferentes na mesma pagina. Mais que isso = visual confuso.

---

## Tailwind CSS: Classes Praticas

```tsx
// Display hero
className="text-7xl md:text-8xl xl:text-9xl font-black tracking-tight leading-none"

// H1 hero padrao
className="text-5xl md:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.1]"

// H2 secao
className="text-4xl md:text-5xl font-bold tracking-tight leading-[1.2]"

// H3 card
className="text-2xl md:text-3xl font-semibold leading-snug"

// H4 label
className="text-lg md:text-xl font-semibold leading-snug"

// Body large (subheadline)
className="text-lg md:text-xl font-normal leading-relaxed text-gray-600"

// Body padrao
className="text-base font-normal leading-relaxed"

// Small / microcopy
className="text-sm font-medium"

// Caption
className="text-xs font-medium tracking-wide"

// Label uppercase
className="text-xs font-semibold tracking-widest uppercase text-gray-500"

// Numero de impacto (stat)
className="text-5xl md:text-6xl font-black tabular-nums"

// Preco principal
className="text-5xl md:text-6xl font-black"

// Preco riscado
className="text-2xl font-normal line-through text-gray-400"
```

---

## Checklist Tipografico

Antes de entregar, verificar:

- [ ] H1 ≥ 56px desktop, ≥ 36px mobile
- [ ] Body ≥ 16px em todos os textos corridos
- [ ] Line-height body ≥ 1.6
- [ ] Letter-spacing negativo nos headings pesados (700+)
- [ ] Letter-spacing positivo em qualquer texto em UPPERCASE
- [ ] Maximo 2 familias tipograficas na pagina
- [ ] Maximo 3 pesos diferentes na pagina
- [ ] Razao entre niveis adjacentes ≥ 1.25x
- [ ] Texto de botao: 16-18px, font-weight 600+
- [ ] Numeros de impacto (stats): `tabular-nums` aplicado
