#!/usr/bin/env node
/**
 * GATE DE FIDELIDADE (3.7.0, só no caminho CLONAR): o clone medido contra a original, nas duas larguras.
 *
 * Por que existe. No teste de aluno do CLONAR na 3.6.3 o passo 4 do clonar.md mandava "olhar a imagem e conferir cor a cor", e o
 * lado-a-lado saía reduzido e sem diff. Quem achou os 5 defeitos reais da volta 1 (herói 708 contra 723 px, margem 60 contra 45,
 * bolinhas nos logos, círculo nos ícones, pontos de quebra) e os 3 da volta 2 (ícones 10% maiores, cor do placeholder, peso do
 * rodapé) foram o `medir.mjs` e o `comparar.py` que o aluno escreveu à mão. Este gate é a versão deles na skill, sem dado do site.
 *
 * O que mede, em 1440x900 e 390x844 (celular), na original e no clone, com a mesma espera e a mesma rolagem:
 *   1. a altura da página;
 *   2. os elementos-chave (títulos, parágrafos, links, botões, itens de lista, imagens, campos, cabeçalho, seções e rodapé),
 *      pareados pelo que são (tag e texto, ou o nome do arquivo da imagem), com a caixa e o estilo que se vê;
 *   3. o diff de pixels da página inteira, e os retângulos onde ele está, cada um com o elemento da original que ele cobre.
 * Grava em <projeto>/gates/fidelidade/ (ou --saida): original-<w>.png, clone-<w>.png, diff-<w>.png (as diferenças em vermelho sobre o
 * clone, em tamanho real), lado-<w>.png (original e clone lado a lado, sem redução) e laudo.json.
 *
 * Reprova (saída 1) quando, em qualquer largura: a altura difere mais de 4 px, mais de 1% dos pixels difere, um elemento da original
 * não tem par no clone, ou um par tem caixa (mais de 3 px) ou estilo diferente. Os limites mudam com --limite-pixels, --limite-altura e
 * --limite-caixa; diferença declarada no delta (interação que não se clona) não se esconde aqui: vai na entrega.
 * A página que não abre no navegador é ERRO DE FERRAMENTA (saída 3), nunca defeito da página.
 *
 * Uso:
 *   node scripts/gate-fidelidade.mjs --url <clone servido> [--original <url>] [--projeto <dir>] [--saida <dir>]
 *        [--larguras 1440,390] [--limite-pixels 1] [--limite-altura 4] [--limite-caixa 3] [--sem-registrar-uso]
 * Sem --original, a URL vem de <projeto>/original/identidade.json (campo url, a saída do extrai-identidade.mjs) ou de
 * <projeto>/original/url.txt. Com --projeto, o uso do Playwright fica registrado no uso-ferramentas.py (a evidência é o print do clone).
 */
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { LIMITES, compararElementos, dentroDe, falhasDaLargura, fmtPct, retangulos, rotulo } from './fidelidade-lib.mjs';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); } catch {
      console.error('ERRO DE FERRAMENTA: playwright não encontrado (npm i -g playwright && npx playwright install chromium)');
      process.exit(3);
    }
  }
}

const args = process.argv.slice(2);
const pega = (n, padrao = null) => { const i = args.indexOf(n); return i >= 0 && i + 1 < args.length ? args[i + 1] : padrao; };
const tem = (n) => args.includes(n);
const URL_CLONE = pega('--url');
const PROJETO = pega('--projeto') ? path.resolve(pega('--projeto')) : null;
const lim = {
  ...LIMITES,
  pixelsPct: Number(pega('--limite-pixels', LIMITES.pixelsPct)),
  alturaPx: Number(pega('--limite-altura', LIMITES.alturaPx)),
  caixaPx: Number(pega('--limite-caixa', LIMITES.caixaPx)),
};
const LARGURAS = String(pega('--larguras', '1440,390')).split(',').map((s) => Number(s.trim())).filter(Boolean);

function urlDaOriginal() {
  if (pega('--original')) return pega('--original');
  if (!PROJETO) return null;
  try { const j = JSON.parse(readFileSync(path.join(PROJETO, 'original', 'identidade.json'), 'utf8')); if (j && j.url) return j.url; } catch (_) { /* tenta o url.txt */ }
  try { const t = readFileSync(path.join(PROJETO, 'original', 'url.txt'), 'utf8').trim(); if (t) return t; } catch (_) { /* sem url */ }
  return null;
}
const URL_ORIGINAL = urlDaOriginal();
if (!URL_CLONE || !URL_ORIGINAL) {
  console.error('uso: node gate-fidelidade.mjs --url <clone servido> --original <url da original> [--projeto <dir>]');
  if (URL_CLONE && !URL_ORIGINAL) console.error('Faltou a original: passe --original <url>, ou grave a saída do extrai-identidade.mjs em <projeto>/original/identidade.json (ou a URL em <projeto>/original/url.txt).');
  process.exit(2);
}
const SAIDA = path.resolve(pega('--saida') || (PROJETO ? path.join(PROJETO, 'gates', 'fidelidade') : 'fidelidade'));
mkdirSync(SAIDA, { recursive: true });

class ErroDeFerramenta extends Error {}

/** Abre a página com uma nova tentativa; falhou duas vezes, é erro de ferramenta. */
async function abrir(page, url) {
  let ultimo = null;
  for (let t = 0; t < 2; t++) {
    try { await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }); return; } catch (e) {
      ultimo = e;
      try { await page.goto(url, { waitUntil: 'load', timeout: 45000 }); return; } catch (e2) { ultimo = e2; }
    }
    await page.waitForTimeout(500);
  }
  throw new ErroDeFerramenta(String(ultimo && ultimo.message || ultimo).split('\n')[0]);
}

/** Rola a página inteira (acorda imagem preguiçosa e revelação por rolagem), volta ao topo e espera fontes e imagens. */
async function estabilizar(page) {
  await page.evaluate(async () => {
    const alto = () => document.documentElement.scrollHeight;
    for (let y = 0; y < alto(); y += Math.max(200, Math.floor(innerHeight * 0.6))) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
    scrollTo(0, alto()); await new Promise((r) => setTimeout(r, 200));
    scrollTo(0, 0);
    try { await document.fonts.ready; } catch (_) { /* sem API de fontes */ }
    await Promise.all([...document.images].map((im) => (im.complete ? null : new Promise((r) => { im.onload = im.onerror = r; setTimeout(r, 4000); }))));
  });
  await page.waitForTimeout(700);
}

/** Os elementos-chave visíveis, com caixa absoluta e estilo computado. Nada do site: só tags. */
function medirNaPagina(props) {
  const SEL = 'h1,h2,h3,h4,h5,h6,p,a,button,li,img,input,textarea,select,label,blockquote,figcaption,header,footer,nav,main,section';
  const out = [];
  for (const el of document.querySelectorAll(SEL)) {
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || Number(cs.opacity) === 0) continue;
    const estilo = {};
    for (const p of props) estilo[p] = cs[p];
    const tag = el.tagName.toLowerCase();
    out.push({
      tag,
      texto: tag === 'img' ? (el.getAttribute('alt') || '') : (el.innerText || el.value || el.getAttribute('placeholder') || el.getAttribute('aria-label') || '').slice(0, 120),
      visivel: tag === 'img' ? '' : (el.innerText || '').slice(0, 120),
      src: tag === 'img' ? (el.currentSrc || el.src || '') : '',
      rect: [r.x + scrollX, r.y + scrollY, r.width, r.height].map((v) => Math.round(v * 10) / 10),
      estilo,
    });
    if (out.length >= 600) break;
  }
  return { elementos: out, altura: document.documentElement.scrollHeight };
}

/** Diff no próprio navegador (canvas): sem Pillow nem pacote de PNG. Devolve a porcentagem, a grade de células e as imagens novas. */
async function diffDePixels(page, pngA, pngB, celula = 8) {
  return page.evaluate(async ([a, b, celula]) => {
    const carregar = (b64) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = `data:image/png;base64,${b64}`; });
    const [ia, ib] = await Promise.all([carregar(a), carregar(b)]);
    const w = Math.max(ia.width, ib.width), h = Math.max(ia.height, ib.height);
    const pegar = (im) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, w, h); x.drawImage(im, 0, 0); return x.getImageData(0, 0, w, h).data; };
    const da = pegar(ia), db = pegar(ib);
    const colunas = Math.ceil(w / celula), linhas = Math.ceil(h / celula);
    const mascara = new Uint8Array(colunas * linhas);
    const saida = document.createElement('canvas'); saida.width = w; saida.height = h;
    const sx = saida.getContext('2d'); sx.drawImage(ib, 0, 0); sx.fillStyle = 'rgba(255,255,255,0.65)'; sx.fillRect(0, 0, w, h);
    const marca = sx.getImageData(0, 0, w, h);
    let dif = 0;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      const fora = x >= Math.min(ia.width, ib.width) || y >= Math.min(ia.height, ib.height);
      if (fora || Math.abs(da[i] - db[i]) + Math.abs(da[i + 1] - db[i + 1]) + Math.abs(da[i + 2] - db[i + 2]) > 30) {
        dif++; mascara[Math.floor(y / celula) * colunas + Math.floor(x / celula)] = 1;
        marca.data[i] = 230; marca.data[i + 1] = 0; marca.data[i + 2] = 0; marca.data[i + 3] = 255;
      }
    }
    sx.putImageData(marca, 0, 0);
    const lado = document.createElement('canvas'); lado.width = ia.width + ib.width + 24; lado.height = h;
    const lx = lado.getContext('2d'); lx.fillStyle = '#888'; lx.fillRect(0, 0, lado.width, h); lx.drawImage(ia, 0, 0); lx.drawImage(ib, ia.width + 24, 0);
    return { pct: (dif / (w * h)) * 100, colunas, linhas, mascara: Array.from(mascara), diff: saida.toDataURL('image/png').split(',')[1], lado: lado.toDataURL('image/png').split(',')[1] };
  }, [pngA.toString('base64'), pngB.toString('base64'), celula]);
}

async function medirLargura(navegador, largura, PROPS) {
  const mob = largura < 768;
  const altura = mob ? 844 : 900;
  const um = async (url, quem) => {
    const ctx = await navegador.newContext({ viewport: { width: largura, height: altura }, deviceScaleFactor: 1, isMobile: mob, hasTouch: mob, reducedMotion: 'no-preference' });
    const page = await ctx.newPage();
    try {
      await abrir(page, url);
      await estabilizar(page);
      const medida = await page.evaluate(medirNaPagina, PROPS);
      const png = await page.screenshot({ fullPage: true, animations: 'disabled', caret: 'hide' });
      writeFileSync(path.join(SAIDA, `${quem}-${largura}.png`), png);
      return { ...medida, png };
    } finally { await ctx.close(); }
  };
  const [o, c] = await Promise.all([um(URL_ORIGINAL, 'original'), um(URL_CLONE, 'clone')]);
  const ctx = await navegador.newContext({ viewport: { width: 800, height: 600 } });
  const page = await ctx.newPage();
  const d = await diffDePixels(page, o.png, c.png);
  await ctx.close();
  writeFileSync(path.join(SAIDA, `diff-${largura}.png`), Buffer.from(d.diff, 'base64'));
  writeFileSync(path.join(SAIDA, `lado-${largura}.png`), Buffer.from(d.lado, 'base64'));
  // A caixa "tem pixel diferente" quando pelo menos 2 células e 2% das células dela diferem: um olho que segue o mouse num canto
  // de um botão grande não faz do fundo calculado do botão uma diferença que se vê.
  const temPixel = ([x, y, w, h]) => {
    let n = 0, total = 0;
    for (let cy = Math.max(0, Math.floor(y / 8)); cy <= Math.min(d.linhas - 1, Math.floor((y + h) / 8)); cy++)
      for (let cx = Math.max(0, Math.floor(x / 8)); cx <= Math.min(d.colunas - 1, Math.floor((x + w) / 8)); cx++) { total++; if (d.mascara[cy * d.colunas + cx]) n++; }
    return n >= 2 && n >= total * 0.02;
  };
  const caixas = retangulos(d.mascara, d.colunas, d.linhas, 8).map((r) => ({ ...r, dentro: (() => { const e = dentroDe(r, o.elementos); return e ? rotulo(e) : 'fora dos elementos medidos'; })() }));
  return { largura, alturaOriginal: o.altura, alturaClone: c.altura, pixelsPct: d.pct, comparacao: compararElementos(o.elementos, c.elementos, lim, temPixel), medidosOriginal: o.elementos.length, medidosClone: c.elementos.length, retangulos: caixas };
}

async function principal() {
  const { PROPS } = await import('./fidelidade-lib.mjs');
  const { chromium } = carregarPlaywright();
  const navegador = await chromium.launch();
  const linhas = ['GATE DE FIDELIDADE', `original: ${URL_ORIGINAL}`, `clone:    ${URL_CLONE}`, '='.repeat(88)];
  const falhas = [];
  const laudo = { original: URL_ORIGINAL, clone: URL_CLONE, limites: lim, larguras: [] };
  try {
    for (const w of LARGURAS) {
      const m = await medirLargura(navegador, w, PROPS);
      laudo.larguras.push({ ...m, comparacao: m.comparacao });
      const nome = `${w} px`;
      linhas.push('', `${nome}: altura ${m.alturaOriginal} contra ${m.alturaClone} px; ${fmtPct(m.pixelsPct)} dos pixels diferentes; ${m.comparacao.pares} de ${m.medidosOriginal} elementos pareados`);
      const vistas = m.comparacao.diferencas.filter((d) => !d.invisivel), invisiveis = m.comparacao.diferencas.filter((d) => d.invisivel);
      for (const d of vistas.slice(0, 15)) linhas.push(`  DIFERE   ${d.rotulo} (y ${Math.round(d.y)}): ${d.itens.join('; ')}`);
      if (vistas.length > 15) linhas.push(`  (mais ${vistas.length - 15} no laudo.json)`);
      for (const d of invisiveis.slice(0, 6)) linhas.push(`  AVISO    ${d.rotulo} (y ${Math.round(d.y)}): ${d.itens.join('; ')} (nenhum pixel diferente na caixa: não se vê, não reprova)`);
      if (invisiveis.length > 6) linhas.push(`  (mais ${invisiveis.length - 6} aviso(s) no laudo.json)`);
      for (const k of m.comparacao.faltando.slice(0, 10)) linhas.push(`  FALTA    ${k.replace(/@1$/, '')} (está na original, não no clone)`);
      for (const r of m.retangulos.slice(0, 10)) linhas.push(`  PIXELS   x ${r.x} y ${r.y}, ${r.largura}x${r.altura} px, em ${r.dentro}`);
      if (m.retangulos.length > 10) linhas.push(`  (mais ${m.retangulos.length - 10} retângulo(s) no diff-${w}.png)`);
      falhas.push(...falhasDaLargura(nome, m, lim));
    }
  } catch (e) {
    await navegador.close().catch(() => {});
    if (e instanceof ErroDeFerramenta || /net::|Navigation|Target closed|browser has been closed/i.test(String(e && e.message))) {
      console.log(`ERRO DE FERRAMENTA: a página não abriu no navegador (${String(e.message || e).split('\n')[0]}): não é defeito da página nem do clone; rode o gate de novo`);
      process.exit(3);
    }
    throw e;
  }
  await navegador.close();
  writeFileSync(path.join(SAIDA, 'laudo.json'), JSON.stringify(laudo, null, 2), 'utf8');
  const rel = (p) => (PROJETO ? path.relative(PROJETO, p) : p).split(path.sep).join('/');
  linhas.push('', `Imagens em tamanho real: ${rel(SAIDA)}/lado-<largura>.png (original à esquerda) e diff-<largura>.png (diferença em vermelho). Laudo: ${rel(path.join(SAIDA, 'laudo.json'))}.`);
  if (PROJETO && !tem('--sem-registrar-uso')) {
    const evid = path.join(SAIDA, `clone-${LARGURAS[0]}.png`);
    const r = spawnSync(process.execPath, [path.join(AQUI, 'py.mjs'), path.join(AQUI, 'uso-ferramentas.py'), '--projeto', PROJETO, 'registrar', 'Playwright', '--arquivo', evid, '--detalhe', 'gate-fidelidade.mjs mediu e printou a original e o clone'], { encoding: 'utf8', env: { ...process.env, PYTHONUTF8: '1' } });
    linhas.push(r.status === 0 ? 'Uso do Playwright registrado no uso-ferramentas.py (evidência: o print do clone).' : `AVISO: não registrei o uso do Playwright (${`${r.stdout || ''}${r.stderr || ''}`.trim().split('\n')[0]}).`);
  }
  if (falhas.length) {
    linhas.push('', ...falhas.map((f) => `FALHA ${f}`), '', `RESULTADO: REPROVA em ${falhas.length} ponto(s). Abra o lado e o diff de cada largura, conserte o clone e rode de novo.`);
    console.log(linhas.join('\n'));
    process.exit(1);
  }
  linhas.push('', 'RESULTADO: PASSA (clone fiel nas larguras medidas).');
  console.log(linhas.join('\n'));
}

principal().catch((e) => { console.error(e && e.stack ? e.stack : String(e)); process.exit(1); });
