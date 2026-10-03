/** Prévia das 3 direções da etapa PLANO: três HTML de primeira dobra viram um PNG de cada
 *  (desktop e celular) e o plano/direcoes.png lado a lado; com menos de 3 o script reprova.
 *  O modo --miniaturas grava uma imagem por formato de seção para o cardápio do plano. */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const SCRIPT = path.join(__dirname, 'previa-direcoes.mjs');
const pasta = fs.mkdtempSync(path.join(os.tmpdir(), 'previa-dir-'));
const cores = ['#2f4858', '#f6ae2d', '#86bbd8'];
const arquivos = cores.map((cor, i) => {
  const f = path.join(pasta, `dir-${i}.html`);
  fs.writeFileSync(f, `<!doctype html><html lang="pt-BR"><body style="margin:0;background:${cor}"><h1 style="font:64px Georgia;padding:80px">Direção ${i + 1}</h1></body></html>`);
  return f;
});

let falhas = 0;
const checa = (nome, ok, detalhe = '') => {
  console.log(`${ok ? 'ok  ' : 'FALHA'} ${nome}${ok ? '' : `: ${detalhe}`}`);
  if (!ok) falhas += 1;
};
const largura = (f) => fs.readFileSync(f).readUInt32BE(16);
const altura = (f) => fs.readFileSync(f).readUInt32BE(20);
const rodar = (argv) => spawnSync(process.execPath, [SCRIPT, ...argv], { encoding: 'utf8' });

const saida = path.join(pasta, 'plano');
let r = rodar(['--saida', saida, ...arquivos]);
checa('3 direções saem com exit 0', r.status === 0, r.stdout + r.stderr);
for (const letra of ['a', 'b', 'c']) {
  const d = path.join(saida, `direcao-${letra}.png`);
  const m = path.join(saida, `direcao-${letra}-celular.png`);
  checa(`direcao-${letra}.png gravada em 1440 de largura`, fs.existsSync(d) && largura(d) === 1440, fs.existsSync(d) ? String(largura(d)) : 'não existe');
  checa(`direcao-${letra}-celular.png gravada em 390`, fs.existsSync(m) && largura(m) === 390, fs.existsSync(m) ? String(largura(m)) : 'não existe');
}
const lado = path.join(saida, 'direcoes.png');
checa('direcoes.png existe', fs.existsSync(lado));
if (fs.existsSync(lado)) {
  checa('direcoes.png é mais larga que alta (lado a lado)', largura(lado) > altura(lado), `${largura(lado)}x${altura(lado)}`);
  checa('direcoes.png tem tamanho de comparação (>= 1200 px)', largura(lado) >= 1200, String(largura(lado)));
}
checa('nenhum HTML temporário sobra na saída', !fs.readdirSync(saida).some((f) => f.endsWith('.html')), fs.readdirSync(saida).join(','));

r = rodar(['--saida', path.join(pasta, 'dois'), arquivos[0], arquivos[1]]);
checa('2 direções reprovam com exit 1', r.status === 1, `status ${r.status}`);
checa('a mensagem diz que são 3', /3/.test(r.stdout + r.stderr), r.stdout + r.stderr);

r = rodar(['--saida', path.join(pasta, 'falta'), arquivos[0], arquivos[1], path.join(pasta, 'nao-existe.html')]);
checa('arquivo inexistente reprova com exit 1', r.status === 1, `status ${r.status}`);

const mini = path.join(pasta, 'miniaturas');
const fonte = path.join(pasta, 'secoes');
fs.mkdirSync(fonte);
fs.copyFileSync(arquivos[0], path.join(fonte, 'caixas-iguais.html'));
fs.copyFileSync(arquivos[1], path.join(fonte, 'linha-do-tempo.html'));
r = rodar(['--miniaturas', fonte, '--saida', mini]);
checa('miniaturas saem com exit 0', r.status === 0, r.stdout + r.stderr);
for (const n of ['caixas-iguais', 'linha-do-tempo']) {
  const f = path.join(mini, `${n}.png`);
  checa(`miniatura ${n}.png gravada e pequena (<= 800 px)`, fs.existsSync(f) && largura(f) <= 800, fs.existsSync(f) ? String(largura(f)) : 'não existe');
}

fs.rmSync(pasta, { recursive: true, force: true });
console.log(falhas ? `\n${falhas} falha(s)` : '\ntodas as checagens passaram');
process.exit(falhas ? 1 : 0);
