"""3.8.0 (27/10/2026): o gate de SEO precisa estar nos textos que o agente e o aluno leem.

Auditoria de SEO de 27/10/2026 em duas páginas reais da IAutomate (sales: SEO 83; SobrAI: SEO 66 e 0 palavras no HTML cru).
Aqui se prova que o SKILL.md, o criar.md, o plano.md, o clonar.md, o README e o CHANGELOG dizem o mesmo que o código:
o comando do gate, o comando que cria os três arquivos antes dele, a linha `Domínio final:` do PLANO e a linha SEO do bloco da entrega.
"""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"
README = RAIZ / "README.md"
CHANGELOG = RAIZ / "CHANGELOG.md"
CRIAR = RAIZ / "references" / "caminhos" / "criar.md"
CLONAR = RAIZ / "references" / "caminhos" / "clonar.md"
PLANO = RAIZ / "references" / "plano.md"
TRAVESSOES = (chr(0x2014), chr(0x2013))


def ler(p):
    return p.read_text(encoding="utf-8")


def trecho(t, ini, fim):
    i = t.index(ini)
    j = t.find(fim, i + len(ini))
    return t[i:] if j < 0 else t[i:j]


class Versao(unittest.TestCase):
    def test_skill_na_3_8_0_e_readme_e_changelog_acompanham(self):
        self.assertRegex(ler(SKILL)[:600], r"(?m)^version: 3\.8\.0$")
        self.assertIn("router (v3.8.0)", ler(README))
        self.assertTrue(ler(CHANGELOG).startswith("# Changelog\n\n## 3.8.0 (27/10/2026): gate de SEO"), ler(CHANGELOG)[:90])


class Skill(unittest.TestCase):
    def test_tabela_de_scripts_tem_o_gate_e_o_gerador_no_passo_f(self):
        # o SKILL.md tem teto de 330 linhas (test-docs-3510-juncao.py): os dois scripts dividem a linha da tabela
        linhas = [l for l in ler(SKILL).splitlines() if l.startswith("| `gate-seo.py`")]
        self.assertEqual(len(linhas), 1)
        self.assertIn("`gerar-seo.py`", linhas[0])
        self.assertTrue(linhas[0].rstrip().endswith("| f |"), linhas[0])

    def test_skill_md_continua_dentro_do_teto_de_330_linhas(self):
        self.assertLessEqual(len(ler(SKILL).splitlines()), 330)

    def test_bloco_da_entrega_leva_canonical_json_ld_e_a_linha_seo(self):
        bloco = trecho(ler(SKILL), "## Bloco obrigatório da entrega", "No EDITAR o bloco")
        ident = [l for l in bloco.splitlines() if l.startswith("IDENTIDADE DA PÁGINA:")]
        self.assertEqual(len(ident), 1)
        self.assertIn("canonical", ident[0])
        self.assertIn("JSON-LD", ident[0])
        seo = [l for l in bloco.splitlines() if l.startswith("SEO:")]
        self.assertEqual(seo, ["SEO: gate-seo <passa|reprova> no modo <prévia|domínio> | palavras no HTML cru <N> | pendências: <lista>"])


class Criar(unittest.TestCase):
    def etapa_f(self):
        c = ler(CRIAR)
        return c[c.index("## f. Gates mecânicos"):c.index("## g. Auditores")]

    def test_comando_do_gate_junto_dos_de_publicacao_e_rastreamento(self):
        f = self.etapa_f()
        gate = "py.mjs gate-seo.py --dist <dir>/dist --plano <dir>/PLANO.md"
        self.assertIn(gate, f)
        self.assertLess(f.index("gate-publicacao.py"), f.index(gate))
        self.assertLess(f.index("gate-rastreamento.py"), f.index(gate))
        self.assertLess(f.index(gate), f.index("gate-plano.py --projeto"))

    def test_nome_seo_na_lista_de_nomes_da_wave(self):
        nomes = re.search(r"\(nomes: ([^)]+)\)", self.etapa_f()).group(1)
        self.assertIn("`seo`", nomes)

    def test_gerar_seo_vem_antes_do_gate_e_roda_na_pasta_do_projeto(self):
        f = self.etapa_f()
        gerar = "py.mjs gerar-seo.py --dist <dir> --url-final"
        self.assertIn(gerar, f)
        self.assertLess(f.index(gerar), f.index("py.mjs gate-seo.py"))
        # o montar-dist apaga da dist o que o projeto não tem: o gerador roda no projeto, não na dist/
        pos = f.index(gerar)
        explicacao = f[pos:pos + 900]
        for item in ("projeto", "montar-dist", "404.html"):
            self.assertIn(item, explicacao, item)

    def test_etapa_f_diz_que_o_gate_roda_no_comando_unico_e_os_dois_modos(self):
        f = self.etapa_f()
        for item in ("modo prévia", "modo domínio", "Domínio final:"):
            self.assertIn(item, f, item)

    def test_etapa_e_lista_o_seo_do_html_cru(self):
        c = ler(CRIAR)
        e = c[c.index("## e. Construção"):c.index("## f. Gates mecânicos")]
        for item in ("300 palavras", "canonical", "JSON-LD", "h1"):
            self.assertIn(item, e, item)


class Plano(unittest.TestCase):
    def test_modelo_da_secao_f_tem_a_linha_dominio_final(self):
        p = ler(PLANO)
        modelo = p[p.index("## f. Código e publicação\n"):p.index("## g. Aprovação\n")]
        self.assertRegex(modelo, r"(?m)^Domínio final: a definir$")
        for termo in ("noindex", "robots", "og:image"):     # o gate-plano cobra estes três na seção f
            self.assertIn(termo, modelo)

    def test_o_que_o_gate_cobra_explica_os_dois_modos(self):
        p = ler(PLANO)
        for item in ("gate-seo.py", "gerar-seo.py", "prévia", "domínio final", "Domínio final:"):
            self.assertIn(item, p, item)

    def test_o_modelo_do_plano_sem_trocar_e_modo_previa(self):
        """O texto do modelo, copiado como está, não liga o modo domínio por engano."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("gate_seo", pathlib.Path(__file__).with_name("gate-seo.py"))
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        import tempfile
        with tempfile.TemporaryDirectory() as t:
            arq = pathlib.Path(t) / "PLANO.md"
            p = ler(PLANO)
            arq.write_text(p[p.index("## f. Código e publicação\n"):p.index("## g. Aprovação\n")], encoding="utf-8")
            self.assertIsNone(gate.url_do_plano(arq))


class Clonar(unittest.TestCase):
    def test_clonar_lista_o_seo_entre_os_avisos_por_fidelidade(self):
        c = ler(CLONAR)
        trecho_avisos = c[c.index("- Viram AVISO"):c.index("Leia cada aviso")]
        self.assertIn("`seo`", trecho_avisos)


class Readme(unittest.TestCase):
    def test_readme_tem_a_secao_do_gate_de_seo_em_ingles(self):
        r = ler(README)
        sec = trecho(r, "## SEO gate", "\n## ")
        for item in ("gate-seo.py", "gerar-seo.py", "preview", "domain", "robots.txt", "sitemap.xml", "404.html", "JSON-LD", "--raiz", "Domínio final:"):
            self.assertIn(item, sec, item)

    def test_readme_novidades_e_lista_de_testes(self):
        r = ler(README)
        self.assertIn("## What is new in 3.8.0", r)
        self.assertLess(r.index("## What is new in 3.8.0"), r.index("## What is new in 3.7.1"))
        for t in ("test-gate-seo.py", "test-gerar-seo.py", "test-docs-380.py"):
            self.assertIn(t, r, t)


class Changelog(unittest.TestCase):
    def test_entrada_3_8_0_com_os_numeros_das_duas_paginas_e_a_contagem_de_testes(self):
        c = ler(CHANGELOG)
        sec = c[c.index("## 3.8.0"):c.index("## 3.7.1")]
        for item in ("sales.juliocouto.com.br", "SobrAI", "83", "66", "100", "281 KB", "364 KB", "3,6 MB", "1.710", "gate-seo.py", "gerar-seo.py",
                     "404.html", "seo-audit", "Lighthouse"):
            self.assertIn(item, sec, item)
        self.assertRegex(sec, r"rodar-testes\.mjs` \d+ de \d+")


class SemTravessao(unittest.TestCase):
    def test_nenhum_arquivo_novo_ou_mudado_tem_travessao(self):
        arquivos = [SKILL, README, CHANGELOG, CRIAR, CLONAR, PLANO] + [RAIZ / "scripts" / n for n in (
            "gate-seo.py", "gerar-seo.py", "test-gate-seo.py", "test-gerar-seo.py", "test-docs-380.py", "conserto-de-gate.mjs", "rodar-gates.mjs", "montar-dist.py")]
        for a in arquivos:
            t = ler(a)
            # o histórico antigo do CHANGELOG e do README pode ter; o que vale aqui é a seção 3.8.0 e as seções novas
            if a in (CHANGELOG,):
                t = t[:t.index("## 3.7.1")]
            if a in (README,):
                t = t[:t.index("## What is new in 3.7.1")] if "## What is new in 3.8.0" in t else ""
            for ch in TRAVESSOES:
                self.assertNotIn(ch, t, f"{a.name}: travessão")


if __name__ == "__main__":
    unittest.main()
