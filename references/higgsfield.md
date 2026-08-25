# Higgsfield: animação e b-roll na página

## SETUP (primeira vez, ~3 minutos)

Se a pessoa ainda não tem conta nem CLI, conduza por estes passos. Não pule nenhum,
e não presuma que já está feito: rode a verificação do passo 5 antes de gerar.

**1. Conta.** Criar em higgsfield.ai. **Plano pago é necessário para uso comercial**
(o gratuito não libera). Página de cliente é uso comercial.

**2. Instalar a CLI:**
```bash
npm i -g @higgsfield/cli
```

**3. Autenticar** (abre o navegador para a pessoa concluir o login):
```bash
higgsfield auth login
```

**4. Instalar as skills companheiras** (trazem geração de imagem, vídeo, áudio, 3D,
brandkit, thumbnail, e mais):
```bash
npx skills add higgsfield-ai/skills
```

**5. Selecionar o workspace.** PASSO QUE FALTA EM TODO TUTORIAL e trava tudo: sem
workspace selecionado, qualquer comando responde `Error: No workspace selected`.
```bash
higgsfield workspace list                 # anote o ID
higgsfield workspace set <workspace_id>
higgsfield account status                 # confirma: e-mail, plano e créditos
```
O `account status` é a verificação de que deu certo. Se ele imprime o plano e o
saldo, está pronto. Se erra, volte ao passo que falhou em vez de tentar gerar.

**Sem conta:** siga sem. Entregue os blocos estáticos, DECLARE a pendência na
entrega ("os blocos X e Y ficaram estáticos: exigem conta Higgsfield") e ofereça
as rotas que não pedem conta paga: animação em CSS/Framer Motion no próprio bloco,
ou a rota Replicate de `references/ai-video-generation.md`. Falta de conta degrada
o resultado, não bloqueia a entrega.

**Rota alternativa por chave de API** (sem CLI, para automação): ver a seção de
autenticação mais abaixo neste arquivo (`HF_API_KEY_ID` e `HF_API_KEY_SECRET`).

---


## Licoes de composicao com video (medidas em pagina real, 25/08/2026)

### O veu existe pra o texto ficar legivel, NAO pra esconder o video

Primeira versao de uma secao com video de fundo: video a `opacity:.5` e veu comecando em
cor SOLIDA no topo, indo a 86-92% no resto. Conta do que sobrava visivel: **entre 0% e 7%**.
O clipe estava la, custou credito, e ninguem via. O dono olhou e perguntou se o video tinha
sido gerado.

Faixa que funcionou: **video a 100%** e veu entre **72% e 48%** (mais forte atras do titulo,
mais fraco embaixo). Sempre CALCULE o que sobra antes de aceitar: `visivel = opacidade_video
x (1 - alpha_veu)`. Abaixo de 15% de visibilidade, o video e enfeite invisivel: ou aumenta,
ou tira e economiza o credito.

### Cartao branco opaco em cima de video = video escondido

Na mesma secao, 4 cartoes brancos cobriam justamente a area do clipe. Tirar os cartoes
resolveu o video mas QUEBROU o contraste: texto solto sobre o video media 2,92 a 3,97, abaixo
do minimo de 4,5, porque as partes escuras do clipe passam por tras da letra.

A saida foi COMPOSICAO, nao opacidade: texto virou coluna a esquerda, video virou janela a
direita, com veu lateral proprio. Area com movimento visivel subiu de 38,8% para 42,4% e o
contraste passou em 11 de 11 elementos. Quando texto e video brigam, separe-os no espaco em
vez de apagar um dos dois.

### Como MEDIR contraste sobre video (nao da pra usar a cor de fundo do CSS)

Sobre video nao existe "cor de fundo": cada quadro tem uma. Metodo que funciona:
1. esconder o glifo do texto e fotografar o retangulo EXATO onde ele fica
2. usar o **percentil 5** dos pixels do fundo como pior caso, nao a media
3. repetir em **3 instantes distintos** do clipe (o quadro mais escuro e o que reprova)

Duas armadilhas que deram resultado falso e custaram tempo:
- `Math.min` iniciado em 1 devolve 1,00 sempre (o minimo nunca sobe). Inicie em `Infinity`.
- fazer `seek` sem esperar o evento `seeked` devolve o MESMO quadro tres vezes, e a medicao
  parece consistente quando na verdade nem rodou.

### Modelo de video sem parametro `seed`

A regra 3 (seed sempre anotado) nao se aplica a todo modelo: o `seedance_2_0` nao aceita
`seed`. Nesses casos, anote o **ID do job** da geracao, que recupera exatamente o mesmo clipe.
Confira com `higgsfield model get <job_type>` quais parametros o modelo aceita ANTES de montar
o comando, em vez de presumir.

---

## 1. A ordem de preferência não mudou, e ela existe por um motivo

```
1. Material REAL (GalerIA / Drive / gravação de tela)   ← sempre primeiro
2. Gravação de tela nova                                 ← software, dashboard, produto
3. Higgsfield                                            ← só quando 1 e 2 não existem
```

Para produto de software isto não é preciosismo. Numa página de venda o
espectador reconhece tela de verdade, e reconhece cena genérica de IA também.
Vídeo bonito que não é do produto é enfeite caro: ocupa a maior banda da página
e não prova nada.

**Higgsfield é bom em**: ambiente abstrato, textura, luz, movimento de câmera
sobre cena inventada, produto que não existe fisicamente ainda.
**Higgsfield é ruim em**: mostrar a SUA interface, o SEU dashboard, o SEU
resultado. Nada disso ele sabe.

---

## 2. As cinco regras que vêm de defeito medido, não de gosto

Todas nasceram de defeitos medidos em projetos reais. Cada uma custou uma
rodada de retrabalho.

### 2.1 Uma trilha, UMA proporção. Decidida ANTES de gerar.

A fila de herói de uma página de lançamento acumulou 11 clipes com **5 proporções diferentes**
(1.598, 1.610, 1.696, 1.798 e 1.863, medidas com ffprobe). Não existe caixa fixa
que sirva pras cinco: com a caixa em 1.798, o clipe de 1.863 perdia 3,5% na
horizontal e os de 1.598 perdiam 11% na vertical. O resultado no celular foi
diagrama cortado no meio e ilegível.

`aspect_ratio` é **parâmetro da API**. Isso é evitável na origem:

> Antes de gerar o primeiro clipe de uma trilha, escreva a proporção dela.
> Todo clipe daquela trilha nasce com a mesma. Se um clipe de fora entrar depois,
> ele é reencodado pra essa proporção, não a caixa que se adapta a ele.

Quando a mistura for inevitável (assets legados), a saída é `object-fit: contain`
com a chapa na cor do campo, e não `cover`. `contain` nunca corta.

### 2.2 Gerar no TAMANHO DA CAIXA, não maior

`resolution` também é parâmetro. Um projeto real tinha clipes de 1280x712 pintados em
390x217 no celular: 3,3x de desperdício, baixado inteiro, para ser jogado fora
na decodificação.

> Meça a caixa em CSS px na maior largura em que ela aparece, multiplique por 2
> (DPR de retina) e gere nesse tamanho. Nunca acima.

Caixa de 390x217 no celular e 969x722 no desktop → gere 1080p e sirva um só.
Caixa de 340px de card → 720 já sobra.

### 2.3 `seed` sempre anotado

`seed` é parâmetro (1 a 1.000.000). Sem ele, regenerar "o mesmo clipe" devolve
outro clipe, e a página muda sem ninguém ter pedido.

> Anote o seed junto do prompt no comentário do código, ao lado do nome do
> arquivo. Regeneração sem o seed original é asset novo, não a mesma coisa.

### 2.4 Nome de arquivo com hash de CONTEÚDO, e pôster com hash PRÓPRIO

O edge do Cloudflare cacheia por caminho: arquivo com nome igual e bytes novos
continua servindo o velho.

E o erro caro: o pôster era derivado do nome do mp4 (`${arq}.webp`). Reencodar
os vídeos trocou o hash e **os seis pôsteres foram pra 404**, deixando a seção
com seis lajes pretas, pior justamente pra quem usa movimento reduzido e só vê o
pôster.

> Dois arquivos, dois campos, dois hashes. `arq` e `poster` separados no código.

### 2.5 O vídeo do herói É o elemento de LCP

Medido no ar com 1,6Mbps / 150ms / CPU 4x: o LCP de uma página real foi o `<video>` da
abertura, e o que pinta nele antes de qualquer byte de mp4 é o **pôster**.

> Todo herói com vídeo leva `<link rel="preload" as="image" fetchPriority="high">`
> no pôster. Sem isso o pôster entra na fila depois das fontes e do CSS: medido,
> o LCP do celular saiu de 2660ms (acima do piso de 2500) para 2252ms só com essa
> linha.

E o mp4 nunca com `autoplay` no markup: `preload="none"`, `src` atribuído por
IntersectionObserver quando chega perto.

---

## 3. A API

Base: `https://platform.higgsfield.ai`

**Autenticação** (confirmada em docs.higgsfield.ai/docs/authentication, 22/08/2026).
Não é bearer: é chave mais secret no mesmo header.

```bash
# formato novo, recomendado
curl https://platform.higgsfield.ai/requests/REQUEST_ID/status \
  --header "Authorization: Key ${HF_API_KEY_ID}:${HF_API_KEY_SECRET}"

# formato legado, ainda aceito
#   hf-api-key: ${HF_API_KEY_ID}
#   hf-secret:  ${HF_API_KEY_SECRET}
```

A credencial se cria em **cloud.higgsfield.ai**, e cada uma é um par
(key ID + secret). Server-side sempre: o secret não pode ir pro navegador.

Assíncrona: submete, recebe `request_id`, faz polling ou recebe webhook.

```
GET /requests/{request_id}/status
```

### Endpoints de vídeo (os que interessam pra página)

| Uso | Endpoint |
|---|---|
| texto → vídeo, qualidade | `/veo3.1` |
| texto → vídeo, barato/rápido | `/veo3.1/fast` |
| texto → vídeo, alternativa | `/kling-video/v2.5-turbo/pro/text-to-video` |
| imagem → vídeo (animar um still) | `/veo3.1/image-to-video` |
| imagem → vídeo, barato | `/bytedance/seedance/v1/lite/image-to-video` |

Também existem `minimax/hailuo-02/pro`, `higgsfield-ai/dop`,
`higgsfield-ai/soul` (personagem, é o de UGC), `higgsfield-ai/popcorn/auto` e
`flux-pro/kontext/max`.

### Corpo da requisição

| Campo | Observação pra página |
|---|---|
| `prompt` | obrigatório, ver a seção 4 |
| `aspect_ratio` | 16:9, 9:16, 4:3, 3:4, 1:1, 2:3, 3:2. **Decidido pela trilha, regra 2.1** |
| `resolution` | 480 / 720 / 1080 (2K e 4K em alguns). **Tamanho da caixa × 2, regra 2.2** |
| `duration` | 4 a 12s conforme o endpoint. Para loop de fundo, o mais curto que fecha |
| `seed` | 1 a 1.000.000. **Sempre anotar, regra 2.3** |
| `image_url` | para image-to-video |
| `end_image_url` | primeiro/último quadro, útil pra fechar loop |
| `negative_prompt` | ver a seção 4 |
| `cfg_scale` | 0 a 1 |

**`image-to-video` é quase sempre a escolha certa em página.** Você já tem o
still da marca, o print do produto, a foto do expert. Animar o que já existe
mantém a identidade; text-to-video inventa uma cena que não é da marca.

Existe também um CLI em `higgsfield.ai/cli`, feito pra agente. Preferir a API
quando for script; o CLI serve pra exploração manual.

---

## 4. Prompt: direcionado, nunca genérico

A regra de ouro aqui é **bem direcionado**. Prompt escrito a partir do
conteúdo daquela seção e da direção da página, nunca genérico, senão sai peça
bonita que não tem nada a ver e vira retrabalho.

Estrutura que funciona pra fundo de página:

```
[Sujeito/textura]. [Movimento, lento e contínuo]. [Luz e paleta, com as cores
da marca]. [Câmera: quase parada, sem corte]. [Nada de texto na imagem].
```

Fundo de herói:
```
Abstract dark warm surface, slow drifting light, deep charcoal with amber
accents, extremely slow camera push, continuous single shot, no cuts, no text,
no people, cinematic, subtle grain
negative: text, letters, watermark, logo, fast motion, cuts, faces
```

Textura de seção:
```
Macro texture of [material], soft directional light moving slowly across the
surface, [cor da marca] tones, single continuous shot, no text
negative: text, watermark, hands, people, jump cut
```

Animar um still que já existe (image-to-video):
```
Subtle parallax on the existing composition. Only light and depth move.
Do not change layout, colors or add elements.
negative: new objects, text, distortion, morphing
```

### Negativos universais pra página

`text, letters, typography, watermark, logo, subtitles, fast motion, hard cuts,
flashing, morphing, distorted faces, extra limbs`

Texto gerado por IA dentro do vídeo é o carimbo mais rápido de "isso é IA", e
numa página de venda ele aparece atrás da sua tipografia real, brigando com ela.

---

## 5. Onde entra no fluxo do construtor

Higgsfield entra na **etapa de assets**, depois do wireframe e antes do gate de
qualidade. Nunca antes de existir seção definida: gerar vídeo pra depois achar
onde encaixa é o caminho do enfeite.

```
wireframe (Stitch) → componentes (21st.dev) → código
   → ASSETS: 1) material real  2) gravação de tela  3) Higgsfield
      └─ proporção da trilha decidida
      └─ tamanho da caixa medido
      └─ PROPOSTA: o que seria gerado, em qual seção, com qual prompt
      └─ PARAR. Só gera com o ok do responsável pela página.
   → gate de qualidade (inclui os gates de vídeo abaixo)
```

**Proposta antes de gerar** é boa prática em qualquer geração paga: entra no
plano como descrição do que seria gerado, e só roda depois do ok. Crédito é
dinheiro real, seu ou do cliente.

**Máximo 1 retry, cache primeiro.** O Higgsfield tem histórico de bloqueio.
Guardar o `request_id` e o resultado localmente antes de qualquer segunda
tentativa.

---

## 6. Gates de vídeo, pra rodar antes de entregar

Adicionar ao gate de qualidade da skill. Todos vieram de defeito real:

- [ ] **Proporção**: todos os clipes da mesma trilha têm a mesma razão?
      (`ffprobe -v error -select_streams v:0 -show_entries stream=width,height`)
- [ ] **Escala**: `naturalWidth` do vídeo contra a caixa medida. Acima de 1,3x
      é desperdício de banda; abaixo de 0,8x é imagem borrada.
- [ ] **Corte**: com a caixa e a razão reais, quanto do quadro o `cover` está
      comendo? Acima de 15% em qualquer eixo, o conteúdo do clipe está sendo
      decidido pelo CSS e não pelo encoder.
- [ ] **Pôster**: existe, tem hash próprio (não derivado do mp4) e responde 200?
- [ ] **Conteúdo do quadro**: extrair 6 frames com ffmpeg e OLHAR. Texto cortado
      na borda, nome de cliente, credencial, ID interno, valor. Já apareceu um clipe
      com texto de terminal saindo do quadro **no próprio arquivo**, e isso
      só apareceu extraindo o frame.
- [ ] **LCP**: se o vídeo está acima da dobra, o pôster tem `preload` com
      `fetchPriority="high"`?
- [ ] **Movimento reduzido**: com `prefers-reduced-motion: reduce`, sobra só o
      pôster?

---

## 7. Crédito morre no fim do ciclo

Os créditos de qualquer plano pago **expiram no fim de cada ciclo de
cobrança, sem rollover**. Pacote avulso de top-up expira em 90 dias.

Isso não é detalhe de faturamento, é o modelo de operação:

> Gerar de um em um, conforme a necessidade aparece, desperdiça saldo que morre.
> O certo é **leva planejada por ciclo**: a página inteira tem os assets decididos
> juntos, gerados juntos, e o que sobrar de crédito no mês é prejuízo.

Consequência prática pro fluxo: quando entrar numa página, levantar TODOS os
lugares que pedem movimento antes de gerar o primeiro. Uma proposta só, com a
lista inteira, e o custo somado em créditos.

Planos (agosto/2026, fonte secundária, confirmar no painel): Starter US$19 por
270 créditos, Plus US$59 por 1.200, Ultra US$129 por 3.000.

## 8. Uso comercial: liberado, e sem marca d'água

**Qualquer plano pago libera uso comercial** (anúncio pago, página de venda,
trabalho de cliente) e remove a marca d'água. O plano gratuito não: ele carimba
tudo e não dá direito comercial.

Antes de gerar qualquer asset pra um cliente, confirme que a conta usada é de
um plano pago, não do gratuito.

## 9. DoP: o preset é a razão de existir

O que separa o Higgsfield de gerar vídeo em qualquer outro lugar é o **DoP**
(Director of Photography): um modelo de image-to-video treinado em MOVIMENTO DE
CÂMERA, com mais de 100 presets. Ele parte de um keyframe seu e aplica um
movimento dirigido, em vez de reinventar a cena.

Três práticas que a documentação e os testes de terceiros convergem em recomendar:

1. **Um movimento por clipe.** Dois presets no mesmo clipe brigam e o resultado
   vira tremor.
2. **Escolher o preset E repetir o movimento no texto do prompt** (por exemplo,
   selecionar "crash zoom in" e escrever "crash zoom in" no prompt). Fazer os dois
   é o que dá resultado repetível.
3. Em image-to-video, acrescentar **"preserve the original face, lighting and
   geometry"**. É isso que faz a câmera se mover sem o modelo redesenhar a cena,
   e é o que mantém a identidade da marca no quadro.

### Quais presets servem pra página, e quais não

Página de venda pede movimento que não chame atenção pra si. O catálogo do DoP é
de cinema, então a maioria dos presets famosos dele é justamente o que NÃO serve.

**Servem** (contínuos, lentos, sem evento):
- push in / push out muito lento
- orbit lento e parcial
- drift lateral
- parallax sutil sobre still

**Não servem em fundo de seção** (têm um "momento", e o momento compete com o
texto que a pessoa está lendo):
- crash zoom, dolly zoom (efeito Vertigo), bullet time
- 360 orbit completo
- whip pan, snap zoom
- qualquer coisa com corte

Regra curta: se o preset tem um clímax, ele é pra anúncio, não pra fundo de
página. Em anúncio o clímax é o ponto; atrás de uma headline ele rouba a leitura.

## 10. Antes do primeiro uso

Checklist de onboarding pra quem nunca usou o Higgsfield:

1. Criar conta em `cloud.higgsfield.ai`.
2. Escolher um plano pago (o gratuito não libera uso comercial, ver seção 8).
3. Gerar o par de credenciais (key ID + secret) no painel da conta.
4. Exportar `HF_API_KEY_ID` e `HF_API_KEY_SECRET` no ambiente, nunca commitar.
5. Confirmar no próprio painel o saldo de créditos do ciclo (ver seção 7) antes
   de planejar a leva de assets da página.

Se não quiser criar conta própria, use a rota via Replicate documentada em
`references/ai-video-generation.md`.
