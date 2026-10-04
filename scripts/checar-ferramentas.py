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

Versao 3 (02/10/2026): a skill depende de TRES coisas, a skill `frontend-design`, os
auditores adversariais e a pesquisa de referencias reais. Critico passa a ser so o que essas
tres precisam pra rodar: python3, node, Playwright com o Chromium baixado (prints das
referencias e prova de entrega) e a skill `frontend-design` instalada. Todo o resto
(21st.dev, Stitch, Higgsfield, skills de acabamento, banco de design, Openverse) e OPCIONAL:
nunca bloqueia e, por padrao, nem e checado, porque checar MCP por `claude mcp list` leva
ate um minuto e o aluno nao precisa de nada disso.

Uso:
    python3 scripts/checar-ferramentas.py              # criticos + opcionais locais rapidos
    python3 scripts/checar-ferramentas.py --opcionais  # tambem MCPs, Higgsfield e rede
    python3 scripts/checar-ferramentas.py --json       # para consumo por agente
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

# QUEM BLOQUEIA (v3). Critico e so o que as tres dependencias da skill precisam: python3 e
# node rodam os gates, o Playwright com Chromium tira os prints das referencias e a prova de
# entrega, e a `frontend-design` faz o plano visual. Todo o resto e opcional e nunca bloqueia.
CRITICIDADE = {
    "python3": True,
    "node": True,
    "Playwright": True,
    "skill frontend-design": True,
    "21st": False,
    "stitch": False,
    "ffmpeg/ffprobe": False,
    "Higgsfield CLI": False,
    "skill design-taste-frontend": False,
    "skill high-end-visual-design": False,
    "skill animate": False,
    "Assets sem chave (Openverse)": False,
    "Banco de design": False,
    "Pillow e numpy": False,
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


# (rotulo, papel, critico, ok, detalhe, como_resolver). Item opcional lento e nao checado
# sai com ok=None: nao e verde nem vermelho, e o uso-ferramentas.py nao o cobra.
def checagens(opcionais=False):
    yield ("python3", "roda os gates e o registro dos auditores", CRITICIDADE["python3"],
           sys.version_info >= (3, 8), sys.version.split()[0], "instale o Python 3.8 ou mais novo")

    ok, saida = roda("node --version")
    yield ("node", "roda o Playwright, os prints e os gates visuais", CRITICIDADE["node"], ok,
           saida.splitlines()[0] if saida else "", "instale o Node 18 ou mais novo (https://nodejs.org)")

    ok, saida = roda(
        f'NODE_PATH="$HOME/.npm-global/lib/node_modules" node "{RAIZ}/scripts/screenshot-prova.js" --check')
    yield ("Playwright", "prints das referencias e prova de entrega (Chromium baixado)",
           CRITICIDADE["Playwright"], ok, saida.splitlines()[0][:110] if saida else "",
           "npm i -g playwright && npx playwright install chromium")

    yield ("skill frontend-design", "plano visual antes do codigo (passo c do CRIAR)",
           CRITICIDADE["skill frontend-design"], skill_existe("frontend-design"), "",
           "npx -y skills add anthropics/skills --skill frontend-design --agent claude-code")

    # ---------------- daqui pra baixo, tudo opcional: nunca bloqueia ----------------
    try:
        import numpy, PIL  # noqa: F401
        tem_pn, det_pn = True, f"Pillow {PIL.__version__}, numpy {numpy.__version__}"
    except ImportError:
        tem_pn, det_pn = False, "ausentes"
    yield ("Pillow e numpy", "repeticao e nitidez de foto (gate-imagens) e a prancha de animacao (opcional)",
           CRITICIDADE["Pillow e numpy"], tem_pn, det_pn, "pip install pillow numpy")

    ok, saida = roda("ffprobe -version")
    yield ("ffmpeg/ffprobe", "gate de video (so em pagina com video)", CRITICIDADE["ffmpeg/ffprobe"], ok,
           saida.splitlines()[0] if saida else "", "brew install ffmpeg")

    TASTE = "npx skills add Leonxlnx/taste-skill"
    for s, papel, fix in [
        ("design-taste-frontend", "segunda opiniao anti-slop (opcional)", TASTE),
        ("high-end-visual-design", "acabamento (opcional)", TASTE),
        ("animate", "movimento em React (opcional)",
         "npx -y skills add https://github.com/delphi-ai/animate-skill --agent claude-code"),
    ]:
        yield (f"skill {s}", papel, CRITICIDADE[f"skill {s}"], skill_existe(s), "", fix)

    ok, saida = roda(f'python3 "{RAIZ}/scripts/search.py" "dark premium" --domain style -n 1')
    yield ("Banco de design", "consulta opcional de estilo, paleta e fonte", CRITICIDADE["Banco de design"],
           ok and "results" in saida.lower(), "", "conferir data/*.csv no repo")

    if not opcionais:
        for rotulo, papel in [("21st", "componentes do 21st.dev"), ("stitch", "wireframe no Stitch"),
                              ("Higgsfield CLI", "video gerado"),
                              ("Assets sem chave (Openverse)", "busca de foto com licenca aberta")]:
            yield (rotulo, papel, CRITICIDADE[rotulo], None, "nao checado (rode com --opcionais)", "")
        return

    ok21, det21 = testar_21st()
    yield ("21st", "componentes do 21st.dev (opcional)", CRITICIDADE["21st"], ok21, det21[:140],
           'opcional. Chave gratuita em https://21st.dev/mcp, depois '
           'claude mcp add --transport http 21st https://21st.dev/api/mcp --scope user --header "x-api-key: SUA_CHAVE" '
           f'e export {CHAVES_21ST[0]}=SUA_CHAVE (o teste usa a chave numa busca real)')

    est, det = estado_mcp("stitch")
    yield ("stitch", "wireframe no Stitch (opcional)", CRITICIDADE["stitch"], est == "conectado",
           f"{est}: {det[:110]}", "opcional. Confira quem esta na porta do proxy antes de reiniciar")

    ok, saida = roda("higgsfield account status")
    yield ("Higgsfield CLI", "video gerado (opcional, conta paga)", CRITICIDADE["Higgsfield CLI"],
           ok and "plan" in saida.lower(), saida.splitlines()[0][:110] if saida else "",
           "opcional. npm i -g @higgsfield/cli && higgsfield auth login && higgsfield workspace set <id>")

    ok, saida = roda(
        f'env -u PEXELS_API_KEY python3 "{RAIZ}/scripts/assets-search.py" "office" --type openverse -n 1')
    yield ("Assets sem chave (Openverse)", "busca de foto com licenca aberta (opcional)",
           CRITICIDADE["Assets sem chave (Openverse)"], ok and ("Imagem:" in saida or "http" in saida), "",
           "checar rede; a rota nao precisa de chave")


def main():
    opcionais = "--opcionais" in sys.argv
    linhas = []
    for rotulo, papel, critico, ok, detalhe, fix in checagens(opcionais):
        linhas.append(dict(ferramenta=rotulo, papel=papel, critico=critico,
                           ok=None if ok is None else bool(ok), checado=ok is not None,
                           detalhe=detalhe, como_resolver=fix))

    if "--json" in sys.argv:
        print(json.dumps(linhas, ensure_ascii=False, indent=2))
    else:
        larg = max(len(l["ferramenta"]) for l in linhas) + 2
        print("\nFERRAMENTAS DO CONSTRUTOR-PAGINAS (v3)\n" + "=" * 72)
        for l in linhas:
            if not l["checado"]:
                marca = "  -  "
            else:
                marca = "OK  " if l["ok"] else ("FALTA" if l["critico"] else "aviso")
            print(f"  [{marca:5}] {l['ferramenta']:<{larg}} {l['papel']}")
            if l["checado"] and not l["ok"]:
                if l["detalhe"]:
                    print(f"            {l['detalhe']}")
                print(f"            RESOLVER: {l['como_resolver']}")
        criticos = [l for l in linhas if l["critico"] and not l["ok"]]
        avisos = [l for l in linhas if not l["critico"] and l["checado"] and not l["ok"]]
        print("=" * 72)
        if criticos:
            print(f"  {len(criticos)} ferramenta(s) CRITICA(s) sem responder. Resolva antes de comecar:")
            print("  sem elas nao ha print de referencia, nem plano visual, nem prova de entrega.\n")
        else:
            print("  Tudo critico responde. Pode comecar o briefing.")
            if avisos:
                print(f"  {len(avisos)} opcional(is) ausente(s): nao bloqueia nada, a skill nao depende deles.")
            if not opcionais:
                print("  Opcionais de rede e MCP nao foram checados (rode com --opcionais se quiser usar).")
            print()

    return 1 if any(l["critico"] and not l["ok"] for l in linhas) else 0


if __name__ == "__main__":
    sys.exit(main())
