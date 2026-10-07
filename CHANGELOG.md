# Changelog

## 3.5.3 (06/10/2026): receitas de movimento, lente alinhada e vídeo de prova

O dono disse da página aprovada: "as animações da página ficaram foda, todas as páginas criadas com
essa skill têm que ser criativas assim". O movimento dela não estava na skill.

### Adicionado
- `references/receitas-de-movimento.md`: 15 receitas (14 da v7 e o painel de cor na navegação interna, do protótipo v8) com HTML, CSS e JS reais, reserva sem
  script e com movimento reduzido, custo no celular e a gramática de base (uma curva, 0,25 a 2,0 s,
  observador 0,18 e -6%, estado escondido só atrás de `.js`).
- `scripts/provar-painel.mjs`, `test-painel.cjs`, `roteiro-demo-receitas.json`: a prova do painel de cor (cobre 100% da janela, solta no fim, foco, endereço, voltar, só clique simples em link marcado, movimento reduzido, sem script, teto de tempo, token `--marca`, 390 e 360) e o vídeo do demo com o painel cobrindo a tela.
- `references/receitas/demo.html`: página autocontida com um bloco por receita (`data-receita`).
- `scripts/provar-receitas.mjs`, `test-receitas.py`, `test-receitas-navegador.cjs`, `test-linhas.cjs`
  (+ `scripts/fixtures/`): a prova de pixel, sem script e movimento reduzido; o texto em linhas
  re-divide depois da fonte e na mudança de largura (defeito medido na v7).
- `scripts/gravar-video.js`, `scripts/video/*`, `scripts/roteiro-pagina.json` e dois testes: vídeo
  da rolagem em desktop e celular (copiado do criador-dash; ação nova `rolar_pagina`; faixa 10 a 90 s).
- `gate-etapas.py`: a etapa 5 exige o campo `video` (os dois `.webm`, conferidos e no SHA-256).

### Alterado
- `auditores.md` (lente de movimento) e `anti-vibe-coding.md` (sinal 2): reprova o MESMO fade em
  bloco, não a quantidade de itens revelados; o teto fixo de revelações saiu de todos os arquivos.
- `ritmo-e-animacao.md`, `plano.md` e `caminhos/criar.md`: a animação de cada seção sai do repertório
  ou declara `criação nova: <motivo>`; o passo h cobra o vídeo.

## 3.5.0 (04/10/2026): o padrão da v7 vira regra e gate

O dono reprovou a v6 da página do estúdio ("correta e genérica") e a v7 saiu muito melhor. O
relatório da v7 listou 15 decisões que a 3.4 não exigia nem orientava. As que se medem viraram
gate; as outras, referência curta. Teste vermelho antes e verde depois em cada peça
(`relatorios/v35-tdd-vermelho.txt` e `v35-testes.txt`).

### Adicionado
- `scripts/gate-ritmo.mjs` (+ `ritmo-regras.mjs`): reprova duas seções VIZINHAS com o mesmo
  esqueleto (posição do título x tipo de corpo) e mais de 1 "título centralizado + cartões". Gate
  à parte do `gate-composicao.mjs`: distingue cartões iguais de comparação assimétrica e foto de
  desenho fixo, e a decisão é testada sem navegador.
- `scripts/anim.mjs`, `scripts/prancha.py`, `scripts/gate-animacao.py`: o par de prova de animação
  da v7, sem caminho nem seletor fixo (uma lista `secoes.json`), e o gate que reprova seção com
  menos de 2% de pixels mudando entre início e fim (1440 e 390), mais de 2 seções com o mesmo tipo
  de animação e menos pranchas que linhas da tabela do plano.
- `scripts/sobreposicao.mjs`: varredura de rolagem que mede a interseção entre um elemento
  sticky e os blocos que ele não pode cobrir.
- `scripts/medir-dobra.mjs`: aviso "imagem ilustrativa" e área de foto contra desenho na primeira
  tela, usado pelo `gate-imagens.py --url`.
- `references/ritmo-e-animacao.md`, `imagem.md`, `densidade-servico-local.md`, `vh-estavel.md`,
  `sticky-e-sobreposicao.md`, `texto-em-linhas.md`.
- Testes: `test-animacao.py` e `test-gates-v35.cjs` (um processo de navegador por vez).

### Mudado
- `gate-plano.py` cobra `Momento assinatura:` (elemento, 3 ou mais seções, estados com `->`), a
  tabela `Composição por seção` (Seção, Desktop, Celular, Animação; uma linha por seção, sem célula
  vazia, no máximo 2 seções com o mesmo tipo) e `Material da cliente pedido:`.
- `gate-imagens.py`: foto repetida entre seções (pHash a menos de 10 bits ou mesma origem),
  nitidez relativa (laplaciano da foto dividido pelo da foto desfocada: abaixo de 2,5 reprova, abaixo de 6 avisa), "imagem ilustrativa" visível na
  primeira tela, 60% de foto na primeira tela com `--url`, e pessoa identificável de banco sem
  autorização deixa de bloquear a página de teste: vira aviso de tráfego real (`--trafego-real` a
  reprova).
- `gate-simetria.mjs`: falha em elemento com `data-assimetrico` vira aviso.
- `gate-responsivo.mjs`: filho de contêiner com `overflow-x: auto` e `scroll-snap-type` não é
  estouro; imprime scrollWidth e innerWidth medidos.
- `wave.py`: gates `ritmo` e `animacao` (fora do clone fiel).
- `SKILL.md` (3.5.0, 327 linhas), `criar.md`, `plano.md`, `preferencias-de-design.md` e README.

## 3.4.0 (03/10/2026): etapa PLANO antes de qualquer código

Decisão do dono: "seria bom se essa skill desse opções de visual e tipos de seções pro cara,
inclusive uma etapa de planejamento pra copy, pixel, código, referências". No CRIAR, entre as
referências (b) e o plano visual (c), entra o passo b2: um `PLANO.md` único que o aluno aprova
antes do código. Teste vermelho antes e verde depois em cada peça.

### Adicionado
- `references/plano.md`: a etapa, o modelo do `PLANO.md` em 7 seções (referências, visual,
  seções, copy, pixel e rastreamento, código e publicação, aprovação) e o que o gate cobra.
- `references/secoes/`: cardápio de 18 formatos de seção para 8 objetivos (primeira dobra, dor,
  mecanismo ou diferencial, prova, oferta, como funciona, FAQ, fecho), cada um com quando usar,
  estrutura, armadilha e um HTML mínimo que passa no `gate-sem-kicker.py`.
- `references/rastreamento.md`: snippet de Meta Pixel e GA4 com os IDs em `window.RASTREIO`
  (vazios no repositório), os eventos `clique_whatsapp`, `clique_cta`, `rolagem_50`,
  `rolagem_90` e `envio_formulario` por `data-evento`, e onde o aluno pega cada ID.
- `scripts/previa-direcoes.mjs`: as 3 primeiras dobras em PNG (1440 e 390) e o
  `plano/direcoes.png` lado a lado; `--miniaturas` grava as miniaturas do cardápio.
- `scripts/gate-plano.py`: reprova o `PLANO.md` sem as 7 seções, as 3 prévias e a comparação,
  a copy com sustentação, o pixel declarado e os eventos, com ID real no texto ou com alguma
  aprovação desmarcada.
- `scripts/gate-rastreamento.py`: reprova a `dist/` sem o pixel e os eventos que o plano pediu.
- Testes: `test-gate-plano.py`, `test-secoes.py`, `test-previa-direcoes.cjs`.

### Mudado
- `SKILL.md` e `references/caminhos/criar.md`: passo b2 obrigatório; o plano visual detalha a
  direção escolhida; a copy parte da aprovada; `gate-plano.py` antes da construção e
  `gate-rastreamento.py` nos gates mecânicos.
- `wave.py`: gates `plano` (só no CRIAR) e `rastreamento`.

## 3.3.0 (03/10/2026): "correta, mas vazia", os buracos que a auditoria da v5 achou

Um auditor independente deu 7,0 à v5 da página do estúdio, com todos os gates verdes: nenhuma
pessoa na página, desenhos que liam como wireframe, revelação por grupo no celular, ícone da v3
e o dono só no rodapé. Cada buraco virou medida, com teste vermelho antes e verde depois.

### Adicionado
- `scripts/gerar-icones.mjs`: favicon e apple-touch-icon gerados de `icones/icone.svg`
  (`data-motivo` = "Ícone do site" do plano), com registro em `icones/icones.json`.

### Mudado
- `gate-composicao.mjs`: desenho que lê como wireframe (80% ou mais de retas alinhadas e
  retângulos), linha do tempo que passa do último marco (1440 e 390), público de pessoas sem
  figura humana na primeira tela (`--publico` ou `--projeto`) e traço fino ou destaque abaixo
  de 3:1 contra o que está embaixo dele.
- `gate-movimento.mjs`: item que termina de animar antes de entrar na tela numa rolagem de
  300 px/s (1440, 390 e 320) e `scroll-behavior: smooth` com movimento reduzido reprovam.
- `gate-simetria.mjs`: texto das caixas da mesma linha com mais de 1 linha de diferença
  (regra 20) e passos lado a lado sem caixa (regra 15).
- `gate-texto.mjs`: viúva em parágrafo na fonte do título e em texto de caixa.
- `gate-publicacao.py`: comentário interno no HTML publicado e, com o plano ao lado da `dist/`,
  ícone que não saiu do SVG da identidade atual.
- `gate-imagens.py`: o título do crédito é o da fonte; ilustração própria não pede licença.
- `gate-verdade.py`: o dono ou a profissional que o briefing nomeia aparece no corpo.
- `wave.py`: a `comparacao-referencias` responde `--gosto bonito|correto`; "correto" ou sem
  resposta volta ao plano visual.

## 3.2.0 (02/10/2026): os buracos de gate que a auditoria independente da v4 achou

Um auditor independente deu 6,5 à v4 da página do estúdio com todos os gates verdes. Cada
defeito que passou virou medida, com teste vermelho antes e verde depois.

### Adicionado
- `scripts/gate-movimento.mjs`: visita real (8 s parada no topo, depois rolagem); animação que
  roda com a seção fora da tela reprova, e menos de 2 seções animando ao chegar reprova. Pegou o
  `setTimeout` de 3 s da v4.
- `scripts/gate-composicao.mjs`: mais de 2 seções seguidas com o mesmo esqueleto (posição do
  título + corpo) reprova; SVG sem `data-desenho`, metáfora de biblioteca e traçado repetido
  reprovam. Tell V17 "esqueleto repetido".
- `scripts/gate-imagens.py`: tabela fixa em `imagens/LICENCAS.md`; licença com versão e link,
  pessoa identificável sem autorização, crédito completo no HTML (CC BY-SA alterada diz "mesma
  licença") e "imagem ilustrativa" no og-image.
- `scripts/gate-relatorio.py`: número de medida no relatório cita o arquivo de texto do gate e
  está nele; medida anterior à `dist/` reprova.
- `screenshot-prova.js --com-320`.

### Mudado
- `gate-texto.mjs`: 320 px e subtítulos (h3, h4, dt, summary, `[data-titulo]`).
- `gate-simetria.mjs`: título com título nos cards vizinhos (4 px), buraco interno, e
  ilustração `aria-hidden` em fluxo conta como conteúdo da coluna.
- `gate-responsivo.mjs` no celular: fixo somado até 15%, 1 botão de ação por tela, nenhum botão
  a menos de 8 px da barra de baixo, foto do herói com 35% da 1a tela.
- `gate-etapas.py`: etapa 2 exige `secoes` ({secao, tratamento, referencia}, nunca o mesmo em 3
  seguidas) e valida `icones`.
- `uso-ferramentas.py`: registro guarda o sha256; plano alterado depois do registro reprova.
- `wave.py`: gates `movimento`, `composicao` e `imagens` no master.

## 3.1.0 (02/10/2026): o que a auditoria independente da v3 achou vira gate

Um auditor independente deu 5,5 à página do estúdio feita pela v3, que a autoavaliação tinha
aprovado com média 7,78 e "tells 0". Cada achado grave virou regra medida, com teste vermelho
antes e verde depois.

### Adicionado
- `scripts/gate-simetria.mjs`: itens paralelos (3 a 6 do mesmo tipo) com topo e altura iguais
  com 1 px de tolerância depois da animação; escada reprova; lista vertical ao lado do h2 reprova
  no desktop; colunas vizinhas com mais de 80 px de diferença na base reprovam.
- `scripts/gate-texto.mjs`: viúva em h1 e h2 em 6 telas, item de texto que começa com minúscula
  e mais de um trecho em itálico colorido; aviso a partir de 10 filetes de 1 px.
- `scripts/gate-verdade.py`: tabela `evidencias/sustentacao.md` (frase da página -> linha do
  briefing, mais os padrões de Não afirmar por pendência), cobrando também title, meta
  description e og:description.
- `scripts/montar-dist.py` e `scripts/gate-publicacao.py`: o deploy sai só de `dist/`, com o
  que a página referencia (CSS em linha opcional); pasta de trabalho, .md, JSON de auditoria,
  fonte de build e arquivo não usado reprovam.
- `scripts/test-preferencias.py`: cada item numerado da memória de gosto do dono precisa de par
  `gosto:N` nos arquivos de preferência (pula com aviso quando a memória não existe).
- Tell V16 "jornal de filetes" em `references/anti-vibe-coding.md`.

### Mudado
- `gate-responsivo.mjs`: botão em uma linha até 768 px e, no celular, trecho de mais de 2
  telas sem botão visível reprova.
- `wave.py`: `--origem` em cada lente; autoavaliação não libera entrega (AUDITORIA INDEPENDENTE
  PENDENTE); gates `simetria`, `texto`, `verdade` e `publicacao` no master.
- `gate-etapas.py`: etapa 2 exige `foto_publico` (público -> foto -> por quê) e etapa 3 exige
  `sustentacao`.
- `references/preferencias-de-design.md`: itens 14 a 17, 19 e 20 da memória de gosto (passos e
  itens paralelos em grade de caixas iguais, FAQ e fecho animados, ícone próprio animado, botão
  do topo sem preço, preço composto num bloco, sem pílula em mockup) e as regras novas de foto,
  texto e publicação. O item só do dono vai para o arquivo local.
- `references/caminhos/criar.md` e `references/auditores.md`: foto contra o público, nada por
  cima de pessoa, logo de terceiro, tabela de sustentação, subagente auditor independente.

## 3.0.0 (02/10/2026): enxuto, três dependências

Decisão do dono: "se o construtor só precisar do front end designer e auditores, e pesquisa
de referências, pra mim tá ótimo". O objetivo é a página sair muito boa, não só passar em gate.
O teste com aluno do mesmo dia mostrou o problema da v2: a página passou em todos os gates
mecânicos e saiu com cara de rascunho, porque a direção visual vinha de um banco de CSV e de
memória, e nunca de página de verdade.

### Migração da v2 para a v3

| Na v2 | Na v3 |
|---|---|
| SKILL.md com 2.642 linhas e 6 steps espalhados | SKILL.md com menos de 300 linhas que só roteia; cada caminho em `references/caminhos/` |
| Ordem copy, design, código; direção a partir do banco de design (`search.py`) | Ordem briefing, referências, plano visual, copy, código; o banco virou consulta opcional |
| Step 0.5 "3 referências" pelo `github-search.py` (repositórios, não páginas) | Passo b: 6 a 10 páginas reais printadas e lidas (`capturar-referencias.mjs`), cobradas pelo `gate-referencias.py` |
| `frontend-design` como uma entre oito skills de design | `frontend-design` é dependência crítica e escreve o `plano-visual.md` antes do código |
| 8 lentes de auditoria | 9 lentes: entra `comparacao-referencias`, que reprovada manda voltar ao plano visual |
| Crítico: Playwright, `design-taste-frontend`, banco de design, Openverse, gate de tells | Crítico: python3, node, Playwright com Chromium e a skill `frontend-design` |
| 21st.dev, Stitch, Higgsfield, nanobanana, brandkit, animate, high-end-visual-design, magicui e shadcn espalhados pelo fluxo | Seção "Ferramentas opcionais" no fim do SKILL.md; nenhuma bloqueia, o `uso-ferramentas.py` não cobra |
| React obrigatório em página de venda | HTML + Tailwind compilado como padrão; React só quando o caso pede |
| Etapas do `gate-etapas.py`: 0 entender, 1 copy, 2 direção, 3 build, 4 verificar, 5 medir | 0 briefing, 1 referências (roda o gate de referências), 2 plano visual, 3 copy, 4 construção, 5 entrega |
| 60 arquivos em `references/` | 8 no topo, 5 em `references/caminhos/` e 47 da v2 em `references/arquivo/`, fora do fluxo |

### Adicionado

- `scripts/capturar-referencias.mjs`: abre cada URL no Chromium headless e grava a primeira
  dobra e uma seção do meio, atualizando `referencias/referencias.json`.
- `scripts/gate-referencias.py`: reprova sem 6 referências válidas, 2 de cada tipo, com prints
  reais (PNG, tamanho mínimo, não chapado, sem repetição), leitura nos quatro eixos, princípio
  e `lido: true`. Testes em `scripts/test-gate-referencias.py` e `scripts/test-capturar-referencias.cjs`.
- `references/pesquisa-de-referencias.md`, `references/auditores.md` (substitui
  `audit-agents.md`) e `references/caminhos/*.md`.
- `wave.py`: lente `comparacao-referencias`, gate `referencias` e `--caminho` (o clone fiel
  dispensa o gate de referências).
- `README.md` reescrito em inglês e este `CHANGELOG.md`.

### Mudado

- `checar-ferramentas.py`: só quatro críticos; opcionais de rede e MCP só com `--opcionais`.
- `uso-ferramentas.py`: cobra só Playwright e `frontend-design`; opcional viva nunca reprova.
- `gate-etapas.py` e `references/gate-etapas.md`: etapas novas do CRIAR. O perfil `dash` não mudou.
- `scripts/test-docs.py` reescrito para a estrutura nova (roteamento, ordem do CRIAR, opcionais
  fora do caminho principal, links e órfãos, além das travadas do aluno que continuam valendo).

### Removido

- `references/index.yaml` e `scripts/gerar-index.py` (índice de linhas para um SKILL.md de
  2.600 linhas, desnecessário num roteador curto).
- `scripts/github-search.py` (substituído pela pesquisa de páginas reais).
- Referências órfãs ou duplicadas movidas para `references/arquivo/` (nenhum caminho depende delas).

## 2.0.0

Versão com os 6 steps, as 8 lentes e as correções das 21 travadas do teste com aluno
(branch `fix/travadas-do-aluno`).
