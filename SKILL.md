---
name: construtor-paginas
version: 2.0.0
description: "Use quando o usuário quiser criar uma página web (landing page, sales page, captura, institucional, portfólio, dashboard), clonar uma página existente a partir de URL ou PDF, refazer/redesenhar uma página (v2, redesign, upgrade visual), otimizar/auditar o visual de uma página já publicada, ou editar algo pontual numa página que já existe (trocar texto, headline, cor, preço, adicionar/remover seção, corrigir mobile). Sinais: criar página, landing page, hero section, clonar site, copiar página, refazer página, pdf para html, melhorar página, deixar bonito, editar página, trocar texto, mudar cor, ajustar botão, adicionar seção, arrumar mobile. Stacks: React, Next.js, Vue, Svelte, HTML+Tailwind."
---

# Construtor de Páginas - Skill Completa

Skill unificada para construir páginas web profissionais, bonitas e de alta conversão. Combina o melhor de 7 skills especializadas em uma única referência.

**`<dir-da-skill>`** em todo comando = a pasta onde esta skill foi clonada, a que tem este
SKILL.md (ex.: `~/minhas-skills/construtor-paginas`). Troque pelo caminho real antes de colar.
`<dir>` = a pasta do projeto da página.

**Glossário (as palavras em inglês que aparecem neste arquivo):**
- **gate**: portão. Comando ou checagem que REPROVA (sai com código 1) e impede avançar.
- **tell**: sinal que entrega página feita por IA (kicker, número gigante, brilho atrás do texto).
- **kicker / eyebrow**: rótulo curto em caixa alta, com letra espaçada, em cima do título. Proibido.
- **wave / lente**: rodada de auditoria com 8 revisores independentes; cada revisor e uma lente.
- **fallback**: rota reserva quando a ferramenta principal falta (ex.: componente a mão sem 21st.dev).
- **MCP**: conector que da ferramentas novas ao Claude (21st.dev, Stitch). Aparece em `claude mcp list`.
- **LCP**: tempo até o maior elemento da primeira tela aparecer. Meta: abaixo de 2,5 s.
- **og:image**: imagem que aparece quando o link e compartilhado no WhatsApp e no Instagram.
- **dials / design read**: ajustes e leitura de direção visual das skills de design (Step 2).
- **CTA**: o botão da ação principal (agendar, comprar, chamar no WhatsApp).

---

## RUNBOOK (a espinha: leia isto primeiro, o resto e detalhe)

**Caminho CRIAR: siga `references/caminho-criar.md`**, uma página com todos os comandos na
ordem exata. Este SKILL.md vira o índice do porque de cada passo.

O essencial pra rodar, em poucas linhas. O detalhe de cada item esta nas seções abaixo; conteúdo pesado de implementação fica em `references/` e só deve ser carregado quando o caso pedir (ver Índice).

1. **5 caminhos:** CRIAR do zero / CLONAR (URL ou PDF) / **CLONAR + ELEVAR** (clone E melhoria no mesmo pedido) / MELHORAR (página que já existe e vai continuar existindo) / EDITAR (mudança pontual). **Atenção ao 2B:** rodar CLONAR quando o pedido era CLONAR+ELEVAR entrega uma página fiel que o dono reprova de olho, porque fidelidade e o oposto de melhoria. **Rotear ANTES de tudo** (ver "CAMINHOS DE EXECUÇÃO"): cada um tem fluxo e gates próprios. Rodar 6 steps numa troca de headline e tão errado quanto editar no improviso uma página nova.
1b. **ANTES DE TUDO:** rodar `python3 <dir-da-skill>/scripts/checar-ferramentas.py`. Crítico sem responder = PARA e conduz a correção. Ferramenta morta com fallback silencioso já deixou as duas camadas visuais desligadas por meses.
1c. **Aluno sem conta paga, sem chave nenhuma:** pode fazer a página inteira. 21st.dev e Higgsfield são OPCIONAIS e nunca bloqueiam: a rota padrão do aluno e componente feito a mão em Tailwind e movimento em CSS. O que bloqueia e só o que é de graça: Playwright, a skill `design-taste-frontend`, o banco de design (`search.py`), a foto real sem chave (Openverse) e o gate de tells.
2. **Step 0 começa pela ENTREVISTA DE BRIEFING (0.0):** as seis perguntas da rodada 1 pra todo mundo, rodada 2 só pra quem já tem cliente. Sem as seis respondidas, não avança. Antes disso roda o **0.0-PRE**, que é um GATE: `checar-ferramentas.py` manda cada ferramenta FAZER algo e confere o retorno. Ferramenta CRÍTICA sem responder **para a skill** até ser conectada (o agente conduz a instalação, não só avisa). Opcional degradado segue, com a degradação DECLARADA na entrega. Por fim, carregar contexto do projeto.
3. **Ordem sagrada:** COPY (Step 1) → DESIGN (Step 2) → CÓDIGO (Step 3). Nunca pixel antes de copy travada.
4. **Step 1:** se o usuário já trouxe copy, validar e travar (COPY LOCK); senão gerar (copy-pagina-vendas opcional).
5. **Step 2:** consultar o banco de design (`search.py`: aceita os termos comuns em português, como pilates, estúdio, clínica, consultório, academia, restaurante, advocacia, e traduz sozinho) pra estilo/paleta/fonte antes de inventar; wireframe no Stitch (ou fallback).
6. **Step 3:** buildar com componentes do 21st.dev, após passar no gate de entrada, **assets reais** (foto/mockup/video, nunca só SVG+gradiente), zero dado inventado.
7. **Step 4 e O PORTÃO:** rodar a wave de auditoria adversarial (8 lentes + síntese). Deploy acontece DENTRO do Step 4, DEPOIS da wave.
7b. **Gate barato que roda ANTES da wave:** `gate-classes-mortas.py`. Classe de utilitário invalida passa no build e morre no CSS, e nenhum gate visual pega. Já custou uma barra fixa sem fundo em 92% da rolagem.
8. **ENFORCEMENT (caminhos CRIAR, CLONAR e MELHORAR):** a mensagem de entrega DEVE conter o BLOCO OBRIGATÓRIO DA ENTREGA, com as quatro linhas fixas (veredito da wave, identidade da página, passe de gosto, prova de entrega) mais as pendências. Texto único e completo na seção "ENFORCEMENT DO GATE" do Step 4, item 2. Sem o bloco = você pulou o gate = falhou. **No caminho EDITAR a wave NÃO roda:** ali o bloco e o checklist de regressão + a prova do ponto alterado.
9. **Ferramentas críticas bloqueiam quando ausentes;** opcionais podem degradar com motivo declarado.
10. **Bloqueia entrega:** 3+ tells de IA, página sem asset real, footer-legal/checkout quebrado, dado inventado, crítico confirmado ou regressão confirmada. O ciclo 4.2f decide sobre as notas.
11. **Regras absolutas do output:** zero travessão (grep U+2014 = 0), zero emoji, acentuação PT-BR correta, consistência de contato.
11b. **NUNCA INVENTAR ID VISUAL.** Se o usuário indicou/forneceu a identidade (pasta de assets, logo, paleta, fontes, link, PDF, slides), USAR O ASSET REAL. Recriar logo em texto/SVG aproximado, chutar cor ou fonte = PROIBIDO. Só criar do zero quando NÃO há ID indicada. Logo legível demais a 40px? Aumenta o tamanho ou pede uma versão, nunca substitui por uma invenção.
12. **Pos-sessao:** registrar contexto em `references/sessions/` e `references/projects/` (locais). Proibido entregar e não registrar.
13. **Atalhos:** capture simples/pagina trivial → ROTA EXPRESSA (steps colapsados, wave de oito lentes). Sessão nao-interativa ou "faz direto" → sem paradas, gates inline (ver exceção no protocolo de execução).

---

## MAPA DESTE ARQUIVO (onde cada coisa mora)

| Bloco | Seções |
|---|---|
| **Roteamento** | RUNBOOK, QUANDO ACIONAR, CAMINHOS DE EXECUÇÃO (CRIAR / CLONAR / MELHORAR / EDITAR), PORTA ÚNICA |
| **Preparação** | PROTOCOLO DE ATIVAÇÃO (pre-requisitos + instalação), GATE DE QUALIDADE auxiliar, PROTOCOLO POS-SESSAO, Índice de `references/` |
| **O fluxo** | Processo de 6 Steps, parada forçada, rota expressa, regras inegociáveis, anti-patterns, gates, tech stack, **Step 0** (0.0 briefing, 0.1 a 0.7), **Step 1** copy, **Step 2** direção, **Step 3** build (3.2 vídeo, **3.2b movimento/Higgsfield**, 3.6 auto-revisao), **Step 4** (4.0 wave, 4.0b/4.1 scoring, 4.2 QA, **4.2b identidade**, **4.2c passe de gosto**, 4.3 deploy, 4.4 QA pós, 4.5 prova, GATE 4), **Step 5** medir |
| **Apêndice** | Regras de deploy, anti-patterns de código, blueprints, projetos e sessões locais, links e galerias |

**Nada que seja etapa de execução mora depois do Step 5.** Se você esta escrevendo uma exigência
nova, ela entra dentro do step que a executa, nunca no fim do arquivo.

---

## QUANDO ACIONAR: 4 GATILHOS OBRIGATÓRIOS (sem exceção)

Esta skill DEVE ser acionada automaticamente, ANTES de qualquer código, sempre que o usuário quiser:

1. **CRIAR uma página nova** (landing, sales page, institucional, home, dashboard, etc.)
2. **CLONAR uma página existente** (de URL ao vivo ou PDF): "clonar essa página", "copiar esse site", "replicar esse layout"
3. **MELHORAR uma página que já existe e vai continuar existindo**: "melhora essa página", "otimiza", "aumenta a conversão", "deixa mais bonita", "audita essa página", e também "refazer / v2 / redesign" quando o objetivo é elevar a mesma página
4. **EDITAR algo pontual numa página existente**: "troca o headline", "muda a cor do botão", "corrige o preço", "adiciona uma seção de FAQ", "arruma no mobile"

Se a mensagem do usuário cair em qualquer um dos 4, ACIONE a skill primeiro. Não começar a codar,
nem perguntar detalhes soltos, antes de entrar no fluxo da skill (Step 0 → ...). Falha histórica
documentada: numa sessão de clone real (jun/2026) o agente NÃO acionou a skill de cara e o usuário teve que
mandar, não repetir.

Caso de clone especificamente: ler `references/projects/` antes, e seguir as regras de clone
(manter identidade original: cores via `getComputedStyle`, logo real baixado do site). Ver
anti-patterns no fim deste arquivo e o checklist visual em `references/anti-vibe-coding.md`.

---

## CAMINHOS DE EXECUÇÃO: ROTEAR ANTES DE QUALQUER COISA

O fluxo de 6 steps foi desenhado pra página NOVA. Aplicar ele inteiro numa troca de
headline gera atrito e faz o usuário abandonar a skill; e pular ele numa página nova
gera página feia. Por isso a PRIMEIRA decisão e sempre: **qual caminho corresponde ao pedido?**

Declarar o caminho escolhido na primeira resposta, em uma linha, antes de executar:
`Caminho: EDITAR (mudanca pontual em pagina existente).`

| Sinal no pedido | Caminho | Fluxo |
|---|---|---|
| não existe página ainda | **CRIAR** | 6 steps completos |
| "clona / copia / replica" + URL ou PDF | **CLONAR** | fluxo CLONE (abaixo) |
| clone **e** melhoria no mesmo pedido ("clona e deixa foda", "clone melhorado") | **CLONAR + ELEVAR** | fluxo 2B: identidade intocada, composição elevada |
| página existe e o pedido e elevar o todo | **MELHORAR** | fluxo MELHORAR (abaixo) |
| página existe e o pedido e um ponto específico | **EDITAR** | fluxo EDITAR (abaixo) |
| página existe e o pedido e outra LINGUAGEM pro mesmo conteúdo ("a mesma ideia, mais tecnológica", "faz uma versão dark", "uma mais sobria") | **VARIANTE VISUAL** | fluxo 5 (abaixo) |

**Na dúvida entre MELHORAR e EDITAR, pergunte.** A diferença e escopo: mexer em uma
coisa nomeada e EDITAR; revisar a página e MELHORAR. Errar pra mais (rodar melhoria
quando ele queria trocar uma palavra) irrita tanto quanto errar pra menos.

**O que vale em todos os caminhos, sem exceção:** nunca inventar ID visual, nunca inventar
dado, zero travessão, zero emoji, acentuação correta, asset real, e prova de entrega
(screenshot do resultado lido com os próprios olhos) antes de dizer que acabou.

---

### CAMINHO 1: CRIAR (página nova, do zero)

Objetivo: página que ainda não existe. **Este e o único caminho que roda o rito completo:
os 6 steps, com parada forçada entre eles e os 4 gates.** O fluxo detalhado esta na seção
"Processo de 6 Steps: Workflow Principal", mais abaixo neste arquivo.

**Lista de comandos na ordem, em uma página: `references/caminho-criar.md`.**

Resumo da ordem, que é sagrada: Step 0 entender e inventariar, Step 1 COPY (fecha em
COPY LOCK), Step 2 DIREÇÃO (banco de design + wireframe), Step 3 BUILDAR (componentes e
assets reais), Step 4 AUDITAR (wave de 8 lentes) e só então deploy, Step 5 pos-sessao.
Nunca pixel antes de copy travada.

---

### CAMINHO 2: CLONAR (URL ao vivo ou PDF)

Objetivo: reproduzir com fidelidade. **Aqui a copy e a identidade JÁ EXISTEM: não
minerar VoC, não escrever copy nova, não rodar COPY LOCK.** Inventar aqui é defeito.

1. **Extrair o real, nunca olhar e chutar.** Rodar o extrator (testado em 08/08/2026):

   ```bash
   # requer playwright: npm install -g playwright && npx playwright install chromium
   node <dir-da-skill>/scripts/extrai-identidade.mjs "<URL>"
   ```

   Devolve em JSON: paleta real ordenada por frequência de uso, variáveis CSS da marca
   (`--laranja: #FA4E04` etc), o h1 e o CTA com estilo computado, lista de seções e as
   imagens. Logo: BAIXAR o arquivo, nunca recriar. Do PDF: extrair pelo arquivo.
   `redesign-existing-projects` ajuda na leitura crítica do que foi extraído.

   **Gotcha do extrator (custou duas tentativas no teste):** o Playwright e CommonJS,
   então em arquivo `.mjs` ele entra pelo default export, e o `NODE_PATH` **não vale
   pra `import`**, só pra `require`. O script resolve isso sozinho via `createRequire`
   (procura o playwright no projeto, no NODE_PATH e no root global do npm). Nunca cravar
   caminho absoluto de `node_modules` no script: só funciona na máquina de quem escreveu.
2. **Inventariar o que existe**: seções na ordem, componentes, breakpoints, interações.
3. **Declarar o delta**: o que será idêntico e o que muda (e por que). Sem pedido
   explícito, o default e ZERO mudança de identidade.
4. **Buildar** seguindo Step 3 (assets reais, stack do projeto).
5. **GATE DE FIDELIDADE** (substitui o Gate 1 e 2): print do original e do clone lado
   a lado, conferindo cor a cor, fonte, hierarquia, ordem das seções e mobile. Divergiu
   sem ter sido declarado no delta? Volta.
6. Step 4 normal (wave, identidade 4.2b, passe de gosto 4.2c, deploy, QA pós, prova 4.5) e pos-sessao.

### CAMINHO 2B: CLONAR + ELEVAR (o pedido e "clona E deixa foda")

**Este caminho nasceu de uma falha real (26/08/2026).** O pedido foi "faz o clone da original e
deixa foda". Rodei o CAMINHO 2 (CLONAR), cuja regra e fidelidade, entreguei, e o dono
respondeu: *"a página ficou quase igual a original. eu não te pedi pra fazer uma melhora
visual?"*. Ele estava certo, e o processo ajudou a errar: **CLONAR mede FIDELIDADE (quanto mais
parecido, melhor) e MELHORAR mede NAO-REGRESSAO (não pode piorar). Nenhum dos dois pergunta se
ficou MELHOR.** Rodando o caminho errado, o gate aprovou uma entrega que o dono reprovou em
dois segundos de olho.

**Como saber que é este caminho:** o pedido tem as DUAS coisas, clone e melhoria ("clona e
melhora", "faz igual mas melhor", "clone melhorado", "deixa foda"). Na dúvida, pergunte: a
diferença entre os dois caminhos e enorme e cara.

#### O que é INTOCÁVEL (some com isto é você destruiu a marca do cliente)
Extraia com `scripts/extrai-identidade.mjs` e NÃO mexa: cor, logo, família tipográfica, copy,
telefone, endereço, CNPJ, números. Identidade real vence qualquer preferência estética, sua ou
de skill de design. Se a `high-end-visual-design` mandar trocar Inter por Geist e Inter for a
fonte do cliente, a resposta e não, e o conflito se declara na entrega.

#### O que você DEVE mudar (e o trabalho, não um bônus)
O erro de 26/08 foi confundir HIGIENE com DESIGN. Trocar ícone genérico por foto, reorganizar
grid, converter para WebP e otimizar peso e higiene: melhora a página e **não muda o que a
pessoa VÊ quando abre**. Elevar mexe nos eixos abaixo.

| Eixo | Pergunta que ele responde | Sinal de que você não mexeu |
|---|---|---|
| **Composição** | as seções ainda são retângulos empilhados? | toda seção e um container centralizado, uma embaixo da outra |
| **Escala** | a tipografia tem drama? | h1 e h2 no mesmo tamanho da original, tudo entre 2 e 3rem |
| **Profundidade** | há camada, sobreposição, sangria? | tudo chapado, nada atravessa a borda de uma seção |
| **Movimento** | o que se mexe, e por que? | só fade-in de scroll, igual em toda seção |
| **Densidade** | o ritmo varia? | mesma altura de seção e mesmo respiro do início ao fim |
| **Assinatura** | qual é o elemento que só ESTA página tem? | não existe: da pra trocar por qualquer concorrente |

**Regra prática:** pelo menos **quatro** dos seis eixos precisam ter mudança NOMEADA, com o
antes e o depois. Menos que isso, e polimento com outro nome.

#### O gate deste caminho

```bash
# 1. os dois lado a lado, na mesma escala, numa imagem so
python3 <dir-da-skill>/scripts/lado-a-lado.py <png-original> <png-sua-versao> comparativo.jpg
```

2. **OLHE a imagem** e responda, por escrito, antes de qualquer outra coisa:
   **"o dono veria a diferença sem eu apontar?"** Se a resposta honesta e não, volte. Nenhuma
   lista de melhorias compensa um "não" aqui.
3. Liste os EIXOS alterados, com antes e depois. Menos de 4 = não elevou.
4. Liste o que foi PRESERVADO da identidade, item a item. Elevar sem preservar e outro defeito,
   pior: virou outra marca.

**>>> GATE 2B: os dois prints lado a lado, a resposta escrita da pergunta do item 2, quatro ou
mais eixos com antes/depois, e a lista do que foi preservado? Se NÃO, PARA AQUI. <<<**

**Por que não existe um número aqui:** a primeira tentativa de gate foi um medidor de distância
visual por pixel (ritmo de luminância, altura, peso claro/escuro). Ele reprovou no próprio teste
de calibração: deu 27,3% para a versão que o dono REPROVOU e 26,3% para a corrigida, ou seja,
apontou a boa como mais parecida com a original. Diferença de pixel não mede "cara de igual",
que mora em composição e escala. O medidor foi descartado; ficou o olho, com a imagem na mão.

---

### CAMINHO 3: MELHORAR (a página continua sendo a mesma, só melhor)

Objetivo: elevar sem destruir o que já funciona. O erro clássico e "melhorar" trocando
tudo e derrubando a conversão que existia.

1. **BASELINE PRIMEIRO, obrigatório.** Antes de tocar em qualquer coisa: screenshot
   desktop e mobile do estado atual, Lighthouse atual, e o que já converte (se houver
   dado). Sem baseline não existe "melhorou", existe "ficou diferente".

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

   **MEDIR SEMPRE COM COMPRESSÃO. `python3 -m http.server` NÃO comprime, e isso
   inverte o resultado.** Custou meia sessão em 08/08/2026 numa página de lançamento: servida sem
   gzip, a versão nova aparecia PIOR (Performance 76 vs 77, LCP 7,3s vs 6,3s) e o gate
   bloqueou; servida com gzip, as duas empatam em 93 e LCP 3,2s, com a nova melhor em
   TBT. A página era a mesma: mudou só o servidor. Sem compressão o HTML ia inteiro
   (116 KB); com gzip, 18 KB. Cloudflare Pages e Vercel servem comprimido, então medir
   sem compressão compara um cenário que não existe. Usar
   `scripts/servidor-gzip.py <pasta> <porta>` pra servir o build local.

   **NUNCA usar Edge headless com `--window-size=390` pra simular mobile.** Ele não emula
   dispositivo: só estreita a janela mantendo layout de desktop, e o screenshot sai com
   texto "cortado" na direita. Isso gera diagnóstico falso de overflow. Custou uma rodada
   inteira de investigação em 08/08/2026 numa página de lançamento: o print acusava corte, e a
   medição real (`scrollWidth` vs `clientWidth` em 320/375/390/768/1024) deu ZERO overflow.
   Mobile de verdade = Playwright com `isMobile: true` e `deviceScaleFactor: 2`.

   Guardar os screenshots e o JSON: o gate do fim compara contra eles.
2. **Diagnóstico com nota**, não opinião solta: rodar `references/taste-gate.md` e
   `references/anti-vibe-coding.md` sobre a página atual, e listar os problemas com
   nota por dimensão.
3. **Priorizar por impacto**: hierarquia e espaçamento primeiro (maior alavancagem),
   depois copy do above-the-fold, depois assets, depois movimento. Cosmético por último.
4. **Preservar o que funciona.** Não mexer no que já converte sem motivo declarado.
   Identidade só muda com pedido explícito.
5. **Aplicar em lotes revisaveis**, do maior impacto pro menor.
6. **GATE DE MELHORIA (nao-regressao, ADICIONAL ao GATE 4, nunca no lugar dele)**: antes e
   depois lado a lado, com a nota de cada dimensão nos dois estados. **Se houver regressão confirmada por medida, não entregue. Queda de nota isolada é sinal, conforme o ciclo 4.2f.** Lighthouse entra só como comparação CONDICIONAL: **se houve baseline
   de Lighthouse**, o novo tem que ser igual ou melhor; **sem navegador não há baseline**, então
   vira pendência declarada e NÃO bloqueia (igual ao item 1 e ao 4.2). O que bloqueia aqui é a
   nao-regressao por dimensão, que não depende de navegador.
7. **Step 4 normal** (wave, identidade 4.2b, passe de gosto 4.2c, deploy, QA pós, prova 4.5) e
   pos-sessao. O gate de melhoria empilha SOBRE o GATE 4; ele não substitui nenhum item dele.

### CAMINHO 4: EDITAR (mudança pontual, cirúrgica)

Objetivo: fazer exatamente o que foi pedido, sem efeito colateral. **Este caminho NÃO
roda os 6 steps e NÃO tem parada forçada entre steps.** Rodar o rito completo aqui é
erro de processo.

1. **Travar o escopo em uma frase** e repetir pro usuário: "vou trocar o headline da
   hero, e só isso". Se o pedido tiver mais de uma coisa, listar todas antes de começar.
2. **Localizar o arquivo real** que serve a página no ar (não um parecido). Conferir
   qual projeto/rota esta publicado antes de editar.
3. **Editar só o escopo.** Proibido "já que estou aqui" mexer em espaçamento, cor ou
   copy que ninguém pediu. Melhoria fora do escopo = propor no fim, não aplicar.
4. **Checklist de regressão** (o que quebra sem avisar): mobile, dark mode se existir,
   links e âncoras, formulário e checkout, e a seção vizinha a que foi tocada.
5. **Deploy** seguindo a regra de nunca sobrescrever projeto existente.
6. **PROVA**: screenshot do ponto alterado no ar, desktop e mobile, lido com os próprios
   olhos. Mais a confirmação de que o resto da página continua igual.
7. Registro curto na sessão (o que mudou e onde), sem o relatório completo.

**Gates que NÃO se aplicam ao caminho EDITAR:** COPY LOCK, direção visual, wireframe,
wave de 8 lentes. Uma edição pontual não precisa reauditar a página inteira. O que
continua valendo: regressão, prova de entrega e as regras absolutas de output.

### CAMINHO 5: VARIANTE VISUAL (mesmo conteúdo, outra linguagem)

Sinal no pedido: a página já existe e o que se pede e outra LINGUAGEM para o mesmo
conteúdo. "A mesma ideia, só que mais tecnológica." "Faz uma versão dark." "Uma mais
sobria pra mostrar pro cliente."

Não é CRIAR (a copy existe e já está travada), não é CLONAR (não há fidelidade a medir),
não é MELHORAR (a versão anterior continua no ar e valida) e não é EDITAR (muda tudo
menos o conteúdo). Rodar por analogia funciona até certo ponto e deixa buraco.

**TRAVADO, e não se negocia:** copy palavra por palavra, dados de contato, identidade de
marca (cor, logo, família tipográfica), ordem das seções, âncoras do menu, destino do
lead. Variante e sobre FORMA.

**MUDA:** terreno, grade, escala, densidade, movimento, famílias de layout, acabamento.

Fluxo: herda o COPY LOCK e os tokens da versão anterior, refaz o Step 2 (direção) inteiro,
refaz o Step 3, e o Step 4 roda completo, incluindo wave.

#### O gate deste caminho

1. As duas versões lado a lado (`scripts/lado-a-lado.py`), na mesma escala.
2. Responda por escrito: **"as duas leem como duas direções legítimas, ou como uma boa e
   uma pior?"** Variante que fica pior que a anterior não é variante, e regressão com
   outro nome. **A nota da wave da variante não pode ficar abaixo da nota da versão que
   ela quer acompanhar.**
3. Liste o que foi PRESERVADO, item a item. Sem isso a variante virou outra marca.
4. **Registre o que foi REJEITADO da direção nova, e por que.** Quando o banco de design
   devolveu "Cyberpunk UI" e "HUD / Sci-Fi FUI" para uma busca de dark tech, aceitar teria
   trazido neon, glitch e scanline (tells banidos) para dentro de uma página de empresa de
   segurança do trabalho. A recusa vai escrita no código, senão o próximo aceita.

#### A armadilha própria deste caminho: forma que pede conteúdo que a fonte não tem

Medido numa variante "técnica" de uma copy institucional curta: a tabela de ocorrências
ficou com **55% de régua vazia**, porque é a forma de um relatório sem o dado do
relatório. A linguagem de dado pede dado; se a fonte não fornece e a regra proíbe
inventar, a forma fica oca e a variante sai pior que a original.

**Antes de escolher a linguagem, pergunte se o CONTEÚDO a sustenta.** Copy curta e
institucional não sustenta gramática de painel. Isso se decide no Step 2, não depois de
construir.

---

## PORTA ÚNICA: NENHUMA SKILL DE DESIGN RODA SOZINHA PRA PÁGINA

Existem várias skills de design instaladas (`frontend-design`, `design-taste-frontend`,
`high-end-visual-design`, `animate`, `canvas-design`, `brandkit`, `redesign-existing-projects`,
`impeccable`). **Nenhuma delas atende um pedido de página por conta própria.** Todas são
ETAPAS deste fluxo, e quem decide quando cada uma entra e esta skill.

Motivo: sozinhas elas cobrem só um pedaço. A `frontend-design`, por exemplo, tem 55 linhas
e trata de direção estética; ela não trava copy, não consulta o banco de design, não exige
asset real, não roda a wave de auditoria, não publica e não registra a sessão. Uma página
entregue só com ela sai bonita e falha nos gates que já custaram retrabalho aqui.

**Regra de precedência (não negociar):**
- Pedido de página (criar, clonar, refazer) = ESTA skill assume, sempre, mesmo que o usuário
  cite outra skill pelo nome. Se ele pedir "faz com a frontend-design", entra por aqui é a
  `frontend-design` e usada DENTRO do Step 2.
- As outras skills são invocadas por ESTA, no step certo, e o resultado volta pro fluxo.
- Nunca rodar duas skills de design em paralelo disputando a mesma decisão: a ordem abaixo
  existe pra que cada uma opine no momento em que a decisão ainda está aberta.

**Onde cada uma entra:**

| Step | Skill que esta skill invoca | Para que |
|------|------------------------------|----------|
| antes do Step 2 | `brandkit` | só se a marca não existir ainda (logo, paleta, tipografia) |
| Step 2 | `frontend-design` | direção estética e tipográfica, antes de qualquer código |
| Step 2 | `design-taste-frontend` | framework anti-slop na direção |
| Step 2 (clone) | `redesign-existing-projects` | auditoria audit-first do que já existe |
| Step 4 | `animate` | movimento e microinteração, DEPOIS da interface resolvida |
| Step 4 | `high-end-visual-design` | acabamento premium |
| Step 4 | `design-taste-frontend` | de novo, agora como gate anti-slop sobre a página pronta |
| Step 4 | `impeccable` (CLI) | refino final opcional |
| fora do fluxo | `canvas-design` | peça gráfica estática (PNG/PDF) que acompanha a página, nunca a página |

Se o usuário pedir explicitamente só uma etapa ("me da uma direção estética", "só anima isso
aqui", "faz um pôster"), ai sim a skill específica roda sozinha: não é pedido de página.

---

## PROTOCOLO DE ATIVAÇÃO: EXECUTAR SEMPRE AO INICIAR

**OBRIGATÓRIO ao ser acionado:**

### 0. VERIFICAR PRE-REQUISITOS (MCPs + plugins + skills): RODA PRIMEIRO

Antes de qualquer coisa, checar o que esta DISPONÍVEL na sessão e direcionar o
usuário a instalar o que faltar. O modelo enxerge as ferramentas/skills ativas no
próprio contexto (lista de tools + system-reminders de skills). Confirmar presença de:

**A fonte da verdade desta tabela e o `scripts/checar-ferramentas.py`**, não o texto: e ele que
classifica cada uma como CRÍTICA ou opcional e que reprova. Se divergirem, o script vence, e o
texto e que esta desatualizado.

**CRÍTICA = para a skill até conectar.** São as que, faltando, produzem uma página pior sem
ninguém perceber, e todas são gratuitas: Playwright (sem prova de entrega você entrega no
escuro), a skill `design-taste-frontend` (sem gate anti-slop a cara de IA passa), o banco de
design, a rota de foto real sem chave e o gate de tells. **Opcional = segue, com a degradação
declarada na entrega.** 21st.dev e Higgsfield são opcionais desde o teste com aluno
(02/10/2026): o verificador dava "tudo OK" porque rodava na máquina do dono, com a chave e a
conta dele, e um aluno de verdade teria o 21st bloqueando no primeiro comando.

| Dependência | Como detectar | Papel | Faltando: bloqueia ou degrada? |
|-------------|---------------|-------|---------|
| **Playwright** | `node <dir-da-skill>/scripts/screenshot-prova.js --check` | prova de entrega, extrator de identidade, gate de vídeo | **CRÍTICA: bloqueia.** Prova obrigatória em todos os caminhos: `npm install -g playwright && npx playwright install chromium` |
| **ffmpeg / ffprobe** | `ffprobe -version` | gate de vídeo (só em página com vídeo) | pular o gate de vídeo |
| **Higgsfield (CLI)** | `higgsfield account status` (imprime e-mail, plano e créditos) | movimento e b-roll nos blocos (Step 3.2b), **OPCIONAL: a rota padrão do aluno e movimento em CSS** | conta PAGA para uso comercial. Sem ela: material real do cliente, gravação de tela, b-roll de acervo aberto ou animação CSS/Framer Motion, com a pendência declarada na entrega. Setup completo (inclusive o `higgsfield workspace set <id>`, que trava todo mundo) em `references/higgsfield.md` |
| **HF_API_KEY_ID + HF_API_KEY_SECRET (env)** | verificar presença da variável sem imprimir o valor | rota por API do `scripts/higgsfield.py` (lote, `--dry-run`) | usar a CLI (rota assistida) ou seguir sem movimento gerado |
| **Stitch (MCP)** | tools `mcp__stitch__*` | wireframe (Step 2) | auto-instalar (protocolo item 1); último caso: layout direto no código |
| **21st.dev Magic (MCP)** | `checar-ferramentas.py` faz uma CHAMADA REAL (initialize, tools/list e uma busca de componente) com a chave em `TWENTYFIRST_API_KEY` | componentes (Step 3) | **opcional, nunca bloqueia.** Sem ele: componente a mão em Tailwind, declarado na entrega. Com ele vivo, o gate de uso 4.6 cobra o uso (ou dispensa com motivo). |
| **design-taste-frontend (skill)** | skill listada | gate anti-slop (Step 4 e 4.9) | **CRÍTICA: bloqueia.** E o único passo que tira a cara de IA; sem ela o scoring manual 4.0b vira formalidade. |
| **redesign-existing-projects (skill)** | skill listada | audit-first em clone/redesign (Step 2) | recomendado (protocolo item 4); fallback: auditoria manual das 5 dimensões |
| **high-end-visual-design (skill)** | skill listada | acabamento premium (Step 4) | recomendado (protocolo item 4); fallback: segue sem |
| **impeccable (CLI)** | `npx impeccable --version` | refino UI (Step 4) | opcional, roda via npx quando precisar |
| **PEXELS_API_KEY (env)** | verificar presença da variável sem imprimir o valor | assets-search.py videos/fotos | recomendado (protocolo item 3); **fallback que NÃO precisa de chave: `--type photo` cai sozinho na Openverse e devolve FOTO REAL** (crédito ao autor obrigatório, ver `references/assets-sem-chave.md`) |
| **frontend-design (skill)** | skill listada | direção estética ANTES do código (Step 2) | recomendado (protocolo item 4); fallback: seguir só com design-taste-frontend |
| **animate (skill)** | skill listada | movimento e microinteração (Step 4, DEPOIS da UI pronta) | recomendado (protocolo item 4); fallback: animar a mão com Framer Motion, sem sistema |
| **canvas-design (skill)** | skill listada | peça gráfica ESTÁTICA que acompanha a página (PNG/PDF) | opcional: só entra se o pedido incluir arte estática |
| **brandkit (skill)** | skill listada | criar identidade quando a marca ainda não existe (antes do Step 2) | opcional: usar a identidade que o cliente já tem |

**Ordem de uso das skills de design (não inverter):** `brandkit` (identidade, se não existir)
antes de `frontend-design` + `design-taste-frontend` (direção estética, Step 2), que vem antes
do código (Step 3), que vem antes de `animate` + `impeccable` + `high-end-visual-design`
(refino e movimento, Step 4). Animar antes de a interface estar resolvida só mascara layout ruim.

**Ação (PROTOCOLO DE INSTALAÇÃO, na primeira ativação com dependência faltando):**

**As CRÍTICAS bloqueiam; as opcionais tem fallback legítimo.** Quem manda e o
`checar-ferramentas.py` (0.0-PRE). Até 26/08/2026 esta seção dizia que nada bloqueava, e o
resultado foi o pior dos mundos: o 21st.dev morreu, o fallback "faz a mão" rodou em silêncio
por meses e o teto do resultado caiu sem ninguém ser avisado. Fallback de opcional se declara na
entrega; fallback de crítica vira defeito invisível.
O que o setup completo faz e levantar o TETO do resultado (componente pronto em vez de a mão,
foto real em vez de gerada, gate de gosto automático em vez de manual). Oferecer sempre,
nunca prender o usuário num loop de instalação.

1. **Instalar AUTOMATICAMENTE o que não precisa de segredo do usuário** (fazer, não perguntar):
   - Stitch: `npm install -g stitch-mcp && claude mcp add stitch --scope user -- stitch-mcp proxy`
   - impeccable: nada a instalar (roda via `npx impeccable`)
   Executar, confirmar com o comando de detecção e avisar o usuário do que foi instalado.
2. **Playwright: necessário para a prova visual.** A prova de entrega (screenshot lido)
   e obrigatória em todos os caminhos, e depende dele. Se faltar, instalar de cara:
   `npm install -g playwright && npx playwright install chromium`.
3. **Oferecer a configuração do 21st.dev:** opcional. Quem quiser, ganha componente pronto; quem não quiser, segue com componente a mão em Tailwind. Pexels também é opcional.
4. **Instalar `design-taste-frontend`:** também é crítica. As demais skills de design são opcionais.
5. **Modo não interativo:** registrar o bloqueio crítico e os comandos de instalação. A ausência de interação não autoriza substituir ferramenta crítica por fallback. Opcional ausente (21st.dev, Higgsfield, Stitch) segue pela rota sem conta, declarada na entrega.

```bash
# --- 21st.dev Magic (componentes, OPCIONAL) --- API key gratuita em https://21st.dev/mcp
claude mcp add --transport http 21st https://21st.dev/api/mcp --scope user --header "x-api-key: <sua-chave-21st>"
# e a mesma chave no ambiente, pro checar-ferramentas.py fazer a chamada real:
export TWENTYFIRST_API_KEY="<sua-chave-21st>"

# --- Google Stitch (wireframe) --- binario global stitch-mcp
npm install -g stitch-mcp && claude mcp add stitch --scope user -- stitch-mcp proxy

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

> Depois de `claude mcp add`, os MCPs aparecem na próxima sessão (ou após reconectar).
> Sempre reportar ao usuário o resumo do que esta conectado vs o que falta antes de avançar.

### 1. Carregar contexto do projeto
verificar se existe arquivo em `references/projects/{nome-projeto}.md`. Se existir, ler antes de qualquer código.

### 2. Consultar sessões recentes
`ls references/sessions/` e ler a mais recente do mesmo projeto se houver.

### 3. Continuar de onde parou
não reinventar padrões já definidos; respeitar brand tokens, componentes e convenções do projeto.

```bash
# Busca rapida ao iniciar (caminhos relativos ao diretorio da skill)
ls ./references/projects/
ls ./references/sessions/
```

---

## GATE DE QUALIDADE: EXECUTAR ANTES DE ENTREGAR

**(Checklist AUXILIAR de build: ajuda a chegar limpo na wave. O PORTÃO de entrega e a wave de auditoria do Step 4, única autoridade final.)**

**OBRIGATÓRIO antes de declarar qualquer página pronta:**

1. **Ler `references/design-laws.md`**: verificar que nenhum ban absoluto foi aplicado sem ser solicitado explicitamente
2. **Rodar taste-gate** (`references/taste-gate.md`): score em 6 dimensões Design
3. **Regra de entrega:**
   - Score médio >= 4.0 → entregar
   - Score 3.0-3.9 → corrigir o item de maior impacto antes de entregar
   - Score < 3.0 → revisar hierarquia e espaçamento (maior alavancagem), depois re-scorar
4. **AI Slop Test final:** "Isso parece gerado por IA?" + "Tem algum detalhe que só alguém com gosto colocaria?"
5. **Rodar anti-vibe-coding checklist** (`references/anti-vibe-coding.md`): 5 sinais de substância + **15 tells VISUAIS de IA** (seção "Tells VISUAIS de IA"). FALHA em footer legal ou checkout funcional **bloqueia a entrega**.
6. **Rodar a Taste Skill SE instalada** (anti-slop, tasteskill.dev): acionar a skill `design-taste-frontend` sobre a página pronta como enforcement anti-slop. Em CLONE/redesign, usar `redesign-existing-projects` (audit-first) ANTES, no Step 2. Pra acabamento premium, `high-end-visual-design`. Se nenhuma estiver instalada: o scoring manual do item 2 (taste-gate) cobre.
7. **Refinamento profundo** (opcional): `npx impeccable detect <url>` (auditoria), `npx impeccable polish/critique` (refino).
8. **Gate de VÍDEO**: `node scripts/gate-video.mjs --url <url> --publico ./public` (só se a página tiver vídeo). Sobe sozinho o Chromium do Playwright: **não precisa de Edge nem de CDP no ar** (quem já tiver um navegador com CDP pode reaproveitar com `--cdp http://localhost:9333`). Exige `ffmpeg`/`ffprobe` no PATH. Sete checagens, todas nascidas de defeito medido numa página de lançamento em produção:
   proporção única por trilha, escala do arquivo contra a caixa, corte do `cover`, pôster com hash próprio respondendo 200, **extrair 6 frames e OLHAR** (texto cortado, nome de cliente, credencial), `preload` no pôster se o vídeo estiver acima da dobra, e `prefers-reduced-motion` deixando só o pôster.
   FALHA em pôster 404 ou em conteúdo indevido no quadro **bloqueia a entrega**.

---

## PROTOCOLO POS-SESSAO: EXECUTAR SEMPRE AO CONCLUIR

**OBRIGATÓRIO ao finalizar qualquer sessão de sucesso:**

### 1. Salvar contexto da sessão

Criar arquivo em `references/sessions/YYYY-MM-DD-{projeto}.md` com:

```markdown
# Sessão: {Nome do Projeto}

**Data:** YYYY-MM-DD
**Projeto:** {nome-pasta-ou-repo}
**Status:** Concluído / Em andamento

## O que foi pedido
- item 1
- item 2

## O que foi entregue
- descrição objetiva de cada entrega

## Aprendizados e Padrões Novos
### {Titulo do aprendizado}
**Causa/Contexto:** ...
**Solucao/Padrao:** ...
**Regra nova (se houver):** ...

## Arquivos alterados
- `caminho/arquivo.tsx`: descrição da mudança

## Referência do projeto
Ver: `references/projects/{nome-projeto}.md`
```

### 2. Atualizar (ou criar) o arquivo do projeto

Se o projeto já tem `references/projects/{nome}.md`, atualizar com:
- Novos componentes criados
- Novos padrões de animação usados
- Bugs encontrados e corrigidos
- Checklist de pendências atualizado
- Qualquer mudança nos brand tokens

Se o projeto NÃO tem arquivo ainda, criar com a estrutura completa (ver `references/projects/EXAMPLE.md` como template).

### 3. Atualizar a skill se surgiu algo novo

Se a sessão revelou um **anti-pattern novo**, **técnica nova** ou **correção de regra existente**:
- Adicionar ao arquivo correspondente em `references/` (ex: `animacoes-avancadas.md`, `visual-excellence.md`)
- Ou adicionar na seção `## Anti-Patterns` do SKILL.md
- Nunca deixar um aprendizado só na cabeça: registrar sempre.

### PROIBIDO entregar e não registrar

Cada sessão concluída sem registro e conhecimento perdido. O protocolo leva menos de 5 minutos e evita retrabalho em todas as sessões futuras.

---

---


## Índice: o que fica aqui vs o que carregar sob demanda

Neste arquivo (ver MAPA DESTE ARQUIVO, no topo): runbook, os 4 caminhos, porta única das skills de design, protocolo de ativação com pre-requisitos, gate de qualidade auxiliar, protocolo pos-sessao, regras inegociáveis, anti-patterns, os 5 gates, Steps 0 a 5 (com briefing 0.0, movimento 3.2b, identidade 4.2b e passe de gosto 4.2c), wave de auditoria, regras de deploy, blueprints, links e galerias.

**Este e o ÚNICO catálogo de `references/` do arquivo.** Se você procurou uma lista de referências no fim, ela não existe mais: estava duplicada e foi apagada.

**Scripts da skill (ficam em `scripts/`, não em `references/`):**

| Script | Para que |
|---|---|
| `scripts/screenshot-prova.js` | prova de entrega (desktop + mobile + clique) e **checagem de identidade da página** (4.2b). `--check` confere o Playwright, `--sem-identidade` só pra baseline de página de terceiro |
| `scripts/gate-responsivo.mjs` | 12 telas reais: overflow, CTA na dobra, toque 44px, corpo 14px, imagem distorcida (4.2d) |
| `scripts/wave.py` | registro das 8 lentes, AUDITOR MASTER (4.2e) e o CICLO de rodadas com critério de parada (4.2f) |
| `scripts/gate-classes-mortas.py` | acha classe de utilitário que existe no código e NÃO existe no CSS gerado: o build passa e o estilo nunca chega na tela (4.2c-bis) |
| `scripts/gate-oclusao.mjs` | acha texto COBERTO por camada decorativa ou CORTADO pela caixa, nas duas telas (4.2d) |
| `scripts/gate-video.mjs` | as 7 checagens de vídeo executáveis (razão por trilha, escala, corte, pôster, frames, LCP, reduced-motion). Sobe o Chromium do Playwright sozinho |
| `scripts/extrai-identidade.mjs` | extrai paleta real, vars CSS, h1/CTA e imagens de uma URL (caminho CLONAR) |
| `scripts/lado-a-lado.py` | monta original e sua versão lado a lado, mesma escala, pro gate do caminho CLONAR + ELEVAR |
| `scripts/search.py` + `data/` | banco de design: 50 estilos, 21 paletas, 50 font pairings, guidelines UX (indexado em inglês; traduz os termos comuns em português) |
| `scripts/assets-search.py` | fotos e vídeos (Pexels com chave, Openverse sem chave) |
| `scripts/higgsfield.py` | cliente da API Higgsfield: `--dry-run` monta a requisição sem gastar crédito, `--lote` gera a página inteira de uma vez (crédito não faz rollover), grava manifesto com seed e pôster com hash próprio |
| `scripts/github-search.py` | referências de template no GitHub (Step 0.5) |
| `scripts/servidor-gzip.py` | servir o build local COM compressão (medir sem gzip inverte o resultado) |

Carregar da pasta `references/` APENAS quando o caso pedir:

| Arquivo | Quando carregar |
|---------|-----------------|
| `references/preferencias-de-design.md` | OBRIGATÓRIO em toda página: gosto medido em correções reais (sem kicker em caixa alta, sem numeração 01/02/03 nem número gigante em card, foto de pessoa inteira e em moldura com identidade, imagem que casa com a seção, pricing limpa, botões rolam pra oferta, comparação lado a lado e assimétrica, bom em cor viva e ruim sem vermelho parado). Carregar ANTES do Step 2 |
| `references/mcp-workflow.md` | Workflow detalhado 21st.dev Magic + Google Stitch (prompts, exemplos, regras de uso) |
| `references/github-assets-search.md` | Busca de templates no GitHub e assets visuais (comandos completos, presets, setup Pexels) |
| `references/assets-sem-chave.md` | Assets SEM nenhuma API key: Openverse (foto real com licença CC), undraw, picsum, e como creditar o autor corretamente |
| `references/workflow-otimizacao.md` | Otimizar/upgrade de página existente (auditoria por severidade, upgrades por camada) |
| `references/workflow-pdf.md` | Clonar página a partir de PDF (mapeamento visual, paleta, implementação fiel) |
| `references/design-system.md` | Princípios de design, escala tipográfica, cores semânticas, gradientes, UX Nielsen |
| `references/shadcn-setup.md` | Setup e componentes shadcn/ui + CSS variables (stack React/Next) |
| `references/tailwind-patterns.md` | Padrões Tailwind: breakpoints, layouts, dark mode, v4.1 CSS-first |
| `references/magicui-quickstart.md` | Magic UI: componentes e exemplos rápidos (stack React) |
| `references/animacoes-epicas.md` | Scroll reveal, stagger, blur reveal, split text, spotlight, parallax, CSS-only |
| `references/landing-design.md` | Fórmulas above-the-fold, headlines, ordem de seções, CTAs, mobile, performance |
| `references/estruturas-alto-impacto.md` | Templates prontos: heros, títulos, botões, mockups, dividers, features, stats, testimonials |
| `references/glassmorphism.md` | Glass cards: base, variantes e quando NÃO usar |
| `references/acessibilidade.md` | WCAG 2.1 AA: contraste, focus, screen readers, movimento |
| `references/checklist-pre-entrega.md` | Checklist auxiliar de build (a wave do Step 4 e o portão; isto ajuda a chegar limpo nela) |
| `references/background-video.md` | Sistema de camadas de vídeo de fundo (z-index, isolation, overlays) |
| `references/google-workspace.md` | Google Docs/Sheets/Drive (requer scripts locais NÃO inclusos no repo) |

### Referências especializadas (auditoria e qualidade)
- `references/audit-agents.md`: wave adversarial de 8 lentes + síntese + auditor master (Step 4)
- `references/scoring-system.md`: rubrica 0-10 por dimensão
- `references/strategist-audit.md`: auditoria Hook/Story/Offer
- `references/anti-vibe-coding.md`: 5 sinais de substância + 15 tells VISUAIS de IA
- `references/taste-gate.md` e `references/design-laws.md`: gosto e bans absolutos
- `references/page-types.md`: decision tree de classificação da página
- `references/psychological-triggers.md`, `cta-placement-map.md`, `social-proof-hierarchy.md`, `urgency-scarcity-patterns.md`, `trust-signals-placement.md`
- `references/typography-scale.md`, `section-transitions.md`, `animation-audit.md`, `desktop-layout-rules.md`, `mobile-checklist-detailed.md`
- `references/visual-assets.md`, `visual-excellence.md`, `visual-references.md`, `efeitos-avancados.md`, `animacoes-avancadas.md`, `magicui-components.md`
- `references/nanobanana-mockup-carousel.md`, `veo-video-workflow.md`, `ai-video-generation.md`, `pdf-to-page.md`, `post-launch.md`
- `references/higgsfield.md`: SETUP da CLI (conta, login, skills, `workspace set`), rota Higgsfield pra movimento e b-roll (Step 3.2b), as 5 regras de vídeo em página e as lições de composição medidas (conta do véu, contraste de texto sobre vídeo, cartão opaco escondendo o clipe)
- `references/ui-reference.md`, `official-ui-reference.md`, `reference.md`, `learn.md`, `chart.md`: shadcn/Tailwind (stack React/Next)



## Processo de 6 Steps: Workflow Principal

**ESTE E O WORKFLOW DO CAMINHO 1 (CRIAR do zero).** Para CLONAR, MELHORAR ou EDITAR, ver "CAMINHOS DE EXECUÇÃO": os fluxos são outros e os gates mudam. No caminho CRIAR, os 6 steps são sequenciais e nenhum pode ser pulado. Copy vem antes de design. Design vem antes de código.

Tempo estimado: 80-120 minutos do material até página live.

**Constraint global:** Velocidade (LCP < 2.5s) governa TODA decisão desde o Step 0. Não é um item de checklist, e um filtro permanente. Se uma animação, imagem ou feature compromete o LCP, ela SAI.

---

### PROTOCOLO DE EXECUÇÃO OBRIGATÓRIO: PARADA FORÇADA ENTRE STEPS

**CADA STEP TERMINA COM UMA PARADA. EU NÃO AVANÇO SEM CONFIRMAÇÃO DO USUÁRIO.**

**Escopo desta regra:** ela só vale nos caminhos CRIAR, CLONAR e MELHORAR. No caminho EDITAR (mudança pontual) NÃO existe parada entre steps: executa o escopo travado, testa regressão, publica e mostra a prova. Ver "CAMINHOS DE EXECUÇÃO".

Não importa a urgência, não importa o tamanho do material, não importa que o próximo step seja "óbvio". Cada step e uma resposta separada. O usuário lê, aprova ou corrige, e SÓ ENTÃO o próximo step começa.

**EXCEÇÃO (única): execução nao-interativa.** Se a sessão não permite confirmação do usuário (subagente, wave, automação agendada) OU o usuário pediu explicitamente execução direta ("faz direto", "sem parar", "de ponta a ponta"), NÃO parar entre steps. Nesse modo: executar cada GATE normalmente, registrar o output completo de cada step na resposta final (blueprint, copy lock, direção visual, scores) e listar as decisões que o usuário deveria ter aprovado, para revisão a posteriori. A exceção dispensa a PARADA, nunca o GATE.

```
FORMATO OBRIGATÓRIO ao final de cada step:

---
## [OK] Step X concluído: [NOME DO STEP]

[OUTPUT COMPLETO DO STEP, blueprint / direção visual / checklist / etc]

GATE X:
- [x] item 1
- [x] item 2
- [x] item N

**Posso avançar para o Step Y (NOME)?** Confirme ou me diga o que ajustar.
---
```

> A ENTREVISTA DE BRIEFING (rodada 1 para todos, rodada 2 só para quem já tem cliente) não mora
> aqui: ela é a primeira coisa do Step 0, na subseção **0.0 BRIEFING**. Esta seção trata só de
> quando parar entre steps.

**PROIBIDO** executar Step 1 na mesma resposta que Step 0.
**PROIBIDO** executar Step 2 na mesma resposta que Step 1.
**PROIBIDO** executar Step 3 na mesma resposta que Step 2.
**PROIBIDO** executar qualquer step sem ter apresentado o output do step anterior E recebido confirmação do usuário.
**PROIBIDO** escrever código (Step 3) sem ter a copy travada (Step 1 concluído).
**PROIBIDO** fazer direção visual (Step 2) sem ter a copy aprovada (Step 1 concluído).

Se o output do step não foi escrito na resposta + pergunta de confirmação não foi feita → o step NÃO foi executado.

### ROTA EXPRESSA (capture simples e páginas triviais)

Para capture page simples (< 3 telas, formulário + headline) ou página explicitamente trivial/descartavel, o processo colapsa SEM perder os gates:

1. **Steps 0-2 em UMA resposta:** blueprint + copy lock + direção visual apresentados juntos, com os 3 gates checados inline (uma única parada de confirmação, ou nenhuma no modo nao-interativo).
2. **Step 3 normal** (as regras inegociáveis continuam valendo).
3. **Step 4 com as oito lentes registradas no `wave.py`:** a rota expressa reduz a apresentação, não a cobertura da auditoria. O bloco de veredito na entrega continua OBRIGATÓRIO.

O que a rota expressa NÃO dispensa: **as seis respostas da rodada 1 do briefing (0.0: nicho, local, público, oferta, preço, ação)**, copy antes de código, identidade real quando indicada, assets críticos confirmados (incluindo o destino do lead), identidade da página (4.2b), passe de gosto (4.2c) e o BLOCO OBRIGATÓRIO DA ENTREGA completo. O que ela colapsa e a APRESENTAÇÃO dos steps, nunca a entrevista nem os gates.

### REGRAS INEGOCIÁVEIS: LER ANTES DE QUALQUER PÁGINA

**PROIBIDO INVENTAR ID VISUAL QUANDO HÁ UMA INDICADA.** Se o usuário forneceu ou apontou a identidade (pasta de assets, arquivo de logo, paleta, tipografia, link, PDF, slides, marca existente), e OBRIGATÓRIO usar o asset REAL: o logo oficial (extrair/baixar e usar a imagem), as cores exatas, as fontes indicadas. PROIBIDO recriar o logo em texto/SVG aproximado, chutar paleta ou trocar fonte por "parecida". Se o logo oficial ficar ilegível no tamanho de uso, aumentar/ajustar o tamanho ou pedir uma versão, NUNCA substituir por uma invenção. Criar identidade do zero só quando NÃO há nenhuma indicada. Falha real: num projeto com ID definida o logo oficial foi trocado por um wordmark inventado, o usuário teve que cobrar.

**PROIBIDO PULAR STEPS.** Cada step tem um GATE, uma entrega obrigatória que DEVE existir antes de avançar. Se o gate não foi cumprido, PARE e volte. Não importa a urgência.

**PROIBIDO BUILDAR SEM COPY TRAVADA.** Copy (Step 1) DEVE estar escrita, aprovada e "frozen" antes de qualquer código ou design. Design sem copy = design que vai mudar. Código sem copy = retrabalho garantido. A ordem e: copy first, design second, code third.

**MCP conectado, PROIBIDO não usar** (se ausente, fallback do Step 0): construir componente UI do zero sem consultar o 21st.dev; iniciar código de página nova sem wireframe no Stitch; usar logo de marca sem buscar no `logo_search`. Com o MCP disponível, pular = visual inferior e retrabalho. Sem o MCP, seguir pelo fallback documentado (componente a mão, layout direto, SVG oficial/vetorial).

**PROIBIDO HTML/CSS PURO para páginas de venda, mentoria ou high-ticket.** HTML puro = página feia, sem animações, sem componentes profissionais, sem o "tcham" visual. SEMPRE usar React + Vite (ou o framework do projeto existente) para ter acesso a: Framer Motion, shadcn/ui, Magic UI, Tailwind compilado, componentes reutilizáveis. Exceções, com stack definida na tabela DECISÃO DE TECH STACK: capture pages simples (2-3 telas, formulário + headline) e **serviço local / agendamento** (estúdio, clínica, consultório: HTML + Tailwind compilado, sem React, movimento em CSS). "HTML puro" aqui quer dizer sem Tailwind compilado e sem sistema; HTML + Tailwind compilado não é HTML puro.

**PROIBIDO BUILDAR SEM DIREÇÃO VISUAL.** Ir direto do PDF pro código produz páginas "funcionais mas feias". Antes de escrever a primeira linha de código, DEVE existir: paleta definida (10-15 vars), font pairing escolhido, layout de CADA seção desenhado, lista de assets necessários.

**PROIBIDO ENTREGAR SEM ASSETS VISUAIS.** Páginas com SVGs genéricos e fundos sólidos não impressionam. DEVE ter: textura/profundidade nos fundos, foto/mockup/video real, animações de scroll, efeitos de hover, pelo menos 1 elemento "wow" por scroll. **Catálogo de "wow" PERMITIDO** (não dispara os tells de IA): foto real tratada, mockup de produto, vídeo de fundo bem integrado, number ticker, marquee de logos/depoimentos, parallax sutil, noise/pattern discreto, transição de seção trabalhada, micro-interacao no CTA. **PROIBIDO usar como "wow":** blob de glow desfocado, aurora atrás de conteúdo, glow colorido em botão, glassmorphism generalizado, floating orbs, gradient-clip em título, shimmer decorativo: estes são tells visuais de IA (V1-V15 de `references/anti-vibe-coding.md`) e REPROVAM na wave do Step 4. Se o usuário não forneceu foto e não há API de stock/geracao disponível: usar monograma/ilustracao funcional, REGISTRAR como pendência na entrega e pedir o asset real; isso não bloqueia a entrega, bloqueia RODAR TRÁFEGO. **Antes de cair nisso, use a rota sem chave:** `python3 scripts/assets-search.py "<tema em ingles>" --type photo` devolve foto real da Openverse sem nenhuma API key (crédito obrigatório). Retângulo vazio no hero não é mais aceitável.

### ANTI-PATTERNS DE PROCESSO E DE IA: O QUE DEU ERRADO E NUNCA PODE REPETIR

> Esta lista e a de PROCESSO e cara de IA. A lista de CÓDIGO e CSS esta na seção
> "Anti-Patterns de código (NUNCA FAÇA)", perto do fim do arquivo. São duas, e as duas valem.

| Anti-Pattern | O que acontece | Solução |
|-------------|---------------|---------|
| Pular Step 1 (COPY & MENSAGEM) | Copy genérica, design que não casa com a mensagem, retrabalho garantido | SEMPRE escrever e aprovar copy ANTES de qualquer design ou código |
| Design sem copy travada | Copy muda → design muda → código muda → 3x o trabalho | Copy Lock obrigatório: copy frozen antes de avançar |
| Pular Step 2 (DIRECIONAR) | Página sem identidade visual, cores aleatórias, sem ritmo | SEMPRE definir tokens + layout por seção ANTES de codar |
| HTML/CSS puro em página high-ticket | Sem animações, sem componentes, parece template grátis | SEMPRE React + Vite + Framer Motion + shadcn/ui |
| SVGs básicos como "design" | Página parece protótipo, não produto final | Hugeicons como primário em landing (Lucide só pra UI/dashboard). PROIBIDO o par "caixinha arredondada com fundo tingido + glifo abstrato": e o tell número 1 do passe de gosto (4.2c) |
| Fundos sólidos sem textura | Visual flat e sem profundidade | Adicionar noise, gradientes sutis, patterns, overlays |
| Zero animações de scroll | Página estática e sem vida | Scroll reveal nas secoes-CHAVE: 2 a 4 por página, no máximo 1 por seção. Em TODO elemento e vibe-coding e reprova na wave |
| Não criar assets visuais | Seções vazias, sem impacto | Buscar/gerar fotos, vídeos, mockups, ilustrações DURANTE o build |
| Formato carta no desktop | Parece documento Word, não página de venda | NUNCA coluna única centralizada em high-ticket (ver desktop-layout-rules.md) |
| Clonar e inventar identidade nova | Cliente quer a marca dele; paleta/logo inventados = retrabalho garantido | Ao CLONAR site real: manter identidade original. Extrair cores exatas via `getComputedStyle` no navegador, baixar o LOGO REAL do site (nunca recriar). Só reinventar se pedido explícito |
| Foto de produto (fundo branco) sobre superfície escura/colorida | Vira "caixa branca" recortada = cara de IA na hora | Foto com fundo branco SÓ em card/superficie branca ou clara (encaixa invisível). Em dark, precisa de remoção de fundo real, nunca colar por cima |
| Tells visuais de IA (mono kicker, "01" gigante, blob glow, stats no hero, preço mono, ENTER na busca) | "Cara de vibecoding/template SaaS" | Rodar o checklist `anti-vibe-coding.md` seção "Tells VISUAIS de IA" ANTES de entregar. Referência de bonito = concorrente do nicho, não Dribbble |
| Kicker uppercase abrindo seção, numeração 01/02/03 ou número gigante decorativo em card, figcaption-pilula sobre foto | Reprovados em correção real como "cara de IA", com retrabalho de página inteira (31/08/2026 e 02/10/2026) | Seção abre no título; card sem número; foto sem pílula. Vale pra toda página: `references/preferencias-de-design.md`; o `gate-sem-kicker.py` cobra os três primeiros |
| Foto/banner com crop que decapita a pessoa ou esconde a cena | "Ficou estranho pra caralho": o crop valia pelo arquivo, não pela janela | Conferir TODO crop pela janela renderizada; preferir split com foto inteira a banner cortado |
| Conectar 21st.dev / Stitch e não usar | Burla a regra "PROIBIDO componente sem 21st" só registrando o MCP | Usar de fato: 21st builder/inspiration por componente; Stitch as vezes só devolve design system (tela trava): nesse caso documentar e usar os tokens |
| Tratar e-commerce/varejo home como sales page | Copy lock, oferta, value stack, checkout, vídeo por seção não se aplicam a vitrine de loja | E-commerce home = identidade real + cards com estrelas/avaliacao + nav por categoria/genero + grid de marcas + cupom 1a compra + trust strip. Pular Steps de copy/oferta de high-ticket |
| Framer `whileInView` + `once:true` travando em opacity 0 | Seção inteira fica INVISÍVEL se o observer não dispara | Usar `useInView` + fallback `setTimeout(()=>setForced(true), 1400)` que força visível. Nunca deixar opacity 0 final sem garantia |

### GATES OBRIGATÓRIOS ENTRE STEPS

**Estes gates são do caminho CRIAR.** Os outros caminhos tem gate próprio, descrito em
"CAMINHOS DE EXECUÇÃO": CLONAR troca os gates 1 e 2 pelo **gate de fidelidade** (original e clone lado
a lado) e fecha no GATE 4 normal; MELHORAR fecha no GATE 4 **mais** o **gate de melhoria**
(antes e depois com nota por dimensão, e nenhuma dimensão pode ter piorado), que é um gate
ADICIONAL de nao-regressao, não um substituto; EDITAR fecha no **checklist de regressão + prova
do ponto alterado**, e só ele dispensa a wave. Exigir COPY LOCK num clone ou wave de 8 lentes numa troca de headline não é
rigor, e processo errado: o gate tem que caber no que foi pedido.

```
STEP 0 (ENTENDER & INVENTARIAR) ────────────────────────────
  GATE 0: checar-ferramentas.py rodado (ferramentas críticas aprovadas pelo verificador) + As SEIS respostas da rodada 1 (0.0) registradas, cada uma marcada como resposta do
          usuário ou SUPOSIÇÃO + classificação + mapa de seções + flags de copy + inventário
          de assets documentados?
  [ ] SIM → avança pro Step 1
  [ ] NÃO → PARA. Completa o Step 0 primeiro.

STEP 1 (COPY & MENSAGEM) ───────────────────────────────────
  GATE 1: VoC minerado + Before/After Grid + hierarquia de mensagens + copy de CADA seção escrita + COPY LOCK declarado?
  [ ] SIM → avança pro Step 2
  [ ] NÃO → PARA. NENHUM design sem copy aprovada. Nunca.

STEP 2 (DIRECIONAR) ────────────────────────────────────────
  GATE 2: Paleta CSS + font pairing + layout de CADA seção + lista de assets definidos?
  [ ] SIM → avança pro Step 3
  [ ] NÃO → PARA. Não escreva uma linha de código sem direção visual.

STEP 3 (BUILDAR) ───────────────────────────────────────────
  GATE 3: Todas seções construídas com assets reais + animações + layout desktop rico +
          decisão de MOVIMENTO declarada (quais blocos ganharam movimento e por que os
          outros não ganharam, ver 3.2b)?
  [ ] SIM → avança pro Step 4
  [ ] NÃO → PARA. Volte e complete o que falta. Página incompleta = página feia.

STEP 4 (VERIFICAR & SHIPAR) ────────────────────────────────
  GATE 4: Auditoria Designer (notas declaradas, ciclo 4.2f aprovado) + Auditoria Estrategista (notas declaradas,
          ciclo 4.2f aprovado) + QA checklist 100% (Lighthouse 90+ quando houver navegador; sem ele,
          pendência declarada) + consistência de contato conferida dígito por dígito + diff de
          claims feito + IDENTIDADE DA PÁGINA (4.2b, conferida pelo script) + PASSE DE GOSTO
          rodado (4.2c) + **gate-sem-kicker.py passou** (toda página sai sem kicker em caixa alta e sem número decorativo;
          roda `python3 <dir-da-skill>/scripts/gate-sem-kicker.py <arquivo.html|dist/>`) + deploy funcionando
          (ou, na entrega SEM deploy, servidor local com o deploy declarado como pendência) + PROVA DE ENTREGA 4.5
          (screenshots desktop/mobile LIDOS + interação principal testada)?
  [ ] SIM → avança pro Step 5 (monitoramento)
  [ ] NÃO → PARA. Corrige antes de entregar. Sem exceções. Verificação quebrada = entrega bloqueada, nunca "entrego sem prova".
```

### DECISÃO DE TECH STACK (decidida no Step 2, item 2.5; o tipo de página sai do Step 0, item 0.2)

| Tipo de página | Tech Stack | Justificativa |
|---------------|-----------|---------------|
| Sales page (mid/high-ticket) | React + Vite + Framer Motion + shadcn/ui + Tailwind | Precisa de animações, componentes ricos, visual premium |
| Challenge / Desafio | React + Vite + Framer Motion + Magic UI + Tailwind | Precisa de energia visual, countdowns, efeitos |
| Capture page simples (< 3 telas) | HTML + Tailwind compilado | Simples o suficiente, velocidade máxima |
| Serviço local / agendamento (estúdio, clínica, consultório) | HTML + Tailwind compilado, sem React | Uma ação (agendar), sem checkout nem oferta empilhada; movimento em CSS. Template em `references/page-types.md` |
| Página institucional | React + Vite + Framer Motion + shadcn/ui | Profissionalismo visual obrigatório |
| Rota em projeto existente (ex.: site que já roda em React) | Mesmo framework do projeto (React/Vite) | Consistência, reuso de componentes |

**Se o projeto destino JÁ usa React, a nova página DEVE ser uma rota React, não um HTML avulso.**

---

## Step 0: ENTENDER & INVENTARIAR (5-10 min)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 0 --arquivo evidencias/etapa-0.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

Recebe o material do usuário e extrai tudo que precisa ANTES de tocar em copy, design ou código.

### 0.0-PRE FERRAMENTAS: rodar o verificador ANTES de qualquer coisa

```bash
python3 <dir-da-skill>/scripts/checar-ferramentas.py
```

**Este e o primeiro comando da skill, antes até da entrevista de briefing.** Ele não pergunta se
a ferramenta esta configurada: ele MANDA cada uma fazer alguma coisa e confere se voltou. Sai
com código diferente de zero quando falta crítico.

**Por que existe (26/08/2026, custou meses sem ninguém perceber):** o MCP do 21st.dev estava
configurado e MORTO havia tempo indeterminado (`Not authenticated: your API key is missing or
was reset`). A skill mandava "buildar com componentes do 21st.dev OU a mão", o MCP nunca
respondia, e ela caia no "a mão" TODA VEZ. O Stitch estava no mesmo estado (proxy de pé, tools
com timeout), então as DUAS camadas visuais da skill estavam desligadas. O dono percebeu pelo
RESULTADO ("o design não ta interessante, pouca coisa e usada do 21st.dev"), não por erro
nenhum, porque **fallback silencioso não reclama**.

A detecção antiga era "a tool `mcp__magic__*` aparece na lista?". Aparecia. E estava morta.
**Estar na lista não é verificação.** Verificação e mandar fazer e conferir o retorno.

**E o teste tem que exercitar a CREDENCIAL, não só a conexão** (o do 21st.dev faz uma busca real de componente com a chave de `TWENTYFIRST_API_KEY`; sem a chave no ambiente ele sai como opcional ausente, nunca como verde). Um MCP passou verde neste
verificador e devolveu `HTTP 401 (invalid authentication credentials)` na primeira chamada
real da sessão. O ping alcançava o servidor; o que faltava era a chave, e nada no teste
usava a chave. Ferramenta que responde ao ping e falha na chamada real e PIOR que
ferramenta ausente: a ausência e declarada e vira fallback consciente, essa e descoberta
pelo resultado, tarde. Todo teste de ferramenta com credencial precisa fazer uma chamada
que a USE (listar, buscar, ler algo).

**O que fazer com o resultado:**

| Resultado | Ação |
|---|---|
| Tudo respondendo | Segue pro 0.0 (entrevista de briefing) |
| **Crítico sem responder** | **PARA.** Conduza a pessoa pela correção (abaixo). Não comece a página. |
| Só opcional degradado | Segue, e DECLARE a degradação na entrega |

**CONDUZIR, não avisar.** Quando faltar algo, não diga "você precisa configurar o 21st.dev":
abra a página, de o comando pronto e espere a chave. A pessoa que esta usando a skill quase
sempre não sabe o que é um MCP.

| Ferramenta | Como conduzir |
|---|---|
| **21st.dev (magic), opcional** | Só se a pessoa quiser. Abra `https://21st.dev/mcp`, peça a chave, e rode: `claude mcp add --transport http 21st https://21st.dev/api/mcp --scope user --header "x-api-key: SUA_CHAVE"` e `export TWENTYFIRST_API_KEY=SUA_CHAVE`. Avise que as tools novas só aparecem na próxima sessão. Sem chave: componente a mão em Tailwind. |
| **Playwright** | `npm i -g playwright && npx playwright install chromium` (baixa ~265 MB; a versão leve e `--only-shell`, ~94 MB) |
| **Higgsfield** | Setup completo em `references/higgsfield.md`, seção SETUP (inclui o `workspace set`, que trava todo mundo) |
| **Stitch** | Proxy local. Timeout costuma ser conflito de porta: confira quem esta na porta antes de reiniciar |
| **ffmpeg** | `brew install ffmpeg` |

**Regra que nasceu daqui, e vale pra qualquer ferramenta que a skill venha a usar:** toda
dependência nova precisa entrar no `checar-ferramentas.py` com um teste que a EXERCITA. Se você
não conseguir escrever esse teste, a dependência não entra na skill: sem teste, ela vai morrer
em silêncio e degradar o resultado sem avisar ninguém.

---

### 0.0 BRIEFING: entrevista de 2 rodadas (logo depois do verificador de ferramentas)

**Desvio:** se o usuário já chegou com doc, PDF, briefing fechado ou copy pronta, NÃO abra a
entrevista inteira. Va para o 0.1, leia o material e use a entrevista só para o que ficou em
branco (tipicamente preço, destino do lead e ação esperada).

**EXTRAIA o básico primeiro. Pergunta simples, que qualquer um responde.**

O pedido real chega assim: *"cria uma página pra mim de uma academia"*. Só isso. NÃO responda
com "qual o seu publico-alvo e qual a dor dele?": isso é vocabulário de marqueteiro, e quem tem
academia responde "todo mundo que quer emagrecer", que não serve pra nada. E NÃO pergunte sobre
cliente antigo logo de cara: muita gente ainda não abriu o negócio e trava na primeira pergunta.

**RODADA 1, o básico. Mande as perguntas juntas, numa lista curta, pra pessoa responder de uma
vez.** São todas de fato, sem interpretação. **Troque os exemplos entre parênteses pelos do
nicho do pedido**: exemplo de academia numa consultoria jurídica soa automático e desanima.

1. **Qual é o nicho, exatamente?** (academia, só musculação, crossfit, pilates, funcional)
2. **Onde você atende?** (cidade e bairro, ou online)
3. **Atende quem?**
   - cliente final PESSOA: mulheres, homens, os dois; e a faixa de idade, se souber
   - cliente final EMPRESA (B2B): porte, segmento e quem decide a compra (cargo). Gênero e
     idade são o eixo errado aqui é devolvem resposta inútil
4. **O que você vende?** (plano mensal, aula avulsa, pacote fechado, avaliação)
5. **Quanto custa, mais ou menos?**
6. **O que você quer que a pessoa faça nessa página?** (agendar aula, chamar no WhatsApp,
   comprar direto, deixar o contato)

Com essas seis já da pra escrever copy que aponta pra alguém. Nicho + cidade + gênero + faixa
etária já é um público; oferta + preço + ação já é uma página.

**CRITÉRIO DE ACEITE (resposta presente não é resposta útil).** Antes de dar a rodada 1 por
respondida, conferir:
- **nicho** só vale com o que + pra quem + resolvendo o que ("consultoria" não vale;
  "consultoria de folha de pagamento pra indústria de pequeno porte" vale)
- **público** só vale com pelo menos um atributo além de "empresas" ou "todo mundo"
- **oferta** só vale com formato e recorrência (mensal, avulso, pacote, projeto fechado)
- **ação** só vale com o destino nomeado (qual WhatsApp, qual formulário, qual checkout)

Reprovou em alguma? Não mande a pergunta aberta de novo: devolva **2 ou 3 opções concretas** pra
pessoa escolher ("e mais pra A, B ou C?").

**RODADA 2, só SE a pessoa já atende gente.** Pergunte: *"você já tem cliente hoje?"*. Se sim,
estas quatro rendem muito, porque devolvem material que não da pra inventar:

- **"Me conta o último cliente que fechou: quem era e o que trouxe ele até você?"** (a persona
  real, quase sempre mais específica que a imaginada)
- **"O que ele te falou quando chegou? Se lembrar da frase, melhor."** (voz do cliente verbatim,
  vira headline. Anote com as palavras DELA, sem traduzir pro seu vocabulário)
- **"Quem procura você e você percebe que não é pra você?"** (o anti-publico afia a mira mais
  rápido que descrever o público certo; vira a seção "para quem NÃO é")
- **"O que essa pessoa já tinha tentado antes, e por que não deu certo?"** (devolve a objeção
  real e o diferencial, sem você inventar nenhum dos dois)

Se a pessoa ainda NÃO tem cliente, pule a rodada 2 sem drama e siga com as seis primeiras.
**Registre a flag `sem prova social` no output do Step 0**: ela viaja com o projeto e muda o
gate do Step 4 (ver 4.0b, dimensão Prova Social). Nunca transforme a entrevista em
interrogatorio: e melhor uma página boa com seis respostas do que nenhuma página porque a
pessoa cansou de responder.

**Se travar ou responder genérico, NÃO repita a pergunta.** Ofereça um palpite pra ela reagir:
*"Pelo que costuma acontecer em academia de bairro, e gente de 30 a 50 que já tentou treinar
sozinha e desistiu, e o que trava e não saber começar sem se machucar. E por ai, ou o seu caso
e outro?"*. Gente e muito melhor em CORRIGIR do que em CRIAR do zero, e um palpite errado rende
mais que uma pergunta aberta.

**ONDE O PALPITE E PROIBIDO.** Palpite serve pra nicho, público, dor, objeção e anti-publico:
campos de interpretação, que a pessoa corrige em dois segundos. **NUNCA palpite preço, garantia,
número de alunos, resultado, prazo, data ou depoimento.** Esses são fato, e palpite aceito por
silêncio vira dado inventado na página (proibido pelo QA 4.2, item "ZERO dado inventado"). Sem
confirmação: deixar em branco, registrar como pendência do usuário e NÃO deixar aparecer na
página até ser confirmado.

**Resposta pela metade** (respondeu 4 das 6, ignorou 2): não reenvie a lista inteira nem repita
tudo. Devolva **só as que faltam**, numa única mensagem curta, já com palpite pra pessoa apenas
confirmar ou corrigir.

**Regra de parada:** só avance com as seis da rodada 1 respondidas e aprovadas no critério de
aceite. Sem público e oferta definidos na largada, a página inteira nasce apontando pra ninguém,
e o retrabalho custa a página toda, não um parágrafo.

**Modo nao-interativo** (subagente, automação, ou o usuário pediu "faz direto"): não existe
ninguém pra responder, então NÃO trave. Preencha com palpite derivado do pedido as CINCO de
interpretação (nicho, local, público, oferta, ação), marque cada uma como `SUPOSICAO` no output
do Step 0 e liste na entrega as que precisam de confirmação. **A pergunta 5 (preço) e fato e NÃO
se palpita:** fica registrada como PENDENTE, a página sai sem número de preço e o CTA leva pra
conversa. A exceção dispensa a PARADA, nunca o registro: seguir em silêncio com suposição e que
é proibido.

Diferença medida em página real (demo de pilates, 25/08/2026): o pedido trazia nicho, público,
faixa etária e objetivo, e o resultado foi a headline "Pilates para quem sente dor nas costas e
nunca pisou num estúdio", as três objeções reais na seção "isso parece com você", e o FAQ que
ataca "tenho mais de 50 anos, ainda da tempo?". Nada disso sai de um briefing que diz só
"academia".

### 0.1 Ler o Material
- Se PDF: `Read file_path="/caminho/do/arquivo.pdf"` (todas as páginas)
- Se Google Doc / Sheet: **requisito externo, NÃO vem neste repo.** Os scripts
  `~/.claude/scripts/google-api.sh` e `google-oauth-capture.py` precisam estar instalados e
  autenticados na máquina (ver `references/google-workspace.md`). Existindo:
  `bash ~/.claude/scripts/google-api.sh doc <DOC_ID>` e
  `bash ~/.claude/scripts/google-api.sh sheet <SHEET_ID> "Aba"`.
  **Não existindo (caso da maioria das máquinas): pedir ao usuário o texto colado ou o PDF
  exportado.** Nunca ficar tentando rodar um script que não está instalado.
- Se texto direto: ler a mensagem do usuário

### 0.2 Classificar a Página
Usar a decision tree de `references/page-types.md`:

**Perguntar/detectar:**
1. **Tipo:** sales-page, capture, challenge, vsl, institutional, checkout-bridge, thank-you, servico-local (estudio, clinica, consultorio: a acao e agendar)
2. **Faixa de preço:** free, low-ticket (R$7-97), mid-ticket (R$197-997), high-ticket (R$1.000+)
3. **Tom:** premium, urgente, educacional, pessoal, energia
4. **Temperatura:** fria (página longa), morna (média), quente (curta)

**Output da classificação:**
- Se high-ticket + sales-page → layout desktop rico OBRIGATÓRIO (nunca formato carta)
- Se capture/vsl → formato centrado OK
- Se challenge → dark mode + energia
- Consultar `references/page-types.md` para template de seções

### 0.3 Mapear Seções
Listar cada seção do material:
```
SEÇÃO 1: Hero, "Headline exata", CTA: "Texto do botão"
SEÇÃO 2: Social Proof, 4 números
SEÇÃO 3: Problema, 3 dores listadas
...
```

### 0.4 Avaliar a Copy
Não apenas extrair, AVALIAR:
- Headlines fortes ou genéricas? (Flaggar se fracas)
- CTAs claros com verbo de ação + benefício?
- Oferta empilhada com ancoragem de preço?
- Social proof presente e específica (números, nomes)?
- Copy no nível de leitura 5a-7a série? (simplificar se muito complexa)

### 0.5 Puxar Referências
Buscar 3 páginas de referência do nicho como benchmark visual:
```bash
python3 <dir-da-skill>/scripts/github-search.py "<tipo-pagina>" --stars 50
```
Ou buscar manualmente páginas de concorrentes/referencia que o usuário mencionar.

### 0.6 Contexto de Funil
Identificar:
- **De onde vem o tráfego?** (Meta Ads, orgânico, email, WhatsApp)
- **O que vem depois?** (checkout, grupo WhatsApp, email sequence)
- **Message match:** headline da página deve ecoar a promessa do anúncio

### 0.7 Inventário de Conteúdo

Confirmar AGORA o que existe e o que precisa ser criado/buscado:

```
ASSETS EXISTENTES:
- Logo: [ ] SIM (onde?) / [ ] NÃO
- Foto do mentor/produto: [ ] SIM (onde?) / [ ] NÃO
- Depoimentos com foto: [ ] SIM (quantos?) / [ ] NÃO
- Vídeo (VSL/pitch): [ ] SIM (URL?) / [ ] NÃO
- Screenshots/resultados: [ ] SIM / [ ] NÃO

ASSETS A CRIAR:
- Fotos: [ ] buscar Pexels / [ ] gerar IA / [ ] usuário fornece
- Ícones: [ ] Lucide / [ ] Heroicons / [ ] custom SVG
- Mockups: [ ] necessário? / [ ] tipo: phone / laptop / dashboard
- Vídeo de fundo: [ ] necessário? / [ ] buscar Pexels

DESTINO DO LEAD/VENDA (asset crítico número 1 de capture/sales):
- Form de captura: endpoint/CRM/webhook? URL: ___________
- Checkout: link Hotmart/Kiwify/Stripe? URL: ___________
- WhatsApp/grupo: numero/link? ___________

CHECKPOINT FUNIL:
- De onde vem o tráfego? ___________
- O que vem depois desta página? ___________
- Qual a promessa do anúncio? (para message match) ___________
```

Se assets críticos estão em falta (destino do lead/checkout, foto do mentor, depoimentos, preço final) → **PAUSAR e perguntar o usuário antes de avançar** (em modo nao-interativo: seguir com placeholder EXPLÍCITO, ex. `data-endpoint=""` + comentário TODO, e declarar na entrega que a página NÃO pode receber tráfego até o destino ser plugado). **PROIBIDO** entregar form que mostra sucesso sem enviar o lead SEM declarar isso em destaque na entrega.

Se o usuário NÃO tem fotos e não há API de stock/geracao: monograma/ilustracao funcional + pendência registrada na entrega (não bloqueia entrega; bloqueia rodar tráfego).

### Output do Step 0
Blueprint documentado com:
- **As seis respostas da rodada 1 (0.0)**, escritas na resposta, cada uma marcada como
  `resposta do usuario` ou `SUPOSICAO` (modo nao-interativo)
- **Flags do briefing:** `sem prova social` (quando a pessoa ainda não tem cliente) e a lista
  de campos de fato que ficaram em branco (preço, garantia, números, datas)
- Classificação (tipo + preço + tom + temperatura)
- Mapa de seções
- Flags de copy (o que precisa melhorar)
- 3 URLs de referência
- Contexto de funil
- Inventário de assets (o que existe vs o que precisa criar)

**>>> GATE 0: checar-ferramentas.py rodado (ferramentas críticas aprovadas pelo verificador) + As seis respostas da rodada 1 (0.0) registradas (resposta do usuário ou SUPOSIÇÃO declarada) + blueprint + inventário de assets documentados por escrito? Assets críticos existem ou há plano para obtelos? Se NÃO, PARA AQUI. <<<**

**PARADA OBRIGATÓRIA:** Apresentar o blueprint completo ao usuário e perguntar: "Step 0 concluído. Posso avançar para o Step 1 (COPY & MENSAGEM)?", NÃO AVANÇAR SEM RESPOSTA.

---

## Step 1: COPY & MENSAGEM (10-20 min)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 1 --arquivo evidencias/etapa-1.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

**O step mais crítico do processo.** Copy define o que vai ser construído. Design serve a copy, não o contrário. Nenhum pixel antes de copy aprovada.

### 1.0 De onde vem a copy? (decidir primeiro)

Antes de produzir qualquer copy, checar o que o usuário já trouxe:

- **Já chegou com a copy pronta** (texto, doc, briefing fechado): NÃO gerar do zero.
  Apenas validar (checklist 1.5), organizar na hierarquia (1.3) e travar (1.6 COPY LOCK).
- **Chegou sem copy, ou com copy fraca/incompleta:** produzir a copy seguindo 1.1 a 1.4.
  Aqui, **opcionalmente**, acionar a skill `copy-pagina-vendas` (frameworks Brunson/Hormozi/
  Schwartz) para gerar a copy de venda, e o construtor transforma o resultado em página.
- **Serviço local / agendamento** (estúdio, clínica, consultório: página com UMA ação, agendar,
  e sem oferta empilhada): use o modelo curto `references/copy-servico-local.md` (headline,
  subtítulo, 3 dores, mecanismo, como agendar, formas de atender, dúvidas, chamada final). A
  `copy-pagina-vendas` não serve aqui: o modo Clássico e pra venda acima de R$ 297 e o modo
  Desafio e pra evento.
- **Caso de dúvida:** perguntar ao usuário se ele tem copy ou quer que ela seja criada.

> `copy-pagina-vendas` e OPCIONAL e só entra quando NÃO há copy boa. Se o usuário já tem a copy,
> pular direto pra validação + COPY LOCK. Nunca reescrever copy que o usuário aprovou.

**Instalação da copy-pagina-vendas** (ela é uma skill separada; se não estiver na máquina, este e
o único passo):

```bash
# <pasta-das-skills> = onde o seu Claude Code procura skills (no padrao, ~/.claude/skills)
git clone https://github.com/ojuliocouto/skill-copy-pagina-vendas.git <pasta-das-skills>/copy-pagina-vendas
```

Se o clone não for possível no momento, seguir sem ela: coletar o briefing do usuário e escrever a
copy diretamente com os frameworks citados, deixando claro que a skill dedicada faz isso melhor.

### 1.1 VoC Mining (Voice of Customer)

Identificar linguagem real dos clientes, palavras que eles usam, não palavras que achamos que eles usam.

**Fontes de VoC (pedir ao usuário ou buscar):**
- Comentários em posts de Meta/Instagram sobre o produto
- Reviews na Hotmart/Kiwify
- DMs e mensagens de WhatsApp de alunos
- Comentários em YouTube do nicho
- Perguntas frequentes que chegam

**Extrair e documentar:**
```
PALAVRAS QUE USAM PARA O PROBLEMA:
- "___________"
- "___________"

PALAVRAS QUE USAM PARA O RESULTADO DESEJADO:
- "___________"
- "___________"

OBJEÇÕES QUE APARECEM:
- "___________"
```

Se não há VoC disponível → usar a copy existente do material + inferir com base no público.

### 1.2 Before/After Grid

Define a transformação que a página precisa comunicar:

```
ESTADO ANTES (o que o usuário SENTE/TEM/FAZ hoje):
- Sente: ___________
- Tem: ___________
- Faz (média dia): ___________
- Status: ___________

ESTADO DEPOIS (o que o usuário SENTE/TEM/FAZ com o produto):
- Sente: ___________
- Tem: ___________
- Faz (média dia): ___________
- Status: ___________
```

Esta grid alimenta o hero, o problem section e o CTA.

### 1.3 Hierarquia de Mensagens

Definir qual promessa fica em qual posição:

```
PROMESSA PRINCIPAL (hero headline, 1 frase, o maior benefício):
"___________"

PROMESSA DE SUPORTE 1 (subheadline, expande a principal):
"___________"

PROMESSA DE SUPORTE 2 (features/bullets, provas da promessa):
- ___________
- ___________

OBJEÇÕES E CONTRA-ARGUMENTOS (posicionamento defensivo):
- Objeção: "___" → Contra: "___"
- Objeção: "___" → Contra: "___"

URGENCIA/ESCASSEZ (real, nunca inventada):
"___________"
```

### 1.4 Copy Wireframe (Seção por Seção)

Escrever o texto real de cada seção. Não placeholders, texto REAL que vai na página:

```
HERO:
- H1: "___________"
- Subheadline: "___________"
- CTA button: "___________"
- Micro-copy abaixo do CTA (OPCIONAL, nunca no hero): "___________"
  (a `design-taste-frontend` proíbe texto embaixo do botão do hero; garantia ou detalhe vai no
  subtítulo. Fora do hero, uma linha curta embaixo do botão e permitida.)

SEÇÃO 2 ([nome]):
- Título: "___________"
- Corpo: "___________"

SEÇÃO 3 ([nome]):
- Título: "___________"
- [bullets/texto]:
  • ___________
  • ___________

[continuar para todas as seções mapeadas no Step 0]

OFERTA (se houver):
- Headline da oferta: "___________"
- O que inclui (value stack):
  • ___________  (valor R$___)
  • ___________  (valor R$___)
- Garantia: "___________"
- Preço de: R$____ | Por: R$____
- CTA final: "___________"
```

### 1.5 Checklist de Qualidade da Copy

Antes de travar, verificar:
- [ ] Headlines passam no teste "So what?" (dizem um benefício real, não uma feature)
- [ ] CTAs tem verbo de ação + benefício (ex: "Quero automatizar agora" não "Enviar")
- [ ] Copy esta no nível de leitura 5a-7a série (sem jargão técnico desnecessário)
- [ ] Promessa principal e específica (números, resultados, tempo) não genérica
- [ ] Objeções principais foram respondidas em alguma seção
- [ ] Urgência e real (data de encerramento, vagas limitadas) não inventada

### 1.6 COPY LOCK

Declarar formalmente:

```
=== COPY LOCK ===
Data: ___________
Versão: 1.0
Status: FROZEN, nenhuma alteração sem aprovação explícita do usuário

A copy acima esta travada. O Step 2 (DIRECIONAR) usara esta copy como
base imutável. Qualquer mudança de copy requer voltar ao Step 1.
=================
```

### Output do Step 1
- VoC mining documentado
- Before/After Grid preenchida
- Hierarquia de mensagens definida
- Copy de CADA seção escrita (texto real, sem placeholders)
- Checklist de qualidade 100% verificado
- COPY LOCK declarado

**>>> GATE 1: VoC + Before/After + Hierarquia + Copy de TODAS as seções escrita + COPY LOCK declarado? Se NÃO, PARA AQUI. Nenhum design sem copy aprovada. <<<**

**PARADA OBRIGATÓRIA:** Apresentar a copy completa ao usuário e perguntar: "Step 1 concluído. A copy esta aprovada? Posso avançar para o Step 2 (DIRECIONAR)?", NÃO AVANÇAR SEM RESPOSTA.

---

## Step 2: DIRECIONAR (5-10 min)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 2 --arquivo evidencias/etapa-2.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

Define a direção visual baseada na copy aprovada no Step 1. O design serve a copy, nunca o contrário.

### 2.0 Consultar o BANCO DE DESIGN (OBRIGATÓRIO, antes de inventar cor/fonte/estilo)

Antes de definir qualquer estilo, paleta ou tipografia, **consultar o banco de design**
(`data/*.csv` via `scripts/search.py`) com base no tom + tipo de página detectados no Step 0.
NUNCA inventar paleta/fonte do zero quando o banco tem opção validada.

**PRECEDÊNCIA (quem vence):** 1º identidade REAL indicada pelo usuário (logo, paleta, fontes: regra inegociável); 2º brand tokens de projeto existente carregados no Protocolo de Ativação (consistência de funil vence sugestão do banco); 3º banco de design (`search.py`). O banco e a fonte quando NÃO há identidade nem projeto anterior; nunca sobrepõe os dois primeiros.

**BANCO x SKILLS DE DESIGN: o banco e PONTO DE PARTIDA, não sentença.** Depois de tirar paleta e
fonte do banco, passe o resultado pela `frontend-design` e pela `design-taste-frontend`. Se uma
delas reprovar o que o banco devolveu (caso medido no teste com aluno, 02/10/2026: o banco deu
creme #FFF8F0 + dourado #A16207 + Lora serifada para um estúdio de pilates, e as duas skills
chamam exatamente esse trio de visual padrão de IA), **pegue o próximo resultado do banco**
(`-n 3` e o segundo da lista, ou o segundo par de fonte) e declare por escrito, no output do
Step 2, o MOTIVO da troca: qual resultado foi descartado, qual skill reprovou e por que. Se os
três primeiros resultados forem reprovados, ajuste UM eixo do primeiro (troca o acento ou a
fonte de título) e declare do mesmo jeito. Nunca fique parado decidindo: a regra e esta, e o
aluno do teste perdeu 20 minutos sem ela.

Rodar os 3:

**O banco (CSVs) e indexado em inglês, e o `search.py` traduz os termos comuns em português** (pilates, estúdio, clínica, consultório, academia, restaurante, advocacia, saúde, beleza, acolhedor, escuro, moderno e outros: lista em `TRADUCOES`, no `scripts/core.py`). A saída mostra a consulta traduzida. Termo fora da lista e 0 resultado? Traduza você (ex.: "mentoria dark premium" → "dark premium coaching").

```bash
# Estilo visual (50 estilos: cyberpunk, OLED dark, glassmorphism, brutalism, etc.)
python3 <dir-da-skill>/scripts/search.py "<tone + niche em ingles>" --domain style -n 3
# Paleta (21 paletas por tipo de produto, com primary/secondary/CTA/bg/text/border em hex)
python3 <dir-da-skill>/scripts/search.py "<product type em ingles>" --domain color -n 2
# Font pairing (50 pares, ja com CSS @import e Tailwind config prontos)
python3 <dir-da-skill>/scripts/search.py "<mood em ingles>" --domain typography -n 2
```

Também disponíveis: `--domain ux` (guidelines), `--domain chart` (data viz), `--domain landing`,
`--domain product`, `--domain prompt`. Use `--json` se for parsear o resultado.

Pegar do retorno: cores em hex (viram as CSS vars do 2.1), o `CSS Import` e o `Tailwind Config`
do font pairing, e os "Effects & Animation" do estilo (alimentam o Step 3).

**Depois** do banco, conferir referências visuais reais em `references/visual-references.md`:
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

### 2.1 Paleta Visual (Flat: 10-15 variáveis CSS)

Preencher as CSS vars abaixo com os valores **vindos do `search.py`** (paleta + font pairing do 2.0),
ajustando ao tom. O template e a forma; os valores saem do banco de design, não inventados.

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

### 2.2 Layout por Seção

Definir o grid de cada seção usando `references/desktop-layout-rules.md`:

```
SEÇÃO 1: Hero       → Split 60/40 (texto + foto)     | Dark BG
SEÇÃO 2: Stats      → 4-col counter row              | Light BG
SEÇÃO 3: Problema   → 3-col icon cards               | Dark BG
...
```

**Regras (de desktop-layout-rules.md):**
- Max 2 seções seguidas com mesmo layout
- Hero DEVE ter visual ao lado (nunca só texto)
- Alternar backgrounds claro/escuro
- Seções obrigatoriamente side-by-side: mentor bio, testimonials, features, garantia

### 2.3 Wireframe Rápido (Validação)

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

**Gate:** Se a estrutura não casa com o objetivo de conversão → ajustar ANTES de buildar. Voltar ao mapa de seções se necessário.

### 2.4 Decisão de Assets
Listar assets necessários por seção:
- Hero: foto do mentor OU vídeo embed OU mockup
- Features: ícones SVG custom (não genéricos)
- Testimonials: fotos de alunos OU screenshots WhatsApp
- Mentor: foto profissional
- Garantia: badge/selo

### 2.5 Decisão de Tech Stack
Consultar a tabela DECISÃO DE TECH STACK (acima). Definir AGORA:
- Framework: React + Vite? HTML puro? Rota no projeto existente?
- Dependências: Framer Motion? shadcn/ui? Magic UI?
- Onde vive o código: novo projeto? subpasta? nova rota no SPA?

### Output do Step 2
Documento com:
- Paleta CSS completa (10-15 vars)
- Font pairing definido
- Layout de CADA seção (grid, split, cards: especificado)
- Lista de assets por seção
- Tech stack escolhido

**>>> GATE 2: Paleta + font pairing + layout de CADA seção + lista de assets + tech stack definidos por escrito? Se NÃO, PARA AQUI. Não escreva UMA LINHA de código sem direção visual completa. Página sem direção = página feia. <<<**

**PARADA OBRIGATÓRIA:** Apresentar a direção visual completa ao usuário e perguntar: "Step 2 concluído. Posso avançar para o Step 3 (BUILDAR)?", NÃO AVANÇAR SEM RESPOSTA.

---

## Step 3: BUILDAR (30-60 min)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 3 --arquivo evidencias/etapa-3.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

Construção do código, seção por seção, com assets criados INLINE. A copy do Step 1 e a direção visual do Step 2 estão travadas, apenas implementar.

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
- `references/reference.md`: documentação Tailwind CSS (utilities, config)
- `references/chart.md`: instalar e usar o componente Chart do shadcn (data viz)
- `references/learn.md`: guia de aprendizado shadcn/ui (padrões e boas práticas)

### 3.2 Construir Seção por Seção

Seguir a ordem definida no Step 1. Para cada seção:
1. Implementar o layout definido (grid split, não formato carta)
2. Inserir a copy extraída do material
3. **Avaliar vídeo de background para a seção** (ver protocolo e condições abaixo)
4. Criar/buscar demais assets visuais (imagem, ícone)
5. Adicionar animação de scroll reveal (CSS-only preferido sobre JS)
6. Testar responsividade (mobile colapsa pra single column)

**PROTOCOLO DE VÍDEO DE BACKGROUND (condicional por tipo de página):**

Vídeo de fundo e um diferencial FORTE, mas subordinado a constraint global de LCP e ao tipo de página:

| Tipo de página | Vídeo de background |
|---------------|---------------------|
| Sales page / Challenge (mid/high-ticket) | Hero OBRIGATÓRIO + secoes-chave (1 a 3 vídeos por página) |
| Institucional | Hero recomendado |
| Capture simples / thank-you | NÃO usar (velocidade máxima; textura/pattern no lugar) |
| E-commerce home | NÃO usar (identidade real + fotos de produto) |

Regras quando usar: se compromete LCP < 2.5s, SAI (constraint global vence). Fontes, nesta ordem: material real do cliente, Pexels (`PEXELS_API_KEY`), Veo, Higgsfield (ver 3.2b). Sem nenhuma, fallback: gradiente + noise/pattern + foto tratada, e registrar na entrega que o vídeo ficou pendente.

- **Buscar primeiro:** `assets-search.py "descricao-da-secao" --type video`: buscar vídeos stock que combinem com o tema
- **Se não encontrar stock adequado:** gerar com Veo 2 → ver `references/veo-video-workflow.md`, ou Higgsfield → `references/higgsfield.md`
- **Implementar** o vídeo como background absoluto da seção com overlay:
  - Seções escuras: vídeo `object-cover` + overlay escuro (gradiente/`bg-black/60`)
  - Seções claras: vídeo `object-cover` + véu claro próprio (nunca baixar a opacidade do vídeo)
- **O VÉU EXISTE PRA O TEXTO FICAR LEGÍVEL, NÃO PRA ESCONDER O VÍDEO.** Calcule antes de aceitar:
  `visivel = opacidade_video x (1 - alpha_veu)`. **Abaixo de 15% de visibilidade o vídeo e enfeite
  invisível: ou aumenta, ou tira e economiza o crédito.** Faixa medida que funcionou em página
  real (25/08/2026): vídeo a 100% e véu entre 72% e 48% (mais forte atrás do título, mais fraco
  embaixo). Texto sobre vídeo exige MEDIR contraste (mínimo 4.5:1) contra as partes ESCURAS do
  clipe: se não bate, a saída e composição (texto numa coluna, vídeo numa janela ao lado), não
  aumentar o véu. Lições completas em `references/higgsfield.md`.
- **Otimizar:** `ffmpeg -i input.mp4 -c:v libx264 -crf 28 -vf scale=1280:-2 -an output.mp4`
- **Mobile:** esconder vídeos no mobile (performance) com `hidden md:block` + `preload="none"`

**Criar demais assets INLINE** (não como step separado):
- **Imagens de app/produto:** gerar com Nanobanana (Gemini) → WebP → mockup iPhone15Pro ou Safari (ver `references/nanobanana-mockup-carousel.md`)
- Imagens gerais: buscar com `assets-search.py` ou gerar descrição para IA
- **Ícones:** Hugeicons como primário (46k+ ícones, 10 estilos) para landing pages. Lucide para UI/dashboards simples. NUNCA genericos/simples, e NUNCA "quadradinho arredondado com fundo tingido + glifo abstrato" (o tell número 1 do passe de gosto 4.2c)
- Vídeos stock: `assets-search.py "descricao" --type video`

**Efeitos avançados, consultar SEMPRE antes de entregar:**
- Ver `references/efeitos-avancados.md` para: 3D Card Tilt, Text Scramble, Magnetic Cursor, Gradient Border animado, Noise Texture, SVG Blob Morphing, Confetti, CSS Scroll-Timeline, Parallax Multicamada, Counter Animado, etc.
- **BANIDOS do catálogo (reprovam na wave, são tells V1-V15):** Aurora Background, Floating Orbs, SVG Blob de glow, Glassmorphism generalizado, glow colorido em botão, gradient-clip em título. Estão no arquivo de referência, mas NÃO podem ser usados como "wow" nesta skill.
- Regra: mínimo 2 efeitos por página (1 de fundo + 1 de interação). Máximo 2 por seção.
- CTA principal DEVE ter micro-interacao: mudança de tom no hover + elevação sutil. Confetti ou magnetic só QUANDO o tom da página pede (igual ao 3.6), nunca por padrão.

**Mockup Carousel (produto digital/SaaS):**
- Gerar screenshots com Nanobanana → iPhone15Pro + MockupCarousel → seção side-by-side
- Ver workflow completo em `references/nanobanana-mockup-carousel.md`

### 3.2-ART GATE DO PRIMEIRO BLOCO: o diretor de arte entra ANTES de replicar o padrão

**Construa SÓ o hero. Pare. Olhe. Só depois construa o resto.**

Este e o único ponto do Step 3 em que corrigir e barato. O hero define token, densidade,
escala tipográfica, ritmo de espaçamento e o nível de acabamento; as outras seções copiam esse
padrão. Errar no hero não custa uma seção, custa a página inteira, e o erro só aparecia la no
Step 4, quando refazer significa mexer em tudo.

```bash
# 1. Renderize SO o que existe ate agora (funciona em arquivo local)
node <dir-da-skill>/scripts/screenshot-prova.js "file:///caminho/index.html" ./prova-hero --sem-identidade
```

2. **OLHE o PNG.** Não responda de cabeça: abra a imagem. Um checklist respondido de memória
   aprova o que os olhos reprovariam (o caso de 26/08: um véu por cima do vídeo deixou o vídeo
   0 a 7% visível e o checklist passou liso, porque ninguém abriu a imagem).

3. **Chame a `design-taste-frontend` sobre esse PNG**, com a direção do Step 2 na mão. Não é o
   gate anti-slop do 4.9: aqui ela responde uma pergunta só, e e a que importa agora:
   **"o que esta na tela e o que a direção do Step 2 prometia?"**

4. **Compare item a item com o 2.1**, porque o desvio entre a direção escrita e o código e a
   regra, não a exceção:

| O que conferir | Reprova quando |
|---|---|
| Cor | apareceu hex fora das CSS vars do 2.1 (o build "resolveu" uma cor no meio do caminho) |
| Tipografia | a escala do 2.1 virou outra coisa, ou entrou peso/familia que não estava na direção |
| Espaçamento | o ritmo vertical não segue a escala; seção respira diferente do que foi desenhado |
| Densidade | o hero ficou vazio com texto centralizado, quando a direção pedia layout rico |
| Acabamento | profundidade veio de glow/aura em vez de sombra real e hierarquia |

**>>> GATE 3.2-ART: o hero na tela corresponde a direção do Step 2? Se NÃO, corrija o hero AGORA,
antes de construir a próxima seção. Replicar padrão errado e o jeito mais caro de errar. <<<**

Depois de aprovado, o hero vira a REFERÊNCIA: as demais seções se conformam a ele, e qualquer
desvio deliberado (uma seção que quebra o padrão de propósito) se declara na entrega.

### 3.2b MOVIMENTO NOS BLOCOS: decidir bloco a bloco (rota padrão: CSS; Higgsfield opcional)

**Rota padrão do aluno: movimento em CSS** (entrada do hero, reveal em 2 a 4 secoes-chave, hover
e microinteração no botão, um elemento próprio que se mexe, como um fio que balança). Ela não
pede conta nem chave e NÃO deixa a página pior. **Higgsfield e opcional** (plano pago para uso
comercial): quem tiver conta ganha b-roll e vídeo gerado nos blocos; quem não tiver segue em CSS
sem pendência de "página incompleta".

Página inteira parada, com bloco de texto e ícone, entrega menos do que merece. **Neste step,
pergunte SEMPRE quais blocos ganham movimento** e trate isso como parte do build, não como
sobremesa. Os candidatos típicos são os blocos que hoje só tem texto:
- lista de benefícios ou "o que muda", que costuma ser 3 ou 4 cards de texto com ícone
- passo a passo do processo
- fundo de seção intermediária, pra quebrar a monotonia entre dobras

Ordem de preferência para VÍDEO no bloco (não muda): **material real do cliente → gravação de
tela → Higgsfield**. Cena genérica de IA se reconhece; imagem real do negócio ganha dela sempre
que existir. Sem nenhum dos três, o bloco ganha movimento em CSS, que é a rota padrão.

**Sem conta Higgsfield:** siga pela rota CSS (animação no próprio bloco) ou b-roll do acervo
aberto, e diga na entrega, numa linha, que não houve vídeo gerado. Falta de conta não bloqueia
a entrega e não vira defeito.

**Aluno sem conta nem CLI?** O setup inteiro esta em `references/higgsfield.md`, na seção
SETUP: criar conta (**plano pago para uso comercial**), `npm i -g @higgsfield/cli`,
`higgsfield auth login`, `npx skills add higgsfield-ai/skills` e, o passo que trava todo mundo
e não aparece em tutorial nenhum, `higgsfield workspace set <id>` (sem workspace selecionado,
qualquer comando responde "No workspace selected"). Verificação: `higgsfield account status`
imprime e-mail, plano e créditos. Conduza a pessoa por eles em vez de só avisar que falta conta.

As 5 regras de vídeo em página (proporção única decidida antes, gerar no tamanho da caixa x2,
seed anotado, pôster com hash próprio, vídeo do herói e o LCP) estão em
`references/higgsfield.md` e valem pra QUALQUER rota de vídeo, inclusive a do Replicate.

### 3.3 Checklist Brazil (integrado no build)

Durante a construção, incluir:
- [ ] GTM head + body tags (se o projeto/cliente fornecer um container)
- [ ] Link de checkout nos CTAs (Hotmart/Kiwify/Stripe/etc, conforme o projeto)
- [ ] Meta Pixel / tracking (se aplicável)
- [ ] Favicon do próprio projeto (`<link rel="icon" type="image/png" href="favicon.png" />`)
- [ ] Light mode para vendas / dark mode para desafio; capture herda a identidade do projeto/funil (sem identidade: escolher pelo tom do Step 0)
- [ ] `data-cfasync="false"` no script principal (Cloudflare Rocket Loader)

### 3.4 Speed como Constraint

Durante todo o build:
- [ ] TODAS imagens em WebP (`cwebp -q 82`)
- [ ] `width` + `height` em TODA imagem (evita CLS)
- [ ] `loading="lazy"` abaixo do fold
- [ ] `fetchpriority="high"` na hero image
- [ ] CSS animations > JS animations (quando possível)
- [ ] Tailwind compilado (NUNCA cdn.tailwindcss.com)
- [ ] `preconnect` para Google Fonts
- [ ] Vídeos: `preload="none"`, esconder no mobile
- [ ] Target: LCP < 2.5s, página total < 2MB

### 3.5 Compilar para Produção
```bash
# Compilar Tailwind
npx tailwindcss@3 -i _input.css -o tailwind-compiled.css --content ./index.html --minify

# Converter imagens
for f in *.png *.jpg; do [ -f "$f" ] && cwebp -q 82 "$f" -o "${f%.*}.webp"; done
```

### 3.6 Auto-Revisao Visual (antes de avançar)

**Responda este checklist OLHANDO a página renderizada, nunca de memória.** Rode
`screenshot-prova.js` sobre a página inteira e abra os PNG (desktop e mobile) antes do primeiro
item. Checklist respondido de cabeça aprova o que os olhos reprovariam: e assim que passa véu que
apaga o vídeo, favicon deformado e seção que quebrou só no mobile.

Antes de considerar o build "pronto", revisar CADA seção:
- [ ] Tem pelo menos 1 elemento visual "wow" DO CATÁLOGO PERMITIDO? (foto tratada, mockup, vídeo integrado, number ticker, marquee, parallax sutil, micro-interacao no CTA)
- [ ] ZERO tells de IA? (sem blob glow, aurora, floating orbs, glow em botão, glassmorphism generalizado, gradient-clip em título: ver `references/anti-vibe-coding.md` V1-V15)
- [ ] Desktop tem layout rico (side-by-side, grid, split): NUNCA coluna única centralizada (exceto capture)?
- [ ] Assets reais estão no lugar? (fotos, ícones Hugeicons, mockup Nanobanana, vídeo se aplicável): ZERO placeholders?
- [ ] Scroll reveal nas secoes-CHAVE (2 a 4 usos por página, no máximo 1 por seção)? NUNCA em todo elemento: reveal em excesso e sinal de vibe-coding (`anti-vibe-coding.md`, sinal 2) e reprova na wave.
- [ ] Backgrounds alternam e tem textura DISCRETA? (noise, pattern, gradiente sutil: profundidade vem de sombra real e hierarquia, não de "aura")
- [ ] Cards e seções tem profundidade? (shadows reais, borda 1px, elevação no hover: sem border glow colorido)
- [ ] CTA principal tem micro-interacao? (mudança de tom no hover, elevação sutil, magnetic ou confetti QUANDO o tom da página pede: nunca glow colorido difuso)
- [ ] Vídeo de background conforme a tabela do 3.2? (obrigatório só onde a tabela manda; capture NÃO leva)
- [ ] **Movimento decidido bloco a bloco (3.2b)?** Quais ganharam movimento, por qual rota (material do cliente, gravação de tela, Higgsfield, CSS/Framer Motion) e por que os outros ficaram estáticos. Bloco de texto+ícone sem movimento e sem motivo declarado = decisão não tomada
- [ ] Vídeo de fundo passa na conta do véu (`visivel = opacidade_video x (1 - alpha_veu)` >= 15%) e o texto por cima mede >= 4.5:1 de contraste?
- [ ] Produto digital/SaaS tem mockup carousel com Nanobanana? (se página de venda de app/ferramenta)

Se QUALQUER item acima for NÃO → corrigir AGORA, antes de ir pro Step 4.

**>>> GATE 3: Todas seções construídas com layout desktop rico + assets reais + animações + pelo menos 1 efeito "wow" por scroll + DECISÃO DE MOVIMENTO declarada (quais blocos ganharam movimento, por qual rota, e por que os outros ficaram estáticos: ver 3.2b)? Se NÃO, PARA AQUI. Página incompleta = página feia. Volte e complete o que falta. <<<**

**PARADA OBRIGATÓRIA:** Apresentar preview ou descrição detalhada do que foi buildado ao usuário e perguntar: "Step 3 concluído. Posso avançar para o Step 4 (VERIFICAR & SHIPAR)?", NÃO AVANÇAR SEM RESPOSTA.

---

## Step 4: VERIFICAR & SHIPAR (20-30 min)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 4 --arquivo evidencias/etapa-4.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

**OBRIGATÓRIO: Auditoria Adversarial por WAVE DE SUBAGENTS antes do deploy.**
A auditoria NUNCA é feita pelo mesmo contexto que construiu a página (viés: o construtor
não enxerga o próprio erro). Dispara-se uma wave de 8 subagents adversariais paralelos,
cada um com UMA lente independente, e um agente de síntese consolida o gate.

### GATE COM ESPERA FIXA MEDE O INSTRUMENTO, NÃO A PÁGINA

Vale para TODO gate deste Step, e para qualquer medição automatizada que você escrever.

Um gate que rola, espera um prazo fixo e fotografa esta medindo a página JUNTO com o
próprio atraso. Com animação de entrada em curso, a região amostrada cai no lugar errado e
produz número que nunca existiu para ninguém. Caso medido (08/2026): o gate leu **botão
branco contra botão branco, 1,09:1**, numa composição cujo contraste real e 12,4:1, e
reprovou 12 de 12 telas. A página estava certa; a espera de 260ms e que pegava o bloco no
meio do caminho.

**Como diagnosticar sem perseguir fantasma:** por eliminação, com REPETIÇÃO (5 execuções
por cenário, porque o defeito e intermitente e uma única passada não distingue sorte de
causa). No caso acima: fade de 700ms reprovou 4 de 5; sem fade, 1 de 5; deslocamento de
14px, 0 de 6.

Duas regras saem daqui:

- **Gate que mede cor espera a região ESTABILIZAR** (duas leituras iguais dentro de
  tolerância, com teto de tempo), nunca um prazo. Isso cobre de brinde imagem preguiçosa
  que chega depois, troca de fonte e pôster de vídeo. Um gate com prazo fixo pune página
  com animação caprichada e aprova página sem movimento nenhum: incentivo invertido.
- **Antes de implementar a correção de uma hipótese, MEÇA A HIPÓTESE.** Neste mesmo caso a
  explicação mais plausível (`scroll-behavior: smooth` corrompendo a captura) foi
  REFUTADA por medição: a API que o gate usa ignora essa propriedade. A correção já tinha
  sido implementada e trouxe regressão própria. Correção baseada em causa errada e pior
  que nenhuma, porque parece conserto.

---

### AUTORIDADE: qual checklist e O portão

A skill tem várias listas (1.5 copy, 3.3 Brazil, 3.6 auto-revisao, 4.2 QA, Checklist
Pre-Entrega). **A wave de auditoria adversarial (4.0), com seu fallback manual (4.0b/4.1),
e O PORTÃO DE ENTREGA.** Todas as outras listas são **auxiliares de build** que ajudam a
chegar limpo na wave; nenhuma delas substitui ou dispensa a wave. Entrega = wave passou.

**Escopo:** isto vale nos caminhos CRIAR, CLONAR e MELHORAR. O caminho EDITAR (mudança
pontual) tem portão próprio, menor e proporcional: checklist de regressão + prova do ponto
alterado. Rodar a wave de 8 lentes numa troca de headline não é rigor, e processo errado.

### ENFORCEMENT DO GATE (ler antes de tudo, falha histórica recorrente)

O maior erro documentado desta skill: o agente ACIONA a skill mas PULA esta auditoria,
builda e deploya direto, e entrega página com cara de IA / bug. Aconteceu em dois projetos
reais (jun/2026): um site institucional e um clone. Para tornar isso impossível de esconder:

1. **Deploy acontece DENTRO do Step 4, DEPOIS da wave (4.0).** Buildar (Step 3) e depois
   deployar sem rodar a wave = gate pulado = a skill FALHOU. Não existe "deploy rápido".
2. **BLOCO OBRIGATÓRIO DA ENTREGA (fonte única, vale pra CRIAR, CLONAR e MELHORAR, inclusive
   na rota expressa):** a mensagem que apresenta a página ao usuário DEVE conter estas QUATRO
   linhas. Falta uma = gate pulado = não entregue.

   ```
   VEREDITO DA WAVE: deploy_liberado <true|false> | scores por lente | críticos: <lista ou nenhum>
   IDENTIDADE DA PÁGINA: title / description / favicon PNG quadrado / og:title / og:description /
     og:image conferidos (colar o output do screenshot-prova.js)
   PASSE DE GOSTO (4.2c): tells ANTES -> DEPOIS (o depois tem que ser 0) + itens de composição alterados
   PROVA DE ENTREGA (4.5): arquivos de screenshot LIDOS + resultado do clique da interação principal
   PENDÊNCIAS DECLARADAS: <fallbacks que rodaram degradados, deploy/Lighthouse/og:image absoluta
     quando não houver domínio, assets que faltam>
   ```

   **No caminho EDITAR** o bloco e outro, menor: checklist de regressão + prova do ponto alterado
   + pendências. A wave não roda ali.
3. **Escada de fallback da wave** (usar o degrau mais alto disponível):
   1. Tool `Workflow` disponível → wave completa em paralelo (8 lentes, inclusive na rota expressa).
   2. Sem `Workflow`, mas com `Task`/`Agent` (subagentes) → rodar CADA lente como subagente
      independente. E o caso mais comum e PREFERIDO ao fallback manual: preserva a auditoria
      fora do contexto que construiu.
   3. Sem nenhuma forma de subagente → fallback manual (4.0b/4.1) e **colar o scoring mesmo
      assim**, declarando que a auditoria foi auto-avaliacao. Pular e documentar como "pulei"
      não é aceitável sem pelo menos o fallback manual pontuado.

---

### 4.0 WAVE DE AUDITORIA ADVERSARIAL (OBRIGATÓRIO, roda primeiro)

Ver protocolo completo, schema e esqueleto Workflow em `references/audit-agents.md`.

1. Compilar a página e subir **preview deploy** (branch, nunca main) ou servir local.
2. Disparar os 8 agentes EM PARALELO via tool `Workflow` (parallel), passando
   `args: { url, arquivos }`:

   | Agente | Lente | Reprova (critical) se |
   |--------|-------|-----------------------|
   | `design-critic` | taste / anti-slop (roda `design-taste-frontend`) | taste < 4.0, ou **3+ tells visuais de IA**, ou footer/checkout quebrado |
   | `assets-auditor` | presença de imagem/mockup/video real | só texto+gradiente+SVG, SaaS sem mockup, lead magnet sem mockup do material |
   | `visual-auditor` | hierarquia, paleta, spacing, grid desktop | formato carta, side-by-side em coluna única, sem hierarquia |
   | `motion-auditor` | scroll reveal, hover, hero entrance, counters | hero estático, seção sem feedback, card sem hover |
   | `cro-auditor` | CTAs, form, WhatsApp, oferta, message match, Hook/Story/Offer | CTA insuficiente, form/checkout quebrado, sem message match |
   | `a11y-auditor` | focus, labels, alt, ARIA, contraste 4.5:1, zero emoji | falha WCAG crítica, emoji na página |
   | `responsive-auditor` | as 12 telas reais, mobile E desktop (roda `gate-responsivo.mjs`) | overflow horizontal, CTA fora da dobra, alvo de toque < 44px, corpo < 14px, texto cortado |
   | `content-auditor` | dado inventado, claim sem fonte, travessão, consistência de contato | claim que não está na fonte, travessão > 0, telefone divergente |

3. Cada agente retorna o schema `VERDICT`. Agente de **síntese** consolida em `SINTESE`.
4. **GATE:** registre todas as lentes e execute `wave.py checar` e `wave.py rodada` (4.2e e 4.2f). Críticos e regressões confirmados bloqueiam. O ciclo admite piso, gravidade esgotada, convergência ou teto, sempre com a nota real e as pendências declaradas. A síntese não pode criar um piso incompatível com o ciclo.

Sem `Workflow`, use subagentes disponíveis. Sem subagentes, registre a autoavaliação e sua limitação, conforme a escada de fallback acima.

---

### 4.0b AUDITORIA DO DESIGNER: Scoring System (fallback manual / checklist das lentes)

Pontuar cada dimensão de 0-10 usando `references/scoring-system.md`:

| Dimensão | Nota | Status |
|----------|------|--------|
| Hierarquia Visual | /10 | |
| Tipografia (ver `references/typography-scale.md`) | /10 | |
| Animações (ver `references/animation-audit.md`) | /10 | |
| Grid & Layout (ver `references/desktop-layout-rules.md`) | /10 | |
| CTAs (ver `references/cta-placement-map.md`) | /10 | |
| Prova Social (ver `references/social-proof-hierarchy.md`) | /10 ou N/A | |
| Mobile (ver `references/mobile-checklist-detailed.md`) | /10 | |
| Performance Visual | /10 | |
| Trust Signals (ver `references/trust-signals-placement.md`) | /10 | |

**Registre as notas reais. A decisão de encerramento pertence ao ciclo 4.2f; esta tabela não cria um segundo bloqueio por nota.**

**Exceção única, para quem ainda NÃO tem cliente:** se o briefing (0.0) registrou a flag
`sem prova social`, a dimensão Prova Social entra como **N/A** e sai do calculo da média, desde
que a página traga os substitutos verificáveis (credencial do profissional, fotos reais do
espaço e do equipamento, garantia, condição de inauguração, CNPJ e endereço). Regra completa em
`references/scoring-system.md`, dimensão 6. Sem os substitutos, a dimensão volta a pontuar
normalmente. Depoimento inventado continua PROIBIDO em qualquer cenário.

**SEM CLIENTE AINDA: o que a página mostra e o que fica oculto (regra única).** Quando o
briefing tem a flag `sem prova social`:
- **A página MOSTRA só substitutos verificáveis**, cada um conferido contra a fonte: credencial
  do profissional (nome e número do registro no conselho, quando o cliente informar), fotos
  reais do espaço e do equipamento, endereço com referência, horário, CNPJ, garantia real,
  condição de inauguração que o cliente confirmou. Sem nenhum deles confirmado, a página sai
  sem seção de prova e o motivo vai em PENDÊNCIAS DECLARADAS.
- **A página OCULTA o espaço do depoimento futuro**: ele pode existir no HTML como
  `<section data-reservado="depoimentos" hidden>` (ou comentário), nunca visível. Proibido na
  tela: "em breve depoimentos", estrela, contador de alunos, logo de parceiro que não existe.
- **Isto não fere o "ZERO placeholder" do 4.2:** placeholder e o que o VISITANTE vê. Seção
  `hidden` reservada não aparece pra ninguém; ela entra na lista de pendências com o que falta
  pra ligar ("3 depoimentos com nome e foto, autorizados").
- Modelo de copy do mesmo caso em `references/copy-servico-local.md`, seção "Sem cliente ainda".

---

### 4.1 AUDITORIA DO ESTRATEGISTA: Hook/Story/Offer

Executar auditoria estratégica completa usando `references/strategist-audit.md`:

**PRE-CHECK (responder antes de auditar):**
- [ ] De onde vem o tráfego desta página?
- [ ] Qual a temperatura da audiência (fria/morna/quente)?
- [ ] Qual o nível na Value Ladder do produto?
- [ ] Qual o objetivo desta página no funil?
- [ ] Há message match entre o anuncio/post e o hero?

**Dimensões estratégicas:**

| Dimensão | Nota | Status |
|----------|------|--------|
| Hook (Gancho: hero) | /10 | |
| Story (Narrativa: mentor/transformacao) | /10 | |
| Offer (Oferta: value stack, preço, garantia) | /10 | |
| Sequência Psicológica (AIDA expandida) | /10 | |
| Prova Social (hierarquia e distribuição) | /10 | |
| Urgência & Escassez | /10 | |
| Message Match com o Tráfego | /10 | |

**Registre as notas reais. A decisão de encerramento pertence ao ciclo 4.2f; esta tabela não cria um segundo bloqueio por nota.**

---

**Se uma dimensão apontou um defeito verificável:**
1. Identificar o que esta errado
2. Corrigir no codigo/copy
3. Re-pontuar
4. Execute o ciclo 4.2f com os achados confirmados e registre a decisão.

---

### 4.2 QA Pre-Deploy

**Funcional:**
- [ ] Todos links funcionam (internos e externos)
- [ ] Todos CTAs apontam pro checkout correto
- [ ] Forms submetem corretamente (se houver)
- [ ] Countdown funcionando (se houver)
- [ ] **Consistência de contato:** telefone, WhatsApp, email batem em TODA a página e nos links (`href="tel:"` / `wa.me/`). Bug real de produção: o hero mostrava um DDD e o WhatsApp ia pra outro. Conferir dígito por dígito.
- [ ] **Âncoras com header sticky:** todo target de âncora (`id`) tem `scroll-margin-top` >= altura da barra fixa, senão o título fica escondido atrás dela ao clicar no menu.

**Visual:**
- [ ] Match design em breakpoints: 320px, 375px, 768px, 1024px, 1280px, 1440px
- [ ] Desktop: NENHUMA seção obrigatória side-by-side esta em coluna única
- [ ] Desktop: não há formato "carta" em páginas high-ticket
- [ ] Sem texto cortado ou overflow
- [ ] Animações funcionando
- [ ] Imagens carregando (nenhum placeholder vazio)

**Performance:**
- [ ] Lighthouse 90+ (todos os scores). **NÃO bloqueia:** exige Chrome/Chromium instalado; sem navegador compatível vira PENDÊNCIA DECLARADA na entrega. **Entrega SEM deploy (pasta local/arquivo único):** Lighthouse, QA pos-deploy, GTM e a **URL absoluta** da `og:image` viram PENDÊNCIAS declaradas no bloco de entrega (não bloqueiam o gate; bloqueiam rodar tráfego). **As TAGS de identidade (title, description, favicon PNG, og:title, og:description, og:image) continuam bloqueando, com ou sem deploy: ver 4.2b**
- [ ] **SEO abaixo de 90 sob `noindex` e ESPERADO, não defeito.** Fora do domínio final a página
  nasce com `noindex` (4.2b), e o Lighthouse derruba o SEO (medido no teste com aluno: 63) só pela
  auditoria `is-crawlable`. Confira no JSON que `is-crawlable` e a ÚNICA auditoria de SEO
  reprovada; se for, registre "SEO 63 por noindex, esperado até o domínio final" e siga. Qualquer
  outra auditoria de SEO reprovada (title, description, link sem texto) e defeito de verdade.
  Os 90+ de Performance, Acessibilidade e Boas práticas continuam valendo.
- [ ] LCP < 2.5s
- [ ] TODAS imagens em WebP
- [ ] Tailwind compilado (não CDN)
- [ ] CSS minificado

**Conteúdo:**
- [ ] ZERO placeholder/Lorem Ipsum visível (seção `hidden` reservada pra depoimento futuro não conta: ver SEM CLIENTE AINDA, no 4.0b)
- [ ] ZERO dado inventado (número, estatística, "100%", depoimento). Se não está na fonte, NÃO existe.
- [ ] **Diff de claims:** listar TODA afirmação factual/promessa da página (urgência, escassez, garantia, "sem gravação", "vagas limitadas", bônus) e conferir uma a uma contra o briefing/material do usuário. Claim que não está na fonte = REMOVER (não é polimento, e dado inventado).
- [ ] **FOTO TAMBÉM AFIRMA, e o diff de claims tem que cobri-la.** Caso medido (08/2026): cinco frentes de serviço administrativas ilustradas com fotos do próprio cliente, duas delas de procedimento clínico (eletroencefalograma e coleta de sangue). Nenhuma palavra foi inventada, e mesmo assim a página passou a sugerir um serviço que a fonte não declara. E a mesma falha que já tinha custado uma rodada por escrito, num canal que o checklist não cobria. **Liste o que cada FOTO mostra, contra o título ao lado dela.** Se a imagem afirma algo que a fonte não diz, ela sai do lado daquele título (pode viver numa faixa sem título colado).
- [ ] **DADO ESTRUTURADO TAMBÉM AFIRMA.** Um `areaServed` no JSON-LD declara área de atendimento, e e justamente o campo que o buscador lê para montar resultado local; um `priceRange` declara faixa de preço. Conferir cada campo do JSON-LD contra a fonte, do mesmo jeito que se confere a copy. Campo não obrigatório que a fonte não sustenta: apagar.
- [ ] **TEXTO ALTERNATIVO E CONTEÚDO, não acessório.** Numa auditoria, 4 de 5 alts descreviam cena diferente da que estava na foto, e quem usa leitor de tela recebia descrição falsa da operação de uma empresa real. Alt gerado por template ("foto 3 de 16") e o mesmo problema com outra cara: dezesseis imagens com uma descrição efetiva. Escrever cada alt OLHANDO a imagem.
- [ ] Textos revisados (sem typos)
- [ ] Preços corretos
- [ ] Links de checkout corretos
- [ ] Telefone/WhatsApp correto
- [ ] **Sweep de travessão:** rodar `grep` pelo caractere em-dash (U+2014) nos arquivos da página, resultado deve ser ZERO. Substituir por `:` / `,` / `.` ou reescrever. Vale pra todo texto do output.

**Tracking:**
- [ ] GTM presente (head + body) SE o projeto/cliente forneceu container (senão: pendência declarada na entrega)
- [ ] Meta Pixel (se aplicável)
- [ ] UTM pass-through funcionando

**SEO + compartilhamento:** não é item de checklist, e GATE. Ver **4.2b IDENTIDADE DA PÁGINA**, logo abaixo, com o comando que reprova.

**Acessibilidade:**
- [ ] Contraste 4.5:1 mínimo
- [ ] Alt text em todas imagens
- [ ] Focus states visíveis
- [ ] `prefers-reduced-motion` respeitado
- [ ] ZERO emojis (usar ícones SVG)

### 4.2b IDENTIDADE DA PÁGINA: title, description e favicon são GATE, não checklist

Toda página entregue TEM que sair com, no mínimo:
- `<title>` próprio (não "Document", não o nome do template)
- `<meta name="description">` que descreve a oferta, não o produto genérico
- **favicon PNG** do projeto (`<link rel="icon" type="image/png" href="favicon.png">`) mais
  `apple-touch-icon`. Favicon só em SVG não serve: muitos navegadores não leem.
- `og:title`, `og:description` e `og:image`

**O comando que reprova** (o mesmo da prova de entrega 4.5, que já abre a página no Playwright):

```bash
node <dir-da-skill>/scripts/screenshot-prova.js <url> <outdir>
# a checagem de identidade roda junto e sai com exit 1 se faltar item obrigatorio.
# So no BASELINE do caminho MELHORAR (pagina de terceiro, ainda nao sua) use --sem-identidade.
# Na prova de entrega, NUNCA passe essa flag: seria pular o gate.
```

**O que bloqueia e o que vira pendência (regra única, não "depende"):**
- title, meta description, favicon PNG quadrado, `og:title` e `og:description`: **BLOQUEIAM
  sempre**, inclusive na entrega sem deploy. São 6 linhas de HTML e não dependem de domínio.
- `og:image`: a TAG e obrigatória sempre. Já o ARQUIVO 1200x630 com **URL absoluta** exige
  domínio: sem deploy, deixar o caminho relativo no HTML, gerar a imagem, e declarar
  "og:image com URL absoluta pendente até o domínio existir". Isso é pendência declarada,
  não gate aberto.

**INDEXAÇÃO: fora do domínio final, a página nasce `noindex`.** Item de GATE, não de gosto.

Publicar a página de um cliente REAL num domínio de teste, com `robots.txt` liberado,
`canonical` apontando para si mesma e CNPJ, telefone e endereço no JSON-LD, cria um
duplicado completo competindo com o site do próprio cliente na busca. Quem paga a conta e
ele, e ninguém pediu isso.

Enquanto a página não estiver no domínio definitivo:
- `<meta name="robots" content="noindex, nofollow">` no HTML
- `robots.txt` com `Disallow: /`
- sem `sitemap.xml`
- `canonical` e o campo `url` do JSON-LD apontando para a **página original do cliente**,
  nunca para o endereço de teste

Isso sai, tudo de uma vez, quando o domínio final existir. Colocar na entrega como
pendência declarada, junto com o `og:image` absoluto.

**Gotcha do favicon:** favicon TEM que ser quadrado. Redimensionar preservando proporção
(`sips -Z`, `object-fit` e afins) a partir de uma foto 3:2 devolve 32x21, não 32x32, e o
navegador distorce. Recorte quadrado PRIMEIRO, depois redimensione. Conferir com
`sips -g pixelWidth -g pixelHeight` antes de declarar pronto: os dois números tem que ser iguais
(o script também confere isso sozinho).

**Receita da og:image 1200x630:** montar um HTML do card (logo + foto + headline + contato),
renderizar via Playwright e exportar JPG/PNG. **Receita do favicon:** recorte quadrado e depois
`rsvg-convert -w 180 -h 180 logo.svg -o apple-touch-icon.png` (e 32/16px), ou `sips -c` a partir
da foto.

Por que virou gate e não ficou no checklist: já estava escrito no checklist, com aviso de que
"saiu zerado na 1a versão", e MESMO ASSIM uma página foi entregue sem favicon e sem nenhuma og
tag (demo de pilates, 25/08/2026). Checklist não bloqueia, gate bloqueia. Item que só vive em
lista de conferência e item que vai ser pulado quando o contexto encher.

O custo de errar e desproporcional ao esforço de acertar: a página e compartilhada no WhatsApp e
no Instagram sem imagem nenhuma e com título errado, e parece amadora antes de alguém abrir.

---

### 4.2c PASSE DE GOSTO (último ato ANTES do deploy, OBRIGATÓRIO)

A `design-taste-frontend` já rodava nesta skill em dois pontos, e mesmo assim saiu página com
cara de IA. O motivo: nos dois pontos ela roda como LENTE DE AUDITORIA, que da nota e aponta.
**Apontar o defeito não é remover o defeito.** Uma nota 8,5 com três tells presentes continua
sendo uma página com três tells presentes.

Por isso existe este passo, e ele é o ÚLTIMO antes do deploy: depois da wave (4.0), depois do QA
(4.2), com a página rodando (preview local ou de branch). Carregue a `design-taste-frontend` e
passe a página inteira com mandato de CORRIGIR, não de pontuar.

**ORDEM FIXA do Step 4, sem interpretação:** 4.0 wave → 4.2 QA → 4.2b identidade → 4.2c passe de
gosto → 4.2c-bis, 4.2d (gates executáveis) → 4.2e master → 4.2f ciclo → 4.2g (só se rejeitou
asset gerado) → 4.3 deploy → 4.4 QA pos-deploy → 4.5 prova de entrega → 4.6 uso → GATE 4. A lista
de comandos dessa ordem esta em `references/caminho-criar.md`. O passe roda ANTES do
deploy justamente pra não existir "corrigi depois do print": se por qualquer motivo você mexer na
composição DEPOIS do 4.3, e obrigatório re-deployar e repetir o 4.5 inteiro.

**O que este passe caça, na ordem em que mais entrega resultado:**

1. **Ícone genérico em caixinha.** Quadradinho arredondado com fundo tingido + glifo abstrato e
   o tell mais reconhecível que existe. Piora quando o glifo não significa nada (um risco pra
   "fortalece a lombar", um alvo pra "respira"). Saídas melhores, em ordem: recorte real de uma
   foto que a página já tem, virando miniatura; tirar o ícone e deixar a tipografia carregar;
   marca desenhada com personalidade que represente mesmo a ideia. Trocar por OUTRO glifo
   genérico não resolve nada.
2. **Uniformidade excessiva.** Todos os cards do mesmo tamanho, todo canto com o mesmo raio,
   toda sombra igual, toda seção centralizada, toda seção com a mesma estrutura de título e
   subtítulo. Página feita por gente tem ritmo: algo quebra a grade, algo e assimétrico.
3. **Os 15 tells de `references/anti-vibe-coding.md`**, com os números medidos, não no olho.

**O que NÃO se mexe neste passe:** paleta e tipografia (vieram do banco de design e já foram
decididas), copy (foi travada no COPY LOCK), e qualquer coisa que já passou por medição
(contraste, opacidade calibrada, enquadramento). O passe e de COMPOSIÇÃO e PERSONALIDADE.

**Prova de que rodou:** a lista dos itens de composição alterados (o que era e o que virou) mais
a contagem de tells ANTES e DEPOIS. **O DEPOIS tem que ser 0.** Como o Step 3.6 e a wave já
exigem zero tells antes daqui, `0 → 0` e resultado VALIDO e comum: nesse caso a prova e a lista
de itens de composição inspecionados (ícones, ritmo, assimetria), nunca "rodei e estava tudo
certo" sem citar o que foi olhado.

---

### 4.2c-bis GATE DE CLASSE MORTA: o build passa e o estilo nunca chega na tela

```bash
python3 <dir-da-skill>/scripts/gate-classes-mortas.py --projeto <dir>
# e registre o resultado na wave, com o exit REAL:
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> gate classes-mortas --exit <0|1> --detalhe "<o que o gate imprimiu>"
```

Projeto com `dist/` (Vite, Next) lê o CSS de la. **Página HTML + Tailwind compilado, sem `dist/`:**
o gate lê os `.css` da raiz do projeto sozinho (o `tailwind-compiled.css` do 3.5). Só use
`--css` e `--fonte` quando o CSS ou o código morarem em outra pasta.

**Framework de utilitário não reclama de classe invalida.** Ela fica no HTML, o build sai
verde, e o navegador ignora. O que sobra e um estilo que você jura ter aplicado e que
nunca chegou na tela.

Custos medidos num único projeto (08/2026): quatro numa página e uma na seguinte.

| Classe | O que ela NÃO fez |
|---|---|
| `bg-<cor>/97` | a barra fixa ficou **sem fundo em 92% da rolagem**, com o texto da página atravessando os links do menu |
| `bg-<cor>/12` | o disco da seta do CTA ficou sem preenchimento |
| `border-<cor>/12` | o fio do rodapé caiu no cinza padrão do framework, virando a coisa mais clara de uma página inteiramente verde |
| `outline-3` | os campos do formulário ficaram **sem anel de foco**: o `focus:outline-none` matou a regra global e o `outline-3`, que não existe, não repos nada |
| `shadow-lift` | token que existia em OUTRO tema do mesmo projeto: o único controle sobre as fotos ficou sem separação do fundo |

**Por que nenhum outro gate pega:** o build passa; o gate visual quase nunca vê, porque a
diferença e um fio de 1px ou um fundo que falta atrás de uma barra, e isso some em
screenshot reduzido; e quem escreveu conferiu o ARQUIVO, não o PIXEL.

**A regra que sai daqui, e vale além deste gate:** `assert` de troca prova que o ARQUIVO
mudou. Só medição no navegador prova que o PIXEL mudou. Edição de classe utilitária
precisa das duas, sempre.

Calibrado contra os cinco defeitos acima: com eles reintroduzidos o gate sai 1 e nomeia
os cinco arquivos; sem eles, sai 0.

**>>> GATE 4.2c-bis: `gate-classes-mortas.py` saiu com código 0? Se NÃO, a classe não
existe no CSS e o estilo que você acha que aplicou não está na tela. <<<**

---

### 4.2c-ter COMENTÁRIO QUE AFIRMA COMPORTAMENTO E UMA PROMESSA

Nasceu de **três reincidências no mesmo projeto**, e as três passaram por revisão sem
serem notadas, justamente porque o comentário era convincente:

| O que o comentário afirmava | O que a medição achou |
|---|---|
| "a barra fica sólida depois que a página rola" | nunca ficava: a classe de fundo não existia |
| "a grade nasce ALINHADA ao casco" | defasagem de 48px, exatamente meia célula (porcentagem em `background-position` resolve contra área menos tamanho da imagem, e para gradiente isso da zero) |
| "os mesmos quatro números reaparecem na seção seguinte" | a seção seguinte renderizava só o primeiro: três números sumiam da página inteira em janela baixa |

O padrão e sempre o mesmo: o comentário descreve a INTENÇÃO, o código entrega outra
coisa, e o comentário passa a PROTEGER o defeito, porque quem revisa depois lê a
afirmação, acredita e não reconfere.

**Regra:** comentário que afirma comportamento observável ("fica sólido", "aparece",
"reaparece", "alinha", "some", "pinta") só entra depois de a afirmação ser medida. Sem
medição, escreva a intenção ("a ideia aqui é...") ou não escreva. Comentário que mente e
pior que comentário que falta.

**Na wave isto vira material de auditoria:** as lentes tratam comentário que afirma
comportamento como CLAIM a verificar, do mesmo jeito que tratam número na copy.

---

### 4.2d GATE DE OCLUSÃO: conteúdo coberto não é conteúdo invisível

```bash
node <dir-da-skill>/scripts/gate-oclusao.mjs --url <url>
```

**Falha real que criou este gate (26/08/2026).** Uma faixa de números foi desenhada pra
atravessar a borda entre duas seções. A textura de grão da seção de baixo era
`absolute inset-0` SEM z-index, então pintava por cima e comia os rótulos ("empresas
atendidas", "colaboradores impactados"). O dono viu no primeiro olhar. Nenhum gate viu, no
desktop nem no mobile, e os dois motivos valem pra qualquer página:

1. **Coberto não é invisível.** O que eu media era `opacity: 0` e `visibility: hidden`. O
   elemento não era nem um nem outro: estava la, opaco, com outra coisa na frente. São dois
   defeitos diferentes e só um estava coberto por teste.
2. **Eu aprovei olhando screenshot reduzido.** O PNG de página inteira vinha em 1440px e o
   visualizador reduziu pra ~450px. Um rótulo de 13px vira 4px nessa escala: o defeito era
   fisicamente invisível na imagem que eu usei pra aprovar.

**Regra que sai daqui, e vale pra toda conferência visual:** detalhe se confere em RECORTE da
seção, em escala 1:1 ou 2x. Screenshot de página inteira serve pra ver ritmo e composição,
nunca pra aprovar texto, rótulo, borda ou espaçamento.

O gate rola até cada bloco de texto, pergunta ao navegador quem esta naquele pixel
(`elementFromPoint`) e reprova quando a resposta não é o próprio elemento. Roda nas duas telas.
Também pega texto cortado pela própria caixa.

**Causa quase sempre a mesma:** camada decorativa (textura, véu, gradiente) com
`absolute inset-0` e sem z-index. A decoração vai pra trás (`-z-10`) e a ordem entre seções se
declara com z explícito, em vez de depender da ordem do documento. Cuidado com `isolate`: ele
fecha o contexto de empilhamento da seção, e ai a seção SEGUINTE pinta por cima da anterior
INTEIRA, elemento que atravessa a borda incluído.

**Calibrado contra o defeito real:** com o bug reintroduzido o gate acusa 8 blocos cobertos e
sai 1; com a correção, passa. Gate que nunca reprova não vale nada.

**>>> GATE 4.2d: `gate-oclusao.mjs` saiu com código 0 nas duas telas? Se NÃO, conserte a
ordem de empilhamento. <<<**

---

### 4.2e AUDITOR MASTER: a wave aconteceu inteira?

```bash
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> checar
```

**Por que existe (pedido do dono, 26/08/2026, depois de uma falha em cadeia):**

> *"no final, depois dessas lanes que você passa, eu preciso que um último auditor master
> avalie se todas as waves foram feitas, foram executadas. Porque a gente não pode pular sobre
> a gente pra fazer auditoria; todos tem que participar do processo."*

Ele estava descrevendo um buraco real. A skill mandava rodar a wave adversarial, eu declarei
que caiu no "fallback manual" e segui. Resultado: a lente de responsividade **nunca rodou**, a
página foi entregue testada em UMA resolução, e o CTA do herói aparecia cortado no monitor
dele. Ninguém mentiu; o processo simplesmente permitia que uma lente sumisse sem deixar rastro.

**A regra e a mesma do gate de uso de ferramentas: declaração não vale, registro com evidência
vale.** Cada lente se registra ao terminar; o master reprova se faltar QUALQUER uma.

```bash
# Comando inteiro em cada linha: guardar o comando numa variavel e chamar a variavel NAO roda no zsh (shell
# padrao do Mac), que trata a variavel inteira como nome de arquivo e sai com exit 127.

# cada lente, ao terminar
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> registrar responsive-auditor --veredito aprovado --nota 8.5 \
   --achados "12 telas medidas; CTA na dobra em todas; 3 alvos de toque corrigidos pra 44px"

# cada gate executavel, com o exit code REAL
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> gate responsivo --exit 0 --detalhe "12 telas, zero problema"
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> gate oclusao --exit 0 --detalhe "163 blocos, nenhum coberto"

# e o master, por ultimo
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> checar
```

**O que o master bloqueia:** lente que não rodou, gate sem registro, gate vermelho, registro inválido. Notas e vereditos das lentes alimentam o ciclo 4.2f. Ele **não julga se a página esta bonita**: isso
é trabalho das lentes. Ele julga se o PROCESSO aconteceu.

**Lente que não se aplica** se registra com `--veredito nao_aplicavel` e o motivo, e aparece
marcada no relatório. O que não existe e sumir em silêncio.

**`--achados` exige 25 caracteres.** "ok" não é auditoria: o registro tem que dizer o que foi
OLHADO e o que foi encontrado, senão ele não serve pra ninguém revisar depois.

**>>> GATE 4.2e: `wave.py checar` saiu com código 0? Se NÃO, rode as lentes que faltam. Uma
lente pulada não vira "passou por omissão". <<<**

---

**O master NÃO julga nota (corrigido em 27/08/2026).** Ele responde uma pergunta só: *o
processo aconteceu inteiro?*. Lente que faltou, gate vermelho, gate sem registro: isso trava.
Nota baixa não, porque quem decide se a nota basta e o CICLO (4.2f). Enquanto o master também
barrava por piso de nota, os dois gates se contradiziam de frente: o ciclo mandava ENTREGAR com
a nota declarada e o master travava a MESMA entrega pela MESMA nota, e não existia estado que
satisfizesse os dois ao mesmo tempo. E o "ficar travado" que o dono proibiu, só que escrito em
dois arquivos diferentes. As notas continuam aparecendo no relatório do master, como SINAL.

**Regra que vale pra qualquer par de gates:** cada gate responde UMA pergunta, e dois gates
nunca respondem a mesma. Gate duplicado não é redundância saudável, e deadlock esperando
acontecer.

---

### 4.2f O CICLO: auditar, corrigir, RE-auditar, e saber a hora de parar

```bash
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> rodada --criticos <criticos confirmados> --altos <altos confirmados> --regressoes <achados causados pela rodada anterior>
```

**Pedido do dono (27/08/2026), depois de duas waves seguidas:**

> *"se for o caso, tem que ter na skill, então bora. só não podemos ficar travados ou com a
> skill nota do"*

As duas metades desse pedido brigam entre si, e e por isso que o critério precisa ser escrito
com cuidado. "Não ficar travado" pede uma saída; "não ficar com nota do" pede que a saída não
seja render-se. Uma rodada de wave não é o fim do processo: e uma iteração dele.

**O que a prática mostrou em DOIS projetos** (uma landing e a skill de dashboards): o painel
adversarial NUNCA para de achar coisa. A nota sobe rápido nas primeiras rodadas e depois
oscila, porque cada rodada encontra um canto novo e menor. Nesta página foi 5,69 -> 6,44 na
segunda, com os achados confirmados caindo de 17 para 6. Exigir média 8,0 como ÚNICA porta de
saída transforma o processo num loop que só termina por cansaço, e loop que termina por cansaço
entrega pior que critério honesto.

**Alto que depende de dado do cliente (`--pendencias-do-usuario N`).** Número do WhatsApp,
foto do espaço, credencial do profissional, depoimento: quando o achado ALTO só some com algo
que apenas o cliente tem, ele NÃO conta como alto. Passe quantos dos `--altos` são desse tipo:

```bash
python3 <dir-da-skill>/scripts/wave.py --projeto <dir> rodada --criticos 0 --altos 4 --pendencias-do-usuario 2 --regressoes 0
```

Cada um vai no bloco PENDÊNCIAS DECLARADAS, com o que falta e onde entra na página. Nunca vale
pra crítico, e não pode ser maior que `--altos` (o script recusa). Sem este campo, no teste com
aluno (02/10/2026), o critério "zero alto" nunca ficou verdadeiro e o ciclo só soltou pelo teto.

**As três portas de saída, e a ordem importa:**

| # | Critério | Por que |
|---|---|---|
| 1 | **ZERO crítico confirmado** | Inegociável, em qualquer rodada. Crítico e o que quebra uso, mente pro visitante ou expõe o cliente. Não se negocia com média. |
| 2 | **Nenhuma REGRESSÃO** | Nenhum achado confirmado desta rodada pode ter sido CAUSADO por uma correção da rodada anterior. Se foi, a correção quebrou outra coisa, e isso não é avanço. |
| 3 | **Gravidade secou, OU piso, OU convergência** | Zero crítico e zero ALTO confirmados (o que sobrou e acabamento); ou a média chegou a 8,0; ou duas rodadas seguidas subiram menos de 0,3. |

Bateu 1 e 2 e fechou o 3? **ENTREGA, com a nota real escrita na entrega.** Teto de 4 rodadas
como último freio.

**A armadilha que quase travou o ciclo, e por que o critério 2 mudou (27/08/2026).** A primeira
versão média regressão pela NOTA: qualquer lente que caísse em relação a rodada anterior
segurava a entrega. Parece óbvio e esta errado. Cada rodada sorteia auditores independentes, e
a nota deles não é uma medida calibrada, e um julgamento. Na rodada 4 desta página a wave gastou
**446 chamadas de ferramenta** contra uma fração disso nas anteriores (a lente de a11y mediu
contraste no pixel composto de 89 nos de texto, viewport a viewport, e descartou duas rodadas de
números próprios por contaminação), e **as oito notas caíram**, com a média indo de 6,88 pra
6,19. A página não tinha piorado: a RÉGUA tinha ficado mais fina, e as duas coisas são
indistinguiveis olhando só pro número. Pelo critério antigo aquilo era regressão em oito lentes
e o ciclo nunca fecharia, que é exatamente o "ficar travado" que o dono proibiu.

O que É comparável entre rodadas e o **achado**, porque ele vem com medida e local: da pra
apontar qual correção o causou. Naquela mesma rodada havia UMA regressão de verdade por esse
critério, e ela nada tinha a ver com as notas: a foto 06.webp passou a aparecer duas vezes no
mesmo viewport porque eu tinha trocado o fundo de uma seção sem conferir quem mais usava o
arquivo. Essa trava o ciclo. As oito notas caindo, não.

**Regra derivada, vale pra qualquer métrica de qualidade julgada por agente:** compare
ACHADOS entre rodadas, nunca NOTAS. Nota serve pra declarar na entrega e pra sinalizar
tendência; ela não serve de gate entre rodadas porque o instrumento muda junto com o objeto
medido. O script imprime a queda de nota como SINAL, com esse aviso, e não trava por causa dela.

**A parte que evita a "nota do": a nota vai DECLARADA.** Nota 6,8 escrita na entrega, junto com
o que ficou em aberto e o custo de cada item, e honesta: o dono decide se aquilo basta pro uso
dele. Nota 6,8 escondida atrás da palavra "auditado" e que é nota do. O que esta proibido não é
entregar 6,8, e entregar 6,8 dizendo 8,5.

**O que NUNCA sai do lugar entre rodadas:** crítico e crítico. Se a rodada 4 ainda tem um
crítico confirmado, não existe entrega, existe conserto. O teto de rodadas solta a média, nunca
o crítico.

**>>> GATE 4.2f: `wave.py rodada --criticos N` saiu com código 0? Se NÃO, ele diz exatamente o
que falta: corrigir crítico, desfazer regressão, ou rodar mais uma. <<<**

---

### 4.2g REJEITAR TAMBÉM PRECISA DE MEDIDA (27/08/2026)

Gate existe pra impedir que coisa ruim passe. Este item existe pro contrário: pra impedir que
coisa BOA seja jogada fora por diagnóstico feito no olho. Os dois erros custam, e o segundo e
mais difícil de perceber porque ninguém reclama de um asset que você não usou.

**O caso.** Gerei b-roll no Higgsfield a partir da foto da fachada do cliente, olhei o primeiro
e o último quadro, e rejeitei o clipe inteiro escrevendo em três arquivos que o modelo *"apagou
a porta de entrada e deformou o letreiro"*. O dono perguntou: *"pq vc rejeitou? e só o prompt do
higgsfield ser melhor feito, não?"*. Fui medir quadro a quadro:

| O que eu afirmei | A medida |
|---|---|
| "apagou a porta de entrada" | **falso**: a porta esta nos 121 quadros. No último ela ocupa 57px em vez de 195px, que é ESCORÇO de órbita |
| "deformou o letreiro" | **falso**: letreiro íntegro; o logo girando pra frente na quina e comportamento 3D correto |
| "redesenhou o prédio" | **falso**: o quadro 0 reconstrói a foto do cliente com **0,70px** de erro mediano de reprojecao |

O defeito real era outro e muito menor: um lens flare inventado a partir do quadro 36 e uma
janela que não existe nascendo na empena esquerda no quadro 53, que é uma parede que nenhuma
foto mostra (o modelo TEM que inventar o que ninguém fotografou). Os dois se resolvem com
`ffmpeg -t`, sem gastar crédito e sem regerar: corte no 52, pingue-pongue, 4,42s contínuos e
100% fiéis. **O lever estava na mão e a rejeição não procurou.**

E a parte que fecha a conta: eu tinha extraído o quadro 0 daquele mesmo clipe e publicado como
"a foto limpa da fachada", inclusive escrevendo isso no comentário. O pôster no ar diferia da
chapa real do cliente por **MÃE 74** e do quadro 0 do Higgsfield por **MÃE 0,80**. Ou seja:
rejeitei a ferramenta, joguei fora o movimento, fiquei com os pixels dela e ainda documentei o
contrário.

**As quatro regras que saem disso:**

1. **Material gerado se audita no TEMPO.** A unidade e o QUADRO, não o clipe. Comparar o
   primeiro com o último responde "mudou?" e não responde "QUANDO quebrou?", que é a única
   pergunta que gera decisão. Curva de deriva com resíduo DEPOIS de compensar o movimento de
   câmera: sem compensar, você esta medindo a câmera andando, não o modelo redesenhando.
2. **Escorço não é apagamento.** Numa órbita, tudo encolhe e vira de perfil. Recorte fixo sobre
   câmera em movimento produz "sumiu" que é mentira. Quadro INTEIRO primeiro.
3. **Antes de descartar, procure o corte.** Quase todo clipe gerado tem uma janela inicial fiel,
   porque a deriva acumula. Cortar custa zero. Descartar custa o asset inteiro.
4. **O defeito vale pela JANELA, não pelo arquivo.** Meça o defeito no pixel COMPOSTO, com véu,
   overlay e enquadramento aplicados. Aqui o flare tinha +36 de R-B no arquivo e **3,38 de 255**
   na tela, porque o véu naquela região e 91,5% opaco: invisível, e não justificava corte.

**O que continua valendo como recusa legítima:** o segundo clipe animava funcionarias
identificáveis da empresa, e 83% da mudança sobrevive a compensação de movimento, ou seja o
modelo re-sintetizou rosto de gente real. Isso não é acabamento e nenhum prompt resolve: e
decisão de uso de imagem, e quem decide e o dono, não a skill. A diferença entre este caso e o
da fachada e exatamente a diferença entre uma objeção MEDIDA e uma impressão.

**>>> GATE 4.2g: rejeitou asset gerado? Escreva a MEDIDA que sustenta (qual quadro, qual
número) e diga se existe corte que salva. "Ficou ruim" não é motivo de descarte. <<<**

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
- SEMPRE criar subpasta para páginas novas
- Paths relativos (sem `/` inicial)
- Deploy IMEDIATO após qualquer edição

#### Proteção do projeto no deploy

### Quando deployar
- **Página nova ou mudança visual/estrutural:** deploy acontece DENTRO do Step 4, DEPOIS da wave de auditoria. Nunca antes. (Esta regra vence qualquer outra: ver ENFORCEMENT DO GATE.)
- **Hotfix pos-wave em projeto já no ar** (typo, link, contato, ajuste pontual que não muda layout): deploy imediato após a edição, sem esperar o usuário pedir, seguido dos sweeps rápidos de QA (contato, travessão, links).

### NUNCA Sobrescrever Projetos Existentes
- Ao subir página nova em projeto Cloudflare Pages (ou Vercel, etc.) que JÁ TEM CONTEÚDO, **NUNCA** fazer deploy de uma pasta avulsa que sobrescreva o conteúdo inteiro.
- **SEMPRE** criar uma subpasta dentro do projeto existente para a página nova.
- **Workflow correto:**
  1. Verificar o que já existe no projeto hospedado (checar `dist/public/`, `wrangler.toml`, etc.)
  2. Criar a página nova em subpasta (ex: `dist/public/evento-0326-v1/`)
  3. Copiar a subpasta para dentro do projeto original
  4. Fazer deploy a partir do diretório raiz do projeto original (ex: `dist/public/`)
- **Workflow ERRADO (nunca fazer):** deployar pasta avulsa direto com `wrangler pages deploy minha-pasta/`: isso APAGA tudo que existia antes no projeto.
- Motivo: Cloudflare Pages substitui TODOS os arquivos do deploy anterior. Se você deployar só a subpasta, todas as outras paginas/rotas desaparecem.

---



### 4.4 QA Pos-Deploy

- [ ] Página live = página local (comparar visualmente)
- [ ] GTM dispara (verificar via Tag Assistant)
- [ ] Checkout funciona no domínio live
- [ ] Mobile: testar em dispositivo real (não só emulador)
- [ ] OG tags funcionam (testar sharing debugger)

### 4.5 PROVA DE ENTREGA (screenshots lidos + interação testada, OBRIGATÓRIO)

Falha histórica (auditoria de sessões 02/07/2026, 34 casos de "pronto sem estar"): o script
de screenshot quebrava e a página era entregue mesmo assim (uma proposta comercial), ou a
interação principal nunca foi clicada (uma roleta publicada com o popup morto). Regra dura:

**SE A VERIFICAÇÃO QUEBRAR, A ENTREGA ESTA BLOQUEADA. Conserta a verificação primeiro.
"Não consegui tirar screenshot" NUNCA justifica entregar sem prova.**

1. Rodar o script canônico no DEPLOY REAL (não no preview de build, não no arquivo aberto com
   `file://`). **Única exceção: entrega SEM deploy**, e ai a prova roda contra o servidor local
   com compressão (`python3 scripts/servidor-gzip.py <pasta> <porta>`), com o deploy declarado
   como pendência no bloco de entrega:
   ```bash
   node <dir-da-skill>/scripts/screenshot-prova.js <url-live> <outdir>
   # pagina com interacao principal (roleta, quiz, form, popup, calculadora):
   node <dir-da-skill>/scripts/screenshot-prova.js <url-live> <outdir> --click "<seletor do CTA/interacao>"
   ```
   O script captura desktop (1440px) + mobile (390px) full-page e o estado pos-clique, e
   **roda junto a checagem de IDENTIDADE DA PÁGINA (4.2b)**: title, description, favicon PNG
   quadrado, og:title, og:description e og:image.
   Ele sai com erro (exit 1) se a página não carregar, o clique falhar, o PNG vier em branco
   ou faltar item de identidade. Colar o output dele no bloco de entrega.
   **Cabeçalho fixo no meio do print e ARTEFATO, não defeito (medido em 02/10/2026).** O
   `fullPage` pinta elemento `fixed`/`sticky` na posição da rolagem do momento da captura: se a
   página não estava em scrollY 0, o menu e o "Pular para o conteúdo" saem por cima do título.
   O `screenshot-prova.js` tira o foco, para a página no topo e confirma scrollY 0 em três
   leituras antes do print (imprime a linha `topo ... scrollY 0 confirmado`), e bloqueia se não
   conseguir. **Print de página inteira sai SEMPRE por ele**, nunca por script próprio: foi um
   script próprio que gerou o print torto do aluno. Na dúvida se e defeito real, abra a página em
   scrollY 0 e pergunte ao navegador quem esta em cima do h1 (`elementFromPoint`).
2. **LER os PNGs com a tool Read** (olhar com os próprios olhos) e conferir contra o
   checklist: ID visual real, sem tells de IA, sem seção quebrada, popup/resultado da
   interação visível no pos-clique.
3. Página com interação principal: o `--click` e OBRIGATÓRIO nos DOIS viewports (o script
   já faz). Ele clica no primeiro elemento VISÍVEL do seletor em cada tela (o botão do
   cabeçalho costuma sumir no celular); se nenhum aparece, a mensagem e "o seletor existe mas
   esta oculto neste viewport", e a saída e trocar pelo seletor do botão que aparece ali.
   Link de WhatsApp sem número (`wa.me/?text=...`) sai como `AVISO DESTINO DO LEAD`: o clique
   abre o app sem destinatário, então o número entra em PENDÊNCIAS DECLARADAS e a página não
   recebe tráfego até ele existir. Form de captura: submeter um lead de teste e confirmar o destino (webhook,
   planilha, CRM) antes de declarar pronto.
4. Usar Playwright headless (o script acima), NUNCA o Chrome MCP pra essa prova: em página
   pesada o MCP da timeout de 45s e derruba a verificação (falha recorrente nas sessões).
5. A mensagem final de entrega deve citar os arquivos de screenshot lidos e o resultado
   do teste de interação, junto com o veredito da wave (4.0).

### 4.6 GATE DE USO: ferramenta viva não se pula

```bash
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> checar
```

**A regra, e ela não tem exceção:** toda ferramenta que o 0.0-PRE mediu como RESPONDENDO
precisa aparecer no registro de uso, com evidência. Ferramenta que não respondeu não é cobrada,
porque ali a degradação já foi declarada. Não existe terceira opção. **"O 21st.dev eu pulei"
com o 21st.dev vivo e sem dispensa assinada REPROVA a entrega.**

**Quem aceita dispensa:** só ferramenta OPCIONAL (21st.dev, Higgsfield, Stitch, ffmpeg, skills
de acabamento). Ferramenta CRÍTICA viva (Playwright, `design-taste-frontend`, banco de design,
Openverse, gate de tells) não se dispensa: o script recusa o `dispensar` e o `checar` reprova
dispensa antiga. A lista de críticas vem do `checar-ferramentas.py` (dicionário `CRITICIDADE`).

**Por que este gate e diferente do 0.0-PRE:** aquele garante que a ferramenta RESPONDE. Este
garante que ela foi USADA. São buracos distintos, e tapar só o primeiro não resolve nada: da
pra ter o 21st.dev conectado, verde no verificador, e a página sair 100% feita a mão do mesmo
jeito. O resultado e idêntico ao do MCP morto, só que agora sem nem a desculpa.

**A evidência não é a sua palavra.** Cada registro aponta um artefato que o script confere de
novo na hora do gate: arquivo que precisa existir e ter tamanho, ou trecho que precisa ser
achado no código. Registro cujo artefato sumiu vale como não registrado (o componente do
21st.dev que você trocou por um card a mão depois: o gate pega).

Registre conforme for usando, não no fim de memória:

```bash
# Comando inteiro em cada linha (variavel com comando nao roda no zsh).

# componente que veio mesmo do MCP: o trecho tem que estar no codigo
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> registrar magic --no-codigo "<classe-ou-nome-do-componente>" --em <dir> --detalhe "hero do 21st.dev"
# artefato no disco
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> registrar Playwright --arquivo prova/prova-desktop.png --detalhe "prova de tela lida"
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> registrar "Higgsfield CLI" --arquivo assets/hero-loop.mp4 --detalhe "b-roll do hero"
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> registrar "skill design-taste-frontend" --arquivo index.html --detalhe "passe de gosto, 3 tells removidos"
```

**Não se aplica a esta página? DISPENSE, com motivo, e o motivo vai na entrega:**

```bash
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir-do-projeto> dispensar "ffmpeg/ffprobe" --motivo "esta pagina nao tem video: o gate de video nao se aplica"
```

Dispensa exige motivo de verdade (o script recusa motivo com menos de 15 caracteres e qualquer motivo que contenha "não usei" ou "não usei", em qualquer caixa) e sai marcada no relatório e no
bloco de entrega. A diferença entre dispensar e pular e essa: **dispensa e uma decisão assinada
que o dono lê; pulo e uma decisão escondida que ele descobre pelo resultado, meses depois.**


**O caminho muda o que é cobrado.** A skill roteia em 4 caminhos, e cobrar as mesmas
ferramentas em todos seria o mesmo erro de cobrar ffmpeg numa página sem vídeo:

```bash
# CRIAR, CLONAR e MELHORAR: cobra tudo que estiver vivo
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> checar --caminho criar

# EDITAR (mudanca pontual): cobra so a PROVA do ponto alterado
python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> checar --caminho editar
```

Exigir b-roll do Higgsfield pra trocar o texto de um botão não melhora nada, e gate impossível
de passar honestamente empurra pra dispensar tudo, que e como um gate deixa de valer.
**A regra que continua valendo na edição:** se a MUDANÇA pede a ferramenta (o pedido e "põe um
vídeo no hero"), ela volta a ser cobrada e você registra o uso normalmente.

**>>> GATE 4.6: `uso-ferramentas.py checar` saiu com código 0? Se NÃO, volte e USE o que
esta faltando. Nenhuma explicação substitui rodar de novo verde. <<<**

---

**>>> GATE 4: só entrega com TODOS os itens abaixo verdes. Se NÃO em qualquer um, PARA AQUI é corrige.**
- Auditoria Designer (4.0b) com as notas declaradas e o ciclo 4.2f aprovado
- Auditoria Estrategista (4.1) com as notas declaradas e o ciclo 4.2f aprovado
- QA checklist 4.2 100%: Lighthouse 90+ quando houver navegador (SEO abaixo de 90 aceito só por `noindex`/`is-crawlable`); sem navegador, pendência declarada
- CONSISTÊNCIA DE CONTATO conferida dígito por dígito: colar no bloco de entrega os números achados no HTML e nos `tel:`/`wa.me` (mais de um número distinto sem justificativa REPROVA)
- DIFF DE CLAIMS feito: lista de afirmações x fonte, com o veredito de cada uma
- IDENTIDADE DA PÁGINA (4.2b): output do `screenshot-prova.js` sem REPROVA
- GATE DE TELLS verde: `gate-sem-kicker.py` (sem kicker em caixa alta, sem 01/02/03, sem número gigante)
- GATE DE CLASSE MORTA 4.2c-bis verde (nenhuma classe do código ausente do CSS gerado)
- GATE DE OCLUSÃO 4.2d verde (nenhum texto coberto ou cortado)
- RESPONSIVIDADE verde nas 12 telas (`gate-responsivo.mjs`)
- AUDITOR MASTER 4.2e verde (todas as 8 lentes e todos os gates registrados no `wave.py`)
- CICLO 4.2f fechado (zero crítico, zero regressão, e gravidade secou, piso, convergência ou teto), com a NOTA REAL escrita na entrega
- PASSE DE GOSTO 4.2c rodado, com os itens de composição alterados e a contagem de tells terminando em 0
- Deploy funcionando e verificado (ou entrega sem deploy, abaixo)
- ZERO placeholder visível
- PROVA DE ENTREGA 4.5: screenshots desktop e mobile LIDOS + interação principal testada
- GATE DE USO 4.6 verde (toda ferramenta viva usada, ou opcional dispensada COM MOTIVO que vai na entrega)

**ENTREGA SEM DEPLOY (pasta local, arquivo único, aluno sem conta de hosting) e caminho LEGÍTIMO, não gate pulado:** a prova 4.5 roda contra o servidor local (`python3 scripts/servidor-gzip.py <pasta> <porta>`), e deploy, QA pos-deploy, Lighthouse e `og:image` com URL absoluta entram como PENDÊNCIAS DECLARADAS no bloco de entrega. Tudo o mais do GATE 4 continua valendo igual: wave, identidade, passe de gosto, contato, claims e prova lida com os próprios olhos. **<<<**

---

## Step 5: MEDIR & ITERAR (ongoing, primeiro check 48h)

Ao concluir esta etapa, grave seu JSON e as evidências conforme `references/gate-etapas.md`.
Execute `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 5 --arquivo evidencias/etapa-5.json`.
Saída diferente de zero bloqueia o avanço. Na entrega, execute também `checar 4`.
Este registro do fluxo CRIAR não se aplica aos caminhos com fluxo próprio.

**A página NÃO está pronta quando vai ao ar. Esta pronta quando CONVERTE.**

Referência completa: `references/post-launch.md`

### 5.1 Setup de Medição
- Instalar Microsoft Clarity (grátis) para heatmaps + recordings
- Verificar GTM events: page_view, scroll_depth, cta_click, checkout_click
- Verificar GA4 conversions

### 5.2 Primeiro Check (48h)
Após 48h com tráfego:
1. **Scroll depth:** onde param de scrollar?
2. **Heatmap:** onde clicam (e onde não)?
3. **Recordings:** assistir 10 sessões
4. **Comparar com benchmark** (ver tabela em post-launch.md):
   - Sales page: 2-5% conversão
   - Capture: 15-30%
   - Challenge: 20-40%

### 5.3 Se Abaixo do Benchmark
1. Identificar seção mais fraca (maior drop-off no scroll depth)
2. Formular hipótese: "Se mudar X, Y melhora porque Z"
3. **Voltar ao Step 3** para ajuste CIRÚRGICO (não reformar tudo)
4. Re-deploy e re-medir em 48-72h
5. Se melhorou → documentar como pattern
6. Se piorou → reverter

### 5.4 Se No Benchmark
Documentar o que funcionou na pattern library pessoal:
- Tipo de página, preço, conversão, LCP
- Quais seções engajaram mais
- Quais CTAs performaram melhor
- Aprendizado principal

---













## Anti-Patterns de código (NUNCA FAÇA)

> Esta lista e a de CÓDIGO, CSS e performance. A lista de PROCESSO e de cara de IA esta em
> "ANTI-PATTERNS DE PROCESSO E DE IA", antes dos gates. São duas, e as duas valem.

- Mais de 3 tamanhos de fonte por página
- Espaçamento aleatório (usar grid de 8px)
- Preto puro (#000) em branco puro (#fff)
- Texto colorido em fundo colorido sem checar contraste
- Animações > 500ms para elementos de UI
- Glassmorphism em tudo
- Sombras em tudo
- Gradientes em texto (difícil de ler)
- Animações automáticas que não podem ser paradas
- Remover indicadores de foco
- Texto cinza abaixo de 4.5:1 de contraste
- Alvos de clique < 44px
- **NUNCA usar `cdn.tailwindcss.com` em produção**: e um script JS que gera CSS no browser; Cloudflare Rocket Loader e CDNs bloqueiam/deferrem, quebrando TODO o layout. Sempre compilar para CSS puro
- Paths absolutos (com `/`) em assets quando deploy for em subpasta: quebra em Cloudflare Pages e similares
- Imagens PNG/JPG grandes sem converter para WebP antes do deploy
- Operador `!x.bottom > 0`: precedência errada; usar `x.bottom <= 0`
- CSS duplicado (ex: duas definições de `.btn-gold`): auditar antes de entregar
- **NUNCA usar `section > * { z-index: 1 }` para "subir" conteúdo acima de backgrounds**: cria stacking contexts nos filhos, quebra overlaps entre seções. Usar `z-index: -1` nos backgrounds + `isolation: isolate` na section
- **NUNCA adicionar `overflow: hidden` em seções com imagens/elementos que fazem overlap** (margin negativo) entre seções adjacentes
- **Evitar overlaps entre seções com margin negativo**: extremamente frágil com animações de fundo. Preferir manter conteúdo dentro de uma única seção
- Badges/selos decorativos sem função ("● online", "live feed" falso): cara de vibe-coding
- **NUNCA entregar página com botão de compra/CTA que não dispara, ou sem footer legal**: os 2 maiores tells de vibe-coding (ver `references/anti-vibe-coding.md`)
- **NUNCA corrigir por `str.replace`/`sed` sem `assert` e sem MEDIR o efeito**: quando o trecho
  procurado não existe, a troca falha em SILÊNCIO (código 0, build verde, arquivo intacto). Em
  27/08/2026 duas correções de uma mesma rodada saíram no-op assim: os pontos da linha do tempo
  nunca entraram no DOM (`::before` com `content: none`) e a quebra de grade dos cartões nunca
  aconteceu, porque eu escrevi o alvo de cabeça (`text-brand-dark/85`) e o arquivo tinha `/50`.
  As duas passaram no `vite build` e não mudaram um pixel. Regra: uma linha de `assert velho in t`
  por troca, contagem impressa, e depois `getComputedStyle`/`getBoundingClientRect` no render pra
  confirmar que o pixel mudou. **`✓ built` não é prova de que a edição aconteceu.**

---

## Blueprints Comprovados

Páginas que atingiram 100% de aprovação e estão documentadas como referência completa:

Ao reusar padrões de projetos anteriores, salve blueprints próprios em `references/projects/`
(paletas, animações, gradientes, componentes comprovados) e consulte-os ao criar páginas similares.

### Protocolo de Manutenção dos Blueprints

**Ao concluir qualquer página aprovada pelo usuário (nota >= 9/10 em todas as dimensões):**

1. Verificar se o tipo de página já existe no registro de blueprints do projeto
2. Se não existe: criar `references/{slug-da-pagina}-patterns.md` com:
   - Paleta CSS completa usada
   - Font pairing
   - Layout por seção
   - Vídeos de background (nomes dos arquivos + fontes)
   - Componentes e efeitos especiais usados
   - Lições aprendidas (anti-patterns encontrados)
3. Registrar no arquivo do projeto (references/projects/) a URL, o tipo e o caminho do arquivo
4. **Não criar blueprint de páginas em andamento**: apenas após aprovação final do usuário

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
- CTA Gallery: https://cta.gallery: referência opcional antes de qualquer CTA section
- Navbar Gallery: https://navbar.gallery: referência opcional antes de qualquer NavBar
- Component Gallery: https://component.gallery: 60 componentes × 95 design systems × 2.676 exemplos

### Por tipo de site
- Saaspo: https://saaspo.com: 2.900 páginas SaaS, 709 seções, filtros por tipo/stack/indústria
- Curated Design: https://curated.design: curadoria premium por nicho (Tech, AI, Finance, Agency, E-commerce)
- Landing Love: https://landing.love: 1.946 sites com vídeo full-page; categorias: `/categories/minimal/`, `/dark-mode/`, `/saas/`, `/3d-website/`, `/technology/`
- Rebrand Gallery: https://rebrand.gallery: identidade visual, rebrands de marcas grandes

### Mobile / UX patterns
- Mobbin: https://mobbin.com: 599.800 screenshots de 1.150+ apps, busca por padrão de UI
