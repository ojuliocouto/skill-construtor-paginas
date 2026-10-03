# Cardápio de seções

A biblioteca da etapa PLANO (`references/plano.md`, seção c). Cada objetivo de seção tem 2 ou
3 formatos; cada formato tem um arquivo curto (quando usar, estrutura, armadilha) e um HTML
mínimo de exemplo, que vira miniatura no PLANO.md:

`node <dir-da-skill>/scripts/previa-direcoes.mjs --miniaturas <dir-da-skill>/references/secoes --saida <dir>/plano/miniaturas`

O aluno escolhe um formato por objetivo e monta a ordem. Regra de composição que os gates
cobram depois: o mesmo formato em 3 seções seguidas reprova (`gate-composicao.mjs`), e a seção
que é o diferencial do negócio leva o formato mais forte. Os exemplos seguem
`references/preferencias-de-design.md`: sem kicker, sem 01/02/03, sem número gigante.

### Primeira dobra
- `dobra-split-imagem`: quando há uma foto forte e a promessa cabe em duas linhas.
- `dobra-faixa-cheia`: quando a imagem conta a história sozinha e tem área calma para o texto.
- `dobra-tipografica`: quando ainda não há foto boa, ou a frase é o argumento.

### Dor
- `lista-editorial`: dores ditas em frase inteira, lidas como conversa.
- `caixas-iguais`: 3 ou 4 situações paralelas do mesmo peso, cada uma com desenho próprio.
- `faixa-destaque`: uma frase só que resume a dor e dá respiro.

### Mecanismo ou diferencial
- `comparacao-assimetrica`: quando existe contraste real entre o jeito comum e o seu.
- `split-imagem`: quando uma foto prova o que o método faz.

### Prova
- `credencial-retrato`: quem ainda não tem depoimento mostra quem atende, com registro confirmado.
- `depoimentos-grade`: só com depoimento real, com nome e autorização.
- `mosaico-do-espaco`: negócio local mostra o lugar real, com legenda.

### Oferta
- `oferta-bloco-unico`: uma oferta só, limpa, com o botão do destino real.
- `oferta-duas-opcoes`: duas formas reais de comprar, lado a lado e com a mesma altura.

### Como funciona
- `linha-do-tempo`: processo em que a ordem importa, sem número nos marcos.
- `caixas-iguais`: passos curtos do mesmo peso, em caixas iguais.

### FAQ
- `faq-coluna-centrada`: 4 a 7 dúvidas que travam a decisão, abrindo ao clique.
- `faq-duas-colunas`: muitas dúvidas curtas, todas à vista.

### Fecho
- `fecho-faixa-cheia`: última frase e o botão, quando a página já respondeu tudo.
- `fecho-split-contato`: negócio local que fecha com endereço, horário e contato.
