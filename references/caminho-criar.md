# Caminho CRIAR em uma página: os comandos, na ordem

`<dir-da-skill>` = a pasta desta skill. `<dir>` = a pasta do projeto da página. Cada comando
vai inteiro na linha (variável com comando não roda no zsh). Saída diferente de zero = PARA e
conserta. O porquê de cada passo está no SKILL.md, na seção indicada entre parênteses.

## Antes de tudo (0.0-PRE)
1. `python3 <dir-da-skill>/scripts/checar-ferramentas.py` (21st.dev e Higgsfield são opcionais)
2. Ler `references/preferencias-de-design.md` (vale pra toda página)

## Step 0: entender (0.0 a 0.7)
3. Seis perguntas do briefing: nicho, local, público, oferta, preço, ação. Fato ausente = PENDENTE.
4. Classificar em `references/page-types.md` (estúdio, clínica, consultório = `servico-local`)
5. Gravar `evidencias/etapa-0.json` (formato em `references/gate-etapas.md`) e:
   `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 0 --arquivo evidencias/etapa-0.json`

## Step 1: copy (1.0 a 1.6)
6. Serviço local: `references/copy-servico-local.md`. Venda: 1.1 a 1.4. Fechar no COPY LOCK.
7. `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 1 --arquivo evidencias/etapa-1.json`

## Step 2: direção (2.0 a 2.5)
8. Banco de design (aceita português):
   `python3 <dir-da-skill>/scripts/search.py "<nicho e tom>" --domain style -n 3`
   `python3 <dir-da-skill>/scripts/search.py "<nicho>" --domain color -n 3`
   `python3 <dir-da-skill>/scripts/search.py "<tom>" --domain typography -n 3`
9. Passar o resultado pela `frontend-design` e pela `design-taste-frontend`; reprovado, pega o
   próximo resultado do banco e escreve o motivo (2.0). Stack pela tabela DECISÃO DE TECH STACK.
10. `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 2 --arquivo evidencias/etapa-2.json`

## Step 3: construir (3.1 a 3.6)
11. Construir SÓ o hero e olhar o print (3.2-ART):
    `node <dir-da-skill>/scripts/screenshot-prova.js "file://<dir>/index.html" <dir>/prova-hero --sem-identidade`
12. Foto real sem chave: `python3 <dir-da-skill>/scripts/assets-search.py "<tema em inglês>" --type photo`
13. Resto da página, movimento em CSS (3.2b), e compilar o Tailwind (3.5):
    `npx tailwindcss@3 -i _input.css -o tailwind-compiled.css --content ./index.html --minify`
14. `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 3 --arquivo evidencias/etapa-3.json`

## Step 4: verificar (4.0 a 4.6), servindo com compressão
15. `python3 <dir-da-skill>/scripts/servidor-gzip.py <dir> 8765` (em outro terminal; mate no fim)
16. Gates executáveis, cada um seguido do registro na wave com o exit REAL:
    `python3 <dir-da-skill>/scripts/gate-sem-kicker.py <dir>/index.html`
    `python3 <dir-da-skill>/scripts/gate-classes-mortas.py --projeto <dir>`
    `node <dir-da-skill>/scripts/gate-responsivo.mjs --url http://localhost:8765/`
    `node <dir-da-skill>/scripts/gate-oclusao.mjs --url http://localhost:8765/`
    `node <dir-da-skill>/scripts/screenshot-prova.js http://localhost:8765/ <dir>/prova --click "<seletor do botão>"`
    `python3 <dir-da-skill>/scripts/uso-ferramentas.py --projeto <dir> checar --caminho criar`
    registro: `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> gate <nome> --exit <0|1> --detalhe "<saída>"`
    (nomes: sem-kicker, classes-mortas, responsivo, oclusão, identidade, uso-ferramentas)
17. As 8 lentes (`references/audit-agents.md`), uma por subagente, cada uma registrada:
    `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> registrar <lente> --veredito <aprovado|reprovado> --nota <0-10> --achados "<o que olhou e achou>"`
18. Auditor master: `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> checar`
19. Ciclo (4.2f), uma vez por rodada:
    `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> rodada --criticos <N> --altos <N> --pendencias-do-usuario <N> --regressoes <N>`
    Saiu CONTINUA: corrige, refaz os gates do item 16 e as lentes com achado, roda de novo.
20. Passe de gosto (4.2c): tells antes e depois, o depois tem que ser 0.
21. Depois da wave, re-registrar a etapa 3 é esperado (`references/gate-etapas.md`):
    `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 3 --arquivo evidencias/etapa-3.json`
    `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 4 --arquivo evidencias/etapa-4.json`
22. Lighthouse quando houver navegador (SEO abaixo de 90 por `noindex` é esperado, 4.2).
23. Deploy (4.3) ou, sem conta de hosting, entrega local com o deploy em pendência.
24. LER os PNGs de `<dir>/prova` com os próprios olhos e escrever o BLOCO OBRIGATÓRIO DA ENTREGA
    (veredito da wave, identidade, passe de gosto, prova, pendências declaradas).

## Step 5: medir (depois do tráfego)
25. Clarity e eventos (5.1); primeiro check em 48 h (5.2);
    `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir> registrar 5 --arquivo evidencias/etapa-5.json`
