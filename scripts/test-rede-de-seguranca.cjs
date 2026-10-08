'use strict';
/** N13 (3.5.8): separar a rede de segurança do script principal quando os dois dividem o mesmo <script>. Sem navegador. */
const assert = require('node:assert');
const { dividirScript } = require('./rede-de-seguranca.cjs');

const REDE = "(function (d) { d.classList.replace('no-js', 'js'); setTimeout(function () { if (!d.hasAttribute('data-js-ok')) d.classList.replace('js', 'no-js'); }, 5000); })(document.documentElement)";
const VH = "(function () { var largura = 0; function medir() { if (window.innerWidth === largura) return; largura = window.innerWidth; document.documentElement.style.setProperty('--vh', window.innerHeight / 100 + 'px'); } medir(); window.addEventListener('resize', medir); })()";
let n = 0;
const caso = (nome, f) => { f(); n++; console.log('ok  ' + nome); };

caso('rede e vh no mesmo script: a rede fica, o vh vai para o principal', () => {
  const r = dividirScript(REDE + ';\n' + VH);
  assert.match(r.rede, /data-js-ok/);
  assert.doesNotMatch(r.rede, /addEventListener/);
  assert.match(r.principal, /addEventListener/);
  assert.doesNotMatch(r.principal, /data-js-ok/);
});
caso('sem ponto e vírgula, só quebra de linha depois do bloco', () => {
  const r = dividirScript('function medir() {\n  x();\n}\n' + REDE + '\nwindow.addEventListener("resize", medir)');
  assert.match(r.rede, /hasAttribute/);
  assert.match(r.principal, /function medir/);
  assert.match(r.principal, /resize/);
});
caso('ponto e vírgula dentro de texto e de comentário não corta a instrução', () => {
  const r = dividirScript("var s = 'a;b'; // um; dois\n/* tres; quatro */ " + REDE + ';');
  assert.match(r.rede, /data-js-ok/);
  assert.match(r.principal, /a;b/);
});
caso('script só da rede: principal vazio', () => {
  const r = dividirScript(REDE);
  assert.ok(r.rede && !r.principal.trim());
});
caso('script sem rede: tudo é principal', () => {
  const r = dividirScript(VH);
  assert.strictEqual(r.rede, '');
  assert.match(r.principal, /addEventListener/);
});
caso('o ruim continua ruim: só a classe js sem temporizador é rede, e o gate vê que falta o temporizador no fixture do navegador', () => {
  const r = dividirScript('document.documentElement.classList.add("js");' + VH);
  assert.match(r.rede, /classList\.add\("js"\)/);
  assert.doesNotMatch(r.rede, /setTimeout/);
});
caso('confirmação do script principal (setAttribute data-js-ok) NÃO é rede', () => {
  const r = dividirScript(REDE + ';document.documentElement.setAttribute("data-js-ok","");');
  assert.doesNotMatch(r.rede, /setAttribute/);
  assert.match(r.principal, /setAttribute/);
});
caso('temporizador que só retira a classe (sem repor js) também é rede, reconhecido pelo data-js-ok', () => {
  const r = dividirScript("document.documentElement.classList.add('js');\nsetTimeout(function () { var d = document.documentElement; if (!d.hasAttribute('data-js-ok')) d.classList.remove('js'); }, 5000);\n" + VH);
  assert.match(r.rede, /remove\('js'\)/);
  assert.doesNotMatch(r.principal, /remove\('js'\)/);
});
console.log(`${n}/${n} passaram`);
