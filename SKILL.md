---
name: construtor-paginas
description: "Use quando o usuario quiser criar uma pagina web (landing page, sales page, captura, institucional, portfolio, dashboard), clonar uma pagina existente a partir de URL ou PDF, refazer/redesenhar uma pagina (v2, redesign, upgrade visual), otimizar/auditar o visual de uma pagina ja publicada, ou editar algo pontual numa pagina que ja existe (trocar texto, headline, cor, preco, adicionar/remover secao, corrigir mobile). Sinais: criar pagina, landing page, hero section, clonar site, copiar pagina, refazer pagina, pdf para html, melhorar pagina, deixar bonito, editar pagina, trocar texto, mudar cor, ajustar botao, adicionar secao, arrumar mobile. Stacks: React, Next.js, Vue, Svelte, HTML+Tailwind."
---

# Construtor de Paginas - Skill Completa

Skill unificada para construir paginas web profissionais, bonitas e de alta conversao. Combina o melhor de 7 skills especializadas em uma unica referencia.

---

## RUNBOOK (a espinha: leia isto primeiro, o resto e detalhe)

O essencial pra rodar, em poucas linhas. O detalhe de cada item esta nas secoes abaixo; conteudo pesado de implementacao fica em `references/` e so deve ser carregado quando o caso pedir (ver Indice).

1. **4 caminhos:** CRIAR do zero / CLONAR (URL ou PDF) / MELHORAR (pagina que ja existe e vai continuar existindo) / EDITAR (mudanca pontual). **Rotear ANTES de tudo** (ver "OS 4 CAMINHOS"): cada um tem fluxo e gates proprios. Rodar 6 steps numa troca de headline e tao errado quanto editar no improviso uma pagina nova.
1b. **ANTES DE TUDO:** rodar `python3 <dir-da-skill>/scripts/checar-ferramentas.py`. Critico sem responder = PARA e conduz a correcao. Ferramenta morta com fallback silencioso ja deixou as duas camadas visuais desligadas por meses.
2. **Step 0 comeca pela ENTREVISTA DE BRIEFING (0.0):** as seis perguntas da rodada 1 pra todo mundo, rodada 2 so pra quem ja tem cliente. Sem as seis respondidas, nao avanca. Depois: checar pre-requisitos (MCPs/skills), instalar AUTOMATICAMENTE o que nao pede chave (Stitch), instalar Playwright (o unico necessario na pratica), **oferecer uma vez** 21st.dev/Pexels/Taste Skills e, sem chave, seguir pelo fallback com a degradacao DECLARADA na entrega. Nenhuma dependencia bloqueia o inicio. Por fim, carregar contexto do projeto.
3. **Ordem sagrada:** COPY (Step 1) → DESIGN (Step 2) → CODIGO (Step 3). Nunca pixel antes de copy travada.
4. **Step 1:** se o usuario ja trouxe copy, validar e travar (COPY LOCK); senao gerar (copy-pagina-vendas opcional).
5. **Step 2:** consultar o banco de design (`search.py`, keywords em INGLES) pra estilo/paleta/fonte antes de inventar; wireframe no Stitch (ou fallback).
6. **Step 3:** buildar com componentes do 21st.dev (ou a mao), **assets reais** (foto/mockup/video, nunca so SVG+gradiente), zero dado inventado.
7. **Step 4 e O PORTAO:** rodar a wave de auditoria adversarial (7 lentes + sintese). Deploy acontece DENTRO do Step 4, DEPOIS da wave.
8. **ENFORCEMENT (caminhos CRIAR, CLONAR e MELHORAR):** a mensagem de entrega DEVE conter o BLOCO OBRIGATORIO DA ENTREGA, com as quatro linhas fixas (veredito da wave, identidade da pagina, passe de gosto, prova de entrega) mais as pendencias. Texto unico e completo na secao "ENFORCEMENT DO GATE" do Step 4, item 2. Sem o bloco = voce pulou o gate = falhou. **No caminho EDITAR a wave NAO roda:** ali o bloco e o checklist de regressao + a prova do ponto alterado.
9. **MCPs/skills sao obrigatorios QUANDO conectados;** se ausentes, usar o fallback documentado, nunca travar.
10. **Bloqueia entrega:** 3+ tells de IA, pagina sem asset real, footer-legal/checkout quebrado, dado inventado, nota < 7 em qualquer dimensao.
11. **Regras absolutas do output:** zero travessao (grep U+2014 = 0), zero emoji, acentuacao PT-BR correta, consistencia de contato.
11b. **NUNCA INVENTAR ID VISUAL.** Se o usuario indicou/forneceu a identidade (pasta de assets, logo, paleta, fontes, link, PDF, slides), USAR O ASSET REAL. Recriar logo em texto/SVG aproximado, chutar cor ou fonte = PROIBIDO. So criar do zero quando NAO ha ID indicada. Logo legivel demais a 40px? Aumenta o tamanho ou pede uma versao, nunca substitui por uma invencao.
12. **Pos-sessao:** registrar contexto em `references/sessions/` e `references/projects/` (locais). Proibido entregar e nao registrar.
13. **Atalhos:** capture simples/pagina trivial → ROTA EXPRESSA (steps colapsados, wave de 3 lentes). Sessao nao-interativa ou "faz direto" → sem paradas, gates inline (ver excecao no protocolo de execucao).

---

## MAPA DESTE ARQUIVO (onde cada coisa mora)

| Bloco | Secoes |
|---|---|
| **Roteamento** | RUNBOOK, QUANDO ACIONAR, OS 4 CAMINHOS (CRIAR / CLONAR / MELHORAR / EDITAR), PORTA UNICA |
| **Preparacao** | PROTOCOLO DE ATIVACAO (pre-requisitos + instalacao), GATE DE QUALIDADE auxiliar, PROTOCOLO POS-SESSAO, Indice de `references/` |
| **O fluxo** | Processo de 6 Steps, parada forcada, rota expressa, regras inegociaveis, anti-patterns, gates, tech stack, **Step 0** (0.0 briefing, 0.1 a 0.7), **Step 1** copy, **Step 2** direcao, **Step 3** build (3.2 video, **3.2b movimento/Higgsfield**, 3.6 auto-revisao), **Step 4** (4.0 wave, 4.0b/4.1 scoring, 4.2 QA, **4.2b identidade**, **4.2c passe de gosto**, 4.3 deploy, 4.4 QA pos, 4.5 prova, GATE 4), **Step 5** medir |
| **Apendice** | Regras de deploy, anti-patterns de codigo, blueprints, projetos e sessoes locais, links e galerias |

**Nada que seja etapa de execucao mora depois do Step 5.** Se voce esta escrevendo uma exigencia
nova, ela entra dentro do step que a executa, nunca no fim do arquivo.

---

## QUANDO ACIONAR: 4 GATILHOS OBRIGATORIOS (sem exceção)

Esta skill DEVE ser acionada automaticamente, ANTES de qualquer código, sempre que o usuário quiser:

1. **CRIAR uma página nova** (landing, sales page, institucional, home, dashboard, etc.)
2. **CLONAR uma página existente** (de URL ao vivo ou PDF): "clonar essa página", "copiar esse site", "replicar esse layout"
3. **MELHORAR uma página que já existe e vai continuar existindo**: "melhora essa página", "otimiza", "aumenta a conversão", "deixa mais bonita", "audita essa página", e também "refazer / v2 / redesign" quando o objetivo é elevar a mesma página
4. **EDITAR algo pontual numa página existente**: "troca o headline", "muda a cor do botão", "corrige o preço", "adiciona uma seção de FAQ", "arruma no mobile"

Se a mensagem do usuário cair em qualquer um dos 4, ACIONE a skill primeiro. Não começar a codar,
nem perguntar detalhes soltos, antes de entrar no fluxo da skill (Step 0 → ...). Falha histórica
documentada: numa sessao de clone real (jun/2026) o agente NÃO acionou a skill de cara e o usuário teve que
mandar, não repetir.

Caso de clone especificamente: ler `references/projects/` antes, e seguir as regras de clone
(manter identidade original: cores via `getComputedStyle`, logo real baixado do site). Ver
anti-patterns no fim deste arquivo e o checklist visual em `references/anti-vibe-coding.md`.

---

## OS 4 CAMINHOS: ROTEAR ANTES DE QUALQUER COISA

O fluxo de 6 steps foi desenhado pra pagina NOVA. Aplicar ele inteiro numa troca de
headline gera atrito e faz o usuario abandonar a skill; e pular ele numa pagina nova
gera pagina feia. Por isso a PRIMEIRA decisao e sempre: **qual dos 4 caminhos e este?**

Declarar o caminho escolhido na primeira resposta, em uma linha, antes de executar:
`Caminho: EDITAR (mudanca pontual em pagina existente).`

| Sinal no pedido | Caminho | Fluxo |
|---|---|---|
| nao existe pagina ainda | **CRIAR** | 6 steps completos |
| "clona / copia / replica" + URL ou PDF | **CLONAR** | fluxo CLONE (abaixo) |
| pagina existe e o pedido e elevar o todo | **MELHORAR** | fluxo MELHORAR (abaixo) |
| pagina existe e o pedido e um ponto especifico | **EDITAR** | fluxo EDITAR (abaixo) |

**Na duvida entre MELHORAR e EDITAR, pergunte.** A diferenca e escopo: mexer em uma
coisa nomeada e EDITAR; revisar a pagina e MELHORAR. Errar pra mais (rodar melhoria
quando ele queria trocar uma palavra) irrita tanto quanto errar pra menos.

**O que vale nos 4 caminhos, sem excecao:** nunca inventar ID visual, nunca inventar
dado, zero travessao, zero emoji, acentuacao correta, asset real, e prova de entrega
(screenshot do resultado lido com os proprios olhos) antes de dizer que acabou.

---

### CAMINHO 1: CRIAR (pagina nova, do zero)

Objetivo: pagina que ainda nao existe. **Este e o unico caminho que roda o rito completo:
os 6 steps, com parada forcada entre eles e os 4 gates.** O fluxo detalhado esta na secao
"Processo de 6 Steps: Workflow Principal", mais abaixo neste arquivo.

Resumo da ordem, que e sagrada: Step 0 entender e inventariar, Step 1 COPY (fecha em
COPY LOCK), Step 2 DIRECAO (banco de design + wireframe), Step 3 BUILDAR (componentes e
assets reais), Step 4 AUDITAR (wave de 7 lentes) e so entao deploy, Step 5 pos-sessao.
Nunca pixel antes de copy travada.

---

### CAMINHO 2: CLONAR (URL ao vivo ou PDF)

Objetivo: reproduzir com fidelidade. **Aqui a copy e a identidade JA EXISTEM: nao
minerar VoC, nao escrever copy nova, nao rodar COPY LOCK.** Inventar aqui e defeito.

1. **Extrair o real, nunca olhar e chutar.** Rodar o extrator (testado em 08/08/2026):

   ```bash
   # requer playwright: npm install -g playwright && npx playwright install chromium
   node <dir-da-skill>/scripts/extrai-identidade.mjs "<URL>"
   ```

   Devolve em JSON: paleta real ordenada por frequencia de uso, variaveis CSS da marca
   (`--laranja: #FA4E04` etc), o h1 e o CTA com estilo computado, lista de secoes e as
   imagens. Logo: BAIXAR o arquivo, nunca recriar. Do PDF: extrair pelo arquivo.
   `redesign-existing-projects` ajuda na leitura critica do que foi extraido.

   **Gotcha do extrator (custou duas tentativas no teste):** o Playwright e CommonJS,
   entao em arquivo `.mjs` ele entra pelo default export, e o `NODE_PATH` **nao vale
   pra `import`**, so pra `require`. O script resolve isso sozinho via `createRequire`
   (procura o playwright no projeto, no NODE_PATH e no root global do npm). Nunca cravar
   caminho absoluto de `node_modules` no script: so funciona na maquina de quem escreveu.
2. **Inventariar o que existe**: secoes na ordem, componentes, breakpoints, interacoes.
3. **Declarar o delta**: o que sera identico e o que muda (e por que). Sem pedido
   explicito, o default e ZERO mudanca de identidade.
4. **Buildar** seguindo Step 3 (assets reais, stack do projeto).
5. **GATE DE FIDELIDADE** (substitui o Gate 1 e 2): print do original e do clone lado
   a lado, conferindo cor a cor, fonte, hierarquia, ordem das secoes e mobile. Divergiu
   sem ter sido declarado no delta? Volta.
6. Step 4 normal (wave, identidade 4.2b, passe de gosto 4.2c, deploy, QA pos, prova 4.5) e pos-sessao.

### CAMINHO 3: MELHORAR (a pagina continua sendo a mesma, so melhor)

Objetivo: elevar sem destruir o que ja funciona. O erro classico e "melhorar" trocando
tudo e derrubando a conversao que existia.

1. **BASELINE PRIMEIRO, obrigatorio.** Antes de tocar em qualquer coisa: screenshot
   desktop e mobile do estado atual, Lighthouse atual, e o que ja converte (se houver
   dado). Sem baseline nao existe "melhorou", existe "ficou diferente".

   ```bash
   # screenshot do estado atual: usar o script canonico, que roda Playwright
   node <dir-da-skill>/scripts/screenshot-prova.js "<URL>" ./baseline

   # Lighthouse: roda por npx (v12.8.2 confirmada). PRECISA de Chrome/Chromium instalado.
   # Sem Chrome, ele falha com "No Chrome installations found." e vira PENDENCIA
   # DECLARADA: anote na entrega e SIGA. Lighthouse NAO bloqueia o gate (ver Step 4.2).
   # SEM Chrome instalado, use o Chromium que o Playwright ja baixou. Testado e funcionando
   # em Mac sem Chrome (scores 100/100/89/90); a flag --no-sandbox e o que faz funcionar:
   #   export NODE_PATH="$HOME/.npm-global/lib/node_modules"
   #   export CHROME_PATH="$(node -e "console.log(require('playwright').chromium.executablePath())")"
   #   npx lighthouse "<URL>" --quiet --chrome-flags="--headless=new --no-sandbox" --output=json
   npx lighthouse "<URL>" --quiet --chrome-flags="--headless=new" --output=json \
     --output-path=baseline_lh.json
   ```

   **MEDIR SEMPRE COM COMPRESSAO. `python3 -m http.server` NAO comprime, e isso
   inverte o resultado.** Custou meia sessao em 08/08/2026 numa pagina de lancamento: servida sem
   gzip, a versao nova aparecia PIOR (Performance 76 vs 77, LCP 7,3s vs 6,3s) e o gate
   bloqueou; servida com gzip, as duas empatam em 93 e LCP 3,2s, com a nova melhor em
   TBT. A pagina era a mesma: mudou so o servidor. Sem compressao o HTML ia inteiro
   (116 KB); com gzip, 18 KB. Cloudflare Pages e Vercel servem comprimido, entao medir
   sem compressao compara um cenario que nao existe. Usar
   `scripts/servidor-gzip.py <pasta> <porta>` pra servir o build local.

   **NUNCA usar Edge headless com `--window-size=390` pra simular mobile.** Ele nao emula
   dispositivo: so estreita a janela mantendo layout de desktop, e o screenshot sai com
   texto "cortado" na direita. Isso gera diagnostico falso de overflow. Custou uma rodada
   inteira de investigacao em 08/08/2026 numa pagina de lancamento: o print acusava corte, e a
   medicao real (`scrollWidth` vs `clientWidth` em 320/375/390/768/1024) deu ZERO overflow.
   Mobile de verdade = Playwright com `isMobile: true` e `deviceScaleFactor: 2`.

   Guardar os screenshots e o JSON: o gate do fim compara contra eles.
2. **Diagnostico com nota**, nao opiniao solta: rodar `references/taste-gate.md` e
   `references/anti-vibe-coding.md` sobre a pagina atual, e listar os problemas com
   nota por dimensao.
3. **Priorizar por impacto**: hierarquia e espacamento primeiro (maior alavancagem),
   depois copy do above-the-fold, depois assets, depois movimento. Cosmetico por ultimo.
4. **Preservar o que funciona.** Nao mexer no que ja converte sem motivo declarado.
   Identidade so muda com pedido explicito.
5. **Aplicar em lotes revisaveis**, do maior impacto pro menor.
6. **GATE DE MELHORIA (nao-regressao, ADICIONAL ao GATE 4, nunca no lugar dele)**: antes e
   depois lado a lado, com a nota de cada dimensao nos dois estados. **Se alguma dimensao
   piorou, nao entrega.** Lighthouse entra so como comparacao CONDICIONAL: **se houve baseline
   de Lighthouse**, o novo tem que ser igual ou melhor; **sem navegador nao ha baseline**, entao
   vira pendencia declarada e NAO bloqueia (igual ao item 1 e ao 4.2). O que bloqueia aqui e a
   nao-regressao por dimensao, que nao depende de navegador.
7. **Step 4 normal** (wave, identidade 4.2b, passe de gosto 4.2c, deploy, QA pos, prova 4.5) e
   pos-sessao. O gate de melhoria empilha SOBRE o GATE 4; ele nao substitui nenhum item dele.

### CAMINHO 4: EDITAR (mudanca pontual, cirurgica)

Objetivo: fazer exatamente o que foi pedido, sem efeito colateral. **Este caminho NAO
roda os 6 steps e NAO tem parada forcada entre steps.** Rodar o rito completo aqui e
erro de processo.

1. **Travar o escopo em uma frase** e repetir pro usuario: "vou trocar o headline da
   hero, e so isso". Se o pedido tiver mais de uma coisa, listar todas antes de comecar.
2. **Localizar o arquivo real** que serve a pagina no ar (nao um parecido). Conferir
   qual projeto/rota esta publicado antes de editar.
3. **Editar so o escopo.** Proibido "ja que estou aqui" mexer em espacamento, cor ou
   copy que ninguem pediu. Melhoria fora do escopo = propor no fim, nao aplicar.
4. **Checklist de regressao** (o que quebra sem avisar): mobile, dark mode se existir,
   links e ancoras, formulario e checkout, e a secao vizinha a que foi tocada.
5. **Deploy** seguindo a regra de nunca sobrescrever projeto existente.
6. **PROVA**: screenshot do ponto alterado no ar, desktop e mobile, lido com os proprios
   olhos. Mais a confirmacao de que o resto da pagina continua igual.
7. Registro curto na sessao (o que mudou e onde), sem o relatorio completo.

**Gates que NAO se aplicam ao caminho EDITAR:** COPY LOCK, direcao visual, wireframe,
wave de 7 lentes. Uma edicao pontual nao precisa reauditar a pagina inteira. O que
continua valendo: regressao, prova de entrega e as regras absolutas de output.

---

## PORTA UNICA: NENHUMA SKILL DE DESIGN RODA SOZINHA PRA PAGINA

Existem varias skills de design instaladas (`frontend-design`, `design-taste-frontend`,
`high-end-visual-design`, `animate`, `canvas-design`, `brandkit`, `redesign-existing-projects`,
`impeccable`). **Nenhuma delas atende um pedido de pagina por conta propria.** Todas sao
ETAPAS deste fluxo, e quem decide quando cada uma entra e esta skill.

Motivo: sozinhas elas cobrem so um pedaco. A `frontend-design`, por exemplo, tem 55 linhas
e trata de direcao estetica; ela nao trava copy, nao consulta o banco de design, nao exige
asset real, nao roda a wave de auditoria, nao publica e nao registra a sessao. Uma pagina
entregue so com ela sai bonita e falha nos gates que ja custaram retrabalho aqui.

**Regra de precedencia (nao negociar):**
- Pedido de pagina (criar, clonar, refazer) = ESTA skill assume, sempre, mesmo que o usuario
  cite outra skill pelo nome. Se ele pedir "faz com a frontend-design", entra por aqui e a
  `frontend-design` e usada DENTRO do Step 2.
- As outras skills sao invocadas por ESTA, no step certo, e o resultado volta pro fluxo.
- Nunca rodar duas skills de design em paralelo disputando a mesma decisao: a ordem abaixo
  existe pra que cada uma opine no momento em que a decisao ainda esta aberta.

**Onde cada uma entra:**

| Step | Skill que esta skill invoca | Para que |
|------|------------------------------|----------|
| antes do Step 2 | `brandkit` | so se a marca nao existir ainda (logo, paleta, tipografia) |
| Step 2 | `frontend-design` | direcao estetica e tipografica, antes de qualquer codigo |
| Step 2 | `design-taste-frontend` | framework anti-slop na direcao |
| Step 2 (clone) | `redesign-existing-projects` | auditoria audit-first do que ja existe |
| Step 4 | `animate` | movimento e microinteracao, DEPOIS da interface resolvida |
| Step 4 | `high-end-visual-design` | acabamento premium |
| Step 4 | `design-taste-frontend` | de novo, agora como gate anti-slop sobre a pagina pronta |
| Step 4 | `impeccable` (CLI) | refino final opcional |
| fora do fluxo | `canvas-design` | peca grafica estatica (PNG/PDF) que acompanha a pagina, nunca a pagina |

Se o usuario pedir explicitamente so uma etapa ("me da uma direcao estetica", "so anima isso
aqui", "faz um poster"), ai sim a skill especifica roda sozinha: nao e pedido de pagina.

---

## PROTOCOLO DE ATIVACAO: EXECUTAR SEMPRE AO INICIAR

**OBRIGATORIO ao ser acionado:**

### 0. VERIFICAR PRE-REQUISITOS (MCPs + plugins + skills): RODA PRIMEIRO

Antes de qualquer coisa, checar o que esta DISPONIVEL na sessao e direcionar o
usuario a instalar o que faltar. O modelo enxerge as ferramentas/skills ativas no
proprio contexto (lista de tools + system-reminders de skills). Confirmar presenca de:

| Dependencia | Como detectar | Papel | Fallback (caminho legitimo, nunca bloqueia o inicio) |
|-------------|---------------|-------|---------|
| **Playwright** | `node <dir-da-skill>/scripts/screenshot-prova.js --check` | prova de entrega, extrator de identidade, gate de video | **necessario na pratica** (prova obrigatoria nos 4 caminhos): `npm install -g playwright && npx playwright install chromium` |
| **ffmpeg / ffprobe** | `ffprobe -version` | gate de video (so em pagina com video) | pular o gate de video |
| **Higgsfield (CLI)** | `higgsfield account status` (imprime e-mail, plano e creditos) | movimento e b-roll nos blocos (Step 3.2b), **passo esperado, nao enfeite** | conta PAGA para uso comercial. Sem ela: material real do cliente, gravacao de tela, b-roll de acervo aberto ou animacao CSS/Framer Motion, com a pendencia declarada na entrega. Setup completo (inclusive o `higgsfield workspace set <id>`, que trava todo mundo) em `references/higgsfield.md` |
| **HF_API_KEY_ID + HF_API_KEY_SECRET (env)** | `echo $HF_API_KEY_ID` | rota por API do `scripts/higgsfield.py` (lote, `--dry-run`) | usar a CLI (rota assistida) ou seguir sem movimento gerado |
| **Stitch (MCP)** | tools `mcp__stitch__*` | wireframe (Step 2) | auto-instalar (protocolo item 1); ultimo caso: layout direto no codigo |
| **21st.dev Magic (MCP)** | tools `mcp__magic__*` | componentes (Step 3) | recomendado (protocolo item 3); fallback: componentes a mao (shadcn/Tailwind) |
| **design-taste-frontend (skill)** | skill listada | gate anti-slop (Step 4) | recomendado (protocolo item 4); fallback: scoring manual 4.0b |
| **redesign-existing-projects (skill)** | skill listada | audit-first em clone/redesign (Step 2) | recomendado (protocolo item 4); fallback: auditoria manual das 5 dimensoes |
| **high-end-visual-design (skill)** | skill listada | acabamento premium (Step 4) | recomendado (protocolo item 4); fallback: segue sem |
| **impeccable (CLI)** | `npx impeccable --version` | refino UI (Step 4) | opcional, roda via npx quando precisar |
| **PEXELS_API_KEY (env)** | `echo $PEXELS_API_KEY` | assets-search.py videos/fotos | recomendado (protocolo item 3); **fallback que NAO precisa de chave: `--type photo` cai sozinho na Openverse e devolve FOTO REAL** (credito ao autor obrigatorio, ver `references/assets-sem-chave.md`) |
| **frontend-design (skill)** | skill listada | direcao estetica ANTES do codigo (Step 2) | recomendado (protocolo item 4); fallback: seguir so com design-taste-frontend |
| **animate (skill)** | skill listada | movimento e microinteracao (Step 4, DEPOIS da UI pronta) | recomendado (protocolo item 4); fallback: animar a mao com Framer Motion, sem sistema |
| **canvas-design (skill)** | skill listada | peca grafica ESTATICA que acompanha a pagina (PNG/PDF) | opcional: so entra se o pedido incluir arte estatica |
| **brandkit (skill)** | skill listada | criar identidade quando a marca ainda nao existe (antes do Step 2) | opcional: usar a identidade que o cliente ja tem |

**Ordem de uso das skills de design (nao inverter):** `brandkit` (identidade, se nao existir)
antes de `frontend-design` + `design-taste-frontend` (direcao estetica, Step 2), que vem antes
do codigo (Step 3), que vem antes de `animate` + `impeccable` + `high-end-visual-design`
(refino e movimento, Step 4). Animar antes de a interface estar resolvida so mascara layout ruim.

**Acao (PROTOCOLO DE INSTALACAO, na primeira ativacao com dependencia faltando):**

**NENHUMA dependencia bloqueia o inicio do trabalho.** Todas tem fallback documentado, e o
fallback e um caminho legitimo: da pra entregar pagina numa maquina limpa, sem chave nenhuma.
O que o setup completo faz e levantar o TETO do resultado (componente pronto em vez de a mao,
foto real em vez de gerada, gate de gosto automatico em vez de manual). Oferecer sempre,
nunca prender o usuario num loop de instalacao.

1. **Instalar AUTOMATICAMENTE o que nao precisa de segredo do usuario** (fazer, nao perguntar):
   - Stitch: `npm install -g stitch-mcp && claude mcp add stitch -- stitch-mcp proxy`
   - impeccable: nada a instalar (roda via `npx impeccable`)
   Executar, confirmar com o comando de deteccao e avisar o usuario do que foi instalado.
2. **Playwright: o unico que na pratica voce precisa.** A prova de entrega (screenshot lido)
   e obrigatoria nos 4 caminhos, e depende dele. Se faltar, instalar de cara:
   `npm install -g playwright && npx playwright install chromium`.
3. **Oferecer as credenciais gratuitas (21st.dev Magic e Pexels)** uma vez, com o link:
   - 21st.dev Magic: chave gratuita em https://21st.dev (usar no `claude mcp add magic` abaixo).
   - Pexels: chave gratuita em https://www.pexels.com/api/ (exportar no shell).
   Se o usuario nao quiser agora, SEGUIR pelo fallback e registrar na entrega o que rodou
   degradado. Nao repetir o pedido a cada step.
4. **Oferecer as Taste Skills (https://www.tasteskill.dev/)** e as skills `frontend-design` e
   `animate` do mesmo jeito: melhoram muito o resultado, nao bloqueiam. Sem as taste skills o
   gate anti-slop roda no scoring manual (4.0b); declarar isso na entrega.
5. **Modo nao-interativo** (sem como perguntar): executar o passo 1 automaticamente,
   usar fallbacks para o resto e INCLUIR na mensagem de entrega o bloco de instalacao
   com o que falta e o comando pronto de cada item.

**Registro honesto e obrigatorio:** o que rodou por fallback DEVE aparecer na entrega
(ex: "gate rodou em modo manual, taste skills nao instaladas"). Degradar em silencio e
que e proibido, nao degradar.

A unica coisa que NUNCA acontece e travar a sessao em loop esperando: ou instala agora,
ou o usuario dispensa por escrito, ou (nao-interativo) segue por fallback com pendencia
obrigatoria declarada.

```bash
# --- 21st.dev Magic (componentes) --- precisa de API key gratuita em https://21st.dev
claude mcp add magic --env API_KEY=<sua-chave-21st> -- npx -y @21st-dev/magic@latest

# --- Google Stitch (wireframe) --- binario global stitch-mcp
npm install -g stitch-mcp && claude mcp add stitch -- stitch-mcp proxy

# --- Taste Skills (anti-slop) --- instalar de https://www.tasteskill.dev/
#   design-taste-frontend, redesign-existing-projects, high-end-visual-design
npx skills add Leonxlnx/taste-skill

# --- Skills OFICIAIS da Anthropic (direcao estetica + arte estatica) ---
npx -y skills add anthropics/skills --skill frontend-design --agent claude-code
npx -y skills add anthropics/skills --skill canvas-design --agent claude-code

# --- animate (movimento e microinteracao em React/Next) ---
npx -y skills add https://github.com/delphi-ai/animate-skill --agent claude-code

# --- impeccable (CLI, opcional) --- nao precisa instalar, roda via npx:
npx impeccable --version

# --- Pexels (assets, opcional, gratis) --- chave em https://www.pexels.com/api/
echo 'export PEXELS_API_KEY="<sua-chave>"' >> ~/.zshrc && source ~/.zshrc
```

> Depois de `claude mcp add`, os MCPs aparecem na proxima sessao (ou apos reconectar).
> Sempre reportar ao usuario o resumo do que esta conectado vs o que falta antes de avancar.

### 1. Carregar contexto do projeto
verificar se existe arquivo em `references/projects/{nome-projeto}.md`. Se existir, ler antes de qualquer codigo.

### 2. Consultar sessoes recentes
`ls references/sessions/` e ler a mais recente do mesmo projeto se houver.

### 3. Continuar de onde parou
nao reinventar padroes ja definidos; respeitar brand tokens, componentes e convencoes do projeto.

```bash
# Busca rapida ao iniciar (caminhos relativos ao diretorio da skill)
ls ./references/projects/
ls ./references/sessions/
```

---

## GATE DE QUALIDADE: EXECUTAR ANTES DE ENTREGAR

**(Checklist AUXILIAR de build: ajuda a chegar limpo na wave. O PORTAO de entrega e a wave de auditoria do Step 4, unica autoridade final.)**

**OBRIGATORIO antes de declarar qualquer pagina pronta:**

1. **Ler `references/design-laws.md`**: verificar que nenhum ban absoluto foi aplicado sem ser solicitado explicitamente
2. **Rodar taste-gate** (`references/taste-gate.md`): score em 6 dimensoes Design
3. **Regra de entrega:**
   - Score medio >= 4.0 → entregar
   - Score 3.0-3.9 → corrigir o item de maior impacto antes de entregar
   - Score < 3.0 → revisar hierarquia e espacamento (maior alavancagem), depois re-scorar
4. **AI Slop Test final:** "Isso parece gerado por IA?" + "Tem algum detalhe que so alguem com gosto colocaria?"
5. **Rodar anti-vibe-coding checklist** (`references/anti-vibe-coding.md`): 5 sinais de substancia + **15 tells VISUAIS de IA** (secao "Tells VISUAIS de IA"). FALHA em footer legal ou checkout funcional **bloqueia a entrega**.
6. **Rodar a Taste Skill SE instalada** (anti-slop, tasteskill.dev): acionar a skill `design-taste-frontend` sobre a pagina pronta como enforcement anti-slop. Em CLONE/redesign, usar `redesign-existing-projects` (audit-first) ANTES, no Step 2. Pra acabamento premium, `high-end-visual-design`. Se nenhuma estiver instalada: o scoring manual do item 2 (taste-gate) cobre.
7. **Refinamento profundo** (opcional): `npx impeccable detect <url>` (auditoria), `npx impeccable polish/critique` (refino).
8. **Gate de VIDEO**: `node scripts/gate-video.mjs --url <url> --publico ./public` (so se a pagina tiver video). Sobe sozinho o Chromium do Playwright: **nao precisa de Edge nem de CDP no ar** (quem ja tiver um navegador com CDP pode reaproveitar com `--cdp http://localhost:9333`). Exige `ffmpeg`/`ffprobe` no PATH. Sete checagens, todas nascidas de defeito medido numa pagina de lancamento em producao:
   proporcao unica por trilha, escala do arquivo contra a caixa, corte do `cover`, poster com hash proprio respondendo 200, **extrair 6 frames e OLHAR** (texto cortado, nome de cliente, credencial), `preload` no poster se o video estiver acima da dobra, e `prefers-reduced-motion` deixando so o poster.
   FALHA em poster 404 ou em conteudo indevido no quadro **bloqueia a entrega**.

---

## PROTOCOLO POS-SESSAO: EXECUTAR SEMPRE AO CONCLUIR

**OBRIGATORIO ao finalizar qualquer sessao de sucesso:**

### 1. Salvar contexto da sessao

Criar arquivo em `references/sessions/YYYY-MM-DD-{projeto}.md` com:

```markdown
# Sessao: {Nome do Projeto}

**Data:** YYYY-MM-DD
**Projeto:** {nome-pasta-ou-repo}
**Status:** Concluido / Em andamento

## O que foi pedido
- item 1
- item 2

## O que foi entregue
- descricao objetiva de cada entrega

## Aprendizados e Padroes Novos
### {Titulo do aprendizado}
**Causa/Contexto:** ...
**Solucao/Padrao:** ...
**Regra nova (se houver):** ...

## Arquivos alterados
- `caminho/arquivo.tsx`: descricao da mudanca

## Referencia do projeto
Ver: `references/projects/{nome-projeto}.md`
```

### 2. Atualizar (ou criar) o arquivo do projeto

Se o projeto ja tem `references/projects/{nome}.md`, atualizar com:
- Novos componentes criados
- Novos padroes de animacao usados
- Bugs encontrados e corrigidos
- Checklist de pendencias atualizado
- Qualquer mudanca nos brand tokens

Se o projeto NAO tem arquivo ainda, criar com a estrutura completa (ver `references/projects/EXAMPLE.md` como template).

### 3. Atualizar a skill se surgiu algo novo

Se a sessao revelou um **anti-pattern novo**, **tecnica nova** ou **correcao de regra existente**:
- Adicionar ao arquivo correspondente em `references/` (ex: `animacoes-avancadas.md`, `visual-excellence.md`)
- Ou adicionar na secao `## Anti-Patterns` do SKILL.md
- Nunca deixar um aprendizado so na cabeca: registrar sempre.

### PROIBIDO entregar e nao registrar

Cada sessao concluida sem registro e conhecimento perdido. O protocolo leva menos de 5 minutos e evita retrabalho em todas as sessoes futuras.

---

---


## Indice: o que fica aqui vs o que carregar sob demanda

Neste arquivo (ver MAPA DESTE ARQUIVO, no topo): runbook, os 4 caminhos, porta unica das skills de design, protocolo de ativacao com pre-requisitos, gate de qualidade auxiliar, protocolo pos-sessao, regras inegociaveis, anti-patterns, os 5 gates, Steps 0 a 5 (com briefing 0.0, movimento 3.2b, identidade 4.2b e passe de gosto 4.2c), wave de auditoria, regras de deploy, blueprints, links e galerias.

**Este e o UNICO catalogo de `references/` do arquivo.** Se voce procurou uma lista de referencias no fim, ela nao existe mais: estava duplicada e foi apagada.

**Scripts da skill (ficam em `scripts/`, nao em `references/`):**

| Script | Para que |
|---|---|
| `scripts/screenshot-prova.js` | prova de entrega (desktop + mobile + clique) e **checagem de identidade da pagina** (4.2b). `--check` confere o Playwright, `--sem-identidade` so pra baseline de pagina de terceiro |
| `scripts/gate-video.mjs` | as 7 checagens de video executaveis (razao por trilha, escala, corte, poster, frames, LCP, reduced-motion). Sobe o Chromium do Playwright sozinho |
| `scripts/extrai-identidade.mjs` | extrai paleta real, vars CSS, h1/CTA e imagens de uma URL (caminho CLONAR) |
| `scripts/search.py` + `data/` | banco de design: 50 estilos, 21 paletas, 50 font pairings, guidelines UX (keywords em INGLES) |
| `scripts/assets-search.py` | fotos e videos (Pexels com chave, Openverse sem chave) |
| `scripts/higgsfield.py` | cliente da API Higgsfield: `--dry-run` monta a requisicao sem gastar credito, `--lote` gera a pagina inteira de uma vez (credito nao faz rollover), grava manifesto com seed e poster com hash proprio |
| `scripts/github-search.py` | referencias de template no GitHub (Step 0.5) |
| `scripts/servidor-gzip.py` | servir o build local COM compressao (medir sem gzip inverte o resultado) |

Carregar da pasta `references/` APENAS quando o caso pedir:

| Arquivo | Quando carregar |
|---------|-----------------|
| `references/mcp-workflow.md` | Workflow detalhado 21st.dev Magic + Google Stitch (prompts, exemplos, regras de uso) |
| `references/github-assets-search.md` | Busca de templates no GitHub e assets visuais (comandos completos, presets, setup Pexels) |
| `references/assets-sem-chave.md` | Assets SEM nenhuma API key: Openverse (foto real com licenca CC), undraw, picsum, e como creditar o autor corretamente |
| `references/workflow-otimizacao.md` | Otimizar/upgrade de pagina existente (auditoria por severidade, upgrades por camada) |
| `references/workflow-pdf.md` | Clonar pagina a partir de PDF (mapeamento visual, paleta, implementacao fiel) |
| `references/design-system.md` | Principios de design, escala tipografica, cores semanticas, gradientes, UX Nielsen |
| `references/shadcn-setup.md` | Setup e componentes shadcn/ui + CSS variables (stack React/Next) |
| `references/tailwind-patterns.md` | Padroes Tailwind: breakpoints, layouts, dark mode, v4.1 CSS-first |
| `references/magicui-quickstart.md` | Magic UI: componentes e exemplos rapidos (stack React) |
| `references/animacoes-epicas.md` | Scroll reveal, stagger, blur reveal, split text, spotlight, parallax, CSS-only |
| `references/landing-design.md` | Formulas above-the-fold, headlines, ordem de secoes, CTAs, mobile, performance |
| `references/estruturas-alto-impacto.md` | Templates prontos: heros, titulos, botoes, mockups, dividers, features, stats, testimonials |
| `references/glassmorphism.md` | Glass cards: base, variantes e quando NAO usar |
| `references/acessibilidade.md` | WCAG 2.1 AA: contraste, focus, screen readers, movimento |
| `references/checklist-pre-entrega.md` | Checklist auxiliar de build (a wave do Step 4 e o portao; isto ajuda a chegar limpo nela) |
| `references/background-video.md` | Sistema de camadas de video de fundo (z-index, isolation, overlays) |
| `references/google-workspace.md` | Google Docs/Sheets/Drive (requer scripts locais NAO inclusos no repo) |

### Referencias especializadas (auditoria e qualidade)
- `references/audit-agents.md`: wave adversarial de 7 lentes + sintese (Step 4)
- `references/scoring-system.md`: rubrica 0-10 por dimensao
- `references/strategist-audit.md`: auditoria Hook/Story/Offer
- `references/anti-vibe-coding.md`: 5 sinais de substancia + 15 tells VISUAIS de IA
- `references/taste-gate.md` e `references/design-laws.md`: gosto e bans absolutos
- `references/page-types.md`: decision tree de classificacao da pagina
- `references/psychological-triggers.md`, `cta-placement-map.md`, `social-proof-hierarchy.md`, `urgency-scarcity-patterns.md`, `trust-signals-placement.md`
- `references/typography-scale.md`, `section-transitions.md`, `animation-audit.md`, `desktop-layout-rules.md`, `mobile-checklist-detailed.md`
- `references/visual-assets.md`, `visual-excellence.md`, `visual-references.md`, `efeitos-avancados.md`, `animacoes-avancadas.md`, `magicui-components.md`
- `references/nanobanana-mockup-carousel.md`, `veo-video-workflow.md`, `ai-video-generation.md`, `pdf-to-page.md`, `post-launch.md`
- `references/higgsfield.md`: SETUP da CLI (conta, login, skills, `workspace set`), rota Higgsfield pra movimento e b-roll (Step 3.2b), as 5 regras de video em pagina e as licoes de composicao medidas (conta do veu, contraste de texto sobre video, cartao opaco escondendo o clipe)
- `references/ui-reference.md`, `official-ui-reference.md`, `reference.md`, `learn.md`, `chart.md`: shadcn/Tailwind (stack React/Next)



## Processo de 6 Steps: Workflow Principal

**ESTE E O WORKFLOW DO CAMINHO 1 (CRIAR do zero).** Para CLONAR, MELHORAR ou EDITAR, ver "OS 4 CAMINHOS": os fluxos sao outros e os gates mudam. No caminho CRIAR, os 6 steps sao sequenciais e nenhum pode ser pulado. Copy vem antes de design. Design vem antes de codigo.

Tempo estimado: 80-120 minutos do material ate pagina live.

**Constraint global:** Velocidade (LCP < 2.5s) governa TODA decisao desde o Step 0. Nao e um item de checklist, e um filtro permanente. Se uma animacao, imagem ou feature compromete o LCP, ela SAI.

---

### PROTOCOLO DE EXECUCAO OBRIGATORIO: PARADA FORCADA ENTRE STEPS

**CADA STEP TERMINA COM UMA PARADA. EU NAO AVANÇO SEM CONFIRMACAO DO USUARIO.**

**Escopo desta regra:** ela so vale nos caminhos CRIAR, CLONAR e MELHORAR. No caminho EDITAR (mudanca pontual) NAO existe parada entre steps: executa o escopo travado, testa regressao, publica e mostra a prova. Ver "OS 4 CAMINHOS".

Nao importa a urgencia, nao importa o tamanho do material, nao importa que o proximo step seja "obvio". Cada step e uma resposta separada. O usuario le, aprova ou corrige, e SO ENTAO o proximo step comeca.

**EXCECAO (unica): execucao nao-interativa.** Se a sessao nao permite confirmacao do usuario (subagente, wave, automacao agendada) OU o usuario pediu explicitamente execucao direta ("faz direto", "sem parar", "de ponta a ponta"), NAO parar entre steps. Nesse modo: executar cada GATE normalmente, registrar o output completo de cada step na resposta final (blueprint, copy lock, direcao visual, scores) e listar as decisoes que o usuario deveria ter aprovado, para revisao a posteriori. A excecao dispensa a PARADA, nunca o GATE.

```
FORMATO OBRIGATORIO ao final de cada step:

---
## [OK] Step X concluido: [NOME DO STEP]

[OUTPUT COMPLETO DO STEP, blueprint / direcao visual / checklist / etc]

GATE X:
- [x] item 1
- [x] item 2
- [x] item N

**Posso avançar para o Step Y (NOME)?** Confirme ou me diga o que ajustar.
---
```

> A ENTREVISTA DE BRIEFING (rodada 1 para todos, rodada 2 so para quem ja tem cliente) nao mora
> aqui: ela e a primeira coisa do Step 0, na subsecao **0.0 BRIEFING**. Esta secao trata so de
> quando parar entre steps.

**PROIBIDO** executar Step 1 na mesma resposta que Step 0.
**PROIBIDO** executar Step 2 na mesma resposta que Step 1.
**PROIBIDO** executar Step 3 na mesma resposta que Step 2.
**PROIBIDO** executar qualquer step sem ter apresentado o output do step anterior E recebido confirmacao do usuario.
**PROIBIDO** escrever codigo (Step 3) sem ter a copy travada (Step 1 concluido).
**PROIBIDO** fazer direcao visual (Step 2) sem ter a copy aprovada (Step 1 concluido).

Se o output do step nao foi escrito na resposta + pergunta de confirmacao nao foi feita → o step NAO foi executado.

### ROTA EXPRESSA (capture simples e paginas triviais)

Para capture page simples (< 3 telas, formulario + headline) ou pagina explicitamente trivial/descartavel, o processo colapsa SEM perder os gates:

1. **Steps 0-2 em UMA resposta:** blueprint + copy lock + direcao visual apresentados juntos, com os 3 gates checados inline (uma unica parada de confirmacao, ou nenhuma no modo nao-interativo).
2. **Step 3 normal** (as regras inegociaveis continuam valendo).
3. **Step 4 com wave reduzida a 3 lentes:** `design-critic`, `cro-auditor`, `mobile-auditor` + sweeps de QA (contato, travessao, emoji, dado inventado). O bloco de veredito na entrega continua OBRIGATORIO.

O que a rota expressa NAO dispensa: **as seis respostas da rodada 1 do briefing (0.0: nicho, local, publico, oferta, preco, acao)**, copy antes de codigo, identidade real quando indicada, assets criticos confirmados (incluindo o destino do lead), identidade da pagina (4.2b), passe de gosto (4.2c) e o BLOCO OBRIGATORIO DA ENTREGA completo. O que ela colapsa e a APRESENTACAO dos steps, nunca a entrevista nem os gates.

### REGRAS INEGOCIAVEIS: LER ANTES DE QUALQUER PAGINA

**PROIBIDO INVENTAR ID VISUAL QUANDO HA UMA INDICADA.** Se o usuario forneceu ou apontou a identidade (pasta de assets, arquivo de logo, paleta, tipografia, link, PDF, slides, marca existente), e OBRIGATORIO usar o asset REAL: o logo oficial (extrair/baixar e usar a imagem), as cores exatas, as fontes indicadas. PROIBIDO recriar o logo em texto/SVG aproximado, chutar paleta ou trocar fonte por "parecida". Se o logo oficial ficar ilegivel no tamanho de uso, aumentar/ajustar o tamanho ou pedir uma versao, NUNCA substituir por uma invencao. Criar identidade do zero so quando NAO ha nenhuma indicada. Falha real: num projeto com ID definida o logo oficial foi trocado por um wordmark inventado, o usuario teve que cobrar.

**PROIBIDO PULAR STEPS.** Cada step tem um GATE, uma entrega obrigatoria que DEVE existir antes de avancar. Se o gate nao foi cumprido, PARE e volte. Nao importa a urgencia.

**PROIBIDO BUILDAR SEM COPY TRAVADA.** Copy (Step 1) DEVE estar escrita, aprovada e "frozen" antes de qualquer codigo ou design. Design sem copy = design que vai mudar. Codigo sem copy = retrabalho garantido. A ordem e: copy first, design second, code third.

**MCP conectado, PROIBIDO nao usar** (se ausente, fallback do Step 0): construir componente UI do zero sem consultar o 21st.dev; iniciar codigo de pagina nova sem wireframe no Stitch; usar logo de marca sem buscar no `logo_search`. Com o MCP disponivel, pular = visual inferior e retrabalho. Sem o MCP, seguir pelo fallback documentado (componente a mao, layout direto, SVG oficial/vetorial).

**PROIBIDO HTML/CSS PURO para paginas de venda, mentoria ou high-ticket.** HTML puro = pagina feia, sem animacoes, sem componentes profissionais, sem o "tcham" visual. SEMPRE usar React + Vite (ou o framework do projeto existente) para ter acesso a: Framer Motion, shadcn/ui, Magic UI, Tailwind compilado, componentes reutilizaveis. A unica excecao e capture pages simples (2-3 telas, formulario + headline).

**PROIBIDO BUILDAR SEM DIRECAO VISUAL.** Ir direto do PDF pro codigo produz paginas "funcionais mas feias". Antes de escrever a primeira linha de codigo, DEVE existir: paleta definida (10-15 vars), font pairing escolhido, layout de CADA secao desenhado, lista de assets necessarios.

**PROIBIDO ENTREGAR SEM ASSETS VISUAIS.** Paginas com SVGs genericos e fundos solidos nao impressionam. DEVE ter: textura/profundidade nos fundos, foto/mockup/video real, animacoes de scroll, efeitos de hover, pelo menos 1 elemento "wow" por scroll. **Catalogo de "wow" PERMITIDO** (nao dispara os tells de IA): foto real tratada, mockup de produto, video de fundo bem integrado, number ticker, marquee de logos/depoimentos, parallax sutil, noise/pattern discreto, transicao de secao trabalhada, micro-interacao no CTA. **PROIBIDO usar como "wow":** blob de glow desfocado, aurora atras de conteudo, glow colorido em botao, glassmorphism generalizado, floating orbs, gradient-clip em titulo, shimmer decorativo: estes sao tells visuais de IA (V1-V15 de `references/anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Se o usuario nao forneceu foto e nao ha API de stock/geracao disponivel: usar monograma/ilustracao funcional, REGISTRAR como pendencia na entrega e pedir o asset real; isso nao bloqueia a entrega, bloqueia RODAR TRAFEGO. **Antes de cair nisso, use a rota sem chave:** `python3 scripts/assets-search.py "<tema em ingles>" --type photo` devolve foto real da Openverse sem nenhuma API key (credito obrigatorio). Retangulo vazio no hero nao e mais aceitavel.

### ANTI-PATTERNS DE PROCESSO E DE IA: O QUE DEU ERRADO E NUNCA PODE REPETIR

> Esta lista e a de PROCESSO e cara de IA. A lista de CODIGO e CSS esta na secao
> "Anti-Patterns de codigo (NUNCA FACA)", perto do fim do arquivo. Sao duas, e as duas valem.

| Anti-Pattern | O que acontece | Solucao |
|-------------|---------------|---------|
| Pular Step 1 (COPY & MENSAGEM) | Copy generica, design que nao casa com a mensagem, retrabalho garantido | SEMPRE escrever e aprovar copy ANTES de qualquer design ou codigo |
| Design sem copy travada | Copy muda → design muda → codigo muda → 3x o trabalho | Copy Lock obrigatorio: copy frozen antes de avancar |
| Pular Step 2 (DIRECIONAR) | Pagina sem identidade visual, cores aleatorias, sem ritmo | SEMPRE definir tokens + layout por secao ANTES de codar |
| HTML/CSS puro em pagina high-ticket | Sem animacoes, sem componentes, parece template gratis | SEMPRE React + Vite + Framer Motion + shadcn/ui |
| SVGs basicos como "design" | Pagina parece prototipo, nao produto final | Hugeicons como primario em landing (Lucide so pra UI/dashboard). PROIBIDO o par "caixinha arredondada com fundo tingido + glifo abstrato": e o tell numero 1 do passe de gosto (4.2c) |
| Fundos solidos sem textura | Visual flat e sem profundidade | Adicionar noise, gradientes sutis, patterns, overlays |
| Zero animacoes de scroll | Pagina estatica e sem vida | Scroll reveal nas secoes-CHAVE: 2 a 4 por pagina, no maximo 1 por secao. Em TODO elemento e vibe-coding e reprova na wave |
| Nao criar assets visuais | Secoes vazias, sem impacto | Buscar/gerar fotos, videos, mockups, ilustracoes DURANTE o build |
| Formato carta no desktop | Parece documento Word, nao pagina de venda | NUNCA coluna unica centralizada em high-ticket (ver desktop-layout-rules.md) |
| Clonar e inventar identidade nova | Cliente quer a marca dele; paleta/logo inventados = retrabalho garantido | Ao CLONAR site real: manter identidade original. Extrair cores exatas via `getComputedStyle` no navegador, baixar o LOGO REAL do site (nunca recriar). Só reinventar se pedido explicito |
| Foto de produto (fundo branco) sobre superficie escura/colorida | Vira "caixa branca" recortada = cara de IA na hora | Foto com fundo branco SÓ em card/superficie branca ou clara (encaixa invisivel). Em dark, precisa de remocao de fundo real, nunca colar por cima |
| Tells visuais de IA (mono kicker, "01" gigante, blob glow, stats no hero, preco mono, ENTER na busca) | "Cara de vibecoding/template SaaS" | Rodar o checklist `anti-vibe-coding.md` secao "Tells VISUAIS de IA" ANTES de entregar. Referencia de bonito = concorrente do nicho, nao Dribbble |
| Conectar 21st.dev / Stitch e nao usar | Burla a regra "PROIBIDO componente sem 21st" so registrando o MCP | Usar de fato: 21st builder/inspiration por componente; Stitch as vezes so devolve design system (tela trava): nesse caso documentar e usar os tokens |
| Tratar e-commerce/varejo home como sales page | Copy lock, oferta, value stack, checkout, video por secao nao se aplicam a vitrine de loja | E-commerce home = identidade real + cards com estrelas/avaliacao + nav por categoria/genero + grid de marcas + cupom 1a compra + trust strip. Pular Steps de copy/oferta de high-ticket |
| Framer `whileInView` + `once:true` travando em opacity 0 | Secao inteira fica INVISIVEL se o observer nao dispara | Usar `useInView` + fallback `setTimeout(()=>setForced(true), 1400)` que forca visivel. Nunca deixar opacity 0 final sem garantia |

### GATES OBRIGATORIOS ENTRE STEPS

**Estes gates sao do caminho CRIAR.** Os outros caminhos tem gate proprio, descrito em
"OS 4 CAMINHOS": CLONAR troca os gates 1 e 2 pelo **gate de fidelidade** (original e clone lado
a lado) e fecha no GATE 4 normal; MELHORAR fecha no GATE 4 **mais** o **gate de melhoria**
(antes e depois com nota por dimensao, e nenhuma dimensao pode ter piorado), que e um gate
ADICIONAL de nao-regressao, nao um substituto; EDITAR fecha no **checklist de regressao + prova
do ponto alterado**, e so ele dispensa a wave. Exigir COPY LOCK num clone ou wave de 7 lentes numa troca de headline nao e
rigor, e processo errado: o gate tem que caber no que foi pedido.

```
STEP 0 (ENTENDER & INVENTARIAR) ────────────────────────────
  GATE 0: checar-ferramentas.py rodado (critico respondendo ou correcao conduzida) + As SEIS respostas da rodada 1 (0.0) registradas, cada uma marcada como resposta do
          usuario ou SUPOSICAO + classificacao + mapa de secoes + flags de copy + inventario
          de assets documentados?
  [ ] SIM → avanca pro Step 1
  [ ] NAO → PARA. Completa o Step 0 primeiro.

STEP 1 (COPY & MENSAGEM) ───────────────────────────────────
  GATE 1: VoC minerado + Before/After Grid + hierarquia de mensagens + copy de CADA secao escrita + COPY LOCK declarado?
  [ ] SIM → avanca pro Step 2
  [ ] NAO → PARA. NENHUM design sem copy aprovada. Nunca.

STEP 2 (DIRECIONAR) ────────────────────────────────────────
  GATE 2: Paleta CSS + font pairing + layout de CADA secao + lista de assets definidos?
  [ ] SIM → avanca pro Step 3
  [ ] NAO → PARA. Nao escreva uma linha de codigo sem direcao visual.

STEP 3 (BUILDAR) ───────────────────────────────────────────
  GATE 3: Todas secoes construidas com assets reais + animacoes + layout desktop rico +
          decisao de MOVIMENTO declarada (quais blocos ganharam movimento e por que os
          outros nao ganharam, ver 3.2b)?
  [ ] SIM → avanca pro Step 4
  [ ] NAO → PARA. Volte e complete o que falta. Pagina incompleta = pagina feia.

STEP 4 (VERIFICAR & SHIPAR) ────────────────────────────────
  GATE 4: Auditoria Designer (media ≥8.0, sem notas <7) + Auditoria Estrategista (media ≥8.0,
          sem notas <7) + QA checklist 100% (Lighthouse 90+ quando houver navegador; sem ele,
          pendencia declarada) + consistencia de contato conferida digito por digito + diff de
          claims feito + IDENTIDADE DA PAGINA (4.2b, conferida pelo script) + PASSE DE GOSTO
          rodado (4.2c) + deploy funcionando (ou, na entrega SEM deploy, servidor local com o
          deploy declarado como pendencia) + PROVA DE ENTREGA 4.5 (screenshots desktop/mobile
          LIDOS + interacao principal testada)?
  [ ] SIM → avanca pro Step 5 (monitoramento)
  [ ] NAO → PARA. Corrige antes de entregar. Sem excecoes. Verificacao quebrada = entrega bloqueada, nunca "entrego sem prova".
```

### DECISAO DE TECH STACK (Obrigatoria no Step 1)

| Tipo de pagina | Tech Stack | Justificativa |
|---------------|-----------|---------------|
| Sales page (mid/high-ticket) | React + Vite + Framer Motion + shadcn/ui + Tailwind | Precisa de animacoes, componentes ricos, visual premium |
| Challenge / Desafio | React + Vite + Framer Motion + Magic UI + Tailwind | Precisa de energia visual, countdowns, efeitos |
| Capture page simples (< 3 telas) | HTML + Tailwind compilado | Simples o suficiente, velocidade maxima |
| Pagina institucional | React + Vite + Framer Motion + shadcn/ui | Profissionalismo visual obrigatorio |
| Rota em projeto existente (ex: EA) | Mesmo framework do projeto (React/Vite) | Consistencia, reuso de componentes |

**Se o projeto destino JA usa React, a nova pagina DEVE ser uma rota React, nao um HTML avulso.**

---

## Step 0: ENTENDER & INVENTARIAR (5-10 min)

Recebe o material do usuario e extrai tudo que precisa ANTES de tocar em copy, design ou codigo.

### 0.0-PRE FERRAMENTAS: rodar o verificador ANTES de qualquer coisa

```bash
python3 <dir-da-skill>/scripts/checar-ferramentas.py
```

**Este e o primeiro comando da skill, antes ate da entrevista de briefing.** Ele nao pergunta se
a ferramenta esta configurada: ele MANDA cada uma fazer alguma coisa e confere se voltou. Sai
com codigo diferente de zero quando falta critico.

**Por que existe (26/08/2026, custou meses sem ninguem perceber):** o MCP do 21st.dev estava
configurado e MORTO havia tempo indeterminado (`Not authenticated: your API key is missing or
was reset`). A skill mandava "buildar com componentes do 21st.dev OU a mao", o MCP nunca
respondia, e ela caia no "a mao" TODA VEZ. O Stitch estava no mesmo estado (proxy de pe, tools
com timeout), entao as DUAS camadas visuais da skill estavam desligadas. O dono percebeu pelo
RESULTADO ("o design nao ta interessante, pouca coisa e usada do 21st.dev"), nao por erro
nenhum, porque **fallback silencioso nao reclama**.

A deteccao antiga era "a tool `mcp__magic__*` aparece na lista?". Aparecia. E estava morta.
**Estar na lista nao e verificacao.** Verificacao e mandar fazer e conferir o retorno.

**O que fazer com o resultado:**

| Resultado | Acao |
|---|---|
| Tudo respondendo | Segue pro 0.0 (entrevista de briefing) |
| **Critico sem responder** | **PARA.** Conduza a pessoa pela correcao (abaixo). Nao comece a pagina. |
| So opcional degradado | Segue, e DECLARE a degradacao na entrega |

**CONDUZIR, nao avisar.** Quando faltar algo, nao diga "voce precisa configurar o 21st.dev":
abra a pagina, de o comando pronto e espere a chave. A pessoa que esta usando a skill quase
sempre nao sabe o que e um MCP.

| Ferramenta | Como conduzir |
|---|---|
| **21st.dev (magic)** | Abra `https://21st.dev/mcp`, peca a chave, e rode: `claude mcp remove magic` e depois `claude mcp add magic -- npx -y @21st-dev/magic@latest --api-key <CHAVE>`. Avise que as tools novas so aparecem na proxima sessao. |
| **Playwright** | `npm i -g playwright && npx playwright install chromium` (baixa ~265 MB; a versao leve e `--only-shell`, ~94 MB) |
| **Higgsfield** | Setup completo em `references/higgsfield.md`, secao SETUP (inclui o `workspace set`, que trava todo mundo) |
| **Stitch** | Proxy local. Timeout costuma ser conflito de porta: confira quem esta na porta antes de reiniciar |
| **ffmpeg** | `brew install ffmpeg` |

**Regra que nasceu daqui, e vale pra qualquer ferramenta que a skill venha a usar:** toda
dependencia nova precisa entrar no `checar-ferramentas.py` com um teste que a EXERCITA. Se voce
nao conseguir escrever esse teste, a dependencia nao entra na skill: sem teste, ela vai morrer
em silencio e degradar o resultado sem avisar ninguem.

---

### 0.0 BRIEFING: entrevista de 2 rodadas (logo depois do verificador de ferramentas)

**Desvio:** se o usuario ja chegou com doc, PDF, briefing fechado ou copy pronta, NAO abra a
entrevista inteira. Va para o 0.1, leia o material e use a entrevista so para o que ficou em
branco (tipicamente preco, destino do lead e acao esperada).

**EXTRAIA o basico primeiro. Pergunta simples, que qualquer um responde.**

O pedido real chega assim: *"cria uma pagina pra mim de uma academia"*. So isso. NAO responda
com "qual o seu publico-alvo e qual a dor dele?": isso e vocabulario de marqueteiro, e quem tem
academia responde "todo mundo que quer emagrecer", que nao serve pra nada. E NAO pergunte sobre
cliente antigo logo de cara: muita gente ainda nao abriu o negocio e trava na primeira pergunta.

**RODADA 1, o basico. Mande as perguntas juntas, numa lista curta, pra pessoa responder de uma
vez.** Sao todas de fato, sem interpretacao. **Troque os exemplos entre parenteses pelos do
nicho do pedido**: exemplo de academia numa consultoria juridica soa automatico e desanima.

1. **Qual e o nicho, exatamente?** (academia, so musculacao, crossfit, pilates, funcional)
2. **Onde voce atende?** (cidade e bairro, ou online)
3. **Atende quem?**
   - cliente final PESSOA: mulheres, homens, os dois; e a faixa de idade, se souber
   - cliente final EMPRESA (B2B): porte, segmento e quem decide a compra (cargo). Genero e
     idade sao o eixo errado aqui e devolvem resposta inutil
4. **O que voce vende?** (plano mensal, aula avulsa, pacote fechado, avaliacao)
5. **Quanto custa, mais ou menos?**
6. **O que voce quer que a pessoa faca nessa pagina?** (agendar aula, chamar no WhatsApp,
   comprar direto, deixar o contato)

Com essas seis ja da pra escrever copy que aponta pra alguem. Nicho + cidade + genero + faixa
etaria ja e um publico; oferta + preco + acao ja e uma pagina.

**CRITERIO DE ACEITE (resposta presente nao e resposta util).** Antes de dar a rodada 1 por
respondida, conferir:
- **nicho** so vale com o que + pra quem + resolvendo o que ("consultoria" nao vale;
  "consultoria de folha de pagamento pra industria de pequeno porte" vale)
- **publico** so vale com pelo menos um atributo alem de "empresas" ou "todo mundo"
- **oferta** so vale com formato e recorrencia (mensal, avulso, pacote, projeto fechado)
- **acao** so vale com o destino nomeado (qual WhatsApp, qual formulario, qual checkout)

Reprovou em alguma? Nao mande a pergunta aberta de novo: devolva **2 ou 3 opcoes concretas** pra
pessoa escolher ("e mais pra A, B ou C?").

**RODADA 2, so SE a pessoa ja atende gente.** Pergunte: *"voce ja tem cliente hoje?"*. Se sim,
estas quatro rendem muito, porque devolvem material que nao da pra inventar:

- **"Me conta o ultimo cliente que fechou: quem era e o que trouxe ele ate voce?"** (a persona
  real, quase sempre mais especifica que a imaginada)
- **"O que ele te falou quando chegou? Se lembrar da frase, melhor."** (voz do cliente verbatim,
  vira headline. Anote com as palavras DELA, sem traduzir pro seu vocabulario)
- **"Quem procura voce e voce percebe que nao e pra voce?"** (o anti-publico afia a mira mais
  rapido que descrever o publico certo; vira a secao "para quem NAO e")
- **"O que essa pessoa ja tinha tentado antes, e por que nao deu certo?"** (devolve a objecao
  real e o diferencial, sem voce inventar nenhum dos dois)

Se a pessoa ainda NAO tem cliente, pule a rodada 2 sem drama e siga com as seis primeiras.
**Registre a flag `sem prova social` no output do Step 0**: ela viaja com o projeto e muda o
gate do Step 4 (ver 4.0b, dimensao Prova Social). Nunca transforme a entrevista em
interrogatorio: e melhor uma pagina boa com seis respostas do que nenhuma pagina porque a
pessoa cansou de responder.

**Se travar ou responder generico, NAO repita a pergunta.** Ofereca um palpite pra ela reagir:
*"Pelo que costuma acontecer em academia de bairro, e gente de 30 a 50 que ja tentou treinar
sozinha e desistiu, e o que trava e nao saber comecar sem se machucar. E por ai, ou o seu caso
e outro?"*. Gente e muito melhor em CORRIGIR do que em CRIAR do zero, e um palpite errado rende
mais que uma pergunta aberta.

**ONDE O PALPITE E PROIBIDO.** Palpite serve pra nicho, publico, dor, objecao e anti-publico:
campos de interpretacao, que a pessoa corrige em dois segundos. **NUNCA palpite preco, garantia,
numero de alunos, resultado, prazo, data ou depoimento.** Esses sao fato, e palpite aceito por
silencio vira dado inventado na pagina (proibido pelo QA 4.2, item "ZERO dado inventado"). Sem
confirmacao: deixar em branco, registrar como pendencia do usuario e NAO deixar aparecer na
pagina ate ser confirmado.

**Resposta pela metade** (respondeu 4 das 6, ignorou 2): nao reenvie a lista inteira nem repita
tudo. Devolva **so as que faltam**, numa unica mensagem curta, ja com palpite pra pessoa apenas
confirmar ou corrigir.

**Regra de parada:** so avance com as seis da rodada 1 respondidas e aprovadas no criterio de
aceite. Sem publico e oferta definidos na largada, a pagina inteira nasce apontando pra ninguem,
e o retrabalho custa a pagina toda, nao um paragrafo.

**Modo nao-interativo** (subagente, automacao, ou o usuario pediu "faz direto"): nao existe
ninguem pra responder, entao NAO trave. Preencha com palpite derivado do pedido as CINCO de
interpretacao (nicho, local, publico, oferta, acao), marque cada uma como `SUPOSICAO` no output
do Step 0 e liste na entrega as que precisam de confirmacao. **A pergunta 5 (preco) e fato e NAO
se palpita:** fica registrada como PENDENTE, a pagina sai sem numero de preco e o CTA leva pra
conversa. A excecao dispensa a PARADA, nunca o registro: seguir em silencio com suposicao e que
e proibido.

Diferenca medida em pagina real (demo de pilates, 25/08/2026): o pedido trazia nicho, publico,
faixa etaria e objetivo, e o resultado foi a headline "Pilates para quem sente dor nas costas e
nunca pisou num estudio", as tres objecoes reais na secao "isso parece com voce", e o FAQ que
ataca "tenho mais de 50 anos, ainda da tempo?". Nada disso sai de um briefing que diz so
"academia".

### 0.1 Ler o Material
- Se PDF: `Read file_path="/caminho/do/arquivo.pdf"` (todas as paginas)
- Se Google Doc / Sheet: **requisito externo, NAO vem neste repo.** Os scripts
  `~/.claude/scripts/google-api.sh` e `google-oauth-capture.py` precisam estar instalados e
  autenticados na maquina (ver `references/google-workspace.md`). Existindo:
  `bash ~/.claude/scripts/google-api.sh doc <DOC_ID>` e
  `bash ~/.claude/scripts/google-api.sh sheet <SHEET_ID> "Aba"`.
  **Nao existindo (caso da maioria das maquinas): pedir ao usuario o texto colado ou o PDF
  exportado.** Nunca ficar tentando rodar um script que nao esta instalado.
- Se texto direto: ler a mensagem do usuario

### 0.2 Classificar a Pagina
Usar a decision tree de `references/page-types.md`:

**Perguntar/detectar:**
1. **Tipo:** sales-page, capture, challenge, vsl, institutional, checkout-bridge, thank-you
2. **Faixa de preco:** free, low-ticket (R$7-97), mid-ticket (R$197-997), high-ticket (R$1.000+)
3. **Tom:** premium, urgente, educacional, pessoal, energia
4. **Temperatura:** fria (pagina longa), morna (media), quente (curta)

**Output da classificacao:**
- Se high-ticket + sales-page → layout desktop rico OBRIGATORIO (nunca formato carta)
- Se capture/vsl → formato centrado OK
- Se challenge → dark mode + energia
- Consultar `references/page-types.md` para template de secoes

### 0.3 Mapear Secoes
Listar cada secao do material:
```
SECAO 1: Hero, "Headline exata", CTA: "Texto do botao"
SECAO 2: Social Proof, 4 numeros
SECAO 3: Problema, 3 dores listadas
...
```

### 0.4 Avaliar a Copy
Nao apenas extrair, AVALIAR:
- Headlines fortes ou genericas? (Flaggar se fracas)
- CTAs claros com verbo de acao + beneficio?
- Oferta empilhada com ancoragem de preco?
- Social proof presente e especifica (numeros, nomes)?
- Copy no nivel de leitura 5a-7a serie? (simplificar se muito complexa)

### 0.5 Puxar Referencias
Buscar 3 paginas de referencia do nicho como benchmark visual:
```bash
python3 ~/.claude/skills/construtor-paginas/scripts/github-search.py "<tipo-pagina>" --stars 50
```
Ou buscar manualmente paginas de concorrentes/referencia que o usuario mencionar.

### 0.6 Contexto de Funil
Identificar:
- **De onde vem o trafego?** (Meta Ads, organico, email, WhatsApp)
- **O que vem depois?** (checkout, grupo WhatsApp, email sequence)
- **Message match:** headline da pagina deve ecoar a promessa do anuncio

### 0.7 Inventario de Conteudo

Confirmar AGORA o que existe e o que precisa ser criado/buscado:

```
ASSETS EXISTENTES:
- Logo: [ ] SIM (onde?) / [ ] NAO
- Foto do mentor/produto: [ ] SIM (onde?) / [ ] NAO
- Depoimentos com foto: [ ] SIM (quantos?) / [ ] NAO
- Video (VSL/pitch): [ ] SIM (URL?) / [ ] NAO
- Screenshots/resultados: [ ] SIM / [ ] NAO

ASSETS A CRIAR:
- Fotos: [ ] buscar Pexels / [ ] gerar IA / [ ] usuario fornece
- Icones: [ ] Lucide / [ ] Heroicons / [ ] custom SVG
- Mockups: [ ] necessario? / [ ] tipo: phone / laptop / dashboard
- Video de fundo: [ ] necessario? / [ ] buscar Pexels

DESTINO DO LEAD/VENDA (asset critico numero 1 de capture/sales):
- Form de captura: endpoint/CRM/webhook? URL: ___________
- Checkout: link Hotmart/Kiwify/Stripe? URL: ___________
- WhatsApp/grupo: numero/link? ___________

CHECKPOINT FUNIL:
- De onde vem o trafego? ___________
- O que vem depois desta pagina? ___________
- Qual a promessa do anuncio? (para message match) ___________
```

Se assets criticos estao em falta (destino do lead/checkout, foto do mentor, depoimentos, preco final) → **PAUSAR e perguntar o usuario antes de avancar** (em modo nao-interativo: seguir com placeholder EXPLICITO, ex. `data-endpoint=""` + comentario TODO, e declarar na entrega que a pagina NAO pode receber trafego ate o destino ser plugado). **PROIBIDO** entregar form que mostra sucesso sem enviar o lead SEM declarar isso em destaque na entrega.

Se o usuario NAO tem fotos e nao ha API de stock/geracao: monograma/ilustracao funcional + pendencia registrada na entrega (nao bloqueia entrega; bloqueia rodar trafego).

### Output do Step 0
Blueprint documentado com:
- **As seis respostas da rodada 1 (0.0)**, escritas na resposta, cada uma marcada como
  `resposta do usuario` ou `SUPOSICAO` (modo nao-interativo)
- **Flags do briefing:** `sem prova social` (quando a pessoa ainda nao tem cliente) e a lista
  de campos de fato que ficaram em branco (preco, garantia, numeros, datas)
- Classificacao (tipo + preco + tom + temperatura)
- Mapa de secoes
- Flags de copy (o que precisa melhorar)
- 3 URLs de referencia
- Contexto de funil
- Inventario de assets (o que existe vs o que precisa criar)

**>>> GATE 0: checar-ferramentas.py rodado (critico respondendo ou correcao conduzida) + As seis respostas da rodada 1 (0.0) registradas (resposta do usuario ou SUPOSICAO declarada) + blueprint + inventario de assets documentados por escrito? Assets criticos existem ou ha plano para obtelos? Se NAO, PARA AQUI. <<<**

**PARADA OBRIGATORIA:** Apresentar o blueprint completo ao usuario e perguntar: "Step 0 concluido. Posso avancar para o Step 1 (COPY & MENSAGEM)?", NAO AVANCAR SEM RESPOSTA.

---

## Step 1: COPY & MENSAGEM (10-20 min)

**O step mais critico do processo.** Copy define o que vai ser construido. Design serve a copy, nao o contrario. Nenhum pixel antes de copy aprovada.

### 1.0 De onde vem a copy? (decidir primeiro)

Antes de produzir qualquer copy, checar o que o usuario ja trouxe:

- **Ja chegou com a copy pronta** (texto, doc, briefing fechado): NAO gerar do zero.
  Apenas validar (checklist 1.5), organizar na hierarquia (1.3) e travar (1.6 COPY LOCK).
- **Chegou sem copy, ou com copy fraca/incompleta:** produzir a copy seguindo 1.1 a 1.4.
  Aqui, **opcionalmente**, acionar a skill `copy-pagina-vendas` (frameworks Brunson/Hormozi/
  Schwartz) para gerar a copy de venda, e o construtor transforma o resultado em pagina.
- **Caso de duvida:** perguntar ao usuario se ele tem copy ou quer que ela seja criada.

> `copy-pagina-vendas` e OPCIONAL e so entra quando NAO ha copy boa. Se o usuario ja tem a copy,
> pular direto pra validacao + COPY LOCK. Nunca reescrever copy que o usuario aprovou.

### 1.1 VoC Mining (Voice of Customer)

Identificar linguagem real dos clientes, palavras que eles usam, nao palavras que achamos que eles usam.

**Fontes de VoC (pedir ao usuario ou buscar):**
- Comentarios em posts de Meta/Instagram sobre o produto
- Reviews na Hotmart/Kiwify
- DMs e mensagens de WhatsApp de alunos
- Comentarios em YouTube do nicho
- Perguntas frequentes que chegam

**Extrair e documentar:**
```
PALAVRAS QUE USAM PARA O PROBLEMA:
- "___________"
- "___________"

PALAVRAS QUE USAM PARA O RESULTADO DESEJADO:
- "___________"
- "___________"

OBJECOES QUE APARECEM:
- "___________"
```

Se nao ha VoC disponivel → usar a copy existente do material + inferir com base no publico.

### 1.2 Before/After Grid

Define a transformacao que a pagina precisa comunicar:

```
ESTADO ANTES (o que o usuario SENTE/TEM/FAZ hoje):
- Sente: ___________
- Tem: ___________
- Faz (media dia): ___________
- Status: ___________

ESTADO DEPOIS (o que o usuario SENTE/TEM/FAZ com o produto):
- Sente: ___________
- Tem: ___________
- Faz (media dia): ___________
- Status: ___________
```

Esta grid alimenta o hero, o problem section e o CTA.

### 1.3 Hierarquia de Mensagens

Definir qual promessa fica em qual posicao:

```
PROMESSA PRINCIPAL (hero headline, 1 frase, o maior beneficio):
"___________"

PROMESSA DE SUPORTE 1 (subheadline, expande a principal):
"___________"

PROMESSA DE SUPORTE 2 (features/bullets, provas da promessa):
- ___________
- ___________

OBJECOES E CONTRA-ARGUMENTOS (posicionamento defensivo):
- Objecao: "___" → Contra: "___"
- Objecao: "___" → Contra: "___"

URGENCIA/ESCASSEZ (real, nunca inventada):
"___________"
```

### 1.4 Copy Wireframe (Secao por Secao)

Escrever o texto real de cada secao. Nao placeholders, texto REAL que vai na pagina:

```
HERO:
- H1: "___________"
- Subheadline: "___________"
- CTA button: "___________"
- Micro-copy abaixo do CTA: "___________"

SECAO 2 ([nome]):
- Titulo: "___________"
- Corpo: "___________"

SECAO 3 ([nome]):
- Titulo: "___________"
- [bullets/texto]:
  • ___________
  • ___________

[continuar para todas as secoes mapeadas no Step 0]

OFERTA (se houver):
- Headline da oferta: "___________"
- O que inclui (value stack):
  • ___________  (valor R$___)
  • ___________  (valor R$___)
- Garantia: "___________"
- Preco de: R$____ | Por: R$____
- CTA final: "___________"
```

### 1.5 Checklist de Qualidade da Copy

Antes de travar, verificar:
- [ ] Headlines passam no teste "So what?" (dizem um beneficio real, nao uma feature)
- [ ] CTAs tem verbo de acao + beneficio (ex: "Quero automatizar agora" nao "Enviar")
- [ ] Copy esta no nivel de leitura 5a-7a serie (sem jargao tecnico desnecessario)
- [ ] Promessa principal e especifica (numeros, resultados, tempo) nao generica
- [ ] Objecoes principais foram respondidas em alguma secao
- [ ] Urgencia e real (data de encerramento, vagas limitadas) nao inventada

### 1.6 COPY LOCK

Declarar formalmente:

```
=== COPY LOCK ===
Data: ___________
Versao: 1.0
Status: FROZEN, nenhuma alteracao sem aprovacao explicita do usuario

A copy acima esta travada. O Step 2 (DIRECIONAR) usara esta copy como
base imutavel. Qualquer mudanca de copy requer voltar ao Step 1.
=================
```

### Output do Step 1
- VoC mining documentado
- Before/After Grid preenchida
- Hierarquia de mensagens definida
- Copy de CADA secao escrita (texto real, sem placeholders)
- Checklist de qualidade 100% verificado
- COPY LOCK declarado

**>>> GATE 1: VoC + Before/After + Hierarquia + Copy de TODAS as secoes escrita + COPY LOCK declarado? Se NAO, PARA AQUI. Nenhum design sem copy aprovada. <<<**

**PARADA OBRIGATORIA:** Apresentar a copy completa ao usuario e perguntar: "Step 1 concluido. A copy esta aprovada? Posso avancar para o Step 2 (DIRECIONAR)?", NAO AVANCAR SEM RESPOSTA.

---

## Step 2: DIRECIONAR (5-10 min)

Define a direcao visual baseada na copy aprovada no Step 1. O design serve a copy, nunca o contrario.

### 2.0 Consultar o BANCO DE DESIGN (OBRIGATORIO, antes de inventar cor/fonte/estilo)

Antes de definir qualquer estilo, paleta ou tipografia, **consultar o banco de design**
(`data/*.csv` via `scripts/search.py`) com base no tom + tipo de pagina detectados no Step 0.
NUNCA inventar paleta/fonte do zero quando o banco tem opcao validada.

**PRECEDENCIA (quem vence):** 1º identidade REAL indicada pelo usuario (logo, paleta, fontes: regra inegociavel); 2º brand tokens de projeto existente carregados no Protocolo de Ativacao (consistencia de funil vence sugestao do banco); 3º banco de design (`search.py`). O banco e a fonte quando NAO ha identidade nem projeto anterior; nunca sobrepoe os dois primeiros.

Rodar os 3:

**IMPORTANTE: buscar com keywords em INGLES.** O banco (CSVs) e indexado em ingles; query em portugues retorna 0 resultados. Traduzir o tom/nicho antes de buscar (ex.: "mentoria dark premium" → "dark premium coaching").

```bash
SKILL=~/.claude/skills/construtor-paginas
# Estilo visual (50 estilos: cyberpunk, OLED dark, glassmorphism, brutalism, etc.)
python3 $SKILL/scripts/search.py "<tone + niche em ingles>" --domain style -n 3
# Paleta (21 paletas por tipo de produto, com primary/secondary/CTA/bg/text/border em hex)
python3 $SKILL/scripts/search.py "<product type em ingles>" --domain color -n 2
# Font pairing (50 pares, ja com CSS @import e Tailwind config prontos)
python3 $SKILL/scripts/search.py "<mood em ingles>" --domain typography -n 2
```

Tambem disponiveis: `--domain ux` (guidelines), `--domain chart` (data viz), `--domain landing`,
`--domain product`, `--domain prompt`. Use `--json` se for parsear o resultado.

Pegar do retorno: cores em hex (viram as CSS vars do 2.1), o `CSS Import` e o `Tailwind Config`
do font pairing, e os "Effects & Animation" do estilo (alimentam o Step 3).

**Depois** do banco, conferir referencias visuais reais em `references/visual-references.md`:
1. Localizar o tipo de página (sales, capture, challenge, vsl, institutional)
2. Abrir 2-3 URLs da tabela correspondente
3. Anotar: paleta dominante, font pairing, layout do hero, 1 elemento "wow"

Critério rápido por tom (norte, mas o banco manda):
- Premium escuro → Linear + Resend
- Premium claro → Lenny's + SuperHi
- Alta energia → Tony Robbins + Arnold's Pump Club
- Minimalista → Netflix + Acquisition.com
- Educacao/credibilidade → G4 Business
- Comunidade/calor → Creative South + Pactto

### 2.1 Paleta Visual (Flat: 10-15 variaveis CSS)

Preencher as CSS vars abaixo com os valores **vindos do `search.py`** (paleta + font pairing do 2.0),
ajustando ao tom. O template e a forma; os valores saem do banco de design, nao inventados.

```css
:root {
  /* Cores */
  --color-bg: #0a0a14;          /* background principal */
  --color-bg-alt: #f9fafb;      /* background alternativo (secoes claras) */
  --color-text: #ffffff;         /* texto principal */
  --color-text-muted: #9ca3af;  /* texto secundario */
  --color-accent: #f97316;      /* cor de destaque (CTAs, links) */
  --color-accent-hover: #ea580c;/* hover do accent */
  --color-border: rgba(255,255,255,0.1); /* bordas */
  --color-card-bg: rgba(255,255,255,0.05); /* fundo dos cards */

  /* Tipografia */
  --font-display: 'Poppins', sans-serif;  /* titulos */
  --font-body: 'Inter', sans-serif;       /* corpo */

  /* Spacing */
  --space-section: 80px;   /* padding entre secoes */
  --space-block: 48px;     /* gap entre blocos */
  --space-element: 24px;   /* gap entre elementos */
  --radius: 16px;          /* border-radius padrao */
}
```

Ajustar cores/fontes conforme o tom detectado no Step 0. Usar `references/efeitos-avancados.md` para dark theme ou `scripts/search.py` para outras paletas.

### 2.2 Layout por Secao

Definir o grid de cada secao usando `references/desktop-layout-rules.md`:

```
SECAO 1: Hero       → Split 60/40 (texto + foto)     | Dark BG
SECAO 2: Stats      → 4-col counter row              | Light BG
SECAO 3: Problema   → 3-col icon cards               | Dark BG
...
```

**Regras (de desktop-layout-rules.md):**
- Max 2 secoes seguidas com mesmo layout
- Hero DEVE ter visual ao lado (nunca so texto)
- Alternar backgrounds claro/escuro
- Secoes obrigatoriamente side-by-side: mentor bio, testimonials, features, garantia

### 2.3 Wireframe Rapido (Validacao)

Gerar esqueleto HTML com gray boxes:
```html
<!-- Wireframe - apenas estrutura, sem conteudo real -->
<section class="hero" style="min-height:90vh; display:grid; grid-template-columns:3fr 2fr;">
  <div>[HEADLINE + CTA]</div>
  <div style="background:#333; border-radius:12px;">[FOTO/VIDEO]</div>
</section>
<section class="stats" style="display:grid; grid-template-columns:repeat(4,1fr);">
  <div>[STAT 1]</div><div>[STAT 2]</div><div>[STAT 3]</div><div>[STAT 4]</div>
</section>
```

**Gate:** Se a estrutura nao casa com o objetivo de conversao → ajustar ANTES de buildar. Voltar ao mapa de secoes se necessario.

### 2.4 Decisao de Assets
Listar assets necessarios por secao:
- Hero: foto do mentor OU video embed OU mockup
- Features: icones SVG custom (nao genericos)
- Testimonials: fotos de alunos OU screenshots WhatsApp
- Mentor: foto profissional
- Garantia: badge/selo

### 2.5 Decisao de Tech Stack
Consultar a tabela DECISAO DE TECH STACK (acima). Definir AGORA:
- Framework: React + Vite? HTML puro? Rota no projeto existente?
- Dependencias: Framer Motion? shadcn/ui? Magic UI?
- Onde vive o codigo: novo projeto? subpasta? nova rota no SPA?

### Output do Step 2
Documento com:
- Paleta CSS completa (10-15 vars)
- Font pairing definido
- Layout de CADA secao (grid, split, cards: especificado)
- Lista de assets por secao
- Tech stack escolhido

**>>> GATE 2: Paleta + font pairing + layout de CADA secao + lista de assets + tech stack definidos por escrito? Se NAO, PARA AQUI. Nao escreva UMA LINHA de codigo sem direcao visual completa. Pagina sem direcao = pagina feia. <<<**

**PARADA OBRIGATORIA:** Apresentar a direcao visual completa ao usuario e perguntar: "Step 2 concluido. Posso avancar para o Step 3 (BUILDAR)?", NAO AVANCAR SEM RESPOSTA.

---

## Step 3: BUILDAR (30-60 min)

Construcao do codigo, secao por secao, com assets criados INLINE. A copy do Step 1 e a direcao visual do Step 2 estao travadas, apenas implementar.

### 3.1 Setup do Projeto
```bash
# Criar diretorio
mkdir -p /caminho/do/projeto/

# CSS input para Tailwind
echo '@tailwind base;@tailwind components;@tailwind utilities;' > _input.css

# Favicon: usar SEMPRE o logo/favicon do proprio projeto.
# cp /caminho/do/favicon-do-projeto.png favicon.png
```

**Setup de shadcn/ui + Tailwind (consultar quando o stack for React/Next):**
- `references/ui-reference.md`: instalar todos os componentes shadcn via CLI
- `references/official-ui-reference.md`: criar projeto (TanStack Start / Next) com shadcn
- `references/reference.md`: documentacao Tailwind CSS (utilities, config)
- `references/chart.md`: instalar e usar o componente Chart do shadcn (data viz)
- `references/learn.md`: guia de aprendizado shadcn/ui (padroes e boas praticas)

### 3.2 Construir Secao por Secao

Seguir a ordem definida no Step 1. Para cada secao:
1. Implementar o layout definido (grid split, nao formato carta)
2. Inserir a copy extraida do material
3. **Avaliar video de background para a secao** (ver protocolo e condicoes abaixo)
4. Criar/buscar demais assets visuais (imagem, icone)
5. Adicionar animacao de scroll reveal (CSS-only preferido sobre JS)
6. Testar responsividade (mobile colapsa pra single column)

**PROTOCOLO DE VIDEO DE BACKGROUND (condicional por tipo de pagina):**

Video de fundo e um diferencial FORTE, mas subordinado a constraint global de LCP e ao tipo de pagina:

| Tipo de pagina | Video de background |
|---------------|---------------------|
| Sales page / Challenge (mid/high-ticket) | Hero OBRIGATORIO + secoes-chave (1 a 3 videos por pagina) |
| Institucional | Hero recomendado |
| Capture simples / thank-you | NAO usar (velocidade maxima; textura/pattern no lugar) |
| E-commerce home | NAO usar (identidade real + fotos de produto) |

Regras quando usar: se compromete LCP < 2.5s, SAI (constraint global vence). Fontes, nesta ordem: material real do cliente, Pexels (`PEXELS_API_KEY`), Veo, Higgsfield (ver 3.2b). Sem nenhuma, fallback: gradiente + noise/pattern + foto tratada, e registrar na entrega que o video ficou pendente.

- **Buscar primeiro:** `assets-search.py "descricao-da-secao" --type video`: buscar videos stock que combinem com o tema
- **Se nao encontrar stock adequado:** gerar com Veo 2 → ver `references/veo-video-workflow.md`, ou Higgsfield → `references/higgsfield.md`
- **Implementar** o video como background absoluto da secao com overlay:
  - Secoes escuras: video `object-cover` + overlay escuro (gradiente/`bg-black/60`)
  - Secoes claras: video `object-cover` + veu claro proprio (nunca baixar a opacidade do video)
- **O VEU EXISTE PRA O TEXTO FICAR LEGIVEL, NAO PRA ESCONDER O VIDEO.** Calcule antes de aceitar:
  `visivel = opacidade_video x (1 - alpha_veu)`. **Abaixo de 15% de visibilidade o video e enfeite
  invisivel: ou aumenta, ou tira e economiza o credito.** Faixa medida que funcionou em pagina
  real (25/08/2026): video a 100% e veu entre 72% e 48% (mais forte atras do titulo, mais fraco
  embaixo). Texto sobre video exige MEDIR contraste (minimo 4.5:1) contra as partes ESCURAS do
  clipe: se nao bate, a saida e composicao (texto numa coluna, video numa janela ao lado), nao
  aumentar o veu. Licoes completas em `references/higgsfield.md`.
- **Otimizar:** `ffmpeg -i input.mp4 -c:v libx264 -crf 28 -vf scale=1280:-2 -an output.mp4`
- **Mobile:** esconder videos no mobile (performance) com `hidden md:block` + `preload="none"`

**Criar demais assets INLINE** (nao como step separado):
- **Imagens de app/produto:** gerar com Nanobanana (Gemini) → WebP → mockup iPhone15Pro ou Safari (ver `references/nanobanana-mockup-carousel.md`)
- Imagens gerais: buscar com `assets-search.py` ou gerar descricao para IA
- **Icones:** Hugeicons como primario (46k+ icones, 10 estilos) para landing pages. Lucide para UI/dashboards simples. NUNCA genericos/simples, e NUNCA "quadradinho arredondado com fundo tingido + glifo abstrato" (o tell numero 1 do passe de gosto 4.2c)
- Videos stock: `assets-search.py "descricao" --type video`

**Efeitos avancados, consultar SEMPRE antes de entregar:**
- Ver `references/efeitos-avancados.md` para: 3D Card Tilt, Text Scramble, Magnetic Cursor, Gradient Border animado, Noise Texture, SVG Blob Morphing, Confetti, CSS Scroll-Timeline, Parallax Multicamada, Counter Animado, etc.
- **BANIDOS do catalogo (reprovam na wave, sao tells V1-V15):** Aurora Background, Floating Orbs, SVG Blob de glow, Glassmorphism generalizado, glow colorido em botao, gradient-clip em titulo. Estao no arquivo de referencia, mas NAO podem ser usados como "wow" nesta skill.
- Regra: minimo 2 efeitos por pagina (1 de fundo + 1 de interacao). Maximo 2 por secao.
- CTA principal DEVE ter micro-interacao: mudanca de tom no hover + elevacao sutil. Confetti ou magnetic so QUANDO o tom da pagina pede (igual ao 3.6), nunca por padrao.

**Mockup Carousel (produto digital/SaaS):**
- Gerar screenshots com Nanobanana → iPhone15Pro + MockupCarousel → seção side-by-side
- Ver workflow completo em `references/nanobanana-mockup-carousel.md`

### 3.2b MOVIMENTO NOS BLOCOS: o Higgsfield e passo ESPERADO, nao enfeite

Pagina inteira parada, com bloco de texto e icone, entrega menos do que merece. **Neste step,
pergunte SEMPRE quais blocos ganham movimento** e trate isso como parte do build, nao como
sobremesa. Os candidatos tipicos sao os blocos que hoje so tem texto:
- lista de beneficios ou "o que muda", que costuma ser 3 ou 4 cards de texto com icone
- passo a passo do processo
- fundo de secao intermediaria, pra quebrar a monotonia entre dobras

Ordem de preferencia (nao muda): **material real do cliente → gravacao de tela → Higgsfield**.
Cena generica de IA se reconhece; imagem real do negocio ganha dela sempre que existir.

**Sem conta Higgsfield:** siga, declare a pendencia na entrega ("os blocos X e Y foram
entregues estaticos: exigem conta Higgsfield") e ofereca as rotas que nao pedem conta paga
(animacao CSS/Framer Motion no proprio bloco, ou b-roll do acervo aberto). Falta de conta
degrada o resultado, nao bloqueia a entrega.

**Aluno sem conta nem CLI?** O setup inteiro esta em `references/higgsfield.md`, na secao
SETUP: criar conta (**plano pago para uso comercial**), `npm i -g @higgsfield/cli`,
`higgsfield auth login`, `npx skills add higgsfield-ai/skills` e, o passo que trava todo mundo
e nao aparece em tutorial nenhum, `higgsfield workspace set <id>` (sem workspace selecionado,
qualquer comando responde "No workspace selected"). Verificacao: `higgsfield account status`
imprime e-mail, plano e creditos. Conduza a pessoa por eles em vez de so avisar que falta conta.

As 5 regras de video em pagina (proporcao unica decidida antes, gerar no tamanho da caixa x2,
seed anotado, poster com hash proprio, video do heroi e o LCP) estao em
`references/higgsfield.md` e valem pra QUALQUER rota de video, inclusive a do Replicate.

### 3.3 Checklist Brazil (integrado no build)

Durante a construcao, incluir:
- [ ] GTM head + body tags (se o projeto/cliente fornecer um container)
- [ ] Link de checkout nos CTAs (Hotmart/Kiwify/Stripe/etc, conforme o projeto)
- [ ] Meta Pixel / tracking (se aplicavel)
- [ ] Favicon do proprio projeto (`<link rel="icon" type="image/png" href="favicon.png" />`)
- [ ] Light mode para vendas / dark mode para desafio; capture herda a identidade do projeto/funil (sem identidade: escolher pelo tom do Step 0)
- [ ] `data-cfasync="false"` no script principal (Cloudflare Rocket Loader)

### 3.4 Speed como Constraint

Durante todo o build:
- [ ] TODAS imagens em WebP (`cwebp -q 82`)
- [ ] `width` + `height` em TODA imagem (evita CLS)
- [ ] `loading="lazy"` abaixo do fold
- [ ] `fetchpriority="high"` na hero image
- [ ] CSS animations > JS animations (quando possivel)
- [ ] Tailwind compilado (NUNCA cdn.tailwindcss.com)
- [ ] `preconnect` para Google Fonts
- [ ] Videos: `preload="none"`, esconder no mobile
- [ ] Target: LCP < 2.5s, pagina total < 2MB

### 3.5 Compilar para Producao
```bash
# Compilar Tailwind
npx tailwindcss@3 -i _input.css -o tailwind-compiled.css --content ./index.html --minify

# Converter imagens
for f in *.png *.jpg; do [ -f "$f" ] && cwebp -q 82 "$f" -o "${f%.*}.webp"; done
```

### 3.6 Auto-Revisao Visual (antes de avançar)
Antes de considerar o build "pronto", revisar CADA secao:
- [ ] Tem pelo menos 1 elemento visual "wow" DO CATALOGO PERMITIDO? (foto tratada, mockup, video integrado, number ticker, marquee, parallax sutil, micro-interacao no CTA)
- [ ] ZERO tells de IA? (sem blob glow, aurora, floating orbs, glow em botao, glassmorphism generalizado, gradient-clip em titulo: ver `references/anti-vibe-coding.md` V1-V15)
- [ ] Desktop tem layout rico (side-by-side, grid, split): NUNCA coluna unica centralizada (exceto capture)?
- [ ] Assets reais estao no lugar? (fotos, icones Hugeicons, mockup Nanobanana, video se aplicavel): ZERO placeholders?
- [ ] Scroll reveal nas secoes-CHAVE (2 a 4 usos por pagina, no maximo 1 por secao)? NUNCA em todo elemento: reveal em excesso e sinal de vibe-coding (`anti-vibe-coding.md`, sinal 2) e reprova na wave.
- [ ] Backgrounds alternam e tem textura DISCRETA? (noise, pattern, gradiente sutil: profundidade vem de sombra real e hierarquia, nao de "aura")
- [ ] Cards e secoes tem profundidade? (shadows reais, borda 1px, elevacao no hover: sem border glow colorido)
- [ ] CTA principal tem micro-interacao? (mudanca de tom no hover, elevacao sutil, magnetic ou confetti QUANDO o tom da pagina pede: nunca glow colorido difuso)
- [ ] Video de background conforme a tabela do 3.2? (obrigatorio so onde a tabela manda; capture NAO leva)
- [ ] **Movimento decidido bloco a bloco (3.2b)?** Quais ganharam movimento, por qual rota (material do cliente, gravacao de tela, Higgsfield, CSS/Framer Motion) e por que os outros ficaram estaticos. Bloco de texto+icone sem movimento e sem motivo declarado = decisao nao tomada
- [ ] Video de fundo passa na conta do veu (`visivel = opacidade_video x (1 - alpha_veu)` >= 15%) e o texto por cima mede >= 4.5:1 de contraste?
- [ ] Produto digital/SaaS tem mockup carousel com Nanobanana? (se pagina de venda de app/ferramenta)

Se QUALQUER item acima for NAO → corrigir AGORA, antes de ir pro Step 4.

**>>> GATE 3: Todas secoes construidas com layout desktop rico + assets reais + animacoes + pelo menos 1 efeito "wow" por scroll + DECISAO DE MOVIMENTO declarada (quais blocos ganharam movimento, por qual rota, e por que os outros ficaram estaticos: ver 3.2b)? Se NAO, PARA AQUI. Pagina incompleta = pagina feia. Volte e complete o que falta. <<<**

**PARADA OBRIGATORIA:** Apresentar preview ou descricao detalhada do que foi buildado ao usuario e perguntar: "Step 3 concluido. Posso avancar para o Step 4 (VERIFICAR & SHIPAR)?", NAO AVANCAR SEM RESPOSTA.

---

## Step 4: VERIFICAR & SHIPAR (20-30 min)

**OBRIGATORIO: Auditoria Adversarial por WAVE DE SUBAGENTS antes do deploy.**
A auditoria NUNCA e feita pelo mesmo contexto que construiu a pagina (vies: o construtor
nao enxerga o proprio erro). Dispara-se uma wave de 7 subagents adversariais paralelos,
cada um com UMA lente independente, e um agente de sintese consolida o gate.

### AUTORIDADE: qual checklist e O portao

A skill tem varias listas (1.5 copy, 3.3 Brazil, 3.6 auto-revisao, 4.2 QA, Checklist
Pre-Entrega). **A wave de auditoria adversarial (4.0), com seu fallback manual (4.0b/4.1),
e O PORTAO DE ENTREGA.** Todas as outras listas sao **auxiliares de build** que ajudam a
chegar limpo na wave; nenhuma delas substitui ou dispensa a wave. Entrega = wave passou.

**Escopo:** isto vale nos caminhos CRIAR, CLONAR e MELHORAR. O caminho EDITAR (mudanca
pontual) tem portao proprio, menor e proporcional: checklist de regressao + prova do ponto
alterado. Rodar a wave de 7 lentes numa troca de headline nao e rigor, e processo errado.

### ENFORCEMENT DO GATE (ler antes de tudo, falha historica recorrente)

O maior erro documentado desta skill: o agente ACIONA a skill mas PULA esta auditoria,
builda e deploya direto, e entrega pagina com cara de IA / bug. Aconteceu em dois projetos
reais (jun/2026): um site institucional e um clone. Para tornar isso impossivel de esconder:

1. **Deploy acontece DENTRO do Step 4, DEPOIS da wave (4.0).** Buildar (Step 3) e depois
   deployar sem rodar a wave = gate pulado = a skill FALHOU. Nao existe "deploy rapido".
2. **BLOCO OBRIGATORIO DA ENTREGA (fonte unica, vale pra CRIAR, CLONAR e MELHORAR, inclusive
   na rota expressa):** a mensagem que apresenta a pagina ao usuario DEVE conter estas QUATRO
   linhas. Falta uma = gate pulado = nao entregue.

   ```
   VEREDITO DA WAVE: deploy_liberado <true|false> | scores por lente | criticos: <lista ou nenhum>
   IDENTIDADE DA PAGINA: title / description / favicon PNG quadrado / og:title / og:description /
     og:image conferidos (colar o output do screenshot-prova.js)
   PASSE DE GOSTO (4.2c): tells ANTES -> DEPOIS (o depois tem que ser 0) + itens de composicao alterados
   PROVA DE ENTREGA (4.5): arquivos de screenshot LIDOS + resultado do clique da interacao principal
   PENDENCIAS DECLARADAS: <fallbacks que rodaram degradados, deploy/Lighthouse/og:image absoluta
     quando nao houver dominio, assets que faltam>
   ```

   **No caminho EDITAR** o bloco e outro, menor: checklist de regressao + prova do ponto alterado
   + pendencias. A wave nao roda ali.
3. **Escada de fallback da wave** (usar o degrau mais alto disponivel):
   1. Tool `Workflow` disponivel → wave completa em paralelo (7 lentes, ou 3 na rota expressa).
   2. Sem `Workflow`, mas com `Task`/`Agent` (subagentes) → rodar CADA lente como subagente
      independente. E o caso mais comum e PREFERIDO ao fallback manual: preserva a auditoria
      fora do contexto que construiu.
   3. Sem nenhuma forma de subagente → fallback manual (4.0b/4.1) e **colar o scoring mesmo
      assim**, declarando que a auditoria foi auto-avaliacao. Pular e documentar como "pulei"
      nao e aceitavel sem pelo menos o fallback manual pontuado.

---

### 4.0 WAVE DE AUDITORIA ADVERSARIAL (OBRIGATORIO, roda primeiro)

Ver protocolo completo, schema e esqueleto Workflow em `references/audit-agents.md`.

1. Compilar a pagina e subir **preview deploy** (branch, nunca main) ou servir local.
2. Disparar os 7 agentes EM PARALELO via tool `Workflow` (parallel), passando
   `args: { url, arquivos }`:

   | Agente | Lente | Reprova (critical) se |
   |--------|-------|-----------------------|
   | `design-critic` | taste / anti-slop (roda `design-taste-frontend`) | taste < 4.0, ou **3+ tells visuais de IA**, ou footer/checkout quebrado |
   | `assets-auditor` | presenca de imagem/mockup/video real | so texto+gradiente+SVG, SaaS sem mockup, lead magnet sem mockup do material |
   | `visual-auditor` | hierarquia, paleta, spacing, grid desktop | formato carta, side-by-side em coluna unica, sem hierarquia |
   | `motion-auditor` | scroll reveal, hover, hero entrance, counters | hero estatico, secao sem feedback, card sem hover |
   | `mobile-auditor` | 320/375/768px, hamburger JS | layout quebra, hamburger morto, overflow |
   | `cro-auditor` | CTAs, form, WhatsApp, oferta, message match, Hook/Story/Offer | CTA insuficiente, form/checkout quebrado, sem message match |
   | `a11y-auditor` | focus, labels, alt, ARIA, contraste 4.5:1, zero emoji | falha WCAG critica, emoji na pagina |

3. Cada agente retorna o schema `VERDICT`. Agente de **sintese** consolida em `SINTESE`.
4. **GATE (regua UNICA, vale pra wave e pro fallback manual):**
   - Qualquer achado `critical` => `deploy_liberado: false` => PARA, devolve fixes,
     construtor corrige e re-roda SO as lentes que reprovaram.
   - Qualquer lente/dimensao com nota < 7 => BLOQUEIA (mesmo sem critical).
   - Media geral < 8.0 => NAO libera: aplicar os polimentos apontados e re-scorar.
   - Libera deploy apenas com: zero criticos + todas as notas >= 7 + media >= 8.0.
   (O taste-gate usa escala propria 1-5 com corte 4.0; ele alimenta a lente design-critic,
   nao substitui esta regua.)

> Se a tool `Workflow` nao estiver disponivel na sessao, cair no fallback manual abaixo
> (4.0b Designer + 4.1 Estrategista pontuados inline) e DOCUMENTAR que a wave foi pulada.

---

### 4.0b AUDITORIA DO DESIGNER: Scoring System (fallback manual / checklist das lentes)

Pontuar cada dimensao de 0-10 usando `references/scoring-system.md`:

| Dimensao | Nota | Status |
|----------|------|--------|
| Hierarquia Visual | /10 | |
| Tipografia (ver `references/typography-scale.md`) | /10 | |
| Animacoes (ver `references/animation-audit.md`) | /10 | |
| Grid & Layout (ver `references/desktop-layout-rules.md`) | /10 | |
| CTAs (ver `references/cta-placement-map.md`) | /10 | |
| Prova Social (ver `references/social-proof-hierarchy.md`) | /10 ou N/A | |
| Mobile (ver `references/mobile-checklist-detailed.md`) | /10 | |
| Performance Visual | /10 | |
| Trust Signals (ver `references/trust-signals-placement.md`) | /10 | |

**Media minima para avancar: 8.0/10. Qualquer nota < 7 = BLOQUEIO.**

**Excecao unica, para quem ainda NAO tem cliente:** se o briefing (0.0) registrou a flag
`sem prova social`, a dimensao Prova Social entra como **N/A** e sai do calculo da media, desde
que a pagina traga os substitutos verificaveis (credencial do profissional, fotos reais do
espaco e do equipamento, garantia, condicao de inauguracao, CNPJ e endereco). Regra completa em
`references/scoring-system.md`, dimensao 6. Sem os substitutos, a dimensao volta a pontuar
normalmente. Depoimento inventado continua PROIBIDO em qualquer cenario.

---

### 4.1 AUDITORIA DO ESTRATEGISTA: Hook/Story/Offer

Executar auditoria estrategica completa usando `references/strategist-audit.md`:

**PRE-CHECK (responder antes de auditar):**
- [ ] De onde vem o trafego desta pagina?
- [ ] Qual a temperatura da audiencia (fria/morna/quente)?
- [ ] Qual o nivel na Value Ladder do produto?
- [ ] Qual o objetivo desta pagina no funil?
- [ ] Ha message match entre o anuncio/post e o hero?

**Dimensoes estrategicas:**

| Dimensao | Nota | Status |
|----------|------|--------|
| Hook (Gancho: hero) | /10 | |
| Story (Narrativa: mentor/transformacao) | /10 | |
| Offer (Oferta: value stack, preco, garantia) | /10 | |
| Sequencia Psicologica (AIDA expandida) | /10 | |
| Prova Social (hierarquia e distribuicao) | /10 | |
| Urgencia & Escassez | /10 | |
| Message Match com o Trafego | /10 | |

**Media minima para avancar: 8.0/10. Qualquer nota < 7 = BLOQUEIO.**

---

**Se qualquer dimensao (designer OU estrategista) ficou abaixo de 7:**
1. Identificar o que esta errado
2. Corrigir no codigo/copy
3. Re-pontuar
4. So avancar quando todas as notas forem >= 7 (idealmente >= 8)

---

### 4.2 QA Pre-Deploy

**Funcional:**
- [ ] Todos links funcionam (internos e externos)
- [ ] Todos CTAs apontam pro checkout correto
- [ ] Forms submetem corretamente (se houver)
- [ ] Countdown funcionando (se houver)
- [ ] **Consistencia de contato:** telefone, WhatsApp, email batem em TODA a pagina e nos links (`href="tel:"` / `wa.me/`). Bug real de producao: o hero mostrava um DDD e o WhatsApp ia pra outro. Conferir digito por digito.
- [ ] **Ancoras com header sticky:** todo target de ancora (`id`) tem `scroll-margin-top` >= altura da barra fixa, senao o titulo fica escondido atras dela ao clicar no menu.

**Visual:**
- [ ] Match design em breakpoints: 320px, 375px, 768px, 1024px, 1280px, 1440px
- [ ] Desktop: NENHUMA secao obrigatoria side-by-side esta em coluna unica
- [ ] Desktop: nao ha formato "carta" em paginas high-ticket
- [ ] Sem texto cortado ou overflow
- [ ] Animacoes funcionando
- [ ] Imagens carregando (nenhum placeholder vazio)

**Performance:**
- [ ] Lighthouse 90+ (todos os scores). **NAO bloqueia:** exige Chrome/Chromium instalado; sem navegador compativel vira PENDENCIA DECLARADA na entrega. **Entrega SEM deploy (pasta local/arquivo unico):** Lighthouse, QA pos-deploy, GTM e a **URL absoluta** da `og:image` viram PENDENCIAS declaradas no bloco de entrega (nao bloqueiam o gate; bloqueiam rodar trafego). **As TAGS de identidade (title, description, favicon PNG, og:title, og:description, og:image) continuam bloqueando, com ou sem deploy: ver 4.2b**
- [ ] LCP < 2.5s
- [ ] TODAS imagens em WebP
- [ ] Tailwind compilado (nao CDN)
- [ ] CSS minificado

**Conteudo:**
- [ ] ZERO placeholder/Lorem Ipsum
- [ ] ZERO dado inventado (numero, estatistica, "100%", depoimento). Se nao esta na fonte, NAO existe.
- [ ] **Diff de claims:** listar TODA afirmacao factual/promessa da pagina (urgencia, escassez, garantia, "sem gravacao", "vagas limitadas", bonus) e conferir uma a uma contra o briefing/material do usuario. Claim que nao esta na fonte = REMOVER (nao e polimento, e dado inventado).
- [ ] Textos revisados (sem typos)
- [ ] Precos corretos
- [ ] Links de checkout corretos
- [ ] Telefone/WhatsApp correto
- [ ] **Sweep de travessao:** rodar `grep` pelo caractere em-dash (U+2014) nos arquivos da pagina, resultado deve ser ZERO. Substituir por `:` / `,` / `.` ou reescrever. Vale pra todo texto do output.

**Tracking:**
- [ ] GTM presente (head + body) SE o projeto/cliente forneceu container (senao: pendencia declarada na entrega)
- [ ] Meta Pixel (se aplicavel)
- [ ] UTM pass-through funcionando

**SEO + compartilhamento:** nao e item de checklist, e GATE. Ver **4.2b IDENTIDADE DA PAGINA**, logo abaixo, com o comando que reprova.

**Acessibilidade:**
- [ ] Contraste 4.5:1 minimo
- [ ] Alt text em todas imagens
- [ ] Focus states visiveis
- [ ] `prefers-reduced-motion` respeitado
- [ ] ZERO emojis (usar icones SVG)

### 4.2b IDENTIDADE DA PAGINA: title, description e favicon sao GATE, nao checklist

Toda pagina entregue TEM que sair com, no minimo:
- `<title>` proprio (nao "Document", nao o nome do template)
- `<meta name="description">` que descreve a oferta, nao o produto generico
- **favicon PNG** do projeto (`<link rel="icon" type="image/png" href="favicon.png">`) mais
  `apple-touch-icon`. Favicon so em SVG nao serve: muitos navegadores nao leem.
- `og:title`, `og:description` e `og:image`

**O comando que reprova** (o mesmo da prova de entrega 4.5, que ja abre a pagina no Playwright):

```bash
node <dir-da-skill>/scripts/screenshot-prova.js <url> <outdir>
# a checagem de identidade roda junto e sai com exit 1 se faltar item obrigatorio.
# So no BASELINE do caminho MELHORAR (pagina de terceiro, ainda nao sua) use --sem-identidade.
# Na prova de entrega, NUNCA passe essa flag: seria pular o gate.
```

**O que bloqueia e o que vira pendencia (regra unica, nao "depende"):**
- title, meta description, favicon PNG quadrado, `og:title` e `og:description`: **BLOQUEIAM
  sempre**, inclusive na entrega sem deploy. Sao 6 linhas de HTML e nao dependem de dominio.
- `og:image`: a TAG e obrigatoria sempre. Ja o ARQUIVO 1200x630 com **URL absoluta** exige
  dominio: sem deploy, deixar o caminho relativo no HTML, gerar a imagem, e declarar
  "og:image com URL absoluta pendente ate o dominio existir". Isso e pendencia declarada,
  nao gate aberto.

**Gotcha do favicon:** favicon TEM que ser quadrado. Redimensionar preservando proporcao
(`sips -Z`, `object-fit` e afins) a partir de uma foto 3:2 devolve 32x21, nao 32x32, e o
navegador distorce. Recorte quadrado PRIMEIRO, depois redimensione. Conferir com
`sips -g pixelWidth -g pixelHeight` antes de declarar pronto: os dois numeros tem que ser iguais
(o script tambem confere isso sozinho).

**Receita da og:image 1200x630:** montar um HTML do card (logo + foto + headline + contato),
renderizar via Playwright e exportar JPG/PNG. **Receita do favicon:** recorte quadrado e depois
`rsvg-convert -w 180 -h 180 logo.svg -o apple-touch-icon.png` (e 32/16px), ou `sips -c` a partir
da foto.

Por que virou gate e nao ficou no checklist: ja estava escrito no checklist, com aviso de que
"saiu zerado na 1a versao", e MESMO ASSIM uma pagina foi entregue sem favicon e sem nenhuma og
tag (demo de pilates, 25/08/2026). Checklist nao bloqueia, gate bloqueia. Item que so vive em
lista de conferencia e item que vai ser pulado quando o contexto encher.

O custo de errar e desproporcional ao esforco de acertar: a pagina e compartilhada no WhatsApp e
no Instagram sem imagem nenhuma e com titulo errado, e parece amadora antes de alguem abrir.

---

### 4.2c PASSE DE GOSTO (ultimo ato ANTES do deploy, OBRIGATORIO)

A `design-taste-frontend` ja rodava nesta skill em dois pontos, e mesmo assim saiu pagina com
cara de IA. O motivo: nos dois pontos ela roda como LENTE DE AUDITORIA, que da nota e aponta.
**Apontar o defeito nao e remover o defeito.** Uma nota 8,5 com tres tells presentes continua
sendo uma pagina com tres tells presentes.

Por isso existe este passo, e ele e o ULTIMO antes do deploy: depois da wave (4.0), depois do QA
(4.2), com a pagina rodando (preview local ou de branch). Carregue a `design-taste-frontend` e
passe a pagina inteira com mandato de CORRIGIR, nao de pontuar.

**ORDEM FIXA do Step 4, sem interpretacao:** 4.0 wave → 4.2 QA → 4.2b identidade → 4.2c passe de
gosto → 4.3 deploy → 4.4 QA pos-deploy → 4.5 prova de entrega → GATE 4. O passe roda ANTES do
deploy justamente pra nao existir "corrigi depois do print": se por qualquer motivo voce mexer na
composicao DEPOIS do 4.3, e obrigatorio re-deployar e repetir o 4.5 inteiro.

**O que este passe caca, na ordem em que mais entrega resultado:**

1. **Icone generico em caixinha.** Quadradinho arredondado com fundo tingido + glifo abstrato e
   o tell mais reconhecivel que existe. Piora quando o glifo nao significa nada (um risco pra
   "fortalece a lombar", um alvo pra "respira"). Saidas melhores, em ordem: recorte real de uma
   foto que a pagina ja tem, virando miniatura; tirar o icone e deixar a tipografia carregar;
   marca desenhada com personalidade que represente mesmo a ideia. Trocar por OUTRO glifo
   generico nao resolve nada.
2. **Uniformidade excessiva.** Todos os cards do mesmo tamanho, todo canto com o mesmo raio,
   toda sombra igual, toda secao centralizada, toda secao com a mesma estrutura de titulo e
   subtitulo. Pagina feita por gente tem ritmo: algo quebra a grade, algo e assimetrico.
3. **Os 15 tells de `references/anti-vibe-coding.md`**, com os numeros medidos, nao no olho.

**O que NAO se mexe neste passe:** paleta e tipografia (vieram do banco de design e ja foram
decididas), copy (foi travada no COPY LOCK), e qualquer coisa que ja passou por medicao
(contraste, opacidade calibrada, enquadramento). O passe e de COMPOSICAO e PERSONALIDADE.

**Prova de que rodou:** a lista dos itens de composicao alterados (o que era e o que virou) mais
a contagem de tells ANTES e DEPOIS. **O DEPOIS tem que ser 0.** Como o Step 3.6 e a wave ja
exigem zero tells antes daqui, `0 → 0` e resultado VALIDO e comum: nesse caso a prova e a lista
de itens de composicao inspecionados (icones, ritmo, assimetria), nunca "rodei e estava tudo
certo" sem citar o que foi olhado.

---

### 4.3 Deploy

```bash
# Cloudflare Pages (subpasta em projeto existente)
cp -r /caminho/local/ /caminho/projeto-principal/dist/public/subpasta/
npx wrangler pages deploy "/caminho/projeto-principal/dist/public" --project-name NOME --commit-dirty=true

# OU Vercel
vercel --prod

# OU Git
git add . && git commit -m "feat: nova pagina" && git push
```

**Regras de deploy:**
- NUNCA sobrescrever projetos existentes
- SEMPRE criar subpasta para paginas novas
- Paths relativos (sem `/` inicial)
- Deploy IMEDIATO apos qualquer edicao

### 4.4 QA Pos-Deploy

- [ ] Pagina live = pagina local (comparar visualmente)
- [ ] GTM dispara (verificar via Tag Assistant)
- [ ] Checkout funciona no dominio live
- [ ] Mobile: testar em dispositivo real (nao so emulador)
- [ ] OG tags funcionam (testar sharing debugger)

### 4.5 PROVA DE ENTREGA (screenshots lidos + interacao testada, OBRIGATORIO)

Falha historica (auditoria de sessoes 02/07/2026, 34 casos de "pronto sem estar"): o script
de screenshot quebrava e a pagina era entregue mesmo assim (uma proposta comercial), ou a
interacao principal nunca foi clicada (uma roleta publicada com o popup morto). Regra dura:

**SE A VERIFICACAO QUEBRAR, A ENTREGA ESTA BLOQUEADA. Conserta a verificacao primeiro.
"Nao consegui tirar screenshot" NUNCA justifica entregar sem prova.**

1. Rodar o script canonico no DEPLOY REAL (nao no preview de build, nao no arquivo aberto com
   `file://`). **Unica excecao: entrega SEM deploy**, e ai a prova roda contra o servidor local
   com compressao (`python3 scripts/servidor-gzip.py <pasta> <porta>`), com o deploy declarado
   como pendencia no bloco de entrega:
   ```bash
   node <dir-da-skill>/scripts/screenshot-prova.js <url-live> <outdir>
   # pagina com interacao principal (roleta, quiz, form, popup, calculadora):
   node <dir-da-skill>/scripts/screenshot-prova.js <url-live> <outdir> --click "<seletor do CTA/interacao>"
   ```
   O script captura desktop (1440px) + mobile (390px) full-page e o estado pos-clique, e
   **roda junto a checagem de IDENTIDADE DA PAGINA (4.2b)**: title, description, favicon PNG
   quadrado, og:title, og:description e og:image.
   Ele sai com erro (exit 1) se a pagina nao carregar, o clique falhar, o PNG vier em branco
   ou faltar item de identidade. Colar o output dele no bloco de entrega.
2. **LER os PNGs com a tool Read** (olhar com os proprios olhos) e conferir contra o
   checklist: ID visual real, sem tells de IA, sem secao quebrada, popup/resultado da
   interacao visivel no pos-clique.
3. Pagina com interacao principal: o `--click` e OBRIGATORIO nos DOIS viewports (o script
   ja faz). Form de captura: submeter um lead de teste e confirmar o destino (webhook,
   planilha, CRM) antes de declarar pronto.
4. Usar Playwright headless (o script acima), NUNCA o Chrome MCP pra essa prova: em pagina
   pesada o MCP da timeout de 45s e derruba a verificacao (falha recorrente nas sessoes).
5. A mensagem final de entrega deve citar os arquivos de screenshot lidos e o resultado
   do teste de interacao, junto com o veredito da wave (4.0).

**>>> GATE 4: Auditoria Designer (media ≥8.0, sem notas <7) + Auditoria Estrategista (media ≥8.0, sem notas <7) + QA checklist 100% pass (Lighthouse 90+ quando houver navegador; sem ele, pendencia declarada) + CONSISTENCIA DE CONTATO conferida digito por digito (colar no bloco de entrega os numeros achados no HTML e nos `tel:`/`wa.me`: mais de um numero distinto sem justificativa REPROVA) + DIFF DE CLAIMS feito (lista de afirmacoes x fonte, com o veredito de cada uma) + IDENTIDADE DA PAGINA (4.2b, com o output do `screenshot-prova.js` sem REPROVA) + PASSE DE GOSTO rodado (4.2c, com os itens de composicao alterados e a contagem de tells, que tem que terminar em 0) + deploy funcionando e verificado + ZERO placeholders + PROVA DE ENTREGA 4.5 (screenshots desktop/mobile LIDOS + interacao principal testada)? Se NAO em qualquer item, PARA AQUI. Corrige TUDO antes de entregar.**

**ENTREGA SEM DEPLOY (pasta local, arquivo unico, aluno sem conta de hosting) e caminho LEGITIMO, nao gate pulado:** a prova 4.5 roda contra o servidor local (`python3 scripts/servidor-gzip.py <pasta> <porta>`), e deploy, QA pos-deploy, Lighthouse e `og:image` com URL absoluta entram como PENDENCIAS DECLARADAS no bloco de entrega. Tudo o mais do GATE 4 continua valendo igual: wave, identidade, passe de gosto, contato, claims e prova lida com os proprios olhos. **<<<**

---

## Step 5: MEDIR & ITERAR (ongoing, primeiro check 48h)

**A pagina NAO esta pronta quando vai ao ar. Esta pronta quando CONVERTE.**

Referencia completa: `references/post-launch.md`

### 5.1 Setup de Medicao
- Instalar Microsoft Clarity (gratis) para heatmaps + recordings
- Verificar GTM events: page_view, scroll_depth, cta_click, checkout_click
- Verificar GA4 conversions

### 5.2 Primeiro Check (48h)
Apos 48h com trafego:
1. **Scroll depth:** onde param de scrollar?
2. **Heatmap:** onde clicam (e onde nao)?
3. **Recordings:** assistir 10 sessoes
4. **Comparar com benchmark** (ver tabela em post-launch.md):
   - Sales page: 2-5% conversao
   - Capture: 15-30%
   - Challenge: 20-40%

### 5.3 Se Abaixo do Benchmark
1. Identificar secao mais fraca (maior drop-off no scroll depth)
2. Formular hipotese: "Se mudar X, Y melhora porque Z"
3. **Voltar ao Step 3** para ajuste CIRURGICO (nao reformar tudo)
4. Re-deploy e re-medir em 48-72h
5. Se melhorou → documentar como pattern
6. Se piorou → reverter

### 5.4 Se No Benchmark
Documentar o que funcionou na pattern library pessoal:
- Tipo de pagina, preco, conversao, LCP
- Quais secoes engajaram mais
- Quais CTAs performaram melhor
- Aprendizado principal

---













## Regras de Deploy (OBRIGATORIO)

### Quando deployar
- **Pagina nova ou mudanca visual/estrutural:** deploy acontece DENTRO do Step 4, DEPOIS da wave de auditoria. Nunca antes. (Esta regra vence qualquer outra: ver ENFORCEMENT DO GATE.)
- **Hotfix pos-wave em projeto ja no ar** (typo, link, contato, ajuste pontual que nao muda layout): deploy imediato apos a edicao, sem esperar o usuario pedir, seguido dos sweeps rapidos de QA (contato, travessao, links).

### NUNCA Sobrescrever Projetos Existentes
- Ao subir pagina nova em projeto Cloudflare Pages (ou Vercel, etc.) que JA TEM CONTEUDO, **NUNCA** fazer deploy de uma pasta avulsa que sobrescreva o conteudo inteiro.
- **SEMPRE** criar uma subpasta dentro do projeto existente para a pagina nova.
- **Workflow correto:**
  1. Verificar o que ja existe no projeto hospedado (checar `dist/public/`, `wrangler.toml`, etc.)
  2. Criar a pagina nova em subpasta (ex: `dist/public/evento-0326-v1/`)
  3. Copiar a subpasta para dentro do projeto original
  4. Fazer deploy a partir do diretorio raiz do projeto original (ex: `dist/public/`)
- **Workflow ERRADO (nunca fazer):** deployar pasta avulsa direto com `wrangler pages deploy minha-pasta/`: isso APAGA tudo que existia antes no projeto.
- Motivo: Cloudflare Pages substitui TODOS os arquivos do deploy anterior. Se voce deployar so a subpasta, todas as outras paginas/rotas desaparecem.

---


## Anti-Patterns de codigo (NUNCA FACA)

> Esta lista e a de CODIGO, CSS e performance. A lista de PROCESSO e de cara de IA esta em
> "ANTI-PATTERNS DE PROCESSO E DE IA", antes dos gates. Sao duas, e as duas valem.

- Mais de 3 tamanhos de fonte por pagina
- Espacamento aleatorio (usar grid de 8px)
- Preto puro (#000) em branco puro (#fff)
- Texto colorido em fundo colorido sem checar contraste
- Animacoes > 500ms para elementos de UI
- Glassmorphism em tudo
- Sombras em tudo
- Gradientes em texto (dificil de ler)
- Animacoes automaticas que nao podem ser paradas
- Remover indicadores de foco
- Texto cinza abaixo de 4.5:1 de contraste
- Alvos de clique < 44px
- **NUNCA usar `cdn.tailwindcss.com` em producao**: e um script JS que gera CSS no browser; Cloudflare Rocket Loader e CDNs bloqueiam/deferrem, quebrando TODO o layout. Sempre compilar para CSS puro
- Paths absolutos (com `/`) em assets quando deploy for em subpasta: quebra em Cloudflare Pages e similares
- Imagens PNG/JPG grandes sem converter para WebP antes do deploy
- Operador `!x.bottom > 0`: precedencia errada; usar `x.bottom <= 0`
- CSS duplicado (ex: duas definicoes de `.btn-gold`): auditar antes de entregar
- **NUNCA usar `section > * { z-index: 1 }` para "subir" conteudo acima de backgrounds**: cria stacking contexts nos filhos, quebra overlaps entre secoes. Usar `z-index: -1` nos backgrounds + `isolation: isolate` na section
- **NUNCA adicionar `overflow: hidden` em secoes com imagens/elementos que fazem overlap** (margin negativo) entre secoes adjacentes
- **Evitar overlaps entre secoes com margin negativo**: extremamente fragil com animacoes de fundo. Preferir manter conteudo dentro de uma unica secao
- Badges/selos decorativos sem funcao ("● online", "live feed" falso): cara de vibe-coding
- **NUNCA entregar pagina com botao de compra/CTA que nao dispara, ou sem footer legal**: os 2 maiores tells de vibe-coding (ver `references/anti-vibe-coding.md`)

---

## Blueprints Comprovados

Paginas que atingiram 100% de aprovacao e estao documentadas como referencia completa:

Ao reusar padroes de projetos anteriores, salve blueprints proprios em `references/projects/`
(paletas, animacoes, gradientes, componentes comprovados) e consulte-os ao criar paginas similares.

### Protocolo de Manutencao dos Blueprints

**Ao concluir qualquer pagina aprovada pelo usuario (nota >= 9/10 em todas as dimensoes):**

1. Verificar se o tipo de pagina ja existe no registro de blueprints do projeto
2. Se nao existe: criar `references/{slug-da-pagina}-patterns.md` com:
   - Paleta CSS completa usada
   - Font pairing
   - Layout por secao
   - Videos de background (nomes dos arquivos + fontes)
   - Componentes e efeitos especiais usados
   - Licoes aprendidas (anti-patterns encontrados)
3. Registrar no arquivo do projeto (references/projects/) a URL, o tipo e o caminho do arquivo
4. **Nao criar blueprint de paginas em andamento**: apenas apos aprovacao final do usuario

---


## Projetos: Referências de Contexto (local, por projeto)

Arquivos de projeto ficam em `references/projects/` (gerados localmente, fora do Git). Ler antes
de qualquer código quando o projeto já foi trabalhado antes. Estrutura: ver `references/projects/EXAMPLE.md`.

## Sessões Anteriores (local)

Histórico em `references/sessions/` (gerado localmente, fora do Git). Consultar para continuidade
entre sessões do mesmo projeto. Estrutura: ver `references/sessions/EXAMPLE.md`.

## Links Externos

- shadcn/ui: https://ui.shadcn.com
- Tailwind CSS: https://tailwindcss.com/docs
- Magic UI: https://magicui.design/docs
- Radix UI: https://www.radix-ui.com
- React Hook Form: https://react-hook-form.com
- Zod: https://zod.dev
- Lucide Icons: https://lucide.dev (UI simples, dashboards: ~1.500 ícones, 1 estilo)
- Heroicons: https://heroicons.com (Tailwind UI: ~300 ícones, outline/solid)
- **Hugeicons: https://hugeicons.com** (landing pages premium: 46.000+ ícones, 10 estilos, `npm install hugeicons-react`)

## Galerias de Referência Visual: Atualizadas 2026

### Por componente / seção (usar antes de construir)
- CTA Gallery: https://cta.gallery: referência obrigatória antes de qualquer CTA section
- Navbar Gallery: https://navbar.gallery: referência obrigatória antes de qualquer NavBar
- Component Gallery: https://component.gallery: 60 componentes × 95 design systems × 2.676 exemplos

### Por tipo de site
- Saaspo: https://saaspo.com: 2.900 páginas SaaS, 709 seções, filtros por tipo/stack/indústria
- Curated Design: https://curated.design: curadoria premium por nicho (Tech, AI, Finance, Agency, E-commerce)
- Landing Love: https://landing.love: 1.946 sites com vídeo full-page; categorias: `/categories/minimal/`, `/dark-mode/`, `/saas/`, `/3d-website/`, `/technology/`
- Rebrand Gallery: https://rebrand.gallery: identidade visual, rebrands de marcas grandes

### Mobile / UX patterns
- Mobbin: https://mobbin.com: 599.800 screenshots de 1.150+ apps, busca por padrão de UI
