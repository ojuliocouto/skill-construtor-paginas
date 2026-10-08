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
        (self.pasta / 'briefing.txt').write_text('Documento de controle com informações confirmadas', encoding="utf-8")
        self.doc = {'briefing': dict.fromkeys(['nicho', 'local', 'publico', 'oferta', 'preco', 'acao'], 'Informado'), 'inventario': ['Fonte'], 'pendencias_cliente': ['Número do WhatsApp'], 'arquivos': ['briefing.txt']}

    def rodar(self, *args):
        (self.pasta / 'etapa.json').write_text(json.dumps(self.doc), encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), '--projeto', str(self.pasta), *args], capture_output=True, text=True, encoding="utf-8")
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
        (self.pasta / 'briefing.txt').write_text('Conteúdo diferente', encoding="utf-8")
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

    def test_evidencia_mudada_diz_o_que_refazer_na_ordem(self):
        # A22 (segunda leva): a mensagem lista, na ordem, o registro das etapas afetadas, com o caminho completo.
        import io, contextlib
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 0)
        (self.pasta / 'briefing.txt').write_text('mudou', encoding="utf-8")
        r = subprocess.run([sys.executable, str(SCRIPT), '--projeto', str(self.pasta), 'checar', '0'], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn('briefing.txt', r.stdout)
        self.assertRegex(r.stdout, r'refaça, nesta ordem')
        self.assertRegex(r.stdout, r'gate-etapas\.py.* registrar 0 --arquivo etapa\.json')
        self.assertIn('/scripts/py.mjs', r.stdout.replace('\\', '/'))

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
        (self.pasta / 'e.json').write_text(json.dumps(doc), encoding="utf-8")
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

    # v3.5.6 (achado A8): a linha "Ícone do site: <motivo>" é cobrada quando o plano visual é
    # registrado, não só no passo e.4, quando o aluno já construiu a página.
    def test_plano_visual_sem_linha_do_icone_do_site_reprova(self):
        (self.pasta / 'plano-visual.md').write_text('# Plano visual\n\nDireção: oficina.\n', encoding='utf-8')
        self.assertEqual(self.validar('2', self.plano()), 1)
        (self.pasta / 'plano-visual.md').write_text('# Plano visual\n\nÍcone do site: <motivo>\n', encoding='utf-8')
        self.assertEqual(self.validar('2', self.plano()), 1, 'modelo não preenchido')
        (self.pasta / 'plano-visual.md').write_text('# Plano visual\n\nÍcone do site: encaixe de duas peças de madeira\n', encoding='utf-8')
        self.assertEqual(self.validar('2', self.plano()), 0)

    def test_plano_visual_reprova_icone_de_biblioteca(self):
        b = self.plano(icones=[{'secao': 'Como funciona', 'desenha': 'balão de conversa com três pontos'}])
        self.assertEqual(self.validar('2', b), 1)
        b['icones'][0]['desenha'] = 'calendário com check'
        self.assertEqual(self.validar('2', b), 1)
        b['icones'][0]['desenha'] = 'aparelho de pilates visto de lado'
        self.assertEqual(self.validar('2', b), 0, '"visto de lado" não é o sinal de visto')
        b['icones'][0]['desenha'] = 'planta baixa de uma sala com quatro aparelhos'
        self.assertEqual(self.validar('2', b), 0)

    def test_copy_exige_tabela_de_sustentacao(self):
        base = {'copy': 'copy.md', 'aprovacao': 'x', 'arquivos': ['briefing.txt']}
        self.assertEqual(self.validar('3', base), 1)
        base['sustentacao'] = 'evidencias/sustentacao.md'
        self.assertEqual(self.validar('3', base), 1, 'arquivo de sustentação inexistente')
        (self.pasta / 'evidencias').mkdir()
        (self.pasta / 'evidencias' / 'sustentacao.md').write_text('| Frase da página | Linha |\n|---|---|\n| A | "b" |\n', encoding="utf-8")
        self.assertEqual(self.validar('3', base), 0)


    # Fatia C (06/10/2026): a prova de entrega leva o VÍDEO da rolagem junto dos prints.
    def etapa5(self, **extra):
        base = {'gates': 'g', 'auditores': 'a', 'claims': 'c', 'contato': 'x', 'prova': 'prints lidos',
                'pendencias': ['nenhuma'], 'passe_de_gosto': {'antes': 2, 'depois': 0, 'inspecao': 'percorri a página'},
                'arquivos': ['briefing.txt']}
        base.update(extra)
        return base

    def webm(self, nome, conteudo=None):
        (self.pasta / 'videos').mkdir(exist_ok=True)
        (self.pasta / 'videos' / nome).write_bytes(conteudo if conteudo is not None else bytes.fromhex('1a45dfa3') + b'\x00' * 64)
        return 'videos/' + nome

    def test_etapa_5_sem_video_nao_registra(self):
        self.assertEqual(self.validar('5', self.etapa5()), 1)

    def test_etapa_5_exige_video_de_desktop_e_de_celular_que_existam(self):
        d, m = self.webm('video-desktop.webm'), self.webm('video-mobile.webm')
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d})), 1, 'falta o celular')
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d, 'mobile': 'videos/nao-existe.webm'})), 1)
        self.assertEqual(self.validar('5', self.etapa5(video='videos/x.webm')), 1, 'precisa ser {desktop, mobile}')
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d, 'mobile': m})), 0)

    def test_etapa_5_recusa_video_vazio_ou_que_nao_e_webm(self):
        d = self.webm('video-desktop.webm')
        vazio = self.webm('vazio.webm', b'')
        lixo = self.webm('lixo.webm', b'isto nao e um video de verdade, so texto')
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d, 'mobile': vazio})), 1)
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d, 'mobile': lixo})), 1)

    # A31 (b): o registro da etapa 5 lê o desfecho do ciclo do wave.py
    def wave(self, desfecho, ressalvas=None):
        (self.pasta / '.wave-auditoria.json').write_text(json.dumps({'rodadas': [
            {'n': 1, 'desfecho': 'CONTINUA'}, {'n': 2, 'desfecho': desfecho, 'ressalvas': ressalvas or []}]}), encoding='utf-8')

    def etapa5_ok(self):
        d, m = self.webm('video-desktop.webm'), self.webm('video-mobile.webm')
        return self.etapa5(video={'desktop': d, 'mobile': m})

    def test_etapa_5_recusa_quando_o_ciclo_terminou_em_nao_entregar(self):
        self.wave('NAO_ENTREGAR')
        self.assertEqual(self.validar('5', self.etapa5_ok()), 1)

    def test_etapa_5_recusa_ciclo_que_ainda_continua_ou_com_auditoria_pendente(self):
        for d in ('CONTINUA', 'AUDITORIA_PENDENTE'):
            self.wave(d)
            self.assertEqual(self.validar('5', self.etapa5_ok()), 1, d)

    def test_etapa_5_aceita_entrega_e_sem_registro_do_wave(self):
        self.wave('ENTREGA')
        self.assertEqual(self.validar('5', self.etapa5_ok()), 0)
        (self.pasta / '.wave-auditoria.json').write_text('{}', encoding='utf-8')
        self.assertEqual(self.validar('5', self.etapa5_ok()), 0, 'sem rodadas registradas: o resto do gate segue valendo')

    def test_etapa_5_com_ressalvas_registra_e_grava_as_ressalvas_na_evidencia(self):
        for e in ('0', '1', '2', '3', '4'):
            self.registrar_fake(e)
        self.wave('ENTREGA_COM_RESSALVAS', ['lente comparacao-referencias reprovada: eixos tipografia, imagem', '3 altos abertos'])
        self.doc = self.etapa5_ok()
        self.assertEqual(self.rodar('registrar', '5', '--arquivo', 'etapa.json'), 0)
        reg = json.loads((self.pasta / '.etapas-verificadas.json').read_text(encoding='utf-8'))
        self.assertEqual(reg['5']['ressalvas'], ['lente comparacao-referencias reprovada: eixos tipografia, imagem', '3 altos abertos'])
        self.assertEqual(self.rodar('checar', '5'), 0)

    def test_etapa_5_video_fora_do_projeto_e_recusado(self):
        d = self.webm('video-desktop.webm')
        self.assertEqual(self.validar('5', self.etapa5(video={'desktop': d, 'mobile': '../fora.webm'})), 1)

    def test_etapa_5_o_video_entra_na_integridade(self):
        for e in ('0', '1', '2', '3', '4'):
            self.registrar_fake(e)
        d, m = self.webm('video-desktop.webm'), self.webm('video-mobile.webm')
        self.doc = self.etapa5(video={'desktop': d, 'mobile': m})
        self.assertEqual(self.rodar('registrar', '5', '--arquivo', 'etapa.json'), 0)
        self.assertEqual(self.rodar('checar', '5'), 0)
        (self.pasta / m).write_bytes(bytes.fromhex('1a45dfa3') + b'\x01' * 64)
        self.assertEqual(self.rodar('checar', '5'), 1, 'trocar o vídeo depois de registrar invalida a etapa')

    # A32: mudança de briefing no meio do trabalho, com o caminho curto `revalidar --motivo`
    def montar_0_e_3(self):
        """Etapa 0 registrada pelo CLI e a 3 (copy) registrada com o validar real; o briefing é evidência das duas."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('ge2', SCRIPT)
        ge = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ge)
        self.ge = ge
        self.assertEqual(self.rodar('registrar', '0', '--arquivo', 'etapa.json'), 0)
        (self.pasta / 'sustentacao.md').write_text('| Frase | Linha |\n|---|---|\n| a | "x" |\n', encoding='utf-8')
        doc3 = {'copy': 'copy.md', 'aprovacao': 'x', 'sustentacao': 'sustentacao.md', 'arquivos': ['briefing.txt', 'sustentacao.md']}
        (self.pasta / 'etapa-3.json').write_text(json.dumps(doc3), encoding='utf-8')
        h = ge.validar(self.pasta.resolve(), (self.pasta / 'etapa-3.json').resolve(), '3', ge.PAGINAS['3'], 'paginas')
        h['etapa-3.json'] = ge.digest(self.pasta / 'etapa-3.json')
        reg = json.loads((self.pasta / '.etapas-verificadas.json').read_text(encoding='utf-8'))
        reg['3'] = {'hashes': h}
        (self.pasta / '.etapas-verificadas.json').write_text(json.dumps(reg), encoding='utf-8')

    def revalidar(self, motivo='o cliente trocou o preço e o prazo da oferta'):
        args = [sys.executable, str(SCRIPT), '--projeto', str(self.pasta), 'revalidar']
        if motivo is not None:
            args += ['--motivo', motivo]
        r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        return r.returncode, r.stdout + r.stderr

    def test_revalidar_so_o_briefing_mudou_revalida_em_ordem_e_grava_o_motivo(self):
        self.montar_0_e_3()
        (self.pasta / 'briefing.txt').write_text('Documento de controle: o cliente trocou o preço', encoding='utf-8')
        self.assertEqual(self.rodar('checar', '0'), 1, 'antes: a mudança derruba a etapa 0')
        code, out = self.revalidar()
        self.assertEqual(code, 0, out)
        self.assertIn('etapa 0', out.lower())
        self.assertIn('etapa 3', out.lower())
        self.assertIn('revalidada', out)
        reg = json.loads((self.pasta / '.etapas-verificadas.json').read_text(encoding='utf-8'))
        self.assertEqual(set(reg), {'0', '3'}, 'não perde as etapas seguintes')
        self.assertIn('o cliente trocou o preço', reg['0']['revalidada']['motivo'])
        self.assertIn('o cliente trocou o preço', reg['3']['revalidada']['motivo'])
        self.assertEqual(self.rodar('checar', '0'), 0)

    def test_revalidar_nao_e_atalho_outra_evidencia_mudou_e_a_etapa_continua_exigindo_o_gate(self):
        self.montar_0_e_3()
        (self.pasta / 'briefing.txt').write_text('briefing novo do cliente com outro preço', encoding='utf-8')
        (self.pasta / 'sustentacao.md').write_text('| Frase | Linha |\n|---|---|\n| b | "y" |\n', encoding='utf-8')
        antes = (self.pasta / '.etapas-verificadas.json').read_text(encoding='utf-8')
        code, out = self.revalidar()
        self.assertEqual(code, 1, out)
        self.assertIn('sustentacao.md', out)
        self.assertRegex(out, r'registrar 3')
        self.assertEqual((self.pasta / '.etapas-verificadas.json').read_text(encoding='utf-8'), antes, 'nada foi gravado quando bloqueia')

    def test_revalidar_json_da_etapa_mudado_tambem_bloqueia(self):
        self.montar_0_e_3()
        (self.pasta / 'briefing.txt').write_text('briefing novo', encoding='utf-8')
        d = json.loads((self.pasta / 'etapa-3.json').read_text(encoding='utf-8'))
        d['aprovacao'] = 'outra'
        (self.pasta / 'etapa-3.json').write_text(json.dumps(d), encoding='utf-8')
        code, out = self.revalidar()
        self.assertEqual(code, 1, out)
        self.assertIn('etapa-3.json', out)

    def test_revalidar_exige_motivo_de_verdade(self):
        self.montar_0_e_3()
        (self.pasta / 'briefing.txt').write_text('briefing novo', encoding='utf-8')
        self.assertEqual(self.revalidar(motivo=None)[0], 2)
        self.assertEqual(self.revalidar(motivo='mudou')[0], 2)

    def test_revalidar_sem_nada_mudado_diz_que_nao_ha_o_que_revalidar(self):
        self.montar_0_e_3()
        code, out = self.revalidar()
        self.assertEqual(code, 0)
        self.assertIn('nada mudou', out.lower())

    def registrar_fake(self, etapa):
        """Grava direto no registro as etapas anteriores, só para testar a 5 em sequência."""
        import hashlib
        alvo = self.pasta / '.etapas-verificadas.json'
        reg = json.loads(alvo.read_text(encoding="utf-8")) if alvo.exists() else {}
        reg[etapa] = {'hashes': {'briefing.txt': hashlib.sha256((self.pasta / 'briefing.txt').read_bytes()).hexdigest()}}
        alvo.write_text(json.dumps(reg), encoding="utf-8")


if __name__ == '__main__':
    unittest.main(verbosity=2)
