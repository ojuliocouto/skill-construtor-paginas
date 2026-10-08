/**
 * Parte pura do gravador de vídeo de prova (scripts/video/roteiro.cjs e scripts/video/duracao-webm.cjs):
 * validação do roteiro, montagem dos passos, nomes de arquivo e leitura da duração de um WebM.
 * Uso: node scripts/test-roteiro-de-video.cjs
 */
const assert = require('node:assert/strict');
const path = require('node:path');

let falhas = 0;
function teste(nome, fn) {
  try { fn(); console.log(`ok    ${nome}`); } catch (e) { falhas++; console.log(`FALHA ${nome} -> ${String(e.message).split('\n')[0]}`); }
}

const roteiro = require('./video/roteiro.cjs');
const webm = require('./video/duracao-webm.cjs');
const padrao = require('./roteiro-pagina.json');

const seis = (extra = []) => [
  { acao: 'abrir' }, { acao: 'esperar', ms: 3000 },
  ...[1, 2, 3, 4, 5, 6].flatMap((n) => [{ acao: 'print', nome: `quadro ${n}` }, { acao: 'esperar', ms: 1500 }]),
  ...extra,
];

teste('roteiro da página é válido, e o fixo mais o pior caso da rolagem cabe em 10 a 90 s', () => {
  const v = roteiro.validarRoteiro(padrao);
  assert.deepEqual(v.erros, []);
  const fixo = roteiro.duracaoPrevistaMs(padrao.passos) / 1000;
  const pior = fixo + roteiro.duracaoMaximaDaRolagemMs(padrao.passos) / 1000;
  assert.ok(fixo >= 3 && pior <= 90, `fixo ${fixo} s, pior caso ${pior} s`);
});

teste('roteiro do demo (painel de cor): válido, com clique no [data-painel] e ao menos 6 prints', () => {
  const demo = require('./roteiro-demo-receitas.json');
  assert.deepEqual(roteiro.validarRoteiro(demo).erros, []);
  assert.ok(demo.passos.some((p) => p.acao === 'clicar' && /data-painel/.test(p.seletor)), 'sem o clique no link com painel');
  assert.ok(demo.passos.filter((p) => p.acao === 'print' && /painel cobrindo/.test(p.nome)).length === 1, 'sem o quadro do painel cobrindo a tela');
});

teste('N20: o validador lista TODOS os limites quebrados de uma vez (passo e duração juntos)', () => {
  const v = roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, { acao: 'rolar_pagina', max_passos: 60, espera_ms: 3000, prints: 9 }], duracao_minima_s: 30 });
  const texto = v.erros.join(' | ');
  assert.match(texto, /max_passos/); assert.match(texto, /prints/);
  assert.match(texto, /duracao_minima_s/);
  assert.match(texto, /duração prevista/);
});

teste('N20: roteiro bom continua passando, e o ruim original (rolagem sem fim e fora da faixa) continua reprovado', () => {
  const v = roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, ...[1, 2, 3, 4, 5, 6].map((n) => ({ acao: 'print', nome: 'q' + n })), { acao: 'rolar_pagina', max_passos: 45, espera_ms: 3000 }] });
  assert.match(v.erros.join(), /duração prevista/);
  assert.equal(v.ok, false);
});

teste('N20: a mensagem de erro do roteiro cita os limites que valem (para o aluno acertar na primeira)', () => {
  const v = roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, { acao: 'esperar', ms: 99999 }] });
  assert.match(v.erros.join(), /0 a 10000/);
  assert.match(roteiro.limitesEmTexto(), /1 a 45/); assert.match(roteiro.limitesEmTexto(), /10 a 90/); assert.match(roteiro.limitesEmTexto(), /300 a 3000/);
});

teste('a faixa desta skill é de 10 a 90 s (a do criador-dash era de 10 a 15)', () => {
  assert.deepEqual(roteiro.FAIXA_S, { min: 10, max: 90 });
});

teste('rolar_pagina: o roteiro da página usa o ritmo de leitura (meia janela a cada 1,5 s, cerca de 300 px/s)', () => {
  const r = padrao.passos.find((p) => p.acao === 'rolar_pagina');
  assert.ok(r, 'sem rolar_pagina');
  const c = roteiro.configDeRolarPagina(r);
  const pxPorS = (900 * c.passo) / ((c.espera_ms) / 1000);
  assert.ok(pxPorS >= 200 && pxPorS <= 400, `${pxPorS} px/s em 1440x900`);
});

teste('rolar_pagina: cobra passo, espera, máximo e prints dentro dos limites', () => {
  const erros = (p) => roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, ...[1, 2, 3, 4, 5, 6].map((n) => ({ acao: 'print', nome: 'q' + n })), p] }).erros.join();
  assert.equal(erros({ acao: 'rolar_pagina' }), '');
  assert.match(erros({ acao: 'rolar_pagina', passo: 0.05 }), /passo/);
  assert.match(erros({ acao: 'rolar_pagina', passo: 2 }), /passo/);
  assert.match(erros({ acao: 'rolar_pagina', espera_ms: 100 }), /espera_ms/);
  assert.match(erros({ acao: 'rolar_pagina', max_passos: 0 }), /max_passos/);
  assert.match(erros({ acao: 'rolar_pagina', max_passos: 500 }), /max_passos/);
  assert.match(erros({ acao: 'rolar_pagina', prints: 9 }), /prints/);
});

teste('rolar_pagina: o pior caso acima de 90 s é recusado', () => {
  const r = { passos: [{ acao: 'abrir' }, { acao: 'rolar_pagina', espera_ms: 3000, max_passos: 45, prints: 6 }] };
  assert.match(roteiro.validarRoteiro(r).erros.join(), /duração|segundos/);
});

teste('rolar_pagina conta os prints que ela mesma tira', () => {
  const r = { passos: [{ acao: 'abrir' }, { acao: 'rolar_pagina', prints: 6 }] };
  assert.equal(roteiro.validarRoteiro(r).erros.filter((e) => /prints/.test(e)).length, 0);
  const s = { passos: [{ acao: 'abrir' }, { acao: 'rolar_pagina', prints: 2 }] };
  assert.match(roteiro.validarRoteiro(s).erros.join(), /6 prints/);
});

teste('o roteiro padrão tem no mínimo 6 prints (a prancha de quadros)', () => {
  const total = padrao.passos.reduce((n, p) => n + (p.acao === 'print' ? 1 : 0) + (p.acao === 'rolar_pagina' ? p.prints || 0 : 0), 0);
  assert.ok(total >= 6, `${total} prints`);
});

teste('roteiro sem passos, sem abrir no começo ou com ação desconhecida é recusado', () => {
  assert.ok(roteiro.validarRoteiro({ passos: [] }).erros.length);
  assert.ok(roteiro.validarRoteiro({}).erros.length);
  assert.match(roteiro.validarRoteiro({ passos: [{ acao: 'esperar', ms: 100 }] }).erros.join(), /abrir/);
  assert.match(roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, { acao: 'voar' }] }).erros.join(), /voar/);
});

teste('cada ação cobra os seus campos', () => {
  const erros = (p) => roteiro.validarRoteiro({ passos: [{ acao: 'abrir' }, p] }).erros.join();
  assert.match(erros({ acao: 'clicar' }), /seletor/);
  assert.match(erros({ acao: 'esperar' }), /ms/);
  assert.match(erros({ acao: 'esperar', ms: -5 }), /ms/);
  assert.match(erros({ acao: 'esperar', ms: 999999 }), /ms/);
  assert.match(erros({ acao: 'rolar' }), /y/);
  assert.match(erros({ acao: 'mover_mouse' }), /seletor|x/);
  assert.match(erros({ acao: 'escolher', seletor: 'select' }), /indice|valor/);
  assert.match(erros({ acao: 'print' }), /nome/);
  assert.match(erros({ acao: 'esperar_seletor' }), /seletor/);
});

teste('roteiro com menos de 6 prints é recusado', () => {
  const r = { passos: [{ acao: 'abrir' }, { acao: 'esperar', ms: 10000 }, { acao: 'print', nome: 'a' }] };
  assert.match(roteiro.validarRoteiro(r).erros.join(), /6 prints/);
});

teste('duração prevista fora de 10 a 90 s é recusada', () => {
  const curto = { passos: [{ acao: 'abrir' }, ...[1, 2, 3, 4, 5, 6].map((n) => ({ acao: 'print', nome: 'q' + n }))] };
  assert.match(roteiro.validarRoteiro(curto).erros.join(), /duração|segundos/);
  const longo = { passos: [...seis(), ...Array(12).fill({ acao: 'esperar', ms: 9000 })] };
  assert.match(roteiro.validarRoteiro(longo).erros.join(), /duração|segundos/);
});

teste('duracao_minima_s: aceita de 10 a 15 e recusa o resto', () => {
  const com = (v) => roteiro.validarRoteiro({ ...padrao, duracao_minima_s: v }).erros.join();
  assert.equal(com(11), '');
  assert.match(com(3), /duracao_minima_s/);
  assert.match(com(40), /duracao_minima_s/);
  assert.match(com('onze'), /duracao_minima_s/);
});

teste('montarPassos: preenche padrões e não muda o roteiro original', () => {
  const original = { passos: [{ acao: 'abrir' }, { acao: 'clicar', seletor: '.x', opcional: true }, { acao: 'rolar', y: 300 }] };
  const copia = JSON.stringify(original);
  const passos = roteiro.montarPassos(original);
  assert.equal(passos.length, 3);
  assert.equal(passos[0].opcional, false);
  assert.equal(passos[1].opcional, true);
  assert.equal(passos[0].ordem, 1);
  assert.equal(JSON.stringify(original), copia);
});

teste('perfis: desktop 1440x900 e celular 390x844', () => {
  assert.deepEqual(roteiro.PERFIS.desktop.viewport, { width: 1440, height: 900 });
  assert.deepEqual(roteiro.PERFIS.mobile.viewport, { width: 390, height: 844 });
  assert.equal(roteiro.PERFIS.mobile.isMobile, true);
});

teste('nomes de arquivo: sem espaço, sem acento, sem barra, numerados', () => {
  assert.equal(roteiro.nomeDoVideo('desktop'), 'video-desktop.webm');
  assert.equal(roteiro.nomeDoVideo('mobile'), 'video-mobile.webm');
  assert.equal(roteiro.nomeDoPrint('desktop', 3, 'Aba Evolução / filtro'), 'desktop-03-aba-evolucao-filtro.png');
  assert.equal(roteiro.nomeDoPrint('mobile', 12, '   '), 'mobile-12-quadro.png');
  assert.ok(!/[\\/:\s]/.test(roteiro.nomeDoPrint('mobile', 1, '../../etc')));
  assert.throws(() => roteiro.nomeDoVideo('tablet'));
});

teste('pasta de saída: só junta nomes, funciona com espaço e acento', () => {
  const pasta = path.join('saída com espaço', 'é');
  assert.equal(roteiro.caminhoDeSaida(pasta, 'video-desktop.webm'), path.join(pasta, 'video-desktop.webm'));
});

// ---- duração de WebM (EBML) ----
function vint(n) { // tamanho EBML de 4 bytes
  return Buffer.from([0x10 | ((n >> 24) & 0x0f), (n >> 16) & 255, (n >> 8) & 255, n & 255]);
}
function el(idHex, corpo) { return Buffer.concat([Buffer.from(idHex, 'hex'), vint(corpo.length), corpo]); }
function cluster(tempoMs, blocosMs) {
  const tc = el('e7', Buffer.from([(tempoMs >> 8) & 255, tempoMs & 255]));
  const blocos = blocosMs.map((rel) => el('a3', Buffer.from([0x81, (rel >> 8) & 255, rel & 255, 0x80, 1, 2, 3])));
  return el('1f43b675', Buffer.concat([tc, ...blocos]));
}
function arquivoFalso(clusters, tamanhoDesconhecido) {
  const cab = el('1a45dfa3', el('4282', Buffer.from('webm')));
  const corpo = Buffer.concat(clusters);
  const seg = tamanhoDesconhecido
    ? Buffer.concat([Buffer.from('18538067', 'hex'), Buffer.from('01ffffffffffffff', 'hex'), corpo])
    : el('18538067', corpo);
  return Buffer.concat([cab, seg]);
}

teste('duracaoDoWebm: soma o tempo do último cluster com o do último bloco', () => {
  const buf = arquivoFalso([cluster(0, [0, 40, 80]), cluster(5000, [0, 40]), cluster(10000, [0, 40, 480])], false);
  assert.equal(webm.duracaoDoWebm(buf), 10480);
});

teste('duracaoDoWebm: aceita o Segment de tamanho desconhecido (gravação ao vivo)', () => {
  const buf = arquivoFalso([cluster(0, [0, 40]), cluster(7000, [0, 960])], true);
  assert.equal(webm.duracaoDoWebm(buf), 7960);
});

teste('duracaoDoWebm: lixo ou arquivo vazio devolve null, nunca inventa número', () => {
  assert.equal(webm.duracaoDoWebm(Buffer.alloc(0)), null);
  assert.equal(webm.duracaoDoWebm(Buffer.from('isto não é um vídeo')), null);
  assert.equal(webm.duracaoDoWebm(arquivoFalso([], false)), null);
});

process.exitCode = falhas ? 1 : 0;
console.log(falhas ? `\n${falhas} falha(s)` : '\nTudo verde.');
