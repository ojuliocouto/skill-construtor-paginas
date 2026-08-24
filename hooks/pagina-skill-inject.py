#!/usr/bin/env python3
"""
Hook UserPromptSubmit: força o acionamento da skill construtor-paginas
quando o usuário quer (1) criar página nova, (2) clonar página, ou
(3) criar versão nova de uma página existente.

Injeta só um lembrete curto e forte (a skill carrega de fato quando o
Skill tool é chamado) — não despeja a SKILL.md inteira.
"""
import json
import re
import sys

PAGE = r"(p[áa]gina|landing\s*page|\bsite\b|website|\bhome\b|hero\s*section|dashboard|portf[óo]lio|one[\s-]*pager|sales\s*page|\blp\b|web\s*app|webapp)"
CREATE = r"(criar|cria\b|crie|fazer|\bfaz\b|fa[çc]a|montar|monte|construir|desenvolver|quero|preciso de|gera\b|gerar)"
CLONE = r"(clonar|clona\b|clone|copiar|copia\b|copie|replicar|replica\b|reproduzir|reproduz)"
VERSION = r"(refazer|refa[çc]|recriar|recria\b|redesign|reformular|reformula|nova\s+vers[ãa]o|outra\s+vers[ãa]o|vers[ãa]o\s+nova|\bv2\b|\bv3\b|upgrade|repaginar)"
# "clona essa", "copiar esse", "refazer essa" — implica a página atual mesmo sem o substantivo
DEMONSTRATIVE = r"(ess[ae]|est[ae]|esse|este|aquel)"


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    p = data.get("prompt", "").lower()
    if not p:
        sys.exit(0)

    has_page = re.search(PAGE, p) is not None
    has_create = re.search(CREATE, p) is not None
    has_clone = re.search(CLONE, p) is not None
    has_version = re.search(VERSION, p) is not None
    has_dem = re.search(DEMONSTRATIVE, p) is not None

    caso = None
    if has_page and has_create:
        caso = "CRIAR página nova"
    elif has_clone and (has_page or has_dem):
        caso = "CLONAR página existente"
    elif has_version and (has_page or has_dem):
        caso = "CRIAR versão nova de página existente"

    if not caso:
        sys.exit(0)

    reminder = (
        "=== GATILHO OBRIGATÓRIO: SKILL construtor-paginas ===\n"
        f"Detectado intuito de {caso}. ACIONE a skill `construtor-paginas` AGORA "
        "(via Skill tool) ANTES de escrever qualquer código ou fazer perguntas soltas. "
        "Siga o fluxo da skill (Step 0 → ...).\n"
        "Se for CLONE/versão de site real: manter a IDENTIDADE ORIGINAL (extrair cores "
        "exatas via getComputedStyle no navegador, baixar o LOGO REAL do site, nunca inventar) "
        "e rodar o checklist de tells visuais de IA (references/anti-vibe-coding.md) antes de entregar."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": reminder,
        }
    }))


if __name__ == "__main__":
    main()
