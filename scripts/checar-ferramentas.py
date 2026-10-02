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
import urllib.error
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# QUEM BLOQUEIA. Critico e so o que a skill nao consegue fazer sem: prova de tela, gate
# anti-slop, banco de design, foto real sem chave e o gate de tells. 21st.dev e Higgsfield
# sao OPCIONAIS (relatorio do aluno, 02/10/2026): o verificador dava "tudo OK" porque rodava
# na maquina do dono, com a chave e a conta dele; um aluno de verdade teria o 21st vermelho
# (bloqueando) e o Higgsfield pedindo plano pago no primeiro comando. Rota padrao do aluno:
# componente a mao com Tailwind e movimento em CSS. Quem tiver as contas ganha teto maior.
CRITICIDADE = {
    "Playwright": True,
    "21st": False,
    "stitch": False,
    "ffmpeg/ffprobe": False,
    "Higgsfield CLI": False,
    "skill design-taste-frontend": True,
    "skill frontend-design": False,
    "skill high-end-visual-design": False,
    "skill animate": False,
    "Assets sem chave (Openverse)": True,
    "Banco de design": True,
    "gate-sem-kicker.py": True,
}

# Onde o teste do 21st procura a chave para fazer a chamada REAL. Estar em `claude mcp list`
# nao prova chave nenhuma: um MCP ja passou verde aqui e devolveu 401 na primeira chamada.
CHAVES_21ST = ("TWENTYFIRST_API_KEY", "API_KEY_21ST", "MAGIC_API_KEY")
URL_21ST = "https://21st.dev/api/mcp"


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


def _post_json(url, corpo, cabecalhos, timeout=20):
    """POST JSON e devolve (status, cabecalhos_minusculos, texto). Nunca levanta."""
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(), method="POST",
                                 headers={"content-type": "application/json",
                                          "accept": "application/json, text/event-stream",
                                          **cabecalhos})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, e.read().decode("utf-8", "replace")
    except Exception as e:  # rede, DNS, timeout
        return 0, {}, repr(e)


def _jsonrpc(texto):
    """Le resposta JSON-RPC em JSON puro ou em SSE (linhas data:)."""
    for bloco in [texto] + [l[5:].strip() for l in texto.splitlines() if l.startswith("data:")]:
        try:
            return json.loads(bloco)
        except (json.JSONDecodeError, TypeError):
            continue
    return {}


def testar_21st():
    """Chamada REAL ao MCP do 21st.dev: initialize, tools/list e uma busca de componente.

    Devolve (ok, detalhe). Opcional: falhar aqui nunca bloqueia, so tira o 21st da cobranca
    de uso e manda declarar a rota a mao na entrega."""
    chave = next((os.environ[k] for k in CHAVES_21ST if os.environ.get(k)), None)
    if not chave:
        est, _ = estado_mcp("21st")
        if est == "ausente":
            est, _ = estado_mcp("magic")
        if est == "ausente":
            return False, "nao configurado (opcional): a pagina sai com componente a mao em Tailwind"
        return False, (f"MCP {est} na lista, mas sem chave em {CHAVES_21ST[0]} nao da pra fazer a "
                       "chamada real; lista de MCP nao prova que a chave vale")
    cab = {"x-api-key": chave}
    st, h, txt = _post_json(URL_21ST, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {},
        "clientInfo": {"name": "checar-ferramentas", "version": "1"}}}, cab)
    if st != 200:
        return False, f"initialize respondeu HTTP {st}: chave recusada ou servico fora ({txt[:60]})"
    if h.get("mcp-session-id"):
        cab["mcp-session-id"] = h["mcp-session-id"]
    _post_json(URL_21ST, {"jsonrpc": "2.0", "method": "notifications/initialized"}, cab)
    st, _, txt = _post_json(URL_21ST, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}, cab)
    ferramentas = (_jsonrpc(txt).get("result") or {}).get("tools") or []
    if st != 200 or not ferramentas:
        return False, f"tools/list respondeu HTTP {st} sem ferramentas ({txt[:60]})"
    busca = next((f for f in ferramentas if "search" in f.get("name", "").lower()), None)
    if not busca:
        return True, f"chave aceita: {len(ferramentas)} ferramentas listadas (nenhuma de busca para exercitar)"
    schema = busca.get("inputSchema") or {}
    campos = schema.get("required") or [k for k, v in (schema.get("properties") or {}).items()
                                        if v.get("type") == "string"][:1]
    st, _, txt = _post_json(URL_21ST, {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
        "name": busca["name"], "arguments": {c: "button" for c in campos}}}, cab)
    resp = _jsonrpc(txt)
    if st != 200 or resp.get("error") or (resp.get("result") or {}).get("isError"):
        return False, f"busca real ({busca['name']}) falhou: HTTP {st} {txt[:60]}"
    return True, f"chamada real ok: {busca['name']}(\"button\") devolveu resultado"


def skill_existe(nome):
    for base in ("~/.claude/skills", "~/.agents/skills", "~/.claude-hubx/skills"):
        if (Path(os.path.expanduser(base)) / nome).exists():
            return True
    return False


# (rotulo, papel, critico?, funcao_de_teste) -> (ok, detalhe, como_resolver)
def checagens():
    ok, saida = roda(
        f'NODE_PATH="$HOME/.npm-global/lib/node_modules" node "{RAIZ}/scripts/screenshot-prova.js" --check')
    yield ("Playwright", "prova de entrega (obrigatoria nos 4 caminhos)", CRITICIDADE["Playwright"], ok,
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
    ok21, det21 = testar_21st()
    yield ("21st", "componentes do 21st.dev (Step 3, opcional)", CRITICIDADE["21st"], ok21, det21[:140],
           'opcional. Quem quiser: chave gratuita em https://21st.dev/mcp, depois '
           'claude mcp add --transport http 21st https://21st.dev/api/mcp --scope user --header "x-api-key: SUA_CHAVE" '
           f'e export {CHAVES_21ST[0]}=SUA_CHAVE (o teste usa a chave numa busca real)')
    yield _mcp("stitch", "wireframe (Step 2)", CRITICIDADE["stitch"],
               "opcional. Proxy local: confira quem esta na porta configurada antes de reiniciar (conflito de porta e a causa comum)")

    ok, saida = roda("ffprobe -version")
    yield ("ffmpeg/ffprobe", "gate de video (so em pagina com video)", False, ok,
           saida.splitlines()[0] if saida else "", "brew install ffmpeg")

    ok, saida = roda("higgsfield account status")
    yield ("Higgsfield CLI", "movimento e b-roll (Step 3.2b, opcional: conta paga)", CRITICIDADE["Higgsfield CLI"],
           ok and "plan" in saida.lower(),
           saida.splitlines()[0][:110] if saida else "",
           "opcional (plano pago). Sem conta: movimento em CSS, que e a rota padrao do aluno. "
           "Com conta: npm i -g @higgsfield/cli && higgsfield auth login && higgsfield workspace set <id>")

    # O comando de instalacao vai LITERAL: quem cai aqui esta com a ferramenta faltando e
    # precisa copiar e colar. Placeholder do tipo `<fonte>` nao instala nada, so parece que
    # instrui (era o que estava aqui ate 27/08/2026). As fontes sao as mesmas da SKILL.md.
    TASTE = "npx skills add Leonxlnx/taste-skill"
    for s, papel, critico, fix in [
        ("design-taste-frontend", "gate anti-slop e passe de gosto (Step 4.9)", True, TASTE),
        ("frontend-design", "direcao estetica antes do codigo (Step 2)", False,
         "npx -y skills add anthropics/skills --skill frontend-design --agent claude-code"),
        ("high-end-visual-design", "acabamento premium (Step 4)", False, TASTE),
        ("animate", "movimento e microinteracao (Step 4)", False,
         "npx -y skills add https://github.com/delphi-ai/animate-skill --agent claude-code"),
    ]:
        yield (f"skill {s}", papel, CRITICIDADE.get(f"skill {s}", critico), skill_existe(s), "", fix)

    ok, saida = roda(
        f'env -u PEXELS_API_KEY python3 "{RAIZ}/scripts/assets-search.py" "office" --type openverse -n 1')
    yield ("Assets sem chave (Openverse)", "foto real sem API key", CRITICIDADE["Assets sem chave (Openverse)"],
           ok and ("Imagem:" in saida or "http" in saida), "",
           "checar rede; a rota nao precisa de chave nenhuma")

    ok, saida = roda(f'python3 "{RAIZ}/scripts/search.py" "dark premium" --domain style -n 1')
    yield ("Banco de design", "paleta, estilo e tipografia (Step 2)", CRITICIDADE["Banco de design"],
           ok and "results" in saida.lower(), "", "conferir data/*.csv no repo")

    gate_sk = RAIZ / "scripts" / "gate-sem-kicker.py"
    existe_gate = gate_sk.exists()
    yield ("gate-sem-kicker.py", "pre-deploy: toda pagina sem kicker em caixa alta e sem numero decorativo",
           CRITICIDADE["gate-sem-kicker.py"],
           existe_gate, "", "o arquivo faz parte da skill: atualize o clone (git pull) em <dir-da-skill>")


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
            print("  siga e DECLARE a degradacao na entrega.")
            print("  Sem pagar nada: 21st.dev e Higgsfield sao opcionais. A pagina sai com")
            print("  componente feito a mao em Tailwind e movimento em CSS, e isso e a rota")
            print("  padrao do aluno, nao uma pagina pior por falta de conta.\n")
        else:
            print("  Tudo respondendo. Pode comecar o Step 0.\n")

    return 1 if any(not l["ok"] and l["critico"] for l in linhas) else 0


if __name__ == "__main__":
    sys.exit(main())
