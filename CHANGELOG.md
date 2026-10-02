# Changelog

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
