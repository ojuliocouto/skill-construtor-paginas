"""Achado A9: o que os scripts mostram ao aluno sai com acentuação correta.

A skill exige português com acento, e a saída do `checar-ferramentas.py` dizia "Tudo critico
responde. Pode comecar o briefing." Este teste varre as frases (strings de mais de uma palavra)
dos scripts da skill, fora docstring, regex e a parte entre chaves de f-string, atrás de palavras
que SEMPRE levam acento em português ("nao", "pagina", "licenca", "codigo"...). Palavra ambígua
("ate", "esta", "ha", "so") fica de fora de propósito: o teste só reprova o que é certo.
Se uma frase precisa mesmo da grafia sem acento (nome de arquivo, valor de protocolo), escreva-a
fora de uma frase (uma palavra só, ou com crase de código).
"""
import io
import pathlib
import re
import tokenize
import unittest

AQUI = pathlib.Path(__file__).resolve().parent
MAPA={"nao":"não","voce":"você","voces":"vocês","pagina":"página","paginas":"páginas","critico":"crítico","criticos":"críticos","critica":"crítica","criticas":"críticas",
"licenca":"licença","licencas":"licenças","opiniao":"opinião","comecar":"começar","sao":"são","tambem":"também","versao":"versão","informacao":"informação","informacoes":"informações",
"configuracao":"configuração","instalacao":"instalação","codigo":"código","proximo":"próximo","proxima":"próxima","ultimo":"último","ultima":"última","obrigatorio":"obrigatório",
"memoria":"memória","usuario":"usuário","diretorio":"diretório","binario":"binário","numero":"número","indice":"índice","unico":"único","unica":"única","minimo":"mínimo","maximo":"máximo",
"rapido":"rápido","disponivel":"disponível","possivel":"possível","acao":"ação","funcao":"função","execucao":"execução","excecao":"exceção","conexao":"conexão","dependencia":"dependência",
"apos":"após","atraves":"através","tres":"três","util":"útil","preco":"preço","servico":"serviço","negocio":"negócio","sessao":"sessão","descricao":"descrição","solucao":"solução",
"geracao":"geração","ilustracao":"ilustração","verificacao":"verificação","conteudo":"conteúdo","titulo":"título","animacao":"animação","relatorio":"relatório","varios":"vários",
"referencia":"referência","referencias":"referências","secao":"seção","secoes":"seções","invalido":"inválido","invalida":"inválida","ilegivel":"ilegível","especifico":"específico","especifica":"específica",
"proprio":"próprio","propria":"própria","facil":"fácil","dificil":"difícil","basico":"básico","ultimos":"últimos","licao":"lição","atencao":"atenção","opcao":"opção","opcoes":"opções","operacao":"operação",
"duvida":"dúvida","duvidas":"dúvidas","pre-requisito":"pré-requisito","existencia":"existência","experiencia":"experiência","orcamento":"orçamento",
"inicio":"início","tecnica":"técnica","tecnico":"técnico","grafico":"gráfico","automatico":"automático","automatica":"automática","padrao":"padrão","padroes":"padrões","paragrafo":"parágrafo","botao":"botão","botoes":"botões",
"estao":"estão","repeticao":"repetição","video":"vídeo","videos":"vídeos","medicao":"medição","medicoes":"medições","selecao":"seleção","validacao":"validação","correcao":"correção","atualizacao":"atualização","identificacao":"identificação","publicacao":"publicação","producao":"produção","composicao":"composição","comparacao":"comparação","direcao":"direção","direcoes":"direções","edicao":"edição","excecoes":"exceções","regiao":"região","religiao":"religião","razao":"razão","decisao":"decisão","revisao":"revisão","versoes":"versões","licoes":"lições","tera":"terá","sera":"será","fara":"fará","ira":"irá","voltara":"voltará","tambem":"também","porem":"porém","ninguem":"ninguém","alem":"além","nivel":"nível","viuva":"viúva","subtitulo":"subtítulo","minuscula":"minúscula","italico":"itálico","icone":"ícone","icones":"ícones","previa":"prévia","previas":"prévias","cartoes":"cartões","autoavaliacao":"autoavaliação","espaco":"espaço","vao":"vão","ja":"já","so":"só","avaliacao":"avaliação","observacao":"observação","indicacao":"indicação","conclusao":"conclusão","pagina-teste":"página-teste","ilustracoes":"ilustrações","animacoes":"animações","proprias":"próprias","proprios":"próprios","limitacao":"limitação","autorizacao":"autorização","evidencia":"evidência","evidencias":"evidências","cobravel":"cobrável","minusculo":"minúsculo","ate":"até"}

RXW = re.compile(r"(?<!--type )(?<![\w/.`'-])(%s)(?![\w/(`=-]|\s{2,}\S|\.(?:md|svg|json|py|mjs|js|css|html|png|jpg)\b)" % "|".join(sorted(MAPA, key=len, reverse=True)), re.I)
IGNORA = {"core.py"}


def frases_do_script(caminho):
    src = caminho.read_text(encoding="utf-8")
    prev, achados = None, []
    for t in tokenize.generate_tokens(io.StringIO(src).readline):
        if t.type == tokenize.STRING:
            pre = re.match(r"[rbfRBF]*", t.string).group(0)
            doc = prev in (None, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT) and t.string[len(pre):][:3] in ('"""', "'''")
            if not doc and "r" not in pre.lower() and len(t.string) > 14 and " " in t.string:
                texto = t.string
                if "f" in pre.lower():
                    texto = re.sub(r"\{\{|\}\}|\{[^{}]*\}", " ", texto)
                achados.append((t.start[0], texto))
        if t.type not in (tokenize.NL, tokenize.COMMENT):
            prev = t.type
    return achados


class Acentuacao(unittest.TestCase):
    def test_a_regra_pega_o_caso_do_achado(self):
        self.assertTrue(RXW.search("Tudo critico responde. Pode comecar o briefing."))
        self.assertFalse(RXW.search("Tudo crítico responde. Pode começar o briefing."))
        self.assertFalse(RXW.search("rode node scripts/py.mjs gate-plano.py --pagina"))

    def test_nenhuma_frase_dos_scripts_sai_sem_acento(self):
        ruins = []
        for arq in sorted(AQUI.glob("*.py")):
            if arq.name.startswith("test-") or arq.name in IGNORA:
                continue
            for n, texto in frases_do_script(arq):
                m = RXW.search(texto)
                if m:
                    ruins.append(f"{arq.name}:{n}: '{m.group(1)}' em {texto.strip()[:90]}")
        self.assertEqual(ruins, [], "\n" + "\n".join(ruins[:60]) + f"\n({len(ruins)} no total)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
