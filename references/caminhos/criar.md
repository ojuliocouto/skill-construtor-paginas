# Caminho CRIAR: página nova, do zero

Oito passos, cada um com um gate que bloqueia. Saída diferente de zero em qualquer comando =
PARA e conserta antes de seguir. `<dir-da-skill>` = a pasta desta skill; `<dir>` = a pasta do
projeto da página. Cada comando vai inteiro na linha (variável com comando não roda no zsh).

A ordem existe por um motivo: a página só sai no nível das melhores do ramo se a direção
nascer delas (b), virar um plano deliberado antes do código (c) e for cobrada por olhos
adversariais no fim (g). Gate mecânico verde não é página boa; é o piso.

**Sessão interativa:** mostre o plano visual (c) e a copy (d) e espere o ok antes de construir.
**Sessão não interativa** (subagente, "faz direto"): siga sem parar, rode todos os gates e liste
na entrega as decisões que o dono deveria ter aprovado. A exceção dispensa a parada, nunca o gate.

## Antes de tudo

1. `python3 <dir-da-skill>/scripts/checar-ferramentas.py`
   Crítico: python3, node, Playwright com Chromium e a skill `frontend-design`. Faltou crítico:
   conduza a instalação (o comando aparece na saída) e só então siga. Opcional ausente não
   bloqueia nada.
2. Leia `references/preferencias-de-design.md`: vale para toda página.
3. Projeto que já existiu: leia `references/projects/<projeto>.md` e a sessão mais recente em
   `references/sessions/` (arquivos locais, fora do Git).

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

Grave `evidencias/briefing.md` e `evidencias/etapa-0.json` (campos em `references/gate-etapas.md`):
`python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 0 --arquivo evidencias/etapa-0.json`

## b. Pesquisa de referências

Método completo em `references/pesquisa-de-referencias.md`. Em resumo: buscar na web 6 a 10
páginas REAIS (pelo menos 2 do mesmo tipo de negócio e 2 de design de alto nível), printar cada
uma e escrever o que ela faz bem e o princípio que se leva dela.

`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> <url> ...`
`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo design <url> <url> ...`

Abra os dois PNGs de cada uma (Read), preencha `faz_bem`, `principio` e `lido: true` no
manifesto e escreva `referencias/sintese.md`. Gate:

`python3 <dir-da-skill>/scripts/gate-referencias.py --projeto <dir>`
`python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 1 --arquivo evidencias/etapa-1.json`

**GATE b:** sem 6 prints reais lidos (2 de cada tipo), o plano visual não começa.

## c. Plano visual, pela skill `frontend-design`

Acione a skill de verdade (Skill tool, `frontend-design`) com o briefing e a síntese das
referências na mão. Ela trabalha em duas passadas: rascunha o plano e depois o revisa contra o
padrão que sairia para qualquer página parecida. Escreva o resultado em `<dir>/plano-visual.md`,
ANTES de qualquer código:

- **Assunto, público e trabalho da página**, em uma frase cada
- **Direção** em uma frase, e de quais referências ela vem (princípio, nunca cópia)
- **Paleta**: 4 a 6 cores com nome e hex
- **Tipografia**: display (com personalidade, usada com contenção), corpo e, se precisar,
  utilitária; escala com tamanhos e pesos
- **Como a imagem entra**: que foto, de quê, com que luz e enquadramento, em que seções, e a
  tabela **público -> foto escolhida -> por quê** (uma linha por foto de pessoa: idade, perfil
  e roupa da pessoa na foto contra o público do briefing). Ela vai para o campo `foto_publico`
  da etapa 2, e o gate da etapa reprova sem ela
- **Ritmo das seções**: a ordem, o layout de cada uma em uma linha ou em wireframe ASCII, onde
  a página respira e onde adensa
- **Assinatura**: o elemento único pelo qual a página vai ser lembrada, e o risco estético
  que ela assume. Ela mora AO LADO da foto, nunca por cima de gente: linha, grade ou forma que
  atravessa rosto ou corpo de pessoa reprova (na v3, o prumo cortava a cabeça da modelo)
- **Revisão**: o que mudou entre a primeira e a segunda passada, e por quê. Os três visuais
  padrão de IA (creme com serifa e terracota; quase preto com um acento ácido; "jornal de
  filetes": muitos fios finos, uma palavra em itálico colorida em vários títulos e fundo de
  grade decorativo) só entram se o briefing pediu

**Precedência:** identidade real do cliente (logo, cor, fonte que ele já usa) vence
`references/preferencias-de-design.md`, que vence o plano. O banco de design
(`python3 <dir-da-skill>/scripts/search.py "<termo>" --domain style`) é consulta opcional:
pode dar ideia, nunca decide.

`python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> registrar "skill frontend-design" --arquivo plano-visual.md --detalhe "plano visual em duas passadas"`
`python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 2 --arquivo evidencias/etapa-2.json`

**GATE c:** sem `plano-visual.md` com os oito itens e a etapa 2 registrada, nenhuma linha de código.

## d. Copy

- Serviço local ou agendamento (estúdio, clínica, consultório, salão): o modelo curto
  `references/copy-servico-local.md`.
- Outros tipos: as seções do tipo em `references/page-types.md` (modelo geral), com headline
  que diz para quem e o que resolve, botão com verbo e ganho, objeções respondidas na página e
  urgência só se for real.
- Se o cliente já trouxe a copy: só valide e organize; copy aprovada não se reescreve.

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

`python3 <dir-da-skill>/scripts/gate-verdade.py --projeto <dir>`

**Sem cliente ainda:** a página MOSTRA só substitutos verificáveis (credencial, fotos reais do
espaço, endereço, horário, CNPJ, condição confirmada) e OCULTA o espaço do depoimento futuro
como `<section data-reservado="depoimentos" hidden>`, que não é placeholder porque ninguém vê.
Na tela, nada de "em breve depoimentos", estrela ou contador.

Grave `evidencias/copy.md` e registre (o JSON da etapa 3 leva `"sustentacao": "evidencias/sustentacao.md"`): `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 3 --arquivo evidencias/etapa-3.json`

## e. Construção

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
   enquadramento), nunca a primeira que aparece. Registre cada uma em `imagens/LICENCAS.md`
   (arquivo, página de origem, autor, licença). Foto que não é do cliente leva "imagem
   ilustrativa" e nunca pode sugerir ser o espaço ou a profissional dele. Arquivo e caixa na
   mesma proporção; WebP; `width` e `height`; `srcset` e `sizes` em TODA foto (não só no
   hero: a foto da sala de 1500 px exibida a 348 px custou 171 KiB no Lighthouse da v3);
   `loading="lazy"` abaixo da dobra; `fetchpriority="high"` no hero.
   **A foto bate com o público** do briefing (idade, perfil, roupa adequada), como registrado
   na tabela do plano visual. **Logo de terceiro na cena reprova** (outro estúdio na parede,
   marca de fabricante legível, nome na roupa): amplie a foto 4x num recorte, procure, e
   retoque ou troque; o retoque vai escrito em `imagens/LICENCAS.md`. A legenda "imagem
   ilustrativa" fica colada na foto que ela descreve, dentro do mesmo card.
3. **Movimento em CSS:** entrada do hero, 2 a 4 revelações nas seções-chave (no máximo uma por
   seção), hover e microinteração no botão, `prefers-reduced-motion` respeitado. Conteúdo
   nunca depende de animação para aparecer. Grade de itens paralelos entra escalonada e cada
   caixa tem o próprio SVG animado; FAQ e fecho também têm movimento.
   **Texto:** `text-wrap: balance` em h1 e h2, `text-wrap: pretty` em parágrafo e pergunta.
   **Botão no celular:** rótulo que cabe numa linha em 320 px e, abaixo de 768 px, barra fixa
   inferior depois do hero (ou botão repetido a cada 2 telas).
   **Peso:** fonte só nos pesos e estilos usados (itálico de 144 KiB para 3 palavras foi achado
   da v3); CSS em linha na publicação (`montar-dist.py --css-em-linha`).
4. **Identidade da página** (bloqueia, com ou sem deploy): `<title>` próprio, meta description,
   favicon PNG quadrado e `apple-touch-icon`, `og:title`, `og:description` e `og:image`.
   Favicon: recorte quadrado primeiro, depois redimensione.
5. **Fora do domínio final, a página nasce `noindex`:** `<meta name="robots" content="noindex,
   nofollow">`, `robots.txt` com `Disallow: /`, sem sitemap, `canonical` apontando para o site
   do cliente quando existir.
6. **Rodapé com identificação** (nome, contato e o que o cliente confirmou) e todo botão com
   destino real. WhatsApp sem número é pendência declarada, e a página não recebe tráfego.

Grave `evidencias/etapa-4.json` e registre: `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 4 --arquivo evidencias/etapa-4.json`

## f. Gates mecânicos

Sirva com compressão (medir sem gzip inverte o resultado) e mate o servidor no fim:
`python3 <dir-da-skill>/scripts/servidor-gzip.py <dir> 8765`

Rode cada gate e registre o exit REAL na wave:

`python3 <dir-da-skill>/scripts/gate-sem-kicker.py <dir>/index.html` (kicker, 01/02/03, número gigante)
`python3 <dir-da-skill>/scripts/gate-classes-mortas.py --projeto <dir>` (classe que não existe no CSS)
`node <dir-da-skill>/scripts/gate-responsivo.mjs --url http://localhost:8765/` (12 telas)
`node <dir-da-skill>/scripts/gate-oclusao.mjs --url http://localhost:8765/` (texto coberto ou cortado)
`node <dir-da-skill>/scripts/gate-simetria.mjs --url http://localhost:8765/` (itens paralelos em caixas iguais, passos fora da coluna ao lado do título, colunas que terminam juntas)
`node <dir-da-skill>/scripts/gate-texto.mjs --url http://localhost:8765/` (viúva em h1 e h2, item em minúscula, itálico colorido repetido)
`python3 <dir-da-skill>/scripts/gate-verdade.py --projeto <dir>` (promessa com linha do briefing, metas incluídas)
`python3 <dir-da-skill>/scripts/montar-dist.py --projeto <dir> --css-em-linha` e `python3 <dir-da-skill>/scripts/gate-publicacao.py --dist <dir>/dist` (só o que é página vai para o ar)
`node <dir-da-skill>/scripts/screenshot-prova.js http://localhost:8765/ <dir>/prova --click "<seletor do botão>"` (identidade, scrollY 0, clique)
`python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> registrar Playwright --arquivo prova/prova-desktop.png --detalhe "prova de tela lida"`
`python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> checar --caminho criar`
`python3 <dir-da-skill>/scripts/gate-referencias.py --projeto <dir>`
`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> gate <nome> --exit <0|1> --detalhe "<o que o gate imprimiu>"`
(nomes: `sem-kicker`, `classes-mortas`, `responsivo`, `oclusao`, `identidade`, `uso-ferramentas`, `referencias`, `simetria`, `texto`, `verdade`, `publicacao`)

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

Lighthouse quando houver Chromium (pendência declarada quando não houver). SEO abaixo de 90
sob `noindex` é esperado se a única auditoria reprovada for `is-crawlable`.

## g. Auditores

As 9 lentes de `references/auditores.md`: as 8 de sempre mais a `comparacao-referencias`, que
põe a página ao lado das referências mais fortes do passo b.

**A rodada de auditores roda com um subagente auditor independente quando o ambiente permite**
(Agent ou Task com o tipo `auditor`, ou um subagente comum com o mandato de refutar): ele
recebe a URL, a `dist/`, o briefing, a tabela de sustentação, a pasta `referencias/` e as
preferências, e nunca o histórico da construção. Cada lente se registra com `--origem subagente`.
**Nota de autoavaliação não libera entrega:** sem subagente, a checagem em sequência serve para
achar e corrigir defeito, mas fica registrada com `--origem autoavaliacao` e o `wave.py rodada`
responde AUDITORIA INDEPENDENTE PENDENTE até uma rodada de outra sessão (sem o histórico, com
`--origem sessao-independente`) ou de outra pessoa (`--origem pessoa`). Na v3, a autoavaliação
deu média 7,78 e "tells 0"; o auditor independente deu 5,5 e cinco achados graves.

`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> registrar <lente> --veredito <aprovado|reprovado> --nota <0-10> --origem <subagente|sessao-independente|pessoa|autoavaliacao> --achados "<o que olhou e achou>"`
`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> checar`
`python3 <dir-da-skill>/scripts/wave.py --projeto <dir> rodada --criticos <N> --altos <N> --pendencias-do-usuario <N> --regressoes <N>`

Saiu CONTINUA: corrige, refaz os gates do passo f que a correção toca, roda de novo as lentes
com achado. **Lente `comparacao-referencias` reprovada = volta ao passo c**, refaz o plano a partir
das referências e reconstrói; não se compensa com nota nas outras lentes. Fechado o ciclo, o
passe de gosto: tells antes e depois, o depois é 0.

## h. Prova e entrega

1. Print final pelo `screenshot-prova.js` (desktop 1440 e celular 390, página inteira em scrollY
   0). Nunca por script próprio: cabeçalho fixo no meio do print é artefato de rolagem.
2. **Leia os PNGs com os próprios olhos** (Read): a página inteira para ritmo e composição, e
   recortes 1:1 para texto, rótulo e borda. Screenshot reduzido não aprova detalhe.
3. A interação principal clicada nos dois viewports.
4. Re-registrar a etapa 4 depois dos auditores é esperado (`references/gate-etapas.md`); depois:
   `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 5 --arquivo evidencias/etapa-5.json`
5. Deploy (opcional para aluno): **sai só de `dist/`**, montada por `montar-dist.py` e aprovada
   pelo `gate-publicacao.py`, nunca da pasta do projeto (na v3 ela tinha 94 arquivos e 18 MB,
   com prints de terceiros e o briefing da cliente). Nunca sobrescrever projeto que já tem
   conteúdo; página nova entra em subpasta do projeto existente. Sem conta de hospedagem, a
   entrega é local e o deploy vira pendência declarada.
6. A mensagem de entrega leva o bloco do SKILL.md (auditores, identidade, passe de gosto, prova,
   pendências) e o link ou os prints.

## Depois da entrega

Registre a sessão em `references/sessions/AAAA-MM-DD-<projeto>.md` e o projeto em
`references/projects/<projeto>.md` (locais, fora do Git; modelos em `EXAMPLE.md`). Medição
real (mapa de calor, conversão) só depois de tráfego: primeira leitura em 48 horas.
