# Pesquisa de referências reais (passo b do CRIAR)

A direção visual nasce de página de verdade, aberta e printada, nunca de memória nem de
banco de CSV. O motivo é medido: a página do teste com aluno (02/10/2026) passou em todos os
gates e saiu com cara de rascunho, porque ninguém olhou o que os melhores do ramo fazem.

## O que procurar: 6 a 10 páginas, de dois tipos

| Tipo no manifesto | O que é | Quantas |
|---|---|---|
| `mesmo-negocio` | página real, no ar, de um negócio do mesmo tipo (outro estúdio de pilates, outra clínica, outro escritório). Brasil e fora | pelo menos 2 |
| `design` | página de alto nível de outro ramo cujo PROBLEMA visual é parecido (serviço de saúde, marca de bem-estar, estúdio pequeno com uma ação só) | pelo menos 2 |

Total mínimo: 6. Mais de 10 vira ruído.

**Como achar (busca na web):**
- mesmo negócio: `"<nicho>" "<cidade>"`, `"<nicho> studio" site oficial`, o nicho em inglês
  (`pilates studio website`, `physiotherapy clinic website`) e os nomes de redes conhecidas
- design: galerias com página de verdade, no ar, como siteinspire.com, land-book.com,
  godly.website, minimal.gallery, onepagelove.com, lapa.ninja e awwwards.com; filtre pelo
  assunto ou pelo tipo de página e abra o site, não o card da galeria
- o que NÃO serve: tela de Dribbble ou Behance (não é página, ninguém rolou), loja de template,
  print de outra IA, página fora do ar

**Quando a busca só devolve classificado, loja e marketplace** (acontece em ofício e comércio local:
marcenaria, serralheria, conserto, atelier): troque a pergunta. Em vez de procurar o serviço,
procure quem o reúne e abra o site OFICIAL de cada nome que aparecer. Lugares por tipo de negócio,
sem lista fixa de endereços (site muda, cai e bloqueia; o que vale é o caminho):
- **Quem faz, não quem vende:** `fabricante de <produto>`, `<ofício> artesanal`, `<ofício> sob medida
  atelier` e o mesmo em inglês (`<craft> workshop`, `<craft> studio`, `<maker> portfolio`). Termos de
  quem faz, não de quem compra (`marcenaria` e `ateliê`, não `comprar móvel`).
- **Quem reconhece o bom:** páginas de prêmio, mostra e feira do setor (premiados e expositores têm
  site próprio, quase sempre cuidado); associação, sindicato, guilda ou conselho do ofício, com a
  lista de associados ou membros; revistas e blogs de arquitetura e decoração, que citam o autor
  com link.
- **Quem lista com o endereço oficial:** Wikipedia e Wikidata (lista de empresas do setor, campo
  "site oficial"), Google Maps e Google Business do bairro (o botão "site" leva ao oficial),
  diretórios de profissionais da área (o perfil aponta para o site do profissional).
- **Perfil de rede social:** o link da bio de quem faz bem leva ao site.
- Para o tipo `design`, a galeria do parágrafo acima já resolve; filtre pelo tipo de página.

Rode a captura nas candidatas e olhe o `estado` que ela imprime ANTES de gastar leitura: só
`ok` entra. `bloqueada` (403, desafio de navegador), `quebrada` (erro, sem estilo, vazia) e
`coberta` (modal que não fecha) saem; troque a URL, não force. Sites grandes de marca costumam
bloquear robô: prefira o site de quem faz, pequeno e cuidado.

**Critério para ficar:** a página tem algo que a nossa precisa fazer melhor (abrir com imagem
forte, escrever pouco e claro, conduzir a uma ação só, passar cuidado e confiança) e faz isso
com acabamento. Página bonita que não ensina nada para o nosso caso não entra.

## Como capturar

```bash
node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> <url> ...
node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --tipo design <url> <url> ...
```

O script abre cada URL no Chromium headless (1440x900), tenta fechar o aviso de cookies por um
botão comum (recusar, fechar ou aceitar, nessa ordem), grava a primeira dobra e uma seção do meio
em `<dir>/referencias/` e atualiza `referencias/referencias.json`. Cada URL sai com um estado e o
motivo (também gravado em `captura` no manifesto):

| Estado | Quando | O que fazer |
|---|---|---|
| `ok` | página renderizada de verdade | ler os dois PNG |
| `bloqueada` | HTTP 401, 403 ou 429, ou texto de bloqueio (Forbidden, "Just a moment", captcha) dominando a página | trocar a URL |
| `quebrada` | HTTP 400 ou mais, página sem folha de estilo aplicada, ou vazia | trocar a URL |
| `coberta` | modal ou aviso cobrindo mais de 40% da janela mesmo depois de tentar fechar | trocar a URL, ou escolher uma página sem modal de região |

O código de saída é diferente de zero enquanto houver menos de 6 referências `ok` no manifesto.
`node <dir-da-skill>/scripts/capturar-referencias.mjs --projeto <dir> --limpar-ruins` tira do
manifesto o que não é `ok` e move os PNG para `descartados/referencias/`. O gate reprova a
referência que ficar no manifesto marcada como ruim. Página que pede login fica de fora. Página
curta de verdade (cabe numa janela) pode ter o print do meio igual ao da dobra.

## Como ler (o trabalho de verdade)

Abra os DOIS PNGs de cada referência com os próprios olhos (Read). Depois preencha no
manifesto, para cada uma:

```json
{
  "url": "https://...",
  "tipo": "mesmo-negocio",
  "prints": {"dobra": "referencias/01-...-dobra.png", "meio": "referencias/01-...-meio.png"},
  "faz_bem": {
    "composicao": "o que a primeira dobra e o meio fazem com o espaço",
    "tipografia": "famílias, escala, peso, como o título carrega a personalidade",
    "imagem": "que foto, de quê, com que luz e enquadramento, onde ela entra",
    "ritmo": "como as seções se alternam, respiro, densidade"
  },
  "principio": "a regra que se leva daqui para a nossa página",
  "lido": true
}
```

**Princípio, nunca cópia.** O que se leva é uma regra transferível ("a foto mostra o
equipamento, não um rosto de banco de imagem"; "o título fala da dor em 8 palavras e a foto
responde"), nunca a frase, o layout idêntico, o logo, a foto ou a paleta exata de outra
marca. Copiar página alheia é plágio e ainda entrega uma página que não é do cliente.

**Banner de cookie, pop-up ou carregamento lento no print:** registre na leitura o que o print
mostra de fato. Leitura inventada sobre o que o print não mostra é dado inventado.

## O gate

```bash
node <dir-da-skill>/scripts/py.mjs gate-referencias.py --projeto <dir>
```

Reprova (exit 1) se houver menos de 6 referências válidas ou menos de 2 de cada tipo. Uma
referência só vale com URL http(s) única, os dois prints dentro do projeto (PNG real, de pelo
menos 320x300, que não está em branco nem é cópia de outro print), a leitura nos quatro eixos,
o princípio e `"lido": true`. O registro da etapa 1 (`gate-etapas.py registrar 1`) roda este
gate e bloqueia junto.

O gate garante que a pesquisa existe e que os prints são reais. Quem cobra se a página ficou
no nível delas é a lente `comparacao-referencias` dos auditores (`references/auditores.md`).

## Saída que alimenta o plano visual

Antes do passo c, escreva em `referencias/sintese.md`, em poucas linhas:
- os 3 princípios que mais se repetem entre as referências boas
- o que todas as do mesmo negócio fazem igual (o padrão do ramo, que a nossa pode seguir ou
  quebrar de propósito)
- as 2 ou 3 referências mais fortes, que viram a régua da lente `comparacao-referencias`
