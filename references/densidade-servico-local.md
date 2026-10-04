# Densidade de copy de serviço local: os 7 itens

Na v7 do estúdio, a página de serviço local ganhou substância que a v6 não tinha: a pessoa decide
com a página aberta, sem precisar perguntar no WhatsApp. Estúdio, clínica, consultório, salão e
academia de bairro respondem a estes sete itens, cada um com fato do briefing (o que falta vira
pendência do cliente, nunca palpite).

| # | Item | Como aparece | Como conferir na `dist/` |
|---|---|---|---|
| 1 | nome e formação de quem cuida | bloco próprio, no corpo (nunca só no rodapé) | o nome do briefing fora do `footer` (`gate-verdade.py`) |
| 2 | o primeiro atendimento, passo a passo | lista ordenada: o que acontece, em que ordem, quanto dura | `ol` com 3 ou mais passos e a duração dita |
| 3 | para quem é e para quem não é | dois blocos, o segundo mais curto e honesto | os dois títulos ("É para você se", "Ainda não é se") |
| 4 | horários | quadro com os dias e as faixas | texto com "segunda", "sábado" e as horas |
| 5 | faixa de preço | "a partir de R$ N", só com o valor confirmado | `R$` no corpo, igual ao do briefing |
| 6 | onde fica | bairro, referência e como chegar | o bairro e uma referência no corpo |
| 7 | o que levar | uma linha por passo ("vá de roupa confortável") | a expressão "levar" ou "traga" no corpo |

## Regras

- Cada item aparece no corpo da página. Preço, horário, formação e registro no conselho são fato:
  sem confirmação do cliente, o item vira "PENDENTE" no PLANO e a página não o afirma.
- O item 3 é o que mais ensina o público sobre a própria dúvida. O bloco "ainda não é" tem de
  dizer o que fazer (por exemplo, procurar o médico antes), nunca só excluir.
- Conferência mínima antes de entregar: um `grep` por item na `dist/index.html` e o resultado
  anotado no relatório. Item sem achado volta para o briefing.

O modelo geral de seções está em `references/copy-servico-local.md`.
