"""Achado A10: o 'próximo comando' que os scripts imprimem traz o caminho completo da skill.

Quem roda o script está na pasta do projeto, não na da skill; `node scripts/py.mjs ...` ali não
existe. O módulo `lancador.py` resolve o caminho em tempo de execução, no formato do lançador:
`node <pasta-da-skill>/scripts/py.mjs <script>.py` para Python e `node <...>/scripts/<script>.mjs`
para os de Node.
"""
import importlib.util
import pathlib
import re
import tempfile
import unittest

AQUI = pathlib.Path(__file__).resolve().parent


def carregar():
    spec = importlib.util.spec_from_file_location("lancador", AQUI / "lancador.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def extrai_caminho(c):
    """Primeiro argumento depois de `node `: entre aspas duplas (caminho com espaço ou acento) ou solto."""
    resto = c[len("node "):]
    if resto.startswith('"'):
        return resto[1:resto.index('"', 1)]
    return resto.split(" ")[0]


class Lancador(unittest.TestCase):
    def test_python_vai_pelo_py_mjs_com_caminho_completo(self):
        c = carregar().comando("gate-plano.py")
        self.assertTrue(c.startswith("node "), c)
        caminho = extrai_caminho(c)
        self.assertTrue(pathlib.Path(caminho).is_absolute() or re.match(r"^[A-Za-z]:/", caminho), c)
        self.assertTrue(caminho.endswith("/scripts/py.mjs"), c)
        self.assertTrue(c.endswith(" gate-plano.py"), c)
        self.assertNotIn("\\", c)

    def test_node_vai_direto_com_caminho_completo(self):
        c = carregar().comando("capturar-referencias.mjs")
        self.assertTrue(extrai_caminho(c).endswith("/scripts/capturar-referencias.mjs"), c)
        self.assertTrue((AQUI / "capturar-referencias.mjs").is_file())

    def test_caminho_com_espaco_e_acento_sai_entre_aspas_duplas_em_qualquer_sistema(self):
        """O CI do Windows roda em `C:\\curso automação\\skill`; aqui a pasta é criada com esse nome em qualquer sistema."""
        with tempfile.TemporaryDirectory() as d:
            pasta = pathlib.Path(d) / "curso automação" / "skill" / "scripts"
            pasta.mkdir(parents=True)
            for nome in ("lancador.py", "py.mjs", "gate-plano.py"):
                (pasta / nome).write_text((AQUI / nome).read_text(encoding="utf-8"), encoding="utf-8")
            spec = importlib.util.spec_from_file_location("lancador_acento", pasta / "lancador.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            c = m.comando("gate-plano.py")
            self.assertRegex(c, r'^node "[^"]*curso automação/skill/scripts/py\.mjs" gate-plano\.py$')
            self.assertEqual(extrai_caminho(c), (pasta / "py.mjs").resolve().as_posix())
            self.assertRegex(m.comando("py.mjs"), r'^node "[^"]*curso automação/skill/scripts/py\.mjs"$')

    def test_caminho_simples_nao_leva_aspas(self):
        with tempfile.TemporaryDirectory() as d:
            pasta = pathlib.Path(d) / "skill" / "scripts"
            pasta.mkdir(parents=True)
            for nome in ("lancador.py", "py.mjs"):
                (pasta / nome).write_text((AQUI / nome).read_text(encoding="utf-8"), encoding="utf-8")
            spec = importlib.util.spec_from_file_location("lancador_simples", pasta / "lancador.py")
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            if m.AQUI.as_posix().isascii() and " " not in m.AQUI.as_posix():
                self.assertNotIn('"', m.comando("py.mjs"))

    def test_script_que_nao_existe_levanta(self):
        with self.assertRaises(FileNotFoundError):
            carregar().comando("nao-existe.py")

    def test_nenhum_script_imprime_comando_com_caminho_relativo(self):
        """Linha que imprime, devolve problema ou avisa com `scripts/x.py|mjs|js` tem de usar comando()."""
        ruins = []
        for arq in sorted(AQUI.iterdir()):
            if arq.suffix not in (".py", ".mjs", ".js", ".cjs") or arq.name.startswith("test-") or ".test." in arq.name:
                continue
            if arq.name in ("lancador.py", "py.mjs"):
                continue
            em_docstring = False
            for n, linha in enumerate(arq.read_text(encoding="utf-8").splitlines(), 1):
                if linha.count('"""') % 2 == 1:
                    em_docstring = not em_docstring
                    continue
                if em_docstring or linha.lstrip().startswith(("#", "*", "//", "/*")):
                    continue
                if re.search(r"(print\(|\.append\(|console\.(log|error)|return \[|raise \w+\(|linhas \+=|^\s+['\"f]+.*scripts/)", linha) \
                        and re.search(r"scripts/[\w.-]+\.(py|mjs|js|cjs)", linha) \
                        and "comando(" not in linha and "AQUI" not in linha and "import" not in linha[:12]:
                    ruins.append(f"{arq.name}:{n}: {linha.strip()[:110]}")
        self.assertEqual(ruins, [], "\n".join(ruins))


if __name__ == "__main__":
    unittest.main(verbosity=2)
