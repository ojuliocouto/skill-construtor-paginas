# -*- coding: utf-8 -*-
"""Monta o comando que o aluno deve rodar, com o caminho COMPLETO da skill (achado A10).

Quem roda um script da skill está na pasta do projeto, não na da skill; um `node scripts/py.mjs ...`
impresso ali não existe. Aqui o caminho é resolvido em tempo de execução, no formato do lançador:

    comando("gate-plano.py")            -> node /.../construtor-paginas/scripts/py.mjs gate-plano.py
    comando("gerar-icones.mjs")         -> node /.../construtor-paginas/scripts/gerar-icones.mjs

O caminho sai com barras normais (`as_posix`), que o Node entende também no Windows.
"""
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def comando(script):
    if not (AQUI / script).is_file():
        raise FileNotFoundError(f"script da skill inexistente: {script}")
    if script.endswith(".py"):
        return f"node {(AQUI / 'py.mjs').as_posix()} {script}"
    return f"node {(AQUI / script).as_posix()}"
