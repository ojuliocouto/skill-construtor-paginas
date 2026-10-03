# Preferências de design: valem para TODA página (carregar ANTES do plano visual)

Regras de gosto medidas em correções reais, repetidas, de quem aprova as páginas desta skill.
Cada item foi cobrança explícita depois de uma entrega. Elas valem para qualquer página, de
qualquer nicho, e têm precedência sobre o banco de design e sobre o estilo sugerido por
qualquer skill de design. A única coisa que vence esta lista é a identidade REAL do cliente
(logo, cor e fonte que ele já usa).

Os itens marcados com **[gate]** são cobrados por script e reprovam com código 1 (o nome do
script vai ao lado). Os outros se conferem no print, com os próprios olhos, e a lente
design-critic cobra. A marca `gosto:N` no fim de cada item liga a regra à correção que a
originou; `scripts/test-preferencias.py` reprova se uma correção nova ficar sem par aqui.

## Proibido (lê como "cara de IA" ou "mal feito")

- **[gate `gate-sem-kicker.py`] Kicker em caixa alta abrindo seção.** Rótulo curto, em caixa
  alta e com letra espaçada, em cima do título ("POR QUE CONTINUAR", "PARA VOCÊ"). A seção abre
  direto no título. <!-- gosto:1 -->
- **Rótulo interno de card** ("Esse programa exige"): na fonte dos títulos, em tamanho contido,
  numa linha, nunca em caixa alta espaçada. <!-- gosto:8 -->
- **[gate `gate-sem-kicker.py`] Numeração decorativa 01/02/03** no topo de card ou de passo.
  <!-- gosto:2 -->
- **[gate `gate-sem-kicker.py`] Número gigante decorativo em card** (um "4" ou um "1" enorme ao
  lado do título, como enfeite). Se o número é informação, ele vai na frase ("turmas de até 4
  pessoas").
- **Foto de pessoa num retângulo de bordas redondas puro.** Foto de gente pede moldura com
  identidade: um recorte com forma própria, um fio na cor da marca deslocado, o símbolo da
  marca na borda. Retângulo arredondado com sombra é o padrão de template. Sem pílula ou
  legenda flutuante sobre a foto: a legenda, se houver, vai embaixo dela. <!-- gosto:3 -->
- **Crop que decapita a pessoa ou esconde a cena.** A pessoa aparece INTEIRA. Se não couber,
  a seção vira split, com a foto num lado e o conteúdo no outro. O crop se confere na JANELA
  renderizada (print), nunca no arquivo. <!-- gosto:4 -->
- **Imagem que não casa com o conteúdo da seção.** Pessoa rindo numa seção de dor reprova;
  pose avançada de exercício numa página para iniciante com dor também. Seção de problema pode
  viver sem imagem. Liste o que cada foto mostra contra o título ao lado dela. <!-- gosto:5 -->
- **Imagem decorativa dentro da seção de preço (pricing).** É a seção mais importante da
  página e fica limpa. <!-- gosto:6 -->
- **[gate `gate-simetria.mjs`] Colunas desbalanceadas** (uma termina muito antes da outra):
  colunas vizinhas não terminam com mais de 80 px de diferença. Alinhar pelo topo e pela base,
  ou reestruturar a seção. <!-- gosto:11 -->
- **Pílula de etiqueta dentro de mockup** (um chip "exemplo" no cabeçalho de uma caixa de
  entrada, de uma tela, de um cartão). O aviso de que é exemplo vai só como legenda discreta
  embaixo do mockup, nunca como chip ou pílula dentro dele. <!-- gosto:14 -->

## Itens paralelos, passos, FAQ e fecho

- **[gate `gate-simetria.mjs`] Itens paralelos vão em caixas simétricas e animadas.** Grupo de
  3 ou 4 itens do mesmo tipo (situações, benefícios, passos, perguntas) é grade de caixas com
  mesma largura, mesma altura, topo e conteúdo interno alinhados, e entrada escalonada ao
  rolar. Item solto flutuando em alturas diferentes (escada) reprova. Sequência de passos
  também vira grade de caixas iguais (em linha no desktop, uma coluna no celular), com o
  título da seção em largura total em cima: "título à esquerda + lista vertical à direita"
  reprova no desktop ("não tá simétrico"). Título de seção de processo fala com quem compra
  ("Como funciona para você começar"), não com quem constrói. <!-- gosto:15 -->
- **[gate `gate-simetria.mjs`] Caixa de grade tem ícone animado ÚNICO e alturas iguais
  medidas.** Top e height iguais com 1 px de tolerância, medidos depois da animação; o texto
  de cada caixa na mesma faixa de linhas. Cada caixa com um SVG próprio, desenhado para o
  texto dela e animado (traço que se desenha, leve deslocamento). Biblioteca de ícone genérico
  em quadradinho continua proibida: o problema era o genérico, não o ícone. <!-- gosto:20 -->
- **Fecho e FAQ também animam.** Seção final parada e FAQ numa caixa só com metade da tela
  vazia reprovam. FAQ com o título em largura total e as perguntas em grade (ou numa coluna
  centrada), entrando com movimento; fecho com pelo menos um movimento além do título.
  <!-- gosto:19 -->

## Botões e oferta

- **Botões de navegação rolam para a oferta** (`#oferta`, ou a seção de agendamento no
  serviço local), MENOS o do topo. Só os botões DENTRO da oferta e no fecho saem para o
  checkout, o WhatsApp ou o formulário. <!-- gosto:7 -->
- **Botão do topo não fala de preço.** O botão da primeira dobra puxa para a dor ou para a
  solução ("Ver como funciona", levando à seção que explica), e o preço não aparece na
  primeira dobra. Botão de preço só depois da prova e na barra. <!-- gosto:16 -->
- **Preço composto não parece plano alternativo.** Entrada + mensalidade vão num bloco só, com
  "+" entre as partes e a linha-resumo "R$ X na entrada + R$ Y por mês". Dois cartões soltos
  lado a lado leem como "escolha um ou outro". <!-- gosto:17 -->
- **[gate `gate-responsivo.mjs`] Botão em UMA linha** em 320, 360, 390 e 768 px. Rótulo curto
  no celular ("Agendar pelo WhatsApp") em vez de botão que quebra em duas linhas.
- **[gate `gate-responsivo.mjs`] Botão a no máximo 2 telas** em qualquer ponto da rolagem do
  celular: barra fixa depois do hero ou botão repetido. Trecho de mais de 2 telas sem nenhum
  botão visível reprova.

## Estruturas aprovadas

- **Pricing limpa:** título em largura total em cima; ancoragem compacta num card (itens em
  2 colunas, total no cabeçalho); cards de preço em fileira (empilham no tablet), preço
  grande em linha própria, parcela embaixo, regra separada por fio; botão centralizado
  fechando a seção.
- **Par de comparação (antes e depois, com e sem): LADO A LADO e ASSIMÉTRICO.** Empilhado
  reprova; simétrico também. O lado que interessa leva mais largura, começa mais alto e
  carrega o movimento; o outro fica mais estreito, recuado e parado. O título de cada coluna
  fica centralizado sobre a própria coluna. Duas OPÇÕES (grupo e particular, plano A e B) não
  são comparação: ficam lado a lado, alinhadas pelo topo e com a mesma altura. <!-- gosto:12 -->
- **Bom = cor viva COM movimento; ruim = vermelho parado.** A cor do botão (CTA) não serve
  de sinal de aprovação: sobre fundo escuro, laranja e vermelho leem como alerta.
  <!-- gosto:13 -->
- **Imagem gerada por IA:** conceito criativo encaixado no produto, nunca retrato de estúdio
  genérico ("mais do mesmo"). Rosto de gente real só com material real ou com autorização de
  uso de imagem. <!-- gosto:9 -->
- **Vídeo de fundo:** véu mais leve (a faixa sob o texto intacta e o contraste medido no
  pixel) e clipe mais lento (playbackRate perto de 0,7) para dar tempo de ver. <!-- gosto:10 -->

## Texto na tela

- **[gate `gate-texto.mjs`] Sem palavra sozinha na última linha (viúva) em h1 e h2**, no
  desktop e no celular. `text-wrap: balance` nos títulos e `text-wrap: pretty` nos parágrafos
  resolvem quase todos os casos; o resto se resolve na copy.
- **[gate `gate-texto.mjs`] Todo item de texto visível começa com letra maiúscula**: descrição
  de card, item de lista, legenda, rótulo de botão. "até 4 pessoas por turma" reprova.
- **[gate `gate-texto.mjs`] No máximo uma palavra em itálico colorida na página inteira.** A
  fórmula "serifa + uma palavra em itálico colorida" repetida em vários títulos é tell (ver
  V16 em `references/anti-vibe-coding.md`).

## Foto e público

- **A foto bate com o público do briefing**: idade, perfil e roupa adequada ao que a página
  vende. Para mulheres de 35 a 60 com dor, modelo de 25 de top cropped em pose avançada
  reprova. O plano visual registra a tabela "público -> foto escolhida -> por quê".
- **Nenhum elemento gráfico atravessa rosto ou corpo de pessoa na foto** (linha, grade,
  selo, forma da assinatura). A assinatura mora ao lado da foto, nunca por cima de gente.
- **Foto com logo de terceiro na cena reprova** (outro estúdio na parede, marca de fabricante
  legível, nome de academia na roupa). Retoque o logo ou troque a foto, e registre o retoque.
- **[gate `gate-composicao.mjs`] Público de pessoas se vê na página**, na primeira tela: foto
  real autorizada ou ilustração própria no traço da identidade, nas situações reais da página.
  Página "correta e vazia", só com objeto, ficou em 7,0 (auditoria da v5).
- **[gate `gate-composicao.mjs`] Desenho lê de primeira.** Retângulo dentro de retângulo é
  wireframe; desenho de situação mostra corpo e gesto. Traço fino e destaque a 3:1 do fundo.

## Lições operacionais

- **Asset trocado = NOME trocado.** Trocar o conteúdo de uma imagem mantendo o nome faz o
  navegador mostrar a versão velha em cache. Versione o nome do arquivo e confira o byte no
  domínio (md5 local contra o publicado).
- **Arquivo e caixa na MESMA proporção.** Gere o asset já no formato da caixa:
  `object-fit: cover` com proporções diferentes corta de forma imprevisível.
- **Grade de 6 itens: 3x2**, nunca 4 + 2.
- **Descrição de card começa com letra maiúscula.**
- **Variante "com visual diferente" não é troca de copy.** Se a página nova mantém a mesma
  gramática (mesma grade de cartões, mesmo botão, mesmo título), é a mesma página. Mexa em 4
  dos 6 eixos do CAMINHO 2B e confira com `scripts/lado-a-lado.py`.
- **Fundo contínuo: UMA camada fixa**, com planos que entram na rolagem e nunca voltam a
  zero. Fundo por seção, cada um com sua máscara, cria faixa escura em toda emenda.
  `animation-timeline: scroll(root block)` exige `animation-duration: auto` (o padrão é 0s).
- **`radial-gradient` em porcentagem mede até o CANTO mais longe.** Numa máscara de caixa
  quadrada, 82% fica fora da borda e a máscara não apaga nada. Use `closest-side`.
- **Promessa só do que o negócio entrega**, conferida contra a fonte e contra as outras
  versões da página. A tabela "frase da página -> linha do briefing" do passo d e o
  `scripts/gate-verdade.py` cobram isso, inclusive na meta description e na og:description.
- **Só sobe para o ar o que é página.** O deploy sai de `dist/`, montada pelo
  `scripts/montar-dist.py` e conferida pelo `scripts/gate-publicacao.py`: prints de terceiros,
  briefing, evidências e JSON de auditoria nunca vão junto.
- **Cada seção com um tratamento próprio.** O mesmo título à esquerda com grade de caixas em
  seção após seção lê como template mesmo com caixas perfeitas (auditoria da v4: 4 seções
  seguidas, 14 caixas). Grade de caixas onde há itens paralelos; nas outras, linha do tempo,
  lista editorial, split com imagem, faixa cheia. `scripts/gate-composicao.mjs` reprova 3
  seguidas iguais e ícone de biblioteca.
- **Animação acontece na visita, não no print.** Revelação só do que entra na tela;
  temporizador que revela tudo reprova no `scripts/gate-movimento.mjs`.
- **Celular: ou botão no cabeçalho, ou barra fixa.** O que é fixo soma até 15% da tela, 1 botão
  de ação por tela, nenhum botão sob a barra, e a foto do herói aparece na primeira tela.
- **Sem autorização de imagem, sem pessoa identificável.** A licença do fotógrafo não cobre a
  imagem de quem aparece; o espaço, o aparelho ou um desenho próprio resolvem, com "imagem
  ilustrativa" também no og-image (`scripts/gate-imagens.py`).
