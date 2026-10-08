/** Gates visuais, família `movimento`: controles cujo nome começa por simetria, movimento.
 *  Divisão do antigo test-gates-visuais.cjs (3.5.7); a lógica está em `gates-visuais-lib.cjs`.
 *  Filtro por nome: `GATES_FILTRO=<prefixo> node scripts/test-gates-visuais-movimento.cjs`. */
require("./gates-visuais-lib.cjs").iniciar(["simetria", "movimento"]);
