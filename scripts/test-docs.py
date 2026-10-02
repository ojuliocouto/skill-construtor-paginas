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


    def test_t19_nenhum_caminho_fixo_na_pasta_do_dono(self):
        # So funcionava porque o dono tem a skill em ~/.claude/skills. Instalacao (git clone,
        # skills add) e o unico lugar onde o destino aparece por extenso.
        ruins = []
        for p, t in textos("SKILL.md", "README.md", "references/*.md"):
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"(~|\$HOME)/\.claude/skills/", linha) and not re.search(r"git clone|skills add", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
                if re.search(r"^SKILL=", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])

    def test_t19_dir_da_skill_explicado(self):
        self.assertRegex(SKILL.read_text(encoding="utf-8")[:6000], r"<dir-da-skill>.{0,40}(pasta|diret)")


    def test_t6_preferencias_genericas_existem_e_nao_citam_pessoa(self):
        pref = RAIZ / "references" / "preferencias-de-design.md"
        self.assertTrue(pref.exists(), "references/preferencias-de-design.md nao existe")
        texto = pref.read_text(encoding="utf-8")
        for nome in ("Júlio", "Julio", "Thales", "MaestrIA", "AutonomIA", "EA", "Operação Claude Code", "Laude"):
            self.assertNotRegex(texto, rf"\b{re.escape(nome)}\b", nome)
        for regra in ("kicker", "01/02/03", "número gigante", "inteira", "pricing", "lado a lado", "vermelho"):
            self.assertIn(regra.lower(), texto.lower(), regra)

    def test_t6_skill_e_scripts_falam_de_toda_pagina(self):
        ruins = []
        for p, t in textos("SKILL.md", "references/index.yaml", "scripts/*.py", "scripts/*.js", "scripts/*.mjs", "hooks/*.py"):
            if p.name.startswith("test-"):
                continue
            for n, linha in enumerate(t.splitlines(), 1):
                if re.search(r"J[uú]lio|MaestrIA|preferencias-dono-ea|\(ex: EA\)", linha):
                    ruins.append(f"{p.name}:{n}: {linha.strip()[:70]}")
        self.assertEqual(ruins, [])


    def secao(self, inicio, fim):
        t = SKILL.read_text(encoding="utf-8")
        i = t.index(inicio)
        return t[i:t.index(fim, i)]

    def test_t7_precedencia_banco_x_skills_de_design_no_2_0(self):
        s = self.secao("### 2.0 Consultar o BANCO DE DESIGN", "### 2.1 ")
        self.assertRegex(s.lower(), r"ponto de partida")
        self.assertRegex(s.lower(), r"pr[oó]ximo resultado do banco")
        self.assertRegex(s.lower(), r"creme")
        self.assertRegex(s.lower(), r"motivo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
