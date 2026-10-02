# Post-Launch: Medir & Iterar

Sistema de medição, benchmarks e iteração após deploy. A página NÃO está "pronta" quando vai ao ar, esta pronta quando CONVERTE.

---

## Setup de Medição (Fazer no Deploy)

### Microsoft Clarity (Grátis: Obrigatório)
```html
<!-- Adicionar no <head> de TODA pagina -->
<script type="text/javascript">
(function(c,l,a,r,i,t,y){
  c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
  t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
  y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
})(window,document,"clarity","script","SEU_PROJECT_ID");
</script>
```

**O que o Clarity entrega grátis:**
- Heatmaps (onde clicam, onde scrollam)
- Session recordings (ver exatamente o que o usuário faz)
- Rage clicks (onde clicam frustrados)
- Dead clicks (clicam em algo que não é clicável)
- Scroll depth (% da página que veem)
- Quick exits (saem em < 10s)

### GTM Events (se o projeto usar GTM)
Garantir que estes eventos estejam disparando:
- `page_view`: visualização
- `scroll_depth`: 25%, 50%, 75%, 90%
- `cta_click`: clique em qualquer CTA
- `form_submit`: envio de formulário
- `video_play`: play no VSL (se houver)
- `checkout_click`: clique no botão de checkout

### Google Analytics 4 (via GTM)
Métricas automáticas:
- Bounce rate
- Session duration
- Pages per session
- Conversion rate (configurar no GA4)

---

## Benchmarks por Tipo de Página

### Conversão (% de visitantes que completam a ação desejada)

| Tipo de Página | Ruim | OK | Bom | Excelente |
|----------------|------|-----|------|-----------|
| **Sales page** (mid-ticket) | < 1% | 1-2% | 2-5% | > 5% |
| **Sales page** (high-ticket) | < 0.5% | 0.5-1% | 1-3% | > 3% |
| **Capture page** (lead magnet) | < 10% | 10-20% | 20-35% | > 35% |
| **Challenge registration** | < 15% | 15-25% | 25-40% | > 40% |
| **VSL page** | < 1% | 1-3% | 3-7% | > 7% |
| **Checkout bridge** | < 5% | 5-15% | 15-30% | > 30% |

### Bounce Rate

| Tipo | Aceitável | Preocupante |
|------|-----------|-------------|
| Sales page | < 60% | > 75% |
| Capture page | < 50% | > 65% |
| Challenge page | < 55% | > 70% |

### Scroll Depth

| Métrica | Saudável | Problema |
|---------|----------|----------|
| Chegam até 50% da página | > 40% | < 25% |
| Chegam até 75% da página | > 25% | < 15% |
| Chegam até CTA final | > 15% | < 8% |

### Core Web Vitals (Performance)

| Métrica | Bom | Precisa Melhorar | Ruim |
|---------|-----|------------------|------|
| LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| INP | < 200ms | 200-500ms | > 500ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |

---

## Primeiro Check: 48 Horas

Após 48h com tráfego, revisar:

### 1. Scroll Depth
**Onde as pessoas param de scrollar?**
- Se param antes da oferta → seções anteriores não engajam
- Se param na oferta → copy/preco não convence
- Se passam da oferta sem clicar → CTA não está claro/visivel

### 2. Heatmap de Cliques
**Onde clicam (e onde NÃO clicam)?**
- Clicam em algo que não é link → adicionar link/CTA ali
- Não clicam no CTA → CTA não está visivel/atrativo
- Rage clicks → algo parece clicável mas não é

### 3. Session Recordings (assistir 10 sessões)
**O que as pessoas fazem?**
- Scrollam rápido sem ler → copy não prende
- Voltam pra cima → procurando algo que não acharam
- Hesitam no CTA → objeção não respondida
- Saem na seção X → seção X e o problema

### 4. Comparar com Benchmark
Se métricas estão ABAIXO do benchmark → ativar ciclo de iteração.

---

## Ciclo de Iteração

### Diagnóstico por Métrica

| Sintoma | Causa Provável | Ação |
|---------|----------------|------|
| Bounce > 70% | Hero não prende / página lenta | Testar headline + melhorar LCP |
| Scroll depth < 25% | Seções iniciais fracas | Reescrever seção pos-hero |
| CTA click < 1% | CTA invisível ou copy fraca | Aumentar CTA, mudar texto, adicionar urgência |
| Checkout drop > 80% | Preço alto sem justificativa | Melhorar value stack, adicionar garantia |
| Session < 30s | Página não relevante pro tráfego | Message match com o anúncio |
| Rage clicks | UI confusa | Corrigir elementos que parecem clicáveis |

### Prioridade de Teste (Maior Impacto Primeiro)

1. **Headline**: maior impacto em bounce e engagement
2. **CTA texto e posição**: impacto direto na conversão
3. **Hero section** (imagem/video): primeira impressão
4. **Social proof** (posição e tipo): influencia na decisão
5. **Oferta/preco** (framing): impacto na conversão final
6. **Design** (cores, layout): menor impacto, mas polimento

### Como Iterar

```
1. Identificar a MÉTRICA mais fraca
2. Identificar a SEÇÃO responsável (via scroll depth + heatmap)
3. Formular hipótese: "Se eu mudar X, espero que Y melhore porque Z"
4. Fazer a mudança CIRÚRGICA (não reformar a página toda)
5. Deploy imediato
6. Esperar 48-72h com tráfego
7. Comparar: melhorou? piorou? neutro?
8. Se melhorou → documentar como pattern
9. Se piorou → reverter
10. Repetir com próxima métrica mais fraca
```

---

## Pattern Library Pessoal

Após cada página que funciona bem, documentar:

```markdown
## [Nome da Página], [Data]
- **Tipo:** sales page / capture / challenge
- **Preço:** R$X
- **Conversão:** X%
- **LCP:** X.Xs
- **O que funcionou:**
  - Hero: [descrever layout e resultado]
  - CTA: [texto, cor, posição]
  - Social proof: [tipo e posição]
  - Seção mais engajada: [qual]
- **O que NÃO funcionou:**
  - [descrever e por que]
- **Aprendizado:**
  - [insight principal]
```

Com o tempo, isso cria um banco de patterns TESTADOS que acelera cada próxima página.

---

## Ferramentas Gratuitas

| Ferramenta | O que faz | URL |
|------------|-----------|-----|
| Microsoft Clarity | Heatmaps + recordings + rage clicks | clarity.microsoft.com |
| Google PageSpeed Insights | Core Web Vitals + sugestões | pagespeed.web.dev |
| GTmetrix | Performance detalhada | gtmetrix.com |
| Lighthouse (Chrome DevTools) | Audit completo local | F12 → Lighthouse |
| Google Analytics 4 | Métricas de tráfego e conversão | analytics.google.com |
| Meta Pixel Helper | Verifica pixel Meta | Chrome extension |
| Tag Assistant | Verifica GTM | Chrome extension |
