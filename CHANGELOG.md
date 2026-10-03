# Changelog

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
