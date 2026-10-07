# Anti-Vibe-Coding: Checklist de Sinais de Construção Sem Qualidade

Checklist final pra garantir que a página não tenha "cara de vibe-coding" (site bonito por fora,
quebrado por dentro). A lente design-critic dos auditores (`references/auditores.md`) usa esta lista.

Base: dissecação frame a frame do reel de Patrick Minardi (@patrickwithprospectflo) "how to spot a
vibe-coded website", analisando o que ele **aponta na tela** (SaaS "LaunchLand"), não só o que fala.

Complementa `references/preferencias-de-design.md` (gosto medido em correção real). Aqui o foco é
**funcionalidade e substância**, e depois **aparência** (os tells V1 a V17).

---

## Os 5 sinais de vibe-coding

| # | Sinal | Como detectar | Correção |
|---|-------|---------------|----------|
| 1 | **Badge/selo decorativo** | Selo "● online", "● live feed", "X verified" pulsante no hero sem dado real por trás. Enfeite que a IA cospe por padrão. | Remover, OU plugar dado real (contador que atualiza de verdade, status que reflete um sistema). |
| 2 | **Fade genérico em bloco** | O MESMO fade/slide aplicado a tudo: tudo entra junto, ou tudo com a mesma animação sem ligação com o conteúdo. Cansa e atrasa. Muitos itens revelados NÃO é o defeito: a v7 aprovada revela 24, cada um quando ELE entra na tela. | Gramática de base única (uma curva, uma escala de duração) com cada item entrando quando chega na tela, MAIS momentos próprios ligados ao conteúdo (`references/receitas-de-movimento.md`). |
| 3 | **Footer sem páginas legais** | Rodapé vazio: sem Termos de Uso, sem Política de Privacidade, sem contato/identificação. (Tell clássico: tem "Privacy" no meio do texto mas rodapé pelado.) | Footer com links reais para Termos e Privacidade + contato (e-mail, CNPJ ou responsável). |
| 4 | **CTA/checkout que não dispara** | Botão de compra/"comece agora"/"assine" que ao clicar não faz nada. Placeholder esquecido. | Plugar o destino real (checkout, link de pagamento, form) e **testar por clique**. |
| 5 | **Casca animada sobre produto quebrado** | Hero com partículas/aurora/gradiente animado lindo, mas a página é só fachada (links mortos, seções vazias, funcionalidade ausente). | Substância antes de casca: garantir que a página funciona inteira ANTES de polir o visual. |

---

## Teste de substância > casca

Pra cada efeito visual chamativo (partículas, aurora, glow, scroll mágico), perguntar:

> "Se esse efeito sumir, a página continua funcional, completa e confiável?"

- **Sim** → o efeito é tempero, ok.
- **Não** (a página é só casca) → FALHA. Resolver funcionalidade primeiro.

---

## Veredito

Itens **3 (footer legal)** e **4 (checkout funcional)** são **não-negociáveis**: qualquer FALHA
neles **bloqueia a entrega**. São os dois maiores tells de vibe-coding e os que mais derrubam
confiança/conversão.

Itens **1, 2 e 5** são **YELLOW**: corrigir se presentes, mas não bloqueiam sozinhos.

```
3 e 4 OK  → pode entregar (corrigir YELLOWs se houver)
3 ou 4 FALHA → NÃO entregar até resolver
```

### Limiar de bloqueio dos tells VISUAIS (V1-V17)

Os tells visuais abaixo (V1 a V17) não bloqueavam sozinhos. Agora bloqueiam por acúmulo:

```
0-2 tells visuais presentes → YELLOW (corrigir, mas não bloqueia)
3+ tells visuais presentes  → CRÍTICO. NÃO entregar. "Cara de IA" acumulada = reprovação.
```

Tells universais (valem em qualquer nicho, contam sempre): V4 (glow blob), V9 (glow difuso
no hover do botão), gradient-clip no título principal, paleta indigo+roxo sobre dark, ícones
idênticos em quadrado-gradiente. Tells calibrados pra e-commerce/clone de loja (V1 kicker mono,
V2/V6 numero/stats no hero): pesam menos numa landing de SaaS, onde a estética e nativa do gênero.
Usar julgamento: o teste e "um cliente bate o olho e diz cara de IA?", não um checkbox cego.

---

## Tells VISUAIS de IA / template genérico (checklist de aparência)

- **Badge-pill de status acima do H1** (check + uppercase espaçado + verde-neon fora da paleta, tipo "INSCRIÇÃO CONFIRMADA"): kit padrão de gerador. Pior quando REPETE informação que a página já dá (stepper com check, hero com "Parabéns"). Feedback real de cliente numa página VIP (10/08/2026): "puta cara de ia isso". Antes de criar badge, conferir se a informação já existe na hierarquia; se precisar de rótulo, usar o padrão visual que a página já tem.

Os 5 sinais acima são sobre **substância**. Esta lista é sobre **aparência**: padrões que fazem o
cliente bater o olho e dizer "cara de IA / vibecoding / template". Validada num clone real (jun/2026),
onde o cliente apontou cada um destes em prints. A lente design-critic conta estes tells.

| # | Tell visual | Por que delata | Correção |
|---|-------------|----------------|----------|
| V1 | **Micro-label uppercase em fonte mono (Space Grotesk) com quadradinho/barra** como kicker de seção ("NOVA COLEÇÃO", "ESCOLHA SEU TERRENO") | Assinatura nº 1 de landing de SaaS/startup gerada. Varejo real não rotula seção assim. | Tirar o kicker. Título forte direto + link "Ver todos". Mono só em tag minúscula funcional (preço, selo). |
| V2 | **Número gigante decorativo** ("01", "02", ou um "4" solto em card) atrás/ao lado de elementos | Vocabulário de "hero de agência" | Remover. Numeração não agrega. **Gate executável:** `scripts/gate-sem-kicker.py` reprova número sozinho com fonte >= 48px e a sequência 01/02/03. |
| V3 | **Palavra gigante de contorno** (`text-stroke`) atrás do conteúdo | Tell de template/portfólio Dribbble | Remover. Se quiser textura, usar marquee de marcas ou pattern sutil. |
| V4 | **Blob de glow radial desfocado** (`blur-[100px]` rounded-full) atrás do produto | Estética SaaS/IA, "aura" | Remover. Profundidade vem de sombra real no produto. |
| V5 | **Speed streaks / raios animados** decorativos | Clichê "esportivo gerado por prompt" | Remover. Energia vem de cor + composição diagonal, não de raios. |
| V6 | **Bloco de "stats"** no hero (número Anton gigante + label) | Padrão de landing SaaS, não de loja | Remover. Prova vai na trust strip / estrelas no card. |
| V7 | **Preço / dado em fonte mono** | Loja real escreve preço na fonte do corpo, bold | `font-mono` → `font-body` bold. |
| V8 | **Dica "ENTER" / atalho de teclado** no campo de busca | Padrão de ferramenta dev (Linear/Vercel) | Remover. Botão de lupa colorido à direita (padrão Netshoes/Centauro). |
| V9 | **Glow colorido difuso no hover do botão** (`box-shadow: 0 10px 30px rgba(cor,.35)` + levitar) | Assinatura de botão "Tailwind template" | Mudar só o tom no hover (`bg-*-dark`). Sombra neutra discreta ou nenhuma. |
| V10 | **Mistura PT/EN incoerente** ("Mais vendidos" + "Best sellers" na mesma página) | Conteúdo autogerado a partir de prompt | Padronizar 100% PT-BR. |
| V11 | **Copy monotemática "marketês"** (tudo girando numa metáfora: "ritmo/pista/bora correr") | Tema gerado de um único prompt | Aterrissar no varejo real ("frete grátis e até 10x", "as marcas que você ama"). |
| V12 | **Hover com rotação exagerada** na foto do produto (`-rotate-3` + scale-110) | Efeito de showcase, atrapalha avaliar o produto | Zoom sutil `scale-105`, sem rotação. |
| V13 | **Separador decorativo de ícone** (raio/bolt) entre itens de marquee | Enfeite que a IA cospe | Ponto (•), barra, ou só espaçamento. |
| V14 | **Seção com clip diagonal + gradiente** repetida com tratamentos diferentes | Estética de template; incoerência de marca | Padronizar (cor chapada). Variar superfícies por cor (claro/escuro), não por efeito. |
| V15 | **Logo minúscula** (<56px desktop) | Faz a marca parecer "perdida"/genérica | Logo proeminente: mín 56-64px desktop, 40-48px mobile. Ao clonar, baixar o logo REAL do site. |
| V16 | **"Jornal de filetes"**: muitos filetes finos de 1 px (cabeçalho, seção, item, card), serifa com UMA palavra em itálico colorida repetida em vários títulos e fundo de grade decorativo | Medido na auditoria de 02/10/2026: 14 filetes, itálico colorido em 3 de 7 títulos e grade no fecho. Serifa + filete + muito branco é o terceiro visual padrão de IA, depois do creme com terracota e do quase preto com acento ácido | No máximo um trecho em itálico colorido na página (`gate-texto.mjs` reprova o segundo); separar por cor de superfície e espaço, não por fio; nada de grade de fundo como enfeite. `gate-texto.mjs` avisa a partir de 10 filetes |
| V17 | **Esqueleto repetido**: o mesmo h2 à esquerda com uma grade de caixas embaixo em seção após seção, e ícone de biblioteca (balão de conversa, calendário com check, boneco de palito) | Medido na auditoria da v4 (02/10/2026): 4 seções seguidas com a mesma composição, 14 caixas na página, 2 ícones de biblioteca e o mesmo par de bonecos em duas seções. As referências fortes dão a cada seção uma composição própria | Cada seção com um tratamento próprio tirado de uma referência (lista editorial, linha do tempo, split com imagem, faixa cheia) e registrado em `secoes` na etapa 2; desenho feito para o assunto, com `data-desenho`. `gate-composicao.mjs` reprova mais de 2 seções seguidas com o mesmo esqueleto e ícone genérico |

**Regra-mãe destes tells:** quando o brief é *clonar e melhorar* uma loja real, a referência de
"bonito" é o concorrente do nicho (Netshoes, Centauro, Nike.com.br, Dafiti), **não** o Dribbble/landing
de SaaS. Se um elemento existiria num pitch de startup mas não numa loja de calçado de verdade, é tell.

**Como caçar:** despachar 1 agente "AI-slop hunter" (lê componentes + screenshot, lista tells com
correção) em paralelo com 1 agente "o que falta inserir". Padrão validado, pega o que o olho cansado
deixa passar.
