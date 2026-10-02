"""O texto da skill também tem gate: o que o aluno copia e cola precisa rodar.

Cada teste nasce de uma travada do teste com aluno (02/10/2026). Texto não roda sozinho,
então o que dá pra medir no texto vira asserção aqui.
"""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"


def textos(*globs):
    for g in globs:
        for p in sorted(RAIZ.glob(g)):
            if "__pycache__" in p.parts or "sessions" in p.parts or "projects" in p.parts:
                continue
            yield p, p.read_text(encoding="utf-8")


class Docs(unittest.TestCase):
    def test_t4_nenhum_comando_em_variavel_que_o_zsh_nao_roda(self):
        # W="python3 ..."; $W registrar -> zsh: "no such file or directory" (exit 127).
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.match(r'\s*[A-Z]+="(python3|node|npx)\b', linha) or re.search(r'\$[A-Z]+ (registrar|gate|checar|rodada|dispensar)\b', linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
