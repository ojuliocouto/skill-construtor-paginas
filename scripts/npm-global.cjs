'use strict';
/**
 * Pasta dos pacotes npm globais (o que `npm root -g` imprime), igual em Windows, macOS e Linux.
 *
 * Por que existe: os scripts da skill carregam o Playwright instalado com `npm i -g playwright`.
 * Chamar `execSync('npm root -g')` depende de shell e, no Windows, `npm` é `npm.cmd`, que o
 * Node 20.12+ não executa sem shell. Aqui o npm roda como `node npm-cli.js root -g`
 * (process.execPath + o npm que vem junto do Node), sem shell e sem depender do PATH.
 * Se não achar o npm-cli.js, calcula a pasta pelo prefixo conhecido de cada sistema.
 */
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

function acharNpmCli() {
  const bin = path.dirname(process.execPath);
  const candidatos = [
    path.join(bin, 'node_modules', 'npm', 'bin', 'npm-cli.js'), // Windows e Node baixado do nodejs.org
    path.join(bin, '..', 'lib', 'node_modules', 'npm', 'bin', 'npm-cli.js'), // macOS e Linux
  ];
  return candidatos.find((c) => fs.existsSync(c)) || null;
}

function prefixoConhecido() {
  if (process.env.npm_config_prefix) return process.env.npm_config_prefix;
  if (process.platform === 'win32') return process.env.APPDATA ? path.join(process.env.APPDATA, 'npm') : null;
  return path.join(path.dirname(process.execPath), '..');
}

function raizGlobal() {
  const cli = acharNpmCli();
  if (cli) {
    const r = spawnSync(process.execPath, [cli, 'root', '-g'], { encoding: 'utf8', windowsHide: true, timeout: 30000 });
    const saida = (r.stdout || '').trim();
    if (r.status === 0 && saida) return saida;
  }
  const prefixo = prefixoConhecido();
  if (!prefixo) throw new Error('não consegui descobrir a pasta global do npm');
  return process.platform === 'win32' ? path.join(prefixo, 'node_modules') : path.join(prefixo, 'lib', 'node_modules');
}

exports.raizGlobal = raizGlobal;
