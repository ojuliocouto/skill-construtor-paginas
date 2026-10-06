# Windows, macOS e Linux

Quem executa os comandos é você, o agente. Confira isto antes do primeiro comando.

1. **Descubra o sistema:** `node -p "process.platform"` (`win32` é Windows, `darwin` é macOS,
   `linux` é Linux).
2. **Python pelo lançador.** Onde este roteiro e as referências escrevem
   `python3 <dir-da-skill>/scripts/<script>.py`, rode
   `node <dir-da-skill>/scripts/py.mjs <script>.py <argumentos>`. O lançador acha o Python da
   máquina (no Windows ele quase nunca se chama `python3`) e liga o modo UTF-8, sem o qual o
   Windows quebra em palavra com acento. `node <dir-da-skill>/scripts/py.mjs --descobrir` diz
   qual Python foi achado. No macOS e no Linux, `python3` direto também funciona.
3. **Windows: rode pelo Git Bash (ou pelo WSL)**, não pelo PowerShell puro. Os comandos são de
   bash (`~/`, `cp -R`, aspas).
4. **Instalar o que falta:**

| | Windows | macOS | Linux (Debian/Ubuntu e Fedora) |
|---|---|---|---|
| Node 18+ | `winget install -e --id OpenJS.NodeJS.LTS` | `brew install node` | instalador ou `nvm` (nodejs.org) |
| Python 3.8+ | `winget install -e --id Python.Python.3.12` | `brew install python` | `sudo apt install python3` ou `sudo dnf install python3` |
| Git | `winget install -e --id Git.Git` (traz o Git Bash) | Ferramentas de Linha de Comando da Apple | `sudo apt install git` ou `sudo dnf install git` |

5. Depois de instalar qualquer coisa, abra um terminal NOVO. Pasta com espaço ou acento
   (`C:\Users\João Silva`) vai entre aspas em todo comando. No Linux, se o Chromium abrir e
   fechar na hora: `npx playwright install --with-deps chromium`.

**O que está provado e o que não está:** a skill foi construída e testada no macOS. No Windows e
no Linux o caminho é o descrito acima, ainda sem execução em máquina real. Se um script falhar
por caminho ou por codificação, mostre o erro e o comando ao usuário e corrija a chamada; gate
que não rodou não conta como aprovado.
