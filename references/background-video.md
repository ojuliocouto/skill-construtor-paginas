# Background Vídeo Animations (Camadas de Fundo)

Sistema comprovado para adicionar vídeos e overlays animados como fundo de seções. Usado em páginas dark-theme e light-theme.

**Resumo do sistema:**
- `section { isolation: isolate; }`: OBRIGATÓRIO em toda section com vídeo
- `.ev2-video-bg { z-index: -1; }`: NUNCA usar z-index: 0 ou positivo no background
- Seções claras: `ev2-video-bg--light` (opacity 0.06) + `ev2-light-grid`
- Seções escuras: `ev2-video-bg--dark` (opacity 0.15 + brightness 0.4) + `ev2-data-nodes` + `ev2-scan-line`
- Mobile: esconder tudo com `display: none !important` (performance)

**REGRAS CRÍTICAS:**
1. **NUNCA `z-index: 0` ou `z-index: 1` nos backgrounds**: usar `z-index: -1` + `isolation: isolate` na section
2. **NUNCA `overflow: hidden` em seções com overlap** (margin negativo) entre seções
3. **NUNCA `section > * { z-index: 1 }`**: cria stacking contexts que quebram overlaps
4. **Testar VISUALMENTE após deploy**: auditoria de código não garante resultado visual

---
