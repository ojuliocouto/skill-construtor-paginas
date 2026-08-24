# Post-Launch: Medir & Iterar

Sistema de medicao, benchmarks e iteracao apos deploy. A pagina NAO esta "pronta" quando vai ao ar, esta pronta quando CONVERTE.

---

## Setup de Medicao (Fazer no Deploy)

### Microsoft Clarity (Gratis: Obrigatorio)
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

**O que o Clarity entrega gratis:**
- Heatmaps (onde clicam, onde scrollam)
- Session recordings (ver exatamente o que o usuario faz)
- Rage clicks (onde clicam frustrados)
- Dead clicks (clicam em algo que nao e clicavel)
- Scroll depth (% da pagina que veem)
- Quick exits (saem em < 10s)

### GTM Events (se o projeto usar GTM)
Garantir que estes eventos estejam disparando:
- `page_view`: visualizacao
- `scroll_depth`: 25%, 50%, 75%, 90%
- `cta_click`: clique em qualquer CTA
- `form_submit`: envio de formulario
- `video_play`: play no VSL (se houver)
- `checkout_click`: clique no botao de checkout

### Google Analytics 4 (via GTM)
Metricas automaticas:
- Bounce rate
- Session duration
- Pages per session
- Conversion rate (configurar no GA4)

---

## Benchmarks por Tipo de Pagina

### Conversao (% de visitantes que completam a acao desejada)

| Tipo de Pagina | Ruim | OK | Bom | Excelente |
|----------------|------|-----|------|-----------|
| **Sales page** (mid-ticket) | < 1% | 1-2% | 2-5% | > 5% |
| **Sales page** (high-ticket) | < 0.5% | 0.5-1% | 1-3% | > 3% |
| **Capture page** (lead magnet) | < 10% | 10-20% | 20-35% | > 35% |
| **Challenge registration** | < 15% | 15-25% | 25-40% | > 40% |
| **VSL page** | < 1% | 1-3% | 3-7% | > 7% |
| **Checkout bridge** | < 5% | 5-15% | 15-30% | > 30% |

### Bounce Rate

| Tipo | Aceitavel | Preocupante |
|------|-----------|-------------|
| Sales page | < 60% | > 75% |
| Capture page | < 50% | > 65% |
| Challenge page | < 55% | > 70% |

### Scroll Depth

| Metrica | Saudavel | Problema |
|---------|----------|----------|
| Chegam ate 50% da pagina | > 40% | < 25% |
| Chegam ate 75% da pagina | > 25% | < 15% |
| Chegam ate CTA final | > 15% | < 8% |

### Core Web Vitals (Performance)

| Metrica | Bom | Precisa Melhorar | Ruim |
|---------|-----|------------------|------|
| LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| INP | < 200ms | 200-500ms | > 500ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |

---

## Primeiro Check: 48 Horas

Apos 48h com trafego, revisar:

### 1. Scroll Depth
**Onde as pessoas param de scrollar?**
- Se param antes da oferta → secoes anteriores nao engajam
- Se param na oferta → copy/preco nao convence
- Se passam da oferta sem clicar → CTA nao esta claro/visivel

### 2. Heatmap de Cliques
**Onde clicam (e onde NAO clicam)?**
- Clicam em algo que nao e link → adicionar link/CTA ali
- Nao clicam no CTA → CTA nao esta visivel/atrativo
- Rage clicks → algo parece clicavel mas nao e

### 3. Session Recordings (assistir 10 sessoes)
**O que as pessoas fazem?**
- Scrollam rapido sem ler → copy nao prende
- Voltam pra cima → procurando algo que nao acharam
- Hesitam no CTA → objecao nao respondida
- Saem na secao X → secao X e o problema

### 4. Comparar com Benchmark
Se metricas estao ABAIXO do benchmark → ativar ciclo de iteracao.

---

## Ciclo de Iteracao

### Diagnostico por Metrica

| Sintoma | Causa Provavel | Acao |
|---------|----------------|------|
| Bounce > 70% | Hero nao prende / pagina lenta | Testar headline + melhorar LCP |
| Scroll depth < 25% | Secoes iniciais fracas | Reescrever secao pos-hero |
| CTA click < 1% | CTA invisivel ou copy fraca | Aumentar CTA, mudar texto, adicionar urgencia |
| Checkout drop > 80% | Preco alto sem justificativa | Melhorar value stack, adicionar garantia |
| Session < 30s | Pagina nao relevante pro trafego | Message match com o anuncio |
| Rage clicks | UI confusa | Corrigir elementos que parecem clicaveis |

### Prioridade de Teste (Maior Impacto Primeiro)

1. **Headline**: maior impacto em bounce e engagement
2. **CTA texto e posicao**: impacto direto na conversao
3. **Hero section** (imagem/video): primeira impressao
4. **Social proof** (posicao e tipo): influencia na decisao
5. **Oferta/preco** (framing): impacto na conversao final
6. **Design** (cores, layout): menor impacto, mas polimento

### Como Iterar

```
1. Identificar a METRICA mais fraca
2. Identificar a SECAO responsavel (via scroll depth + heatmap)
3. Formular hipotese: "Se eu mudar X, espero que Y melhore porque Z"
4. Fazer a mudanca CIRURGICA (nao reformar a pagina toda)
5. Deploy imediato
6. Esperar 48-72h com trafego
7. Comparar: melhorou? piorou? neutro?
8. Se melhorou → documentar como pattern
9. Se piorou → reverter
10. Repetir com proxima metrica mais fraca
```

---

## Pattern Library Pessoal

Apos cada pagina que funciona bem, documentar:

```markdown
## [Nome da Pagina], [Data]
- **Tipo:** sales page / capture / challenge
- **Preco:** R$X
- **Conversao:** X%
- **LCP:** X.Xs
- **O que funcionou:**
  - Hero: [descrever layout e resultado]
  - CTA: [texto, cor, posicao]
  - Social proof: [tipo e posicao]
  - Secao mais engajada: [qual]
- **O que NAO funcionou:**
  - [descrever e por que]
- **Aprendizado:**
  - [insight principal]
```

Com o tempo, isso cria um banco de patterns TESTADOS que acelera cada proxima pagina.

---

## Ferramentas Gratuitas

| Ferramenta | O que faz | URL |
|------------|-----------|-----|
| Microsoft Clarity | Heatmaps + recordings + rage clicks | clarity.microsoft.com |
| Google PageSpeed Insights | Core Web Vitals + sugestoes | pagespeed.web.dev |
| GTmetrix | Performance detalhada | gtmetrix.com |
| Lighthouse (Chrome DevTools) | Audit completo local | F12 → Lighthouse |
| Google Analytics 4 | Metricas de trafego e conversao | analytics.google.com |
| Meta Pixel Helper | Verifica pixel Meta | Chrome extension |
| Tag Assistant | Verifica GTM | Chrome extension |
