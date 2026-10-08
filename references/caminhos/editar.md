# Caminho EDITAR: mudança pontual, cirúrgica

Objetivo: fazer exatamente o que foi pedido, sem efeito colateral. Este caminho NÃO roda
pesquisa de referências, plano visual nem auditores: rodar o rito completo numa troca de
headline é erro de processo.

1. **Travar o escopo em uma frase** e repetir: "vou trocar o headline do hero, e só isso". Mais
   de uma coisa no pedido: listar todas antes de começar.
2. **Localizar o arquivo real** que serve a página no ar, não um parecido. Conferir qual projeto
   e qual rota estão publicados antes de editar.
3. **Editar só o escopo.** Proibido "já que estou aqui" mexer em espaçamento, cor ou copy que
   ninguém pediu. Melhoria fora do escopo se propõe no fim, não se aplica.
4. **Edição por script com `assert`:** troca que não acha o trecho falha em silêncio (build
   verde, arquivo intacto). Uma linha de `assert velho in texto` por troca, e depois medida no
   navegador (`getComputedStyle`, `getBoundingClientRect`) para confirmar que o pixel mudou.
5. **Checklist de regressão:** celular, modo escuro se existir, links e âncoras, formulário e
   checkout, a seção vizinha da que foi tocada, e `gate-classes-mortas.py` se a edição mexeu
   em classe de utilitário.
6. **Deploy** sem nunca sobrescrever projeto existente.
7. **Prova:** print do ponto alterado, desktop e celular, lido com os próprios olhos, mais a
   confirmação de que o resto da página continua igual:
   `node <dir-da-skill>/scripts/screenshot-prova.js <url> <dir>/prova-edicao`
   `node <dir-da-skill>/scripts/py.mjs uso-ferramentas.py --projeto <dir> checar --caminho editar`
8. Registro curto na sessão (o que mudou e onde).

Se a MUDANÇA pede mais (o pedido é "põe um vídeo no hero" ou "refaz a seção de preço"), ela
deixa de ser edição: vire MELHORAR para aquele trecho.

Bloco de entrega deste caminho: escopo travado, checklist de regressão, prova do ponto
alterado e pendências.
