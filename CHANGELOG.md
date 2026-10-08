# Changelog

## 3.5.8 (08/10/2026): segunda rodada do teste de ponta a ponta (achados N1 a N21) e foto real no momento assinatura

Um segundo teste criou uma página real do zero (`ACHADOS` N1 a N21). Teste vermelho antes de cada conserto; nenhum gate foi
afrouxado: onde um gate passa a aceitar mais, há um teste de que o caso ruim original continua reprovando.

### Corrigido
- **N1** `capturar-referencias.mjs` e `qualidade-captura.mjs`: novo estado `vazia` (dobra com 97% ou mais de uma cor só, ou meio de
  uma cor só com foto que não carregou); espera as fotos visíveis (até 6 s) antes do print do meio; dobra com mais de 80% de uma cor
  só segue `ok` com `AVISO`. As medidas ficam em `captura` no manifesto.
- **N2** o prefixo numérico dos PNG segue do maior já usado (pasta, `descartados/referencias/` e manifesto); recaptura da mesma URL
  regrava os mesmos arquivos.
- **N3** `--remover <url>` tira do manifesto uma referência `ok` que não serve e move os PNG para `descartados/referencias/`; trecho
  ambíguo ou desconhecido recusa sem mexer em nada.
- **N4** `pesquisa-de-referencias.md`: tabela de nomes de partida por ofício (só nomes, não endereços).
- **N5** `assets-search.py --type commons`: descarta prova policial (`EFTA`), casa de boneca, reboque e museu e conta quantos tirou
  (`--sem-filtro` mostra tudo); `--autor` e `--categoria` estreitam a busca; cada item traz miniatura de 500 px.
- **N6** a saída mostra a versão de 1920 px quando a foto tem essa largura; `assets-sem-chave.md` diz que a Commons só serve 500, 960,
  1280 e 1920 px (outra largura dá HTTP 400).
- **N7** `gate-imagens.py`: o crédito é casado com a foto pelo link da origem dentro do item de crédito, não pelo nome do autor; sem
  esse link, o título entre aspas vale se for de alguma foto do mesmo autor. Título que não é de nenhuma continua reprovando.
- **N8** título real com hífen passa (comparação sem diferença entre hífen e espaço dos dois lados); título errado continua reprovando.
- **N9** `medir-dobra.mjs`: "Imagens ilustrativas" (plural) conta como aviso; a mensagem separa "fora da primeira tela" de "não achei o texto".
- **N10** `gate-verdade.py`: o contador animado (`<span class="contador" data-contador>`) fica dentro da frase, e o título que o carrega
  abre a própria seção.
- **N11** `gate-verdade.py`: telefone formatado na página casa com os dígitos do briefing (com ou sem o 55); número que o briefing
  não tem, ou promessa na mesma frase, continua pedindo linha.
- **N12** `gate-publicacao.py` e `criar.md`: a mensagem do ícone manda copiar o motivo, letra por letra, para um `data-desenho` e mostra
  os que a página tem. A checagem não mudou.

### Corrigido e novo, movimento, prova e auditor (N13 a N21)
- `gate-movimento`: reconhece a rede de segurança (classe `js` e temporizador de `data-js-ok`) dentro de um `<script>` maior, por exemplo junto da medida do `--vh`; só o resto é removido ou atrasado na prova. Novo `scripts/rede-de-seguranca.cjs`. Antes dizia "falta a rede de segurança" com ela presente (N13).
- `gate-responsivo`: o contraste botão/fundo mede também embaixo, à esquerda e à direita e só reprova se metade dos lados medidos está abaixo de 3:1; botão logo abaixo de bloco da cor da marca deixa de reprovar, botão dentro de bloco da própria cor continua reprovando, e a mensagem diz onde mediu (N14).
- `receitas-de-movimento`: `abertura-do-topo` manda o que cai abaixo da dobra do celular para `revela`; regra "atraso longo é quadro-chave parado no começo, nunca `animation-delay`"; `gate-movimento` nomeia o elemento do item que chega parado (`div.item "Dois"`) e explica o `animation-delay` na mensagem (N15, N16).
- `screenshot-prova.js`: o clique de prova em link externo (WhatsApp) é cancelado na própria página; o print de depois sai com a página e não em branco, e sai com 0. Navegação por script externa não gera print de depois (N17).
- `references/caminhos/criar.md`: edição por script e gates encadeados com `&&` (N18); parágrafo "Roteiro próprio" com todos os limites do gravador e o roteiro do demo para página com painel (N20); clique de prova em link externo; `--produto-fisico` no gate de composição.
- `pacote-auditoria.py`: o `briefing-do-auditor.md` leva a pasta absoluta do projeto, as 9 lentes, os critérios, o schema (com `gosto` e `eixos_abaixo`, e o da rodada 2), todas as referências, as telas de 360 e 320 e as pranchas de animação (N19).
- `gravar-video.js` e `video/roteiro.cjs`: o validador do roteiro lista todos os limites quebrados de uma vez, inclusive a duração, e imprime os limites (N20).
- Receita nova `foto-que-se-monta` (16ª) e seção "Escolha do momento assinatura": produto físico usa foto real do produto, nunca desenho; `gate-composicao.mjs --produto-fisico` avisa (não reprova) quando o momento assinatura é só SVG (N21).
- Gates visuais: 85 para 97 controles; `test-gates-visuais-cobertura.py` guarda o mínimo de 97.

## 3.5.7 (08/10/2026): o que o CI do macOS ainda reprovou na 3.5.6

### Corrigido
- **`test-assinatura-demo.cjs` no macOS do CI:** na visita normal do `gate-movimento.mjs` (8 s parada no topo, depois passos de 40% da tela)
  sobrava 1 animação com a seção "Vagas que se preenchem" fora da janela. A mensagem do gate agora diz QUAL foi (tipo, propriedade e
  elemento da primeira). A causa inferida (ver o relatório): o aviso do `IntersectionObserver` chega atrasado numa máquina lenta, já com a
  pessoa além da seção, e a classe `.visivel` dispara a transição fora da janela. A receita-base e o demo ganharam a classe
  `.instantaneo` (estado final de uma vez, sem transição nem animação), posta no callback quando a seção já saiu da janela.
- **`test-gates-visuais.cjs` estourava o teto de 20 min por arquivo no macOS do CI (saída 124 em 1200 s; o arquivo levava ~990 s no macOS,
  ~830 s no Linux e ~890 s no Windows antes de crescer):** dividido por família de gate em `test-gates-visuais-responsivo.cjs`,
  `-composicao.cjs` e `-movimento.cjs`, sobre `gates-visuais-lib.cjs`. Nenhum controle sumiu: 85 antes, 85 depois, e o
  `test-gates-visuais-cobertura.py` (portátil) reprova se algum controle ficar sem família. O filtro `GATES_FILTRO=<prefixo>` segue valendo.

## 3.5.6 (08/10/2026): correções do teste de ponta a ponta (achados A1 a A13)

Um teste criou uma página real como aluno (Ateliê Veio) e anotou cada tropeço. Esta versão corrige o que era da
skill, com teste vermelho antes de cada conserto. Nenhum gate foi afrouxado: onde um gate passa a aceitar mais,
há um teste-mutante que prova que o que é ruim continua reprovando.

### Corrigido
- **A1, A2** `capturar-referencias.mjs` julga a captura (`ok`, `bloqueada`, `quebrada`, `coberta`, com o motivo), tenta
  fechar o aviso de cookies, sai com código diferente de zero enquanto houver menos de 6 boas e ganhou `--limpar-ruins`
  (módulo `qualidade-captura.mjs`). `gate-referencias.py` reprova referência ruim e aceita página curta de verdade com
  o print do meio igual ao da dobra. `pesquisa-de-referencias.md` diz onde procurar quando a busca só dá classificado e loja.
- **A3** `gate-verdade.py` sem `index.html` confere só a tabela contra o briefing e diz "página ainda não existe".
- **A4** a citação é comparada com o briefing inteiro (espaços e quebras colapsados); citação que não está nele reprova.
- **A5** crédito de imagem (bloco marcado) e identificador de licença não são promessa; rótulo curto herda a promessa
  sustentada da mesma seção só com o mesmo número e unidade.
- **A6** a `sustentacao.md` é a tabela viva (texto em `plano.md` e `criar.md`); a saída imprime a linha pronta por seção;
  aviso quando a tabela do PLANO e a `sustentacao.md` divergem.
- **A7** `assets-search.py` ganhou a Wikimedia Commons como segunda rota quando a Openverse não responde (mesmo formato
  e campos de licença, só CC0, CC BY, CC BY-SA e domínio público, pausa e tratamento de HTTP 429), com a rota dita na saída
  e `--type commons`; testada com resposta gravada, sem internet.
- **A8** `Ícone do site: <motivo>` no modelo do PLANO, cobrado por `gate-plano.py` e pelo registro da etapa 2.
- **A9** acentuação em todas as frases impressas pelos scripts, com `test-acentuacao.py`.
- **A10** o próximo comando impresso traz o caminho completo da skill (`scripts/lancador.py`, `test-lancador.py`).
- **A11** painel-de-cor: o texto bate com o código (0,8 + 0,15 + 0,8 = 1,75 s); teste confere tempos do texto contra o código.
- **A12** assinatura-em-tres-estados com `colunas` e `montar()` iguais aos do demo; o par "título + lista vertical" declara
  `data-assimetrico` na receita, na linha do tempo e na regra de design; teste de nome indefinido em JS (`js-livres.py`).
- **A13** `screenshot-prova.js` espera a animação de entrada (teto de 4 s, diz quanto esperou) e congela as entradas
  terminadas antes do print de página inteira, que reiniciava a animação; a receita abertura-do-topo fixa o estado final com `.pronto`.

### Segunda leva (achados A14 a A25 e o aperto do A5)
- **A5 (aperto)** bloco marcado como crédito só isenta frase com cara de crédito; R$, %, "garantia", "dias", "clientes",
  "nota", "grátis" e afins dentro dele voltam a exigir linha (`gate-verdade.py`).
- **A14** o link de pular (fora da janela, `clip`, `clip-path`, 1 px) não conta como botão de ação nem como espaço fixo
  (`gate-responsivo.mjs`); dois botões visíveis continuam reprovando.
- **A15** a mensagem do espaço fixo diz QUAIS elementos somou (seletor e altura); o limite de 15% não mudou. A receita da
  assinatura traz a variante de celular (coluna fora do sticky abaixo de 900 px, estado 2 ao subir a coluna).
- **A16** `data-assinatura` no SVG do momento assinatura (marcador da receita) e `data-icone-repetido-ok` entram no texto
  (`ritmo-e-animacao.md` e a receita); o mesmo desenho fora da assinatura continua reprovando (`gate-composicao.mjs`).
- **A17** o gate de contraste não mede o que está invisível (opacity 0 acima do SVG, visibility, display); cores do exemplo
  da assinatura passam em fundo escuro e claro, conferidas no demo.
- **A18** `data-assimetrico` no HTML de exemplo da assinatura e do título fixo (e conferência em teste).
- **A19** a fórmula do limite de colunas (80 px) está no `criar.md` e a falha diz qual elemento mediu em cada coluna.
- **A20** a receita da assinatura anima a cor da peça no mesmo laço do JS (sem transição de CSS); o demo passa no
  `gate-movimento.mjs` (antes reprovava no celular) e isso virou teste (`test-assinatura-demo.cjs`).
- **A21** o modelo de créditos traz o padrão de link com 44 px de alvo sem buraco entre linhas (medido em 390 e 360).
- **A22** a mensagem do `uso-ferramentas.py` e a do `gate-etapas.py` dizem o que refazer, em ordem, com o caminho completo;
  o `criar.md` avisa nos passos em que isso acontece.
- **A23** `plano-para-secoes.py` gera o `secoes.json` da prova de animação a partir da tabela do PLANO (o que não dá para
  inferir sai `PREENCHER` e o `anim.mjs` recusa); testado com o PLANO real do projeto de teste.
- **A24** `baixar-fontes.mjs` baixa a fonte do Google Fonts (só o latino, woff2, variável quando existir) e imprime o
  `@font-face`; testado com resposta gravada.
- **A25** o `--click` do `screenshot-prova.js` não sai da página: navegação externa é bloqueada, registrada ("o clique
  levaria a <url>") e conta como clique que funciona.

### Terceira leva (CI real e achados A26 a A29)
- **CI (macOS e Ubuntu, `test-assinatura-demo`)** causa reproduzida com CPU a 20x: "Vagas que se preenchem" animava fora da tela, porque
  os temporizadores seguiam depois que a pessoa saía. A regra para todas as receitas: animação presa ao tempo vai ao estado final
  quando a seção sai da janela (vagas, alinhar sozinha, marcos dos passos). `gate-movimento.mjs` ganhou `--cpu` e `--so-celular`.
- **A26** lente `comparacao-referencias` reprovada lista os eixos abaixo (`--eixos-abaixo`) e manda corrigir a página; refazer o plano é ciclo novo.
- **A27** briefing pronto do auditor com orçamento (`auditoria/briefing-do-auditor.md`, gerado pelo `pacote-auditoria.py`); `wave.py registrar`
  guarda `--duracao-min` e `--chamadas` e `wave.py rodada` avisa quando passa do orçamento (15 min e 30 chamadas; 8 min e 15).
- **A28** `gate-movimento.mjs` prova "script bloqueado" e "script que demora 7 s" (desktop e celular) e a receita-base traz a rede de
  segurança (`.js` por script no `<head>` com temporizador e `onerror`); o demo usa. `gate-imagens.py` reprova foto de banco com nome de
  pessoa em alt, legenda ou depoimento, salvo o campo `Negócio fictício de teste: sim` no briefing.
- **A29** `gerar-og-image.mjs`: og:image 1200x630 com título, foto, faixa "Imagem ilustrativa" e a fonte da marca de `fonts/`.

- **A30** (defeito real da 3.5.4) na última rodada do ciclo a ordem é crítico ou regressão aberta = NÃO ENTREGAR, senão ENTREGA COM
  RESSALVAS (a lente de referências reprovada entra na lista, com os eixos); "voltar ao plano" nunca é ordem. Teste com os números do caso real.
- **A31** na rodada 2 as lentes não medidas de novo mostram "nota da rodada 1 mantida" e a média não é apresentada como medida nova; cada
  rodada grava o desfecho e o `gate-etapas.py registrar 5` recusa NÃO ENTREGAR, CONTINUA e auditoria pendente, e grava as ressalvas.
- **A32** `gate-etapas.py revalidar --motivo "<texto>"`: mudança de briefing no meio revalida em ordem só as etapas em que SÓ o briefing mudou
  (o gate delas roda de novo); qualquer outra evidência mudada continua exigindo o gate da etapa.
- **Etapa 5 sem porta dos fundos** `gate-etapas.py registrar 5` recusa quando não há `.wave-auditoria.json`, quando faltam lentes das 9, quando há
  autoavaliação ou quando o ciclo não fechou (mensagem com os comandos do passo g); EDITAR segue isento (não usa essas etapas).
- **A33** `pacote-auditoria.py` exige a resposta `--briefing-reflete-pedido sim|nao` no checklist (ou usa `evidencias/pedidos.md` e avisa quando o
  briefing é mais antigo que o último pedido).

### Ainda não provado
- Windows e Linux reais continuam como na 3.5.5. Nenhuma das correções acima foi rodada fora do macOS.

## 3.5.5 (08/10/2026): Windows, macOS e Linux, com trava e teste em máquina real

A skill é usada ao vivo por alunos, muitos em Windows, e só tinha o mínimo (`py.mjs` e `sistemas.md`).
Esta versão não muda nenhum gate nem limite: é só portabilidade.

### Adicionado
- `scripts/test-portabilidade.py`: a trava, com cinco regras. Reprova (1) comando que só existe no Mac fora de trecho
  marcado como macOS; (2) pasta temporária fixa em vez de `tempfile`; (3) texto aberto, lido ou escrito sem codificação
  explícita; (4) o nome do Python do Mac solto no comando; (5) shell no código (chamada por shell, utilitário de Unix
  como programa, `execSync` com texto, `cpSync`). Varre `.py`, `.mjs`, `.cjs`, `.js` e `.md`; antes de varrer a skill,
  prova a si mesma em exemplos ruins e bons plantados. No primeiro uso apontou 290 ocorrências.
- `scripts/plataforma.py` (sistema, programa no PATH, comando sem shell, instruções de instalação por sistema) e
  `scripts/npm-global.cjs` (pasta global do npm sem shell, para achar o Playwright global no Windows).
- `scripts/rodar-testes.mjs`: a suíte inteira num comando, igual nos três sistemas, com `--so-portateis`.
- `.github/workflows/portabilidade.yml`: a suíte em `windows-latest`, `ubuntu-latest` e `macos-latest` (Node 22,
  Python 3.12) e, no Windows, os testes portáteis numa pasta com acento e espaço. `.gitattributes` com LF.

### Alterado
- Todo comando Python dos textos é `node <dir-da-skill>/scripts/py.mjs <script>.py`.
- Leitura e escrita de texto em UTF-8 em todos os scripts (leitura aceita BOM), `subprocess` sem shell,
  busca de trecho do `uso-ferramentas.py` em Python puro (não depende de `grep`), Playwright global achado sem `execSync`.
- `checar-ferramentas.py`: sem shell, o rótulo do Python deixou de ter o nome do Mac e virou "Python", e cada "RESOLVER" traz o comando do sistema de
  quem rodou (winget, brew, apt ou dnf), com o Python exato que está sem Pillow.
- `references/sistemas.md` reescrito: o que muda por sistema, instalação de cada pré-requisito e erros conhecidos com a saída.

### Ainda não provado
- Windows e Linux reais: o workflow está pronto, o primeiro resultado dele ainda não foi registrado aqui.

## 3.5.4 (08/10/2026): um auditor nas nove lentes, pacote de evidência pronto e teto de 2 rodadas

O dono da skill perguntou "esses 9 revisores são necessários?", a regra dele é teto de 2 rodadas de
corrigir e auditar, e a skill roda ao vivo em aula, onde a página demorar a ficar pronta é o problema.
As 9 lentes continuam existindo como critérios; mudou quantos agentes rodam e quantas rodadas.

### Alterado
- A rodada de auditoria é UM subagente auditor independente que percorre as 9 lentes numa passada e
  devolve um bloco por lente. Uma lente por subagente virou modo opcional (auditoria profunda pedida
  pela pessoa). O registro no `wave.py` segue um por lente, com a origem certa; autoavaliação não libera entrega.
- `wave.py rodada`: o teto cai de 4 para 2. Depois da segunda rodada o ciclo fecha SEMPRE: aprovado,
  `ENTREGA COM RESSALVAS` (achados que sobraram e nota real) ou `NÃO ENTREGAR: crítico aberto`
  (também para regressão aberta). Crítico, regressão, lente de referências reprovada e auditoria
  independente pendente não foram afrouxados. Terceira rodada só com `--rodada-extra-pedida`, registrada
  no histórico; a terceira também fecha e não existe quarta.
- A rodada 2 é de conferência (`references/auditores.md`, "Rodada 2"): cada achado corrigido ou não,
  regressão, e mais nada; não reabre as 9 lentes.
- `references/auditores.md`, `caminhos/criar.md`, `clonar.md`, `melhorar.md`, `gate-etapas.md`, `SKILL.md` e `README.md` alinhados.

### Adicionado
- `scripts/pacote-auditoria.py` (+ `test-pacote-auditoria.py`): junta e confere o pacote do auditor (URL, `dist/`,
  briefing, PLANO, sustentação, referências, prints dos gates, pranchas do vídeo de prova), avisa de captura
  anterior à última mudança da página e sai 1 se faltar item obrigatório. O auditor lê, não captura de novo.
- Testes de texto em `test-docs.py` (nenhum arquivo manda nove subagentes por rodada nem teto de 4) e de ciclo em `test-wave.py`.

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
| Crítico: Playwright, `design-taste-frontend`, banco de design, Openverse, gate de tells | Crítico: Python 3, node, Playwright com Chromium e a skill `frontend-design` |
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
