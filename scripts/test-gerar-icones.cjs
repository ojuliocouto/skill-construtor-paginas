/** P17 (3.5.10): `gerar-icones.mjs` grava favicon.png e apple-touch-icon.png na RAIZ do projeto e imprime as linhas de <link>
 *  prontas, com os nomes reais dos arquivos que gravou (o aluno da 3.5.8 pôs `icones/favicon-32.png` no <head> e só o
 *  screenshot-prova.js mostrou o erro). O teste confere que cada href impresso aponta para um arquivo que existe no projeto.
 */
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

let falhas = 0;
const checa = (nome, ok, d = '') => { console.log(`${ok ? 'ok   ' : 'FALHA'} ${nome}${d ? ' -> ' + d : ''}`); if (!ok) falhas++; };

const proj = fs.mkdtempSync(path.join(os.tmpdir(), 'icones-prova-'));
fs.mkdirSync(path.join(proj, 'icones'));
fs.writeFileSync(path.join(proj, 'icones', 'icone.svg'),
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" data-motivo="grão de café que se parte ao meio"><rect width="32" height="32" fill="#2a1a10"/><ellipse cx="16" cy="16" rx="8" ry="11" fill="#f3e9d8"/></svg>');
const r = spawnSync(process.execPath, [path.join(__dirname, 'gerar-icones.mjs'), '--projeto', proj], { encoding: 'utf8' });
checa('sai 0 e grava os dois PNG na raiz do projeto', r.status === 0 && fs.existsSync(path.join(proj, 'favicon.png')) && fs.existsSync(path.join(proj, 'apple-touch-icon.png')), (r.stderr || '').split('\n')[0]);

const links = r.stdout.split('\n').filter((l) => /<link\b/.test(l));
checa('imprime duas linhas de <link> prontas', links.length === 2, JSON.stringify(links));
const fav = links.find((l) => /rel="icon"/.test(l)) || '';
const apple = links.find((l) => /rel="apple-touch-icon"/.test(l)) || '';
checa('o <link rel="icon"> é PNG de 32x32 e aponta para /favicon.png', /type="image\/png"/.test(fav) && /sizes="32x32"/.test(fav) && /href="\/favicon\.png"/.test(fav), fav);
checa('o <link rel="apple-touch-icon"> é de 180x180 e aponta para /apple-touch-icon.png', /sizes="180x180"/.test(apple) && /href="\/apple-touch-icon\.png"/.test(apple), apple);
const hrefs = links.map((l) => (l.match(/href="([^"]+)"/) || [])[1]).filter(Boolean);
checa('cada href impresso é um arquivo que existe no projeto (nada de icones/favicon-32.png)', hrefs.length === 2 && hrefs.every((h) => fs.existsSync(path.join(proj, h.replace(/^\//, '')))), hrefs.join(', '));
checa('a saída diz que as linhas vão no <head> e que o caminho começa pela raiz do site', /<head>/.test(r.stdout) && /raiz/.test(r.stdout), r.stdout.split('\n').find((l) => /head/.test(l)) || '');

const sem = spawnSync(process.execPath, [path.join(__dirname, 'gerar-icones.mjs'), '--projeto', path.join(proj, 'nao-existe')], { encoding: 'utf8' });
checa('sem icone.svg continua recusando, sem imprimir <link>', sem.status === 1 && !/<link/.test(sem.stdout), String(sem.status));

console.log(falhas ? `\n${falhas} falha(s). ${proj}` : '\nícones gerados e linhas de link conferidas.');
process.exit(falhas ? 1 : 0);
