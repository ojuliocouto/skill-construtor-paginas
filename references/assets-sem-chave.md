# Assets sem chave de API

Nenhuma página pode sair com retângulo cinza vazio no lugar da foto. Este
documento é a rota de fuga quando não existe `PEXELS_API_KEY` configurada.

A regra que vale acima de tudo: **página só com texto, gradiente e SVG genérico
reprova na auditoria visual da skill**. Foto real, mockup ou ilustração temática
não são enfeite, são requisito de aprovação.

---

## 1. Openverse: a melhor rota sem chave

Fotos reais indexadas pela Openverse (mantida pela WordPress Foundation), todas
com licença Creative Commons. Responde sem nenhuma API key.

```bash
# busca direta
node scripts/py.mjs assets-search.py "team meeting office" --type openverse -n 6

# alias curto
node scripts/py.mjs assets-search.py "brazil city aerial" --type cc -n 6

# e o mais importante: sem PEXELS_API_KEY, isto cai na Openverse sozinho
node scripts/py.mjs assets-search.py "coworking space" --type photo -n 6
```

O script já filtra por `license_type=commercial`, ou seja, só volta o que pode
ser usado em página de cliente. Cada resultado sai com:

- URL direta da imagem (JPEG ou PNG real, pronto para baixar)
- autor e link do perfil do autor
- rótulo da licença (exemplo: `CC BY 2.0`)
- link da licença
- página de origem
- o crédito já montado e um bloco `<figure>` pronto para colar

Busque em inglês e com termos concretos. `team meeting office` traz resultado
bom; `inovação disruptiva` não traz nada.

### Segunda rota: Wikimedia Commons (quando a Openverse não responde)

A Openverse às vezes não responde (rede da escola ou do escritório, proxy, a própria API fora do ar:
`Connection reset by peer`). O script não para: na mesma busca `--type photo` (ou `--type openverse`) ele
tenta a **Wikimedia Commons**, que também dispensa chave, e diz qual rota respondeu:

```text
Rota que respondeu: Wikimedia Commons (a Openverse não respondeu (...))
```

```bash
# a mesma busca; a rota é escolhida sozinha
node scripts/py.mjs assets-search.py "woodworking workshop" --type photo -n 6
# pedir a Commons direto
node scripts/py.mjs assets-search.py "woodworking workshop" --type commons -n 6
```

- **Mesma saída e mesmos campos de licença:** URL da imagem (1280 px), miniatura de 500 px, autor com link,
  rótulo e link da licença, página de origem, crédito pronto e `<figure>` para colar.
- **Só existem estas larguras de miniatura: 500, 960, 1280 e 1920 px.** Outra largura (480, 1500) devolve
  `HTTP Error 400: Use thumbnail sizes listed...`. Para a versão do herói, troque `1280px-` por `1920px-` na URL
  (o script já imprime a linha `Versão 1920 px` quando a foto tem essa largura; foto mais estreita que a pedida também dá 400).
- **Só entra licença que uma página de cliente pode usar:** CC0, CC BY, CC BY-SA e domínio público. NC, ND,
  GFDL e "uso livre" de cada país são descartadas. Crédito segue obrigatório em CC BY e CC BY-SA.
- **Pausa e limite:** o script espera 1 s antes de chamar e, em HTTP 429 (limite da Commons), espera o
  `Retry-After` (no máximo 30 s) e tenta **uma** vez. Se ainda der 429, devolve vazio e diz para esperar um
  minuto: insistir só alonga o bloqueio.
- **Busque por AUTOR ou por CATEGORIA, não só por palavra.** Palavra solta de móvel ou ofício traz sala de
  museu, casa de boneca, reboque de cavalo e prova policial (prefixo `EFTA`); no teste, o que serviu veio de
  UM autor, achado por acaso e buscado pelo nome. O script já descarta esses quatro tipos de acervo e conta quantos
  tirou (`--sem-filtro` mostra tudo). Estreite com `--autor` e `--categoria` (só em `--type commons`):
  ```bash
  node scripts/py.mjs assets-search.py "woodworking" --type commons --autor "Shixart1985" -n 8
  node scripts/py.mjs assets-search.py "table" --type commons --categoria "Wooden furniture" -n 8
  ```
  Achou um bom autor numa foto? Busque o nome dele de novo: o acervo de um autor costuma ser coerente.
  Cada item traz a miniatura de 500 px, então dá para escolher sem abrir um título por vez.
  Acervo fraco para "móvel de autor": cena de casa com o tipo de móvel entra como ponte, dita na legenda.
- **O acervo é diferente:** a Commons tem muita foto de ofício, lugar e objeto, e pouca de gente "natural,
  30 a 55 anos". Para rosto de depoimento, a foto do cliente continua sendo o caminho.
- A suíte testa essa rota com a resposta gravada (`scripts/fixtures/commons-resposta.json`), sem internet.

### O script já descarta link morto

A Openverse indexa acervos de terceiros (Flickr, StockSnap). Foto apagada na
origem continua no índice e devolve 410. Antes de listar, o script confere cada
URL e descarta a que não entrega imagem, avisando quantas caíram. Link morto na
página é o mesmo defeito que não ter imagem nenhuma.

Mesmo assim, confira o arquivo depois de baixar: `file` tem que dizer JPEG ou
PNG, nunca "HTML document".

### Baixar e hospedar, nunca fazer hotlink

Link de terceiro sai do ar, muda de endereço e derruba a imagem da página do
cliente. Baixe sempre:

```bash
# o -A não é firula: CDN como o do StockSnap devolve 403 para o curl sem User-Agent,
# e você acaba salvando uma página de erro em HTML com extensão .jpg
curl -L -A "Mozilla/5.0" -o public/img/hero.jpg "https://live.staticflickr.com/.../foto_b.jpg"
file public/img/hero.jpg   # tem que dizer JPEG/PNG com dimensão útil, nunca "HTML document"
```

Depois converta para WebP. Alvo: hero abaixo de 200KB, seções abaixo de 100KB.

---

## 2. Picsum: JPEG real para mockup e placeholder

Não é foto temática, é foto genérica. Serve para preencher mockup, card de
depoimento em rascunho e placeholder de galeria enquanto o cliente não manda o
material dele.

```
https://picsum.photos/1600/900             # aleatória a cada carregamento
https://picsum.photos/seed/hero/1600/900   # estável: mesma seed, mesma foto
https://picsum.photos/1600/900?grayscale&blur=2
```

Use sempre com `seed` em página que vai ao ar, senão a imagem troca a cada
recarregamento e o layout fica instável. E nunca apresente foto do Picsum como
se fosse foto do cliente ou do produto dele.

---

## 3. unDraw: ilustrações SVG temáticas

```
https://undraw.co/illustrations
node scripts/py.mjs assets-search.py --type illustrations "team work"
```

Cor customizável para casar com a paleta da página. Sem obrigação de crédito.
Boas para seção de features, estado vazio e passo a passo. Não substituem foto
real no hero: ilustração sozinha em página inteira ainda parece página vazia.

---

## 4. Backgrounds, patterns e gradientes

```
node scripts/py.mjs assets-search.py --type backgrounds
```

São camada de fundo, não são a imagem da página. Se a única coisa visual da
página for gradiente com pattern SVG, a auditoria reprova.

---

## Como creditar direito (a atribuição não é opcional)

Em `CC BY` e `CC BY-SA`, creditar o autor é **condição da licença**, não
cortesia. Publicar sem o crédito deixa o uso irregular, e quem responde é o
dono da página, não quem baixou a foto.

O padrão internacional é o TASL: Título, Autor, Source (origem) e Licença.

### Modelo pronto na legenda da imagem

```html
<figure>
  <img src="/img/hero.jpg" alt="Reunião de time em escritório" loading="lazy" />
  <figcaption class="text-xs opacity-60 mt-1">
    "Liip team meeting" por
    <a href="https://www.flickr.com/photos/21458229@N00" rel="nofollow">lejoe</a>,
    licença <a href="https://creativecommons.org/licenses/by/2.0/" rel="license">CC BY 2.0</a>
  </figcaption>
</figure>
```

### Modelo pronto na seção de créditos do rodapé

Quando a legenda visível atrapalha o design (hero de tela cheia, por exemplo),
junte tudo numa seção "Créditos de imagem" no rodapé, com um item por foto:

```html
<section id="creditos" class="text-xs opacity-60">
  <h2>Créditos de imagem</h2>
  <ul>
    <li>
      Hero: "Liip team meeting" por
      <a href="https://www.flickr.com/photos/21458229@N00">lejoe</a>,
      <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a>
    </li>
  </ul>
</section>
```

**Link de crédito com alvo de toque de 44 px (padrão medido).** O `gate-responsivo.mjs` reprova alvo de toque menor
que 44 px, e link dentro de frase tem uns 18 px de altura. Duas saídas que parecem boas e NÃO servem: `inline-flex` e
`line-height: 44px` abrem buracos de 44 px entre as linhas do texto (visto no print). O que funciona: linha de 22 px e
link em bloco em linha com 11 px de folga que a margem negativa devolve.

```css
.creditos li { font-size: 14px; line-height: 22px; }
.creditos a { display: inline-block; padding: 11px; margin: -11px; }   /* 22 + 11 + 11 = 44 px de alvo, 0 px de buraco */
```

Medido em 390 e 360 px de largura: cada link com 44 px de altura, as linhas do texto na mesma distância de antes (22 px)
e nenhum buraco entre elas. Link muito curto (duas letras) precisa de `min-width: 44px`. Abaixo de 14 px o gate reprova o texto de corpo; se a fonte for maior que 14 px,
mantenha `line-height` = 44 menos duas vezes o `padding`.

O crédito precisa estar visível na mesma página onde a imagem aparece. Crédito
escondido em `alt`, em comentário de HTML ou em outra página não cumpre a
licença.

### O que cada licença exige

| Licença | Creditar | Uso comercial | Detalhe que pega |
|---|---|---|---|
| CC0 / Public Domain Mark | não exige (mas credite) | sim | rota mais tranquila |
| CC BY | obrigatório | sim | crédito visível na página |
| CC BY-SA | obrigatório | sim | obra derivada herda a mesma licença |
| CC BY-ND | obrigatório | sim | não pode recortar nem alterar a imagem |
| CC BY-NC (e NC-SA, NC-ND) | obrigatório | **não** | fora de página de cliente |
| Licença Pexels | não exige | sim | precisa de `PEXELS_API_KEY` |

Se você alterou a imagem (recorte, filtro, sobreposição de texto), diga isso no
crédito: "imagem recortada a partir do original". Em `ND` nem recorte é
permitido.

---

## O que NÃO fazer

- **Nunca** usar imagem de licença desconhecida em página de cliente. Se você
  não consegue apontar o link da licença, a imagem não entra. Salvar resultado
  de busca de imagem do Google é o caminho mais curto para uma notificação de
  direito autoral.
- Nunca remover o crédito porque "ficou feio". Se não cabe na legenda, vai para
  a seção de créditos do rodapé. Sumir com o crédito não é opção de design.
- Nunca usar foto de banco genérico com pessoa sorrindo apertando a mão como
  prova social. Prova social é print real, número real, rosto real do cliente.
- Nunca fazer hotlink da URL de terceiro (Flickr, Wikimedia) direto no `src` de
  produção.
- Nunca usar imagem `CC BY-NC` em página que vende alguma coisa. `NC` significa
  não comercial, e página de venda é uso comercial.
- Nunca deixar o hero com "Espaço reservado para as fotos reais". Coloque a
  foto da Openverse ou um mockup do Picsum e siga em frente. Placeholder de
  texto é exatamente o defeito que a auditoria reprova.
- Nunca subir a imagem sem otimizar. JPEG de 4MB no hero destrói o LCP.

---

## Checklist antes de publicar sem chave

1. A página tem pelo menos uma imagem real (`<img>` ou `<video>`), não só SVG.
2. Toda imagem foi baixada e está hospedada no próprio projeto.
3. Toda imagem CC tem crédito visível com autor e link da licença.
4. Nenhuma imagem é `NC` em página comercial.
5. Rodou `file` em cada arquivo e confirmou formato e dimensão úteis.
6. Hero abaixo de 200KB, demais imagens abaixo de 100KB, de preferência WebP.

## Licença: o que a busca já garante e o que continua sendo seu trabalho

A busca da Openverse filtra por **uso comercial E permissão de modificação**. Isso importa
porque página de cliente SEMPRE corta, redimensiona e sobrepõe texto, o que cria obra derivada.
Só filtrar por "uso comercial" deixava passar licença **ND (NoDerivatives)**, que proíbe
exatamente isso: o aluno colocaria a foto na página do cliente violando a licença sem saber.

O que ainda depende de você olhar, porque nenhum filtro resolve:

- **Marca e produto de terceiro.** A busca pode devolver foto que mostra logo, embalagem ou
  produto de outra empresa. A licença da FOTO não te da direito sobre a MARCA que aparece nela.
  Nunca use numa página que vende produto concorrente ou que sugira endosso.
- **Pessoa identificável.** Licença de foto não é autorização de uso de imagem. Para peça
  publicitária com rosto reconhecível, use foto de banco com direito de modelo, ou foto do
  próprio cliente.
- **Crédito obrigatório.** CC BY e CC BY-SA exigem creditar autor, fonte e licença. O crédito
  já sai pronto na saída da busca: cole no rodapé da página, não apague.

Regra prática: se a foto tem marca visível ou rosto em primeiro plano, troque. Foto de contexto
(ambiente, objeto, mão, textura) quase nunca tem esse problema.
