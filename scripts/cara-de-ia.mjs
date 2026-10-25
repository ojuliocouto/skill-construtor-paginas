/**
 * RÉGUAS DE "CARA DE IA" (auditoria de 25/10/2026, achados A6, A7, A8 e enfeite de título).
 *
 * Funções puras, sem navegador: gate-texto.mjs e gate-composicao.mjs medem a página e pedem a decisão aqui.
 * O teste é `cara-de-ia.test.mjs`. Cada limite foi calibrado em páginas reais, medidas em 1440x900:
 *
 *  página (veredito do dono ou da auditoria)        filetes de enfeite   tabela   altura    por tela de 900 px
 *  curso para advogados (produção, cara de template)       22               0     11.064 px   1,79  reprova
 *  estúdio v3 (o "jornal de filetes" original)              11               1      5.398 px   1,83  reprova
 *  estúdio v7 (aprovada pelo dono)                          12              20     15.204 px   0,71  passa
 *  torrefação (teste 3.5.8, a mais própria)                  1              11      9.754 px   0,09  passa
 *  ateliê de móveis (teste 3.5.6)                            0               0      9.954 px   0     passa
 *
 * Por isso o filete se conta por TELA e sem a tabela: a contagem crua (22 contra 32 da v7 aprovada) punia
 * a página boa e soltava a ruim. Filete dentro de dl ou table é linha de tabela de rótulo e valor, não enfeite.
 */

/** O aviso antigo do gate-texto (10 ou mais filetes) vira também o mínimo absoluto para reprovar. */
export const FILETES_MINIMO = 10;
/** Filetes de enfeite por tela de 900 px em 1440. Medido: 1,79 e 1,83 nas reprovadas; 0,71 na maior das aprovadas. */
export const FILETES_POR_TELA_MAXIMO = 1.2;

export function julgarFiletes({ enfeite, tabela = 0, alturaPagina, alturaTela = 900 }) {
  const telas = Math.max(1, alturaPagina / alturaTela);
  const porTela = enfeite / telas;
  return {
    telas,
    porTela,
    reprova: enfeite >= FILETES_MINIMO && porTela > FILETES_POR_TELA_MAXIMO,
    aviso: enfeite + tabela >= FILETES_MINIMO,
  };
}

/** Motivo de exceção (data-icone-repetido-ok): frase de pelo menos 3 palavras, nunca "1", "sim" ou "ok". */
export function motivoValido(txt) {
  const palavras = String(txt ?? '').trim().split(/\s+/).filter((p) => /\p{L}{2,}/u.test(p));
  return palavras.length >= 3;
}

/** O motivo de um desenho é a primeira oração do data-desenho: "sinal de mais do logo, gigante" = "sinal de mais do logo". */
export function motivoDoDesenho(d) {
  return String(d ?? '').split(/[,;:(]/)[0].replace(/\s+/g, ' ').trim().toLowerCase();
}

/** Mais de 6 do mesmo motivo na página reprova (V17 da auditoria). Medido: 16 "sinal de mais do logo" na página de produção. */
export const MOTIVO_REPETIDO_MAXIMO = 6;

/** itens: [{ chave, nome }]. Devolve os motivos acima do limite, do mais repetido ao menos. */
export function contarMotivos(itens) {
  const mapa = new Map();
  for (const { chave, nome } of itens) {
    if (!chave) continue;
    const g = mapa.get(chave) || { chave, n: 0, nomes: new Set() };
    g.n++; if (nome) g.nomes.add(nome);
    mapa.set(chave, g);
  }
  return [...mapa.values()].filter((g) => g.n > MOTIVO_REPETIDO_MAXIMO).sort((a, b) => b.n - a.n)
    .map((g) => ({ chave: g.chave, n: g.n, nomes: [...g.nomes].slice(0, 3) }));
}

/** O mesmo enfeite (traço, sublinhado, filete, glifo) em mais de 3 h2 reprova. Medido: o mesmo traço em 9 de 10 h2. */
export const TITULOS_COM_O_MESMO_ENFEITE_MAXIMO = 3;

/** enfeites: um item por h2 visível, '' quando o título não tem enfeite. */
export function julgarEnfeites(enfeites) {
  const conta = new Map();
  for (const e of enfeites) if (e) conta.set(e, (conta.get(e) || 0) + 1);
  let pior = null;
  for (const [assinatura, n] of conta) if (!pior || n > pior.n) pior = { assinatura, n, total: enfeites.length };
  return { pior, reprova: !!pior && pior.n > TITULOS_COM_O_MESMO_ENFEITE_MAXIMO };
}

// Profissões e papéis de gente, no singular, plural, masculino e feminino. Começo de palavra obrigatório
// ((?<!\p{L})); fim livre, salvo onde o radical também nomeia coisa (arquitetura, fotografia, consultoria).
const FIM = '(?!\\p{L})';
const PROFISSOES = [
  'advogad[oa]', `m[eé]dic[oa]s?${FIM}`, 'dentista', 'odont[oó]log', 'contador', 'contabilista', 'nutricionista', 'nutr[oó]log',
  'corretor', 'psic[oó]log', 'psicanalista', 'psiquiatra', 'fisioterapeuta', 'terapeuta', 'fonoaudi[oó]log', 'enfermeir',
  'farmac[eê]utic', 'veterin[aá]ri', `arquitet[oa]s?${FIM}`, 'engenheir', 'professor', 'educador', 'pedagog', 'coach', 'mentorad',
  `consultor(?:a|es|as)?${FIM}`, `personal${FIM}`, 'treinador', 'instrutor', 'esteticista', 'cabeleireir', 'barbeir', 'maquiador',
  'manicure', `fot[oó]graf[oa]s?${FIM}`, 'vendedor', 'gestor', 'empres[aá]ri[oa]', `aut[oô]nom[oa]s?${FIM}`, 'freelancer',
  'concurseir', `ju[ií]z(?:a|es|as)?${FIM}`, 'promotor', 'delegad[oa]', `policia(?:l|is)${FIM}`, 'motorista', 'noiv[oa]', 'casais',
  `beb[eê]s?${FIM}`, 'adolescente', 'universit[aá]ri', 'aposentad', 'atendente', 'cozinheir', 'artista', 'cuidador', 'secret[aá]ri[oa]',
];
// O que já valia antes (público geral).
const GERAL = [
  'mulher', 'homem', 'homens', 'pessoa', 'm[aã]es', `pais${FIM}`, 'crian[cç]a', 'alun[oa]', 'paciente', 'cliente', 'idos[oa]', 'jovens',
  'adult', 'fam[ií]lia', 'gestante', 'atleta', 'estudante', 'profission', `donos?${FIM}`, `donas?${FIM}`, 'empreendedor', 'moradores',
  'p[uú]blico feminino', 'p[uú]blico masculino',
];
// O que a foto ou o desenho mostra (alt e data-desenho).
const NA_IMAGEM = ['senhora', 'senhor', 'menin[oa]', 'm[aã]os? d[aoe]'];

const montar = (lista) => new RegExp(`(?<!\\p{L})(?:${lista.join('|')})`, 'iu');
export const PESSOAS = montar([...GERAL, ...PROFISSOES]);
export const PALAVRAS_PESSOA = montar([...GERAL, ...PROFISSOES, ...NA_IMAGEM]);

export const publicoDePessoas = (txt) => PESSOAS.test(String(txt ?? ''));
export const pessoaNoTexto = (txt) => PALAVRAS_PESSOA.test(String(txt ?? ''));
