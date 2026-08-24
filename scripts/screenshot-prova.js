#!/usr/bin/env node
// Prova de entrega da skill construtor-paginas.
// Captura screenshots desktop + mobile do deploy real e, opcionalmente,
// testa a interacao principal (clique) registrando o estado pos-clique.
// Uso:
//   export NODE_PATH="$HOME/.npm-global/lib/node_modules"
//   node screenshot-prova.js <url> <outdir> [--click "<seletor css>"]
// Sai com exit 1 e mensagem clara em QUALQUER falha: sem screenshot nao ha entrega.

const path = require('path');
const fs = require('fs');

async function main() {
  const args = process.argv.slice(2);
  const url = args[0];
  const outdir = args[1];
  const clickIdx = args.indexOf('--click');
  const clickSel = clickIdx > -1 ? args[clickIdx + 1] : null;

  if (!url || !outdir) {
    console.error('uso: node screenshot-prova.js <url> <outdir> [--click "<seletor>"]');
    process.exit(1);
  }

  // Resolve o playwright do projeto, do NODE_PATH ou do root global do npm, pra
  // funcionar em qualquer maquina sem o usuario precisar exportar variavel.
  let chromium;
  try {
    ({ chromium } = require('playwright'));
  } catch (e) {
    try {
      const rootGlobal = require('child_process')
        .execSync('npm root -g', { encoding: 'utf8' })
        .trim();
      ({ chromium } = require(path.join(rootGlobal, 'playwright')));
    } catch (e2) {
      console.error('FALHA: playwright nao encontrado. Rodar: npm install -g playwright && npx playwright install chromium');
      process.exit(1);
    }
  }

  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const shots = [];

  try {
    const viewports = [
      { name: 'desktop', width: 1440, height: 900 },
      { name: 'mobile', width: 390, height: 844 },
    ];
    for (const vp of viewports) {
      const page = await browser.newPage({ viewport: { width: vp.width, height: vp.height } });
      await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 }).catch(async () => {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(4000);
      });
      await page.waitForTimeout(1500);
      const file = path.join(outdir, `prova-${vp.name}.png`);
      await page.screenshot({ path: file, fullPage: true });
      shots.push(file);

      if (clickSel) {
        const el = page.locator(clickSel).first();
        await el.waitFor({ state: 'visible', timeout: 10000 });
        await el.click();
        await page.waitForTimeout(2500);
        const fClick = path.join(outdir, `prova-${vp.name}-pos-clique.png`);
        await page.screenshot({ path: fClick, fullPage: false });
        shots.push(fClick);
      }
      await page.close();
    }
  } catch (e) {
    console.error(`FALHA na prova de entrega: ${e.message}`);
    console.error('ENTREGA BLOQUEADA: conserte a verificacao antes de declarar pronto.');
    await browser.close();
    process.exit(1);
  }

  await browser.close();

  for (const f of shots) {
    const kb = Math.round(fs.statSync(f).size / 1024);
    if (kb < 5) {
      console.error(`FALHA: ${f} tem so ${kb}KB (pagina em branco?). ENTREGA BLOQUEADA.`);
      process.exit(1);
    }
    console.log(`${f} (${kb}KB)`);
  }
  console.log('OK: agora LEIA os PNGs com a tool Read antes de declarar pronto.');
}

main();
