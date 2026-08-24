# Page Types: Classificacao e Regras por Tipo

Sistema de classificacao de paginas que determina layout, tom visual, e regras especificas ANTES de qualquer codigo.

---

## Classificacao Rapida

Ao receber um pedido de pagina, classificar em 4 dimensoes:

### 1. Tipo de Pagina

| Tipo | Descricao | Formato carta OK? |
|------|-----------|-------------------|
| **sales-page** | Venda de produto/servico (mentoria, curso, coaching) | NAO: obrigatorio desktop layout rico |
| **capture** | Captura de email/lead (opt-in, waitlist, lead magnet) | SIM: pagina curta, pode ser centrada |
| **challenge** | Inscricao em desafio/evento (5 dias, webinar, workshop) | NAO: precisa de visual impactante |
| **vsl** | Video Sales Letter (video + botao) | SIM: foco e 100% no video |
| **institutional** | Sobre nos, programa, escola | NAO: precisa de profissionalismo visual |
| **checkout-bridge** | Pagina pre-checkout (upsell, order bump) | SIM: curta, direta, foco no CTA |
| **thank-you** | Pos-compra/inscricao | SIM: informacional, curta |

### 2. Faixa de Preco

| Faixa | Valor | Impacto no Layout |
|-------|-------|-------------------|
| **free** | R$0 (lead magnet, desafio gratuito) | Visual atrativo mas pode ser simples. Velocidade maxima. |
| **low-ticket** | R$7: R$97 | Formato carta funciona. Copy curta. Impulse buy. |
| **mid-ticket** | R$197: R$997 | Layout deve comunicar valor. Side-by-side obrigatorio. Social proof pesado. |
| **high-ticket** | R$1.000+ | Layout PREMIUM obrigatorio. Cada secao precisa comunicar valor alto. Nada pode parecer "barato". |

### 3. Tom Visual

| Tom | Quando usar | Paleta sugerida |
|-----|-------------|-----------------|
| **premium** | Mentoria high-ticket, programa exclusivo | Dark + accent gold/amber, tipografia pesada |
| **urgente** | Lancamento, deadline, ultimas vagas | Cores vibrantes, countdown, vermelho/laranja |
| **educacional** | Curso, workshop, masterclass | Light mode, azul/verde, clean |
| **pessoal** | Marca pessoal do mentor, "sobre mim" | Cores da marca, foto grande, tom intimo |
| **energia** | Desafio, evento, transformacao | Gradientes ousados, animacoes, preto+neon |

### 4. Temperatura da Audiencia

| Temp | Descricao | Impacto na Pagina |
|------|-----------|-------------------|
| **fria** | Nunca ouviu falar de voce | Pagina LONGA. Muita prova social. Storytelling. Educacao antes da oferta. Copy detalhada. |
| **morna** | Conhece voce mas nunca comprou | Pagina MEDIA. Foco em beneficios + prova social + garantia. Menos educacao, mais persuasao. |
| **quente** | Ja te segue/consome conteudo | Pagina CURTA. Direto ao ponto. Oferta clara + CTA. Menos storytelling. |

---

## Templates de Secoes por Tipo de Pagina

### Sales Page (Mentoria/Curso): High-Ticket

```
Secoes OBRIGATORIAS (nesta ordem):
1. Hero (split 60/40, texto + foto/video)
2. Social Proof Bar (4 stats ou logos)
3. Problema (3-col cards ou split)
4. Solucao (split 50/50)
5. Beneficios (zigzag 2-4 rows)
6. O que recebe (mockup + lista)
7. Bonus (3-col grid)
8. Depoimentos (featured + grid)
9. Sobre o Mentor (foto + bio side-by-side)
10. Value Stack (lista precos)
11. Garantia (badge + texto)
12. FAQ (titulo left + accordion right)
13. CTA Final (full-bleed dark)

Regras especificas:
- NUNCA formato carta
- Light mode para vendas (dados comprovam melhor leitura)
- Dark sections para contraste (problema, value stack, CTA)
- Minimo 8 CTAs espalhados pela pagina
- Depoimentos com foto/video (nunca so texto)
- Preco com ancoragem visual (valor riscado + preco real)
```

### Sales Page (Mentoria/Curso): VSL-First

```
Secoes OBRIGATORIAS:
1. Hero com VSL (video dominante, 60-70% do hero)
2. CTA abaixo do video (aparece apos X minutos ou scroll)
3. Social Proof (stats + logos)
4. Beneficios resumidos (3-col cards)
5. Depoimentos (grid ou carousel)
6. O que recebe (lista compacta)
7. Garantia
8. FAQ
9. CTA Final

Regras especificas:
- Video e o elemento PRINCIPAL, design serve o video
- CTA pode aparecer condicionalmente (apos pitch no video)
- Pagina mais CURTA que sales page full, video faz o trabalho pesado
- Mobile: video 100% width, nada ao lado
```

### Capture Page (Lead Magnet / Opt-in)

```
Secoes OBRIGATORIAS:
1. Hero (headline + subheadline + form de captura)
2. Beneficios do lead magnet (3 bullets ou cards)
3. Social proof rapido (numeros ou logos)
4. CTA repetido

Secoes OPCIONAIS:
- Sobre o autor (mini bio)
- FAQ (2-3 perguntas)

Regras especificas:
- CURTA, max 2-3 telas de scroll
- Formato centrado OK (pagina simples)
- Form com MAX 3 campos (nome + email + whatsapp)
- CTA acima do fold OBRIGATORIO
- Velocidade MAXIMA (< 1.5s LCP)
- Sem distracao, sem navbar com links, sem footer elaborado
```

### Challenge Page (Desafio 5 Dias)

```
Secoes OBRIGATORIAS:
1. Hero (headline + data do evento + CTA de inscricao)
2. O que vai aprender (3-5 dias listados)
3. Para quem e (perfil do participante)
4. Sobre o mentor
5. Social proof (resultados de desafios anteriores)
6. FAQ
7. CTA Final com urgencia

Regras especificas:
- Dark mode com energia (gradientes, neon, animacoes)
- Countdown para data do evento
- Urgencia real (vagas limitadas, data fixa)
- Mobile-first (maioria vem de stories/reels)
```

### Institutional Page (Programa/Escola)

```
Secoes OBRIGATORIAS:
1. Hero (missao/visao + visual impactante)
2. Numeros/Stats
3. O que oferecemos (servicos/produtos)
4. Diferenciais (por que somos diferentes)
5. Depoimentos / Cases
6. Equipe / Fundadores
7. CTA (aplicar, contato, agendar)

Regras especificas:
- Layout PREMIUM obrigatorio (nao pode parecer amador)
- Light mode predominante (profissionalismo)
- Tipografia elegante
- Muita foto real (nao stock)
- Navegacao completa (navbar com links)
```

---

## Decision Tree Rapido

```
O usuario mandou material para criar pagina?
│
├── E um PDF/Doc com copy completa?
│   ├── SIM → Step 0: Classificar tipo + extrair + avaliar
│   └── NAO → Pedir material ou criar copy primeiro
│
├── Qual o tipo?
│   ├── Sales page → Consultar template Sales Page acima
│   ├── Capture → Template Capture (curta, centrada OK)
│   ├── Challenge → Template Challenge (dark-theme, alta urgencia)
│   ├── VSL → Template VSL-First
│   ├── Institutional → Template Institutional
│   └── Outro → Classificar pelo mais proximo
│
├── Qual a faixa de preco?
│   ├── Free/Low-ticket → Layout pode ser simples
│   ├── Mid-ticket → Side-by-side obrigatorio
│   └── High-ticket → Layout PREMIUM, zero "formato carta"
│
├── Qual o tom?
│   ├── Premium → Dark + gold, tipografia pesada
│   ├── Urgente → Cores vibrantes, countdown
│   ├── Educacional → Light, clean, azul/verde
│   ├── Pessoal → Marca do mentor
│   └── Energia → Gradientes, animacoes, neon
│
└── Temperatura da audiencia?
    ├── Fria → Pagina LONGA, muito storytelling + prova
    ├── Morna → Pagina MEDIA, beneficios + prova
    └── Quente → Pagina CURTA, oferta + CTA direto
```

---

## Contexto de Funil (Obrigatorio Considerar)

Antes de buildar, perguntar/identificar:

**De onde vem o trafego?**
- Anuncio Meta (Facebook/Instagram) → Message match com o ad
- Stories/Reels organico → Tom pessoal, mobile-first pesado
- Email marketing → Audiencia morna/quente, pode ser mais direto
- Google Ads → Intent alto, foco em beneficio + CTA rapido
- WhatsApp broadcast → Ultra-quente, pagina minima

**O que vem DEPOIS da pagina?**
- Checkout direto (Hotmart/Kiwify) → CTA aponta pro checkout
- Grupo de WhatsApp → CTA aponta pro link do grupo
- Pagina de obrigado → Upsell ou instrucoes
- Sequencia de email → Captura primeiro, venda depois

**Message Match:**
O headline da pagina DEVE ecoar a promessa do anuncio/post que trouxe o usuario. Se o anuncio diz "Aprenda a faturar 10K/mes com automacao", o hero da pagina deve reforcar isso imediatamente.
