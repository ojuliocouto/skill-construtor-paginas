// Testes do baixar-fontes.mjs (achado A24) com a resposta do Google Fonts GRAVADA: a suíte não depende de internet.
// Rodar: node --test scripts/baixar-fontes.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { baixar, blocosLatinos, montarUrl } from './baixar-fontes.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const css = (n) => fs.readFileSync(path.join(AQUI, 'fixtures', 'fontes', n), 'utf8');
// Família SEM eixo de peso, escrita à mão no formato do Google (um arquivo por peso): o caso estático.
const bloco = (peso) => `/* latin-ext */\n@font-face {\n  font-family: 'Lora';\n  font-style: normal;\n  font-weight: ${peso};\n  src: url(https://fonts.gstatic.com/s/lora/x/ext${peso}.woff2) format('woff2');\n  unicode-range: U+0100-02BA;\n}\n/* latin */\n@font-face {\n  font-family: 'Lora';\n  font-style: normal;\n  font-weight: ${peso};\n  src: url(https://fonts.gstatic.com/s/lora/x/lat${peso}.woff2) format('woff2');\n  unicode-range: U+0000-00FF, U+0131;\n}\n`;
const ESTATICA = bloco(400) + bloco(700);
const WOFF2 = Buffer.concat([Buffer.from('wOF2'), Buffer.alloc(60, 1)]);

/** Rede simulada: o CSS conforme a URL pedida; qualquer .woff2 devolve bytes falsos. */
function rede({ variavelRecusada = false, status = 200, quebra = false } = {}) {
  const chamadas = [];
  const buscar = async (url, op = {}) => {
    chamadas.push(url);
    if (quebra) throw new Error('getaddrinfo ENOTFOUND fonts.googleapis.com');
    if (url.endsWith('.woff2')) return { status: 200, bytes: WOFF2 };
    if (status !== 200) return { status, texto: '' };
    if (url.includes('family=Figtree')) return { status: 200, texto: css('figtree-variavel.css') };
    if (url.includes('family=Bricolage')) return { status: 200, texto: css('bricolage-estatico.css') };
    if (url.includes('family=Lora')) return variavelRecusada && url.includes('..') ? { status: 400, texto: '' } : { status: 200, texto: ESTATICA };
    return { status: 400, texto: '' };
  };
  return { buscar, chamadas };
}
const pasta = () => fs.mkdtempSync(path.join(os.tmpdir(), 'fontes-'));

test('montarUrl: variável vira faixa e estática vira lista', () => {
  assert.match(montarUrl('Figtree', [300, 900], true), /family=Figtree:wght@300\.\.900&display=swap$/);
  assert.match(montarUrl('Bricolage Grotesque', [700, 400], false), /family=Bricolage\+Grotesque:wght@400;700&/);
});

test('blocosLatinos ignora o latin-ext e os outros alfabetos', () => {
  const b = blocosLatinos(css('lora-estatico.css'));
  assert.ok(b.length >= 1 && b.every((x) => /woff2$/.test(x.url)));
  assert.ok(b.every((x) => x.faixa.startsWith('U+0000-00FF')), 'só o subconjunto latino básico');
});

test('variável quando existe: um arquivo, font-weight em faixa e o caminho relativo no url()', async () => {
  const saida = pasta();
  const r = await baixar({ familia: 'Figtree', pesos: [300, 900], saida, prefixo: 'fonts/', buscar: rede().buscar });
  assert.equal(r.variavel, true);
  assert.deepEqual(r.arquivos.map((a) => a.arquivo), ['figtree-variavel.woff2']);
  assert.ok(fs.existsSync(path.join(saida, 'figtree-variavel.woff2')));
  assert.match(r.fontFace, /font-family: 'Figtree';/);
  assert.match(r.fontFace, /font-weight: 300 900;/);
  assert.match(r.fontFace, /font-display: swap;/);
  assert.match(r.fontFace, /url\('fonts\/figtree-variavel\.woff2'\) format\('woff2'\)/);
  assert.match(r.fontFace, /unicode-range: U\+0000-00FF/);
});

test('mesmo arquivo para dois pesos vira UM arquivo e uma faixa (Bricolage é variável)', async () => {
  const r = await baixar({ familia: 'Bricolage Grotesque', pesos: [400, 700], saida: pasta(), buscar: rede().buscar });
  assert.equal(r.arquivos.length, 1);
  assert.match(r.fontFace, /font-weight: 400 700;/);
});

test('família sem eixo de peso: o Google recusa a faixa (400) e o script cai nos pesos estáticos', async () => {
  const { buscar, chamadas } = rede({ variavelRecusada: true });
  const saida = pasta();
  const r = await baixar({ familia: 'Lora', pesos: [400, 700], saida, buscar });
  assert.equal(r.variavel, false);
  assert.ok(chamadas.some((u) => u.includes('wght@400..700')), 'tentou a variável antes');
  assert.ok(chamadas.some((u) => u.includes('wght@400;700')), 'caiu nos estáticos');
  assert.deepEqual(r.arquivos.map((a) => a.arquivo).sort(), ['lora-400.woff2', 'lora-700.woff2']);
  assert.equal((r.fontFace.match(/@font-face/g) || []).length, 2);
});

test('--so-estatica não tenta a variável', async () => {
  const { buscar, chamadas } = rede();
  await baixar({ familia: 'Lora', pesos: [400, 700], saida: pasta(), soEstatica: true, buscar });
  assert.ok(!chamadas.some((u) => u.includes('..')));
});

test('rede caída: mensagem clara e nada gravado pela metade', async () => {
  const saida = path.join(pasta(), 'fonts');
  await assert.rejects(baixar({ familia: 'Figtree', pesos: [300, 900], saida, buscar: rede({ quebra: true }).buscar }),
    /sem conexão com fonts\.googleapis\.com .*Verifique a internet ou o proxy/);
  assert.ok(!fs.existsSync(saida), 'a pasta nem foi criada');
});

test('arquivo de fonte que cai no meio: nada fica gravado', async () => {
  const saida = path.join(pasta(), 'fonts');
  const base = rede();
  const buscar = async (url, op) => (url.endsWith('.woff2') ? { status: 503, bytes: null } : base.buscar(url, op));
  await assert.rejects(baixar({ familia: 'Lora', pesos: [400, 700], saida, buscar }), /não baixou \(HTTP 503\)/);
  assert.ok(!fs.existsSync(saida));
});

test('família que não existe: HTTP 400 vira mensagem com o nome', async () => {
  await assert.rejects(baixar({ familia: 'Fonte Que Nao Existe', pesos: [400], saida: pasta(), buscar: rede().buscar }),
    /respondeu HTTP 400 para "Fonte Que Nao Existe"/);
});

test('pesos inválidos e família vazia são recusados antes de ir à rede', async () => {
  await assert.rejects(baixar({ familia: '', pesos: [400], saida: pasta(), buscar: rede().buscar }), /informe --familia e --pesos/);
  await assert.rejects(baixar({ familia: 'Lora', pesos: [NaN], saida: pasta(), buscar: rede().buscar }), /informe --familia e --pesos/);
});
