#!/usr/bin/env node
/**
 * RODAR-GATES: todos os gates mecânicos da etapa f do `criar.md` num comando só, em paralelo,
 * com UM relatório no fim.
 *
 * Por que existe (3.5.8, teste real de 3 h 15 min). Os gates mecânicos custaram 37 minutos em 6 a
 * 10 rodadas: cada rodada completa levava uns 7 min porque os gates rodavam um depois do outro, e
 * o modelo corrigia um, rodava outro e descobria a falha seguinte. Aqui eles rodam juntos, e o
 * relatório traz TODAS as falhas de uma vez, para corrigir tudo e rodar de novo uma vez só.
 *
 * O que NÃO faz: não substitui nenhum gate, não muda argumento nem limite de nenhum e não aprova
 * nada. Cada gate é o mesmo script de sempre, com os mesmos argumentos do `criar.md`; o comando só
 * os chama (sem shell), junta a saída de cada um em `gates/<nome>-r<N>.txt` e sai com 1 se
 * QUALQUER um reprovar. Um gate que quebra, some ou estoura o tempo máximo também reprova.
 *
 * Uso:
 *   node scripts/rodar-gates.mjs --projeto <dir>                    # todos, em paralelo
 *   node scripts/rodar-gates.mjs --projeto <dir> --so texto,ritmo   # só esses
 *   node scripts/rodar-gates.mjs --projeto <dir> --reprovados       # só o que reprovou por último
 *   node scripts/rodar-gates.mjs --lista                            # mostra o conjunto
 *
 * Opções:
 *   --projeto <dir>      pasta da página (com index.html, PLANO.md, evidencias/ ...). Obrigatória.
 *   --paralelo <n>       teto de gates de navegador ao mesmo tempo (padrão: pela máquina, de 1 a 4).
 *                        Os gates sem navegador (Python rápidos) correm numa pista à parte.
 *   --url <url>          usa uma página já servida em vez de subir um servidor por gate.
 *   --dist <dir>         pasta a servir e a conferir (padrão: <projeto>/dist).
 *   --sem-montar         não roda o montar-dist antes (use se a dist já está montada).
 *   --produto-fisico     repassa ao gate-composicao (negócio de produto físico).
 *   --trafego-real       repassa ao gate-imagens (pessoa identificável de banco reprova).
 *   --com <lista>        liga gates opcionais: animacao, video, sobreposicao.
 *   --publico <dir>      pasta pública do gate de vídeo (--com video).
 *   --fixo <sel> --contra <sel>   seletores do gate de sobreposição (--com sobreposicao).
 *   --tempo-max <s>      segundos por gate antes de interromper e reprovar (padrão 900).
 *   --scripts-dir <dir>  pasta dos gates (padrão: a desta skill; os testes trocam por gates falsos).
 *
 * Saída: 0 se todos passam, 1 se algum reprova, 2 se o pedido está errado (nome de gate, pasta).
 */
import { spawn, spawnSync } from 'node:child_process';
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync, createWriteStream } from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const posix = (p) => String(p).split(path.sep).join('/');

/**
 * Catálogo: a lista oficial do comando. O teste `test-rodar-gates.cjs` a compara com a etapa f do
 * `references/caminhos/criar.md` nos dois sentidos: gate novo no criar.md sem entrar aqui derruba o teste.
 *   nome     = nome da wave (`wave.py gate <nome>`) e do arquivo gates/<nome>-r<N>.txt
 *   arquivo  = script em scripts/ (.py roda pelo py.mjs; .mjs roda pelo Node)
 *   navegador = abre o Chromium (pesa na máquina; conta no teto de concorrência)
 *   url      = precisa da página servida
 *   peso     = ordem de largada estimada (maior primeiro), medida no teste real de 3.5.6
 *   args(c)  = argumentos, iguais aos do criar.md
 */
export const CATALOGO = [
  { nome: 'movimento', arquivo: 'gate-movimento.mjs', navegador: true, url: true, peso: 221,
    args: (c) => ['--url', c.url] },
  { nome: 'responsivo', arquivo: 'gate-responsivo.mjs', navegador: true, url: true, peso: 137,
    args: (c) => ['--url', c.url] },
  { nome: 'oclusao', arquivo: 'gate-oclusao.mjs', navegador: true, url: true, peso: 44,
    args: (c) => ['--url', c.url] },
  { nome: 'simetria', arquivo: 'gate-simetria.mjs', navegador: true, url: true, peso: 18,
    args: (c) => ['--url', c.url] },
  { nome: 'composicao', arquivo: 'gate-composicao.mjs', navegador: true, url: true, peso: 12,
    args: (c) => ['--url', c.url, '--projeto', c.projeto, ...(c.opcoes.produtoFisico ? ['--produto-fisico'] : [])] },
  { nome: 'imagens', arquivo: 'gate-imagens.py', navegador: true, url: true, peso: 9,
    args: (c) => ['--projeto', c.projeto, '--url', c.url, ...(c.opcoes.trafegoReal ? ['--trafego-real'] : [])] },
  { nome: 'texto', arquivo: 'gate-texto.mjs', navegador: true, url: true, peso: 7,
    args: (c) => ['--url', c.url] },
  { nome: 'ritmo', arquivo: 'gate-ritmo.mjs', navegador: true, url: true, peso: 5,
    args: (c) => ['--url', c.url] },
  { nome: 'sem-kicker', arquivo: 'gate-sem-kicker.py', peso: 7,
    args: (c) => [path.join(c.projeto, 'index.html')] },
  { nome: 'classes-mortas', arquivo: 'gate-classes-mortas.py', peso: 1,
    args: (c) => ['--projeto', c.projeto] },
  { nome: 'verdade', arquivo: 'gate-verdade.py', peso: 1,
    args: (c) => ['--projeto', c.projeto] },
  { nome: 'publicacao', arquivo: 'gate-publicacao.py', dist: true, peso: 1,
    args: (c) => ['--dist', c.dist] },
  { nome: 'rastreamento', arquivo: 'gate-rastreamento.py', dist: true, peso: 1,
    args: (c) => ['--dist', c.dist, '--plano', path.join(c.projeto, 'PLANO.md')] },
  { nome: 'plano', arquivo: 'gate-plano.py', peso: 1,
    args: (c) => ['--projeto', c.projeto] },
  { nome: 'referencias', arquivo: 'gate-referencias.py', peso: 1,
    args: (c) => ['--projeto', c.projeto] },
  // Opcionais: dependem de uma etapa anterior ou de argumentos que só o projeto conhece.
  { nome: 'animacao', arquivo: 'gate-animacao.py', opcional: true, peso: 1,
    args: (c) => ['--pasta', path.join(c.projeto, 'prova', 'anim'), '--plano', path.join(c.projeto, 'PLANO.md')] },
  { nome: 'video', arquivo: 'gate-video.mjs', opcional: true, navegador: true, url: true, peso: 60,
    exige: (c) => (c.opcoes.publico ? null : 'o gate de vídeo pede --publico <pasta pública>'),
    args: (c) => ['--url', c.url, '--publico', c.opcoes.publico] },
  { nome: 'sobreposicao', arquivo: 'sobreposicao.mjs', opcional: true, navegador: true, url: true, peso: 20,
    exige: (c) => (c.opcoes.fixo && c.opcoes.contra ? null : 'o gate de sobreposição pede --fixo <seletor> e --contra <seletor>'),
    args: (c) => ['--url', c.url, '--fixo', c.opcoes.fixo, '--contra', c.opcoes.contra] },
];

/** Teto de gates de navegador ao mesmo tempo. Cada Chromium pesa uns 300 a 500 MB e disputa CPU
 *  com os outros: o padrão é metade dos núcleos, entre 1 e 4 (medido em `RELATORIO-PAGINA-358-D.md`). */
export function tetoPadrao(cpus = os.cpus().length) {
  return Math.max(1, Math.min(4, Math.floor(cpus / 2)));
}

/** Aspas para o comando impresso: o que o aluno copia e cola funciona com espaço e acento. */
export function aspas(s) {
  return `"${String(s).replace(/"/g, '\\"')}"`;
}

// ------------------------------------------------------------------------ servidor por gate
// Filhos vivos: se o comando é interrompido (Ctrl+C) ou um gate estoura o tempo, a ÁRVORE inteira morre
// (o py.mjs e o Python dele, o navegador do gate), senão sobra processo pesado rodando escondido.
const VIVOS = new Set();
const NO_WINDOWS = process.platform === 'win32';

function matarArvore(filho) {
  if (!filho || filho.pid === undefined) return;
  try {
    if (NO_WINDOWS) spawnSync('taskkill', ['/pid', String(filho.pid), '/T', '/F'], { windowsHide: true });
    else process.kill(-filho.pid, 'SIGKILL');   // o filho é líder do próprio grupo (detached)
  } catch (_) { try { filho.kill('SIGKILL'); } catch (__) { /* já saiu */ } }
}
function matarTodos() { for (const f of VIVOS) matarArvore(f); }
process.on('exit', matarTodos);
for (const sinal of ['SIGINT', 'SIGTERM']) process.on(sinal, () => { matarTodos(); process.exit(130); });

function portaLivre() {
  return new Promise((resolve, reject) => {
    const s = net.createServer();
    s.on('error', reject);
    s.listen(0, '127.0.0.1', () => { const { port } = s.address(); s.close(() => resolve(port)); });
  });
}

function responde(porta) {
  return new Promise((resolve) => {
    const c = net.connect({ port: porta, host: '127.0.0.1' });
    c.once('connect', () => { c.destroy(); resolve(true); });
    c.once('error', () => resolve(false));
  });
}

/** Sobe o servidor-gzip.py da skill numa porta livre só para este gate. Devolve { url, porta, parar }. */
export async function subirServidor(pasta, scriptsDir = AQUI) {
  const py = path.join(AQUI, 'py.mjs');
  const servidor = path.join(scriptsDir, 'servidor-gzip.py');
  const alvo = existsSync(servidor) ? servidor : path.join(AQUI, 'servidor-gzip.py');
  for (let tentativa = 0; tentativa < 4; tentativa++) {
    const porta = await portaLivre();
    const filho = spawn(process.execPath, [py, alvo, pasta, String(porta)], {
      stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true, detached: process.platform !== 'win32',
      env: { ...process.env, PYTHONUTF8: '1' },
    });
    VIVOS.add(filho);
    let morreu = false;
    filho.on('exit', () => { morreu = true; });
    filho.stdout.on('data', () => {}); filho.stderr.on('data', () => {});
    const limite = Date.now() + 15000;
    while (!morreu && Date.now() < limite && !(await responde(porta))) await new Promise((r) => setTimeout(r, 60));
    if (!morreu && (await responde(porta))) {
      return {
        porta, url: `http://127.0.0.1:${porta}/`,
        parar: () => { VIVOS.delete(filho); matarArvore(filho); },
      };
    }
    VIVOS.delete(filho); matarArvore(filho);
  }
  throw new Error(`não consegui subir o servidor de ${pasta}`);
}

// ------------------------------------------------------------------------ execução de um gate
function comandoDe(g, ctx) {
  const caminho = path.join(ctx.scriptsDir, g.arquivo);
  const args = g.args(ctx);
  if (g.arquivo.endsWith('.py')) return [process.execPath, [path.join(AQUI, 'py.mjs'), caminho, ...args]];
  return [process.execPath, [caminho, ...args]];
}

function executar(g, ctx, saidaArquivo, tempoMaxS) {
  return new Promise((resolve) => {
    const t0 = Date.now();
    const log = createWriteStream(saidaArquivo);
    let tamanho = 0;
    let fechado = false;
    const fim = (codigo, nota) => {
      if (fechado) return; fechado = true;
      if (nota) log.write(`\n${nota}\n`);
      log.end(() => resolve({ codigo, segundos: (Date.now() - t0) / 1000, nota }));
    };
    let filho;
    try {
      const [prog, argv] = comandoDe(g, ctx);
      filho = spawn(prog, argv, {
        cwd: ctx.projeto, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true, detached: !NO_WINDOWS,
        env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
      });
    } catch (e) {
      return fim(126, `não consegui iniciar o gate: ${e.message}`);
    }
    VIVOS.add(filho);
    const quando = setTimeout(() => {
      matarArvore(filho);
      fim(124, `Estourou o tempo máximo de ${tempoMaxS} s e foi interrompido (conta como reprovado).`);
    }, tempoMaxS * 1000);
    const escreve = (b) => { tamanho += b.length; log.write(b); };
    filho.stdout.on('data', escreve);
    filho.stderr.on('data', escreve);
    filho.on('error', (e) => { clearTimeout(quando); VIVOS.delete(filho); fim(126, `gate não executou: ${e.message}`); });
    filho.on('close', (codigo, sinal) => {
      clearTimeout(quando);
      VIVOS.delete(filho);
      fim(codigo === null ? (sinal ? 128 : 1) : codigo);
    });
  });
}

/** Pool: roda `tarefas` (funções async) com no máximo `limite` ao mesmo tempo. */
async function pool(tarefas, limite) {
  const fila = [...tarefas];
  const trabalhadores = Array.from({ length: Math.max(1, Math.min(limite, fila.length || 1)) }, async () => {
    while (fila.length) { const t = fila.shift(); await t(); }
  });
  await Promise.all(trabalhadores);
}

// ------------------------------------------------------------------------ histórico das rodadas
export function lerExecucoes(arquivo) {
  if (!existsSync(arquivo)) return [];
  return readFileSync(arquivo, 'utf8').split(/\r?\n/).map((l) => l.trim()).filter(Boolean).map((l) => {
    const m = /^(\d+)\s+(\S+)\s+(-?\d+)$/.exec(l);
    return m ? { rodada: Number(m[1]), nome: m[2], codigo: Number(m[3]) } : null;
  }).filter(Boolean);
}

/** Último resultado de cada gate em todas as rodadas (uma rodada parcial não apaga o resto). */
export function ultimoDeCada(execucoes) {
  const mapa = new Map();
  for (const e of execucoes) mapa.set(e.nome, e);
  return mapa;
}

// ------------------------------------------------------------------------ linha de comando
function lerArgs(argv) {
  const o = { so: null, com: [], paralelo: null, tempoMax: 900 };
  const pega = (i) => { if (i + 1 >= argv.length || argv[i + 1].startsWith('--')) throw new Error(`${argv[i]} pede um valor`); return argv[i + 1]; };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--projeto') o.projeto = pega(i++);
    else if (a === '--so') o.so = pega(i++).split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--com') o.com = pega(i++).split(',').map((s) => s.trim()).filter(Boolean);
    else if (a === '--paralelo') o.paralelo = Number(pega(i++));
    else if (a === '--url') o.url = pega(i++);
    else if (a === '--dist') o.dist = pega(i++);
    else if (a === '--publico') o.publico = pega(i++);
    else if (a === '--fixo') o.fixo = pega(i++);
    else if (a === '--contra') o.contra = pega(i++);
    else if (a === '--tempo-max') o.tempoMax = Number(pega(i++));
    else if (a === '--scripts-dir') o.scriptsDir = pega(i++);
    else if (a === '--reprovados') o.reprovados = true;
    else if (a === '--sem-montar') o.semMontar = true;
    else if (a === '--produto-fisico') o.produtoFisico = true;
    else if (a === '--trafego-real') o.trafegoReal = true;
    else if (a === '--lista') o.lista = true;
    else if (a === '--ajuda' || a === '-h') o.ajuda = true;
    else throw new Error(`opção desconhecida: ${a}`);
  }
  return o;
}

function linhaDeRepeticao(o, extra) {
  const partes = ['node', aspas(posix(path.join(AQUI, 'rodar-gates.mjs'))), '--projeto', aspas(posix(path.resolve(o.projeto)))];
  for (const [k, v] of [['--dist', o.dist], ['--url', o.url], ['--publico', o.publico], ['--fixo', o.fixo], ['--contra', o.contra]]) if (v) partes.push(k, aspas(posix(v)));
  if (o.paralelo) partes.push('--paralelo', String(o.paralelo));
  if (o.com.length) partes.push('--com', o.com.join(','));
  if (o.produtoFisico) partes.push('--produto-fisico');
  if (o.trafegoReal) partes.push('--trafego-real');
  if (o.semMontar) partes.push('--sem-montar');
  partes.push(...extra);
  return partes.join(' ');
}

const fmt = (s) => (s < 10 ? s.toFixed(1) : Math.round(s).toString()).replace('.', ',');

async function principal() {
  let o;
  try { o = lerArgs(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exit(2); }
  if (o.ajuda) { console.log('Uso: node rodar-gates.mjs --projeto <dir> [--so a,b | --reprovados] [--paralelo N] ... (veja o cabeçalho do arquivo)'); process.exit(0); }
  if (o.lista) {
    console.log('Gates do comando (os marcados [opcional] só rodam com --com):');
    for (const g of CATALOGO) console.log(`  ${g.nome.padEnd(15)} ${g.arquivo}${g.navegador ? '  [navegador]' : ''}${g.opcional ? '  [opcional]' : ''}`);
    process.exit(0);
  }
  if (!o.projeto) { console.error('faltou --projeto <pasta da página>'); process.exit(2); }
  const projeto = path.resolve(o.projeto);
  if (!existsSync(projeto)) { console.error(`pasta não encontrada: ${projeto}`); process.exit(2); }
  const scriptsDir = path.resolve(o.scriptsDir || AQUI);
  const dist = path.resolve(o.dist || path.join(projeto, 'dist'));
  const gatesDir = path.join(projeto, 'gates');
  const execArquivo = path.join(gatesDir, '_execucoes.txt');
  const historico = lerExecucoes(execArquivo);
  const rodada = historico.reduce((m, e) => Math.max(m, e.rodada), 0) + 1;

  // 1. quais gates
  const nomesValidos = new Set(CATALOGO.map((g) => g.nome));
  for (const n of [...(o.so || []), ...o.com]) {
    if (!nomesValidos.has(n)) { console.error(`gate desconhecido: "${n}". Os nomes são: ${CATALOGO.map((g) => g.nome).join(', ')}`); process.exit(2); }
  }
  const comOpcionais = new Set(o.com);
  let escolhidos = CATALOGO.filter((g) => !g.opcional || comOpcionais.has(g.nome) || (o.so && o.so.includes(g.nome)));
  if (o.so) escolhidos = CATALOGO.filter((g) => o.so.includes(g.nome));
  if (o.reprovados) {
    const ult = ultimoDeCada(historico);
    escolhidos = escolhidos.filter((g) => { const e = ult.get(g.nome); return !e || e.codigo !== 0; });
    if (!escolhidos.length) {
      console.log('Nenhum gate reprovado na última execução de cada um: nada para rodar de novo. Faça uma rodada completa antes de seguir.');
      process.exit(0);
    }
  }
  const ctxBase = { projeto, dist, scriptsDir, opcoes: { produtoFisico: o.produtoFisico, trafegoReal: o.trafegoReal, publico: o.publico, fixo: o.fixo, contra: o.contra } };
  for (const g of escolhidos) {
    const motivo = g.exige && g.exige(ctxBase);
    if (motivo) { console.error(motivo); process.exit(2); }
  }

  const teto = o.paralelo && o.paralelo >= 1 ? Math.floor(o.paralelo) : tetoPadrao();
  mkdirSync(gatesDir, { recursive: true });
  const t0 = Date.now();
  console.log(`RODAR-GATES  rodada ${rodada}  projeto: ${posix(projeto)}`);
  console.log(`Máquina: ${process.platform}, ${os.cpus().length} CPUs. ${escolhidos.length} gate(s); teto de ${teto} de navegador ao mesmo tempo.`);

  // 2. montar a dist (os gates de tela olham o que vai para o ar)
  const precisaDist = escolhidos.some((g) => g.url || g.dist);
  if (precisaDist && !o.semMontar && !o.url) {
    const montar = { nome: 'montar-dist', arquivo: 'montar-dist.py', args: (c) => ['--projeto', c.projeto, '--css-em-linha'] };
    const r = await executar(montar, ctxBase, path.join(gatesDir, `montar-dist-r${rodada}.txt`), o.tempoMax);
    console.log(`montar-dist: saída ${r.codigo} em ${fmt(r.segundos)} s (gates/montar-dist-r${rodada}.txt)`);
    if (r.codigo !== 0) {
      console.log(readFileSync(path.join(gatesDir, `montar-dist-r${rodada}.txt`), 'utf8'));
      console.log('REPROVA  montar-dist: sem a dist montada os gates não têm o que medir. Corrija e rode de novo.');
      process.exit(1);
    }
  }
  if (escolhidos.some((g) => g.url) && !o.url && !existsSync(dist)) {
    console.error(`pasta a servir não existe: ${posix(dist)} (rode sem --sem-montar ou passe --url)`);
    process.exit(2);
  }

  // 3. rodar: gates de navegador no pool com teto; os demais, numa pista à parte
  const resultados = new Map();
  const rodarUm = (g) => async () => {
    let servidor = null;
    const ctx = { ...ctxBase, url: o.url };
    try {
      if (g.url && !o.url) { servidor = await subirServidor(dist, scriptsDir); ctx.url = servidor.url; }
    } catch (e) {
      resultados.set(g.nome, { codigo: 126, segundos: 0, nota: e.message });
      writeFileSync(path.join(gatesDir, `${g.nome}-r${rodada}.txt`), `${e.message}\n`);
      return;
    }
    const arquivo = path.join(gatesDir, `${g.nome}-r${rodada}.txt`);
    const r = await executar(g, ctx, arquivo, o.tempoMax);
    if (servidor) servidor.parar();
    resultados.set(g.nome, r);
    process.stdout.write(`  ${r.codigo === 0 ? 'passa  ' : 'REPROVA'} ${g.nome} (${fmt(r.segundos)} s)\n`);
  };
  const porPeso = (a, b) => b.peso - a.peso;
  const pesados = escolhidos.filter((g) => g.navegador).sort(porPeso);
  const leves = escolhidos.filter((g) => !g.navegador).sort(porPeso);
  await Promise.all([pool(pesados.map(rodarUm), teto), pool(leves.map(rodarUm), 2)]);
  const totalS = (Date.now() - t0) / 1000;

  // 4. gravar o histórico (na ordem do catálogo, como o fluxo antigo)
  for (const g of escolhidos) {
    const r = resultados.get(g.nome);
    appendFileSync(execArquivo, `${rodada} ${g.nome} ${r.codigo}\n`);
  }

  // 5. relatório consolidado
  const linhas = [];
  linhas.push('', `===== RELATÓRIO DA RODADA ${rodada} =====`);
  for (const g of escolhidos) {
    const r = resultados.get(g.nome);
    linhas.push(`${r.codigo === 0 ? 'PASSA   ' : 'REPROVA '} ${g.nome.padEnd(15)} ${fmt(r.segundos).padStart(5)} s   gates/${g.nome}-r${rodada}.txt${r.codigo === 0 ? '' : `   (saída ${r.codigo})`}`);
  }
  const reprovados = escolhidos.filter((g) => resultados.get(g.nome).codigo !== 0);
  const somaS = [...resultados.values()].reduce((s, r) => s + r.segundos, 0);
  const avisos = [];
  for (const g of escolhidos) {
    const r = resultados.get(g.nome);
    if (r.codigo !== 0) continue;
    const txt = readFileSync(path.join(gatesDir, `${g.nome}-r${rodada}.txt`), 'utf8');
    for (const l of txt.split(/\r?\n/)) if (/\bAVIS[AO]\b|\bWARN(ING)?\b/.test(l)) avisos.push(`  [${g.nome}] ${l.trim()}`);
  }
  if (avisos.length) {
    const mostrar = avisos.slice(0, 30);
    linhas.push('', '----- AVISOS dos gates que passaram (não reprovam, mas leia) -----', ...mostrar);
    if (avisos.length > mostrar.length) linhas.push(`  (mais ${avisos.length - mostrar.length} aviso(s): estão nos arquivos gates/<nome>-r${rodada}.txt)`);
  }
  if (reprovados.length) {
    linhas.push('', '----- FALHAS (texto inteiro de cada gate que reprovou) -----');
    for (const g of reprovados) {
      const r = resultados.get(g.nome);
      const txt = readFileSync(path.join(gatesDir, `${g.nome}-r${rodada}.txt`), 'utf8').trimEnd();
      linhas.push('', `### ${g.nome} (saída ${r.codigo}, ${fmt(r.segundos)} s)`, txt || '(o gate não imprimiu nada)');
    }
  }
  linhas.push('', `Total: ${fmt(totalS)} s de relógio (soma dos gates: ${fmt(somaS)} s, ${escolhidos.length} gate(s), teto ${teto}).`);
  if (reprovados.length) {
    linhas.push(`RESULTADO: REPROVA em ${reprovados.length} de ${escolhidos.length}: ${reprovados.map((g) => g.nome).join(', ')}.`);
    linhas.push('Corrija TUDO o que está acima e repita só esses:');
    linhas.push(`  ${linhaDeRepeticao(o, ['--reprovados'])}`);
    linhas.push('Quando tudo passar, faça uma rodada completa (sem --so e sem --reprovados) antes de registrar na wave.');
  } else {
    linhas.push(`RESULTADO: PASSA em ${escolhidos.length} de ${escolhidos.length}.`);
    if (o.so || o.reprovados) linhas.push('Foi uma rodada parcial: falta a rodada completa no fim, antes de registrar na wave.');
  }
  linhas.push('Registre na wave o exit REAL de cada gate (wave.py gate <nome> --exit <0|1>): este comando não registra nem aprova nada.');
  const texto = linhas.join('\n');
  console.log(texto);
  writeFileSync(path.join(gatesDir, `_relatorio-r${rodada}.txt`), texto + '\n', 'utf8');
  process.exit(reprovados.length ? 1 : 0);
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  principal().catch((e) => { console.error(e && e.stack ? e.stack : String(e)); process.exit(1); });
}
