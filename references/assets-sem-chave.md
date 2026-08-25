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
python3 scripts/assets-search.py "team meeting office" --type openverse -n 6

# alias curto
python3 scripts/assets-search.py "brazil city aerial" --type cc -n 6

# e o mais importante: sem PEXELS_API_KEY, isto cai na Openverse sozinho
python3 scripts/assets-search.py "coworking space" --type photo -n 6
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
python3 scripts/assets-search.py --type illustrations "team work"
```

Cor customizável para casar com a paleta da página. Sem obrigação de crédito.
Boas para seção de features, estado vazio e passo a passo. Não substituem foto
real no hero: ilustração sozinha em página inteira ainda parece página vazia.

---

## 4. Backgrounds, patterns e gradientes

```
python3 scripts/assets-search.py --type backgrounds
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

## Licenca: o que a busca ja garante e o que continua sendo seu trabalho

A busca da Openverse filtra por **uso comercial E permissao de modificacao**. Isso importa
porque pagina de cliente SEMPRE corta, redimensiona e sobrepoe texto, o que cria obra derivada.
So filtrar por "uso comercial" deixava passar licenca **ND (NoDerivatives)**, que proibe
exatamente isso: o aluno colocaria a foto na pagina do cliente violando a licenca sem saber.

O que ainda depende de voce olhar, porque nenhum filtro resolve:

- **Marca e produto de terceiro.** A busca pode devolver foto que mostra logo, embalagem ou
  produto de outra empresa. A licenca da FOTO nao te da direito sobre a MARCA que aparece nela.
  Nunca use numa pagina que vende produto concorrente ou que sugira endosso.
- **Pessoa identificavel.** Licenca de foto nao e autorizacao de uso de imagem. Para peca
  publicitaria com rosto reconhecivel, use foto de banco com direito de modelo, ou foto do
  proprio cliente.
- **Credito obrigatorio.** CC BY e CC BY-SA exigem creditar autor, fonte e licenca. O credito
  ja sai pronto na saida da busca: cole no rodape da pagina, nao apague.

Regra pratica: se a foto tem marca visivel ou rosto em primeiro plano, troque. Foto de contexto
(ambiente, objeto, mao, textura) quase nunca tem esse problema.
