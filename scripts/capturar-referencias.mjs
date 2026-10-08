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
 * Não clica em banner de cookie nem em nada que aceite termos: se um banner cobrir o print,
 * isso se registra na leitura, e a captura segue. Nada de login.
 *
 * Uso:
 *   node scripts/capturar-referencias.mjs --projeto <dir> --tipo mesmo-negocio <url> [<url> ...]
 *   node scripts/capturar-referencias.mjs --projeto <dir> --tipo design <url> [<url> ...]
 * Sai 0 se todas capturaram, 1 se alguma falhou (as que deram certo ficam gravadas).
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import fs from 'node:fs';
import path from 'node:path';

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
const urls = args.filter((a, i) => !a.startsWith('--') && !['--projeto', '--tipo'].includes(args[i - 1]));

if (!projeto || !TIPOS.includes(tipo) || urls.length === 0) {
  console.error('uso: node capturar-referencias.mjs --projeto <dir> --tipo <mesmo-negocio|design> <url> [<url> ...]');
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

const slug = (u) => {
  try {
    const x = new URL(u);
    return ((x.hostname || 'local') + x.pathname).replace(/^www\./, '').replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').slice(0, 48) || 'pagina';
  } catch { return 'pagina'; }
};

const { chromium } = carregarPlaywright();
const browser = await chromium.launch({ headless: true });
const falhas = [];
try {
  for (const url of urls) {
    const existente = doc.referencias.find((r) => (r.url || '').replace(/\/$/, '') === url.replace(/\/$/, ''));
    const n = existente ? doc.referencias.indexOf(existente) + 1 : doc.referencias.length + 1;
    const base = `${String(n).padStart(2, '0')}-${slug(url)}`;
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1, locale: 'pt-BR' });
    const page = await ctx.newPage();
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForLoadState('networkidle', { timeout: 12000 }).catch(() => {});
      await page.waitForTimeout(1500);
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
      await page.waitForTimeout(400);
      const dobra = path.join(pasta, `${base}-dobra.png`);
      await page.screenshot({ path: dobra });

      const altura = await page.evaluate(() => document.documentElement.scrollHeight);
      const alvo = Math.max(900, Math.round(altura * 0.45) - 450);
      for (let y = 0; y < alvo; y += 600) {
        await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), y);
        await page.waitForTimeout(250);
      }
      await page.evaluate((v) => window.scrollTo({ top: v, behavior: 'instant' }), alvo);
      await page.waitForTimeout(1200);
      const meio = path.join(pasta, `${base}-meio.png`);
      await page.screenshot({ path: meio });

      const titulo = (await page.title()).trim().slice(0, 140);
      const entrada = existente || { url };
      Object.assign(entrada, {
        tipo,
        titulo,
        prints: { dobra: path.relative(path.resolve(projeto), dobra), meio: path.relative(path.resolve(projeto), meio) },
        altura_pagina: altura,
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
      console.log(`ok   ${url}\n     ${entrada.prints.dobra}\n     ${entrada.prints.meio}  (pagina com ${altura}px)`);
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
console.log(`\n${urls.length - falhas.length} de ${urls.length} capturada(s). Manifesto: ${path.relative(process.cwd(), manifesto) || manifesto}`);
console.log('Agora ABRA cada PNG e escreva faz_bem, principio e lido:true. Depois: node scripts/py.mjs gate-referencias.py --projeto <dir>');
process.exit(falhas.length ? 1 : 0);
