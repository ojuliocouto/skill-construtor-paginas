# Preferências de design: valem para TODA página (carregar ANTES do plano visual)

Regras de gosto medidas em correções reais, repetidas, de quem aprova as páginas desta skill.
Cada item foi cobrança explícita depois de uma entrega. Elas valem para qualquer página, de
qualquer nicho, e têm precedência sobre o banco de design e sobre o estilo sugerido por
qualquer skill de design. A única coisa que vence esta lista é a identidade REAL do cliente
(logo, cor e fonte que ele já usa).

Os itens marcados com **[gate]** são cobrados por script: `scripts/gate-sem-kicker.py`
reprova e sai com código 1. Os outros se conferem no print, com os próprios olhos.

## Proibido (lê como "cara de IA" ou "mal feito")

- **[gate] Kicker em caixa alta abrindo seção.** Rótulo curto, em caixa alta e com letra
  espaçada, em cima do título ("POR QUE CONTINUAR", "PARA VOCÊ"). A seção abre direto no
  título. Rótulo pequeno só DENTRO de card, na fonte dos títulos, em tamanho contido, numa
  linha, nunca em caixa alta espaçada.
- **[gate] Numeração decorativa 01/02/03** no topo de card ou de passo.
- **[gate] Número gigante decorativo em card** (um "4" ou um "1" enorme ao lado do título,
  como enfeite). Se o número é informação, ele vai na frase ("turmas de até 4 pessoas").
- **Foto de pessoa num retângulo de bordas redondas puro.** Foto de gente pede moldura com
  identidade: um recorte com forma própria, um fio na cor da marca deslocado, o símbolo da
  marca na borda. Retângulo arredondado com sombra é o padrão de template.
- **Pílula flutuante sobre a foto** (legenda em cápsula por cima da imagem, "Fulano, seu
  mentor"). A foto fica limpa; a legenda, se houver, vai embaixo dela.
- **Crop que decapita a pessoa ou esconde a cena.** A pessoa aparece INTEIRA. Se não couber,
  a seção vira split, com a foto num lado e o conteúdo no outro. O crop se confere na JANELA
  renderizada (print), nunca no arquivo.
- **Imagem que não casa com o conteúdo da seção.** Pessoa rindo numa seção de dor reprova;
  pose avançada de exercício numa página para iniciante com dor também. Liste o que cada foto
  mostra contra o título ao lado dela.
- **Imagem decorativa dentro da seção de preço (pricing).** É a seção mais importante da
  página e fica limpa.
- **Colunas desbalanceadas** (uma termina muito antes da outra). Alinhar pelo topo ou
  reestruturar a seção.

## Estruturas aprovadas

- **Pricing limpa:** título em largura total em cima; ancoragem compacta num card (itens em
  2 colunas, total no cabeçalho); cards de preço em fileira (empilham no tablet), preço
  grande em linha própria, parcela embaixo, regra separada por fio; botão centralizado
  fechando a seção.
- **Botões rolam para a oferta:** todos os botões de rolagem da página miram a seção de
  oferta (ou de agendamento, no serviço local). Só os botões DENTRO dela e no fecho saem
  para o checkout, o WhatsApp ou o formulário.
- **Par de comparação (antes e depois, com e sem): LADO A LADO e ASSIMÉTRICO.** Empilhado
  reprova; simétrico também. O lado que interessa leva mais largura, começa mais alto e
  carrega o movimento; o outro fica mais estreito, recuado e parado. O título de cada coluna
  fica centralizado sobre a própria coluna.
- **Bom = cor viva COM movimento; ruim = vermelho parado.** A cor do botão (CTA) não serve
  de sinal de aprovação: sobre fundo escuro, laranja e vermelho leem como alerta.
- **Imagem gerada por IA:** conceito criativo encaixado no produto, nunca retrato de estúdio
  genérico. Rosto de gente real só com material real ou com autorização de uso de imagem.
- **Vídeo de fundo:** véu mais leve (a faixa sob o texto intacta e o contraste medido no
  pixel) e clipe mais lento (playbackRate perto de 0,7) para dar tempo de ver.

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
  versões da página.
