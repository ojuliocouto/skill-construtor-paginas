# Windows, macOS e Linux

Quem executa os comandos é você, o agente. Confira isto antes do primeiro comando. Desde a 3.5.5
a skill roda os mesmos testes nos três sistemas em máquinas reais do GitHub (workflow
`.github/workflows/portabilidade.yml`); o que isso provou e o que ainda não está provado fica no
fim deste arquivo.

1. **Descubra o sistema:** `node -p "process.platform"` (`win32` é Windows, `darwin` é macOS,
   `linux` é Linux).
2. **Python pelo lançador.** Onde este roteiro e as referências escrevem
   `node <dir-da-skill>/scripts/py.mjs <script>.py <argumentos>`, é esse o comando, em qualquer
   sistema. O lançador acha o Python da máquina (no Windows ele quase nunca se chama como no Mac,
   e a loja da Microsoft deixa um falso que só abre a loja) e liga o modo UTF-8, sem o qual o
   Windows quebra em palavra com acento. `node <dir-da-skill>/scripts/py.mjs --descobrir` diz qual
   Python foi achado. Para instalar pacote no MESMO Python que os scripts usam:
   `node <dir-da-skill>/scripts/py.mjs -m pip install <pacote>`.
3. **Windows: rode pelo Git Bash (ou pelo WSL)** de preferência: os comandos do roteiro são de
   bash (`~/`, aspas simples, `&&`). No PowerShell 5.1 o `&&` não existe: rode um comando por
   linha. Aspas duplas no caminho sempre.
4. **Primeiro comando:** `node <dir-da-skill>/scripts/py.mjs checar-ferramentas.py`. Cada item que
   faltar sai com o comando de instalar do SEU sistema.
5. Depois de instalar qualquer coisa, abra um terminal NOVO (o PATH só vale nele). Pasta com espaço
   ou acento (`C:\Users\João Silva`, `C:\curso automação\skill`) vai entre aspas em todo comando.

## O que muda por sistema

| | Windows | macOS | Linux |
|---|---|---|---|
| Terminal | Git Bash (ou WSL); PowerShell serve para comandos soltos | Terminal ou iTerm | qualquer |
| Como o Python se chama | `python` ou `py -3` | o nome com o 3 no fim | o nome com o 3 no fim |
| Abrir página ou pasta | `start "" <arquivo>` (cmd) ou `Start-Process` (PowerShell) | `open <arquivo>` | `xdg-open <arquivo>` |
| Pasta temporária | `%TEMP%` | `$TMPDIR` | `$TMPDIR` ou a pasta temporária do sistema |
| Fim de linha dos arquivos | o Git converte para LF (`.gitattributes`) | LF | LF |
| Pacotes globais do npm | `%APPDATA%\npm\node_modules` | `<prefixo>/lib/node_modules` | `<prefixo>/lib/node_modules` |

Os scripts da skill já tratam isso sozinhos: UTF-8 em toda leitura e escrita de texto, sem shell
(`subprocess` com lista, `spawn` com lista), pasta temporária pela biblioteca, o Playwright global
achado por `scripts/npm-global.cjs`. Quem escrever script novo respeita a trava
`scripts/test-portabilidade.py`, que reprova comando só de Mac, `/tmp` fixo, texto sem `encoding=`,
`python3` solto e shell no código.

## Instalar o que falta

| | Windows | macOS | Linux (Debian/Ubuntu e Fedora) |
|---|---|---|---|
| Node 18+ (22 recomendado) | `winget install -e --id OpenJS.NodeJS.LTS` | `brew install node` (macOS) | instalador de nodejs.org ou `nvm` |
| Python 3.8+ | `winget install -e --id Python.Python.3.12` | `brew install python` (macOS) | `sudo apt install python3 python3-pip` ou `sudo dnf install python3 python3-pip` |
| Git | `winget install -e --id Git.Git` (traz o Git Bash) | Ferramentas de Linha de Comando da Apple | `sudo apt install git` ou `sudo dnf install git` |
| Pillow e numpy (opcional, gates de imagem) | `node <dir-da-skill>/scripts/py.mjs -m pip install pillow numpy` | igual | igual; no Ubuntu 24.04 e Debian 12 veja o erro "externally-managed-environment" abaixo |
| Playwright | `npm install -g playwright` | igual | igual |
| Chromium do Playwright | `npx playwright install chromium` | igual | `npx playwright install --with-deps chromium` |
| ffmpeg (opcional, só para página com vídeo) | `winget install -e --id Gyan.FFmpeg`; se não tiver o `winget`: `choco install ffmpeg -y` (é o que o CI usa) | `brew install ffmpeg` (macOS) | `sudo apt install ffmpeg` ou `sudo dnf install ffmpeg` |
| Skill `frontend-design` | `npx -y skills add anthropics/skills --skill frontend-design --agent claude-code -g -y --copy` | igual | igual |

O `checar-ferramentas.py` confere tudo isso e imprime a linha certa para a máquina de quem rodou.

## Erros conhecidos

A coluna "saída" é o texto que a pessoa vê. As marcadas com (medida) foram reproduzidas ao
construir a 3.5.5; as marcadas com (documentada) vêm da documentação das ferramentas e ainda não
foram reproduzidas em máquina real nesta skill.

| Saída | Causa e conserto |
|---|---|
| `Não achei o Python 3 (versão 3.8 ou mais nova) nesta máquina.` e código de saída 127 (medida) | Python ausente ou fora do PATH. Instale pela tabela acima e abra um terminal novo. |
| `Python was not found; run without arguments to install from the Microsoft Store` (documentada) | O falso `python.exe` da loja do Windows. O `py.mjs` ignora esse falso; instale o Python de verdade. |
| `UnicodeEncodeError: 'charmap' codec can't encode character` ou `UnicodeDecodeError: 'charmap'` (medida, forçando `PYTHONUTF8=0`) | Script rodado direto no Python do Windows (cp1252). Rode sempre por `node <dir-da-skill>/scripts/py.mjs`, que liga o UTF-8. |
| `playwright não encontrado: npm i -g playwright && npx playwright install chromium` (medida) | Falta o pacote. `npm install -g playwright`, depois `npx playwright install chromium`. |
| `browserType.launch: Executable doesn't exist at ...` (documentada) | O pacote existe, o Chromium não foi baixado: `npx playwright install chromium`. |
| `error while loading shared libraries: libnss3.so` ou `Host system is missing dependencies to run browsers` (documentada) | Linux sem as bibliotecas do Chromium: `npx playwright install --with-deps chromium`. |
| `error: externally-managed-environment` ao instalar Pillow (documentada) | Ubuntu 24.04 e Debian 12 bloqueiam `pip` no Python do sistema. Use `sudo apt install python3-pil python3-numpy`, ou crie um ambiente (`python3 -m venv ~/.venv-skill`) e rode o `py.mjs` com ele no PATH. |
| `npx : O arquivo ...npx.ps1 não pode ser carregado porque a execução de scripts foi desabilitada neste sistema` (documentada) | PowerShell com política restrita. Use o Git Bash, ou `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. |
| `spawn EINVAL` ao chamar `npm.cmd` ou `npx.cmd` pelo Node 20.12+ (documentada) | O Node recusa rodar `.cmd` sem shell. Os scripts da skill não fazem isso (`npm-global.cjs` roda o `npm-cli.js` com o próprio `node`). Se um script novo precisar, use o mesmo caminho. |
| `ffmpeg não encontrado: instale com ...` (medida: gate de vídeo e teste sem ffmpeg no PATH) | O ffmpeg e o ffprobe não estão no PATH. Instale pela tabela acima e abra um terminal novo. O teste `test-gates-visuais.cjs` fica PULADO fora do CI e FALHA no CI. |
| `/usr/bin/env: 'bash\r': No such file or directory` (documentada) | Fim de linha CRLF num script. O `.gitattributes` da skill força LF; se clonou antes dele, rode `git add --renormalize .`. |
| `ENOENT` ou `EPERM` com caminho que tem acento ou espaço (medida: o CI abre `C:\curso automação\skill`) | Falta de aspas no comando. Todo caminho vai entre aspas duplas. |

## O que está provado e o que não está

- **macOS:** suíte inteira passa na máquina de desenvolvimento, e os testes portáteis passam em
  cópia numa pasta com acento e espaço, com `PYTHONUTF8=0` e `LC_ALL=C`, e num PATH em que só existe
  `python`.
- **Windows e Linux reais:** o workflow `portabilidade.yml` roda a suíte inteira em `windows-latest`,
  `ubuntu-latest` e `macos-latest`, e no Windows também os testes portáteis numa pasta
  `C:\curso automação\skill`. Enquanto o resultado verde desse workflow não estiver registrado no
  `CHANGELOG.md`, trate Windows e Linux como "caminho descrito, não provado em máquina real". Se um
  script falhar por caminho ou codificação, mostre o erro e o comando e corrija a chamada; gate que não
  rodou não conta como aprovado.
