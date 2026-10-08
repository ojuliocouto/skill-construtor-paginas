# Auditores adversariais (passo g do CRIAR)

A auditoria nunca é feita pelo mesmo olhar que construiu: quem construiu não enxerga o
próprio erro. Por isso a página passa por **um subagente auditor independente que percorre as
9 lentes numa passada só**. As 9 lentes são CRITÉRIOS, as mesmas do `scripts/wave.py`
(dicionário `LENTES`): design-critic, assets-auditor, visual-auditor, motion-auditor,
responsive-auditor, cro-auditor, a11y-auditor, content-auditor e comparacao-referencias.
Quem decide se entrega é o ciclo (`wave.py rodada`), não a nota. O ciclo tem **teto de 2
rodadas** e a segunda é de conferência, não uma auditoria nova (seção mais abaixo).

Por que um só (v3.5.4): o dono perguntou "esses 9 revisores são necessários?", a regra dele é
teto de 2 rodadas de corrigir e auditar, e a skill roda ao vivo em aula, onde a página demorar
a ficar pronta é o problema. Nove subagentes por rodada capturavam as mesmas telas nove vezes.
Os critérios continuam todos; muda quantos agentes rodam e quantas rodadas.

## Como rodar

1. A página servida com compressão (`scripts/servidor-gzip.py`) e os gates do passo f verdes.
2. **O pacote de evidência, juntado UMA vez pela sessão principal, antes de chamar o auditor.**
   O auditor recebe a evidência pronta e não captura as telas de novo. O pacote tem:
   - a URL da página servida;
   - a `dist/` (`dist/index.html`);
   - o briefing (`evidencias/briefing.md`), o `PLANO.md`, a tabela de sustentação
     (`evidencias/sustentacao.md`) e, quando existir, o `plano-visual.md`;
   - a pasta `referencias/` (a `sintese.md` e os `*-dobra.png`);
   - as capturas de tela que os gates já produziram: `prova-desktop.png` e `prova-mobile.png`
     (`screenshot-prova.js`), com as de 360 e 320 se foram feitas;
   - as pranchas do vídeo de prova: `prancha-desktop.png` e `prancha-mobile.png`
     (`gravar-video.js`), mais as pranchas de animação por seção quando existirem;
   - as preferências do dono da skill, quando o projeto as usa.
   Gere uma vez o que ainda não existir (prints e vídeo, `references/caminhos/criar.md` passo g) e confira:
   `node <dir-da-skill>/scripts/py.mjs pacote-auditoria.py --projeto <dir> --url <url>`.
   Ele lista o que achou, o que falta e o que está velho (capturado antes da última mudança da
   página), grava `auditoria/pacote.json` e sai 1 se faltar item obrigatório. Não chame o auditor
   com pacote incompleto: ele ia capturar por conta própria, de novo.
3. **Quando o ambiente permite subagentes (o padrão):** UM subagente auditor independente (o
   tipo `auditor`, ou um subagente comum com mandato de refutar), que recebe o pacote e as
   preferências, sem o histórico da construção. Ele percorre as 9 lentes numa passada, lê o
   pacote, só abre a página para o que as capturas não mostram (interação, foco, hover) e
   devolve o schema abaixo: um bloco por lente. O registro continua um por lente (as 9 notas e
   vereditos), com `--origem subagente`.

   **Cole o BRIEFING PRONTO no prompt do auditor.** O `pacote-auditoria.py` o gera já preenchido, em `auditoria/briefing-do-auditor.md`: a pasta do projeto (caminho absoluto), todos os
   caminhos do pacote (todas as referências, as telas de 360 e 320 e as pranchas de animação), as 9 lentes, os arquivos de critério
   (`auditores.md`, `preferencias-de-design.md`, `anti-vibe-coding.md`), o schema de retorno (com `gosto` e `eixos_abaixo` na lente
   de referências) e o orçamento. Colar o arquivo basta. O texto (a versão gerada traz os caminhos e o número da rodada):

   > Você é o auditor independente. Refute, não revise: ache o que está errado e diga onde, com a medida.
   > **Orçamento desta rodada:** rodada 1, 15 minutos e no máximo 30 chamadas de ferramenta; rodada 2, 8 minutos e 15 chamadas.
   > **Proibido recapturar o que já está no pacote** (telas, pranchas, vídeo). Só abra a página para o que print não mostra:
   > interação, foco, hover, script bloqueado, e no máximo 6 capturas próprias.
   > O que não deu tempo de olhar volta como **"não verificado"**, por lente, em vez de estourar o tempo.
   > A resposta é o schema, sem relatório longo. No fim, diga a duração em minutos e o número de chamadas.

   Registre o gasto: `wave.py registrar <lente> ... --duracao-min <minutos> --chamadas <n>` (em qualquer lente, a maior vale).
   O `wave.py rodada` AVISA (não reprova) quando a rodada passou do orçamento. Motivo: o auditor único da auditoria real levou
   51 minutos, 113 chamadas e mais de 200 arquivos de evidência recapturando telas por conta própria.
   **Modo opcional, auditoria profunda:** uma lente por subagente (com a tool `Workflow`, uma
   chamada `parallel`; com `Agent`/`Task`, um por lente) só quando a pessoa pedir auditoria
   profunda, com essas palavras ou equivalentes. Nunca por padrão.
4. **Quando não permite** (sem subagente, pedido de agente único): a MESMA checagem roda em
   sequência, uma lente por vez, para achar e corrigir defeito. Ela é autoavaliação, e **nota de
   autoavaliação não libera entrega**: o registro leva `--origem autoavaliacao` e o `wave.py rodada` responde
   AUDITORIA INDEPENDENTE PENDENTE até a rodada independente acontecer em outra sessão, sem o
   histórico (`--origem sessao-independente`), ou com outra pessoa (`--origem pessoa`). Custo
   medido de confiar na autoavaliação (02/10/2026): média 7,78 e "tells 0" contra 5,5 e cinco
   achados graves do auditor independente, na mesma página.
5. Cada lente devolvida se registra:
   `node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> registrar <lente> --veredito <aprovado|reprovado> --nota <0-10> --origem <subagente|sessao-independente|pessoa|autoavaliacao> --achados "<o que olhou, o que mediu, o que achou>"`
6. Master: `node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> checar` (todas as lentes e
   todos os gates registrados).
7. Ciclo: `node <dir-da-skill>/scripts/py.mjs wave.py --projeto <dir> rodada --criticos <N> --altos <N> --pendencias-do-usuario <N> --regressoes <N>`.
   Saiu CONTINUA (rodada 1): corrija, refaça os gates que a correção toca, junte o pacote de novo
   (a página mudou, os prints antigos ficam velhos), salve os achados da rodada 1 em
   `auditoria/achados-rodada-1.json` e feche a rodada de conferência (a seção sobre a segunda rodada, abaixo).

## Schema de retorno (toda lente)

```json
{
  "lente": "string",
  "aprovado": true,
  "score": 8.5,
  "achados": [
    { "item": "string", "severidade": "critico|alto|medio|baixo", "evidencia": "string", "fix": "string" }
  ]
}
```

- **Evidência é obrigatória e verificável:** print, medida (px, contraste, alvo de toque),
  trecho de código com linha ou passo de reprodução. Achado sem evidência é descartado.
- **Fix nunca viola a regra da skill:** proibido sugerir depoimento inventado, urgência falsa,
  dado fora do briefing ou um tell de `references/anti-vibe-coding.md` como melhoria.
- **Crítico** quebra uso, mente para o visitante ou expõe o cliente. **Alto** que só some com
  dado que apenas o cliente tem (número do WhatsApp, foto do espaço, credencial) entra em
  `--pendencias-do-usuario` e vai declarado na entrega.

## A régua do ciclo (`wave.py rodada`)

1. Zero crítico confirmado. Inegociável.
2. Nenhuma regressão (achado causado pela correção da rodada anterior).
3. A lente `comparacao-referencias` reprovada na rodada 1 mantém o ciclo aberto (CONTINUA); na última rodada ela vira
   ressalva listada na entrega, depois de crítico e regressão. Reprovar essa lente NÃO manda reconstruir sozinha (o teto é 2 rodadas e a segunda é só conferência): o
   `wave.py rodada` lista os eixos abaixo das referências e manda corrigir esses eixos na página, entre as rodadas.
   Refazer o plano visual e reconstruir é um ciclo novo, só se a pessoa pedir.
4. Auditoria independente: nota de autoavaliação não libera (AUDITORIA INDEPENDENTE PENDENTE).
5. Depois disso, fecha quando a gravidade secou (zero crítico e zero alto), ou a média chegou a
   8,0 com nenhuma lente abaixo de 7, ou **bateu o teto de 2 rodadas**.

**Teto de 2 rodadas, e depois dele o ciclo fecha SEMPRE.** A segunda rodada termina em uma de
três saídas: aprovado; **ENTREGA COM RESSALVAS**, que lista os achados que sobraram e a nota
real, e as duas vão escritas na entrega; ou **NÃO ENTREGAR: crítico aberto** (ou regressão
aberta). O teto fecha o ciclo e não afrouxa nada: crítico aberto, regressão, conteúdo falso
(o `content-auditor` reprovado por dado inventado é crítico) e auditoria independente pendente
continuam barrando a entrega na segunda rodada, e nunca viram ressalva. **Ordem na última rodada (A30):** 1) crítico ou
regressão aberta = NÃO ENTREGAR; 2) senão, ENTREGA COM RESSALVAS, que lista o que sobrou, inclusive a lente
`comparacao-referencias` reprovada com os eixos abaixo. "Voltar ao plano visual" nunca aparece como ordem: é ciclo novo, só se a pessoa pedir.
O `wave.py rodada` nunca pede terceira rodada sozinho e recusa a terceira chamada. Uma terceira
só acontece se a PESSOA pedir, com `rodada --rodada-extra-pedida ...`; o pedido fica registrado no
histórico, a terceira também fecha sempre e não existe quarta. A nota real vai escrita na entrega, sempre.

Compare ACHADOS entre rodadas, nunca notas: cada rodada é um olhar novo e a nota não é medida
calibrada. Nota que cai pode ser régua mais fina, não página pior.

## Rodada 2: conferência, não auditoria nova

A rodada 2 existe para confirmar a correção, e o auditor é o mesmo da rodada 1 (a mesma
instância, quando o ambiente deixa continuar a conversa com ele, ou um novo recebendo a lista).
Ele recebe o pacote refeito (prints e pranchas capturados DEPOIS da correção; o
`pacote-auditoria.py --rodada 2` confere) e a lista de achados da rodada 1, e confere três
coisas, e mais nada:

1. cada achado foi corrigido, com evidência;
2. a correção não quebrou outra coisa (regressão), olhando só o que a correção tocou;
3. mais nada. Ele não reabre as 9 lentes do zero, não procura achado novo fora do que a
   correção tocou e não troca a régua. Defeito grave que apareça no caminho entra como
   `regressão` ou `não corrigido`, nunca como lista nova.

Schema de retorno (um item por achado da rodada 1):

```json
{
  "rodada": 2,
  "achados": [
    { "achado": "string (o item da rodada 1, com a lente)", "estado": "corrigido|não corrigido|regressão", "evidencia": "string" }
  ]
}
```

- **corrigido:** a evidência mostra o que mudou (print do mesmo recorte, medida, trecho com linha).
- **não corrigido:** a evidência mostra que o defeito segue lá. Segue como achado aberto com a
  mesma severidade.
- **regressão:** a evidência mostra o que a correção quebrou. Conta em `--regressoes` e, se for
  crítico, em `--criticos`.

**Nota nova só onde houve achado corrigido ou regressão (A31).** O auditor da rodada 2 devolve nota nova SÓ das lentes que tiveram achado
corrigido ou regressão; as outras ficam com a nota da rodada 1 (o `wave.py rodada` mostra "nota da rodada 1 mantida" e que a média da
rodada 2 mistura notas novas e mantidas, nunca como se tudo tivesse sido medido de novo).

A sessão registra de novo só as lentes cujos achados mudaram de estado (`registrar`, mesma
`--origem subagente`), conta `--criticos`, `--altos` e `--regressoes` do que ficou aberto e fecha:
`wave.py rodada ...`. O ciclo para aí (ENTREGA COM RESSALVAS ou NÃO ENTREGAR).

## As 9 lentes

### 1. design-critic (cara de IA, gosto)
Lê a página inteira no print e em recortes 1:1. Conta os tells de
`references/anti-vibe-coding.md` (V1 a V17, o V16 é o "jornal de filetes" e o V17 o esqueleto repetido) e as proibições de
`references/preferencias-de-design.md`, item por item (inclusive itens paralelos em caixas
iguais, passos em grade, FAQ e fecho com movimento, legenda que explica o design). Aplica a autocrítica da `frontend-design`: alguma
parte do plano virou o padrão que sairia para qualquer página parecida? Os três visuais
padrão de IA (creme com serifa e terracota; quase preto com um acento ácido; "jornal de
filetes", com fios finos, itálico colorido repetido e grade de fundo) só valem se o briefing pediu.
**Reprova (crítico) se:** 3 ou mais tells presentes, footer sem identificação, ou botão que
não leva a lugar nenhum.

### 2. assets-auditor (imagem real)
A página não pode ser só texto, gradiente e ícone. Confere cada imagem: de onde veio, qual a
licença (está em `imagens/LICENCAS.md`?), se casa com o título ao lado, se o recorte na JANELA
(não no arquivo) mostra o que importa, se há legenda de imagem ilustrativa quando a foto não é
do cliente, colada na foto. Confere a tabela público -> foto -> por quê do plano visual
contra a foto aberta (idade, perfil, roupa), procura logo de terceiro num recorte ampliado 4x
e confirma que nenhum elemento gráfico atravessa rosto ou corpo de pessoa. Público de pessoas
pede gente na primeira tela (foto autorizada ou ilustração própria); cada desenho se lê sem o
texto ao lado (planta baixa de retângulos e "mesa" de retas não se leem).
**Reprova (crítico) se:** nenhuma imagem real, foto que contradiz o público, logo de terceiro
legível na cena, linha ou forma por cima de pessoa, imagem sem licença registrada, foto que sugere
ser do cliente (o espaço, a profissional) sem ser, ou logo indicado pelo cliente trocado por
invenção.

### 3. visual-auditor (hierarquia, grid, enquadramento)
Hierarquia tipográfica, coerência de paleta com o plano visual, espaçamento, grid de desktop,
ritmo entre seções. Imagem com `loading="lazy"` precisa ter carregado antes do julgamento
(role até ela e espere `complete && naturalWidth > 0`).
**Reprova (crítico) se:** hero só com texto centralizado quando o plano pedia imagem, cor ou
fonte fora do plano visual, crop que corta rosto ou objeto principal.

### 4. motion-auditor (movimento)
Entrada do hero em escada; cada item revelado quando ELE chega na tela (a v7 aprovada pelo dono
revela 24 elementos, um a um, em 0,8 s, com observador de limiar 0,18 e margem de -6%); mais os
momentos próprios ligados ao conteúdo (traço que desenha a marca, barras que crescem, vagas que
se preenchem, a assinatura que muda de estado); hover e microinteração no botão;
`prefers-reduced-motion` respeitado. A base é única: uma curva (`cubic-bezier(.2,.8,.2,1)`) e uma
escala de duração (0,25 a 2,0 s), com as receitas de `references/receitas-de-movimento.md`.
Movimento que nunca termina (fica em opacity 0 se o observer falhar) é crítico.
**Reprova (crítico) se:** conteúdo que pode ficar invisível, animação sem respeitar
reduced-motion. **Reprova (maior) se:** o MESMO fade aplicado em bloco a tudo (tudo entra junto,
ou tudo com a mesma animação sem ligação com o conteúdo, o sinal 2 do `anti-vibe-coding.md`) ou
se a página só tem fade e nenhum momento próprio. Quantidade de itens revelados não reprova;
repetição sem ligação com o conteúdo reprova.

### 5. responsive-auditor (12 telas)
Roda `scripts/gate-responsivo.mjs` e olha os prints do celular em recortes 1:1.
**Reprova (crítico) se:** rolagem lateral, botão principal fora da dobra, alvo de toque abaixo
de 44px, corpo abaixo de 14px, texto cortado.

### 6. cro-auditor (conversão)
Uma ação clara, repetida nos pontos certos, com o destino real; headline que diz para quem e o
que resolve; objeções respondidas na página; mensagem coerente com a origem do tráfego.
**Reprova (crítico) se:** botão sem destino, formulário que mostra sucesso sem enviar, ação
principal ambígua.

### 7. a11y-auditor (acessibilidade)
Foco visível, label, alt que descreve a foto de verdade (olhando a foto), ARIA, contraste
4.5:1 medido no pixel, zero emoji, link "pular para o conteúdo" funcionando.
**Reprova (crítico) se:** contraste abaixo de 4.5:1 em texto de corpo, imagem de conteúdo sem
alt, controle sem nome acessível.

### 8. content-auditor (verdade)
Diff de claims: toda afirmação da página (texto, foto, alt, JSON-LD, title, meta description,
og:description, comentário que afirma comportamento) contra o briefing, pela tabela
`evidencias/sustentacao.md` e pelo `gate-verdade.py`. Lê também o que a frase INSINUA: "você
chega, faz a avaliação e começa" afirma mesmo dia sem dizer "mesmo dia". Sweep de travessão (U+2014 e U+2013 = 0). Telefone e
WhatsApp dígito por dígito em todo `tel:` e `wa.me`.
**Reprova (crítico) se:** dado, depoimento, número, preço ou credencial que não está na fonte;
travessão; contato divergente.

### 9. comparacao-referencias (está no nível das referências?)
A lente que a v3 criou. Pega as 2 ou 3 referências mais fortes de `referencias/sintese.md` e
põe cada uma ao lado da página, na mesma escala:

```bash
node <dir-da-skill>/scripts/py.mjs lado-a-lado.py <dir>/referencias/<ref>-dobra.png <print-da-pagina-dobra.png> <dir>/referencias/comparativo-1.jpg --rotulos "Referência,Nossa página"
```

Olhe a imagem e responda por escrito, eixo por eixo (composição, tipografia, imagem, ritmo,
acabamento): **no nível** ou **abaixo**, com o porquê. Depois a pergunta que decide: **um
designer exigente colocaria esta página na mesma pasta das referências?**
Por fim, por escrito e registrada com `--gosto`: **isso é bonito ou só está correto?** (a régua
do dono depois de uma página com 9,05 nas lentes que ele chamou de FEIA; a v5 do estúdio ficou
em 7,0 como "correta, mas vazia"). Perguntas que ajudam a responder: há gente do público na
página? Alguém de fora diz o que cada desenho é sem ler o texto? Existe um momento que
surpreende? A ordem das seções é a de qualquer landing ou a das referências?
**Reprova se:** a resposta honesta é não, se dois ou mais eixos ficaram abaixo, ou se a página
é só correta (`--gosto correto`). Reprovada,
registre os eixos abaixo (`--eixos-abaixo composicao,tipografia,imagem,ritmo`, só os que ficaram abaixo): a correção é desses
eixos, na página, entre as rodadas, com o que faltou escrito nos achados. Voltar ao plano visual (passo c) e reconstruir é
um ciclo novo, que a pessoa decide ("refazer o plano e reconstruir custa mais que a rodada 2"). No caminho
CLONAR a referência é a página original. Esta lente não aceita "não aplicável".

## Passe de gosto (último ato antes da entrega)

Apontar o defeito não é remover o defeito. Depois do ciclo, passe a página inteira com
mandato de CORRIGIR: ícone genérico em caixinha, uniformidade excessiva (todo card igual, toda
seção centralizada), os tells de `references/anti-vibe-coding.md`. Prova: tells antes e
depois, e o depois tem que ser 0, mais a lista do que foi inspecionado.

## O desfecho do ciclo e a etapa 5 (A31)

O `wave.py rodada` grava o desfecho de cada rodada (`CONTINUA`, `NAO_ENTREGAR`, `ENTREGA`, `ENTREGA_COM_RESSALVAS`, `AUDITORIA_PENDENTE`) em
`.wave-auditoria.json`. O `gate-etapas.py registrar 5` lê o último: recusa registrar a entrega pronta quando terminou em NÃO ENTREGAR, em
CONTINUA ou com auditoria independente pendente; com ENTREGA COM RESSALVAS registra e grava as ressalvas na evidência da etapa.

Sem auditoria não há entrega registrada: o `gate-etapas.py registrar 5` também recusa quando não existe `.wave-auditoria.json`, quando o registro
não tem as 9 lentes, quando alguma lente é autoavaliação ou quando o ciclo não foi fechado, e a mensagem traz os comandos do passo g. O caminho
EDITAR (edição pontual) não passa por essas etapas e segue isento de auditoria completa, como diz a tabela de caminhos do `SKILL.md`.
