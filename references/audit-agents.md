# Auditoria Adversarial por Wave de Subagents (Step 4)

A auditoria de design NUNCA pode ser feita pelo mesmo contexto que construiu a pagina:
o construtor nao enxerga o proprio erro. Por isso o Step 4 dispara uma **wave de
subagents adversariais paralelos**, cada um com UMA lente independente, sem ver o
trabalho dos outros. Um agente de sintese consolida e o gate bloqueia a entrega se
qualquer item critico reprovar.

Orquestracao via tool `Workflow` (parallel/pipeline). Alinhado com a regra global de
planejamento (waves de subagents) e com as regras criticas de workflow do usuario.

---

## Como rodar

1. Compilar a pagina e subir um **preview deploy** (branch, nunca main) OU servir local.
2. Passar a URL (preview/local) + os arquivos relevantes pra CADA agente.

> **Verificacao visual sem Chrome:** se a MCP claude-in-chrome / Chrome nao estiver
> disponivel, dirigir o **Microsoft Edge via Playwright** para screenshot de desktop e
> mobile (`chromium.launch({channel:'msedge'})` ou conectar via CDP). O agente DEVE olhar
> a imagem, nao confiar so no codigo. Validado num projeto real (maquina sem Chrome).

3. Disparar os 7 agentes EM PARALELO (uma unica chamada Workflow `parallel`).
4. Cada agente retorna o schema `VERDICT` abaixo.
5. Agente de sintese consolida. Critico reprovado = **BLOQUEIO**, devolve fixes.
6. Construtor aplica os fixes e re-roda SO os agentes que reprovaram.

---

## Schema de retorno (todo agente)

```json
{
  "lente": "string",
  "aprovado": true,
  "score": 8.5,
  "severidade_max": "none|low|medium|critical",
  "achados": [
    { "item": "string", "severidade": "critical", "evidencia": "string", "fix": "string" }
  ]
}
```

- `severidade: critical` em qualquer achado => `aprovado: false` => bloqueia deploy.
- **Regua unica do gate** (identica a do SKILL.md, Step 4): zero criticos + todas as lentes >= 7 + media >= 8.0 => libera. Lente < 7 bloqueia mesmo sem critical. Media < 8.0 => aplicar polimentos e re-scorar antes de liberar.
- **`evidencia` e OBRIGATORIA e VERIFICAVEL:** screenshot, medicao (px, ratio de contraste, touch target), trecho de codigo com linha, ou passo de reproducao. Achado sem evidencia concreta = descartado pela sintese, nao conta como critico. Motivo: auditor sem obrigacao de evidencia gera falso-positivo (caso real: 2 de 5 "criticos" refutados com medicao).
- **`fix` NUNCA pode violar as regras da skill:** proibido sugerir inventar depoimento, criar escassez/urgencia falsa, adicionar dado que nao esta no briefing, ou usar elementos dos tells V1-V15 como "melhoria". A sintese descarta fixes toxicos e registra a ocorrencia.

---

## Os 7 agentes (lentes independentes)

### 1. design-critic (taste / anti-slop)
Roda a skill `design-taste-frontend` sobre a pagina pronta. Avalia as 6 dimensoes de
taste (1-5) e aplica o AI Slop Test. Consulta `references/taste-gate.md`,
`references/anti-vibe-coding.md`, `references/scoring-system.md`.
Conta os tells visuais V1-V15 presentes na pagina (ver `anti-vibe-coding.md`).
**Reprova (critical) se:** media de taste < 4.0, OU **3+ tells visuais de IA presentes**
(limiar do anti-vibe-coding: glow blob, glow no botao, gradient-clip no titulo, indigo+roxo
sobre dark, icones identicos contam sempre), OU footer-legal / checkout quebrado.

### 1b. assets-auditor (presenca de imagem/midia)
Verifica que a pagina NAO e so texto + gradiente + icones SVG. A regra da skill (SKILL.md
linha "PROIBIDO ENTREGAR SEM ASSETS VISUAIS") exige fotos/mockups/video reais.
**Reprova (critical) se:** pagina sem nenhuma imagem/mockup/video real (so SVG generico e
fundo), OU produto digital/SaaS sem mockup do produto, OU lead magnet sem mockup do material
(capa do ebook/guia). Placeholder vazio tambem reprova.
**Reprova (critical) tambem se a ID foi indicada e NAO foi usada:** logo oficial recriado em
texto/SVG aproximado em vez do asset real, paleta ou fonte "parecida" no lugar da indicada.
Quando ha ID fornecida (pasta/arquivo/link/marca), o logo na pagina TEM que ser o oficial.

### 2. visual-auditor (hierarquia / paleta / grid + ENQUADRAMENTO de imagem)
Hierarquia tipografica, coerencia de paleta, spacing, grid desktop. Consulta
`references/desktop-layout-rules.md`, `references/typography-scale.md`,
`references/design-laws.md`.
**Reprova (critical) se:** formato "carta" em high-ticket, secao obrigatoria side-by-side
em coluna unica, titulos sem hierarquia, paleta incoerente.
**ART-DIRECTION DE FOTO (licao de projeto real, jun/2026):** "uniformizar altura do bloco" NAO
e qualidade. Antes de aprovar qualquer imagem, conferir o RECORTE de verdade:
- `object-fit:cover` com aspect-ratio errado CORTA conteudo: rosto pela testa, cabeca cortada,
  print de conversa fatiado no meio. Reprovar se cover cortar o foco (rosto/mensagem). Casar o
  aspect-ratio com a foto (retrato 4/5 pra foto de pessoa; `contain` pra screenshot/clipping que
  precisa ser lido inteiro) e ajustar `object-position` pro rosto.
- **Hero em retrato no MOBILE**: foto alta empurra o rosto pra baixo da dobra (so aparece o cabelo).
  Conferir o primeiro viewport mobile (390px) e enquadrar (aspect 1/1 + object-position no rosto).
- **LAZY-LOAD**: imagem com `loading="lazy"` pode NAO ter carregado na hora do screenshot, e card
  vazio parece "ok". SEMPRE forcar load (scroll + `i.loading='eager';i.src=i.src`) e esperar
  `i.complete && i.naturalWidth>0` ANTES de julgar. Card vazio = re-capturar, nunca aprovar.

### 3. motion-auditor (animacoes)
Scroll reveal, hover, counters, hero entrance, micro-interacoes. Consulta
`references/animation-audit.md`, `references/section-transitions.md`.
**Reprova (critical) se:** hero sem animacao de entrada, secoes estaticas sem feedback,
cards sem reacao ao hover.

### 4. mobile-auditor (responsivo)
Breakpoints 320px / 375px / 768px, hamburger JS funcional, sem overflow/texto cortado.
Consulta `references/mobile-checklist-detailed.md`.
**Reprova (critical) se:** layout quebra no mobile, hamburger nao funciona, overflow
horizontal.

### 5. cro-auditor (conversao / funil)
CTAs suficientes e bem posicionados, form funcional, WhatsApp, oferta/value stack,
message match, Hook/Story/Offer. Consulta `references/strategist-audit.md`,
`references/cta-placement-map.md`, `references/social-proof-hierarchy.md`,
`references/urgency-scarcity-patterns.md`.
**Reprova (critical) se:** CTA insuficiente, form quebrado, checkout errado, sem message
match com o trafego.

### 6. a11y-auditor (acessibilidade)
Focus states, labels de form, alt text, ARIA, contraste 4.5:1, `prefers-reduced-motion`,
zero emojis. Consulta `references/trust-signals-placement.md` para selos.
**Reprova (critical) se:** falha WCAG critica (contraste, label, alt ausente em imagem de
conteudo), emoji na pagina.

---

## Agente de sintese (consolidador)

Recebe os 7 verdicts. Produz:

```json
{
  "deploy_liberado": false,
  "criticos": [ { "lente": "...", "item": "...", "fix": "..." } ],
  "polimentos": [ { "lente": "...", "item": "...", "fix": "..." } ],
  "scores": { "design": 7.5, "visual": 8, "motion": 6, "mobile": 9, "cro": 8, "a11y": 7 }
}
```

Regra do gate (LITERALMENTE a mesma do SKILL.md, Step 4, e do README):
- `criticos.length > 0` => `deploy_liberado: false`. PARA. Devolve a lista pro construtor.
- Qualquer lente com `score < 7` => `deploy_liberado: false`, mesmo sem nenhum critico.
- Media dos scores < 8.0 => `deploy_liberado: false`: aplicar os polimentos apontados e re-scorar.
- Libera deploy APENAS com: zero criticos + todas as lentes >= 7 + media >= 8.0.

---

## Esqueleto Workflow (referencia)

```js
export const meta = {
  name: 'auditoria-pagina',
  description: 'Wave adversarial de 7 agentes auditando a pagina antes do deploy',
  phases: [{ title: 'Auditar' }, { title: 'Sintese' }],
}

const URL = args.url            // preview/local
const ARQ = args.arquivos       // paths relevantes

const LENTES = [
  { key: 'design-critic',   ref: 'taste-gate.md, anti-vibe-coding.md (contar tells V1-V15: 3+ = critical)' },
  { key: 'assets-auditor',  ref: 'SKILL.md regra PROIBIDO ENTREGAR SEM ASSETS VISUAIS' },
  { key: 'visual-auditor', ref: 'desktop-layout-rules.md, typography-scale.md' },
  { key: 'motion-auditor', ref: 'animation-audit.md, section-transitions.md' },
  { key: 'mobile-auditor', ref: 'mobile-checklist-detailed.md' },
  { key: 'cro-auditor',    ref: 'strategist-audit.md, cta-placement-map.md' },
  { key: 'a11y-auditor',   ref: 'trust-signals-placement.md' },
]

const verdicts = await parallel(LENTES.map(l => () =>
  agent(
    `Auditar a pagina ${URL} (arquivos: ${ARQ}) pela lente ${l.key}. ` +
    `Consultar ${l.ref}. Default adversarial: na duvida, reprovar. Retornar o schema VERDICT.`,
    { label: l.key, phase: 'Auditar', schema: VERDICT_SCHEMA }
  )
)).filter(Boolean)

const sintese = await agent(
  `Consolidar estes verdicts: ${JSON.stringify(verdicts)}. ` +
  `Critico reprovado = deploy_liberado:false. Retornar schema SINTESE.`,
  { label: 'sintese', phase: 'Sintese', schema: SINTESE_SCHEMA }
)

return sintese
```

Quem chama o Workflow passa `args: { url, arquivos }`. O retorno governa o gate do Step 4:
`deploy_liberado:false` => corrigir criticos e re-rodar so as lentes reprovadas.
