"""3.5.10, frente A: o que o roteiro do caminho CRIAR (e o SKILL.md) precisa dizer depois do teste de aluno da página Torra Clara.

Arquivo próprio para não colidir com o test-docs.py nas três frentes da 3.5.10. Cada teste cita o achado (P1 a P17) do
relatório `pagina-teste-358/RELATORIO.md`, seção 5. Texto não roda sozinho: o que dá para medir no texto vira asserção.
"""
import pathlib
import re
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SKILL = RAIZ / "SKILL.md"
REF = RAIZ / "references"
CRIAR = REF / "caminhos" / "criar.md"


def ler(p):
    return p.read_text(encoding="utf-8")


def secao_b(criar):
    i = criar.index("## b. Pesquisa de referências")
    return criar[i:criar.index("## b2. PLANO", i)]


def linha_do_comando(texto, script):
    """A linha de comando (entre crases) que roda `script` e tem os argumentos do roteiro."""
    achadas = [m.group(0) for m in re.finditer(r"`node [^`\n]*" + re.escape(script) + r"[^`\n]*`", texto)]
    return achadas


class PassoB(unittest.TestCase):
    def test_extra_o_passo_b_cita_o_remover_e_diz_quando_usar(self):
        b = secao_b(ler(CRIAR))
        self.assertIn("--remover", b)
        self.assertRegex(b, r"(?s)--remover[^\n]*\n?[^\n]*(ok|serve|cookie)")

    def test_p2_p3_o_passo_b_diz_o_que_fazer_com_aviso_de_cookies_que_continua_e_com_meio_igual_a_dobra(self):
        b = secao_b(ler(CRIAR))
        self.assertRegex(b, r"(?i)aviso de cookies continua vis[ií]vel")
        self.assertRegex(b, r"(?i)meio (igual|é igual)[^\n]*dobra|igual ao da dobra")
        self.assertIn("--longa", b)

    def test_p1_o_passo_b_lista_o_bloqueio_de_robo_como_estado_bloqueada(self):
        b = secao_b(ler(CRIAR))
        self.assertRegex(b, r"(?i)bloqueada")
        self.assertRegex(b, r"(?i)verificar a seguran[cç]a da (sua )?conex[aã]o|verify the security of your connection")


class PassoE(unittest.TestCase):
    def test_p6_unsplash_nao_abre_por_script_e_a_busca_explicita_cai_para_a_commons(self):
        criar = ler(CRIAR)
        self.assertRegex(criar, r"(?s)Unsplash[^.]{0,120}n[aã]o abre por script")
        self.assertIn("307", criar)
        self.assertRegex(criar, r"(?s)--type openverse[^.]{0,200}Commons|Openverse n[aã]o responder[^.]{0,120}Commons")

    def test_p7_o_comando_da_og_image_passa_fonte_do_titulo_e_as_cores_do_plano_visual(self):
        criar = ler(CRIAR)
        cmds = linha_do_comando(criar, "gerar-og-image.mjs")
        self.assertTrue(cmds, "criar.md não traz o comando do gerar-og-image.mjs")
        um = cmds[0]
        for flag in ("--fonte", "--cor-fundo", "--cor-texto", "--titulo", "--foto"):
            self.assertIn(flag, um, f"o comando da og:image não mostra {flag}: {um}")
        self.assertRegex(criar, r"(?s)--fonte[^.]{0,200}t[ií]tulo")
        self.assertRegex(criar, r"(?s)--cor-fundo[^.]{0,200}(plano-visual|paleta)")

    def test_p17_o_criar_diz_os_nomes_dos_icones_e_as_duas_linhas_de_link(self):
        criar = ler(CRIAR)
        self.assertIn('<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">', criar)
        self.assertIn('<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">', criar)
        self.assertRegex(criar, r"(?s)gerar-icones\.mjs[^\n]*\n?[^\n]*(raiz|n[aã]o em `?icones/)")

    def test_extra_sobreposicao_sem_elemento_fixo_nao_se_aplica_e_diz_como_registrar(self):
        criar = ler(CRIAR)
        i = criar.index("sobreposicao.mjs --url")
        trecho = criar[i:i + 1500]
        self.assertRegex(trecho, r"(?i)n[aã]o (se aplica|roda)")
        self.assertRegex(trecho, r"(?i)sem elemento (fixo|sticky)|nenhum elemento (fixo|sticky)|n[aã]o tem (elemento )?(sticky|fixo)")
        self.assertRegex(trecho, r"grep")


class RegistroDeSessao(unittest.TestCase):
    """P16: o N25 da 3.5.9 tirou a ordem de gravar em references/sessions e references/projects; aqui vai o resto (modelos e README)."""

    def test_os_modelos_nao_mandam_para_o_registro_dentro_da_pasta_da_skill(self):
        for nome in ("sessions", "projects"):
            t = ler(REF / nome / "EXAMPLE.md")
            self.assertNotRegex(t, r"references/(projects|sessions)/\{", f"{nome}/EXAMPLE.md aponta para um registro dentro da pasta da skill")
            self.assertIn("<projeto>/", t, nome)

    def test_nenhum_texto_manda_gravar_na_pasta_da_skill(self):
        for p in (SKILL, CRIAR):
            t = ler(p)
            for m in re.finditer(r"(registre|salve|grave|atualize|copie)[^\n]{0,80}`references/(sessions|projects)/[^`]*`", t, re.I):
                self.assertRegex(m.group(0), r"(?i)modelo|copie|só para copiar|leitura", f"{p.name}: {m.group(0)}")

    def test_readme_nao_diz_que_o_registro_real_mora_na_pasta_da_skill(self):
        t = ler(RAIZ / "README.md")
        for linha in t.splitlines():
            if "EXAMPLE.md" in linha and ("projects/" in linha or "sessions/" in linha):
                self.assertNotRegex(linha, r"real files are local", linha)


if __name__ == "__main__":
    unittest.main(verbosity=2)
