"""Provas pela CLI: pular etapa e alterar evidência precisam bloquear."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name('gate-etapas.py')


class Etapas(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = pathlib.Path(self.temp.name)
        (self.pasta / 'briefing.txt').write_text('Documento de controle com informações confirmadas')
        self.doc = {'briefing': dict.fromkeys(['nicho', 'local', 'publico', 'oferta', 'preco', 'acao'], 'Informado'), 'inventario': ['Fonte'], 'pendencias_cliente': ['Número do WhatsApp'], 'arquivos': ['briefing.txt']}

    def rodar(self, *args):
        (self.pasta / 'etapa.json').write_text(json.dumps(self.doc))
        r = subprocess.run([sys.executable, str(SCRIPT), '--projeto', str(self.pasta), *args], capture_output=True, text=True)
        return r.returncode

    def test_positivo_e_releitura(self):
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 0)
        self.assertEqual(self.rodar('checar', '0'), 0)

    def test_nao_pula_copy(self):
        self.assertEqual(self.rodar('registrar', '2', '--arquivo', 'etapa.json'), 1)

    def test_briefing_incompleto_reprova(self):
        del self.doc['briefing']['acao']
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 1)

    def test_artefato_alterado_reprova(self):
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 0)
        (self.pasta / 'briefing.txt').write_text('Conteúdo diferente')
        self.assertEqual(self.rodar('checar', '0'), 1)

    def test_v3_referencias_antes_do_plano_visual(self):
        # v3: a etapa 1 e a pesquisa de referencias, e ela roda o gate-referencias.py.
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 0)
        self.doc = {'referencias': 'referencias/referencias.json', 'arquivos': ['briefing.txt']}
        self.assertEqual(self.rodar('registrar', '1', '--arquivo', 'etapa.json'), 1,
                         'etapa 1 passou sem nenhum print de referencia')
        self.doc = {'direcao': 'x', 'tipografia': 'x', 'paleta': 'x', 'imagem': 'x', 'ritmo': 'x',
                    'assinatura': 'x', 'referencias_usadas': ['x'], 'arquivos': ['briefing.txt']}
        self.assertEqual(self.rodar('registrar', '2', '--arquivo', 'etapa.json'), 1,
                         'plano visual registrado sem a etapa de referencias')

    def test_artefato_ausente_reprova(self):
        self.doc['arquivos'] = ['inexistente.txt']
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 1)

    # Auditoria da v3 (02/10/2026): foto do hero contra o público e promessa fora do briefing.
    # O plano visual passa a registrar público -> foto -> por quê, e a copy, a tabela de sustentação.
    def validar(self, etapa, doc):
        import importlib.util
        spec = importlib.util.spec_from_file_location('ge', SCRIPT)
        ge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ge)
        (self.pasta / 'e.json').write_text(json.dumps(doc))
        try:
            ge.validar(self.pasta.resolve(), (self.pasta / 'e.json').resolve(), etapa, ge.PAGINAS[etapa], 'paginas')
            return 0
        except ValueError:
            return 1

    def test_plano_visual_exige_foto_contra_o_publico(self):
        base = {'direcao': 'x', 'tipografia': 'x', 'paleta': 'x', 'imagem': 'x', 'ritmo': 'x',
                'assinatura': 'x', 'referencias_usadas': ['x'], 'arquivos': ['briefing.txt']}
        self.assertEqual(self.validar('2', base), 1)
        base['foto_publico'] = [{'publico': 'Mulheres de 35 a 60 com dor', 'foto': 'hero.webp'}]
        self.assertEqual(self.validar('2', base), 1, 'sem o porquê')
        base['foto_publico'][0]['porque'] = 'Aluna adulta com a profissional ao lado'
        base['secoes'] = self.SECOES
        self.assertEqual(self.validar('2', base), 0)

    # Auditoria da v4 (02/10/2026): 4 seções seguidas com o mesmo esqueleto e ícone de biblioteca.
    # O plano visual passa a dar a cada seção um tratamento próprio, ligado a uma referência.
    SECOES = [{'secao': 'Situações', 'tratamento': 'grade de caixas com desenho próprio', 'referencia': 'Tia (09)'},
              {'secao': 'Avaliação', 'tratamento': 'faixa cheia com ilustração grande', 'referencia': 'Kins (07)'},
              {'secao': 'Como funciona', 'tratamento': 'linha do tempo', 'referencia': 'Kins (07)'},
              {'secao': 'Dúvidas', 'tratamento': 'lista editorial em coluna centrada', 'referencia': 'Parsley (10)'}]

    def plano(self, **extra):
        base = {'direcao': 'x', 'tipografia': 'x', 'paleta': 'x', 'imagem': 'x', 'ritmo': 'x',
                'assinatura': 'x', 'referencias_usadas': ['x'], 'arquivos': ['briefing.txt'],
                'foto_publico': [{'publico': 'Mulheres de 35 a 60', 'foto': 'sala.webp', 'porque': 'Sem pessoa identificável'}],
                'secoes': [dict(s) for s in self.SECOES]}
        base.update(extra)
        return base

    def test_plano_visual_exige_tratamento_por_secao(self):
        b = self.plano(); del b['secoes']
        self.assertEqual(self.validar('2', b), 1, 'sem secoes')
        b = self.plano(); b['secoes'][1]['referencia'] = ''
        self.assertEqual(self.validar('2', b), 1, 'tratamento sem referência')

    def test_plano_visual_reprova_tres_secoes_seguidas_com_o_mesmo_tratamento(self):
        b = self.plano()
        for s in b['secoes'][:3]:
            s['tratamento'] = 'Título à esquerda + grade de caixas'
        self.assertEqual(self.validar('2', b), 1)
        b['secoes'][2]['tratamento'] = 'linha do tempo'
        self.assertEqual(self.validar('2', b), 0, 'duas seguidas iguais é o limite')

    def test_plano_visual_reprova_icone_de_biblioteca(self):
        b = self.plano(icones=[{'secao': 'Como funciona', 'desenha': 'balão de conversa com três pontos'}])
        self.assertEqual(self.validar('2', b), 1)
        b['icones'][0]['desenha'] = 'calendário com check'
        self.assertEqual(self.validar('2', b), 1)
        b['icones'][0]['desenha'] = 'planta baixa de uma sala com quatro aparelhos'
        self.assertEqual(self.validar('2', b), 0)

    def test_copy_exige_tabela_de_sustentacao(self):
        base = {'copy': 'copy.md', 'aprovacao': 'x', 'arquivos': ['briefing.txt']}
        self.assertEqual(self.validar('3', base), 1)
        base['sustentacao'] = 'evidencias/sustentacao.md'
        self.assertEqual(self.validar('3', base), 1, 'arquivo de sustentação inexistente')
        (self.pasta / 'evidencias').mkdir()
        (self.pasta / 'evidencias' / 'sustentacao.md').write_text('| Frase da página | Linha |\n|---|---|\n| A | "b" |\n')
        self.assertEqual(self.validar('3', base), 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
