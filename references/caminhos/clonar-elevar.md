# Caminho CLONAR + ELEVAR: "clona E deixa foda"

Nasceu de uma falha real (26/08/2026). O pedido foi "faz o clone da original e deixa foda";
rodou o CLONAR, cuja régua é fidelidade, e o dono respondeu que a página tinha ficado quase
igual à original. CLONAR mede fidelidade, MELHORAR mede não regressão, e nenhum dos dois
pergunta se ficou MELHOR. Este caminho pergunta.

**Como reconhecer:** o pedido tem as duas coisas, clone e melhoria ("clona e melhora", "igual
mas melhor", "clone melhorado"). Na dúvida, pergunte: a diferença é enorme e cara.

## O que é intocável

Extraia com `node <dir-da-skill>/scripts/extrai-identidade.mjs "<URL>"` e não mexa: cor, logo,
família tipográfica, copy, telefone, endereço, CNPJ, números. Identidade real vence qualquer
preferência estética, inclusive a do plano visual.

## O que DEVE mudar

Higiene (trocar ícone por foto, reorganizar grade, otimizar peso) melhora a página e não muda
o que a pessoa VÊ quando abre. Elevar mexe nestes eixos:

| Eixo | Pergunta | Sinal de que não mexeu |
|---|---|---|
| Composição | as seções ainda são retângulos empilhados? | toda seção é um container centralizado |
| Escala | a tipografia tem drama? | títulos no mesmo tamanho da original |
| Profundidade | há camada, sobreposição, sangria? | tudo chapado |
| Movimento | o que se mexe, e por quê? | só fade de rolagem igual em toda seção |
| Densidade | o ritmo varia? | mesma altura e mesmo respiro do início ao fim |
| Assinatura | qual elemento só ESTA página tem? | dá para trocar por qualquer concorrente |

Pelo menos **quatro** dos seis eixos com mudança NOMEADA, com antes e depois.

## O fluxo

1. Extrair e printar a original (como no `references/caminhos/clonar.md`, passo 1).
2. Pesquisa de referências do CRIAR (passo b, `references/pesquisa-de-referencias.md`): a
   original diz o que preservar; as referências dizem até onde elevar.
3. Plano visual pela `frontend-design` (passo c do CRIAR), com a identidade da original travada
   como restrição e a mudança concentrada nos seis eixos.
4. Construção, gates e auditores do CRIAR (passos e, f, g), com `--caminho clonar-elevar`.

## O gate deste caminho

`node <dir-da-skill>/scripts/py.mjs lado-a-lado.py <png-original> <png-nova> <dir>/comparativo.jpg --rotulos "Original,Elevada"`

1. Olhe a imagem e responda por escrito: **o dono veria a diferença sem eu apontar?** Se a
   resposta honesta é não, volte. Nenhuma lista de melhorias compensa esse não.
2. Liste os eixos alterados, com antes e depois. Menos de 4 = não elevou.
3. Liste o que foi PRESERVADO da identidade, item a item. Elevar sem preservar virou outra marca.

Não existe número aqui de propósito: um medidor de distância por pixel deu 27,3% para a versão
reprovada e 26,3% para a corrigida. Diferença de pixel não mede "cara de igual"; o olho, com a
imagem na mão, mede.
