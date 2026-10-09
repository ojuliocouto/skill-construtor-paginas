/**
 * Confere, antes de abrir o navegador, que a página a medir está no ar.
 *
 * Por que existe (P11, 3.5.10): no teste de ponta a ponta da Torra Clara o servidor local caiu 4 vezes e os gates
 * estouraram com `net::ERR_CONNECTION_REFUSED` e um stack trace do Playwright. Quem lia pensava que a página estava
 * quebrada; o defeito era o servidor. Agora cada gate de navegador chama `exigirServidor(url)` logo depois de ler os
 * argumentos: se nada responde na URL, o gate para com UMA mensagem que começa com `servidor fora do ar em <url>`,
 * diz como subir de novo e deixa claro que isso não é veredito sobre a página. Saída 3 (a 1 é "a página reprovou", a 2
 * é "pedido errado").
 *
 * Qualquer resposta HTTP, até 404, conta como "no ar": o assunto aqui é a porta, não o conteúdo.
 */
import http from 'node:http';
import https from 'node:https';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
export const SAIDA_SERVIDOR_FORA = 3;
export const MARCA = 'servidor fora do ar em';

function umaTentativa(url, tempoMs) {
  return new Promise((resolve) => {
    let alvo;
    try { alvo = new URL(url); } catch { return resolve({ ok: false, motivo: `a URL "${url}" não é válida` }); }
    if (alvo.protocol !== 'http:' && alvo.protocol !== 'https:') return resolve({ ok: true });   // file:// e afins não têm servidor
    const cliente = alvo.protocol === 'https:' ? https : http;
    const req = cliente.request(alvo, { method: 'GET', timeout: tempoMs, rejectUnauthorized: false }, (res) => {
      res.resume();
      resolve({ ok: true });
    });
    req.on('timeout', () => { req.destroy(); resolve({ ok: false, motivo: `não respondeu em ${Math.round(tempoMs / 1000)} s` }); });
    req.on('error', (e) => resolve({ ok: false, motivo: e.code === 'ECONNREFUSED' ? 'nada ouve nessa porta (conexão recusada)' : (e.code || e.message) }));
    req.end();
  });
}

/** Tenta algumas vezes (servidor que acabou de subir leva uns décimos de segundo). Devolve { ok, motivo? }. */
export async function conferirServidor(url, { tentativas = 3, esperaMs = 400, tempoMs = 5000 } = {}) {
  let ultimo = { ok: false, motivo: 'sem resposta' };
  for (let i = 0; i < tentativas; i++) {
    ultimo = await umaTentativa(url, tempoMs);
    if (ultimo.ok) return ultimo;
    if (i < tentativas - 1) await new Promise((r) => setTimeout(r, esperaMs));
  }
  return ultimo;
}

/** A mensagem única de "servidor fora do ar", com o comando para subir de novo. */
export function mensagemServidorFora(url, motivo) {
  const py = path.join(AQUI, 'py.mjs').split(path.sep).join('/');
  const comando = /[^\x00-\x7f ]| /.test(py) ? `node "${py}"` : `node ${py}`;
  return [
    `${MARCA} ${url}: ${motivo}.`,
    `Isto não é veredito sobre a página: o gate nem chegou a abri-la. Suba o servidor e rode o gate de novo:`,
    `  ${comando} servidor-gzip.py <pasta da dist> <porta>`,
    `Se a porta estiver ocupada, o servidor escolhe outra e imprime a linha "URL: http://127.0.0.1:<porta>/": use ESSA URL no --url.`,
    `Se a dist foi refeita agora há pouco (montar-dist.py), confira que o servidor continua de pé antes de repetir.`,
  ].join('\n');
}

/** Para o gate com a mensagem acima (saída 3) se nada responde em `url`. */
export async function exigirServidor(url, opcoes) {
  const r = await conferirServidor(url, opcoes);
  if (r.ok) return;
  console.error(mensagemServidorFora(url, r.motivo));
  process.exit(SAIDA_SERVIDOR_FORA);
}
