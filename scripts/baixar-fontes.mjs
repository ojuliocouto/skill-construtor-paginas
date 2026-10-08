#!/usr/bin/env node
/**
 * Baixa uma fonte do Google Fonts para a pasta do projeto (achado A24, teste de ponta a ponta de 08/10/2026).
 *
 * A skill manda usar a fonte local e só nos pesos usados, mas não dizia como baixar. Este script pede o CSS do Google
 * Fonts com um User-Agent de navegador moderno (é ele que faz o Google devolver woff2), fica só com o subconjunto
 * LATINO, baixa os arquivos woff2 para `fonts/` e imprime o `@font-face` pronto, com o caminho relativo certo.
 *
 * Uso:
 *   node scripts/baixar-fontes.mjs --familia "Bricolage Grotesque" --pesos 400,700 [--saida fonts] [--prefixo fonts/] [--so-estatica]
 *   node scripts/baixar-fontes.mjs --familia Figtree --pesos 300,900          (variável quando a família tiver)
 *
 *   --pesos       os pesos que a página usa (só esses): "400,700". Com variável, vale o menor e o maior.
 *   --saida       pasta dos arquivos (padrão: fonts, dentro da pasta onde você está)
 *   --prefixo     caminho que vai no `url()` do @font-face (padrão: o nome da pasta de saída + "/")
 *   --so-estatica não tenta a variável: um arquivo por peso
 *
 * Variável quando existir: pede `wght@<menor>..<maior>`; se o Google recusa (família sem eixo de peso), cai para os
 * pesos estáticos. Pesos que o Google serve no mesmo arquivo variável viram UM arquivo e um `font-weight: 400 700`.
 * Sem internet, o script diz qual endereço não respondeu e sai com 1, sem deixar arquivo pela metade.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const UA_NAVEGADOR = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

export function slug(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

export function montarUrl(familia, pesos, variavel) {
  const fam = encodeURIComponent(familia).replace(/%20/g, '+');
  const lista = [...new Set(pesos)].sort((a, b) => a - b);
  const eixo = variavel && lista.length > 1 ? `${lista[0]}..${lista[lista.length - 1]}` : lista.join(';');
  return `https://fonts.googleapis.com/css2?family=${fam}:wght@${eixo}&display=swap`;
}

/** Os blocos @font-face do subconjunto latino (o comentário `/* latin *​/` que o Google põe antes de cada um). */
export function blocosLatinos(css) {
  const out = [];
  const re = /\/\*\s*([a-z0-9-]+)\s*\*\/\s*@font-face\s*\{([^}]*)\}/gi;
  let m;
  while ((m = re.exec(css))) {
    if (m[1].toLowerCase() !== 'latin') continue;
    const campo = (nome) => { const x = new RegExp(nome + '\\s*:\\s*([^;]+);', 'i').exec(m[2]); return x ? x[1].trim() : ''; };
    const url = /url\(([^)]+)\)/.exec(m[2]);
    out.push({ familia: campo('font-family').replace(/^['"]|['"]$/g, ''), estilo: campo('font-style') || 'normal', peso: campo('font-weight'),
      url: url ? url[1].replace(/^['"]|['"]$/g, '') : '', faixa: campo('unicode-range'), estiramento: campo('font-stretch') });
  }
  return out;
}

async function buscarPadrao(url, opcoes = {}) {
  const r = await fetch(url, { headers: { 'User-Agent': UA_NAVEGADOR, ...(opcoes.headers || {}) } });
  return { status: r.status, texto: opcoes.binario ? null : await r.text(), bytes: opcoes.binario ? Buffer.from(await r.arrayBuffer()) : null };
}

/** Pura o bastante para testar: recebe `buscar(url, {binario})` e devolve o que gravou e o CSS pronto. */
export async function baixar({ familia, pesos, saida, prefixo, soEstatica = false, buscar = buscarPadrao }) {
  if (!familia || !pesos || !pesos.length || pesos.some((p) => !Number.isFinite(p) || p < 1 || p > 1000)) throw new Error('informe --familia e --pesos (ex.: 400,700)');
  let css = null, variavel = false;
  const tentativas = soEstatica || pesos.length < 2 ? [false] : [true, false];
  for (const v of tentativas) {
    const url = montarUrl(familia, pesos, v);
    let r;
    try { r = await buscar(url); } catch (e) { throw new Error(`sem conexão com fonts.googleapis.com (${url}): ${e.message || e}. Verifique a internet ou o proxy e rode de novo.`); }
    if (r.status === 200 && blocosLatinos(r.texto).length) { css = r.texto; variavel = v; break; }
    if (r.status !== 200 && !(v && r.status === 400)) {
      throw new Error(`o Google Fonts respondeu HTTP ${r.status} para "${familia}" (${url}): confira o nome da família e os pesos.`);
    }
  }
  if (!css) throw new Error(`o Google Fonts não devolveu o subconjunto latino de "${familia}" nos pesos ${pesos.join(', ')}: confira o nome e os pesos.`);

  const blocos = blocosLatinos(css);
  const porArquivo = new Map();
  for (const b of blocos) {
    if (!porArquivo.has(b.url)) porArquivo.set(b.url, { ...b, pesos: [] });
    porArquivo.get(b.url).pesos.push(...b.peso.split(/\s+/).map(Number).filter(Number.isFinite));
  }
  const dir = path.resolve(saida);
  const base = slug(familia);
  const gravar = [];
  for (const [url, b] of porArquivo) {
    const ps = [...new Set(b.pesos)].sort((x, y) => x - y);
    const faixa = ps.length > 1 ? `${ps[0]} ${ps[ps.length - 1]}` : String(ps[0]);
    const arquivo = ps.length > 1 || variavel ? `${base}-variavel${b.estilo === 'italic' ? '-italico' : ''}.woff2` : `${base}-${ps[0]}.woff2`;
    let r;
    try { r = await buscar(url, { binario: true }); } catch (e) { throw new Error(`sem conexão com fonts.gstatic.com (${url}): ${e.message || e}`); }
    if (r.status !== 200 || !r.bytes || r.bytes.length < 4) throw new Error(`o arquivo da fonte não baixou (HTTP ${r.status}): ${url}`);
    gravar.push({ arquivo, bytes: r.bytes, bloco: b, faixa });
  }
  // Só grava depois de baixar tudo: nada fica pela metade se a rede cair no meio.
  fs.mkdirSync(dir, { recursive: true });
  for (const g of gravar) fs.writeFileSync(path.join(dir, g.arquivo), g.bytes);
  const pref = prefixo ?? (path.basename(dir) + '/');
  const fontFace = gravar.map((g) => [
    '@font-face {',
    `  font-family: '${g.bloco.familia}';`,
    `  font-style: ${g.bloco.estilo};`,
    `  font-weight: ${g.faixa};`,
    ...(g.bloco.estiramento ? [`  font-stretch: ${g.bloco.estiramento};`] : []),
    '  font-display: swap;',
    `  src: url('${pref}${g.arquivo}') format('woff2');`,
    ...(g.bloco.faixa ? [`  unicode-range: ${g.bloco.faixa};`] : []),
    '}',
  ].join('\n')).join('\n');
  return { variavel, arquivos: gravar.map((g) => ({ arquivo: g.arquivo, bytes: g.bytes.length })), fontFace };
}

function lerArgs(argv) {
  const v = (n) => { const i = argv.indexOf(n); return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[i + 1] : null; };
  return { familia: v('--familia'), pesos: (v('--pesos') || '').split(',').map((s) => Number(s.trim())), saida: v('--saida') || 'fonts', prefixo: v('--prefixo'), soEstatica: argv.includes('--so-estatica') };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const a = lerArgs(process.argv.slice(2));
  try {
    const r = await baixar(a);
    console.log(`${r.variavel ? 'Fonte VARIÁVEL' : 'Fontes estáticas'} (só o latino) gravadas em ${a.saida}/:`);
    for (const f of r.arquivos) console.log(`  ${f.arquivo}  ${(f.bytes / 1024).toFixed(1)} KB`);
    console.log('\nCole no CSS:\n\n' + r.fontFace + '\n');
    console.log('Lembrete: só os pesos que a página usa, `font-display: swap` e <link rel="preload" as="font" type="font/woff2" crossorigin> para a fonte do título.');
  } catch (e) {
    console.error('ERRO: ' + (e.message || e));
    process.exit(1);
  }
}
