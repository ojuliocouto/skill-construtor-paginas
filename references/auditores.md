# Auditores adversariais (passo g do CRIAR)

A auditoria nunca é feita pelo mesmo olhar que construiu: quem construiu não enxerga o
próprio erro. Por isso a página passa por **9 lentes independentes**, as mesmas do
`scripts/wave.py` (dicionário `LENTES`): design-critic, assets-auditor, visual-auditor,
motion-auditor, responsive-auditor, cro-auditor, a11y-auditor, content-auditor e
comparacao-referencias. Quem decide se entrega é o ciclo (`wave.py rodada`), não a nota.

## Como rodar

1. A página servida com compressão (`scripts/servidor-gzip.py`) e os gates do passo f verdes.
2. **Quando o ambiente permite subagentes (o padrão):** a rodada roda com subagente auditor
   independente (o tipo `auditor`, ou um subagente comum com mandato de refutar), uma lente por
   subagente ou um auditor para as nove, recebendo só a URL, a `dist/`, o briefing, a tabela
   de sustentação, a pasta `referencias/` e as preferências, sem o histórico da construção.
   Com a tool `Workflow`, uma chamada `parallel`; com `Agent`/`Task`, um subagente por lente.
   Registro com `--origem subagente`.
3. **Quando não permite** (sem subagente, pedido de agente único): a MESMA checagem roda em
   sequência, uma lente por vez, para achar e corrigir defeito. Ela é autoavaliação, e **nota de
   autoavaliação não libera entrega**: o registro leva `--origem autoavaliacao` e o `wave.py rodada` responde
   AUDITORIA INDEPENDENTE PENDENTE até a rodada independente acontecer em outra sessão, sem o
   histórico (`--origem sessao-independente`), ou com outra pessoa (`--origem pessoa`). Custo
   medido de confiar na autoavaliação (02/10/2026): média 7,78 e "tells 0" contra 5,5 e cinco
   achados graves do auditor independente, na mesma página.
4. Cada lente devolve o schema abaixo e se registra:
   `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> registrar <lente> --veredito <aprovado|reprovado> --nota <0-10> --origem <subagente|sessao-independente|pessoa|autoavaliacao> --achados "<o que olhou, o que mediu, o que achou>"`
5. Master: `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> checar` (todas as lentes e
   todos os gates registrados).
6. Ciclo: `python3 <dir-da-skill>/scripts/wave.py --projeto <dir> rodada --criticos <N> --altos <N> --pendencias-do-usuario <N> --regressoes <N>`.
   Saiu CONTINUA: corrija, refaça os gates que a correção toca, rode de novo as lentes que
   tinham achado, feche outra rodada.

## Schema de retorno (toda lente)

```json
{
  "lente": "string",
  "aprovado": true,
  "score": 8.5,
  "achados": [
    { "item": "string", "severidade": "critico|alto|medio|baixo", "evidencia": "string", "fix": "string" }
  ]
}
```

- **Evidência é obrigatória e verificável:** print, medida (px, contraste, alvo de toque),
  trecho de código com linha ou passo de reprodução. Achado sem evidência é descartado.
- **Fix nunca viola a regra da skill:** proibido sugerir depoimento inventado, urgência falsa,
  dado fora do briefing ou um tell de `references/anti-vibe-coding.md` como melhoria.
- **Crítico** quebra uso, mente para o visitante ou expõe o cliente. **Alto** que só some com
  dado que apenas o cliente tem (número do WhatsApp, foto do espaço, credencial) entra em
  `--pendencias-do-usuario` e vai declarado na entrega.

## A régua do ciclo (`wave.py rodada`)

1. Zero crítico confirmado. Inegociável.
2. Nenhuma regressão (achado causado pela correção da rodada anterior).
3. A lente `comparacao-referencias` não pode estar reprovada: se estiver, o ciclo manda voltar
   ao plano visual (passo c), com qualquer nota nas outras.
4. Depois disso, fecha quando a gravidade secou (zero crítico e zero alto), ou a média chegou a
   8,0 com nenhuma lente abaixo de 7, ou duas rodadas seguidas subiram menos de 0,3, ou bateu o
   teto de 4 rodadas. A nota real vai escrita na entrega, sempre.

Compare ACHADOS entre rodadas, nunca notas: cada rodada é um olhar novo e a nota não é medida
calibrada. Nota que cai pode ser régua mais fina, não página pior.

## As 9 lentes

### 1. design-critic (cara de IA, gosto)
Lê a página inteira no print e em recortes 1:1. Conta os tells de
`references/anti-vibe-coding.md` (V1 a V17, o V16 é o "jornal de filetes" e o V17 o esqueleto repetido) e as proibições de
`references/preferencias-de-design.md`, item por item (inclusive itens paralelos em caixas
iguais, passos em grade, FAQ e fecho com movimento, legenda que explica o design). Aplica a autocrítica da `frontend-design`: alguma
parte do plano virou o padrão que sairia para qualquer página parecida? Os três visuais
padrão de IA (creme com serifa e terracota; quase preto com um acento ácido; "jornal de
filetes", com fios finos, itálico colorido repetido e grade de fundo) só valem se o briefing pediu.
**Reprova (crítico) se:** 3 ou mais tells presentes, footer sem identificação, ou botão que
não leva a lugar nenhum.

### 2. assets-auditor (imagem real)
A página não pode ser só texto, gradiente e ícone. Confere cada imagem: de onde veio, qual a
licença (está em `imagens/LICENCAS.md`?), se casa com o título ao lado, se o recorte na JANELA
(não no arquivo) mostra o que importa, se há legenda de imagem ilustrativa quando a foto não é
do cliente, colada na foto. Confere a tabela público -> foto -> por quê do plano visual
contra a foto aberta (idade, perfil, roupa), procura logo de terceiro num recorte ampliado 4x
e confirma que nenhum elemento gráfico atravessa rosto ou corpo de pessoa.
**Reprova (crítico) se:** nenhuma imagem real, foto que contradiz o público, logo de terceiro
legível na cena, linha ou forma por cima de pessoa, imagem sem licença registrada, foto que sugere
ser do cliente (o espaço, a profissional) sem ser, ou logo indicado pelo cliente trocado por
invenção.

### 3. visual-auditor (hierarquia, grid, enquadramento)
Hierarquia tipográfica, coerência de paleta com o plano visual, espaçamento, grid de desktop,
ritmo entre seções. Imagem com `loading="lazy"` precisa ter carregado antes do julgamento
(role até ela e espere `complete && naturalWidth > 0`).
**Reprova (crítico) se:** hero só com texto centralizado quando o plano pedia imagem, cor ou
fonte fora do plano visual, crop que corta rosto ou objeto principal.

### 4. motion-auditor (movimento)
Entrada do hero, 2 a 4 revelações nas seções-chave (nunca em todo elemento), hover e
microinteração no botão, `prefers-reduced-motion` respeitado. Movimento que nunca termina (fica
em opacity 0 se o observer falhar) é crítico.
**Reprova (crítico) se:** conteúdo que pode ficar invisível, animação sem respeitar
reduced-motion.

### 5. responsive-auditor (12 telas)
Roda `scripts/gate-responsivo.mjs` e olha os prints do celular em recortes 1:1.
**Reprova (crítico) se:** rolagem lateral, botão principal fora da dobra, alvo de toque abaixo
de 44px, corpo abaixo de 14px, texto cortado.

### 6. cro-auditor (conversão)
Uma ação clara, repetida nos pontos certos, com o destino real; headline que diz para quem e o
que resolve; objeções respondidas na página; mensagem coerente com a origem do tráfego.
**Reprova (crítico) se:** botão sem destino, formulário que mostra sucesso sem enviar, ação
principal ambígua.

### 7. a11y-auditor (acessibilidade)
Foco visível, label, alt que descreve a foto de verdade (olhando a foto), ARIA, contraste
4.5:1 medido no pixel, zero emoji, link "pular para o conteúdo" funcionando.
**Reprova (crítico) se:** contraste abaixo de 4.5:1 em texto de corpo, imagem de conteúdo sem
alt, controle sem nome acessível.

### 8. content-auditor (verdade)
Diff de claims: toda afirmação da página (texto, foto, alt, JSON-LD, title, meta description,
og:description, comentário que afirma comportamento) contra o briefing, pela tabela
`evidencias/sustentacao.md` e pelo `gate-verdade.py`. Lê também o que a frase INSINUA: "você
chega, faz a avaliação e começa" afirma mesmo dia sem dizer "mesmo dia". Sweep de travessão (U+2014 e U+2013 = 0). Telefone e
WhatsApp dígito por dígito em todo `tel:` e `wa.me`.
**Reprova (crítico) se:** dado, depoimento, número, preço ou credencial que não está na fonte;
travessão; contato divergente.

### 9. comparacao-referencias (está no nível das referências?)
A lente que a v3 criou. Pega as 2 ou 3 referências mais fortes de `referencias/sintese.md` e
põe cada uma ao lado da página, na mesma escala:

```bash
python3 <dir-da-skill>/scripts/lado-a-lado.py <dir>/referencias/<ref>-dobra.png <print-da-pagina-dobra.png> <dir>/referencias/comparativo-1.jpg --rotulos "Referência,Nossa página"
```

Olhe a imagem e responda por escrito, eixo por eixo (composição, tipografia, imagem, ritmo,
acabamento): **no nível** ou **abaixo**, com o porquê. Depois a pergunta que decide: **um
designer exigente colocaria esta página na mesma pasta das referências?**
**Reprova se:** a resposta honesta é não, ou se dois ou mais eixos ficaram abaixo. Reprovada,
não se corrige na lente: volta ao plano visual (passo c), com o que faltou escrito. No caminho
CLONAR a referência é a página original. Esta lente não aceita "não aplicável".

## Passe de gosto (último ato antes da entrega)

Apontar o defeito não é remover o defeito. Depois do ciclo, passe a página inteira com
mandato de CORRIGIR: ícone genérico em caixinha, uniformidade excessiva (todo card igual, toda
seção centralizada), os tells de `references/anti-vibe-coding.md`. Prova: tells antes e
depois, e o depois tem que ser 0, mais a lista do que foi inspecionado.
