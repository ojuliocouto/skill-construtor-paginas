#!/usr/bin/env node
/**
 * Grava 3 quadros (início, meio e fim) da animação de cada seção, em desktop 1440 e celular 390.
 *
 * Por que existe (04/10/2026). A v7 do estúdio provou que cada seção anima o próprio conteúdo com
 * uma prancha por seção; o script que gravava os quadros morava na pasta da página, com um seletor
 * fixo (`.passos`) e um modo por seção escrito à mão. Aqui ele é parametrizado: uma lista de
 * seções em JSON, nenhum caminho nem seletor de página específica.
 *
 * Uso: node scripts/anim.mjs --url <url> --saida <pasta> --secoes <secoes.json> [--so <nome>]
 *
 * `secoes.json` é uma lista de objetos:
 *   nome         prefixo dos arquivos (ex.: "04-avaliacao"); obrigatório
 *   seletor      seletor CSS da seção; obrigatório
 *   titulo, tipo usados pelo prancha.py e pelo gate-animacao.py (o tipo é o da coluna Animação do PLANO.md)
 *   modo         "entrada" (padrão): rola até a seção e grava ao chegar;
 *                "heroi": grava a partir da carga, sem rolar, e rola 260 px no último quadro;
 *                "rolagem": seção alta com elemento fixo (sticky) que muda com a rolagem; grava em
 *                4%, 50% e 99% do caminho por dentro da seção
 *   ancora       fração da janela em que o topo da seção para (padrão 0.1; seção que aparece pelo fundo, 0.55)
 *   esperas      [a, b, c] em ms antes de cada quadro (entrada: 90, 550, 2300; heroi: 80, 650, 2200; rolagem: 700 cada)
 *   clique       seletor clicado entre o 1º e o 2º quadro (FAQ que abre, aba que troca)
 *   rolarHorizontal  seletor de um carrossel: no celular, rola 330 px de lado antes do último quadro
 *
 * Saída: <saida>/quadros/<nome>-desk-1..3.png e <nome>-mob-1..3.png. Segue com o prancha.py.
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
const { chromium } = carregarPlaywright();

const args = process.argv.slice(2);
const valor = (n) => { const i = args.indexOf(n); return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : null; };
const URL_ALVO = valor('--url'), SAIDA = valor('--saida'), JSON_SECOES = valor('--secoes'), SO = valor('--so');
if (!URL_ALVO || !SAIDA || !JSON_SECOES) {
  console.error('uso: node anim.mjs --url <url> --saida <pasta> --secoes <secoes.json> [--so <nome>]');
  process.exit(2);
}
let secoes;
try { secoes = JSON.parse(fs.readFileSync(JSON_SECOES, 'utf8').replace(/^\uFEFF/, '')); } catch (e) { console.error('secoes.json ilegível: ' + e.message); process.exit(2); }
if (!Array.isArray(secoes) || !secoes.every((s) => s.nome && s.seletor)) { console.error('secoes.json: cada seção precisa de "nome" e "seletor"'); process.exit(2); }
const quadros = path.join(SAIDA, 'quadros');
fs.mkdirSync(quadros, { recursive: true });

const PADRAO = { entrada: [90, 550, 2300], heroi: [80, 650, 2200], rolagem: [700, 700, 700] };
const TELAS = [['desk', 1440, 900, false], ['mob', 390, 844, true]];
const navegador = await chromium.launch();
let falhou = false;

for (const sec of secoes) {
  if (SO && sec.nome !== SO) continue;
  const modo = sec.modo || 'entrada';
  if (!PADRAO[modo]) { console.error(`${sec.nome}: modo "${modo}" desconhecido (entrada, heroi, rolagem)`); falhou = true; continue; }
  const esperas = sec.esperas || PADRAO[modo];
  for (const [tag, w, h, movel] of TELAS) {
    // Um contexto novo por seção e tela: a animação de entrada começa do zero.
    const ctx = await navegador.newContext({ viewport: { width: w, height: h }, isMobile: movel, hasTouch: movel, deviceScaleFactor: 1 });
    const p = await ctx.newPage();
    const q = (i) => p.screenshot({ path: path.join(quadros, `${sec.nome}-${tag}-${i}.png`) });
    try {
      await p.goto(URL_ALVO, { waitUntil: modo === 'heroi' ? 'domcontentloaded' : 'networkidle', timeout: 45000 });
      await p.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
      if (!(await p.$(sec.seletor))) throw new Error(`seletor "${sec.seletor}" não existe na página`);
      const pular = (frac) => p.evaluate(([s, f]) => {
        const el = document.querySelector(s);
        window.scrollTo(0, Math.max(0, el.getBoundingClientRect().top + scrollY - innerHeight * f));
      }, [sec.seletor, frac]);
      if (modo === 'heroi') {
        await p.waitForTimeout(esperas[0]); await q(1);
        await p.waitForTimeout(esperas[1]); await q(2);
        await p.waitForTimeout(esperas[2]); await p.evaluate(() => window.scrollTo(0, 260)); await p.waitForTimeout(400); await q(3);
      } else if (modo === 'rolagem') {
        for (const [i, alvo] of [[1, 0.04], [2, 0.5], [3, 0.99]]) {
          await p.evaluate(([s, pr]) => {
            const el = document.querySelector(s), vh = innerHeight, r = el.getBoundingClientRect();
            const topo = vh * 0.62 - pr * (r.height - vh * 0.3);
            window.scrollTo(0, scrollY + r.top - topo);
          }, [sec.seletor, alvo]);
          await p.waitForTimeout(esperas[i - 1]); await q(i);
        }
      } else {
        await pular(sec.ancora ?? 0.1);
        await p.waitForTimeout(esperas[0]); await q(1);
        if (sec.clique) { await p.click(sec.clique); await p.waitForTimeout(170); } else await p.waitForTimeout(esperas[1]);
        await q(2);
        if (sec.rolarHorizontal && movel) {
          await p.waitForTimeout(esperas[1]);
          await p.evaluate((s) => document.querySelector(s).scrollBy({ left: 330, behavior: 'smooth' }), sec.rolarHorizontal);
          await p.waitForTimeout(900);
        } else await p.waitForTimeout(sec.clique ? 800 : esperas[2]);
        await q(3);
      }
    } catch (e) {
      console.error(`${sec.nome} (${tag}): ${e.message}`);
      falhou = true;
    }
    await ctx.close();
  }
  console.log('quadros', sec.nome);
}
await navegador.close();
process.exit(falhou ? 1 : 0);
