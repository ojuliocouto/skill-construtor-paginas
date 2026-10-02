# Evidências das etapas (caminho CRIAR)

O `gate-etapas.py` confere sequência, campos obrigatórios, arquivos presentes e SHA-256.
Não verifica sozinho se a copy é boa, se uma aprovação é autêntica ou se a imagem foi lida.
Essas responsabilidades continuam com o usuário e com os auditores.

Crie uma pasta `evidencias/` dentro do projeto da página. Nunca use a pasta da skill para
guardar dados de cliente. Cada etapa recebe um JSON próprio e arquivos de evidência. Use
cópias estáveis dos documentos aprovados: modificar a evidência invalida a etapa.

## Campos por etapa (perfil `paginas`)

| Etapa | Passo do CRIAR | Campos obrigatórios |
|---|---|---|
| 0 | a. briefing | `briefing` com seis respostas (`nicho`, `local`, `publico`, `oferta`, `preco`, `acao`), `inventario` (o material real que existe), `pendencias_cliente` |
| 1 | b. referências | `referencias` (caminho do manifesto). O registro roda o `gate-referencias.py` e bloqueia se ele reprovar |
| 2 | c. plano visual | `direcao`, `tipografia`, `paleta`, `imagem`, `ritmo`, `assinatura`, `referencias_usadas` |
| 3 | d. copy | `copy`, `aprovacao` |
| 4 | e. construção | `primeiro_bloco`, `stack`, `imagens` (cada imagem com fonte e licença) |
| 5 | f, g, h. gates, auditores e prova | `gates`, `auditores`, `claims`, `contato`, `passe_de_gosto`, `prova`, `pendencias` |

Todas as etapas também exigem `arquivos`: lista de arquivos não vazios dentro do projeto.
Fato que falta no briefing (preço, número do WhatsApp) entra como `"Pendente: ..."`, nunca
inventado. Para `passe_de_gosto`, use `{"antes": N, "depois": 0, "inspecao": "o que foi olhado"}`:
a contagem final precisa ser zero. Para campos sem pendência, escreva `"Nenhuma"`. Não coloque
tokens, senhas ou identificadores de conta em evidências destinadas ao Git.

Exemplo de `evidencias/etapa-0.json`, só para mostrar o formato:

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
  "inventario": "Fotos reais: nenhuma. Logo: nenhum. Depoimento: nenhum. Contato: pendente",
  "pendencias_cliente": ["Número do WhatsApp", "Fotos do espaço"],
  "arquivos": ["evidencias/briefing.md"]
}
```

```bash
python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 0 --arquivo evidencias/etapa-0.json
python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> checar 0
```

Registrar de novo uma etapa invalida as seguintes. Antes de entregar, confira a etapa 5.
O perfil `dash` continua no script para quem usa a skill de dashboards; ele não muda aqui.

## Re-registrar a etapa 4 depois dos auditores é esperado

Toda correção dos auditores mexe no `index.html`, que é evidência da etapa 4 (construção). Na
hora de registrar a etapa 5 o gate responde `BLOQUEIA: Etapa 4: evidência mudou (index.html).
Revalide esta etapa e as seguintes.` Isso é esperado e NÃO quer dizer refazer a construção: a
página mudou de propósito, e o gate só pede que o registro aponte a versão nova.

Depois da última rodada dos auditores:

1. Atualize `evidencias/etapa-4.json` se o `primeiro_bloco` ou as `imagens` mudaram.
2. `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 4 --arquivo evidencias/etapa-4.json`
3. `python3 <dir-da-skill>/scripts/gate-etapas.py --projeto <dir-do-projeto> registrar 5 --arquivo evidencias/etapa-5.json`

O que NÃO é esperado: evidência das etapas 0 a 3 mudar depois dos auditores. Briefing,
referências, plano visual ou copy alterados querem dizer que a auditoria mudou o que já
estava decidido. Se foi a lente `comparacao-referencias` que reprovou, esse é exatamente o
caso: volte ao plano visual (etapa 2), registre de novo e siga dali.
