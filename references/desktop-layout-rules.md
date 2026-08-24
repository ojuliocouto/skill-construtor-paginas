# Desktop Layout Rules: Anti "Formato Carta"

Regras obrigatorias de layout para paginas desktop. Baseado em pesquisa com dados de NN/G, CXL, Stanford Web Credibility Project e analise de paginas de venda brasileiras (Erico Rocha, Thiago Nigro, Pedro Sobral, Leandro Ladeira).

---

## O Problema: Formato Carta

O "formato carta" e uma pagina com:
- Coluna unica centralizada (~700px)
- Texto bloco apos bloco
- Zero conteudo side-by-side
- Parece um documento Word, nao uma pagina de vendas

**Por que falha em desktop:**
- Desperdiça 60%+ do viewport em monitores 1920px
- Sem ancoras visuais para guiar o scanning (F-pattern/Z-pattern)
- Monotonia visual causa "content blindness" (86% dos usuarios)
- Comunica produto de R$47-197: nao de R$1.000+
- Stanford: 46.1% julgam credibilidade pelo visual ANTES de ler

**Quando formato carta E valido:**
- Carta de vendas estilo Gary Halbert (ebook R$47)
- VSL page (so video + botao)
- Email renderizado como pagina
- Low-ticket impulse buy
- Mobile (tudo e single column anyway)

---

## 7 Regras Nao-Negociaveis

### Regra 1: Max 2 secoes seguidas com mesmo layout
Nunca mais de 2 secoes com layout identico em sequencia. Apos 2 blocos centrados, DEVE haver mudanca (side-by-side, grid, full-bleed).

### Regra 2: Alternar direcao do conteudo
Para cada 3 secoes, ao menos 1 deve ter conteudo side-by-side com visual alternando lados:
- Secao A: imagem esquerda + texto direita
- Secao B: texto esquerda + imagem direita

### Regra 3: Visual element a cada ~900px
Usuarios devem encontrar um elemento visual significativo (imagem, grid de icones, video, mudanca de background) a cada 1.5 viewport heights.

### Regra 4: Hero DEVE ter elemento visual ao lado
Hero (above the fold) DEVE conter: headline + subheadline + CTA + elemento visual (foto, video, mockup) em layout side-by-side ou assimetrico. Hero so-texto desperdiça o real estate mais valioso da pagina.

### Regra 5: Secoes que OBRIGATORIAMENTE sao side-by-side no desktop
| Secao | Motivo |
|-------|--------|
| Mentor/instrutor bio | Foto ao lado do texto cria conexao pessoal |
| Depoimentos com foto | Face + quote lado a lado e 2-3x mais credivel |
| Features/modulos | Icone/imagem + descricao melhora scannability |
| Before/After | Comparacao so funciona em 2 colunas |
| Garantia | Badge + texto lado a lado sinaliza legitimidade |

### Regra 6: Alternar backgrounds a cada 3-4 secoes
Criar "capitulos" visuais com backgrounds diferentes:
- Dark (slate-950, gray-950, navy)
- Light (white, gray-50, cream)
- Gradient (indigo→purple, orange→amber)
- Full-bleed image/video

### Regra 7: Texto max 600-700px, viewport USADO
Linhas de texto devem ter 50-75 caracteres (~600-700px). Mas o RESTANTE do viewport deve ser UTILIZADO (imagens, decorativos, whitespace intencional). Nunca margens vazias acidentais.

---

## Grid System Padrao

### Container
```css
.container {
  max-width: 1200px; /* padrao */
  margin: 0 auto;
  padding: 0 24px;
}
/* Variantes: */
/* 960px, conservador (Erico Rocha) */
/* 1200px, mais comum (padrao recomendado) */
/* 1280px, image-heavy pages */
/* 1440px, ultra-wide com muito visual */
```

### Grid Splits Comuns
| Pattern | CSS Grid | Quando usar |
|---------|----------|-------------|
| 50/50 | `grid-template-columns: 1fr 1fr` | Hero, benefits alternados |
| 60/40 | `grid-template-columns: 3fr 2fr` | Hero (texto pesado), about mentor |
| 40/60 | `grid-template-columns: 2fr 3fr` | Modulos com mockup |
| 33/33/33 | `repeat(3, 1fr)` | Cards de beneficio, testimonials, pricing |
| 25x4 | `repeat(4, 1fr)` | Stats counter, feature icons |
| Full | `1fr` | FAQ, garantia, CTA final (OK ser single col) |

### Responsive Breakpoints
```css
/* Mobile: single column */
@media (max-width: 767px) { /* 1 coluna, stacked */ }

/* Tablet: 2 colunas reduzidas */
@media (min-width: 768px) and (max-width: 1023px) { /* 2 colunas */ }

/* Desktop: grid completo */
@media (min-width: 1024px) { /* 2-4 colunas */ }
```

### Section Padding Vertical
```css
.section         { padding: 80px 0; }   /* padrao */
.section--large  { padding: 120px 0; }  /* hero, pricing */
.section--small  { padding: 48px 0; }   /* social proof bar, garantia */
```

---

## Templates de Layout por Secao

### HERO: Split Screen (60/40)
```html
<section style="min-height:90vh; display:flex; align-items:center;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:3fr 2fr; gap:48px; align-items:center;">
    <!-- Coluna texto -->
    <div>
      <span class="badge">Tag/Badge</span>
      <h1>Headline grandao</h1>
      <p>Subheadline explicando o valor</p>
      <a href="#" class="btn-primary">CTA Principal</a>
      <div class="social-proof">+2.400 alunos</div>
    </div>
    <!-- Coluna visual -->
    <div>
      <img src="mentor-foto.webp" alt="Mentor" />
      <!-- ou: video embed, mockup, ilustracao -->
    </div>
  </div>
</section>
```

### SOCIAL PROOF BAR: 4-Stat Counter
```html
<section style="padding:48px 0; background:#f8f8f8;">
  <div style="max-width:1200px; margin:0 auto;
    display:grid; grid-template-columns:repeat(4,1fr); gap:32px; text-align:center;">
    <div>
      <span class="stat-number">2.400+</span>
      <span class="stat-label">Alunos</span>
    </div>
    <div>
      <span class="stat-number">98%</span>
      <span class="stat-label">Satisfacao</span>
    </div>
    <div>
      <span class="stat-number">R$50M+</span>
      <span class="stat-label">Faturados</span>
    </div>
    <div>
      <span class="stat-number">5 anos</span>
      <span class="stat-label">No mercado</span>
    </div>
  </div>
</section>
```

### PROBLEMA: 3-Column Icon Cards
```html
<section style="padding:80px 0; background:#0a0a14; color:white;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;">
    <h2 style="text-align:center; margin-bottom:48px;">Voce sente que...</h2>
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:32px;">
      <div class="pain-card">
        <svg><!-- icone --></svg>
        <h3>Titulo da dor 1</h3>
        <p>Descricao do problema</p>
      </div>
      <!-- repete 2x -->
    </div>
  </div>
</section>
```

### SOLUCAO / BENEFICIOS: Zigzag Alternado
```html
<!-- Beneficio 1: imagem esquerda + texto direita -->
<section style="padding:80px 0;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:center;">
    <div>
      <img src="beneficio-1.webp" alt="Beneficio 1" style="border-radius:16px;" />
    </div>
    <div>
      <h3>Beneficio 1</h3>
      <p>Explicacao do beneficio com detalhes relevantes.</p>
    </div>
  </div>
</section>

<!-- Beneficio 2: texto esquerda + imagem direita (INVERTIDO) -->
<section style="padding:80px 0; background:#f9fafb;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:1fr 1fr; gap:64px; align-items:center;">
    <div>
      <h3>Beneficio 2</h3>
      <p>Explicacao do beneficio com detalhes relevantes.</p>
    </div>
    <div>
      <img src="beneficio-2.webp" alt="Beneficio 2" style="border-radius:16px;" />
    </div>
  </div>
</section>
```

**Regra NN/G para zigzag:** Funciona quando as imagens tem VALOR INFORMACIONAL (screenshots, resultados, diagramas). Falha com imagens decorativas genericas. Max 2-4 rows de zigzag.

### O QUE RECEBE: Mockup 40% + Lista 60%
```html
<section style="padding:80px 0; background:#0a0a14; color:white;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:2fr 3fr; gap:48px; align-items:start;">
    <!-- Mockup do produto -->
    <div>
      <img src="course-mockup.webp" alt="Curso" style="width:100%; border-radius:12px;" />
    </div>
    <!-- Lista de modulos -->
    <div>
      <h2>O que voce recebe</h2>
      <div class="module-list">
        <div class="module-item" style="display:grid; grid-template-columns:40px 1fr; gap:16px; padding:20px 0; border-bottom:1px solid rgba(255,255,255,0.1);">
          <span class="module-number" style="font-size:24px; font-weight:800; color:var(--accent);">01</span>
          <div>
            <h4>Nome do Modulo</h4>
            <p>Descricao breve do conteudo</p>
          </div>
        </div>
        <!-- repete para cada modulo -->
      </div>
    </div>
  </div>
</section>
```

### BONUS: 3-Column Card Grid
```html
<section style="padding:80px 0; background:linear-gradient(135deg, #1a0a2e, #0a0a14);">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;">
    <h2 style="text-align:center; color:white; margin-bottom:48px;">Bonus Exclusivos</h2>
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:24px;">
      <div class="bonus-card" style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); border-radius:16px; padding:32px;">
        <span class="bonus-tag">BONUS #1</span>
        <h3>Nome do Bonus</h3>
        <p>Descricao do valor</p>
        <span class="bonus-value">Valor: R$497</span>
      </div>
      <!-- repete -->
    </div>
  </div>
</section>
```

### DEPOIMENTOS: Featured + 3-Column Grid
```html
<section style="padding:80px 0; background:#f9fafb;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;">
    <!-- Depoimento destaque -->
    <div style="display:grid; grid-template-columns:300px 1fr; gap:40px; padding:48px; background:white; border-radius:16px; margin-bottom:40px;">
      <img src="aluno-destaque.webp" alt="Aluno" style="border-radius:12px; width:100%; aspect-ratio:3/4; object-fit:cover;" />
      <div>
        <div class="stars"><!-- 5 estrelas --></div>
        <p class="quote">"Depoimento completo do aluno destaque com detalhes especificos sobre resultados..."</p>
        <p class="name"><strong>Nome do Aluno</strong>, Cargo/Contexto</p>
      </div>
    </div>
    <!-- Grid de depoimentos menores -->
    <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:24px;">
      <div class="testimonial-card"><!-- quote + nome + foto --></div>
      <!-- repete -->
    </div>
  </div>
</section>
```

**Alternativa BR:** Grid de screenshots de WhatsApp (3 colunas). Muito comum no mercado de infoprodutos brasileiro.

### SOBRE O MENTOR: Foto 40% + Bio 60%
```html
<section style="padding:80px 0;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:2fr 3fr; gap:64px; align-items:center;">
    <div>
      <img src="mentor-pro.webp" alt="Nome do Mentor" style="border-radius:16px; width:100%; aspect-ratio:3/4; object-fit:cover;" />
    </div>
    <div>
      <span class="section-label">Quem vai te guiar</span>
      <h2>Nome do Mentor</h2>
      <p>Bio com credenciais, resultados e historia resumida. Incluir numeros concretos (faturamento, anos de experiencia, alunos formados).</p>
      <div class="mentor-stats" style="display:grid; grid-template-columns:repeat(3,1fr); gap:24px; margin-top:32px;">
        <div><strong>10+ anos</strong><br>de experiencia</div>
        <div><strong>5.000+</strong><br>alunos</div>
        <div><strong>R$50M+</strong><br>faturados</div>
      </div>
    </div>
  </div>
</section>
```

### VALUE STACK: Lista com precos + CTA
```html
<section style="padding:100px 0; background:#0a0a14; color:white;">
  <div style="max-width:900px; margin:0 auto; padding:0 24px; text-align:center;">
    <h2>Tudo que voce recebe</h2>
    <div class="value-list" style="margin:48px 0;">
      <div class="value-item" style="display:grid; grid-template-columns:1fr auto; padding:20px 0; border-bottom:1px solid rgba(255,255,255,0.1); text-align:left;">
        <span>Modulo Principal Completo</span>
        <span style="text-decoration:line-through; opacity:0.5;">R$1.997</span>
      </div>
      <!-- repete para cada item -->
    </div>
    <p class="total-crossed" style="font-size:32px; text-decoration:line-through; color:#ff4444;">De R$8.994</p>
    <p class="actual-price" style="font-size:56px; font-weight:900; color:#00ff88; margin:16px 0;">Por apenas 12x R$97</p>
    <a href="#" class="btn-primary" style="font-size:20px; padding:20px 48px;">QUERO MINHA VAGA AGORA</a>
  </div>
</section>
```

### GARANTIA: Badge + Texto (max 800px, centrado OK)
```html
<section style="padding:80px 0;">
  <div style="max-width:800px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:180px 1fr; gap:40px; align-items:center;">
    <img src="garantia-badge.webp" alt="Garantia 7 dias" style="width:180px;" />
    <div>
      <h3>Garantia Incondicional de 7 Dias</h3>
      <p>Se por qualquer motivo voce sentir que nao e pra voce, basta pedir reembolso em ate 7 dias e devolvemos 100% do seu investimento.</p>
    </div>
  </div>
</section>
```

### FAQ: Titulo Left + Accordion Right
```html
<section style="padding:80px 0; background:#f9fafb;">
  <div style="max-width:1200px; margin:0 auto; padding:0 24px;
    display:grid; grid-template-columns:1fr 2fr; gap:64px;">
    <!-- Lado esquerdo: titulo sticky -->
    <div style="position:sticky; top:100px; align-self:start;">
      <h2>Perguntas Frequentes</h2>
      <p>Tire suas duvidas antes de comecar.</p>
    </div>
    <!-- Lado direito: accordion -->
    <div class="faq-list">
      <details class="faq-item">
        <summary>Pergunta 1?</summary>
        <p>Resposta detalhada.</p>
      </details>
      <!-- repete -->
    </div>
  </div>
</section>
```

### CTA FINAL: Full-bleed dark + centrado
```html
<section style="padding:100px 0; background:linear-gradient(135deg, #0a0a14, #1a1a2e); text-align:center;">
  <div style="max-width:800px; margin:0 auto; padding:0 24px;">
    <h2 style="font-size:42px; color:white; margin-bottom:24px;">
      Pronto pra transformar seus resultados?
    </h2>
    <p style="color:rgba(255,255,255,0.6); margin-bottom:40px;">
      Ultimas vagas com condicao especial. Garantia de 7 dias.
    </p>
    <a href="#" class="btn-primary" style="font-size:20px; padding:20px 48px;">
      QUERO COMECAR AGORA
    </a>
  </div>
</section>
```

---

## Fluxo Ideal de Secoes: Pagina de Mentoria/Curso

```
SECAO           | LAYOUT DESKTOP                | BACKGROUND
----------------+-------------------------------+------------------
1. Hero         | Split 60/40 (texto + foto)    | Dark/gradient
2. Social Proof | 4-stat counter row            | Light (#f8f8f8)
3. Problema     | 3-col icon cards              | Dark
4. Solucao      | Split 50/50 (texto + img)     | White
5. Beneficios   | Zigzag alternado (2-4 rows)   | Alternating bg
6. O que recebe | Mockup 40% + lista 60%        | Dark
7. Bonus        | 3-col card grid               | Gradient
8. Depoimentos  | Featured + 3-col grid         | Light
9. Sobre mentor | Foto 40% + bio 60%            | White
10. Value Stack | Lista precos centrado (900px)  | Dark
11. Garantia    | Badge + texto (max 800px)      | White
12. FAQ         | Titulo left + accordion right  | Light
13. CTA Final   | Full-bleed dark + centrado     | Dark (=hero)
```

---

## Checklist Desktop Layout

Antes de entregar qualquer pagina, verificar:

- [ ] Hero tem elemento visual ao lado do texto (nunca so texto)
- [ ] Nao ha mais de 2 secoes seguidas com layout identico
- [ ] Secao "Sobre o Mentor" tem foto ao lado do texto
- [ ] Depoimentos usam grid (nunca lista vertical unica)
- [ ] Benefits/features alternam direcao (zigzag ou grid)
- [ ] Backgrounds alternam claro/escuro a cada 3-4 secoes
- [ ] Texto nunca ultrapassa 700px de largura em linhas corridas
- [ ] Container principal e 1200px (nao 700px "carta")
- [ ] Mobile colapsa pra single column naturalmente
- [ ] Nenhuma secao obrigatoria side-by-side esta em coluna unica no desktop
