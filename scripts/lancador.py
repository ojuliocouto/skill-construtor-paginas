# -*- coding: utf-8 -*-
"""Monta o comando que o aluno deve rodar, com o caminho COMPLETO da skill (achado A10).

Quem roda um script da skill está na pasta do projeto, não na da skill; um `node scripts/py.mjs ...`
impresso ali não existe. Aqui o caminho é resolvido em tempo de execução, no formato do lançador:

    comando("gate-plano.py")            -> node /.../construtor-paginas/scripts/py.mjs gate-plano.py
    (com espaço ou acento no caminho, ele sai entre aspas duplas: node "C:/curso automação/skill/scripts/py.mjs" gate-plano.py)
    comando("gerar-icones.mjs")         -> node /.../construtor-paginas/scripts/gerar-icones.mjs

O caminho sai com barras normais (`as_posix`), que o Node entende também no Windows.
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _caminho(p):
    """Caminho entre aspas duplas quando tem espaço ou caractere fora de ASCII (funcionam em cmd, PowerShell, bash e zsh)."""
    s = p.as_posix()
    return f'"{s}"' if (" " in s or not s.isascii()) else s


def comando(script):
    if not (AQUI / script).is_file():
        raise FileNotFoundError(f"script da skill inexistente: {script}")
    if script.endswith(".py"):
        return f"node {_caminho(AQUI / 'py.mjs')} {script}"
    return f"node {_caminho(AQUI / script)}"
