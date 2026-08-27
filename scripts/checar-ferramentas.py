#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Checagem de ferramentas do construtor-paginas: testa se RESPONDE, nao se esta configurado.

Existe porque em 26/08/2026 descobrimos que o MCP do 21st.dev estava configurado e MORTO
("Not authenticated: your API key is missing or was reset") havia tempo indeterminado. A skill
mandava "buildar com componentes do 21st.dev OU a mao", o MCP nunca respondia, e ela caia no
"a mao" TODA VEZ. Ninguem percebeu porque fallback silencioso nao reclama. O Stitch estava no
mesmo estado (proxy de pe, tools fetch com timeout), entao as DUAS camadas visuais da skill
estavam desligadas.

A licao: "esta na lista de tools" NAO e verificacao. Verificacao e mandar a ferramenta fazer
alguma coisa e conferir se voltou.

Uso:
    python3 scripts/checar-ferramentas.py            # tabela + saida != 0 se faltar critico
    python3 scripts/checar-ferramentas.py --json     # para consumo por agente
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def roda(cmd, timeout=25):
    """Executa e devolve (ok, saida). Nunca levanta: timeout e binario ausente viram ok=False."""
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return p.returncode == 0, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, f"timeout depois de {timeout}s"
    except Exception as e:  # binario ausente, permissao, etc
        return False, repr(e)


def estado_mcp(nome):
    """Le `claude mcp list` e classifica UM servidor.

    Distingue os quatro estados que importam, porque so o primeiro serve:
      conectado          -> responde
      sem_auth           -> configurado, mas a chave morreu ou nunca existiu
      falhou             -> nao conecta
      tools_falharam     -> conecta mas nao entrega as tools (foi o caso do Stitch)
    """
    ok, saida = roda("claude mcp list", timeout=45)
    if not ok and not saida:
        return "indeterminado", "nao consegui rodar `claude mcp list`"
    for linha in saida.splitlines():
        if not linha.strip().startswith(nome + ":") and f" {nome}:" not in linha:
            if not linha.strip().startswith(nome):
                continue
        baixo = linha.lower()
        if "needs authentication" in baixo:
            return "sem_auth", linha.strip()
        if "failed to connect" in baixo:
            return "falhou", linha.strip()
        if "tools fetch failed" in baixo or "timed out" in baixo:
            return "tools_falharam", linha.strip()
        if "connected" in baixo:
            return "conectado", linha.strip()
    return "ausente", f"'{nome}' nao aparece em `claude mcp list`"


def skill_existe(nome):
    for base in ("~/.claude/skills", "~/.agents/skills", "~/.claude-hubx/skills"):
        if (Path(os.path.expanduser(base)) / nome).exists():
            return True
    return False


# (rotulo, papel, critico?, funcao_de_teste) -> (ok, detalhe, como_resolver)
def checagens():
    ok, saida = roda(
        f'NODE_PATH="$HOME/.npm-global/lib/node_modules" node "{RAIZ}/scripts/screenshot-prova.js" --check')
    yield ("Playwright", "prova de entrega (obrigatoria nos 4 caminhos)", True, ok,
           saida.splitlines()[0][:110] if saida else "",
           "npm i -g playwright && npx playwright install chromium")

    def _mcp(nome, papel, critico, url_fix):
        # nome pode ser uma string ou uma tupla de nomes aceitos (o mesmo servidor ja
        # apareceu com nomes diferentes conforme o transporte). Basta UM responder.
        nomes = (nome,) if isinstance(nome, str) else tuple(nome)
        piores = []
        for n in nomes:
            est, det = estado_mcp(n)
            if est == "conectado":
                return (n, papel, critico, True, f"{est}: {det[:110]}", url_fix)
            piores.append((n, est, det))
        n, est, det = piores[0]
        rotulo = nomes[0] if len(nomes) == 1 else " ou ".join(nomes)
        return (rotulo, papel, critico, False, f"{est}: {det[:110]}", url_fix)

    # O servidor do 21st.dev ja teve DOIS nomes: "magic" (transporte stdio, via npx) e
    # "21st" (transporte HTTP). Em 27/08/2026 o "magic" estava com a chave resetada e foi
    # ESCOPO IMPORTA: adicionar sem --scope user prende o servidor ao projeto do
    # diretorio atual, e ele SOME quando o cwd muda. Aconteceu em 27/08/2026: o
    # `claude mcp list` dizia Connected na home e nao listava nada dentro da pasta da
    # skill (que tem git proprio, entao e outro projeto). Sempre `--scope user`.
    # REMOVIDO; entrou o "21st" por HTTP. Aceitar os dois nomes evita o proximo falso
    # negativo: o servidor conectado com nome novo e o verificador reprovando por
    # procurar o antigo, que e exatamente o que aconteceu hoje.
    yield _mcp(("21st", "magic"), "componentes do 21st.dev (Step 3)", True,
               'chave nova em https://21st.dev/mcp, depois: claude mcp add --transport http 21st https://21st.dev/api/mcp --header "x-api-key: SUA_CHAVE"')
    yield _mcp("stitch", "wireframe (Step 2)", False,
               "proxy local: conferir se ~/.claude/scripts/stitch-proxy.py responde na porta configurada (conflito de porta e a causa comum)")

    ok, saida = roda("ffprobe -version")
    yield ("ffmpeg/ffprobe", "gate de video (so em pagina com video)", False, ok,
           saida.splitlines()[0] if saida else "", "brew install ffmpeg")

    ok, saida = roda("higgsfield account status")
    yield ("Higgsfield CLI", "movimento e b-roll (Step 3.2b)", False, ok and "plan" in saida.lower(),
           saida.splitlines()[0][:110] if saida else "",
           "npm i -g @higgsfield/cli && higgsfield auth login && higgsfield workspace set <id>")

    for s, papel, critico in [
        ("design-taste-frontend", "gate anti-slop e passe de gosto (Step 4.9)", True),
        ("frontend-design", "direcao estetica antes do codigo (Step 2)", False),
        ("high-end-visual-design", "acabamento premium (Step 4)", False),
        ("animate", "movimento e microinteracao (Step 4)", False),
    ]:
        yield (f"skill {s}", papel, critico, skill_existe(s), "", f"npx skills add <fonte>/{s}")

    ok, saida = roda(
        f'env -u PEXELS_API_KEY python3 "{RAIZ}/scripts/assets-search.py" "office" --type openverse -n 1')
    yield ("Assets sem chave (Openverse)", "foto real sem API key", True,
           ok and ("Imagem:" in saida or "http" in saida), "",
           "checar rede; a rota nao precisa de chave nenhuma")

    ok, saida = roda(f'python3 "{RAIZ}/scripts/search.py" "dark premium" --domain style -n 1')
    yield ("Banco de design", "paleta, estilo e tipografia (Step 2)", True,
           ok and "results" in saida.lower(), "", "conferir data/*.csv no repo")


def main():
    linhas = []
    for item in checagens():
        rotulo, papel, critico, ok, detalhe, fix = item
        linhas.append(dict(ferramenta=rotulo, papel=papel, critico=critico,
                           ok=bool(ok), detalhe=detalhe, como_resolver=fix))

    if "--json" in sys.argv:
        print(json.dumps(linhas, ensure_ascii=False, indent=2))
    else:
        larg = max(len(l["ferramenta"]) for l in linhas) + 2
        print("\nFERRAMENTAS DO CONSTRUTOR-PAGINAS\n" + "=" * 72)
        for l in linhas:
            marca = "OK  " if l["ok"] else ("FALTA" if l["critico"] else "aviso")
            print(f"  [{marca:5}] {l['ferramenta']:<{larg}} {l['papel']}")
            if not l["ok"]:
                if l["detalhe"]:
                    print(f"            {l['detalhe']}")
                print(f"            RESOLVER: {l['como_resolver']}")
        quebrados = [l for l in linhas if not l["ok"]]
        criticos = [l for l in quebrados if l["critico"]]
        print("=" * 72)
        if criticos:
            print(f"  {len(criticos)} ferramenta(s) CRITICA(s) sem responder.")
            print("  Resolva antes do Step 1: sem elas a pagina nasce pela rota degradada e")
            print("  ninguem percebe, porque o fallback nao reclama.\n")
        elif quebrados:
            print(f"  Tudo critico responde. {len(quebrados)} opcional(is) degradado(s):")
            print("  siga e DECLARE a degradacao na entrega.\n")
        else:
            print("  Tudo respondendo. Pode comecar o Step 0.\n")

    return 1 if any(not l["ok"] and l["critico"] for l in linhas) else 0


if __name__ == "__main__":
    sys.exit(main())
