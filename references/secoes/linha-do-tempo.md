# Linha do tempo

Formato `linha-do-tempo`. Exemplo mínimo: `linha-do-tempo.html` (abra no navegador ou veja a miniatura no plano).

## Quando usar

Para um processo em que a ordem importa (do primeiro contato à primeira aula, do diagnóstico ao resultado).

## Estrutura

Uma linha horizontal no desktop (vertical no celular) com um marco por etapa e o texto embaixo de cada marco. A linha termina no último marco, sem passar dele. Marcos sem número: a posição já diz a ordem.

## Armadilha

Numeração 01/02/03 gigante nos marcos; linha que segue além do último passo; mais de 5 etapas.

## Título ao lado de marcos verticais

Se o plano pede o título à esquerda e os marcos empilhados à direita (a assinatura em três estados faz isso), declare `data-assimetrico="motivo escrito"` na seção: a regra de simetria (`gate-simetria.mjs`) reprova esse par por padrão e passa a avisar quando o atributo está lá. Sem o atributo, reprova.
