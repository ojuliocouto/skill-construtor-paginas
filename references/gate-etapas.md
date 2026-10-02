# Evidências das etapas

O `gate-etapas.py` confere sequência, campos obrigatórios, arquivos presentes e SHA-256.
Não verifica sozinho se a copy é boa, se uma aprovação é autêntica ou se a imagem foi lida.
Essas responsabilidades continuam com o usuário e as lentes de auditoria.

Crie uma pasta `evidencias/` dentro do projeto do aluno. Nunca use a pasta da skill para
guardar dados de cliente. Cada etapa recebe um JSON próprio e arquivos de evidência.
Use cópias estáveis dos documentos aprovados: modificar a evidência invalida a etapa.

Exemplo de `evidencias/etapa-0.json`, somente para demonstrar o formato:

```json
{
  "briefing": {
    "nicho": "Informação confirmada no briefing",
    "local": "Informação confirmada no briefing",
    "publico": "Informação confirmada no briefing",
    "oferta": "Informação confirmada no briefing",
    "preco": "Pendente: não publicar preço sem confirmação",
    "acao": "Destino confirmado no briefing"
  },
  "inventario": "Todas as fontes lidas, incluindo abas e linhas; colunas e preenchimento registrados",
  "secoes": ["Seções aprovadas no briefing"],
  "arquivos": ["evidencias/briefing-confirmado.md"]
}
```

Substitua os textos demonstrativos pelos dados efetivamente coletados. Um arquivo fictício
com o formato correto passa na validação estrutural, mas não comprova o trabalho.

Campos do perfil `paginas`, usado somente no fluxo CRIAR:

| Etapa | Campos obrigatórios |
|---|---|
| 0 | `briefing` com seis respostas, `inventario`, `secoes` |
| 1 | `copy`, `aprovacao` |
| 2 | `paleta`, `fontes`, `layouts`, `assets` |
| 3 | `primeiro_bloco`, `movimento` |
| 4 | `claims`, `contato`, `passe_de_gosto`, `entrega`, `pendencias` |
| 5 | `contexto`, `medicao` |

Campos do perfil `dash`:

| Etapa | Campos obrigatórios |
|---|---|
| 1 | `ambiente` |
| 2 | `operacao`, `inventario` |
| 2.5 | `numero_heroi`, `pergunta`, `exclusoes`, `accent`, `densidade`, `tema` |
| 3 | `modo_dados` |
| 4 | `conta_confirmada`, `infra` |
| 5 | `primeiro_render`, `mapeamento` |
| 6 | `prova_publicada`, `passe_de_gosto`, `pendencias` |
| 7 | `contexto` |

Todas as etapas também exigem `arquivos`: lista de arquivos não vazios dentro do projeto.
Para `passe_de_gosto`, use `{"antes": 0, "depois": 0, "inspecao": "Itens efetivamente inspecionados"}`.
A contagem final precisa ser zero. Para campos sem pendência, escreva `"Nenhuma"`.
Para trabalho futuro, como métricas após tráfego, registre o plano e a limitação atual.
Não coloque tokens, senhas ou identificadores de conta em evidências destinadas ao Git.

```bash
python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 0 --arquivo evidencias/etapa-0.json
python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> checar 0
```

No dashboard, acrescente `--perfil dash` e comece pela etapa 1. O gate de ferramentas
continua anterior ao registro. Registrar novamente uma etapa invalida as seguintes.
Antes de entregar, confira a etapa 4 em páginas e a etapa 6 no dashboard.

## Re-registrar a etapa 3 depois da wave é esperado

Toda correção da wave (Step 4) mexe no `index.html`, que é evidência da etapa 3. Na hora de
registrar a etapa 4 o gate responde `BLOQUEIA: Etapa 3: evidência mudou (index.html). Revalide
esta etapa e as seguintes.` Isso é esperado e NÃO quer dizer refazer o Step 3: a página
mudou de propósito, e o gate só pede que o registro aponte a versão nova.

Faça assim, depois da última rodada da wave:

1. Atualize `evidencias/etapa-3.json` se o `primeiro_bloco` ou o `movimento` mudaram na wave.
2. Registre a etapa 3 de novo:
   `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 3 --arquivo evidencias/etapa-3.json`
3. Registre a etapa 4:
   `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 4 --arquivo evidencias/etapa-4.json`

O que NÃO é esperado: evidência das etapas 0, 1 ou 2 mudar depois da wave. Briefing, copy
travada ou direção visual alterados querem dizer que a wave mudou o que já estava aprovado, e
aí o caminho é voltar ao step daquela etapa, não só re-registrar.
