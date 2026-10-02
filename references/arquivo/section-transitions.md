# Biblioteca de Transições Entre Seções

A transição entre seções e invisível quando correta e irritante quando errada. Cada transição deve criar continuidade visual ou marcar uma mudança de capítulo deliberada.

---

## Os 7 Padrões de Transição

### 1. Contraste de Fundo Direto (Sharp Contrast)
**Quando usar:** Mudar de "capítulo" visual (dark para light ou vice-versa). Mais comum.
**Sensação:** Limpeza, clareza, separação de assuntos.

```css
/* Nao ha transicao, a mudanca e abrupta e intencional */
.section-dark  { background: #0a0a14; }
.section-light { background: #ffffff; }
/* Resultado: linha horizontal clara entre as secoes */
```

**Regra:** Funciona quando os backgrounds tem constraste alto. Cinza sobre cinza = não funciona.

---

### 2. Wave Divider SVG
**Quando usar:** Transicao suave entre secoes, especialmente dark-to-light ou light-to-dark. Premium.
**Sensação:** Fluido, orgânico, movimento.

```tsx
// Componente reutilizavel
function WaveDivider({ fromColor, toColor, flip = false }: { fromColor: string; toColor: string; flip?: boolean }) {
  return (
    <div className={`relative h-16 md:h-24 overflow-hidden ${flip ? 'rotate-180' : ''}`}>
      <svg
        className="absolute bottom-0 w-full"
        viewBox="0 0 1440 80"
        preserveAspectRatio="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M0,40 C360,80 1080,0 1440,40 L1440,80 L0,80 Z"
          fill={toColor}
        />
      </svg>
      <div className="absolute inset-0" style={{ background: fromColor }} />
    </div>
  )
}

// Uso:
<WaveDivider fromColor="#0a0a14" toColor="#ffffff" />
<WaveDivider fromColor="#ffffff" toColor="#f8fafc" flip />
```

**Variantes de wave:**
```
Suave (premium):    "M0,40 C360,80 1080,0 1440,40 L1440,80 L0,80 Z"
Agressiva (energia): "M0,0 C480,80 960,0 1440,80 L1440,80 L0,80 Z"
Dupla (luxo):        2 paths com opacidade diferente
Assimétrica:         "M0,60 C400,20 800,80 1440,30 L1440,80 L0,80 Z"
```

---

### 3. Corte Angular (Diagonal Cut)
**Quando usar:** Páginas de energia, desafio, lançamento. Visual dinâmico.
**Sensação:** Momentum, velocidade, ação.

```css
.section-diagonal-bottom {
  clip-path: polygon(0 0, 100% 0, 100% 90%, 0 100%);
  margin-bottom: -4vw; /* compensa o clip */
  padding-bottom: 4vw;
}

.section-diagonal-top {
  clip-path: polygon(0 5%, 100% 0, 100% 100%, 0 100%);
  margin-top: -4vw;
  padding-top: 4vw;
}

/* Angulo mais agressivo: */
.section-sharp-angle {
  clip-path: polygon(0 0, 100% 0, 100% 85%, 0 100%);
}
```

**Regra:** Não usar em mais de 2-3 seções. Cortes demais = página de lanches, não high-ticket.

---

### 4. Gradient Fade de Continuidade
**Quando usar:** Seções complementares que devem parecer um só "bloco". Ex: Hero → Social Proof.
**Sensação:** Fluido, conectado, sem interrupção.

```tsx
// A secao inferior começa com a cor da secao superior (transparente → opaco)
<section className="relative bg-slate-950 pt-0">
  {/* Gradiente de transicao no topo */}
  <div className="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-black/0 to-slate-950 pointer-events-none" />
  {/* Conteudo da secao */}
</section>
```

---

### 5. Card Overlap (Sobreposição de Cards)
**Quando usar:** Uma seção tem cards/elementos que "voam" para dentro da próxima.
**Sensação:** Profundidade, dinamismo, interação entre seções.

```tsx
// O card fica "suspenso" entre duas secoes via margin-top negativa
<section className="bg-slate-950 pb-16">
  {/* Conteudo da secao superior */}
</section>

<section className="bg-white pt-24 relative">
  {/* Cards que aparecem "em cima" da transicao */}
  <div className="max-w-6xl mx-auto px-6 -mt-24 relative z-10">
    <div className="grid grid-cols-3 gap-6">
      <div className="bg-white rounded-2xl shadow-2xl p-8">...</div>
      <div className="bg-white rounded-2xl shadow-2xl p-8">...</div>
      <div className="bg-white rounded-2xl shadow-2xl p-8">...</div>
    </div>
  </div>
  {/* Resto da secao */}
</section>
```

---

### 6. Separador Decorativo (Icon + Linha)
**Quando usar:** Separar sub-secoes dentro de uma seção de mesmo fundo. Não entre seções de cores diferentes.
**Sensação:** Editorial, elegante, organizado.

```tsx
// Linha horizontal com icone central
<div className="flex items-center gap-4 my-16">
  <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
  <div className="w-8 h-8 rounded-full border border-gray-200 dark:border-white/10 flex items-center justify-center">
    <Star className="w-4 h-4 text-gray-300 dark:text-white/30" />
  </div>
  <div className="flex-1 h-px bg-gray-200 dark:bg-white/10" />
</div>

// Variante: 3 pontos
<div className="flex items-center justify-center gap-2 my-16">
  <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
  <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
  <div className="w-1.5 h-1.5 rounded-full bg-gray-300" />
</div>
```

---

### 7. Gradient de Borda de Seção
**Quando usar:** Seções premium com gradiente que "sangra" para a próxima.
**Sensação:** Luxo, sem fronteiras, continuidade de marca.

```tsx
// Secao com gradiente vertical que faz a transicao
<section
  className="relative py-24"
  style={{
    background: 'linear-gradient(to bottom, #0a0a14 0%, #1a1a2e 50%, #0a0a14 100%)'
  }}
>
  {/* A secao seguinte começa no mesmo tom escuro */}
</section>

// Ou: "bleeding" gradient que invade a secao seguinte
<section className="relative bg-slate-950 pb-0">
  <div className="absolute bottom-0 left-0 right-0 h-48 bg-gradient-to-b from-transparent to-white pointer-events-none" />
</section>
<section className="bg-white pt-0">
  {/* Parece continuar da secao anterior */}
</section>
```

---

## Matriz de Decisão: Qual Transição Usar?

| De | Para | Transição Recomendada |
|----|------|-----------------------|
| Dark hero | Light social proof | Sharp contrast OU Wave |
| Light social proof | Dark problema | Sharp contrast |
| Dark problema | Light solução | Wave suave OU Gradient fade |
| Light seção | Light seção (mesma área visual) | Separador decorativo |
| Dark seção | Dark seção seguinte | Gradient de borda |
| Qualquer | Cards flutuando para próxima | Card overlap |
| Light | Diagonal de energia | Corte angular |

---

## Regras Críticas

**NUNCA:** Mesma cor de fundo em 3+ seções seguidas sem nenhuma transição visual.

**NUNCA:** Wave em páginas de energia/desafio, parece premium-suave, não dinâmico.

**NUNCA:** Corte angular em páginas premium/high-ticket, parece landing page de produto barato.

**SEMPRE:** Verificar que o SVG da wave tem a cor exata da seção de destino (não "aproximada").

**MÁXIMO:** 2 tipos diferentes de transição por página. Consistência > variedade.
