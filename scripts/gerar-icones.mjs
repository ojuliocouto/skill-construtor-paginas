#!/usr/bin/env node
/**
 * GERA OS ÍCONES DO SITE a partir do SVG da identidade atual e grava o registro que o
 * gate-publicacao.py confere.
 *
 * Por que existe (03/10/2026, auditoria da v5 do estúdio): favicon.png e apple-touch-icon.png
 * eram os arquivos da v3 (md5 igual), com o prumo sobre grade que a página já tinha abandonado.
 * Copiar a pasta de uma versão para a outra levava o ícone velho junto e nada reclamava.
 *
 * Entrada: <projeto>/icones/icone.svg, com data-motivo="<o que desenha>" na raiz, o mesmo motivo
 * da linha "Ícone do site: <motivo>" do plano-visual.md (e a página precisa desenhar esse motivo
 * em algum data-desenho). Saída: <projeto>/favicon.png (32x32), <projeto>/apple-touch-icon.png
 * (180x180) e <projeto>/icones/icones.json com o sha256 do SVG e dos PNG.
 *
 * Uso: node scripts/gerar-icones.mjs --projeto <dir>
 */
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(execSync('npm root -g', { encoding: 'utf8' }).trim(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}

const args = process.argv.slice(2);
const i = args.indexOf('--projeto');
const projeto = i >= 0 ? args[i + 1] : null;
if (!projeto) { console.error('uso: node gerar-icones.mjs --projeto <dir>'); process.exit(2); }
const svgArq = path.join(projeto, 'icones', 'icone.svg');
if (!fs.existsSync(svgArq)) { console.error(`falta ${svgArq}: desenhe o motivo do plano em SVG quadrado`); process.exit(1); }
const svg = fs.readFileSync(svgArq, 'utf8');
const motivo = (svg.match(/data-motivo="([^"]+)"/) || [])[1];
if (!motivo) { console.error('icone.svg sem data-motivo="<o que desenha>" na raiz'); process.exit(1); }

const { chromium } = carregarPlaywright();
const navegador = await chromium.launch();
const sha = (b) => crypto.createHash('sha256').update(b).digest('hex');
const arquivos = {};
for (const [nome, lado] of [['favicon.png', 32], ['apple-touch-icon.png', 180]]) {
  const page = await navegador.newPage({ viewport: { width: lado, height: lado }, deviceScaleFactor: 1 });
  const corpo = svg.replace(/<svg\b/, `<svg width="${lado}" height="${lado}"`);
  await page.setContent(`<!doctype html><html><body style="margin:0;background:transparent">${corpo}</body></html>`);
  const png = await page.screenshot({ clip: { x: 0, y: 0, width: lado, height: lado }, omitBackground: true });
  fs.writeFileSync(path.join(projeto, nome), png);
  arquivos[nome] = sha(png);
  await page.close();
}
await navegador.close();
const registro = { motivo, svg_sha256: sha(Buffer.from(svg)), arquivos, quando: new Date().toISOString() };
fs.writeFileSync(path.join(projeto, 'icones', 'icones.json'), JSON.stringify(registro, null, 2));
console.log(`ícones gerados de icones/icone.svg ("${motivo}"): ${Object.keys(arquivos).join(', ')}; registro em icones/icones.json`);
