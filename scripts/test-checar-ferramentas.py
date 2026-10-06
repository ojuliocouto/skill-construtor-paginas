#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste do verificador de ferramentas.

Um verificador que nunca reprova nada e pior do que nenhum: passa confianca falsa. Foi
exatamente assim que o MCP do 21st.dev ficou meses morto sendo dado como presente, porque a
deteccao era "aparece na lista?" e ele aparecia. Este teste garante que o checador REPROVA
o que tem que reprovar.

Nao depende do ambiente: o unico caso que exigiria ferramenta instalada e pulado com aviso
quando ela nao esta la.

    python3 scripts/test-checar-ferramentas.py
"""
import importlib.util
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("chk", AQUI / "checar-ferramentas.py")
chk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chk)

falhas, pulados = [], []


def checa(nome, condicao, detalhe=""):
    print(f"  [{'ok  ' if condicao else 'FALHA'}] {nome}{(' -> ' + detalhe) if detalhe else ''}")
    if not condicao:
        falhas.append(nome)


est, _ = chk.estado_mcp("servidor-mcp-que-nao-existe-xyz")
checa("MCP inexistente nao pode ser 'conectado'", est != "conectado", est)

checa("skill inexistente nao pode existir", not chk.skill_existe("skill-que-nao-existe-xyz"))

# O instalador (`npx skills add ... -g`) grava na pasta de config do Claude, que pode vir de
# CLAUDE_CONFIG_DIR; sem `-g` ele grava em ./.claude/skills da pasta atual. O verificador tem
# que achar a skill nos dois lugares, senao o aluno fica com "critico faltando" pra sempre.
import os
import tempfile

with tempfile.TemporaryDirectory() as _tmp:
    _base = pathlib.Path(_tmp)
    (_base / "cfg" / "skills" / "skill-de-teste-cfg").mkdir(parents=True)
    (_base / "proj" / ".claude" / "skills" / "skill-de-teste-proj").mkdir(parents=True)
    _env_antes, _cwd_antes = os.environ.get("CLAUDE_CONFIG_DIR"), os.getcwd()
    try:
        os.environ["CLAUDE_CONFIG_DIR"] = str(_base / "cfg")
        checa("acha skill na pasta de CLAUDE_CONFIG_DIR", chk.skill_existe("skill-de-teste-cfg"))
        os.chdir(_base / "proj")
        checa("acha skill de projeto em ./.claude/skills", chk.skill_existe("skill-de-teste-proj"))
    finally:
        os.chdir(_cwd_antes)
        if _env_antes is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = _env_antes

_fonte_chk = (AQUI / "checar-ferramentas.py").read_text(encoding="utf-8")
_linhas_add = [l for l in _fonte_chk.splitlines() if "skills add " in l]
# No Windows o Python roda comando de texto pelo cmd.exe, que nao entende VAR="x" comando.
# Variavel de ambiente vai pelo parametro env, nunca na frente do comando.
checa("nenhum comando poe variavel de ambiente na frente (quebra no Windows)",
      'NODE_PATH="' not in _fonte_chk and "env=" in _fonte_chk)
checa("todo `skills add` instala global, sem pergunta e por copia (-g -y --copy)",
      bool(_linhas_add) and all("-g -y --copy" in l for l in _linhas_add),
      f"{sum('-g -y --copy' not in l for l in _linhas_add)} linha(s) sem as opcoes")

ok, _ = chk.roda("comando-que-nao-existe-xyz", timeout=5)
checa("binario ausente vira ok=False (nao excecao)", ok is False)

ok, saida = chk.roda("python3 -c \"import time; time.sleep(5)\"", timeout=1)
checa("timeout vira ok=False, com a saida explicando", ok is False and "timeout" in saida.lower(), saida[:40])

# As quatro classificacoes: sao elas que separam "responde" de "esta configurado".
# Sem isso, "Needs authentication" (o estado real do 21st.dev morto) passa por conectado.
orig = chk.roda
for linha, esperado in [
    ("magic: npx -y @21st-dev/magic - ✔ Connected", "conectado"),
    ("magic: npx -y @21st-dev/magic - ✗ Needs authentication", "sem_auth"),
    ("magic: npx -y @21st-dev/magic - ✗ Failed to connect", "falhou"),
    ("magic: npx -y @21st-dev/magic - ⚠ Tools fetch failed", "tools_falharam"),
]:
    chk.roda = lambda *a, _l=linha, **k: (True, _l)
    got, _ = chk.estado_mcp("magic")
    checa(f"'{linha.split('- ')[1]}' classifica como {esperado}", got == esperado, got)
chk.roda = orig

# 21st.dev e Higgsfield sao OPCIONAIS pro aluno (relatorio do aluno, 02/10/2026): quem nao
# paga nada tem que conseguir fazer a pagina. Critico e so o que a skill nao funciona sem.
crit = getattr(chk, "CRITICIDADE", {})
checa("21st.dev e opcional (nunca bloqueia o aluno)", crit.get("21st") is False, str(crit.get("21st")))
checa("Higgsfield e opcional (nunca bloqueia o aluno)", crit.get("Higgsfield CLI") is False, str(crit.get("Higgsfield CLI")))
checa("Playwright continua critico", crit.get("Playwright") is True, str(crit.get("Playwright")))

# v3 (02/10/2026): a skill depende de frontend-design, auditores e pesquisa de referencias.
# Critico e EXATAMENTE python3, node, Playwright e a skill frontend-design. Nada mais bloqueia.
criticos_v3 = {k for k, v in crit.items() if v}
checa("criticos da v3 sao so python3, node, Playwright e frontend-design",
      criticos_v3 == {"python3", "node", "Playwright", "skill frontend-design"}, str(sorted(criticos_v3)))
for opcional in ("skill design-taste-frontend", "Banco de design", "Assets sem chave (Openverse)", "stitch",
                 "skill high-end-visual-design", "skill animate"):
    checa(f"{opcional} e opcional na v3", crit.get(opcional) is False, str(crit.get(opcional)))

# v3.5: o gate-imagens (repeticao e nitidez) e a prancha de animacao medem com Pillow e numpy. Sao
# opcionais (nunca bloqueiam o aluno), mas o verificador avisa o que falta e como instalar.
checa("Pillow e numpy sao opcionais, com aviso", crit.get("Pillow e numpy") is False, str(crit.get("Pillow e numpy")))
pn = [l for l in chk.checagens(False) if l[0] == "Pillow e numpy"]
checa("o verificador checa Pillow e numpy e diz como instalar",
      len(pn) == 1 and "pip install pillow numpy" in pn[0][5] and pn[0][3] in (True, False), str(pn))

# frontend-design ausente tem que reprovar (exit 1); opcional ausente nunca reprova.
orig_skill = chk.skill_existe
orig_argv = sys.argv
import contextlib as _ctx, io as _io
sys.argv = ["checar-ferramentas.py", "--json"]
chk.skill_existe = lambda nome: nome != "frontend-design"
with _ctx.redirect_stdout(_io.StringIO()):
    saida_sem_fd = chk.main()
checa("sem a skill frontend-design o verificador sai 1", saida_sem_fd == 1, str(saida_sem_fd))
chk.skill_existe = lambda nome: nome == "frontend-design"
with _ctx.redirect_stdout(_io.StringIO()) as buf:
    saida_so_fd = chk.main()
linhas_json = __import__("json").loads(buf.getvalue())
lento = [l for l in linhas_json if l["ferramenta"] == "21st"][0]
checa("sem nenhuma skill opcional o verificador nao reprova (so falta opcional)",
      saida_so_fd == 0 or any(l["critico"] and not l["ok"] for l in linhas_json if l["ferramenta"] != "skill frontend-design"),
      str(saida_so_fd))
checa("opcional lento sem --opcionais sai como nao checado (nem verde nem vermelho)",
      lento["checado"] is False and lento["ok"] is None, str(lento))
chk.skill_existe = orig_skill
sys.argv = orig_argv

# O teste do 21st tem que fazer CHAMADA REAL com a chave. Lista de MCP nao prova chave.
import os as _os
teste21 = getattr(chk, "testar_21st", None)
checa("existe testar_21st (chamada real)", callable(teste21))
if callable(teste21):
    salvo = {k: _os.environ.pop(k) for k in list(_os.environ) if k in chk.CHAVES_21ST}
    orig_mcp = chk.estado_mcp
    chk.estado_mcp = lambda n: ("conectado", f"{n}: ✔ Connected")
    ok21, det21 = teste21()
    checa("21st sem chave no ambiente NAO passa so por estar na lista", ok21 is False, det21[:70])
    chamadas = []
    def falso_401(url, corpo, cab, timeout=20):
        chamadas.append((url, cab))
        return 401, {}, '{"error":{"message":"Not authenticated"}}'
    _os.environ[chk.CHAVES_21ST[0]] = "chave-de-teste"
    orig_post = chk._post_json
    chk._post_json = falso_401
    ok21, det21 = teste21()
    checa("21st com chave recusada (401) reprova", ok21 is False and "401" in det21, det21[:70])
    checa("a chamada real manda a chave no cabecalho", any(c[1].get("x-api-key") == "chave-de-teste" for c in chamadas))
    respostas = iter([
        (200, {"mcp-session-id": "s1"}, '{"jsonrpc":"2.0","id":1,"result":{"capabilities":{}}}'),
        (202, {}, ""),
        (200, {}, 'event: message\ndata: {"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"search","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}]}}'),
        (200, {}, '{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"Button"}]}}'),
    ])
    chk._post_json = lambda url, corpo, cab, timeout=20: next(respostas)
    ok21, det21 = teste21()
    checa("21st com chave valida e busca que devolve componente passa", ok21 is True, det21[:70])
    chk._post_json = orig_post
    chk.estado_mcp = orig_mcp
    _os.environ.pop(chk.CHAVES_21ST[0], None)
    _os.environ.update(salvo)

# So faz sentido se a ferramenta estiver instalada: senao seria testar o ambiente, nao o checador.
est_magic, det = chk.estado_mcp("magic")
if est_magic == "ausente":
    pulados.append("magic nao esta configurado nesta maquina: pulei o caso positivo")
else:
    checa("MCP presente e classificado (nao 'ausente')", est_magic != "ausente", est_magic)

print()
for p in pulados:
    print("  pulado:", p)
if falhas:
    print(f"\n  {len(falhas)} caso(s) falharam. O verificador nao esta confiavel.\n")
    sys.exit(1)
print("\n  Verificador confiavel: reprova o que tem que reprovar.\n")
