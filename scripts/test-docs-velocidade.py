"""Documentação dos cortes de velocidade (auditoria de velocidade): o que o `criar.md` manda tem que bater com o que os scripts fazem.

Corte 3 (tempo-limite): o Bash corta o comando em 120 s quando ninguém passa o tempo-limite. O `rodar-gates.mjs` leva até 256 s, e o
construtor de uma página real caiu em 65 laços de espera (102,7 min). O `criar.md` tem que mandar rodar em primeiro plano, com
tempo-limite de 10 minutos (600000 ms), e proibir o laço de espera.
Os outros cortes tem que estar descritos onde o construtor os lê: cache dos gates, registro automático na wave, prova em paralelo,
registro em lote das lentes.
"""
import pathlib
import re
import subprocess
import sys
import unittest

RAIZ = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = RAIZ / "scripts"
CRIAR = (RAIZ / "references" / "caminhos" / "criar.md").read_text(encoding="utf-8")
SKILL = (RAIZ / "SKILL.md").read_text(encoding="utf-8")


def secao(md, titulo_inicio, proximo=r"\n## [a-z]\. "):
    ini = md.index(titulo_inicio)
    resto = md[ini + len(titulo_inicio):]
    m = re.search(proximo, resto)
    return titulo_inicio + (resto[:m.start()] if m else resto)


F = secao(CRIAR, "## f. Gates mecânicos")
G = secao(CRIAR, "## g. Auditores")
H = secao(CRIAR, "## h. Prova e entrega")


class TempoLimite(unittest.TestCase):
    """Corte 3: gate em primeiro plano, com tempo-limite explícito de 10 minutos."""

    def trecho_do_comando_padrao(self):
        i = F.index("**Caminho padrão: um comando só")
        return F[i:i + 2600]

    def test_o_comando_padrao_manda_primeiro_plano_com_600000_ms(self):
        t = self.trecho_do_comando_padrao()
        self.assertIn("600000", t)
        self.assertRegex(t, r"(?i)primeiro plano")
        self.assertRegex(t, r"(?i)laço de espera")

    def test_explica_o_porque_com_o_numero_medido(self):
        t = self.trecho_do_comando_padrao()
        self.assertIn("120 s", t, "o limite padrão do Bash, que corta o comando")
        self.assertIn("102,7", t, "o custo medido do laço de espera")

    def test_proibe_segundo_plano_com_laco(self):
        t = self.trecho_do_comando_padrao()
        self.assertRegex(t, r"(?i)nunca em segundo plano")
        self.assertRegex(t, r"(?i)até 10 minutos|10 minutos")

    def test_a_prova_de_tela_tambem_manda_o_mesmo(self):
        self.assertIn("600000", G)
        self.assertRegex(G, r"(?i)primeiro plano")

    def test_o_proprio_comando_diz_o_mesmo_na_saida(self):
        for nome in ("rodar-gates.mjs", "provar.mjs"):
            texto = (SCRIPTS / nome).read_text(encoding="utf-8")
            self.assertIn("600000", texto, nome)
            self.assertIn("primeiro plano", texto, nome)
            self.assertIn("laço de espera", texto, nome)


class CacheERegistro(unittest.TestCase):
    def test_o_criar_md_descreve_o_cache_por_conteudo_e_o_jeito_de_forcar(self):
        self.assertRegex(F, r"(?i)cache")
        self.assertIn("--sem-cache", F)
        self.assertRegex(F, r"(?i)reprovação nunca entra no cache|só PASSA entra no cache|só o que passou")

    def test_o_criar_md_nao_diz_mais_que_o_comando_nao_registra(self):
        self.assertNotIn("o comando não registra nem aprova nada", CRIAR)
        self.assertNotIn("este comando não registra nem aprova nada", CRIAR)

    def test_o_criar_md_diz_que_a_rodada_completa_registra_na_wave(self):
        self.assertIn("gates-lote", F)
        self.assertRegex(F, r"(?i)rodada completa[^\n]*registra")
        self.assertIn("--sem-registrar", F)

    def test_o_registro_a_mao_continua_documentado_para_os_gates_fora_do_comando(self):
        # identidade vem do screenshot-prova (registrada pelo provar.mjs); uso-ferramentas segue à mão
        self.assertIn("uso-ferramentas", F)
        self.assertIn("wave.py", F)


class ProvaEmParalelo(unittest.TestCase):
    def test_o_criar_md_manda_o_provar_na_prova_de_tela(self):
        self.assertIn("provar.mjs", G)
        self.assertRegex(G, r"(?i)duas por vez|2 por vez|dois por vez")
        self.assertIn("--sem-anim", G)

    def test_o_provar_substitui_os_tres_comandos_sem_apagar_os_individuais(self):
        for cmd in ("screenshot-prova.js", "gravar-video.js", "anim.mjs"):
            self.assertIn(cmd, CRIAR)

    def test_o_criar_md_diz_que_o_video_grava_os_dois_perfis_juntos_e_a_captura_dois_enderecos(self):
        self.assertRegex(CRIAR, r"(?i)desktop e celular (juntos|ao mesmo tempo)|os dois perfis")
        self.assertRegex(CRIAR, r"(?i)dois endereços por vez|2 endereços por vez|dois por vez")

    def test_h_nao_manda_gravar_de_novo_o_que_o_provar_ja_fez(self):
        self.assertIn("provar.mjs", H)


class RegistroDasLentes(unittest.TestCase):
    def test_o_criar_md_manda_registrar_as_lentes_de_uma_vez(self):
        self.assertIn("registrar-lote", G)
        self.assertIn("--origem", G)

    def test_o_registro_um_a_um_continua_documentado(self):
        self.assertIn("wave.py --projeto <dir> registrar <lente>", G)


class SkillMd(unittest.TestCase):
    def test_a_tabela_de_scripts_lista_os_scripts_novos(self):
        for nome in ("provar.mjs", "gates-cache.mjs", "dist_hash.py"):
            self.assertIn(nome, SKILL, nome)
        self.assertIn("rodar-gates.mjs", SKILL)

    def test_a_linha_do_wave_menciona_o_lote(self):
        linha = next(l for l in SKILL.splitlines() if l.startswith("| `wave.py`"))
        self.assertIn("lote", linha)


class SuiteDeTestes(unittest.TestCase):
    def lista(self, *extra):
        r = subprocess.run(["node", str(SCRIPTS / "rodar-testes.mjs"), "--lista", *extra], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_os_testes_de_navegador_novos_ficam_fora_do_conjunto_portatil(self):
        portateis = self.lista("--so-portateis")
        for nome in ("test-capturar-paralelo.cjs", "test-gravar-video-paralelo.cjs", "test-movimento-paralelo.cjs"):
            self.assertNotIn(nome, portateis, f"{nome} precisa de navegador e não é portátil")

    def test_os_testes_sem_navegador_novos_entram_no_conjunto_portatil(self):
        portateis = self.lista("--so-portateis")
        for nome in ("test-dist-hash.py", "test-gates-cache.cjs", "test-provar.cjs", "test-wave-lote.py", "test-docs-velocidade.py"):
            self.assertIn(nome, portateis, nome)


class SemTravessao(unittest.TestCase):
    def test_arquivos_novos_e_documentacao_sem_travessao(self):
        novos = ["dist_hash.py", "gates-cache.mjs", "provar.mjs", "test-dist-hash.py", "test-gates-cache.cjs", "test-provar.cjs",
                 "test-wave-lote.py", "test-capturar-paralelo.cjs", "test-gravar-video-paralelo.cjs", "test-movimento-paralelo.cjs",
                 "test-docs-velocidade.py", "rodar-gates.mjs", "montar-dist.py", "wave.py", "gate-movimento.mjs", "capturar-referencias.mjs", "gravar-video.js"]
        achados = []
        for n in novos:
            texto = (SCRIPTS / n).read_text(encoding="utf-8")
            if "\u2014" in texto or "\u2013" in texto:
                achados.append(n)
        for n in (RAIZ / "references" / "caminhos" / "criar.md", RAIZ / "SKILL.md"):
            texto = n.read_text(encoding="utf-8")
            if "\u2014" in texto or "\u2013" in texto:
                achados.append(n.name)
        self.assertEqual(achados, [], "travessão ou meia-risca nos arquivos")


if __name__ == "__main__":
    unittest.main(verbosity=2)
