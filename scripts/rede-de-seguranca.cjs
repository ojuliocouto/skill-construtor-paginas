/** Separa, dentro de UM script em linha, a rede de segurança (classe `js` + temporizador que a retira) do script principal.
 *
 *  Por que existe (3.5.8, achado N13): o `gate-movimento` simula "o script principal falhou" removendo ou atrasando o script
 *  em linha. Quando o aluno põe a rede de segurança e a medida do `--vh` (que usa `addEventListener`) no MESMO `<script>`,
 *  o gate tratava o script inteiro como principal, levava a rede junto e dizia "falta a rede de segurança" com ela presente.
 *  Aqui o código é partido em instruções de nível zero: as que põem a classe `js` ou conferem `data-js-ok` ficam (rede),
 *  o resto é o principal. Sem rede no script, `rede` volta vazio e o gate segue a regra antiga.
 */
'use strict';

const MARCAS_DO_PRINCIPAL = /IntersectionObserver|addEventListener|querySelector|requestAnimationFrame|fetch\(|getBoundingClientRect/;
const POE_A_CLASSE_JS = /classList\s*\.\s*(add|replace)\s*\(\s*(['"]no-js['"]\s*,\s*)?['"]js['"]/;
const CONFERE_O_SINAL = /hasAttribute\s*\(\s*['"]data-js-ok['"]\s*\)/;

/** Parte o código em instruções de nível zero (fim em `;` ou em `}` seguida de quebra de linha), sem quebrar texto, comentário nem parênteses. */
function instrucoes(codigo) {
  const saida = [];
  let ini = 0, prof = 0, i = 0;
  const n = codigo.length;
  const corta = (fim) => { const t = codigo.slice(ini, fim); if (t.trim()) saida.push(t); ini = fim; };
  while (i < n) {
    const c = codigo[i];
    if (c === '"' || c === "'" || c === '`') {
      for (i++; i < n && codigo[i] !== c; i++) if (codigo[i] === '\\') i++;
      i++; continue;
    }
    if (c === '/' && codigo[i + 1] === '/') { while (i < n && codigo[i] !== '\n') i++; continue; }
    if (c === '/' && codigo[i + 1] === '*') { const f = codigo.indexOf('*/', i + 2); i = f < 0 ? n : f + 2; continue; }
    if (c === '(' || c === '[' || c === '{') prof++;
    else if (c === ')' || c === ']' || c === '}') {
      prof--;
      if (c === '}' && prof === 0) {
        const resto = codigo.slice(i + 1);
        const m = /^[ \t]*(\r?\n)\s*(\S?)/.exec(resto);
        const declaracao = /^\s*(?:async\s+)?function\s+[\w$]/.test(codigo.slice(ini, i + 1));   // `function f() {}` termina no fecha-chave, mesmo se a próxima linha abre com parêntese
        if (m && (declaracao || !/^(?:[(.,;)]|else\b|catch\b|finally\b|while\b)/.test(resto.trimStart()))) { corta(i + 1); i++; continue; }
      }
    } else if (c === ';' && prof === 0) { corta(i + 1); i++; continue; }
    else if (c === '\n' && prof === 0) {
      // quebra de linha sem ponto e vírgula: instrução nova quando a anterior terminou e a próxima começa por palavra
      const antes = codigo.slice(ini, i).trimEnd().slice(-1);
      const depois = /^\s*([A-Za-z_$][\w$]*)/.exec(codigo.slice(i + 1));
      if (antes && /[)\]}'"`\w$]/.test(antes) && depois && !/^(?:else|catch|finally|while|in|of|instanceof)$/.test(depois[1])) { corta(i + 1); i++; continue; }
    }
    i++;
  }
  corta(n);
  return saida;
}

/** @returns {{rede: string, principal: string}} */
function dividirScript(codigo) {
  const rede = [], principal = [];
  for (const parte of instrucoes(codigo)) {
    const ehRede = (POE_A_CLASSE_JS.test(parte) || CONFERE_O_SINAL.test(parte)) && !MARCAS_DO_PRINCIPAL.test(parte);
    (ehRede ? rede : principal).push(parte);
  }
  return { rede: rede.join('\n'), principal: principal.join('\n') };
}

module.exports = { dividirScript, instrucoes, MARCAS_DO_PRINCIPAL };
