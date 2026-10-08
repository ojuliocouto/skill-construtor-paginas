#!/usr/bin/env node
/**
 * Captura de referências reais: abre cada URL no Chromium headless do Playwright e grava
 * dois prints por página, a PRIMEIRA DOBRA (1440x900, topo) e uma SEÇÃO DO MEIO (rolando
 * em passos até cerca de 45% da altura, para a imagem preguiçosa carregar). Atualiza o
 * manifesto `referencias/referencias.json` do projeto com url, tipo, título e os prints.
 *
 * A leitura (faz_bem, princípio, lido) NÃO é escrita por este script: ela só existe depois
 * que alguém abre os dois PNGs com os próprios olhos. O `gate-referencias.py` cobra isso.
 *
 * Antes do print tenta fechar o aviso de cookies por botão comum (prefere "recusar", depois
 * "fechar", por último "aceitar" só dos botões de cookie); nunca preenche formulário nem faz login.
 *
 * A captura se julga (3.5.6): cada URL sai com um estado em `captura` no manifesto,
 *   ok         página renderizada de verdade
 *   bloqueada  HTTP 401/403/429 ou texto de bloqueio (403, Forbidden, "Just a moment", captcha)
 *   quebrada   HTTP 400 ou mais, sem folha de estilo aplicada, ou página vazia
 *   coberta    modal cobrindo mais de 40% da janela mesmo depois de tentar fechar
 *   vazia      (3.5.8) a primeira dobra é uma folha lisa (herói em vídeo que não rendeu), ou o meio é de
 *              uma cor só com fotos que não carregaram. Dobra com mais de 80% de uma cor só segue ok, com aviso.
 * com o motivo. O gate-referencias.py reprova as que não são ok.
 *
 * Uso:
 *   node scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> [<url> ...]
 *   node scripts/capturar-referencias.mjs --projeto <dir> --tipo design <url> [<url> ...]
 *   node scripts/capturar-referencias.mjs --projeto <dir> --limpar-ruins
 *       (tira do manifesto as que não são ok e move os PNG delas para <projeto>/descartados/referencias/)
 *   node scripts/capturar-referencias.mjs --projeto <dir> --remover <url> [<url> ...]
 *       (3.5.8: tira do manifesto uma referência que capturou ok e não serve; aceita o endereço ou um
 *        trecho que só case uma; os PNG vão para <projeto>/descartados/referencias/)
 * Sai 0 se sobraram pelo menos 6 referências boas no manifesto (--minimo N muda o número, só
 * para teste), 1 se faltam. Falhar uma URL isolada não derruba a rodada: as que deram certo
 * ficam gravadas.
 */
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import fs from 'node:fs';
import path from 'node:path';
import { classificar, resumirBoas, proximoPrefixo, acharReferencia } from './qualidade-captura.mjs';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}

const args = process.argv.slice(2);
const valor = (flag) => { const i = args.indexOf(flag); return i >= 0 ? args[i + 1] : undefined; };
const projeto = valor('--projeto');
const tipo = valor('--tipo');
const TIPOS = ['mesmo-negocio', 'design'];
const limparRuins = args.includes('--limpar-ruins');
const MINIMO = Number(valor('--minimo') || 6);
const iRemover = args.indexOf('--remover');
const remover = [];
if (iRemover >= 0) for (let k = iRemover + 1; k < args.length && !args[k].startsWith('--'); k++) remover.push(args[k]);
const modoRemover = iRemover >= 0;
const urls = modoRemover ? [] : args.filter((a, i) => !a.startsWith('--') && !['--projeto', '--tipo', '--minimo'].includes(args[i - 1]));

if (!projeto || (modoRemover && remover.length === 0) || (!limparRuins && !modoRemover && (!TIPOS.includes(tipo) || urls.length === 0))) {
  console.error('uso: node capturar-referencias.mjs --projeto <dir> --tipo <mesmo-negocio|design> <url> [<url> ...]\n     node capturar-referencias.mjs --projeto <dir> --limpar-ruins\n     node capturar-referencias.mjs --projeto <dir> --remover <url> [<url> ...]');
  process.exit(2);
}
for (const u of urls) {
  if (!/^(https?|file):\/\//.test(u)) { console.error(`url invalida: ${u}`); process.exit(2); }
}

const pasta = path.join(path.resolve(projeto), 'referencias');
fs.mkdirSync(pasta, { recursive: true });
const manifesto = path.join(pasta, 'referencias.json');
const doc = fs.existsSync(manifesto) ? JSON.parse(fs.readFileSync(manifesto, 'utf8').replace(/^\uFEFF/, '')) : { referencias: [] };
if (!Array.isArray(doc.referencias)) doc.referencias = [];

// Caminho completo da skill, resolvido agora: quem roda isto está na pasta do projeto, não na da skill (A10).
const AQUI = path.dirname(fileURLToPath(import.meta.url));
// Entre aspas duplas quando o caminho tem espaço ou caractere fora de ASCII (cmd, PowerShell, bash e zsh aceitam).
const entreAspas = (s) => (/[^\x00-\x7f ]| /.test(s) ? `"${s}"` : s);
const scriptCmd = entreAspas(path.join(AQUI, 'capturar-referencias.mjs').split(path.sep).join('/'));
const pyCmd = entreAspas(path.join(AQUI, 'py.mjs').split(path.sep).join('/'));
const relativo = (p) => path.relative(path.resolve(projeto), p).split(path.sep).join('/');

const destinoDescarte = path.join(path.resolve(projeto), 'descartados', 'referencias');
// Move os PNG de uma referência para descartados/referencias/ (nunca apaga). Nome repetido ganha sufixo.
function descartarPrints(r) {
  fs.mkdirSync(destinoDescarte, { recursive: true });
  for (const rel of Object.values(r.prints || {})) {
    const de = path.join(path.resolve(projeto), rel);
    if (!fs.existsSync(de)) continue;
    let para = path.join(destinoDescarte, path.basename(de));
    for (let k = 2; fs.existsSync(para); k++) para = path.join(destinoDescarte, path.basename(de).replace(/(\.png)$/, `-${k}$1`));
    fs.renameSync(de, para);
  }
}

if (modoRemover) {
  const alvos = [];
  let erro = false;
  for (const u of remover) {
    const achada = acharReferencia(doc.referencias, u);
    if (achada.erro === 'ambigua') { console.error(`"${u}" casa mais de uma referência (${achada.candidatas.join(', ')}). Passe o endereço inteiro.`); erro = true; }
    else if (achada.erro) { console.error(`"${u}" não está no manifesto. Referências: ${doc.referencias.map((r) => r.url).join(', ') || '(nenhuma)'}`); erro = true; }
    else if (!alvos.includes(achada)) alvos.push(achada);
  }
  if (erro) { console.error('Nada foi removido.'); process.exit(1); }
  for (const r of alvos) { descartarPrints(r); console.log(`removida: ${r.url}`); }
  doc.referencias = doc.referencias.filter((r) => !alvos.includes(r));
  fs.writeFileSync(manifesto, JSON.stringify(doc, null, 2) + '\n');
  console.log(`\n${alvos.length} removida(s); ${resumirBoas(doc.referencias)} boa(s) no manifesto (mínimo ${MINIMO}). PNG em descartados/referencias/.`);
  process.exit(0);
}

if (limparRuins) {
  const ruins = doc.referencias.filter((r) => r.captura && r.captura.estado !== 'ok');
  for (const r of ruins) {
    descartarPrints(r);
    console.log(`descartada (${r.captura.estado}): ${r.url}`);
  }
  doc.referencias = doc.referencias.filter((r) => !ruins.includes(r));
  fs.writeFileSync(manifesto, JSON.stringify(doc, null, 2) + '\n');
  console.log(`\n${ruins.length} descartada(s); ${resumirBoas(doc.referencias)} boa(s) no manifesto. PNG em descartados/referencias/.`);
  process.exit(0);
}

// 3.5.8 (N2): o número do print segue do MAIOR prefixo já usado (pasta, descartados e manifesto).
const lerNomes = (d) => { try { return fs.readdirSync(d); } catch { return []; } };
const nomesUsados = () => [
  ...lerNomes(pasta), ...lerNomes(destinoDescarte),
  ...doc.referencias.flatMap((r) => Object.values(r.prints || {}).map((p) => path.basename(p))),
];

// Botões comuns de aviso de cookies, do menos ao mais permissivo. Só botões visíveis, com texto curto.
const BOTOES_COOKIE = [
  /^(recusar|rejeitar|reject( all)?|decline|only necessary|apenas necess[aá]rios?|somente necess[aá]rios?)\b/i,
  /^(fechar|close|dispensar|dismiss|not now|agora n[aã]o|continuar sem aceitar)\b/i,
  /^(aceitar( todos)?( os cookies)?|aceito|concordo|entendi|ok|got it|allow all|accept( all)?( cookies)?|i agree|agree)\b/i,
];
async function fecharAviso(page) {
  for (const rx of BOTOES_COOKIE) {
    const clicou = await page.evaluate((fonte) => {
      const rx = new RegExp(fonte.source, fonte.flags);
      const vistos = [...document.querySelectorAll('button, [role="button"], a[role="button"], input[type="button"], input[type="submit"]')];
      for (const b of vistos) {
        const r = b.getBoundingClientRect();
        const tx = (b.innerText || b.value || b.getAttribute('aria-label') || '').trim();
        if (r.width < 10 || r.height < 10 || tx.length === 0 || tx.length > 40 || getComputedStyle(b).visibility === 'hidden') continue;
        if (!rx.test(tx)) continue;
        // só botão dentro de aviso fixo ou diálogo (não "OK" de formulário no meio da página)
        let el = b, aviso = false;
        while (el && el !== document.body) {
          const cs = getComputedStyle(el);
          if (cs.position === 'fixed' || cs.position === 'sticky' || el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true') { aviso = true; break; }
          el = el.parentElement;
        }
        if (!aviso) continue;
        b.click();
        return true;
      }
      return false;
    }, { source: rx.source, flags: rx.flags }).catch(() => false);
    if (clicou) { await page.waitForTimeout(700); return true; }
  }
  return false;
}

// Maior fração da janela coberta por UM elemento fixo, em camada alta ou em diálogo, com conteúdo.
const medirCobertura = () => {
  const W = window.innerWidth, H = window.innerHeight;
  let maior = 0;
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    const dialogo = el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true' || el.tagName === 'DIALOG';
    if (!(cs.position === 'fixed' || dialogo)) continue;
    if (cs.display === 'none' || cs.visibility === 'hidden' || Number(cs.opacity) === 0 || cs.pointerEvents === 'none') continue;
    const z = Number.parseInt(cs.zIndex, 10);
    if (!dialogo && !(z >= 1)) continue;
    if (!(el.innerText || '').trim()) continue;
    const r = el.getBoundingClientRect();
    const w = Math.max(0, Math.min(r.right, W) - Math.max(r.left, 0));
    const h = Math.max(0, Math.min(r.bottom, H) - Math.max(r.top, 0));
    maior = Math.max(maior, (w * h) / (W * H));
  }
  return maior;
};

const medirPagina = () => {
  const temRegras = [...document.styleSheets].some((s) => { try { return s.cssRules.length > 0; } catch { return true; } });
  const inline = document.querySelectorAll('[style]').length >= 3;
  // Folha declarada que não pegou (falhou o carregamento, ou só tem reset): os links ficam no azul
  // padrão do navegador e o corpo na margem de 8 px. Visto em sawkille.com (achado A1).
  const links = [...document.querySelectorAll('a[href]')].filter((a) => { const r = a.getBoundingClientRect(); return r.width > 0 && r.height > 0; }).slice(0, 30);
  const padrao = links.filter((a) => ['rgb(0, 0, 238)', 'rgb(85, 26, 139)'].includes(getComputedStyle(a).color)).length;
  const crua = links.length >= 2 && padrao / links.length >= 0.7 && getComputedStyle(document.body).marginLeft === '8px';
  return {
    texto: (document.body ? document.body.innerText : '').slice(0, 6000),
    temEstilo: (temRegras || inline) && !crua,
    altura: document.documentElement.scrollHeight,
  };
};

// 3.5.8 (N1): fração do print ocupada pela cor mais comum e fotos visíveis que não carregaram.
// A dominância é medida num canvas de uma página à parte do mesmo navegador (sem biblioteca de imagem).
const medirImagensSemCarregar = () => {
  const H = window.innerHeight, W = window.innerWidth;
  return [...document.images].filter((im) => {
    const r = im.getBoundingClientRect();
    if (r.width < 40 || r.height < 40 || r.bottom < 0 || r.top > H || r.right < 0 || r.left > W) return false;
    const cs = getComputedStyle(im);
    if (cs.visibility === 'hidden' || cs.display === 'none') return false;
    return !im.complete || im.naturalWidth === 0;
  }).length;
};
async function esperarImagensVisiveis(page, ms = 6000) {
  await page.evaluate((limite) => new Promise((resolve) => {
    const H = window.innerHeight;
    const pendentes = [...document.images].filter((im) => { const r = im.getBoundingClientRect(); return r.bottom > 0 && r.top < H && !im.complete; });
    if (!pendentes.length) return resolve();
    let falta = pendentes.length;
    const fim = () => { if (--falta <= 0) resolve(); };
    pendentes.forEach((im) => { im.addEventListener('load', fim, { once: true }); im.addEventListener('error', fim, { once: true }); });
    setTimeout(resolve, limite);
  }), ms).catch(() => {});
}
async function medirDominancia(ctxMedida, png) {
  const aux = await ctxMedida.newPage();
  try {
    return await aux.evaluate(async (b64) => {
      const img = new Image();
      await new Promise((ok, no) => { img.onload = ok; img.onerror = no; img.src = 'data:image/png;base64,' + b64; });
      const w = 160, h = Math.max(1, Math.round(160 * img.naturalHeight / img.naturalWidth));
      const c = document.createElement('canvas'); c.width = w; c.height = h;
      const g = c.getContext('2d'); g.drawImage(img, 0, 0, w, h);
      const d = g.getImageData(0, 0, w, h).data, cont = new Map();
      for (let i = 0; i < d.length; i += 4) { const k = ((d[i] >> 3) << 10) | ((d[i + 1] >> 3) << 5) | (d[i + 2] >> 3); cont.set(k, (cont.get(k) || 0) + 1); }
      return Math.max(...cont.values()) / (w * h);
    }, png.toString('base64'));
  } catch { return undefined; } finally { await aux.close(); }
}

const slug = (u) => {
  try {
    const x = new URL(u);
    return ((x.hostname || 'local') + x.pathname).replace(/^www\./, '').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').slice(0, 48) || 'pagina';
  } catch { return 'pagina'; }
};

const { chromium } = carregarPlaywright();
const browser = await chromium.launch({ headless: true });
const ctxMedida = await browser.newContext();
const falhas = [];
const resultado = [];
try {
  for (const url of urls) {
    const existente = doc.referencias.find((r) => (r.url || '').replace(/\/$/, '') === url.replace(/\/$/, ''));
    // recaptura da mesma URL regrava os mesmos arquivos; URL nova ganha o próximo número livre (N2)
    const baseAnterior = existente && existente.prints && existente.prints.dobra ? path.basename(existente.prints.dobra).replace(/-dobra\.png$/, '') : '';
    const base = baseAnterior || `${String(proximoPrefixo(nomesUsados())).padStart(2, '0')}-${slug(url)}`;
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, locale: 'pt-BR' });
    const page = await ctx.newPage();
    try {
      const resposta = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      const http = resposta ? resposta.status() : 0;
      await page.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
      await page.waitForTimeout(1500);
      const fechou = await fecharAviso(page);
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
      await page.waitForTimeout(400);
      const dobra = path.join(pasta, `${base}-dobra.png`);
      const bufDobra = await page.screenshot({ path: dobra });
      const dominanciaDobra = await medirDominancia(ctxMedida, bufDobra);

      const medidas = await page.evaluate(medirPagina);
      const altura = medidas.altura;
      const cobertura = await page.evaluate(medirCobertura);
      const alvo = Math.max(900, Math.round(altura * 0.45) - 450);
      for (let y = 0; y < alvo; y += 600) {
        await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
        await page.waitForTimeout(250);
      }
      await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), alvo);
      await page.waitForTimeout(1200);
      await esperarImagensVisiveis(page);
      const meio = path.join(pasta, `${base}-meio.png`);
      // conta as fotos pendentes ANTES do print: o que não carregou até aqui é o que o print mostra em branco
      const imagensSemCarregar = await page.evaluate(medirImagensSemCarregar);
      const bufMeio = await page.screenshot({ path: meio });
      const dominanciaMeio = await medirDominancia(ctxMedida, bufMeio);
      const veredito = classificar({ http, titulo: await page.title(), texto: medidas.texto, temEstilo: medidas.temEstilo, altura, janela: 900, cobertura, dominanciaDobra, dominanciaMeio, imagensSemCarregar });

      const titulo = (await page.title()).trim().slice(0, 140);
      const entrada = existente || { url };
      Object.assign(entrada, {
        tipo,
        titulo,
        prints: { dobra: path.relative(path.resolve(projeto), dobra).split(path.sep).join('/'), meio: path.relative(path.resolve(projeto), meio).split(path.sep).join('/') },
        altura_pagina: altura,
        captura: { estado: veredito.estado, motivo: veredito.motivo, http, cobertura: Math.round(cobertura * 100) / 100, aviso_fechado: fechou,
          dominancia_dobra: dominanciaDobra === undefined ? null : Math.round(dominanciaDobra * 100) / 100,
          dominancia_meio: dominanciaMeio === undefined ? null : Math.round(dominanciaMeio * 100) / 100, imagens_sem_carregar: imagensSemCarregar,
          ...(veredito.aviso ? { aviso: veredito.aviso } : {}) },
        capturado_em: new Date().toISOString().slice(0, 19),
      });
      if (!existente) {
        Object.assign(entrada, {
          faz_bem: { composicao: '', tipografia: '', imagem: '', ritmo: '' },
          principio: '',
          lido: false,
        });
        doc.referencias.push(entrada);
      }
      resultado.push(veredito.estado);
      const rotulo = veredito.estado.padEnd(9);
      console.log(`${rotulo} ${url}${veredito.motivo ? `\n     motivo: ${veredito.motivo}` : ''}${veredito.aviso ? `\n     AVISO: ${veredito.aviso}` : ''}\n     ${entrada.prints.dobra}\n     ${entrada.prints.meio}  (pagina com ${altura}px${fechou ? ', aviso de cookies fechado' : ''})`);
    } catch (e) {
      falhas.push(url);
      console.error(`FALHA ${url}: ${String(e.message || e).split('\n')[0]}`);
    } finally {
      await ctx.close();
    }
  }
} finally {
  await browser.close();
  fs.writeFileSync(manifesto, JSON.stringify(doc, null, 2) + '\n');
}
const boas = resumirBoas(doc.referencias);
const ruins = resultado.filter((e) => e !== 'ok').length;
console.log(`\n${urls.length - falhas.length} de ${urls.length} capturada(s), ${resultado.filter((e) => e === 'ok').length} ok, ${ruins} ruim(ns), ${falhas.length} com falha. Manifesto: ${path.relative(process.cwd(), manifesto).split(path.sep).join('/') || manifesto}`);
console.log(`Referências boas no manifesto: ${boas} (mínimo ${MINIMO}).`);
if (ruins) console.log(`Tire as ruins do manifesto e dos prints: node ${scriptCmd} --projeto <dir> --limpar-ruins`);
console.log(`Uma ok que não serve (feia, cookie, sem foto)? node ${scriptCmd} --projeto <dir> --remover <url>`);
console.log(`Agora ABRA cada PNG que ficou ok e escreva faz_bem, principio e lido:true. Depois: node ${pyCmd} gate-referencias.py --projeto <dir>`);
if (boas < MINIMO) console.log(`Faltam ${MINIMO - boas} referência(s) boa(s): capture mais URLs (a saída é diferente de zero até chegar no mínimo).`);
process.exit(boas < MINIMO ? 1 : 0);
