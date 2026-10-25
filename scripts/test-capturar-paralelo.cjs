/**
 * Captura de referências em paralelo, 2 por vez (corte 4 da auditoria de velocidade).
 *
 * A captura de 12 a 23 endereços levava 21,5 s por endereço, um depois do outro. Cada endereço abre a PRÓPRIA aba, no mesmo
 * navegador, e não depende dos outros. O que este teste prova, contra páginas locais com atraso de resposta:
 *  1. dois endereços ao mesmo tempo, nunca três (a regra de memória da máquina: no máximo 2 processos pesados);
 *  2. o resultado é o da fila: os mesmos números de print, as mesmas entradas na MESMA ordem do pedido, os mesmos estados,
 *     mesmo quando o 1º endereço termina depois do 2º;
 *  3. a saída vem na ordem do pedido;
 *  4. um endereço que falha não derruba os outros;
 *  5. endereço repetido no mesmo pedido é capturado uma vez;
 *  6. `--em-serie` volta à fila (1 por vez) e fica mais lento;
 *  7. a captura em paralelo é mais rápida que a fila.
 */
const http = require('node:http');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn } = require('node:child_process');

const AQUI = __dirname;
const rodar = (argv) => new Promise((ok) => {
  const t0 = Date.now();
  const p = spawn(process.execPath, argv, { env: process.env, windowsHide: true });
  let out = '', err = '';
  p.stdout.on('data', (d) => { out += d; });
  p.stderr.on('data', (d) => { err += d; });
  p.on('close', (status) => ok({ status, stdout: out, stderr: err, segundos: (Date.now() - t0) / 1000 }));
});

const CORES = ['#d8e2dc', '#ffe5d9', '#cfe1f2'];
const LONGO = 'Móveis sob medida em madeira maciça, desenhados para a medida da sua casa e entregues montados. '.repeat(10);
let emVoo = 0, maxEmVoo = 0;
const ordemDeChegada = [];
const ATRASO = { 1: 2500, 2: 200, 3: 900, 4: 900, 5: 200 };

const servidor = http.createServer((req, res) => {
  const n = Number((req.url.match(/\d+/) || ['0'])[0]);
  emVoo++; maxEmVoo = Math.max(maxEmVoo, emVoo); ordemDeChegada.push(n);
  setTimeout(() => {
    const blocos = Array.from({ length: 8 }, (_, i) =>
      `<section style="height:700px;background:${CORES[(i + n) % 3]};padding:60px;font:32px Georgia">Seção ${i + 1} da página ${n}. ${LONGO.slice(0, 200)}</section>`).join('');
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(`<!doctype html><html lang="pt-BR"><head><title>Referência ${n}</title></head><body style="margin:0">${blocos}</body></html>`);
    emVoo--;
  }, ATRASO[n] || 100);
});

let falhas = 0;
const checa = (nome, ok, detalhe = '') => { console.log(`  [${ok ? 'ok  ' : 'FALHA'}] ${nome}${detalhe ? ' -> ' + detalhe : ''}`); if (!ok) falhas++; };
const pasta = () => fs.mkdtempSync(path.join(os.tmpdir(), 'cap-par-'));
const manifesto = (proj) => JSON.parse(fs.readFileSync(path.join(proj, 'referencias', 'referencias.json'), 'utf8'));

servidor.listen(0, '127.0.0.1', async () => {
  const base = `http://127.0.0.1:${servidor.address().port}`;
  const URLS = [1, 2, 3, 4].map((n) => `${base}/${n}`);
  const cap = (proj, extra, ...urls) => rodar([path.join(AQUI, 'capturar-referencias.mjs'), '--projeto', proj, '--tipo', 'design', '--minimo', '1', ...extra, ...urls]);

  // 1. paralelo: 2 por vez
  const pPar = pasta();
  emVoo = 0; maxEmVoo = 0;
  const par = await cap(pPar, [], ...URLS);
  checa('em paralelo: a captura sai 0', par.status === 0, (par.stderr || '').split('\n')[0]);
  checa('em paralelo: dois endereços ao mesmo tempo, nunca três', maxEmVoo === 2, `no máximo ${maxEmVoo} ao mesmo tempo`);

  // 2. mesmo resultado da fila, mesma ordem do pedido (o 1º endereço é o mais lento)
  const mPar = manifesto(pPar);
  checa('as entradas do manifesto seguem a ORDEM DO PEDIDO, mesmo com o 1º terminando depois', mPar.referencias.map((r) => r.url).join(' ') === URLS.join(' '), mPar.referencias.map((r) => r.url.split('/').pop()).join(','));
  const prefixos = mPar.referencias.map((r) => path.basename(r.prints.dobra).split('-')[0]);
  checa('os números dos prints seguem o pedido: 01, 02, 03, 04', prefixos.join(',') === '01,02,03,04', prefixos.join(','));
  checa('os 8 PNG existem e a pasta não tem print repetido nem faltando', fs.readdirSync(path.join(pPar, 'referencias')).filter((n) => n.endsWith('.png')).length === 8);
  checa('todos ok, com dobra e meio diferentes', mPar.referencias.every((r) => r.captura.estado === 'ok' && !fs.readFileSync(path.join(pPar, r.prints.dobra)).equals(fs.readFileSync(path.join(pPar, r.prints.meio)))));

  // 3. a saída vem na ordem do pedido
  const linhas = par.stdout.split('\n');
  const posicao = URLS.map((u) => linhas.findIndex((l) => l.includes(u)));
  checa('a saída lista os endereços na ordem do pedido', posicao.every((p, i) => p >= 0 && (i === 0 || p > posicao[i - 1])), posicao.join(','));

  // 6. em fila: mesmo resultado, 1 por vez
  const pSer = pasta();
  emVoo = 0; maxEmVoo = 0;
  const ser = await cap(pSer, ['--em-serie'], ...URLS);
  const mSer = manifesto(pSer);
  checa('--em-serie: um endereço por vez', maxEmVoo === 1, `no máximo ${maxEmVoo}`);
  const resumo = (m) => m.referencias.map((r) => [r.url.split('/').pop(), r.captura.estado, path.basename(r.prints.dobra), path.basename(r.prints.meio), r.titulo, r.altura_pagina].join('|')).join('\n');
  checa('o paralelo e a fila dão o mesmo manifesto (url, estado, nome dos prints, título, altura)', resumo(mPar) === resumo(mSer), `\n${resumo(mPar)}\n---\n${resumo(mSer)}`);

  // 7. mais rápido
  checa('em paralelo é mais rápido que em fila', par.segundos < ser.segundos * 0.85, `${par.segundos.toFixed(1)} s contra ${ser.segundos.toFixed(1)} s`);

  // 4. um endereço que falha não derruba os outros
  const pFalha = pasta();
  const comFalha = await cap(pFalha, [], URLS[0], 'http://127.0.0.1:1/morto', URLS[1], URLS[2]);
  const mFalha = manifesto(pFalha);
  checa('endereço morto falha sozinho: os outros 3 foram capturados', mFalha.referencias.length === 3 && mFalha.referencias.every((r) => r.captura.estado === 'ok'), String(mFalha.referencias.length));
  checa('a saída diz qual endereço falhou', /FALHA http:\/\/127\.0\.0\.1:1\/morto/.test(comFalha.stdout + comFalha.stderr));
  checa('o resumo conta 3 de 4', /3 de 4 capturada/.test(comFalha.stdout), comFalha.stdout.split('\n').find((l) => /capturada/.test(l)) || '');

  // 5. endereço repetido
  const pRep = pasta();
  const rep = await cap(pRep, [], URLS[1], URLS[1] + '/', URLS[2]);
  const mRep = manifesto(pRep);
  checa('endereço repetido no mesmo pedido (com e sem barra no fim) é capturado uma vez', rep.status === 0 && mRep.referencias.length === 2, String(mRep.referencias.length));

  // recaptura: a mesma URL regrava os mesmos arquivos, sem duplicar a entrada (comportamento de sempre)
  const antes = fs.readdirSync(path.join(pPar, 'referencias')).filter((n) => n.endsWith('.png')).sort().join(',');
  await cap(pPar, [], URLS[2], `${base}/5`);
  const mDepois = manifesto(pPar);
  checa('recapturar uma URL e acrescentar outra: 5 entradas, a nova com o próximo número livre', mDepois.referencias.length === 5 && path.basename(mDepois.referencias[4].prints.dobra).startsWith('05-'), mDepois.referencias.map((r) => path.basename(r.prints.dobra).slice(0, 2)).join(','));
  checa('a recaptura regravou os mesmos arquivos (nenhum print novo para a URL 3)', fs.readdirSync(path.join(pPar, 'referencias')).filter((n) => n.endsWith('.png')).sort().join(',').startsWith(antes.split(',').slice(0, 6).join(',')));

  servidor.close();
  console.log(falhas ? `\n  ${falhas} falha(s).\n` : '\n  Captura em paralelo confiável.\n');
  process.exit(falhas ? 1 : 0);
});
