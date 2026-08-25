# Sistema de Scoring: Auditoria Pre-Entrega

Toda pagina entregue DEVE ser pontuada neste scorecard antes do deploy. Nota minima por dimensao: **8/10**. Qualquer dimensao abaixo de 7 = BLOQUEIO. Corrigir antes de entregar.

---

## Scorecard Completo (10 dimensoes)

### DIMENSAO 1: Hierarquia Visual: /10

| Nota | Criterio |
|------|----------|
| 10 | Olho navega naturalmente: hero → problema → solucao → prova → oferta. F-pattern ou Z-pattern implicito. Sem pontos de confusao. |
| 8-9 | Hierarquia clara na maioria das secoes. 1-2 secoes menos obvias mas funcionais. |
| 6-7 | Hierarquia perceptivel mas inconsistente. Algumas secoes "brigam" por atencao. |
| 4-5 | Elementos de mesmo peso visual competindo. Olho nao sabe onde ir. |
| 0-3 | Sem hierarquia. Tudo parece igual. Caos visual. |

**Como verificar:** cubra os olhos, abra a pagina, espere 3 segundos. Onde seu olho foi primeiro? Era para la que devia ir?

---

### DIMENSAO 2: Tipografia: /10

| Nota | Criterio |
|------|----------|
| 10 | Escala consistente (D/H1/H2/H3/body/small). Razao minima 1.25x entre niveis. Line-height 1.4-1.7 no body. Letter-spacing correto por peso. Zero fontes conflitantes. |
| 8-9 | Escala quase perfeita. 1-2 valores ligeiramente fora mas sem impacto visual notavel. |
| 6-7 | Hierarquia tipografica presente mas com inconsistencias (H2 muito proximo do H3, body muito pequeno ou grande). |
| 4-5 | Fontes misturadas sem logica. Tamanhos aleatorios. Line-height sufocado. |
| 0-3 | Tipografia completamente inconsistente. Parece montagem aleatoria. |

**Checklist rapido:**
- [ ] H1 ≥ 48px desktop / ≥ 32px mobile
- [ ] Body ≥ 16px (nunca 14px no body corrido)
- [ ] Line-height body: 1.5-1.7
- [ ] Max 2 familias tipograficas na pagina
- [ ] Pesos usados: maximo 3 (regular, semibold, bold/black)

---

### DIMENSAO 3: Animacoes: /10

| Nota | Criterio |
|------|----------|
| 10 | 100% das secoes tem scroll reveal. Todos os elementos interativos tem hover state. Timing 0.3-0.6s. Easing suave (ease-out ou spring). Animacoes servem o conteudo: nao distraem. |
| 8-9 | Animacoes em todas as secoes principais. 1-2 hover states faltando em elementos menores. |
| 6-7 | Scroll reveal presente mas inconsistente. Alguns hovers faltando em botoes secundarios. |
| 4-5 | Animacoes so no hero. Resto estatico. |
| 0-3 | Pagina completamente estatica ou animacoes excessivas que distraem. |

**Ver:** `references/animation-audit.md` para checklist detalhado.

---

### DIMENSAO 4: Grid e Layout: /10

| Nota | Criterio |
|------|----------|
| 10 | ZERO formato carta no desktop. Hero split. Zigzag em beneficios. Backgrounds alternando a cada 3-4 secoes. Container 1200px. Texto nunca mais que 700px de largura. |
| 8-9 | Layout rico na maioria. 1 secao poderia ser mais rica mas nao quebra a experiencia. |
| 6-7 | Maioria side-by-side mas 2-3 secoes em coluna unica desnecessariamente. |
| 4-5 | Metade da pagina em formato carta. Visual monotono. |
| 0-3 | Formato carta completo. Parece documento Word. |

---

### DIMENSAO 5: CTAs: /10

| Nota | Criterio |
|------|----------|
| 10 | ≥8 CTAs distribuidos. Variedade de copy (nao identicos). Peso visual decrescente/crescente estrategico. CTA acima do fold. CTA final com maxima urgencia. Cores com contraste minimo 4.5:1. |
| 8-9 | 6-8 CTAs. Copy variada. Pode ter 1-2 com copy igual mas em posicoes muito diferentes. |
| 6-7 | 4-5 CTAs. Alguma repeticao de copy. Distribuicao irregular (muito no final, pouco no meio). |
| 4-5 | 2-3 CTAs. Nao ha CTA acima do fold ou no meio da pagina. |
| 0-3 | 1 CTA no final. Pagina inteira sem chamada para acao intermediaria. |

**Ver:** `references/cta-placement-map.md` para posicoes especificas.

---

### DIMENSAO 6: Prova Social: /10

| Nota | Criterio |
|------|----------|
| 10 | Video testimonial OU foto+quote+resultado especifico. Diversidade de perfis. Distribuida na pagina (nao so numa secao). Numeros reais. Screenshots de mensagens. |
| 8-9 | Fotos + quotes com resultados. Boa diversidade. 1-2 sem resultado especifico mas com nome/contexto real. |
| 6-7 | Depoimentos presentes mas sem fotos ou so texto. Resultados vagos. |
| 4-5 | Numeros sem contexto ou 1-2 depoimentos genericos. |
| 0-3 | Sem prova social real. Ou so logos sem contexto. |

**N/A: negocio que ainda NAO tem cliente.** Quando o briefing (Step 0.0) registrou a flag
`sem prova social`, esta dimensao sai da conta em vez de reprovar a pagina: recalcular a media
**sem** a dimensao 6 e declarar `Prova Social: N/A (sem cliente ainda)` no bloco de entrega.

A troca nao e de graca. Pra usar o N/A a pagina TEM que trazer substitutos reais e
verificaveis, e a wave confere um a um:
- credencial, formacao ou registro profissional de quem atende
- fotos do espaco, do equipamento ou do processo (reais, do negocio)
- garantia clara e escrita
- condicao de inauguracao/primeira turma, quando existir de verdade
- CNPJ e endereco no footer

Faltando os substitutos, a dimensao VOLTA a valer e pontua normalmente (provavelmente 0-3).
**Inventar depoimento, numero de alunos ou resultado continua PROIBIDO:** e exatamente por
isso que a excecao existe.

**Ver:** `references/social-proof-hierarchy.md` para hierarquia e placement.

---

### DIMENSAO 7: Mobile: /10

| Nota | Criterio |
|------|----------|
| 10 | CTA acima do fold no mobile (375px). H1 ≥32px. Touch targets ≥44px. Formulario funcional. Sem scroll horizontal. Hamburger funcional. LCP mobile <2.5s. |
| 8-9 | Quase perfeito. 1-2 ajustes menores de spacing ou tamanho de fonte que nao prejudicam uso. |
| 6-7 | Funcional mas nao otimizado. CTA talvez nao acima do fold. Alguns espacamentos apertados. |
| 4-5 | Pagina "cabe" no mobile mas experiencia ruim. Texto pequeno, botoes dificeis de tocar. |
| 0-3 | Pagina quebrada no mobile. Scroll horizontal. Layout colapsado. |

**Ver:** `references/mobile-checklist-detailed.md` para checklist completo.

---

### DIMENSAO 8: Performance Visual: /10

| Nota | Criterio |
|------|----------|
| 10 | Imagens WebP + lazy load. Videos com poster. Fontes com font-display: swap. Sem layout shift visivel. Animacoes so apos elemento estar visivel. LCP desktop <2.5s. |
| 8-9 | Maioria otimizada. Pode ter 1-2 imagens JPG/PNG mas sem impacto perceptivel no LCP. |
| 6-7 | Algumas imagens sem lazy load ou sem WebP. LCP aceitavel mas poderia melhorar. |
| 4-5 | Imagens pesadas sem otimizacao. Videos sem poster. LCP lento. |
| 0-3 | Pagina claramente lenta. Imagens bloqueando render. Sem otimizacao alguma. |

---

### DIMENSAO 9: Sinais de Confianca: /10

| Nota | Criterio |
|------|----------|
| 10 | Badge de garantia visivel proximo ao preco. Logos de pagamento acima do CTA de checkout. Selos de seguranca se houver dados sensiveis. Midia/imprensa se disponivel. CNPJ/empresa no footer. |
| 8-9 | Garantia presente e bem posicionada. Logos de pagamento presentes. 1-2 outros sinais faltando mas nao criticos. |
| 6-7 | Garantia presente mas pouco visivel. Logos de pagamento no footer (longe do CTA). |
| 4-5 | So texto de garantia, sem badge visual. Sem logos de pagamento. |
| 0-3 | Sem sinais de confianca. Pagina parece sem seriedade. |

**Ver:** `references/trust-signals-placement.md` para posicoes especificas.

---

### DIMENSAO 10: Fit Estrategico: /10

Avaliado pela auditoria do estrategista (ver `references/strategist-audit.md`).

| Nota | Criterio |
|------|----------|
| 10 | Message match perfeito com o trafego. Temperatura da pagina correta. Hook claro. Sequencia psicologica AIDA completa. Oferta bem ancorada. Urgencia real e crivel. |
| 8-9 | Fit estrategico solido. 1-2 ajustes pontuais (hook poderia ser mais forte, urgencia pouco visivel). |
| 6-7 | Pagina funcional mas sem diferencial estrategico. Message match parcial. Urgencia fraca. |
| 4-5 | Pagina genérica. Poderia ser de qualquer produto/nicho. Sem identidade estrategica. |
| 0-3 | Pagina completamente desconectada da estrategia de funil. Hero nao fala com o trafego. |

---

## Como Aplicar o Scoring

### Passo 1: Pontuar cada dimensao
Abrir a pagina no navegador. Para cada dimensao, atribuir nota de 0-10 com base nos criterios acima.

### Passo 2: Identificar bloqueios
```
BLOQUEIO CRITICO (nota < 7): PAGINA NAO PODE SER ENTREGUE
ALERTA (nota 7): Corrigir se possivel antes de entregar, registrar se nao for possivel
APROVADO (nota ≥ 8): Dimensao passou
```

### Passo 3: Calcular media
```
Media = soma de todas as dimensoes / 10
Media minima para entregar: 8.0
```

### Formato de Output do Scoring

```
## SCORECARD, [Nome do Projeto]

| Dimensao              | Nota | Status |
|-----------------------|------|--------|
| Hierarquia Visual     | X/10 | ✅/⚠️/🚫 |
| Tipografia            | X/10 | ✅/⚠️/🚫 |
| Animacoes             | X/10 | ✅/⚠️/🚫 |
| Grid & Layout         | X/10 | ✅/⚠️/🚫 |
| CTAs                  | X/10 | ✅/⚠️/🚫 |
| Prova Social          | X/10 | ✅/⚠️/🚫 |
| Mobile                | X/10 | ✅/⚠️/🚫 |
| Performance Visual    | X/10 | ✅/⚠️/🚫 |
| Sinais de Confianca   | X/10 | ✅/⚠️/🚫 |
| Fit Estrategico       | X/10 | ✅/⚠️/🚫 |

**MEDIA: X.X/10**

VEREDICTO: [SHIP ✅ / AJUSTES MENORES ⚠️ / BLOQUEADO 🚫]

Pendencias:
- [lista de itens a corrigir se houver]
```

---

## Legenda de Status

| Icone | Criterio |
|-------|----------|
| ✅ | Nota ≥ 8: aprovado |
| ⚠️ | Nota 7: alerta, corrigir se possivel |
| 🚫 | Nota < 7: BLOQUEIO, corrigir antes de entregar |
