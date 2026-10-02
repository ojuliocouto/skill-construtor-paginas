# Taste Gate: Checklist de Qualidade Final

Extraído de: **taste** (scoring rubric + design-taste) + **impeccable** (AI slop test).
Rodar antes de entregar qualquer página. Score < 4 = revisar antes de entregar.

---

## Como usar

1. Percorrer cada item do checklist
2. Atribuir score 1-5 na dimensão Design
3. Se score ≤ 3: identificar o gap de maior impacto e corrigir
4. Para refinamento profundo: invocar `npx impeccable polish` ou `npx impeccable critique`

---

## Dimensão Design: Score 1-5

### Hierarquia Visual
- [ ] Cada tela tem um elemento dominante claro (headline, CTA ou métrica)
- [ ] Conteúdo secundário recua visualmente (menor, mais leve, mais suave)
- [ ] No máximo 3 níveis de hierarquia por tela
- [ ] Ao fazer squint na tela (olhar de longe): dá pra identificar o que é mais importante?

**Score 1:** Elementos competindo por atenção no mesmo peso, o usuário não sabe onde olhar
**Score 3:** Hierarquia razoável, segue convenções existentes sem introduzir problemas
**Score 5:** Clareza imediata, usuário sabe o que fazer antes de ler qualquer palavra

### Tipografia
- [ ] Máximo 2 typefaces
- [ ] Body: line-height 1.4-1.6, max-width 65ch
- [ ] Hierarquia via scale + peso, ratio ≥ 1.25x entre níveis
- [ ] Nenhuma fonte decorativa em texto de interface

**Score 1:** Inconsistente, ilegível, ou fontes que conflitam
**Score 3:** Seguindo sistema existente, nada errado
**Score 5:** Tipografia cria ritmo, o usuário flui pelo conteúdo naturalmente

### Espaçamento
- [ ] Valores em múltiplos de 4px ou 8px (4, 8, 12, 16, 24, 32, 48, 64)
- [ ] Espaço menor dentro de grupos, maior entre grupos (Gestalt)
- [ ] Espaço em branco tratado como elemento, não como desperdício
- [ ] Padding interno de cards/componentes consistente em toda a página

**Score 1:** Espaçamento aleatório, 12px aqui, 17px ali, 14px em outro lugar
**Score 3:** Consistente, grid seguido
**Score 5:** Ritmo de espaçamento cria senso de ordem e confiança

### Cor
- [ ] Regra 60-30-10 respeitada
- [ ] Cor acento usada com parcimônia (raridade = poder)
- [ ] Contraste mínimo WCAG AA: 4.5:1 para texto normal
- [ ] Cor serve comunicação, não decoração

**Score 1:** Cores sem função, contraste insuficiente, hierarquia quebrada por cor
**Score 3:** Sistema de cores seguido, sem violações óbvias
**Score 5:** Cor guia atenção com precisão, cada escolha serve comunicação ou marca

### Motion (se houver animações)
- [ ] Toda animação responde a uma pergunta do usuário ("onde foi?", "está carregando?")
- [ ] Duração dentro de 100-500ms para interações
- [ ] Easing exponencial (não `ease` genérico, não bounce)
- [ ] `prefers-reduced-motion` implementado
- [ ] Nada animando propriedades de layout diretamente

**Score 1:** Animações decorativas que distraem do conteúdo
**Score 3:** Animações corretas, inofensivas
**Score 5:** Motion aumenta compreensão, o usuário entende o que aconteceu mais rápido

### Mobile
- [ ] Toque mínimo de 44x44px para targets interativos
- [ ] Layout mobile não é o desktop "encolhido"
- [ ] Conteúdo prioritário visível sem scroll no mobile
- [ ] Sem scroll horizontal

**Score 1:** Mobile quebrado ou claramente uma afterthought
**Score 3:** Responsivo, funcional
**Score 5:** Mobile tem fluxo próprio, o contexto mobile foi considerado, não adaptado

---

## Scoring Final

```
[ ] Hierarquia Visual:  __/5
[ ] Tipografia:         __/5
[ ] Espaçamento:        __/5
[ ] Cor:                __/5
[ ] Motion:             __/5 (pular se não tem animações)
[ ] Mobile:             __/5

Score médio: __/5
```

**Score ≥ 4.0** → Entregar
**Score 3.0-3.9** → Identificar o item de maior impacto e corrigir antes de entregar
**Score < 3.0** → Não entregar, revisar hierarquia e espaçamento primeiro (maior alavancagem)

---

## AI Slop Test Final

Antes de entregar, responder:

**"Isso parece gerado por IA?"**
→ Se sim: qual elemento é genérico demais? Substituir.

**"Tem algum detalhe que só alguém com gosto colocaria?"**
→ Se não: adicionar um elemento intencional não-óbvio.

---

## Quando acionar impeccable

| Situação | Comando |
|----------|---------|
| Score < 3 e precisa de revisão profunda | `npx impeccable critique` |
| Tudo certo mas quer refinar qualidade final | `npx impeccable polish` |
| Animações precisam de revisão | `npx impeccable animate` |
| Auditoria técnica (a11y, perf, responsivo) | `npx impeccable audit` |
| Design está seguro demais, precisa de mais impacto | `npx impeccable bolder` |
| Design está agressivo demais | `npx impeccable quieter` |
