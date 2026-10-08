# Caminho CRIAR: página nova, do zero

Oito passos e o PLANO (b2), cada um com um gate que bloqueia. Saída diferente de zero em qualquer comando =
PARA e conserta antes de seguir. `<dir-da-skill>` = a pasta desta skill; `<dir>` = a pasta do
projeto da página. Cada comando vai inteiro na linha (variável com comando não roda no zsh).

A ordem existe por um motivo: a página só sai no nível das melhores do ramo se a direção
nascer delas (b), virar um plano deliberado antes do código (c) e for cobrada por olhos
adversariais no fim (g). Gate mecânico verde não é página boa; é o piso.

**Sessão interativa:** mostre o PLANO (b2) com o `direcoes.png` e espere o aluno marcar as aprovações
antes de construir.
**Sessão não interativa** (subagente, "faz direto"): siga sem parar, rode todos os gates e liste
na entrega as decisões que o dono deveria ter aprovado. A exceção dispensa a parada, nunca o gate.

## Antes de tudo

1. `node <dir-da-skill>/scripts/py.mjs checar-ferramentas.py`
   Crítico: Python 3, node, Playwright com Chromium e a skill `frontend-design`. Faltou crítico:
   conduza a instalação (o comando aparece na saída) e só então siga. Opcional ausente não
   bloqueia nada.
2. Leia `references/preferencias-de-design.md`: vale para toda página.
3. Projeto que já existiu: leia `<projeto>/contexto-do-projeto.md` e a sessão mais recente em
   `<projeto>/sessoes/` (na pasta do projeto, nunca na da skill).

## a. Briefing

O que o negócio vende, para quem, a oferta e o que existe de material REAL. Pergunte junto,
numa lista curta, com exemplos do nicho do pedido:

1. O que você vende, exatamente? (o serviço, não a categoria)
2. Onde atende? (cidade e bairro, ou online)
3. Para quem? (pessoa: gênero e faixa de idade; empresa: porte, segmento e quem decide)
4. Qual a oferta? (aula experimental, avaliação, plano mensal, pacote)
5. Quanto custa, mais ou menos?
6. O que a pessoa faz na página, e para onde vai? (qual WhatsApp, qual formulário, qual checkout)

E o inventário do material real: fotos do espaço e da equipe, logo, depoimentos com
autorização, número de contato, credencial do profissional (registro no conselho), endereço,
horário, CNPJ.

**Palpite só em interpretação** (nicho, público, dor, objeção): a pessoa corrige em dois
segundos. **Nunca em fato** (preço, número, depoimento, credencial, resultado, prazo): o que
faltar vira lista de pendências do cliente e não aparece na página até ser confirmado. Modo não
interativo: as cinco de interpretação saem como `SUPOSICAO`, o preço fica PENDENTE e o botão leva
para a conversa.

**Modelo do `evidencias/briefing.md`: um campo próprio para o teste fictício.** Quando o negócio é inventado para testar a
skill, o briefing traz, numa linha sozinha, `Negócio fictício de teste: sim`. Sem essa linha o negócio é real, e o
`gate-imagens.py` REPROVA foto de banco cujo `alt`, legenda ou bloco de depoimento atribui um nome próprio de pessoa
("Marina Coutinho, Icaraí" ao lado de um retrato de banco afirma que aquela é a Marina). Com a linha, o gate deixa passar e
imprime "permitido porque o briefing declara teste fictício". Frase solta no texto ("é um negócio fictício") não vale: tem de
ser o campo, com "sim". Em projeto real, o retrato de banco leva alt ilustrativo e nenhum nome, ou entra a foto do cliente
com autorização.

Grave `evidencias/briefing.md` e `evidencias/etapa-0.json` (campos em `references/gate-etapas.md`):
`node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 0 --arquivo evidencias/etapa-0.json`

## b. Pesquisa de referências

Método completo em `references/pesquisa-de-referencias.md`. Em resumo: buscar na web 6 a 10
páginas REAIS (pelo menos 2 do mesmo tipo de negócio e 2 de design de alto nível), printar cada
uma e escrever o que ela faz bem e o princípio que se leva dela.

`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> <url> ...`
`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo design <url> <url> ...`

Abra os dois PNGs de cada uma (Read), preencha `faz_bem`, `principio` e `lido: true` no
manifesto e escreva `referencias/sintese.md`. Gate:

`node <dir-da-skill>/scripts/py.mjs gate-referencias.py --projeto <dir>`
`node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 1 --arquivo evidencias/etapa-1.json`

**GATE b:** sem 6 prints reais lidos (2 de cada tipo), o plano visual não começa.

## b2. PLANO (obrigatório, antes de qualquer código)

Método e modelo completos em `references/plano.md`. Um documento único, `<dir>/PLANO.md`, com
sete seções que o aluno aprova: a. Referências (os prints, cada um com o que faz bem, e as que
ele marcou), b. Visual (3 direções BEM diferentes, feitas com a `frontend-design`, cada uma com
a primeira dobra real renderizada em PNG), c. Seções (o cardápio de `references/secoes/README.md`
com miniatura e "quando usar", a ordem que ele montou e, desde a 3.5, a tabela
`Composição por seção`: desktop, celular e animação de cada uma), d. Copy (frase -> linha do
briefing que sustenta), e. Pixel e rastreamento (`references/rastreamento.md`), f. Código e
publicação e g. Aprovação. No topo do PLANO, além do pixel: o **Momento assinatura** (um elemento
ligado ao assunto, em 3 ou mais seções, que muda de estado) e o **Material da cliente pedido**
(foto real da profissional, número do WhatsApp, depoimentos com autorização). Estética por seção
em `references/ritmo-e-animacao.md`.

`node <dir-da-skill>/scripts/previa-direcoes.mjs --saida <dir>/plano <dir>/plano/direcoes/a.html <dir>/plano/direcoes/b.html <dir>/plano/direcoes/c.html`
`node <dir-da-skill>/scripts/previa-direcoes.mjs --miniaturas <dir-da-skill>/references/secoes --saida <dir>/plano/miniaturas`

Abra o `plano/direcoes.png` (Read): se duas direções parecem a mesma página com outra cor,
refaça uma delas antes de mostrar.

`node <dir-da-skill>/scripts/py.mjs gate-plano.py --projeto <dir>`

**GATE b2:** sem `PLANO.md` aprovado (as 7 seções, as 3 prévias, a copy sustentada, o pixel
declarado, o momento assinatura, a composição por seção, o material da cliente e todas as caixas
marcadas), o plano visual e o código não começam.

**Momento assinatura em negócio de produto físico.** Quando o que se vende é algo que a pessoa toca, come, veste, habita ou dirige (móveis, comida, imóvel, moda, obra, carro, joia, planta), o momento assinatura é FOTO REAL do produto, nunca desenho nem ilustração figurativa. A receita é `foto-que-se-monta`: a foto do produto se monta em faixas até ficar inteira, com um rótulo ou cota por cima no fim (ex.: "Carvalho maciço, quatro tábuas, montada na sua casa"). Se o cliente ainda não mandou a foto, declare a foto como pendência do plano e use a melhor foto de ambiente do acervo; nunca desenhe o produto no lugar. Desenho só entra quando o que se vende não tem imagem (serviço abstrato, método, software), e mesmo nesse caso a tela real do produto vem antes de qualquer ilustração. Nesses negócios rode o `gate-composicao.mjs` com `--produto-fisico`: ele avisa se o momento assinatura ficou só em SVG. Palavras do dono: "Considerando que se trata de móveis, visual real conta mais que qualquer outra coisa."

## c. Plano visual, pela skill `frontend-design`

Acione a skill de verdade (Skill tool, `frontend-design`) com o briefing, a síntese das
referências e a direção que o aluno escolheu no PLANO na mão: o plano visual detalha essa
direção (e a mistura, se ele pediu), sem reabrir as outras. Ela trabalha em duas passadas: rascunha o plano e depois o revisa contra o
padrão que sairia para qualquer página parecida. Escreva o resultado em `<dir>/plano-visual.md`,
ANTES de qualquer código:

- **Assunto, público e trabalho da página**, em uma frase cada
- **Direção** em uma frase, e de quais referências ela vem (princípio, nunca cópia)
- **Paleta**: 4 a 6 cores com nome e hex
- **Tipografia**: display (com personalidade, usada com contenção), corpo e, se precisar,
  utilitária; escala com tamanhos e pesos
- **Como a imagem entra**: que foto, de quê, com que luz e enquadramento, em que seções, e a
  tabela **público -> foto escolhida -> por quê** (uma linha por foto de pessoa: idade, perfil
  e roupa da pessoa na foto contra o público do briefing, mais a coluna "quem aparece cuidando"
  contra o dono nomeado no briefing). Ela vai para o campo `foto_publico`
  da etapa 2, e o gate da etapa reprova sem ela. **Foto real antes de ilustração** (do cliente, ou
  de banco livre como ponte); ilustração só como acento (`references/imagem.md`)
- **Ritmo das seções**: a ordem, o layout de cada uma em uma linha ou em wireframe ASCII, onde
  a página respira e onde adensa. **Cada seção ganha um tratamento próprio**, tirado de uma
  referência lida (lista editorial, linha do tempo, split com imagem, faixa cheia, grade de
  caixas onde a regra de itens paralelos pede), e a seção que é o diferencial do negócio leva o
  tratamento mais forte. Vai para o campo `secoes` da etapa 2 (`{secao, tratamento, referencia}`):
  o mesmo tratamento em 3 seções seguidas reprova (na v4, 4 seções seguidas tinham h2 à
  esquerda e grade de caixas, e a página leu como template). **Desenhos e ícones** se desenham
  para o assunto e vão no campo `icones` (`{secao, desenha}`); metáfora de biblioteca (balão de
  conversa, calendário com check, boneco de palito) reprova, e o SVG na página leva
  `data-desenho` com a mesma descrição
- **Assinatura**: o elemento único pelo qual a página vai ser lembrada, e o risco estético
  que ela assume. Ela mora AO LADO da foto, nunca por cima de gente: linha, grade ou forma que
  atravessa rosto ou corpo de pessoa reprova (na v3, o prumo cortava a cabeça da modelo)
- **Ícone do site**: uma linha `Ícone do site: <motivo>` (o que o favicon desenha em 32 px, ligado ao
  assunto e à assinatura). O gate da etapa 2 cobra a linha; o passo e.4 só gera os PNG a partir dela
- **Revisão**: o que mudou entre a primeira e a segunda passada, e por quê. Os três visuais
  padrão de IA (creme com serifa e terracota; quase preto com um acento ácido; "jornal de
  filetes": muitos fios finos, uma palavra em itálico colorida em vários títulos e fundo de
  grade decorativo) só entram se o briefing pediu

**Arquivo registrado que muda derruba o registro (acontece aqui).** O `plano-visual.md` é evidência da etapa 2 e da
`frontend-design` no `uso-ferramentas.py`, e cada registro guarda o hash do arquivo. Se você editar o arquivo DEPOIS de
registrar (acontece quando a linha `Ícone do site:` ou a paleta muda no passo e), o `uso-ferramentas.py checar` e o
`gate-etapas.py` reprovam em cascata, e a mensagem de cada um já traz os comandos na ordem: acionar a ferramenta de
novo, `uso-ferramentas.py registrar ... --arquivo`, e `gate-etapas.py registrar` das etapas 2, 3 e 4, nessa ordem.
Para não passar por isso: feche o plano visual (com a linha do ícone) ANTES de registrar a etapa 2.

**Precedência:** identidade real do cliente (logo, cor, fonte que ele já usa) vence
`references/preferencias-de-design.md`, que vence o plano. O banco de design
(`node <dir-da-skill>/scripts/py.mjs search.py "<termo>" --domain style`) é consulta opcional:
pode dar ideia, nunca decide.

`node <dir-da-skill>/scripts/py.mjs uso-ferramentas.py --projeto <dir> registrar "skill frontend-design" --arquivo plano-visual.md --detalhe "plano visual em duas passadas"`
`node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 2 --arquivo evidencias/etapa-2.json`

**GATE c:** sem `plano-visual.md` com os oito itens e a etapa 2 registrada, nenhuma linha de código.

## d. Copy

- Serviço local ou agendamento (estúdio, clínica, consultório, salão): o modelo curto
  `references/copy-servico-local.md` e os 7 itens de densidade de
  `references/densidade-servico-local.md` (quem cuida, primeiro atendimento passo a passo, para quem
  é e para quem não é, horários, faixa de preço, onde fica, o que levar).
- Outros tipos: as seções do tipo em `references/page-types.md` (modelo geral), com headline
  que diz para quem e o que resolve, botão com verbo e ganho, objeções respondidas na página e
  urgência só se for real.
- Se o cliente já trouxe a copy: só valide e organize; copy aprovada não se reescreve.
- A copy aprovada na seção d do PLANO é o ponto de partida: ela vira `evidencias/copy.md`, e a
  tabela dela vira a tabela de sustentação abaixo.

Toda frase com número, preço, credencial ou resultado precisa de fonte no briefing.

**Tabela de sustentação (bloqueia):** junto com a copy, escreva `evidencias/sustentacao.md` com a
tabela `| Frase da página | Linha do briefing que sustenta |`, uma linha por frase que promete
(grátis, número, prazo, preço, resultado, credencial), mais o title, a meta description, o
og:title e a og:description (a prévia do link no WhatsApp também promete). A sustentação é a
linha do briefing entre aspas; "interpretação" só serve para frase que não promete nada. Embaixo,
a seção `## Não afirmar (pendências)`: para cada frase PENDENTE do briefing, um padrão entre
crases com o que a página não pode insinuar. Caso real: com "se a avaliação é gratuita e se é no
mesmo dia" pendente, "Você chega, faz a avaliação postural e começa" e "aula grátis com avaliação
postural" afirmam as duas coisas. A forma honesta: "Antes da primeira aula, você passa por uma
avaliação postural", em frase própria, sem "grátis" e sem "no mesmo dia".

A `evidencias/sustentacao.md` é a tabela VIVA: nasce com a copy do PLANO e cresce até a página
final. A copy final, as respostas da FAQ, os rótulos de barra e qualquer frase nova com promessa
entram nela quando entram na página; a tabela da seção d do PLANO fica como foto do plano e
deixa de ser a fonte. A citação pode ser copiada do briefing tal e qual, inclusive com ponto e
vírgula ou quebra de linha no meio. O crédito de imagem (bloco com `data-credito`, `id="creditos"`
ou classe `creditos`) não é promessa e não entra na tabela, desde que a frase tenha cara de crédito (licença, autor,
fonte, título da obra). Frase ali dentro com R$, %, "garantia", "dias", "clientes", "nota", "grátis" e afins continua
exigindo linha: marcar um bloco como crédito não é porta dos fundos. Quando falta linha, o gate imprime a
linha pronta pra colar, por seção; a citação você preenche com o briefing, nunca com palavra sua.

No passo d a página ainda não existe, então o gate roda sem `index.html` e confere SÓ a tabela
contra o briefing (citação existe, não é PENDENTE, promessa não se apoia em "interpretação",
nenhum padrão de "Não afirmar" aparece nas frases). Ele diz: "página ainda não existe: conferi só a
tabela; rode de novo no passo f". A conferência completa, com a página, é a do passo f.

`node <dir-da-skill>/scripts/py.mjs gate-verdade.py --projeto <dir>`

**Sem cliente ainda:** a página MOSTRA só substitutos verificáveis (credencial, fotos reais do
espaço, endereço, horário, CNPJ, condição confirmada) e OCULTA o espaço do depoimento futuro
como `<section data-reservado="depoimentos" hidden>`, que não é placeholder porque ninguém vê.
Na tela, nada de "em breve depoimentos", estrela ou contador.

Grave `evidencias/copy.md` e registre (o JSON da etapa 3 leva `"sustentacao": "evidencias/sustentacao.md"`): `node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 3 --arquivo evidencias/etapa-3.json`

## e. Construção

**Antes da primeira linha:** `node <dir-da-skill>/scripts/py.mjs gate-plano.py --projeto <dir>` verde.
A construção segue a ordem escolhida no PLANO, com os formatos de `references/secoes/`.

**Stack padrão: HTML + Tailwind compilado.** React só se o projeto destino já for React ou se
a página precisar de estado de verdade (calculadora, quiz, checkout em etapas). Nunca
`cdn.tailwindcss.com`.

`npx tailwindcss@3 -i _input.css -o tailwind-compiled.css --content ./index.html --minify`

1. **Construa SÓ o primeiro bloco (o hero) e olhe** antes de replicar o padrão:
   `node <dir-da-skill>/scripts/screenshot-prova.js "file://<dir>/index.html" <dir>/prova-hero --sem-identidade`
   Abra o PNG. Ele corresponde ao plano visual? Fica de pé ao lado da referência mais forte?
   Se não, corrija o hero agora: é o único ponto em que corrigir é barato.
2. **Imagens:** material real do cliente primeiro. Sem ele, banco com licença livre (Openverse
   pelo `scripts/assets-search.py "<tema em inglês>" --type photo`, Unsplash, Pexels,
   Wikimedia Commons), escolhida pelo que as referências ensinaram (assunto, luz,
   enquadramento), nunca a primeira que aparece. Registre cada uma em `imagens/LICENCAS.md`,
   na tabela com as colunas `Arquivo publicado | Origem | Autor | Título | Licença | Link da
   licença | Alteração | Pessoa identificável | Autorização de imagem | Aviso de ilustrativa`,
   uma linha também para o og-image. **Licença com nome, versão e link** ("CC BY-SA 3.0" com
   https://creativecommons.org/licenses/by-sa/3.0/; Unsplash e Pexels com o link da licença
   deles), e o crédito no rodapé repete autor, título, licença com versão e o link; versão
   alterada de CC BY-SA diz que segue a mesma licença. **Direito de imagem:** licença do
   fotógrafo não cobre a imagem de quem aparece; sem autorização das retratadas, prefira foto
   sem pessoa identificável (o espaço, o aparelho) ou ilustração própria. Na v4, a foto era de
   um estúdio real com duas pessoas identificáveis, o crédito vinha sem versão e sem link da
   licença, e o og-image saía sem "imagem ilustrativa"; o `gate-imagens.py` reprova os três. Foto que não é do cliente leva "imagem
   ilustrativa" e nunca pode sugerir ser o espaço ou a profissional dele. Arquivo e caixa na
   mesma proporção; WebP; `width` e `height`; `srcset` e `sizes` em TODA foto (não só no
   hero: a foto da sala de 1500 px exibida a 348 px custou 171 KiB no Lighthouse da v3);
   `loading="lazy"` abaixo da dobra; `fetchpriority="high"` no hero.
   **A foto bate com o público** do briefing (idade, perfil, roupa adequada), como registrado
   na tabela do plano visual, e **não contradiz o texto ao lado** (quem cuida na foto tem o mesmo
   gênero e papel da profissional nomeada). **Nenhuma foto nem cena repetida entre seções** e
   **nenhuma foto borrada** (nitidez de 100 ou mais); foto de banco com gente leva "imagem
   ilustrativa" visível na primeira tela, e a pessoa identificável sem autorização é aviso de
   tráfego real (`references/imagem.md`). **Logo de terceiro na cena reprova** (outro estúdio na parede,
   marca de fabricante legível, nome na roupa): amplie a foto 4x num recorte, procure, e
   retoque ou troque; o retoque vai escrito em `imagens/LICENCAS.md`. A legenda "imagem
   ilustrativa" fica colada na foto que ela descreve, dentro do mesmo card.
   **O crédito usa o título REAL da fonte** (o do endereço do Unsplash ou da Wikimedia) ou
   nenhum título entre aspas: a v5 publicou um título inventado (`gate-imagens.py`).
   **Público de pessoas se vê na página:** na primeira tela, em 1440 e em 390, aparece uma
   figura humana do público: foto real com autorização das retratadas ou ilustração própria
   (SVG desenhado para a página, no traço da identidade, com `data-figura="pessoa"`, mostrando
   o público nas situações reais da página). Imagem gerada por IA de pessoa fotorrealista não
   resolve. A v5 tinha só uma sala vazia e 7 desenhos de objeto para "mulheres de 35 a 60 com
   dor nas costas", e o auditor perguntou "cadê as pessoas?" (`gate-composicao.mjs --projeto`).
   **Desenho lê de primeira, sem o texto:** retângulos e retas alinhadas (planta baixa, mesa
   de linhas) leem como wireframe e reprovam; traço fino e destaque com pelo menos 3:1 contra
   o que está embaixo deles (o amarelo da v5 estava a 2,07:1).
3. **Movimento em CSS:** entrada do hero, cada item revelado quando ELE entra na tela (gramática
   única de curva e duração) mais momentos próprios ligados ao conteúdo, hover e microinteração no botão, `prefers-reduced-motion` respeitado. Conteúdo
   nunca depende de animação para aparecer. **Revele só o que entra na tela:** nada de
   `setTimeout` que marca tudo como visível (na v4, 3 s depois da carga as 6 seções já estavam
   reveladas com a página parada no topo, e a visita chegava em tudo parado); o
   `gate-movimento.mjs` simula a visita e reprova. Grade de itens paralelos entra escalonada e cada
   caixa tem o próprio SVG animado; FAQ e fecho também têm movimento. **Revele por ITEM, não por
   grupo:** cada caixa, passo e pergunta revela quando ela mesma entra na tela; na v5, a 300 px/s
   no celular, a 3a situação, o 3o passo e duas perguntas chegavam já paradas. **Movimento
   reduzido desliga a rolagem suave** (`scroll-behavior: auto` dentro de
   `@media (prefers-reduced-motion: reduce)`).
   **Texto:** `text-wrap: balance` em h1, h2, h3 e título de card (na v4, os h3 dos passos ficaram com palavra sozinha em 768 e o h2 do fecho em 320), `text-wrap: pretty` em parágrafo e pergunta.
   **Botão no celular:** rótulo que cabe numa linha em 320 px e, abaixo de 768 px, barra fixa
   inferior depois do hero (ou botão repetido a cada 2 telas). **Ou botão no cabeçalho ou barra
   fixa, nunca os dois:** o que é fixo soma até 15% da tela em 390 e 320; no máximo 1 botão de
   ação visível por tela (a barra some quando há botão da página à vista) e nenhum botão encostado
   ou coberto pela barra. Na v4 eram 152 px fixos (18% em 390, 28% em 320), 3 botões na mesma tela
   e a barra cobrindo o botão de "Duas formas". **Foto do herói na primeira tela do celular** com
   pelo menos 35% da altura (na v4: 134 px em 390 e nenhum em 320, com o rosto cortado na dobra). A barra escondida leva
   `visibility: hidden` além do `translate`: só deslocada, ela aparece no print de página
   inteira logo abaixo da primeira tela, por cima da foto (medido na v4).
   **Peso:** fonte só nos pesos e estilos usados (itálico de 144 KiB para 3 palavras foi achado
   da v3); CSS em linha na publicação (`montar-dist.py --css-em-linha`).
   **Baixar a fonte:** `node <dir-da-skill>/scripts/baixar-fontes.mjs --familia "Bricolage Grotesque" --pesos 400,700 --saida fonts`
   baixa do Google Fonts só o subconjunto latino em woff2 (um arquivo variável quando a família tem eixo de peso, senão um
   por peso), grava em `fonts/` e imprime o `@font-face` pronto, com `font-display: swap` e o `url()` relativo. Cole no CSS,
   dê `<link rel="preload" as="font" type="font/woff2" crossorigin>` à fonte do título e liste só os pesos que a página usa.
   Sem internet ele diz qual endereço não respondeu e não deixa arquivo pela metade.
3b. **Padrão da v7 na construção** (cada item custou retrabalho): a animação de cada seção sai
   do repertório (`references/receitas-de-movimento.md`, com a página `references/receitas/demo.html`
   para ver cada uma andando) ou declara `criação nova: <motivo>` no PLANO; o momento assinatura do plano
   aparece nas seções que ele listou; cada seção tem esqueleto, celular e animação próprios
   (`references/ritmo-e-animacao.md`); assimetria pedida no plano leva `data-assimetrico="motivo"`
   no contêiner (o `gate-simetria.mjs` a trata como aviso); carrossel no celular é composição, com
   `overflow-x: auto` e `scroll-snap-type`, e a página sem rolagem lateral; altura de layout em
   `--vh` medido (`references/vh-estavel.md`); sticky num grid que termina antes do bloco de
   largura total (`references/sticky-e-sobreposicao.md`); texto dividido em linhas sem `span`
   interno e `li > span` em CSS (`references/texto-em-linhas.md`).
4. **Identidade da página** (bloqueia, com ou sem deploy): `<title>` próprio, meta description,
   favicon PNG quadrado e `apple-touch-icon`, `og:title`, `og:description` e `og:image`.
   Favicon: recorte quadrado primeiro, depois redimensione. **O ícone é a identidade ATUAL:** o
   plano declara `Ícone do site: <motivo>`, o motivo é desenhado em `icones/icone.svg` (com o
   mesmo `data-motivo`, e a página desenha esse motivo em algum `data-desenho`: **copie a frase do motivo, letra por letra, para dentro do
   `data-desenho` do SVG que o desenha** (pode vir no meio de uma descrição maior; palavra trocada não vale)) e os PNG saem de
   `node <dir-da-skill>/scripts/gerar-icones.mjs --projeto <dir>`. **A og:image sai de um comando** (1200x630, o título, a foto e a
   faixa "Imagem ilustrativa" quando a foto é de banco, com a fonte da marca de `fonts/`; sem fonte, usa a do sistema e diz que é reserva):
   `node <dir-da-skill>/scripts/gerar-og-image.mjs --projeto <dir> --titulo "<título>" --foto imagens/hero.jpg --ilustrativa`. A v5 publicou o favicon da v3
   (md5 igual), com um motivo que a página já tinha abandonado. Se o motivo do ícone mudar aqui, o `plano-visual.md` muda e os registros dele caem (ver o aviso do passo c): refaça
   na ordem que a mensagem do gate mostra.
5. **Fora do domínio final, a página nasce `noindex`:** `<meta name="robots" content="noindex,
   nofollow">`, `robots.txt` com `Disallow: /`, sem sitemap, `canonical` apontando para o site
   do cliente quando existir.
6. **Rodapé com identificação** (nome, contato e o que o cliente confirmou) e todo botão com
   destino real. WhatsApp sem número é pendência declarada, e a página não recebe tráfego.
   **Quem é o dono ou a profissional aparece no corpo**, quando o briefing nomeia (com o que o
   briefing permite dizer, sem inventar credencial); na v5 a fisioterapeuta só estava no rodapé.
7. **Rastreamento, se o PLANO pediu:** o snippet de `references/rastreamento.md` no fim do
   `<head>`, com os IDs vazios no `window.RASTREIO` até o aluno preencher, e o `data-evento`
   em cada link de WhatsApp (`clique_whatsapp`), no botão principal (`clique_cta`) e em cada
   formulário (`envio_formulario`).
8. **Nenhum comentário interno no HTML publicado** (`<!-- -->`, `//` e `/* */` em script e
   style; só o aviso de licença `/*! */` passa): a v5 publicou o histórico da construção num
   comentário do script.

Grave `evidencias/etapa-4.json` e registre: `node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 4 --arquivo evidencias/etapa-4.json`

## f. Gates mecânicos

Sirva com compressão (medir sem gzip inverte o resultado) e mate o servidor no fim:
`node <dir-da-skill>/scripts/py.mjs servidor-gzip.py <dir> 8765`

Rode cada gate e registre o exit REAL na wave:

`node <dir-da-skill>/scripts/py.mjs gate-sem-kicker.py <dir>/index.html` (kicker, 01/02/03, número gigante)
`node <dir-da-skill>/scripts/py.mjs gate-classes-mortas.py --projeto <dir>` (classe que não existe no CSS)
`node <dir-da-skill>/scripts/gate-responsivo.mjs --url http://localhost:8765/` (12 telas)
`node <dir-da-skill>/scripts/gate-oclusao.mjs --url http://localhost:8765/` (texto coberto ou cortado)
`node <dir-da-skill>/scripts/gate-simetria.mjs --url http://localhost:8765/` (itens paralelos em caixas iguais, passos fora da coluna ao lado do título, colunas que terminam juntas, título com título nos cards vizinhos com 4 px de folga, conteúdo interno sem buraco, texto das caixas na mesma faixa de linhas e passos em caixas)

**Limite de colunas desbalanceadas (`gate-simetria.mjs`): 80 px.** Para cada filho de um grid ou flex em linha, a base
é a base da caixa (se ele tem fundo, borda ou sombra) ou o fim do último texto ou ilustração visível dentro dele. Dois
filhos lado a lado não podem terminar com mais de 80 px de diferença entre as bases. A falha diz qual elemento mediu em
cada coluna e onde terminou (`último texto p.fatos, termina em y 812` contra `base da caixa figure.foto, termina em y
893`). Se a coluna de texto termina antes, prenda o último bloco ao rodapé (`margin-top: auto` com o grid esticado) ou
estique a foto até a mesma altura; se a assimetria é pedida no plano, declare `data-assimetrico="motivo"`.
`node <dir-da-skill>/scripts/gate-texto.mjs --url http://localhost:8765/` (viúva em título e subtítulo, de h1 a h4, dt e summary, e em parágrafo na fonte do título ou dentro de caixa, em 7 telas de 320 a 1440; item em minúscula; itálico colorido repetido)
`node <dir-da-skill>/scripts/gate-composicao.mjs --url http://localhost:8765/ --projeto <dir>` (mais de 2 seções seguidas com o mesmo esqueleto, desenho sem `data-desenho`, ícone de biblioteca ou repetido, desenho que lê como wireframe, linha do tempo que passa do último marco, nenhuma pessoa na primeira tela para público de pessoas, destaque abaixo de 3:1)
Negócio de produto físico (móveis, comida, imóvel, moda, obra, carro): acrescente `--produto-fisico` ao comando acima. Se o momento assinatura estiver só em desenho, o gate AVISA (não reprova) que ele deve ser foto real do produto, receita `foto-que-se-monta`.
`node <dir-da-skill>/scripts/gate-movimento.mjs --url http://localhost:8765/` (visita de 8 s parada no topo e depois rolagem: animação que roda fora da tela reprova, pelo menos 2 seções animam ao chegar, nenhum item chega parado numa rolagem de 300 px/s em 1440, 390 e 320, e, com movimento reduzido, nenhuma animação em curso acima de 0,2 s nem rolagem suave)
`node <dir-da-skill>/scripts/py.mjs gate-verdade.py --projeto <dir>` (promessa com linha do briefing, metas incluídas, e o dono nomeado no briefing no corpo da página)
`node <dir-da-skill>/scripts/py.mjs gate-imagens.py --projeto <dir> --url http://localhost:8765/` (licença com versão e link, crédito no HTML com o título real da fonte, aviso no og-image; foto repetida entre seções por pHash e origem, nitidez abaixo de 100, "imagem ilustrativa" e 60% de foto na primeira tela medidos no navegador; pessoa identificável de banco é aviso de tráfego real, e `--trafego-real` a reprova)
`node <dir-da-skill>/scripts/gate-ritmo.mjs --url http://localhost:8765/` (duas seções vizinhas com o mesmo esqueleto e mais de 1 "título centralizado + cartões")
O `secoes.json` sai da tabela "Composição por seção" do PLANO, sem escrever à mão:
`node <dir-da-skill>/scripts/py.mjs plano-para-secoes.py --projeto <dir> --html index.html --saida <dir>/prova/anim/secoes.json`.
Ele infere o nome, o título, o tipo (`assinatura-em-tres-estados` vira `assinatura`), o modo (`heroi` para
`abertura-do-topo`, `rolagem` para a assinatura em "estado 2"), o clique da FAQ (`<seletor> summary`) e o seletor de cada
seção (`#id` ou a primeira classe, pela ordem, só quando o HTML tem o mesmo número de `<section>` que a tabela). O que não
dá para inferir sai como `PREENCHER: ...` e o `anim.mjs` se recusa a rodar até você trocar; carrossel no celular vira aviso
(acrescente `rolarHorizontal`). Exemplo completo, gerado do PLANO do Ateliê Veio:

```json
[
 {"nome": "01-primeira-dobra", "seletor": ".heroi", "titulo": "Primeira dobra", "tipo": "abertura-do-topo", "modo": "heroi"},
 {"nome": "04-depoimentos", "seletor": "#depoimentos", "titulo": "Depoimentos", "tipo": "revelar-ao-entrar"},
 {"nome": "06-como-funciona", "seletor": "#como-funciona", "titulo": "Como funciona", "tipo": "assinatura", "modo": "rolagem"},
 {"nome": "08-duvidas", "seletor": "#duvidas", "titulo": "Dúvidas", "tipo": "pergunta-que-abre", "clique": "#duvidas summary"},
 {"nome": "09-fecho", "seletor": "#fecho", "titulo": "Fecho", "tipo": "assinatura"}
]
```

`node <dir-da-skill>/scripts/anim.mjs --url http://localhost:8765/ --saida <dir>/prova/anim --secoes <dir>/prova/anim/secoes.json` e `node <dir-da-skill>/scripts/py.mjs prancha.py --pasta <dir>/prova/anim --secoes <dir>/prova/anim/secoes.json` (3 quadros por seção em 1440 e 390 e a prancha com a porcentagem de pixels que mudou; abra as pranchas)
`node <dir-da-skill>/scripts/py.mjs gate-animacao.py --pasta <dir>/prova/anim --plano <dir>/PLANO.md` (menos de 2% de pixels mudando entre início e fim, mais de 2 seções com o mesmo tipo, menos pranchas que linhas da tabela do plano)
`node <dir-da-skill>/scripts/sobreposicao.mjs --url http://localhost:8765/ --fixo "<seletor do sticky>" --contra "<seletor do bloco largo>"` (um para cada elemento fixo: 0 px² em 1024 a 1920)
`node <dir-da-skill>/scripts/py.mjs montar-dist.py --projeto <dir> --css-em-linha` e `node <dir-da-skill>/scripts/py.mjs gate-publicacao.py --dist <dir>/dist` (só o que é página vai para o ar, sem comentário interno, e ícones gerados do `icones/icone.svg` do motivo do plano)
`node <dir-da-skill>/scripts/py.mjs gate-rastreamento.py --dist <dir>/dist --plano <dir>/PLANO.md` (pixel e eventos que o plano pediu; passa direto com `Pixel pedido: nenhum`)
`node <dir-da-skill>/scripts/py.mjs gate-plano.py --projeto <dir>` (o plano continua aprovado depois das correções)
`node <dir-da-skill>/scripts/screenshot-prova.js http://localhost:8765/ <dir>/prova --click "<seletor do botão>"` (identidade, scrollY 0, clique)
`node <dir-da-skill>/scripts/py.mjs uso-ferramentas.py --projeto <dir> registrar Playwright --arquivo prova/prova-desktop.png --detalhe "prova de tela lida"`
`node <dir-da-skill>/scripts/py.mjs uso-ferramentas.py --projeto <dir> checar --caminho criar`
`node <dir-da-skill>/scripts/py.mjs gate-referencias.py --projeto <dir>`
`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> gate <nome> --exit <0|1> --detalhe "<o que o gate imprimiu>"`
(nomes: `sem-kicker`, `classes-mortas`, `responsivo`, `oclusao`, `identidade`, `uso-ferramentas`, `referencias`, `simetria`, `texto`, `verdade`, `publicacao`, `movimento`, `composicao`, `imagens`, `plano`, `rastreamento`, `ritmo`, `animacao`)

O `gate-responsivo.mjs` também reprova botão em mais de uma linha até 768 px e trecho de mais de
2 telas sem botão no celular. Rode os gates de tela contra a `dist/` servida (é o que vai para o ar).

Página com vídeo: `node <dir-da-skill>/scripts/gate-video.mjs --url <url> --publico <dir>` (exige ffmpeg).

Conferências que nenhum script faz sozinho, e que a lente content-auditor cobra:
- `grep` de travessão (U+2014 e U+2013) em todo arquivo da página: zero
- contato dígito por dígito em todo `tel:` e `wa.me`
- diff de claims: cada frase, cada FOTO (o que ela mostra contra o título ao lado), cada campo
  do JSON-LD e cada alt contra o briefing
- comentário no código que afirma comportamento ("fica sólido", "aparece") só depois de medido
- edição por script com `assert` da troca e medida no navegador: build verde não prova pixel
- **edição por script e gates na mesma linha: ligue com `&&`, nunca com `;` nem em linhas soltas.** Se o `assert` da troca falha, o `&&` para ali; sem ele os gates rodam em cima da página velha e a rodada inteira (minutos) mede o que você já tinha. Ex.: `python edita.py && bash gates-todos.sh`

Lighthouse quando houver Chromium (pendência declarada quando não houver). SEO abaixo de 90
sob `noindex` é esperado se a única auditoria reprovada for `is-crawlable`.

## g. Auditores

As 9 lentes de `references/auditores.md` (as 8 de sempre mais a `comparacao-referencias`, que
põe a página ao lado das referências mais fortes do passo b) são CRITÉRIOS. **A rodada é UM
subagente auditor independente que as percorre numa passada só** e devolve um bloco por lente.
Uma lente por subagente é modo opcional, só se a pessoa pedir auditoria profunda.

**Checklist do pacote, obrigatório (A33): o briefing reflete o último pedido da pessoa?** Antes de chamar o auditor, releia o
`evidencias/briefing.md` contra o que foi pedido POR ÚLTIMO e responda `--briefing-reflete-pedido sim|nao` (sem a resposta, ou com
`nao`, o pacote fica incompleto). Se você registra os pedidos em `evidencias/pedidos.md` (um por linha, o arquivo é tocado a cada
pedido novo), a data decide: briefing mais antigo que o último pedido dá AVISO e a pergunta é dispensada. Motivo: no teste real o
cliente mudou o pedido no meio e o auditor conferiu a página contra um briefing velho.

**Briefing pronto, com orçamento.** O `pacote-auditoria.py` grava `auditoria/briefing-do-auditor.md`: cole-o no prompt do
auditor. Ele traz os caminhos do pacote e o orçamento (rodada 1: 15 minutos e 30 chamadas de ferramenta; rodada 2: 8 minutos
e 15 chamadas), proíbe recapturar o que já está no pacote (só abre a página para interação, foco, hover e script bloqueado,
no máximo 6 capturas próprias), manda devolver "não verificado" por lente o que não deu tempo, e pede só o schema. Informe a
duração e as chamadas no `wave.py registrar` (`--duracao-min`, `--chamadas`); o `wave.py rodada` avisa se passou. (A auditoria
real levou 51 minutos e 113 chamadas sem esse teto.)

**Antes de chamar o auditor, junte o pacote de evidência UMA vez** (ele não captura as telas de
novo). Gere o que ainda não existir, nesta ordem, e confira:

1. Prints: `node <dir-da-skill>/scripts/screenshot-prova.js http://localhost:8765/ <dir>/provas --com-360 --com-320` (os gates do passo f já geram parte).
2. Vídeo de prova: `node <dir-da-skill>/scripts/gravar-video.js http://localhost:8765/ --saida <dir>/videos` (passo h, item 3b, que reaproveita estes arquivos).
3. `node <dir-da-skill>/scripts/py.mjs pacote-auditoria.py --projeto <dir> --url http://localhost:8765/` `--briefing-reflete-pedido sim|nao`

O pacote tem: a URL, a `dist/`, o briefing (`evidencias/briefing.md`), o `PLANO.md`, a tabela de
sustentação, a pasta `referencias/` (síntese e `*-dobra.png`), as capturas dos gates
(`prova-desktop.png` e `prova-mobile.png`) e as pranchas do vídeo (`prancha-desktop.png` e
`prancha-mobile.png`). O script lista o que achou e o que falta, avisa se a captura é anterior à
última mudança da `dist/` e sai 1 se faltar item obrigatório: sem pacote completo, não chame o auditor.

O auditor é um subagente independente (Agent ou Task com o tipo `auditor`, ou um subagente comum com o
mandato de refutar): recebe o pacote (`auditoria/pacote.json`) e as preferências, e nunca o
histórico da construção. Cada lente se registra com `--origem subagente`, uma por lente (as 9
notas e vereditos), com o veredito que o auditor deu.
**Nota de autoavaliação não libera entrega:** sem subagente, a checagem em sequência serve para
achar e corrigir defeito, mas fica registrada com `--origem autoavaliacao` e o `wave.py rodada`
responde AUDITORIA INDEPENDENTE PENDENTE até uma rodada de outra sessão (sem o histórico, com
`--origem sessao-independente`) ou de outra pessoa (`--origem pessoa`). Na v3, a autoavaliação
deu média 7,78 e "tells 0"; o auditor independente deu 5,5 e cinco achados graves.

`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> registrar <lente> --veredito <aprovado|reprovado> --nota <0-10> --origem <subagente|sessao-independente|pessoa|autoavaliacao> --achados "<o que olhou e achou>"`
A `comparacao-referencias` responde também, com `--gosto bonito|correto`, a pergunta do dono
depois da SobrAI (9,05 nas lentes e "que página FEIA"): **isso é bonito ou só está correto?**
"correto" não aprova e a rodada não entrega: corrija os eixos abaixo das referências (`--eixos-abaixo`); sem resposta, a rodada também não entrega.
`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> checar`
   **Correção depois da rodada 2 (3.5.9):** se a conferência fechou em NÃO ENTREGAR e você corrigiu o achado, em sessão não interativa
   (ninguém para autorizar a rodada extra) a regra é: feche em NÃO ENTREGAR, liste na entrega cada correção feita depois do
   ciclo (achado, o que mudou, a medida do conserto) e peça a rodada extra por escrito; nota de autoavaliação não libera.
   Mudança GRANDE pedida pelo dono ENTRE as rodadas reabre a rodada 1: `node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> reabrir --motivo "<o que o dono pediu>"`
   (uma vez por ciclo, registrada; lentes e gates recomeçam). Detalhe em `references/auditores.md`.
`node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> rodada --criticos <N> --altos <N> --pendencias-do-usuario <N> --regressoes <N>`

**Teto de 2 rodadas.** Saiu CONTINUA na rodada 1: corrige, refaz os gates do passo f que a
correção toca, junta o pacote de novo (`pacote-auditoria.py --rodada 2`, depois de salvar os achados
em `auditoria/achados-rodada-1.json`) e fecha a rodada 2, que é de CONFERÊNCIA (`references/auditores.md`,
"Rodada 2"): o mesmo auditor confere se cada achado foi corrigido, se a correção quebrou outra
coisa, e mais nada; não reabre as 9 lentes. Depois dela o ciclo fecha SEMPRE: aprovado, ENTREGA COM
RESSALVAS (achados que sobraram e nota real, na entrega) ou NÃO ENTREGAR: crítico aberto. Terceira
rodada só se a pessoa pedir (`--rodada-extra-pedida`, registrada). **Lente `comparacao-referencias` reprovada NÃO manda reconstruir sozinha** (o teto é 2 rodadas e a segunda é
conferência): o `wave.py rodada` lista os eixos abaixo das referências e você os corrige na página, entre as rodadas;
refazer o plano visual e reconstruir é um ciclo novo, só se a pessoa pedir. Não se compensa com nota nas outras lentes. Fechado o ciclo, o
passe de gosto: tells antes e depois, o depois é 0.

## h. Prova e entrega

1. Print final pelo `screenshot-prova.js` com `--com-360 --com-320` (desktop 1440, celular 390,
   Android 360 e o menor suportado, 320, página inteira em scrollY 0), servindo a `dist/`. Nunca por script próprio: cabeçalho fixo no meio do print é artefato de rolagem.
2. **Leia os PNGs com os próprios olhos** (Read): a página inteira para ritmo e composição, e
   recortes 1:1 para texto, rótulo e borda. Screenshot reduzido não aprova detalhe.
3. A interação principal clicada nos dois viewports (`--click "<seletor>"`). Botão que é link de WhatsApp ou outro link externo: o clique é capturado e a navegação cancelada, então o teste não sai da página e o print de depois mostra a página; o destino aparece na saída ("o clique levaria a ..."). Confira o número dígito por dígito pelo `href`. Navegação feita por script (`location.href`) também é barrada, mas aí o print de depois não é tirado.
3b. **Vídeo da rolagem, junto dos prints** (já gravado no passo g para o pacote do auditor: reaproveite
   se a página não mudou depois, refaça se mudou): com a página servida, grave desktop e celular do topo ao
   fim em ritmo de leitura:
   `node <dir-da-skill>/scripts/gravar-video.js http://localhost:8765/ --saida <dir>/videos`
   (usa o `roteiro-pagina.json` da pasta de scripts: abre, espera a abertura, rola meia janela a cada 1,5 s e
   tira 7 quadros; leva de 30 a 70 s). **Leia as duas pranchas** (`prancha-desktop.png` e
   `prancha-mobile.png`): o vídeo prova o movimento, a prancha prova o que apareceu em cada ponto.
   **Roteiro próprio** (`--roteiro arquivo.json`): o roteiro padrão só rola a página; efeito que pede clique ou mouse (painel de cor
   de tela inteira, hover do botão) só aparece num roteiro seu. Página com `[data-painel]`: parta do `roteiro-demo-receitas.json` da pasta de scripts da skill, que já
   clica. O gravador confere tudo de uma vez e recusa o roteiro que quebra qualquer limite: `abrir` é o primeiro passo;
   `esperar` de 0 a 10000 ms; `rolar_pagina` com `passo` de 0,2 a 1, `espera_ms` de 300 a 3000, `max_passos` de 1 a 45 e `prints` de 0 a 8;
   no mínimo 6 prints no roteiro; `duracao_minima_s` de 10 a 15; duração prevista de 10 a 90 s (com `rolar_pagina` vale o pior caso:
   `max_passos` x (`espera_ms` + 300 ms) + 1,2 s). A mensagem de recusa repete essa lista de limites.
   Sem a rolagem chegar ao fim da página, a gravação reprova. Os dois `.webm` entram em
   `video` na etapa 5; etapa sem vídeo não registra.
4. Re-registrar a etapa 4 depois dos auditores é esperado (`references/gate-etapas.md`); depois:
   `node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> registrar 5 --arquivo evidencias/etapa-5.json`
5. Deploy (opcional para aluno): **sai só de `dist/`**, montada por `montar-dist.py` e aprovada
   pelo `gate-publicacao.py`, nunca da pasta do projeto (na v3 ela tinha 94 arquivos e 18 MB,
   com prints de terceiros e o briefing da cliente). Nunca sobrescrever projeto que já tem
   conteúdo; página nova entra em subpasta do projeto existente. Sem conta de hospedagem, a
   entrega é local e o deploy vira pendência declarada.
6. **Relatório só com medida gravada:** cada número (px, %, s, KiB, :1, telas, Lighthouse) cita
   entre crases o arquivo de texto do gate que o mediu, e o arquivo é da `dist/` entregue. Na v4
   o auditor refutou 10 afirmações do relatório, entre elas um Lighthouse 100 medido antes da
   versão final. `node <dir-da-skill>/scripts/py.mjs gate-relatorio.py --relatorio <relatório.md> --base <dir> --dist <dir>/dist`
7. A mensagem de entrega leva o bloco do SKILL.md (auditores, identidade, passe de gosto, prova,
   pendências) e o link ou os prints.

## Depois da entrega

Registre a sessão em `<projeto>/sessoes/AAAA-MM-DD.md` e o projeto em
`<projeto>/contexto-do-projeto.md` (na pasta do PROJETO: dado de cliente nunca fica na pasta da skill, regra de
`references/gate-etapas.md`; os modelos, só para copiar, são `references/sessions/EXAMPLE.md` e `references/projects/EXAMPLE.md`). Medição
real (mapa de calor, conversão) só depois de tráfego: primeira leitura em 48 horas.

## Mudança de briefing no meio do trabalho (A32)

Se o cliente pediu outra coisa depois de etapas já registradas, não refaça tudo nem pule etapa: atualize o `evidencias/briefing.md` e rode
`node <dir-da-skill>/scripts/py.mjs gate-etapas.py --projeto <dir> revalidar --motivo "<o que mudou no pedido>"`. Em ordem, para cada
etapa registrada: se nada mudou, fica; se SÓ o briefing mudou, o gate da etapa roda de novo sobre o JSON dela e, passando, ela é
re-registrada com o motivo gravado (`revalidada`); se QUALQUER outra evidência mudou (a tabela de sustentação, o plano, o próprio JSON),
a etapa continua exigindo o gate dela (`registrar`) e nada é gravado. Revalidar NÃO é atalho: a copy que depende do briefing pede
`gate-verdade.py` de novo (o comando avisa). O motivo tem 15 caracteres no mínimo.
