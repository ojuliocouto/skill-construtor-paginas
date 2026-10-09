# Changelog

## 3.5.14 (09/10/2026): conserto dos achados BAIXOS de código da auditoria da 3.5.11 e da 3.5.12 (10, 11 e 12)

Teste vermelho antes, conserto, teste verde, como na 3.5.13. O achado 9 (estado 0 fura o máximo de 4) já estava consertado na 3.5.13:
conferido, `data-assinatura-estado="0"` reprova e `test_estado_zero_reprova` passa.

### `gate-imagens.py`
- **Achado 10, mensagem errada.** A foto de um estado que reaparece em outra seção com `data-assinatura` simples (sem número) era chamada
  de "outra foto". Agora a mensagem diz que é a MESMA foto ("a foto do estado 1 (foto1) aparece com data-assinatura simples, sem o número
  do estado, na seção extra") e o que fazer; foto diferente com `data-assinatura` simples segue com "em outra foto (fotoN)". Os dois casos
  juntos dão as duas mensagens.
- **Achado 11, pilha do parser.** O parser das regiões agora trata os fechamentos implícitos do HTML: `p` (fechado por `div`, `ul`, `table`,
  títulos, `figure`, outro `p` e os demais blocos), `li`, `dt` e `dd`, `option` e `optgroup`, `tr`, `td` e `th`, `tbody`, `thead` e `tfoot`.
  O estado e o grupo declarados num `li` sem `</li>` não passam mais para o irmão. Fim de tag sem abertura no alcance (um `</li>` solto
  dentro de uma lista aninhada) é ignorado; lista e tabela aninhadas não fecham o elemento de fora. Fechamento explícito se comporta como antes.

### `test-imagens.py` (Achado 12)
- O teste do buraco casa as duas mensagens exatas (`falta o estado 1` e `falta o estado 2` do grupo `outro`) e "2 grupos"; o teste do
  `data-assinatura` simples casa a frase inteira com `(foto4)` e exclui a mensagem da regra 8, que também tem as duas palavras. Um mutante
  em cada mensagem deixa o teste novo vermelho (o antigo continuava verde).

### Provas
- `test-imagens.py`: 118 testes (3 do achado 10, 14 do achado 11 e 1 de ponta a ponta no gate, mais as asserções do 12); os de 10 e 11 estavam
  vermelhos antes do conserto. `test-docs*.py` verdes. `test-docs-3514.py` (novo).
- Não foi provado: a suíte inteira (o dono roda); a página Torra Clara não foi refeita (achados 8 e 13 a 15 seguem fora desta versão).

## 3.5.13 (09/10/2026): conserto dos achados ALTOS e MÉDIOS de código da auditoria da 3.5.11 e da 3.5.12

A auditoria adversarial (`AUDITORIA-3511-3512.md`) achou, por leitura de código, brechas nos dois gates novos. Cada caso mínimo da auditoria
foi rodado ANTES do conserto: todos reproduziram (o gate antigo PASSAVA onde devia REPROVAR). Teste vermelho, conserto, teste verde.

### `gate-ritmo.mjs`
- **Achado 1 (alto), configurador por contagem cega.** Só conta controle visível e interativo (8x8 px ou mais, sem `display:none` nem
  `visibility:hidden`; radio ou caixa escondido conta pelo label visível), em 2 ou mais grupos (`fieldset`, `role=radiogroup`, radios do
  mesmo `name`, cada campo; botões do mesmo pai são um grupo). Só UMA coluna da fileira pode ser o configurador, e a outra (o resumo) não
  tem controles. Antes: 4 `<input style="display:none">` ou 4 chips decorativos num cartão faziam "configurador" e a fileira de cartões
  escapava do máximo de 1 "título centralizado + cartões".
- **Achado 3 (médio), lista decidida pela tag.** Coluna com caixa própria (fundo diferente do da seção, borda, sombra ou padding dos dois
  lados) é cartão, seja `ul`, `ol`, `dl` ou `div`; `ul`/`ol`/`dl` com título (`h1` a `h6`) nos itens também é cartão. Lista é só linha leve.
- **Achado 6 (médio), "ao lado" com enfeite.** O conteúdo "ao lado" tem de ser uma coluna IRMÃ do título (mesma grade ou flex), em fluxo,
  visível para quem lê e com texto ou mídia. Selo `aria-hidden`, enfeite em `position:absolute` ou `fixed` e caixa vazia não contam.

### `gate-imagens.py`
- **Achado 2 (alto), sequência sem amarra.** A sequência `data-assinatura-estado` só vale quando o `PLANO.md` do projeto declara
  `Momento assinatura: ...; seções: ...; estados: x -> y -> z` e o número de estados bate com o da página (e o plano lista ao menos tantas
  seções quanto estados). Fotos sem relação marcadas 1, 2 e 3 sem a declaração reprovam. A mensagem da regra 8 só sugere a sequência quando
  o plano a declara; sem o plano, manda declarar primeiro no `PLANO.md`.
- **Achados 4 e 5 (médios).** Cada estado mora na sua seção (a primeira em que ele é o estado mais novo presente), as seções são
  distintas e vêm em ordem crescente na página. A foto do estado k só pode aparecer na seção dela e na do estado k+1 (a cópia por baixo);
  em qualquer outra é repetição. Antes: o estado 1 em 5 seções mais o 2 numa sexta passava, e cru/torrado/xícara de trás para frente também.
- **Achado 9 (baixo, de passagem).** `data-assinatura-estado="0"` reprova.

### `test-ritmo-3512.cjs` (achado 7, médio)
- Seções com nomes únicos e linha da seção casada na saída (`/Cenários do dia\s+título centralizado \+ cartões/`); fixture do quadro com
  `<img>` de verdade (o `div role=img` não era mídia, e o "Fecho" saía "título à esquerda + cartões" sem o teste dizer). Dois mutantes do
  gate (título centralizado e título ao lado rotulados errado) deixam os controles vermelhos.

### Provas
- `test-ritmo-3513.cjs` (novo, navegador): 11 controles, 9 reprovavam com o gate 3.5.12 e os 11 passam agora. `test-ritmo-3512.cjs`: 12 de 12.
- `test-imagens.py`: 100 testes, 12 novos vermelhos antes do conserto, todos verdes depois; o teste que esperava `[]` para 3 fotos de ruído
  passou a exigir o PLANO.
- Torra Clara (`pagina-teste-358/dist`, `PLANO.md` já declara 3 estados e 3 seções): `gate-ritmo.mjs` e `gate-imagens.py` PASSAM sem mudar a página.
- Não foi provado: a suíte inteira (o dono roda); os achados 8 e 13 a 15 da auditoria são da página Torra Clara, não do código, e ficam fora desta versão.

## 3.5.12 (09/10/2026): o gate-ritmo erra o corpo da seção na Torra Clara (último falso positivo da 3.5.10)

Depois da medição de alinhamento da 3.5.10 (P18), o `gate-ritmo.mjs` passou a reprovar a Torra Clara nas seções "Monte o seu plano de
café" e "Dúvidas antes de assinar", as duas lidas como "título à esquerda + cartões". Conferido nos prints do site no ar (1440): o gate
estava errado, a página estava certa. O título foi medido certo (início à esquerda); o que errou foi o CORPO da seção.

### O que estava errado no gate
- "Monte o seu plano" é um configurador (4 fieldsets com 15 radios) ao lado do rótulo do pedido. As duas colunas medem 663 e 486 px, razão
  0,73, acima da linha de 0,70 que o gate usa para "cartões de peso parecido". A página já declarava `data-assimetrico` nessa grade, e o
  gate de ritmo não olha essa marca. Na 3.5.9 a seção passava por acidente (medido de novo com o gate antigo: "título centralizado + cartões", 1 de no máximo 1): o h2 largo de
  uma linha tinha o centro da caixa no meio e era chamado de centralizado; a correção da 3.5.10 acertou o título e deixou o corpo errado à mostra.
- "Dúvidas" são duas colunas de `details` (perguntas). Duas colunas de peso igual viravam "cartões".

### Conserto (`gate-ritmo.mjs`)
- Coluna com 4 ou mais controles (`input`, `select`, `textarea`, `button`, `role=radio|checkbox|tab|switch|option`) vira o corpo
  **configurador**. Radios escondidos (1 px) contam: o que vale é existirem na coluna.
- Colunas que são lista (`ul`/`ol` com 3 ou mais `li`, `dl` com 3 ou mais filhos, ou 2 ou mais `details` irmãos) viram o corpo **lista**.
  Cartão com título, texto e uma lista dentro NÃO vira lista: os filhos dele são de tipos diferentes.
- Nada foi afrouxado: dois configuradores vizinhos, duas FAQs vizinhas, duas listas em colunas vizinhas, e cartões vizinhos com botão,
  campo ou lista dentro de cada cartão continuam reprovando.

### Defeito vizinho (P18, registrado na 3.5.10)
- Título curto centralizado com cartões a menos de 40 px abaixo era tratado como "título ao lado do conteúdo": o 3º cartão da fileira
  fica à direita do título curto e começa logo abaixo dele. Agora "ao lado" exige sobreposição vertical de verdade (24 px ou 30% da
  altura do título). O título de lado de verdade (coluna esquerda, conteúdo à direita na mesma altura) continua "lado"; o título curto
  centralizado volta a contar como "título centralizado + cartões" e entra na regra do máximo de 1.

### Provas
- `test-ritmo-3512.cjs` (novo, navegador): 12 controles, 8 reprovavam antes do conserto e os 12 passam depois; os 15 controles de ritmo
  da 3.5.10 e da v3.5 (`test-gates-v35.cjs`, `test-texto-ritmo-3510.cjs`) seguem verdes.
- `gate-ritmo.mjs` na Torra Clara no ar (https://torra-clara-teste.pages.dev): PASSA, vizinhas iguais 0. Os 9 esqueletos agora são
  distintos entre vizinhas: configurador (seção 7), lista (seção 8).
- Não foi provado: o v6 original do Studio Equilíbrio não está no disco; o formato ruim dele (cartões iguais com título centralizado, 2 ou
  mais) está nos controles `ritmo-vizinhas` e `ritmo-centro-cartoes`. O auditor adversarial não rodou nesta versão.

## 3.5.11 (09/10/2026): o momento assinatura de produto físico que muda de foto (P5, a metade que a 3.5.10 deixou)

A 3.5.10 resolveu o P5 só para a MESMA foto em 3 enquadramentos (receita `produto-em-estados`). Quando o produto muda de foto de verdade
(grão cru, torrado, na xícara na Torra Clara), o `gate-imagens.py` seguia reprovando `data-assinatura` em fotos diferentes (regra da
3.5.10, frente B) e a receita dizia "não use". Esta versão fecha a contradição sem afrouxar o gate: o caso ruim original continua reprovando.

### Variante de 3 fotos da `produto-em-estados`
- Sequência declarada: `data-assinatura-estado="1"`, `"2"`, `"3"` (de 2 a 4 estados), `data-assinatura-grupo="nome"` opcional. Cada estado
  é uma foto do MESMO produto, na sua seção; as seções não precisam ser vizinhas.
- O que faz a sequência ler como continuação e não como 3 fotos soltas: o mesmo quadro (proporção, lado e largura) nas seções, o assunto
  no mesmo ponto (`--ancora`), a foto do estado anterior por baixo do quadro e a nova passando por cima (cortina de `clip-path` com o
  final escrito, `inset(0 0 0 0)`, para o navegador interpolar), e uma trilha de 3 passos com o passo da seção marcado.
- Demo em `references/receitas/demo.html` (continuam 17 receitas: a variante mora dentro da `produto-em-estados`). O
  `provar-receitas.mjs` mede, em 1440 e 390: os 3 quadros com a mesma largura, altura e posição; a cortina muda os pixels dos estados 2 e
  3 (animações paradas no instante da chegada e terminadas, sem depender da carga da máquina); movimento reduzido já chega no estado final.
  Sem script, só a foto do estado aparece, inteira.

### `gate-imagens.py` (regra 13)
- Aceita `data-assinatura` em várias fotos SÓ quando formam a sequência declarada: estados numerados de 1 até N (2 a 4), sem buraco, cada
  estado em uma foto (a cópia dela por baixo do quadro seguinte leva o número do estado dela), fotos diferentes entre os estados, no mesmo
  grupo e em pelo menos N seções. As seções onde a foto leva o número contam como uma só; a foto do estado numa seção sem a marca segue
  sendo repetição.
- Continua reprovando, com mensagem que aponta a saída: 2 ou 3 fotos diferentes com `data-assinatura` simples; buraco ou começo fora do 1;
  1 estado só; mais de 4; estado que não é número; 2 grupos; o mesmo estado em fotos diferentes; estados diferentes na mesma foto; todos os
  estados numa seção só; sequência mais `data-assinatura` simples em outra foto. 21 testes novos em `test-imagens.py` (`SequenciaDeEstados`).

### Torra Clara (a página que achou o P5)
- O grão cru, o torrado e o café na xícara viram a sequência: sítios, semana do seu café e fecho, o mesmo quadro 4:5 à esquerda nas 3
  seções, trilha "1 Cru, 2 Torrado, 3 Na xícara". O `gate-imagens.py` da Torra passa (reprovava desde a 3.5.8); os outros gates que
  passavam continuam passando.
- A primeira rodada de gates na Torra achou um defeito da própria receita: o número do passo da trilha estava em `<span>` no HTML, e o
  `gate-verdade.py` lê todo número visível como promessa ("1", "2", "3" sem linha de sustentação). O número passou a vir de um contador
  de CSS (`counter(passo)` no `::before`); a receita e o demo foram corrigidos junto (teste `test_o_numero_do_passo_vem_de_contador_de_css`).
- O `gate-plano.py` reprovou o PLANO com `produto-em-estados` escrito nas 3 seções ("no máximo 2 seções com a mesma animação"). O tipo
  certo da coluna Animação nas 3 seções é `assinatura:` (o momento assinatura fica fora da contagem), com a receita nomeada depois dos
  dois pontos. A receita agora diz isso (`**No PLANO:**`), com teste.
- O `gate-movimento.mjs` reprovou `li` "chegam parados" (a trilha animava o número do passo quando o quadro entrava, e a trilha, embaixo do
  quadro, entrava na tela depois). A trilha deixou de animar; a receita diz "A trilha não anima", com teste.
- O `gate-ritmo.mjs` da 3.5.11 reprova a Torra Clara ("MONTE O SEU PLANO DE CAFÉ." e "DÚVIDAS ANTES DE ASSINAR", as duas "título à esquerda
  + cartões"), mas reprovava IGUAL na página publicada antes desta mudança (medido com os mesmos gates): vem do P18 da 3.5.10, que passou a
  medir o alinhamento real do título, e o relatório da 3.5.10 rodou os gates de uma pasta anterior à junção. Não é desta mudança e não foi consertado aqui.

### Não foi provado
- A sequência foi provada em UMA página real (a Torra Clara) e no demo com desenhos; página de outro ramo (obra, prato, imóvel) pode pedir
  outro ponto de âncora. O auditor adversarial não rodou nesta versão.
- O quadro é o mesmo nas seções, mas o gate não mede a posição das 3 figuras na página: quem mede é o `provar-receitas.mjs` no demo e o
  relatório da página. Um `gate-simetria` que cobrasse isso numa página qualquer não existe.

## 3.5.10 (09/10/2026): primeira tela visível no celular, texto invisível, servidor local e os achados P1 a P21 do teste da Torra Clara

O teste de ponta a ponta da página Torra Clara (3 h 15 min, `RELATORIO.md` seção 5) deixou 21 achados (P1 a P21) mais a primeira tela do
celular (G22). Três frentes em paralelo (A: captura, imagens e documentação; B: gates; C: movimento, visibilidade e primeira tela) e o P11
(servidor local), cada conserto com teste que reprovava antes. Nenhum gate foi afrouxado: onde um gate passa a aceitar mais, há teste de
que o caso ruim original continua reprovando.

### Primeira tela visível no celular (G22)
- `gate-responsivo.mjs` mede o topo na área que a pessoa vê, com as barras do navegador (390x664 e 360x616 reprovam; 375x553 avisa, por
  ser estimativa sem fonte): manchete, texto de apoio e botão principal inteiros, botão a 8 px ou mais do pé. A foto mínima de 35% passa a
  ser da área visível e o texto ganha da foto (piso de 20%). O botão do herói deixa de ser o link da marca que volta ao topo
  (`topo-da-pagina.mjs`). Reprova a v7 antiga (botão 146 px abaixo da dobra) e a Torra Clara (apoio fora); aprova a v7 atual (botão a
  15 px do pé). `--so-primeira-tela` mede só isso. `medir-dobra.mjs` devolve manchete, apoio, botão e a posição da legenda da foto.

### Texto invisível (P12, P13, P14)
- `gate-movimento.mjs` reprova texto invisível com a página parada 4 s na primeira tela (P13b), invisível na tela por 2 paradas da visita
  (recorte de entrada no alvo do observador, P12) e invisível acima da tela depois de um salto até o fim (P14). `--so-visibilidade`.
- `gate-oclusao.mjs` mede por linha de texto e reprova linha recortada por clip-path (span em linha que quebra, P13a).
- Receitas: a gramática de base ganha "o clip-path de entrada vai no filho", "a primeira tela entra na carga" e "já passou = estado
  final" (`revelar`, `primeiraTela`, `jaPassou`, `observar`, no md e no `demo.html`). Página feita antes da 3.5.10 sem o "já passou"
  reprova na prova do salto até receber a função: é o defeito do P14 em página real, não ruído.

### Servidor local (P11)
- `servidor-gzip.py`: a porta é preferência. Ocupada (inclusive por servidor que ouve só em 127.0.0.1), escolhe uma livre, avisa e
  imprime `URL: http://127.0.0.1:<porta>/`; a saída sai na hora mesmo com pipe. Sem `SO_REUSEADDR`, que deixava dois servidores na mesma
  porta.
- Os gates de navegador (`gate-responsivo`, `gate-oclusao`, `gate-simetria`, `gate-texto`, `gate-composicao`, `gate-movimento`,
  `gate-ritmo`, `gate-video`, `sobreposicao`, `anim` e `medir-dobra`) conferem a URL antes de abrir o navegador (`servidor-no-ar.mjs`) e
  param com "servidor fora do ar em <url>" e o comando para subir de novo, saída 3, no lugar de `net::ERR_CONNECTION_REFUSED` e pilha de
  chamadas. A saída 3 não é veredito sobre a página.
- `rodar-gates.mjs`: usa a URL que o servidor imprime e, se o servidor de um gate cai no meio, sobe outro e repete esse gate uma vez,
  dizendo isso; reprovação sem a marca de servidor fora nunca é repetida.
- `montar-dist.py`: esvazia a `dist/` sem apagar a pasta (servidor ou terminal dentro dela não perde o chão) e avisa "dist refeita".
- Testes: `test-servidor-gzip.py` (7), `test-servidor-fora.cjs` (11 gates), 3 casos novos em `test-rodar-gates.cjs`.

### Captura de referências (P1, P2, P3)
- A tela de bloqueio de robô vira `bloqueada` mesmo quando o cabeçalho e o menu do site passam de 800 caracteres ("We couldn't verify
  the security of your connection", Cloudflare, Akamai, Incapsula, "Press & Hold", "unusual traffic"). Foi o caso da Um Coffee, `ok` na 3.5.8.
- O aviso de cookies só é dado como fechado depois de conferir no DOM que saiu da tela: clique sintético, depois clique de mouse de
  verdade. Aviso que continua visível sai com `aviso_fechado: false`, um AVISO na captura e na saída.
- O print do meio igual ao da dobra vira `vazia` (página mais alta que a janela: a rolagem não andou; página de uma tela só com 30 links
  ou mais: só o topo renderizou). Nova opção `--longa`.

### Imagens e identidade (P6, P7, P17)
- `assets-search.py --type openverse` (e `cc`) cai sozinho para a Wikimedia Commons quando a Openverse falha ou não acha, e avisa;
  `--type sem-chave` e o `criar.md` dizem que o Unsplash não abre por script (HTTP 307).
- `gerar-og-image.mjs` avisa (ATENÇÃO fonte, ATENÇÃO cores) em vez de escolher em silêncio a primeira fonte de `fonts/` e o fundo padrão.
- `gerar-icones.mjs` imprime as duas linhas de `<link>` prontas com os nomes reais (`/favicon.png`, `/apple-touch-icon.png`).

### Gates (P4, P8, P9, P10, P15, P18, P21)
- `gate-plano.py`: o tipo da animação de cada seção confere com o repertório (`## Receita:` de `receitas-de-movimento.md`), `assinatura` ou
  `criação nova: <motivo>` (15 caracteres ou mais).
- `gate-verdade.py`: a regex do dono não atravessa a quebra de linha.
- `gate-texto.mjs`: item que começa com e-mail ou endereço de site fica fora da regra da maiúscula; frase minúscula de verdade segue reprovando.
- `gate-imagens.py` + `lugares_br.py` (novo): cidade, bairro e região não são nome de pessoa em alt, legenda e depoimento; pessoa real segue avisando.
- `gate-etapas.py revalidar`: grava as etapas que passaram até a que bloqueou e diz o que gravou (ou que nada foi gravado); a que
  bloqueou e as seguintes seguem bloqueadas.
- `gate-ritmo.mjs`: "título centralizado" medido por `text-align` calculado e pela posição da primeira linha; a saída mostra como mediu.
- `gate-relatorio.py`: linha que começa com `rodada N:`, `antes:`, `histórico:` ou `versão anterior:` fica fora da regra "anterior à
  `dist/`" (continua citando o arquivo e o número); a que fala do estado atual segue cobrada.

### Receitas (P5, P19, P20)
- Receita nova `produto-em-estados` (a 17a): a MESMA foto do produto atravessa 3 seções e muda de estado (fixa ao lado no desktop, no topo
  de cada seção no celular); a `foto-que-se-monta` pode ser a entrada do estado 1, uma vez só.
- `painel-de-cor`: no máximo 3 botões com `data-painel`, todos para o mesmo destino. `barra-fixa-do-celular`: oferta longa com
  `data-barra-rotulo` e `data-barra-destino`.

### Documentação (P16 e extras)
- Modelo de sessão e README não mandam mais o registro para a pasta da skill (resto do N25). O README deixa de dizer que a captura
  nunca clica em aviso de cookies (falso desde a 3.5.6).
- `criar.md`: o passo b cita `--remover`, `--limpar-ruins`, `--longa` e os estados da captura; o `sobreposicao.mjs` não se aplica a página
  sem elemento sticky ou fixo; o roteiro da etapa f explica a porta, a URL impressa e a saída 3; o topo do celular na área visível; a
  coluna Animação do PLANO; o marcador de história no relatório; `revalidar` que bloqueia.
- `SKILL.md` segue em 330 linhas (teto do `test-docs.py`): o que não coube na tabela foi para o `criar.md`.
- Testes novos: `test-servidor-gzip.py`, `test-servidor-fora.cjs`, `test-primeira-tela.cjs`, `test-visibilidade-movimento.cjs`,
  `test-texto-ritmo-3510.cjs`, `test-gerar-icones.cjs`, `test-docs-criar-3510.py`, `test-docs-3510-juncao.py`; casos novos nos testes
  dos gates, da captura, da busca de foto e das receitas. O teto do `test-assinatura-demo.cjs` subiu de 300 para 480 s (o gate de
  movimento no demo leva 313 s com as provas novas, 4% a mais).

### Não foi provado
- **A área visível de 664 px vem da tabela de aparelhos do Playwright 1.61.1, não de um iPhone físico.** Se um iPhone 14 de verdade mostra
  menos de 657 px de área, o botão da v7 atual também sai da primeira tela lá; no iPhone SE a v7 atual já fica 80 px abaixo (o gate avisa).
  Os 124 px de barras do Android (360x616) vêm do Pixel 5 da tabela; o 375x553 é estimativa e por isso só avisa.
- **A captura da Omsom real não foi reproduzida**: a causa do 900 px nela não está no relatório. Os testes usam páginas locais que
  reproduzem os dois sintomas (rolagem que volta ao topo; tela cheia de links).
- **A v7 atual reprova na prova do salto** (164 elementos em 1440 e 170 em 390 acima da tela, invisíveis) até receber o "já passou". A
  Torra Clara passa nas quatro provas de visibilidade.
- A variante de `produto-em-estados` com 3 fotos diferentes (cru, torrado, na xícara) não existe: o `gate-imagens.py` aceita
  `data-assinatura` em UMA foto só (N22). Fica como pedido para a próxima versão, junto com a régua da legenda "imagem ilustrativa" sobre
  os campos novos do `medir-dobra.mjs`.
- O servidor que cai por causa de OUTRO processo matar o dele (o exit 144 do teste) não foi reproduzido; a correção é detectar, dizer e
  repetir, não impedir a queda. Defeito vizinho do P18 sem conserto: a regra "título ao lado do conteúdo" do `gate-ritmo.mjs` trata como
  "ao lado" um título curto centralizado com cartões a menos de 40 px abaixo.

## 3.5.9 (08/10/2026): gates num comando só, gate de movimento com movimento reduzido e achados N22 a N27

O reteste de ponta a ponta fechou em 3 h 15 min e em NÃO ENTREGAR: duas vezes o auditor achou animação rodando com movimento
reduzido e o gate de movimento passou verde. Esta versão fecha esse furo e ataca os dois ralos de tempo fora da auditoria
(gates, 37 min; achar foto, 21 min). Nenhum gate foi afrouxado.

### Tempo
- Novo `scripts/rodar-gates.mjs`: roda todos os gates mecânicos da etapa f num comando só, em paralelo (teto pela máquina, de 1 a 4 navegadores), com um servidor em porta livre por gate, e imprime um relatório consolidado com PASSA ou REPROVA por gate, tempo, texto inteiro das falhas e total. Grava `gates/<nome>-rN.txt` e `gates/_execucoes.txt` como o fluxo antigo e sai com 1 se qualquer gate reprova. Opções `--so`, `--reprovados`, `--paralelo`, `--confirmar-sozinho`, `--com animacao,video,sobreposicao`. Não substitui nem afrouxa nenhum gate: chama os mesmos scripts com os mesmos argumentos.
- Medido numa cópia da página do teste de 3.5.6: rodada completa de 426 s em série para 197 s em paralelo, com o mesmo veredito e o mesmo texto de falha em todos os 15 gates, na página boa e numa página quebrada de propósito.
- `references/caminhos/criar.md`, etapa f: o comando único é o caminho padrão (rodar tudo, ler o relatório, corrigir tudo, `--reprovados`, rodada completa no fim); os comandos individuais ficam como referência.
- `assets-search.py`: nova opção `--folha <arquivo.png>` monta UMA imagem em grade com as miniaturas dos resultados e o número de cada uma (o mesmo da lista), respeitando a pausa entre chamadas e o HTTP 429; a saída de texto não muda. Acentos corrigidos na saída (achado A9): crédito, condição, saída, atribuição e vizinhos.
- Testes novos: `test-rodar-gates.cjs` (21, portátil, confere o catálogo do comando contra o `criar.md`) e `test-folha-assets.py` (15, precisa de Pillow), ambos provados com mutantes.
- Limite conhecido: em 1 de 6 rodadas na página boa, o `gate-responsivo` reprovou só no paralelo (barra fixa do celular medida com a
  máquina cheia). `--confirmar-sozinho` roda de novo, sozinho, o gate de navegador que reprovou e adota esse veredito; essa opção só
  foi provada com gates falsos.

### Corrigido (N22 a N27)
- **N26** `gate-movimento.mjs`: com movimento reduzido, o gate reprova se sobrar animação ou transição em curso depois da carga e
  durante a rolagem, e nomeia o elemento e a propriedade. Antes só conferia a rolagem suave. As receitas do `demo.html` que não tinham
  a regra de movimento reduzido ganharam a regra.
- **N22** `gate-imagens.py`: `data-assinatura` libera a MESMA foto nas seções do momento assinatura (uma foto só; a mesma foto
  repetida sem a marca continua reprovando).
- **N27** `wave.py reabrir --motivo`: mudança grande pedida pelo dono entre as rodadas reabre a rodada 1, uma vez por ciclo; o
  `criar.md` diz o que fazer quando a correção vem depois da rodada 2 em sessão não interativa.
- **N23** `wave.py --eixos-abaixo` aceita `acabamento` (os cinco eixos da lente).
- **N24** `pacote-auditoria.py`: o orçamento do auditor conta até a resposta chegar, com blocos curtos por lente.
- **N25** o registro da sessão vai na pasta do projeto, nunca na pasta da skill.

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
