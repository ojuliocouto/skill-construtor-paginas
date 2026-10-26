#!/usr/bin/env node
/**
 * PROVAR: a prova de tela da página feita de uma vez, com as provas que não dependem uma da outra rodando ao mesmo tempo.
 *
 * Por que existe (corte 4 da auditoria de velocidade). A prova inteira custava 191,7 s de máquina: prints (`screenshot-prova.js`,
 * 39,9 s), vídeo de rolagem (`gravar-video.js`, 85,4 s) e quadros de animação (`anim.mjs` e `prancha.py`, 63,7 s), uma depois da
 * outra, 2 a 3 vezes por página. Nenhuma depende da outra: cada uma abre o PRÓPRIO navegador e grava arquivos diferentes.
 * Aqui elas rodam DUAS por vez (a regra de memória: no máximo 2 processos pesados de navegador), e o vídeo ainda grava desktop e
 * celular juntos. O resultado é o mesmo, só mais curto.
 *
 * O que NÃO faz: não muda argumento nem limite de nenhuma prova, não lê os PNG por você (abra as pranchas) e não aprova a
 * página. Cada prova é o mesmo script de sempre, com os argumentos do `criar.md`.
 *
 * Uso:
 *   node scripts/provar.mjs --projeto <dir>                       # serve a <dir>/dist e roda as três provas
 *   node scripts/provar.mjs --projeto <dir> --url http://127.0.0.1:8765/ --click "#comprar"
 *
 * Provas (nome no relatório):
 *   prints    screenshot-prova.js <url> <dir>/provas --com-360 --com-320 [--click <sel>]   (identidade, scrollY 0, clique)
 *   video     gravar-video.js <url> --saida <dir>/videos
 *   animacao  anim.mjs --url <url> --saida <dir>/prova/anim --secoes <secoes.json>, e DEPOIS o prancha.py (só se o anim.mjs passou)
 *             Sem o secoes.json a animação é PULADA, dizendo como gerar (`plano-para-secoes.py`); `--sem-anim` pula de propósito.
 *
 * Opções:
 *   --projeto <dir>      pasta da página. Obrigatória.
 *   --url <url>          página já servida. Sem ela, o comando monta a dist (a menos de --sem-montar) e a serve numa porta livre.
 *   --click <seletor>    repassado ao screenshot-prova.js (a prova do botão principal).
 *   --secoes <arquivo>   secoes.json da animação (padrão: <dir>/prova/anim/secoes.json).
 *   --sem-anim           não roda a animação.
 *   --so <provas>        roda só estas provas (prints, video, animacao; várias separadas por vírgula). 3.6.2: depois de mudar a dist,
 *                        `--so animacao` refaz só os quadros e a prancha, no mesmo servidor de porta livre que este comando sobe, sem
 *                        digitar porta e sem refazer prints e vídeo (no teste de aluno da 3.6.1 a prova de animação foi refeita à
 *                        mão numa porta fixa e 49 s se perderam). As outras saem como PULADA, dizendo que foi o --so.
 *   --paralelo <n>       provas ao mesmo tempo (padrão 2; nunca passa de 2).
 *   --sem-montar         não monta a dist antes (use se ela já está montada).
 *   --sem-registrar      não grava a "identidade" na wave.
 *   --tempo-max <s>      segundos por prova antes de interromper e reprovar (padrão 900).
 *   --scripts-dir <dir>  pasta dos scripts (padrão: a desta skill; os testes trocam por scripts de mentira).
 *
 * Registro na wave: o exit real do screenshot-prova.js vira o gate `identidade` (`wave.py gates-lote`), no lugar de digitar.
 * Tempo: leva de 1 a 2 minutos. Rode em PRIMEIRO plano, com tempo-limite de 10 minutos (Bash: timeout de 600000 ms), nunca em segundo
 * plano com laço de espera.
 *
 * Saída: 0 se todas passam, 1 se alguma reprova, 2 se o pedido está errado. Laudo de cada prova: `<dir>/gates/prova-<nome>.txt`.
 */
import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { executar, fmt, pool, subirServidor } from './rodar-gates.mjs';

const AQUI = path.dirname(fileURLToPath(import.meta.url));
const posix = (p) => String(p).split(path.sep).join('/');
const TETO_DE_NAVEGADORES = 2;
const NOMES_DAS_PROVAS = ['prints', 'video', 'animacao'];

function lerArgs(argv) {
  const o = { paralelo: TETO_DE_NAVEGADORES, tempoMax: 900 };
  const pega = (i) => { if (i + 1 >= argv.length || argv[i + 1].startsWith('--')) throw new Error(`${argv[i]} pede um valor`); return argv[i + 1]; };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--projeto') o.projeto = pega(i++);
    else if (a === '--url') o.url = pega(i++);
    else if (a === '--click') o.click = pega(i++);
    else if (a === '--secoes') o.secoes = pega(i++);
    else if (a === '--so') o.so = pega(i++).split(',').map((x) => x.trim()).filter(Boolean);
    else if (a === '--paralelo') o.paralelo = Number(pega(i++));
    else if (a === '--tempo-max') o.tempoMax = Number(pega(i++));
    else if (a === '--scripts-dir') o.scriptsDir = pega(i++);
    else if (a === '--sem-anim') o.semAnim = true;
    else if (a === '--sem-montar') o.semMontar = true;
    else if (a === '--sem-registrar') o.semRegistrar = true;
    else if (a === '--ajuda' || a === '-h') o.ajuda = true;
    else throw new Error(`opção desconhecida: ${a}`);
  }
  return o;
}

/** As provas, na forma que o `executar` do rodar-gates entende: arquivo (.py roda pelo py.mjs) e args(ctx). */
function provas(ctx) {
  const { projeto, url, o } = ctx;
  const animacao = path.join(projeto, 'prova', 'anim');
  const secoes = o.secoes ? path.resolve(o.secoes) : path.join(animacao, 'secoes.json');
  return {
    secoes,
    prints: { nome: 'prints', arquivo: 'screenshot-prova.js', peso: 40,
      args: () => [url, path.join(projeto, 'provas'), '--com-360', '--com-320', ...(o.click ? ['--click', o.click] : [])] },
    video: { nome: 'video', arquivo: 'gravar-video.js', peso: 45,
      args: () => [url, '--saida', path.join(projeto, 'videos')] },
    anim: { nome: 'animacao', arquivo: 'anim.mjs', peso: 64,
      args: () => ['--url', url, '--saida', animacao, '--secoes', secoes] },
    prancha: { nome: 'animacao-prancha', arquivo: 'prancha.py', peso: 3,
      args: () => ['--pasta', animacao, '--secoes', secoes] },
  };
}

async function principal() {
  let o;
  try { o = lerArgs(process.argv.slice(2)); } catch (e) { console.error(e.message); process.exit(2); }
  if (o.ajuda) { console.log('Uso: node provar.mjs --projeto <dir> [--url <url>] [--click <sel>] [--sem-anim] [--paralelo 2] (veja o cabeçalho do arquivo)'); process.exit(0); }
  if (!o.projeto) { console.error('faltou --projeto <pasta da página>'); process.exit(2); }
  const invalidas = (o.so || []).filter((n) => !NOMES_DAS_PROVAS.includes(n));
  if (invalidas.length || (o.so && !o.so.length)) {
    console.error(`--so: prova desconhecida (${invalidas.join(', ') || 'nenhuma informada'}). As provas são: ${NOMES_DAS_PROVAS.join(', ')}.`);
    process.exit(2);
  }
  const projeto = path.resolve(o.projeto);
  if (!existsSync(projeto)) { console.error(`pasta não encontrada: ${projeto}`); process.exit(2); }
  const scriptsDir = path.resolve(o.scriptsDir || AQUI);
  const dist = path.join(projeto, 'dist');
  const gatesDir = path.join(projeto, 'gates');
  const teto = Math.max(1, Math.min(TETO_DE_NAVEGADORES, Math.floor(o.paralelo) || 1));
  mkdirSync(gatesDir, { recursive: true });
  const t0 = Date.now();
  console.log(`PROVAR  projeto: ${posix(projeto)}`);
  console.log(`Prova de tela: prints, vídeo e quadros de animação, ${teto} por vez. Leva de 1 a 2 minutos: rode em primeiro plano, com tempo-limite de 10 minutos (Bash: timeout de 600000 ms), e nunca em segundo plano com laço de espera.`);

  // 1. a página que as provas olham
  let servidor = null;
  let url = o.url;
  if (!url) {
    if (!o.semMontar) {
      const montar = { nome: 'montar-dist', arquivo: 'montar-dist.py', args: () => ['--projeto', projeto, '--css-em-linha'] };
      const r = await executar(montar, { projeto, scriptsDir: AQUI }, path.join(gatesDir, 'prova-montar-dist.txt'), o.tempoMax);
      console.log(`montar-dist: saída ${r.codigo} em ${fmt(r.segundos)} s (gates/prova-montar-dist.txt)`);
      if (r.codigo !== 0) { console.log(readFileSync(path.join(gatesDir, 'prova-montar-dist.txt'), 'utf8')); console.log('REPROVA  montar-dist: sem a dist montada as provas não têm o que olhar.'); process.exit(1); }
    }
    if (!existsSync(path.join(dist, 'index.html'))) {
      console.error(`não há ${posix(path.join(dist, 'index.html'))}: monte a dist (rode sem --sem-montar) ou passe --url com a página já servida`);
      process.exit(2);
    }
    servidor = await subirServidor(dist, scriptsDir);
    url = servidor.url;
    console.log(`servindo a dist em ${url}`);
  }

  // 2. as provas
  const ctx = { projeto, url, scriptsDir, o };
  const p = provas(ctx);
  const resultados = new Map();
  const pulados = [];
  const rodarSimples = (prova, arquivoLaudo) => executar(prova, ctx, arquivoLaudo, o.tempoMax);
  const tarefas = [];
  // Ordem de largada: a mais longa primeiro, para a fila fechar junto.
  const entradas = [
    { id: 'animacao', peso: p.anim.peso, rodar: async () => {
      const laudo = path.join(gatesDir, 'prova-animacao.txt');
      let r = await rodarSimples(p.anim, laudo);
      if (r.codigo === 0) {
        const r2 = await rodarSimples(p.prancha, path.join(gatesDir, 'prova-animacao-prancha.txt'));
        // o laudo da animação junta os dois, e o tempo é a soma
        writeFileSync(laudo, `${readFileSync(laudo, 'utf8')}\n----- prancha.py -----\n${readFileSync(path.join(gatesDir, 'prova-animacao-prancha.txt'), 'utf8')}`, 'utf8');
        r = { codigo: r2.codigo, segundos: r.segundos + r2.segundos };
      }
      resultados.set('animacao', r);
    } },
    { id: 'video', peso: p.video.peso, rodar: async () => { resultados.set('video', await rodarSimples(p.video, path.join(gatesDir, 'prova-video.txt'))); } },
    { id: 'prints', peso: p.prints.peso, rodar: async () => { resultados.set('prints', await rodarSimples(p.prints, path.join(gatesDir, 'prova-prints.txt'))); } },
  ];
  for (const n of NOMES_DAS_PROVAS) if (o.so && !o.so.includes(n)) pulados.push([n, `fora do --so (só rodam: ${o.so.join(', ')})`]);
  if (pulados.some(([n]) => n === 'animacao')) { /* já pulada pelo --so */ }
  else if (o.semAnim) pulados.push(['animacao', 'foi pedido --sem-anim']);
  else if (!existsSync(p.secoes)) pulados.push(['animacao', `não achei ${path.relative(projeto, p.secoes).split(path.sep).join('/')}: gere com plano-para-secoes.py (veja o criar.md, etapa f) e rode de novo`]);
  const puladas = new Set(pulados.map(([id]) => id));
  for (const e of entradas.sort((a, b) => b.peso - a.peso)) if (!puladas.has(e.id)) tarefas.push(e.rodar);
  try { await pool(tarefas, teto); } finally { if (servidor) servidor.parar(); }
  const totalS = (Date.now() - t0) / 1000;

  // 3. relatório
  const ordem = ['prints', 'video', 'animacao'];
  const linhas = ['', '===== RELATÓRIO DA PROVA ====='];
  for (const id of ordem) {
    const pulada = pulados.find(([n]) => n === id);
    if (pulada) { linhas.push(`PULADA   ${id.padEnd(9)} ${pulada[1]}`); continue; }
    const r = resultados.get(id);
    linhas.push(`${r.codigo === 0 ? 'PASSA   ' : 'REPROVA '} ${id.padEnd(9)} ${fmt(r.segundos).padStart(5)} s   gates/prova-${id}.txt${r.codigo === 0 ? '' : `   (saída ${r.codigo})`}`);
  }
  const reprovadas = ordem.filter((id) => resultados.has(id) && resultados.get(id).codigo !== 0);
  if (reprovadas.length) {
    linhas.push('', '----- FALHAS (fim do laudo de cada prova que reprovou) -----');
    for (const id of reprovadas) {
      const txt = readFileSync(path.join(gatesDir, `prova-${id}.txt`), 'utf8').trimEnd().split(/\r?\n/).slice(-30).join('\n');
      linhas.push('', `### ${id} (saída ${resultados.get(id).codigo})`, txt || '(a prova não imprimiu nada)');
    }
  }
  const somaS = [...resultados.values()].reduce((s, r) => s + r.segundos, 0);
  linhas.push('', `Total: ${fmt(totalS)} s de relógio (soma das provas: ${fmt(somaS)} s, ${teto} por vez).`);
  linhas.push(reprovadas.length ? `RESULTADO: REPROVA em ${reprovadas.length} de ${resultados.size}: ${reprovadas.join(', ')}.` : `RESULTADO: PASSA em ${resultados.size} de ${resultados.size}${pulados.length ? ` (${pulados.length} pulada: ${pulados.map(([n]) => n).join(', ')})` : ''}.`);
  linhas.push(registrarIdentidade({ o, resultados, projeto, gatesDir }));
  linhas.push('Este comando não lê as imagens: abra os PNG (provas/, videos/prancha-*.png, prova/anim/) com os próprios olhos antes de declarar pronto.');
  console.log(linhas.join('\n'));
  process.exit(reprovadas.length ? 1 : 0);
}

/** O exit real do screenshot-prova.js é o gate `identidade` da wave. Grava por `wave.py gates-lote`; devolve a linha do relatório. */
function registrarIdentidade({ o, resultados, projeto, gatesDir }) {
  if (o.semRegistrar) return 'Wave: --sem-registrar, não registrei nada. Registre à mão: wave.py gate identidade --exit <0|1>.';
  const r = resultados.get('prints');
  if (!r) return 'Wave: a prova de prints não rodou; nada a registrar.';
  const arquivo = path.join(gatesDir, '_wave-prova.json');
  const detalhe = `provar: screenshot-prova.js (identidade${o.click ? ' e clique' : ''}) ${r.codigo === 0 ? 'PASSA' : `REPROVA (saída ${r.codigo})`} (gates/prova-prints.txt)`;
  writeFileSync(arquivo, JSON.stringify({ gates: [{ nome: 'identidade', exit: r.codigo, detalhe }] }, null, 2), 'utf8');
  const w = spawnSync(process.execPath, [path.join(AQUI, 'py.mjs'), path.join(AQUI, 'wave.py'), '--projeto', projeto, 'gates-lote', '--arquivo', arquivo], {
    encoding: 'utf8', windowsHide: true, timeout: 60000, env: { ...process.env, PYTHONUTF8: '1', PYTHONIOENCODING: 'utf-8' },
  });
  if (w.status === 0) return 'Wave: 1 gate(s) registrado(s) com o exit real (identidade, wave.py gates-lote).';
  return `Wave: NÃO consegui registrar (saída ${w.status}): ${`${w.stdout || ''}${w.stderr || ''}`.trim().split(/\r?\n/).slice(0, 3).join(' | ')}. Registre à mão: wave.py gate identidade --exit <0|1>.`;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  principal().catch((e) => { console.error(e && e.stack ? e.stack : String(e)); process.exit(1); });
}
