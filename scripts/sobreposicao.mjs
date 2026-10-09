#!/usr/bin/env node
/**
 * Mede a sobreposição entre um elemento FIXO (sticky) e os blocos que ele não pode cobrir, ao
 * longo de toda a rolagem.
 *
 * Por que existe (04/10/2026). Na v7 do estúdio o título fixo da seção da dor dividia o grid com
 * a frase de impacto em largura total: ao rolar, o título passava por cima da frase. O
 * gate-oclusao mede a página PARADA e não pegou; o auditor achou (crítico) e a correção foi tirar
 * a frase do grid. A prova foi este script, que rola a página em passos de 20 px, mede a
 * interseção entre a caixa do elemento fixo e a dos blocos, e guarda a maior: 0 px² em 1024, 1280,
 * 1440 e 1920. Aqui ele deixa de ter seletores da Studio e vira parâmetro.
 *
 * Regra: o elemento sticky vive num grid que TERMINA antes do próximo bloco de largura total
 * (`references/sticky-e-sobreposicao.md`).
 *
 * Uso: node scripts/sobreposicao.mjs --url <url> --fixo <seletor> --contra <seletor>[,<seletor>]
 *        [--telas 1024x768,1280x720,1440x900,1920x1080] [--passo 20]
 * Sai com 1 se alguma tela tiver interseção maior que 0 px² ou se um seletor não existir.
 */
import { createRequire } from 'node:module';
import { raizGlobal as raizGlobalNpm } from './npm-global.cjs';
import path from 'node:path';
import { exigirServidor } from './servidor-no-ar.mjs';

const require = createRequire(import.meta.url);
function carregarPlaywright() {
  try { return require('playwright'); } catch {
    try { return require(path.join(raizGlobalNpm(), 'playwright')); }
    catch { console.error('playwright nao encontrado: npm i -g playwright && npx playwright install chromium'); process.exit(1); }
  }
}
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const valor = (n) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null; };
const URL_ALVO = valor('--url'), FIXO = valor('--fixo'), CONTRA = valor('--contra');
const TELAS = (valor('--telas') || '1024x768,1280x720,1440x900,1920x1080').split(',').map((t) => t.split('x').map(Number));
const PASSO = Number(valor('--passo') || 20);
if (!URL_ALVO || !FIXO || !CONTRA || TELAS.some((t) => t.length !== 2 || t.some(Number.isNaN))) {
  console.error('uso: node sobreposicao.mjs --url <url> --fixo <seletor> --contra <seletor>[,<seletor>] [--telas 1024x768,1440x900] [--passo 20]');
  process.exit(2);
}

await exigirServidor(URL_ALVO);   // servidor caído: uma mensagem clara (saída 3), não ERR_CONNECTION_REFUSED (P11)
const navegador = await chromium.launch();
const falhas = [];
console.log('\nSOBREPOSIÇÃO DO ELEMENTO FIXO  ' + URL_ALVO);
console.log('='.repeat(80));
for (const [w, h] of TELAS) {
  const page = await navegador.newPage({ viewport: { width: w, height: h } });
  try { await page.goto(URL_ALVO, { waitUntil: 'networkidle', timeout: 45000 }); }
  catch { await page.goto(URL_ALVO, { waitUntil: 'domcontentloaded', timeout: 45000 }); }
  await page.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  const existe = await page.evaluate(([f, c]) => ({ fixo: document.querySelectorAll(f).length, contra: document.querySelectorAll(c).length }), [FIXO, CONTRA]);
  if (!existe.fixo || !existe.contra) {
    falhas.push(`${w}x${h}: seletor ${!existe.fixo ? `--fixo "${FIXO}"` : `--contra "${CONTRA}"`} não existe na página`);
    await page.close();
    continue;
  }
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  let max = 0, onde = 0;
  for (let y = 0; y <= total; y += PASSO) {
    await page.evaluate((yy) => window.scrollTo(0, yy), y);
    const a = await page.evaluate(([f, c]) => {
      let m = 0;
      for (const fixo of document.querySelectorAll(f)) {
        const r1 = fixo.getBoundingClientRect();
        for (const outro of document.querySelectorAll(c)) {
          if (outro === fixo || outro.contains(fixo) || fixo.contains(outro)) continue;
          const r2 = outro.getBoundingClientRect();
          const ix = Math.max(0, Math.min(r1.right, r2.right) - Math.max(r1.left, r2.left));
          const iy = Math.max(0, Math.min(r1.bottom, r2.bottom) - Math.max(r1.top, r2.top));
          m = Math.max(m, ix * iy);
        }
      }
      return m;
    }, [FIXO, CONTRA]);
    if (a > max) { max = a; onde = y; }
  }
  console.log(`${`${w}x${h}`.padEnd(12)} interseção máxima ${Math.round(max)} px² entre "${FIXO}" e "${CONTRA}"${max > 0 ? ` (em scrollY ${onde})` : ''}`);
  if (max > 0) falhas.push(`${w}x${h}: o elemento fixo cobre o bloco por ${Math.round(max)} px² em scrollY ${onde}: o sticky tem de viver num grid que termina antes do bloco de largura total`);
  await page.close();
}
await navegador.close();
console.log('='.repeat(80));
if (falhas.length) {
  falhas.forEach((f) => console.log('  FALHA: ' + f));
  console.log(`\n  REPROVA: ${falhas.length} tela(s) com sobreposição.\n`);
  process.exit(1);
}
console.log(`  PASSA: ${TELAS.length} tela(s), 0 px² de sobreposição em toda a rolagem.\n`);
