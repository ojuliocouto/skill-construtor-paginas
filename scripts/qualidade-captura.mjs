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
 *   ok         nenhuma das anteriores
 */
export const ESTADOS = ['ok', 'bloqueada', 'quebrada', 'coberta'];
export const LIMITE_COBERTURA = 0.4;

// Frases de página de bloqueio. Só valem quando dominam a página (texto curto) ou estão no título.
const BLOQUEIO = [
  /\b403\b[^.]{0,30}(forbidden|erro|error|proibido)/i, /forbidden/i, /access denied/i, /acesso negado/i, /just a moment/i, /um momento/i,
  /checking your browser/i, /verifying you are human/i, /verificando se voc[eê] [eé] humano/i,
  /verifique que voc[eê] [eé] humano/i, /captcha/i, /attention required/i, /are you a robot/i,
  /you have been blocked/i, /request blocked/i, /pardon our interruption/i, /enable javascript and cookies/i,
  /access to this page has been denied/i, /bot detection/i,
];
const TITULO_BLOQUEIO = [/just a moment/i, /attention required/i, /access denied/i, /forbidden/i, /^403/, /acesso negado/i, /security check/i, /are you a robot/i];
const TEXTO_CURTO = 800; // abaixo disso, a frase de bloqueio domina a página
const TEXTO_VAZIO = 400; // página do tamanho da janela com menos texto que isso não tem conteúdo

export function classificar({ http, titulo = '', texto = '', temEstilo = true, altura = 0, janela = 900, cobertura = 0 }) {
  const t = String(texto || '').replace(/\s+/g, ' ').trim();
  const pct = (x) => `${Math.round(x * 100)}%`;
  if ([401, 403, 429].includes(http)) return { estado: 'bloqueada', motivo: `HTTP ${http}: o site recusou o acesso automático` };
  if (TITULO_BLOQUEIO.some((r) => r.test(String(titulo || '')))) return { estado: 'bloqueada', motivo: `título de bloqueio ("${String(titulo).slice(0, 60)}")` };
  if (t.length < TEXTO_CURTO && BLOQUEIO.some((r) => r.test(t))) return { estado: 'bloqueada', motivo: `texto de bloqueio ou desafio de navegador domina a página ("${t.slice(0, 70)}")` };
  if (http >= 400) return { estado: 'quebrada', motivo: `HTTP ${http}: a página não existe ou deu erro` };
  if (!temEstilo) return { estado: 'quebrada', motivo: 'a página não rendeu estilo (nenhuma folha de estilo aplicada)' };
  if (altura <= janela + 5 && t.length < TEXTO_VAZIO) return { estado: 'quebrada', motivo: `página vazia: altura ${altura}px (a da janela) e só ${t.length} caracteres de texto` };
  if (cobertura > LIMITE_COBERTURA) return { estado: 'coberta', motivo: `um modal ou aviso cobre ${pct(cobertura)} da janela (limite ${pct(LIMITE_COBERTURA)})` };
  return { estado: 'ok', motivo: '' };
}

// Manifesto antigo (sem `captura`) conta como ok: foi capturado antes desta checagem existir.
export function resumirBoas(refs) {
  return (refs || []).filter((r) => !r.captura || r.captura.estado === 'ok').length;
}
