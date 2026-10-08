/** Gates visuais, família `composicao`: controles cujo nome começa por composicao, texto.
 *  Divisão do antigo test-gates-visuais.cjs (3.5.7); a lógica está em `gates-visuais-lib.cjs`.
 *  Filtro por nome: `GATES_FILTRO=<prefixo> node scripts/test-gates-visuais-composicao.cjs`. */
require("./gates-visuais-lib.cjs").iniciar(["composicao", "texto"]);
