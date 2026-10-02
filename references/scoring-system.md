# Sistema de Scoring: Auditoria Pre-Entrega

Toda página entregue DEVE ser pontuada neste scorecard antes do deploy. Nota mínima por dimensão: **8/10**. Qualquer dimensão abaixo de 7 = BLOQUEIO. Corrigir antes de entregar.

---

## Scorecard Completo (10 dimensões)

### DIMENSÃO 1: Hierarquia Visual: /10

| Nota | Critério |
|------|----------|
| 10 | Olho navega naturalmente: hero → problema → solução → prova → oferta. F-pattern ou Z-pattern implícito. Sem pontos de confusão. |
| 8-9 | Hierarquia clara na maioria das seções. 1-2 seções menos óbvias mas funcionais. |
| 6-7 | Hierarquia perceptível mas inconsistente. Algumas seções "brigam" por atenção. |
| 4-5 | Elementos de mesmo peso visual competindo. Olho não sabe onde ir. |
| 0-3 | Sem hierarquia. Tudo parece igual. Caos visual. |

**Como verificar:** cubra os olhos, abra a página, espere 3 segundos. Onde seu olho foi primeiro? Era para la que devia ir?

---

### DIMENSÃO 2: Tipografia: /10

| Nota | Critério |
|------|----------|
| 10 | Escala consistente (D/H1/H2/H3/body/small). Razão mínima 1.25x entre níveis. Line-height 1.4-1.7 no body. Letter-spacing correto por peso. Zero fontes conflitantes. |
| 8-9 | Escala quase perfeita. 1-2 valores ligeiramente fora mas sem impacto visual notável. |
| 6-7 | Hierarquia tipográfica presente mas com inconsistências (H2 muito próximo do H3, body muito pequeno ou grande). |
| 4-5 | Fontes misturadas sem lógica. Tamanhos aleatórios. Line-height sufocado. |
| 0-3 | Tipografia completamente inconsistente. Parece montagem aleatória. |

**Checklist rápido:**
- [ ] H1 ≥ 48px desktop / ≥ 32px mobile
- [ ] Body ≥ 16px (nunca 14px no body corrido)
- [ ] Line-height body: 1.5-1.7
- [ ] Max 2 famílias tipográficas na página
- [ ] Pesos usados: máximo 3 (regular, semibold, bold/black)

---

### DIMENSÃO 3: Animações: /10

| Nota | Critério |
|------|----------|
| 10 | 100% das seções tem scroll reveal. Todos os elementos interativos tem hover state. Timing 0.3-0.6s. Easing suave (ease-out ou spring). Animações servem o conteúdo: não distraem. |
| 8-9 | Animações em todas as seções principais. 1-2 hover states faltando em elementos menores. |
| 6-7 | Scroll reveal presente mas inconsistente. Alguns hovers faltando em botões secundários. |
| 4-5 | Animações só no hero. Resto estático. |
| 0-3 | Página completamente estática ou animações excessivas que distraem. |

**Ver:** `references/animation-audit.md` para checklist detalhado.

---

### DIMENSÃO 4: Grid e Layout: /10

| Nota | Critério |
|------|----------|
| 10 | ZERO formato carta no desktop. Hero split. Zigzag em benefícios. Backgrounds alternando a cada 3-4 seções. Container 1200px. Texto nunca mais que 700px de largura. |
| 8-9 | Layout rico na maioria. 1 seção poderia ser mais rica mas não quebra a experiência. |
| 6-7 | Maioria side-by-side mas 2-3 seções em coluna única desnecessariamente. |
| 4-5 | Metade da página em formato carta. Visual monótono. |
| 0-3 | Formato carta completo. Parece documento Word. |

---

### DIMENSÃO 5: CTAs: /10

| Nota | Critério |
|------|----------|
| 10 | ≥8 CTAs distribuídos. Variedade de copy (não idênticos). Peso visual decrescente/crescente estratégico. CTA acima do fold. CTA final com máxima urgência. Cores com contraste mínimo 4.5:1. |
| 8-9 | 6-8 CTAs. Copy variada. Pode ter 1-2 com copy igual mas em posições muito diferentes. |
| 6-7 | 4-5 CTAs. Alguma repetição de copy. Distribuição irregular (muito no final, pouco no meio). |
| 4-5 | 2-3 CTAs. Não há CTA acima do fold ou no meio da página. |
| 0-3 | 1 CTA no final. Página inteira sem chamada para ação intermediária. |

**Ver:** `references/cta-placement-map.md` para posições específicas.

---

### DIMENSÃO 6: Prova Social: /10

| Nota | Critério |
|------|----------|
| 10 | Vídeo testimonial OU foto+quote+resultado específico. Diversidade de perfis. Distribuída na página (não só numa seção). Números reais. Screenshots de mensagens. |
| 8-9 | Fotos + quotes com resultados. Boa diversidade. 1-2 sem resultado específico mas com nome/contexto real. |
| 6-7 | Depoimentos presentes mas sem fotos ou só texto. Resultados vagos. |
| 4-5 | Números sem contexto ou 1-2 depoimentos genéricos. |
| 0-3 | Sem prova social real. Ou só logos sem contexto. |

**N/A: negócio que ainda NÃO tem cliente.** Quando o briefing (Step 0.0) registrou a flag
`sem prova social`, esta dimensão sai da conta em vez de reprovar a página: recalcular a média
**sem** a dimensão 6 e declarar `Prova Social: N/A (sem cliente ainda)` no bloco de entrega.

A troca não é de graça. Pra usar o N/A a página TEM que trazer substitutos reais e
verificáveis, e a wave confere um a um:
- credencial, formação ou registro profissional de quem atende
- fotos do espaço, do equipamento ou do processo (reais, do negócio)
- garantia clara e escrita
- condição de inauguracao/primeira turma, quando existir de verdade
- CNPJ e endereço no footer

Faltando os substitutos, a dimensão VOLTA a valer e pontua normalmente (provavelmente 0-3).
**Inventar depoimento, número de alunos ou resultado continua PROIBIDO:** e exatamente por
isso que a exceção existe.

**Ver:** `references/social-proof-hierarchy.md` para hierarquia e placement.

---

### DIMENSÃO 7: Mobile: /10

| Nota | Critério |
|------|----------|
| 10 | CTA acima do fold no mobile (375px). H1 ≥32px. Touch targets ≥44px. Formulário funcional. Sem scroll horizontal. Hamburger funcional. LCP mobile <2.5s. |
| 8-9 | Quase perfeito. 1-2 ajustes menores de spacing ou tamanho de fonte que não prejudicam uso. |
| 6-7 | Funcional mas não otimizado. CTA talvez não acima do fold. Alguns espaçamentos apertados. |
| 4-5 | Página "cabe" no mobile mas experiência ruim. Texto pequeno, botões difíceis de tocar. |
| 0-3 | Página quebrada no mobile. Scroll horizontal. Layout colapsado. |

**Ver:** `references/mobile-checklist-detailed.md` para checklist completo.

---

### DIMENSÃO 8: Performance Visual: /10

| Nota | Critério |
|------|----------|
| 10 | Imagens WebP + lazy load. Vídeos com pôster. Fontes com font-display: swap. Sem layout shift visível. Animações só após elemento estar visível. LCP desktop <2.5s. |
| 8-9 | Maioria otimizada. Pode ter 1-2 imagens JPG/PNG mas sem impacto perceptível no LCP. |
| 6-7 | Algumas imagens sem lazy load ou sem WebP. LCP aceitável mas poderia melhorar. |
| 4-5 | Imagens pesadas sem otimização. Vídeos sem pôster. LCP lento. |
| 0-3 | Página claramente lenta. Imagens bloqueando render. Sem otimização alguma. |

---

### DIMENSÃO 9: Sinais de Confiança: /10

| Nota | Critério |
|------|----------|
| 10 | Badge de garantia visível próximo ao preço. Logos de pagamento acima do CTA de checkout. Selos de segurança se houver dados sensíveis. Midia/imprensa se disponível. CNPJ/empresa no footer. |
| 8-9 | Garantia presente e bem posicionada. Logos de pagamento presentes. 1-2 outros sinais faltando mas não críticos. |
| 6-7 | Garantia presente mas pouco visível. Logos de pagamento no footer (longe do CTA). |
| 4-5 | Só texto de garantia, sem badge visual. Sem logos de pagamento. |
| 0-3 | Sem sinais de confiança. Página parece sem seriedade. |

**Ver:** `references/trust-signals-placement.md` para posições específicas.

---

### DIMENSÃO 10: Fit Estratégico: /10

Avaliado pela auditoria do estrategista (ver `references/strategist-audit.md`).

| Nota | Critério |
|------|----------|
| 10 | Message match perfeito com o tráfego. Temperatura da página correta. Hook claro. Sequência psicológica AIDA completa. Oferta bem ancorada. Urgência real e crível. |
| 8-9 | Fit estratégico sólido. 1-2 ajustes pontuais (hook poderia ser mais forte, urgência pouco visível). |
| 6-7 | Página funcional mas sem diferencial estratégico. Message match parcial. Urgência fraca. |
| 4-5 | Página genérica. Poderia ser de qualquer produto/nicho. Sem identidade estratégica. |
| 0-3 | Página completamente desconectada da estratégia de funil. Hero não fala com o tráfego. |

---

## Como Aplicar o Scoring

### Passo 1: Pontuar cada dimensão
Abrir a página no navegador. Para cada dimensão, atribuir nota de 0-10 com base nos critérios acima.

### Passo 2: Identificar bloqueios
```
BLOQUEIO CRÍTICO (nota < 7): PÁGINA NÃO PODE SER ENTREGUE
ALERTA (nota 7): Corrigir se possível antes de entregar, registrar se não for possível
APROVADO (nota ≥ 8): Dimensão passou
```

### Passo 3: Calcular média
```
Média = soma de todas as dimensões / 10
Média mínima para entregar: 8.0
```

### Formato de Output do Scoring

```
## SCORECARD, [Nome do Projeto]

| Dimensão              | Nota | Status |
|-----------------------|------|--------|
| Hierarquia Visual     | X/10 | ✅/⚠️/🚫 |
| Tipografia            | X/10 | ✅/⚠️/🚫 |
| Animações             | X/10 | ✅/⚠️/🚫 |
| Grid & Layout         | X/10 | ✅/⚠️/🚫 |
| CTAs                  | X/10 | ✅/⚠️/🚫 |
| Prova Social          | X/10 | ✅/⚠️/🚫 |
| Mobile                | X/10 | ✅/⚠️/🚫 |
| Performance Visual    | X/10 | ✅/⚠️/🚫 |
| Sinais de Confiança   | X/10 | ✅/⚠️/🚫 |
| Fit Estratégico       | X/10 | ✅/⚠️/🚫 |

**MÉDIA: X.X/10**

VEREDICTO: [SHIP ✅ / AJUSTES MENORES ⚠️ / BLOQUEADO 🚫]

Pendências:
- [lista de itens a corrigir se houver]
```

---

## Legenda de Status

| Ícone | Critério |
|-------|----------|
| ✅ | Nota ≥ 8: aprovado |
| ⚠️ | Nota 7: alerta, corrigir se possível |
| 🚫 | Nota < 7: BLOQUEIO, corrigir antes de entregar |
