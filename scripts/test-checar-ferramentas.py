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
