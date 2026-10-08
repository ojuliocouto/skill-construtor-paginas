/** Gates visuais, família `responsivo`: controles cujo nome começa por responsivo, oclusao, clique, identidade, http, wame, video, dash.
 *  Divisão do antigo test-gates-visuais.cjs (3.5.7); a lógica está em `gates-visuais-lib.cjs`.
 *  Filtro por nome: `GATES_FILTRO=<prefixo> node scripts/test-gates-visuais-responsivo.cjs`. */
require("./gates-visuais-lib.cjs").iniciar(["responsivo", "oclusao", "clique", "identidade", "http", "wame", "video", "dash"]);
