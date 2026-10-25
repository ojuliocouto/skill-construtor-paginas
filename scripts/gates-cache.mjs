#!/usr/bin/env node
/**
 * CACHE DE GATE POR CONTEÚDO (corte 4 da auditoria de velocidade).
 *
 * Por que existe. Cada rodada completa do `rodar-gates.mjs` custa de 4 a 5 minutos e a página passa por
 * 6 a 10 rodadas. Em várias delas nada que o gate lê mudou (correção só de evidência, rodada repetida
 * para conferir, gate reprovado de outro lugar). O gate de movimento sozinho leva 256 s. Gate cujo
 * insumo é idêntico ao da última vez que PASSOU devolve o laudo de então, sem rodar de novo.
 *
 * Regra de ouro: invalidação correta é inegociável. A chave de um gate junta TUDO que pode mudar o veredito:
 *   1. o gate (nome e arquivo) e os argumentos exatos, com os caminhos e a porta trocados por marcadores;
 *   2. a versão dos scripts: o conteúdo de todos os arquivos da pasta de gates (menos testes e fixtures)
 *      e da pasta `references/` da skill, que o gate-plano lê;
 *   3. o conteúdo da `dist/` (hash de cada arquivo, a data não entra) quando o gate abre a página ou a lê;
 *   4. o conteúdo do projeto inteiro, menos as pastas que os gates escrevem (`gates/`, `auditoria/`) e a
 *      `dist/` (já contada em 3), quando algum argumento do gate aponta para o projeto;
 *   5. o ambiente: sistema, versão do Node e do Playwright.
 * Qualquer byte diferente em qualquer item muda a chave e o gate roda de novo.
 *
 * O que NÃO entra no cache: gate que reprovou (reprovação por carga da máquina não pode virar definitiva),
 * gate que quebrou ou estourou o tempo, gate de uma página servida por quem chamou (`--url`: não sabemos o
 * que há lá) e o gate de vídeo (lê uma pasta pública que o comando não conhece).
 *
 * Também é um comando: `node gates-cache.mjs --hash-pasta <dir>` imprime o hash da pasta, o mesmo que o
 * `dist_hash.py` calcula em Python (o teste confere os dois).
 */
import { createHash } from 'node:crypto';
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, readSync, readdirSync, statSync, writeFileSync, renameSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
export const VERSAO_DO_FORMATO = 1;
export const MARCADORES = { projeto: '@@PROJETO@@', dist: '@@DIST@@', url: '@@URL@@' };

const posix = (p) => p.split(path.sep).join('/');
const sha = (dados) => createHash('sha256').update(dados).digest('hex');
/** Ordem de pontos de código, a mesma do `sorted()` do Python (que o hash em Python usa). */
const porBytes = (a, b) => Buffer.compare(Buffer.from(a, 'utf8'), Buffer.from(b, 'utf8'));

export function hashDeTexto(texto) { return sha(texto); }

export function hashArquivo(caminho) {
  const h = createHash('sha256');
  const fd = openSync(caminho, 'r');
  try {
    const bloco = Buffer.allocUnsafe(1024 * 1024);
    for (;;) {
      const n = readSync(fd, bloco, 0, bloco.length, null);
      if (n <= 0) break;
      h.update(bloco.subarray(0, n));
    }
  } finally { closeSync(fd); }
  return h.digest('hex');
}

/** Caminhos relativos (POSIX) dos arquivos da pasta, em ordem. Não desce em pasta ligada por link. */
export function arquivosDaPasta(pasta, ignorar = null) {
  const achados = [];
  const andar = (dir, rel) => {
    let itens;
    try { itens = readdirSync(dir, { withFileTypes: true }); } catch (_) { return; }
    for (const it of itens) {
      const r = rel ? `${rel}/${it.name}` : it.name;
      const completo = path.join(dir, it.name);
      let ehPasta = it.isDirectory();
      let ehArquivo = it.isFile();
      if (it.isSymbolicLink()) {
        let alvo = null;
        try { alvo = statSync(completo); } catch (_) { continue; }
        if (alvo.isDirectory()) continue;      // pasta ligada: o Python também não entra
        ehArquivo = alvo.isFile(); ehPasta = false;
      }
      if (ignorar && ignorar(r, ehPasta)) continue;
      if (ehPasta) andar(completo, r);
      else if (ehArquivo) achados.push(r);
    }
  };
  andar(pasta, '');
  return achados.sort(porBytes);
}

/** Hash do CONTEÚDO da pasta: sha256 de `caminho NUL sha256-do-arquivo LF`, em ordem. A data do arquivo não entra. */
export function hashPasta(pasta, ignorar = null) {
  const h = createHash('sha256');
  for (const rel of arquivosDaPasta(pasta, ignorar)) {
    h.update(Buffer.from(rel, 'utf8'));
    h.update(Buffer.from([0]));
    h.update(Buffer.from(hashArquivo(path.join(pasta, ...rel.split('/'))), 'ascii'));
    h.update(Buffer.from('\n'));
  }
  return h.digest('hex');
}

/** O que os gates ESCREVEM no projeto ou que é copiado em outro lugar: fora do hash do projeto. */
export function ignorarNoProjeto(rel, ehPasta) {
  const topo = rel.split('/')[0];
  if (rel.includes('/')) return ['node_modules', '.git', '__pycache__'].includes(path.posix.basename(rel)) && ehPasta;
  if (ehPasta) return ['gates', 'auditoria', 'node_modules', '.git', 'dist', '__pycache__'].includes(topo);
  return topo === '.wave-auditoria.json';
}

const ehTeste = (nome) => /^test-/.test(nome) || /\.test\.(mjs|cjs|js)$/.test(nome);
const ignorarNosScripts = (rel, ehPasta) => {
  const nome = path.posix.basename(rel);
  if (ehPasta) return ['fixtures', 'node_modules', '__pycache__', '.git'].includes(nome);
  return ehTeste(nome) || nome.endsWith('.pyc');
};

/** Versão dos scripts: o conteúdo da(s) pasta(s) de gates e da `references/` da skill. */
export function versaoDosScripts(pastas) {
  const h = createHash('sha256');
  for (const [rotulo, dir] of pastas) {
    h.update(Buffer.from(`${rotulo}\0${existsSync(dir) ? hashPasta(dir, ignorarNosScripts) : 'ausente'}\n`));
  }
  return h.digest('hex');
}

/** Versão do Playwright (best-effort, sem chamar o npm): sem ela a chave vale sem essa parte. */
export function versaoDoPlaywright() {
  const req = createRequire(import.meta.url);
  const candidatos = [];
  try { candidatos.push(req.resolve('playwright/package.json')); } catch (_) { /* não está no caminho local */ }
  const bin = path.dirname(process.execPath);
  if (process.env.npm_config_prefix) candidatos.push(path.join(process.env.npm_config_prefix, 'lib', 'node_modules', 'playwright', 'package.json'));
  candidatos.push(path.join(bin, '..', 'lib', 'node_modules', 'playwright', 'package.json'));
  if (process.env.APPDATA) candidatos.push(path.join(process.env.APPDATA, 'npm', 'node_modules', 'playwright', 'package.json'));
  for (const c of candidatos) {
    try { return JSON.parse(readFileSync(c, 'utf8')).version || '?'; } catch (_) { /* próximo */ }
  }
  return '?';
}

export function ambiente() {
  return `${process.platform} node${process.versions.node.split('.')[0]} playwright${versaoDoPlaywright()}`;
}

/**
 * Memória de uma execução: o hash da dist, do projeto e dos scripts é calculado UMA vez por comando
 * (vários gates leem o mesmo conteúdo), mas sempre do disco: nada é lembrado entre um comando e outro.
 */
export function criarMemo() {
  const guardado = new Map();
  const uma = (chave, calcular) => { if (!guardado.has(chave)) guardado.set(chave, calcular()); return guardado.get(chave); };
  return {
    dist: (dir) => uma(`dist:${dir}`, () => (existsSync(dir) ? hashPasta(dir) : 'ausente')),
    projeto: (dir) => uma(`projeto:${dir}`, () => hashPasta(dir, ignorarNoProjeto)),
    scripts: (pastas) => uma(`scripts:${pastas.map((p) => p.join('=')).join('|')}`, () => versaoDosScripts(pastas)),
    ambiente: () => uma('ambiente', ambiente),
  };
}

/**
 * Argumentos do gate com marcadores no lugar de projeto, dist e porta, e o que o gate lê.
 * `g.args(ctx)` é o mesmo que roda de verdade; aqui só o chamamos com caminhos de mentira.
 */
export function entradasDoGate(g, opcoes) {
  const ctxM = {
    projeto: MARCADORES.projeto, dist: MARCADORES.dist, url: MARCADORES.url,
    scriptsDir: '@@SCRIPTS@@', opcoes: opcoes || {},
  };
  const args = g.args(ctxM);
  const cita = (m) => args.some((a) => String(a).includes(m));
  return {
    args,
    leProjeto: cita(MARCADORES.projeto),
    leDist: Boolean(g.url || g.dist || cita(MARCADORES.dist) || cita(MARCADORES.url)),
  };
}

/** A chave: hash de tudo que pode mudar o veredito. `partes` fica no registro para quem quiser ver o que mudou. */
export function chaveDoGate(partes) {
  const ordenado = Object.keys(partes).sort().map((k) => `${k}=${partes[k]}`).join('\n');
  return sha(`gate-cache v${VERSAO_DO_FORMATO}\n${ordenado}`);
}

/** Junta as partes do gate com o hash do disco. `memo` vem de criarMemo(). */
export function partesDoGate(g, ctx, memo, pastasDeScripts) {
  const { args, leProjeto, leDist } = entradasDoGate(g, ctx.opcoes);
  const partes = {
    gate: g.nome, arquivo: g.arquivo, argumentos: JSON.stringify(args),
    scripts: memo.scripts(pastasDeScripts), ambiente: memo.ambiente(),
  };
  if (leDist) partes.dist = memo.dist(ctx.dist);
  if (leProjeto) partes.projeto = memo.projeto(ctx.projeto);
  return partes;
}

// ------------------------------------------------------------------------ armazenamento
export const pastaDoCache = (gatesDir) => path.join(gatesDir, '_cache');
const arquivoDoCache = (gatesDir, nome) => path.join(pastaDoCache(gatesDir), `${nome}.json`);

/** O registro guardado do gate, se for legível e do formato atual. Qualquer defeito vira "sem cache". */
export function lerCache(gatesDir, nome) {
  try {
    const r = JSON.parse(readFileSync(arquivoDoCache(gatesDir, nome), 'utf8'));
    if (r && r.versao === VERSAO_DO_FORMATO && r.nome === nome && typeof r.chave === 'string' && r.codigo === 0 && typeof r.laudo === 'string') return r;
  } catch (_) { /* sem registro legível */ }
  return null;
}

/** Só PASSA vira cache. Grava inteiro ou nada (arquivo temporário e troca). */
export function gravarCache(gatesDir, nome, { chave, partes, segundos, rodada, laudo }) {
  mkdirSync(pastaDoCache(gatesDir), { recursive: true });
  const alvo = arquivoDoCache(gatesDir, nome);
  const tmp = `${alvo}.${process.pid}.tmp`;
  const registro = { versao: VERSAO_DO_FORMATO, nome, chave, partes, codigo: 0, segundos, rodada, quando: new Date().toISOString(), laudo };
  writeFileSync(tmp, JSON.stringify(registro, null, 2), 'utf8');
  renameSync(tmp, alvo);
}

/** O cache vale se a chave de agora é a guardada. */
export function acerto(gatesDir, nome, chave) {
  const r = lerCache(gatesDir, nome);
  return r && r.chave === chave ? r : null;
}

// ------------------------------------------------------------------------ linha de comando
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const i = process.argv.indexOf('--hash-pasta');
  if (i < 0 || !process.argv[i + 1]) { console.error('uso: node gates-cache.mjs --hash-pasta <pasta>'); process.exit(2); }
  const pasta = path.resolve(process.argv[i + 1]);
  if (!existsSync(pasta)) { console.error(`pasta não encontrada: ${posix(pasta)}`); process.exit(2); }
  console.log(hashPasta(pasta));
}
