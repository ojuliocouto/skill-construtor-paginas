# Política de imagem: foto real antes de ilustração

Decisão do dono (04/10/2026), depois da v7 do estúdio contra a v6. A v6 seguiu a regra "sem
autorização de imagem, ilustração própria" e saiu com cara de banco corporativo: o dono a
reprovou. A v7 trocou a ilustração chapada por foto real com um véu de cor único, e o auditor
deu o salto em design, em movimento e na comparação com as referências.

## A ordem

1. Foto do cliente, com autorização de quem aparece.
2. Foto de banco livre (Unsplash, Pexels) como ponte, com "imagem ilustrativa" visível.
3. Ilustração própria só como acento (um traço, uma coluna, a marca), nunca como imagem principal.

**Medida:** `gate-imagens.py --url` soma, na primeira tela em 1440 e em 390, a área de foto (`img`)
e a de desenho (`svg` de topo com 40 px ou mais). Foto tem de ser 60% ou mais do total. Acento
que o plano pediu leva `data-ilustracao-ok="motivo"` no SVG e sai da conta.

## A foto não contradiz o texto ao lado

Se o texto nomeia a profissional ("a Carla"), quem cuida na foto tem o mesmo gênero e o mesmo
papel. A tabela do plano visual (público -> foto -> por quê) ganha a coluna "quem aparece
cuidando", conferida contra o dono nomeado no briefing. Sem foto que case, o bloco fica sem foto
(na v7, o bloco da Carla ficou só tipográfico) em vez de repetir uma foto ou usar uma que
contradiz o texto.

## Banco livre como ponte

- "imagem ilustrativa" colada na foto e inteira na primeira tela, em 1440 e em 390: o fundo da
  legenda tem de ficar abaixo de `innerHeight`. Também no og-image. Vale "Imagem ilustrativa" e "Imagens
  ilustrativas" (plural, para duas ou mais fotos); a mensagem do gate diz se o texto está fora da primeira
  tela ou se não foi achado em lugar nenhum da página.
- Crédito com várias fotos do mesmo autor: ponha o link da origem de cada foto no próprio item do crédito
  (`<li>"Título", por Autor, <a href="origem">...</a></li>`). O gate casa o crédito com a foto por esse link,
  não pelo nome do autor. Título com hífen ("Close-up") vale igual com ou sem o hífen.
- Licença com nome e link (Unsplash e Pexels têm o link da licença deles). Título só o da fonte.
- **Pessoa identificável sem autorização das retratadas** é aviso de bloqueio para tráfego real,
  nunca bloqueio da página de teste: o gate imprime `AVISO ... bloqueia tráfego real` e passa.
  Antes de anunciar, entra a foto da cliente com autorização. Com `--trafego-real` o gate reprova.

## Nenhuma foto, nem cena, repetida entre seções

Reprova a mesma origem em `imagens/LICENCAS.md` e fotos com hash perceptual (pHash de 64 bits) a
menos de 10 bits de distância, quando aparecem em seções diferentes. Os recortes da mesma foto
dentro de UMA seção (arte dirigida para o celular) passam. Na v7, "seis fotos" eram duas salas.

## Foto borrada não entra

A medida é RELATIVA: o detalhe fino da foto dividido pelo da mesma foto desfocada (raio 1,5), na
maior variante legível, em 800 px. Abaixo de 2,5 reprova (borrada), abaixo de 6 é aviso (macia).
O laplaciano absoluto foi descartado: ele confunde pouco contraste com borrado e reprovava uma
foto bege nítida da v7 (8,6) enquanto aprovava fotos de alto contraste já desfocadas. Medido em
04/10/2026: desfocadas com raio 2 dão 1,2 a 1,7; nítidas, 18 a 42; macias, 4 a 6. No aviso, abra
o print e confira se o assunto está em foco: desfoque de fundo proposital pode ficar.

## Comandos

`node <dir-da-skill>/scripts/py.mjs gate-imagens.py --projeto <dir> --url http://localhost:8765/`
`node <dir-da-skill>/scripts/py.mjs gate-imagens.py --projeto <dir> --trafego-real` (página que vai receber anúncio)

Mede com Pillow e numpy (o comando de instalar certo para a sua máquina sai do `checar-ferramentas.py`, linha "Pillow e numpy").
