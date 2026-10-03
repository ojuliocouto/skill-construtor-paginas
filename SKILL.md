---
name: construtor-paginas
version: 3.1.0
description: "Use quando o usuário quiser criar uma página web (landing page, sales page, captura, institucional, portfólio, dashboard), clonar uma página existente a partir de URL ou PDF, refazer/redesenhar uma página (v2, redesign, upgrade visual), otimizar/auditar o visual de uma página já publicada, ou editar algo pontual numa página que já existe (trocar texto, headline, cor, preço, adicionar/remover seção, corrigir mobile). Sinais: criar página, landing page, hero section, clonar site, copiar página, refazer página, pdf para html, melhorar página, deixar bonito, editar página, trocar texto, mudar cor, ajustar botão, adicionar seção, arrumar mobile. Stacks: HTML+Tailwind (padrão), React, Next.js, Vue, Svelte."
---

# Construtor de Páginas (v3)

Constrói, clona, melhora e edita páginas web que saem no nível das melhores do ramo, não só
aprovadas em gate. A versão 3 depende de **três coisas, e só delas**:

1. **A skill `frontend-design`**, acionada de verdade para escrever o plano visual antes do
   código.
2. **Auditores adversariais**: 9 lentes independentes que procuram o defeito, inclusive a que
   compara a página com as referências.
3. **Pesquisa de referências reais**: 6 a 10 páginas de verdade, abertas num navegador headless,
   printadas e lidas, antes de qualquer decisão visual.

Decisão do dono (02/10/2026): *"se o construtor só precisar do front end designer e
auditores, e pesquisa de referências, pra mim tá ótimo"*. O objetivo é a página sair muito
boa; os gates mecânicos são o piso, não a meta.

**`<dir-da-skill>`** em todo comando = a pasta onde esta skill foi clonada, a que tem este
SKILL.md. Troque pelo caminho real antes de colar. **`<dir>`** = a pasta do projeto da página.
Cada comando vai inteiro na linha: guardar comando em variável não roda no zsh.

**Glossário curto:**
- **gate**: checagem que REPROVA (sai com código 1) e impede avançar.
- **lente**: um auditor com um critério só; as 9 lentes formam a rodada de auditoria.
- **tell**: sinal que entrega página feita por IA (rótulo em caixa alta em cima do título,
  número gigante decorativo, numeração 01/02/03, brilho difuso atrás do texto).
- **kicker**: rótulo curto em caixa alta, com letra espaçada, em cima do título. Proibido.
- **primeira dobra**: o que aparece na tela antes de rolar.
- **CTA**: o botão da ação principal (agendar, comprar, chamar no WhatsApp).
- **og:image**: a imagem que aparece quando o link é compartilhado.

---

## Quando acionar

ANTES de qualquer código, sempre que o pedido for:

1. **Criar** uma página nova (landing, venda, captura, institucional, serviço local, portfólio)
2. **Clonar** uma página existente, de URL ou PDF
3. **Melhorar** uma página que existe e vai continuar existindo ("melhora", "otimiza", "deixa
   mais bonita", "refaz", "v2", "redesign"), inclusive uma variante visual do mesmo conteúdo
4. **Editar** algo pontual ("troca o headline", "muda a cor do botão", "arruma no celular")

Pedido de página entra por esta skill mesmo que o usuário cite outra skill de design pelo
nome: a `frontend-design` roda DENTRO do caminho, no passo do plano visual. Só pedido de uma
etapa isolada ("me dá uma direção estética", "critica este layout") roda a outra skill sozinha.

---

## Roteamento: escolha o caminho ANTES de qualquer coisa

Declare na primeira resposta, em uma linha: `Caminho: CRIAR (página nova do zero).`

| Sinal no pedido | Caminho | Arquivo com o fluxo |
|---|---|---|
| não existe página ainda | **CRIAR** | `references/caminhos/criar.md` |
| "clona / copia / replica" + URL ou PDF | **CLONAR** | `references/caminhos/clonar.md` |
| clone **e** melhoria no mesmo pedido ("clona e deixa foda") | **CLONAR + ELEVAR** | `references/caminhos/clonar-elevar.md` |
| página existe e o pedido é elevar o todo, ou outra linguagem para o mesmo conteúdo | **MELHORAR** (inclui VARIANTE VISUAL) | `references/caminhos/melhorar.md` |
| página existe e o pedido é um ponto específico | **EDITAR** | `references/caminhos/editar.md` |

Abra o arquivo do caminho e siga na ordem. **Na dúvida entre MELHORAR e EDITAR, pergunte:**
mexer numa coisa nomeada é EDITAR; revisar a página é MELHORAR. **Na dúvida entre CLONAR e
CLONAR + ELEVAR, pergunte:** fidelidade e elevação são réguas opostas, e rodar a errada entrega
uma página que o dono reprova em dois segundos.

| Caminho | Referências | Plano visual (`frontend-design`) | Auditores | Gate próprio |
|---|---|---|---|---|
| CRIAR | 6 a 10 páginas | sim | 9 lentes | os oito passos com gate |
| CLONAR | a original | não (identidade dada) | 9 lentes, `--caminho clonar` | fidelidade lado a lado |
| CLONAR + ELEVAR | original + 6 a 10 | sim, com a identidade travada | 9 lentes | 4 de 6 eixos elevados |
| MELHORAR | 6 a 10 páginas | sim, partindo da atual | 9 lentes | baseline e não regressão |
| EDITAR | não | não | não | escopo travado e regressão |

---

## As três dependências, em uma tela

### Pesquisa de referências (passo b do CRIAR)
Busca na web por páginas REAIS: pelo menos 2 do mesmo tipo de negócio e 2 de design de alto
nível, 6 no mínimo. Cada uma aberta no Chromium headless e printada na primeira dobra e numa
seção do meio:

`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> <url> ...`

Depois de ABRIR cada PNG, escreva o que ela faz bem em composição, tipografia, imagem e ritmo, e
o princípio que se leva dela (nunca frase nem layout idêntico). Gate:

`python3 <dir-da-skill>/scripts/gate-referencias.py --projeto <dir>`

Método completo: `references/pesquisa-de-referencias.md`.

### Plano visual pela `frontend-design` (passo c do CRIAR)
Acione a skill pelo Skill tool, com o briefing e a síntese das referências. Ela trabalha em
duas passadas (rascunho e revisão contra o padrão genérico) e o resultado vai para
`<dir>/plano-visual.md`: assunto e trabalho da página, direção, paleta de 4 a 6 cores com hex,
tipografia com escala, como a imagem entra, ritmo das seções, a assinatura e o que mudou na
revisão. Nenhuma linha de código antes dele. O banco de design (`scripts/search.py` +
`data/*.csv`) é consulta opcional: dá ideia, nunca decide.

### Auditores adversariais (passo g do CRIAR)
As 9 lentes de `references/auditores.md`: design-critic, assets-auditor, visual-auditor,
motion-auditor, responsive-auditor, cro-auditor, a11y-auditor, content-auditor e
**comparacao-referencias** (a página está no nível das referências printadas? Se não, volta ao
plano visual). A rodada roda com **subagente auditor independente quando o ambiente permite**;
quando não permite, a mesma checagem em sequência serve para achar defeito, mas é
autoavaliação, e **nota de autoavaliação não libera entrega**: o `wave.py rodada` responde
AUDITORIA INDEPENDENTE PENDENTE até uma rodada de outra sessão ou de outra pessoa. Cada lente
se registra no `scripts/wave.py` com `--origem`; o master confere que todas rodaram e o ciclo
decide se entrega.

---

## O caminho CRIAR, em resumo

Detalhe, comandos e gates de cada passo: `references/caminhos/criar.md`.

| Passo | O que sai | Gate que bloqueia |
|---|---|---|
| a. Briefing | o que vende, para quem, oferta, preço, ação, material real; o que falta vira pendência do cliente | `gate-etapas.py registrar 0` |
| b. Referências | 6 a 10 páginas reais printadas e lidas, `referencias/sintese.md` | `gate-referencias.py` e `registrar 1` |
| c. Plano visual | `plano-visual.md` pela `frontend-design` | `registrar 2` |
| d. Copy | texto de cada seção, só com fato do briefing, e a tabela frase da página -> linha do briefing | `gate-verdade.py` e `registrar 3` |
| e. Construção | HTML + Tailwind compilado, hero primeiro, imagens com licença | `registrar 4` |
| f. Gates mecânicos | sem kicker, classes mortas, 12 telas (botão em uma linha, botão a 2 telas), oclusão, simetria, texto, verdade, publicação, identidade, uso, referências | cada exit no `wave.py gate` |
| g. Auditores | 9 lentes por subagente independente, ciclo fechado, passe de gosto com 0 tells | `wave.py checar` e `wave.py rodada` |
| h. Prova | prints desktop 1440 e celular 390 e 360 lidos, clique testado, deploy só da `dist/`, bloco de entrega | `registrar 5` |

**Ordem:** briefing, referências, plano, copy, código. O plano vem das referências; a copy
preenche o ritmo que o plano desenhou e nunca inventa fato; o código segue os dois.

---

## Regras que valem em todos os caminhos

- **Nunca inventar identidade visual.** Logo, cor e fonte que o cliente indicou se usam como
  são. Logo ilegível a 40px: aumente ou peça outra versão, nunca recrie em texto.
- **Nunca inventar dado.** Preço, número de alunos, resultado, prazo, credencial, depoimento:
  se não está no briefing, não existe. Foto, alt e JSON-LD também afirmam e entram no diff.
- **Imagem real com licença registrada.** Material do cliente primeiro; senão banco de licença
  livre escolhido pelo que as referências ensinaram, com a licença em `imagens/LICENCAS.md` e
  "imagem ilustrativa" quando a foto não é do cliente.
- **Zero travessão** (U+2014 e U+2013), **zero emoji**, acentuação correta, contato idêntico
  dígito por dígito em toda a página.
- **Sem kicker, sem 01/02/03, sem número gigante decorativo** (`references/preferencias-de-design.md`).
- **Fora do domínio final, `noindex`.** Página de cliente real em endereço de teste não compete
  na busca com o site dele.
- **Nunca sobrescrever projeto publicado.** Página nova entra em subpasta do projeto existente.
- **Prova lida antes de "pronto".** Print desktop e celular aberto com os próprios olhos. Se a
  verificação quebrar, a entrega está bloqueada: conserte a verificação, nunca entregue sem prova.

**Precedência de gosto:** identidade real do cliente, depois `references/preferencias-de-design.md`,
depois o plano visual. Nenhuma skill de design passa por cima dessa ordem.

---

## Bloco obrigatório da entrega (CRIAR, CLONAR, CLONAR + ELEVAR, MELHORAR)

```
AUDITORES: <subagente independente | sessão independente | autoavaliação (não libera)> | nota por lente | média | críticos: <lista ou nenhum> | ciclo: <saída do wave.py rodada>
REFERÊNCIAS: <N> páginas lidas | comparacao-referencias: <aprovado | reprovado> e por quê
IDENTIDADE DA PÁGINA: title / description / favicon PNG quadrado / og:title / og:description / og:image (saída do screenshot-prova.js)
PASSE DE GOSTO: tells antes -> depois (o depois é 0) + o que foi inspecionado
PROVA: arquivos de print LIDOS + resultado do clique da interação principal
PENDÊNCIAS DECLARADAS: o que só o cliente tem, o que rodou degradado, deploy e og:image absoluta sem domínio
```

No EDITAR o bloco é menor: escopo travado, checklist de regressão, prova do ponto alterado e
pendências. Faltou uma linha do bloco = gate pulado = não entregue.

---

## Antes de começar e depois de terminar

**Primeiro comando, em qualquer caminho:**

`python3 <dir-da-skill>/scripts/checar-ferramentas.py`

Crítico, e só isto: python3, node, Playwright com o Chromium baixado e a skill `frontend-design`
instalada. Faltando crítico, conduza a instalação (o comando sai pronto na tela) em vez de só
avisar. Opcional ausente não bloqueia nada. `--opcionais` também checa os MCPs e a rede.

**Contexto de projeto (local, fora do Git):** se existir `references/projects/<projeto>.md`,
leia antes do código, e a sessão mais recente do mesmo projeto em `references/sessions/`.
Respeite as decisões já tomadas ali.

**Ao concluir:** registre `references/sessions/AAAA-MM-DD-<projeto>.md` (o que foi pedido, o que
foi entregue, o que se aprendeu, arquivos alterados) e atualize `references/projects/<projeto>.md`.
Modelos em `EXAMPLE.md`. Aprendizado novo da skill vira regra no arquivo do caminho que a
executa, nunca uma lista solta no fim de um arquivo.

---

## Mapa da skill

**Scripts (`scripts/`):**

| Script | Para que | Passo |
|---|---|---|
| `checar-ferramentas.py` | verificador: crítico x opcional, manda cada ferramenta fazer algo | antes de tudo |
| `gate-etapas.py` | sequência e integridade das evidências de cada passo | a a h |
| `capturar-referencias.mjs` | abre a URL no Chromium headless e grava primeira dobra e meio | b |
| `gate-referencias.py` | reprova sem 6 prints reais lidos, 2 de cada tipo | b, f |
| `search.py` + `core.py` + `data/` | banco de design, consulta opcional | c |
| `assets-search.py` | fotos com licença aberta, sem chave (Openverse) | e |
| `screenshot-prova.js` | prints desktop e celular em scrollY 0, identidade da página, clique | e, f, h |
| `servidor-gzip.py` | serve o build local com compressão | f |
| `gate-sem-kicker.py` | kicker, 01/02/03 e número gigante, em HTML, Tailwind e `.css` | f |
| `gate-classes-mortas.py` | classe do código que não existe no CSS gerado | f |
| `gate-responsivo.mjs` | 12 telas: rolagem lateral, CTA na dobra, toque 44px, corpo 14px, botão em uma linha, botão a 2 telas no celular; no celular, fixo somado até 15%, 1 botão por tela, nenhum botão sob a barra e foto do herói com 35% da 1a tela | f |
| `gate-oclusao.mjs` | texto coberto por camada ou cortado pela caixa | f |
| `gate-simetria.mjs` | itens paralelos em caixas iguais, passos fora da coluna ao lado do título, colunas que terminam juntas, título com título nos cards vizinhos (4 px) e sem buraco interno | f |
| `gate-texto.mjs` | viúva em título e subtítulo (h1 a h4, dt, summary) de 320 a 1440, item em minúscula, itálico colorido repetido | f |
| `gate-composicao.mjs` | cara de template: mais de 2 seções seguidas com o mesmo esqueleto, desenho sem `data-desenho`, ícone de biblioteca ou repetido | f |
| `gate-movimento.mjs` | visita real: 8 s parada no topo, depois rola; reprova animação que roda fora da tela e página que não anima ao chegar | f |
| `gate-verdade.py` | toda promessa (e a meta description) com linha do briefing que sustente | d, f |
| `montar-dist.py` + `gate-publicacao.py` | `dist/` só com o que a página usa, e o gate que reprova a casa na publicação | f, h |
| `gate-video.mjs` | as 7 checagens de vídeo (só em página com vídeo) | f |
| `uso-ferramentas.py` | Playwright e `frontend-design` foram usados de verdade | f |
| `wave.py` | registro das 9 lentes, auditor master e ciclo de rodadas | f, g |
| `lado-a-lado.py` | duas imagens lado a lado na mesma escala | g, CLONAR, MELHORAR |
| `extrai-identidade.mjs` | paleta real, variáveis CSS, h1, CTA e imagens de uma URL | CLONAR |

Testes: `scripts/test-*.py` e `scripts/test-*.cjs` (lista e comando no `README.md`).

**Referências (`references/`):**

| Arquivo | Quando ler |
|---|---|
| `caminhos/criar.md`, `caminhos/clonar.md`, `caminhos/clonar-elevar.md`, `caminhos/melhorar.md`, `caminhos/editar.md` | o fluxo de cada caminho, sempre |
| `pesquisa-de-referencias.md` | passo b: como achar, capturar, ler e registrar |
| `auditores.md` | passo g: as 9 lentes, o schema, a régua do ciclo, o passe de gosto |
| `preferencias-de-design.md` | antes do plano visual, em toda página |
| `anti-vibe-coding.md` | os tells V1 a V15 que a lente design-critic conta |
| `copy-servico-local.md` | passo d, para estúdio, clínica, consultório, salão |
| `page-types.md` | passo d, seções por tipo de página (o modelo geral) |
| `assets-sem-chave.md` | passo e, foto com licença aberta e como creditar |
| `gate-etapas.md` | campos de cada etapa e quando re-registrar |
| `projects/`, `sessions/` | contexto local de projeto (fora do Git) |
| `arquivo/` | referências da v2, fora do fluxo; nenhum caminho depende delas |

---

## Lições que viraram regra (cada uma custou retrabalho medido)

- **Medir com compressão.** Servida sem gzip, a versão nova apareceu pior (LCP 7,3 s contra
  6,3 s); com gzip, empataram. Use `servidor-gzip.py`.
- **Celular de verdade é Playwright com `isMobile`.** Janela estreita de navegador de desktop dá
  diagnóstico falso de corte na direita.
- **Detalhe se confere em recorte 1:1.** Um rótulo de 13px vira 4px num print de página inteira
  reduzido; o defeito era invisível na imagem usada para aprovar.
- **Print de página inteira só pelo `screenshot-prova.js`.** Cabeçalho fixo no meio do print é
  artefato de rolagem, não defeito; o script confirma scrollY 0 antes.
- **Build verde não prova pixel.** Troca por script sem `assert` falha em silêncio; classe de
  utilitário inválida passa no build e morre no CSS (`gate-classes-mortas.py`).
- **Comentário que afirma comportamento só depois de medido.** Três vezes o comentário dizia
  "fica sólido" e o código entregava outra coisa, e o comentário protegia o defeito.
- **Gate que mede cor espera a região estabilizar**, nunca um prazo fixo: com animação de
  entrada, prazo fixo mediu 1,09:1 numa composição de 12,4:1.
- **Compare achados entre rodadas, nunca notas.** Numa rodada mais minuciosa as oito notas
  caíram e a página não tinha piorado; a régua tinha ficado mais fina.
- **Favicon é quadrado.** Redimensionar foto 3:2 preservando proporção dá 32x21; recorte primeiro.
- **Rejeitar asset também exige medida.** "Ficou ruim" não é motivo de descarte; diga qual
  quadro, qual número, e se existe corte que salva.

---

## Ferramentas opcionais (nenhuma bloqueia nada)

A skill funciona inteira sem nenhuma destas. Quem tiver, pode usar como reforço DENTRO dos
passos acima, sem pular nenhum gate; o `uso-ferramentas.py` aceita o registro e nunca cobra.
A documentação detalhada da v2 está em `references/arquivo/`.

| Ferramenta | Onde pode ajudar | Custo |
|---|---|---|
| 21st.dev (MCP) | componente pronto de interface no passo e | chave gratuita |
| Google Stitch (MCP) | wireframe rápido antes do código | conta Google |
| Higgsfield (CLI + `scripts/higgsfield.py`) | vídeo ou movimento gerado em bloco | plano pago |
| nanobanana / Gemini | imagem gerada para conceito de produto (nunca rosto de pessoa real) | chave de API |
| brandkit | identidade nova quando o cliente não tem marca nenhuma | skill separada |
| design-taste-frontend, high-end-visual-design | segunda opinião anti-slop e acabamento | skills separadas |
| animate, magicui, shadcn/ui | movimento e componentes em React, quando a stack for React | skills e pacotes |
| Pexels (`PEXELS_API_KEY`) | foto e vídeo de banco sem exigência de crédito | chave gratuita |
| MCPs pagos de imagem, vídeo ou dados | qualquer reforço pontual | variável |

Regra para qualquer uma: se entrou, o resultado passa pelos mesmos gates e auditores; se
falhou ou não existe, a página segue pela rota padrão (HTML + Tailwind, movimento em CSS, foto
de licença livre) e isso não é degradação.
