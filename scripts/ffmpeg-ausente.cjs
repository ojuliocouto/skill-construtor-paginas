'use strict';
/**
 * O que fazer quando o ffmpeg ou o ffprobe não existem na máquina: dizer o comando de instalar
 * do sistema da pessoa, em vez de estourar `spawnSync ffmpeg ENOENT`.
 *
 * Usado por gate-video.mjs (para o aluno) e por gates-visuais-lib.cjs (teste: PULADO fora do
 * CI, FALHA no CI, onde o ffmpeg é instalado de propósito).
 */
const { spawnSync } = require('node:child_process');

function instrucaoInstalar() {
  if (process.platform === 'win32') return 'winget install -e --id Gyan.FFmpeg  (ou: choco install ffmpeg -y), depois abra um terminal novo';
  if (process.platform === 'darwin') return 'brew install ffmpeg';
  return 'Debian/Ubuntu: sudo apt install ffmpeg  |  Fedora: sudo dnf install ffmpeg (precisa do RPM Fusion)';
}

function temFerramenta(nome) {
  const r = spawnSync(nome, ['-version'], { stdio: 'ignore', windowsHide: true });
  return !r.error && r.status === 0;
}

function mensagemAusente(nome) {
  return `${nome} não encontrado: instale com ${instrucaoInstalar()}`;
}

/** Para testes: sem ffmpeg e ffprobe, PULADO fora do CI e FALHA no CI. Não volta se faltar. */
function pularOuFalharSemFfmpeg() {
  for (const nome of ['ffmpeg', 'ffprobe']) {
    if (temFerramenta(nome)) continue;
    if (process.env.CI) { console.log(`FALHA: ${mensagemAusente(nome)} (no CI ele tem que existir)`); process.exit(1); }
    console.log(`PULADO: ${mensagemAusente(nome)}. Este teste NÃO rodou.`);
    process.exit(0);
  }
}

/** Para scripts: erro de execução por falta do programa vira mensagem clara e saída 127. */
function sairSeAusente(e, nome) {
  if (e && e.code === 'ENOENT') { console.error(`FALHA: ${mensagemAusente(nome)}`); process.exit(127); }
}

module.exports = { instrucaoInstalar, temFerramenta, mensagemAusente, pularOuFalharSemFfmpeg, sairSeAusente };
