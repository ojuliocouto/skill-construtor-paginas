/**
 * Decide se uma captura de referência é boa, olhando o que foi capturado e não só se o
 * navegador terminou sem erro. Função pura: as medidas vêm do navegador (capturar-referencias.mjs).
 *
 * Por que existe (achados A1 e A2, teste de ponta a ponta de 08/10/2026): a captura dizia "ok"
 * para "403 Forbidden", para a verificação do Cloudflare, para página sem CSS e para página com
 * modal de região cobrindo a dobra. O aluno só descobria abrindo cada PNG.
 *
 * Estados, nesta ordem de precedência:
 *   bloqueada  HTTP 401/403/429, ou texto de bloqueio/desafio dominando a página
 *   quebrada   HTTP 400 ou mais, página sem folha de estilo aplicada, ou página vazia
 *   coberta    modal ou aviso cobrindo mais de 40% da janela mesmo depois de tentar fechar
 *   vazia      (3.5.8) a primeira dobra é uma folha lisa, ou o meio é de uma cor só com fotos que não carregaram
 *   ok         nenhuma das anteriores
 */
export const ESTADOS = ['ok', 'bloqueada', 'quebrada', 'coberta', 'vazia'];
export const LIMITE_COBERTURA = 0.4;
// 3.5.8 (N1): fração do print ocupada pela cor mais comum. De 97% para cima o print é uma folha lisa
// (herói em vídeo que não rodou); de 80% para cima só avisa, porque página minimalista de verdade passa.
export const LIMITE_FOLHA_LISA = 0.97;
export const LIMITE_AVISO_DOMINANCIA = 0.8;

// Frases de página de bloqueio. Só valem quando dominam a página (texto curto) ou estão no título.
const BLOQUEIO = [
  /\b403\b[^.]{0,30}(forbidden|erro|error|proibido)/i, /forbidden/i, /access denied/i, /acesso negado/i, /just a moment/i, /um momento/i,
  /checking your browser/i, /verifying you are human/i, /verificando se voc[eê] [eé] humano/i,
  /verifique que voc[eê] [eé] humano/i, /captcha/i, /attention required/i, /are you a robot/i,
  /you have been blocked/i, /request blocked/i, /pardon our interruption/i, /enable javascript and cookies/i,
  /access to this page has been denied/i, /bot detection/i,
  /too many requests/i, /verify (that )?you are (a )?human/i, /confirm you are (a )?human/i, /security check/i,
];
// 3.5.10 (P1): frases tão específicas de tela de bloqueio de robô que valem em qualquer tamanho de texto.
// A tela da Um Coffee tinha o cabeçalho e o menu do site em volta da frase e passou como ok na 3.5.8.
// Frases que podem aparecer num texto comum (too many requests, verify you are human) ficam na lista curta.
const BLOQUEIO_FORTE = [
  /couldn['\u2019]?t verify the security of your connection/i, /verify the security of your connection/i,
  /n[aã]o foi poss[ií]vel verificar a seguran[cç]a da sua conex[aã]o/i,
  /performance (&|&amp;|and) security by cloudflare/i, /\bray id\s*:\s*[0-9a-f]{8,}/i,
  /sorry,? you have been blocked/i, /why have i been blocked/i, /you are being rate limited/i,
  /incapsula incident id/i, /request unsuccessful\. incapsula/i, /reference\s*#\s*\d+\.[0-9a-f]+\.\d+\.[0-9a-f]+/i,
  /press (&|&amp;|and) hold to confirm you are a human/i, /unusual traffic from your computer network/i,
  /detected unusual (traffic|activity)/i, /detectamos (tr[aá]fego|atividade) (incomum|incomuns|at[ií]pic[oa])/i,
  /confirm(e)? que voc[eê] n[aã]o [eé] um rob[oô]/i, /access to this (content|site|website) has been (restricted|denied|blocked)/i,
];
const TITULO_BLOQUEIO = [/just a moment/i, /attention required/i, /access denied/i, /forbidden/i, /^403/, /acesso negado/i, /security check/i, /are you a robot/i];
const TEXTO_CURTO = 800; // abaixo disso, a frase de bloqueio domina a página
const TEXTO_VAZIO = 400; // página do tamanho da janela com menos texto que isso não tem conteúdo

export function classificar({ http, titulo = '', texto = '', temEstilo = true, altura = 0, janela = 900, cobertura = 0, dominanciaDobra, dominanciaMeio, imagensSemCarregar = 0 }) {
  const t = String(texto || '').replace(/\s+/g, ' ').trim();
  const pct = (x) => `${Math.round(x * 100)}%`;
  if ([401, 403, 429].includes(http)) return { estado: 'bloqueada', motivo: `HTTP ${http}: o site recusou o acesso automático` };
  if (TITULO_BLOQUEIO.some((r) => r.test(String(titulo || '')))) return { estado: 'bloqueada', motivo: `título de bloqueio ("${String(titulo).slice(0, 60)}")` };
  const forte = BLOQUEIO_FORTE.map((r) => r.exec(t)).find(Boolean);
  if (forte) return { estado: 'bloqueada', motivo: `texto de bloqueio ou desafio de navegador na página ("${t.slice(Math.max(0, forte.index - 10), forte.index + 70).trim()}")` };
  if (t.length < TEXTO_CURTO && BLOQUEIO.some((r) => r.test(t))) return { estado: 'bloqueada', motivo: `texto de bloqueio ou desafio de navegador domina a página ("${t.slice(0, 70)}")` };
  if (http >= 400) return { estado: 'quebrada', motivo: `HTTP ${http}: a página não existe ou deu erro` };
  if (!temEstilo) return { estado: 'quebrada', motivo: 'a página não rendeu estilo (nenhuma folha de estilo aplicada)' };
  if (altura <= janela + 5 && t.length < TEXTO_VAZIO) return { estado: 'quebrada', motivo: `página vazia: altura ${altura}px (a da janela) e só ${t.length} caracteres de texto` };
  if (cobertura > LIMITE_COBERTURA) return { estado: 'coberta', motivo: `um modal ou aviso cobre ${pct(cobertura)} da janela (limite ${pct(LIMITE_COBERTURA)})` };
  if (typeof dominanciaDobra === 'number' && dominanciaDobra >= LIMITE_FOLHA_LISA) {
    return { estado: 'vazia', motivo: `a primeira dobra é ${pct(dominanciaDobra)} de uma cor só (o herói não rendeu: vídeo ou imagem que não carregou)` };
  }
  if (typeof dominanciaMeio === 'number') {
    if (dominanciaMeio >= LIMITE_FOLHA_LISA) return { estado: 'vazia', motivo: `o print do meio é ${pct(dominanciaMeio)} de uma cor só` };
    if (dominanciaMeio > LIMITE_AVISO_DOMINANCIA && imagensSemCarregar > 0) {
      return { estado: 'vazia', motivo: `o print do meio é ${pct(dominanciaMeio)} de uma cor só e ${imagensSemCarregar} foto(s) não carregaram` };
    }
  }
  const r = { estado: 'ok', motivo: '' };
  if (typeof dominanciaDobra === 'number' && dominanciaDobra > LIMITE_AVISO_DOMINANCIA) {
    r.aviso = `a primeira dobra tem ${pct(dominanciaDobra)} de uma cor só: abra o PNG antes de gastar leitura`;
  }
  return r;
}

// 3.5.8 (N2): próximo número de prefixo (NN-...) a partir dos nomes de arquivo já vistos nas pastas
// (referencias/ e descartados/referencias/). Segue do MAIOR prefixo, nunca do tamanho do manifesto.
export function proximoPrefixo(nomes) {
  let maior = 0;
  for (const n of nomes || []) {
    const m = /^(\d+)-/.exec(String(n));
    if (m) maior = Math.max(maior, Number(m[1]));
  }
  return maior + 1;
}

// 3.5.8 (N3): acha a referência do manifesto para `--remover`. Endereço exato (com ou sem barra final)
// ganha; senão um trecho que só case uma referência; trecho que case várias recusa (ambigua).
export function acharReferencia(refs, alvo) {
  const norm = (u) => String(u || '').trim().replace(/\/$/, '').toLowerCase();
  const a = norm(alvo);
  const lista = refs || [];
  const exata = lista.find((r) => norm(r.url) === a);
  if (exata) return exata;
  const parecidas = a ? lista.filter((r) => norm(r.url).includes(a)) : [];
  if (parecidas.length === 1) return parecidas[0];
  return { erro: parecidas.length > 1 ? 'ambigua' : 'nenhuma', candidatas: parecidas.map((r) => r.url) };
}

// Manifesto antigo (sem `captura`) conta como ok: foi capturado antes desta checagem existir.
export function resumirBoas(refs) {
  return (refs || []).filter((r) => !r.captura || r.captura.estado === 'ok').length;
}
