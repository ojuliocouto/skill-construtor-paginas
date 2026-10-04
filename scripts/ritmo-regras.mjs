/**
 * Regras do GATE DE RITMO, sem navegador: recebem a assinatura de cada seção e devolvem as falhas.
 *
 * A assinatura de uma seção é "<posição do título> + <tipo do corpo>", por exemplo
 * "título centralizado + cartões" ou "título ao lado do conteúdo + lista". Quem mede a assinatura
 * na página é o gate-ritmo.mjs; aqui só mora a decisão, para os testes não precisarem de Chromium.
 *
 * Duas regras (padrão da v7, 04/10/2026):
 *  1. DUAS SEÇÕES VIZINHAS não podem ter o mesmo esqueleto. O gate-composicao deixa passar 2
 *     seguidas e só reprova a terceira; a v7 só saiu da cara de template porque cada seção
 *     escolheu um esqueleto que a anterior não usou.
 *  2. NO MÁXIMO 1 seção "título centralizado + cartões" na página: é o molde de template por
 *     excelência (a v6 tinha duas, a das situações e a de grupo ou particular).
 *
 * Exceção declarada: `data-ritmo-ok="motivo"` na seção; o motivo aparece na saída.
 */
export const CENTRO_CARTOES = 'título centralizado + cartões';
export const MAXIMO_CENTRO_CARTOES = 1;

/** @param {{nome:string, sig:string, excecao?:string}[]} secoes na ordem da página */
export function avaliarRitmo(secoes) {
  const falhas = [];
  const excecoes = [];
  const comparaveis = (s) => !s.sig.startsWith('sem-titulo');
  for (let i = 1; i < secoes.length; i++) {
    const a = secoes[i - 1], b = secoes[i];
    if (!comparaveis(a) || !comparaveis(b) || a.sig !== b.sig) continue;
    if (a.excecao || b.excecao) {
      excecoes.push(`"${a.nome}" e "${b.nome}": ${b.excecao || a.excecao}`);
      continue;
    }
    falhas.push(`seções vizinhas com o mesmo esqueleto ("${a.sig}"): "${a.nome}" e "${b.nome}"; cada seção escolhe um esqueleto que a anterior não usou`);
  }
  const centro = secoes.filter((s) => s.sig === CENTRO_CARTOES && !s.excecao);
  if (centro.length > MAXIMO_CENTRO_CARTOES) {
    falhas.push(`${centro.length} seções no formato "${CENTRO_CARTOES}" (${centro.map((s) => `"${s.nome}"`).join(', ')}); no máximo ${MAXIMO_CENTRO_CARTOES}: é o molde de template`);
  }
  secoes.filter((s) => s.excecao && s.sig === CENTRO_CARTOES).forEach((s) => excecoes.push(`"${s.nome}": ${s.excecao}`));
  return { falhas, excecoes, centroCartoes: centro.length };
}
