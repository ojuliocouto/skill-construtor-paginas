# Workflow de Copia de Pagina a partir de PDF

Quando o usuario fornecer um PDF de uma pagina (screenshot, export, design) e quiser reproduzir como codigo, siga este workflow sistematico.

### Quando Usar

- Usuario pede para "copiar essa pagina" e fornece um PDF
- Usuario quer "replicar esse layout" de um PDF
- Usuario quer "converter esse design" em HTML/React
- Usuario tem um PDF de referencia e quer uma pagina igual ou similar
- Usuario quer "clonar" uma pagina de concorrente/referencia a partir de PDF

### Passo 1: Ler o PDF Completo

**OBRIGATORIO: Ler TODAS as paginas do PDF antes de qualquer implementacao.**

```
# Usar a tool Read com o caminho do PDF
# Para PDFs pequenos (1-10 paginas): ler tudo de uma vez
Read file_path="/caminho/do/arquivo.pdf"

# Para PDFs grandes (10+ paginas): ler em blocos de 20 paginas
Read file_path="/caminho/do/arquivo.pdf" pages="1-20"
Read file_path="/caminho/do/arquivo.pdf" pages="21-40"
```

**O que extrair na leitura:**
- Layout geral (full-width, centralizado, sidebar, etc.)
- Numero e ordem das secoes
- Hierarquia do conteudo (titulos, subtitulos, corpo)
- Textos exatos (headlines, CTAs, descricoes)
- Imagens e icones presentes
- Elementos interativos (botoes, formularios, menus)

### Passo 2: Mapear a Estrutura Visual

Apos ler o PDF, documentar mentalmente (ou em comentarios) cada secao:

```
MAPA DA PAGINA (extraido do PDF):
================================

SECAO 1, NAVBAR
- Tipo: fixa/flutuante/transparente
- Logo: posicao esquerda/centro
- Links: quais e quantos
- CTA navbar: texto do botao
- Estilo: glass/solido/transparente

SECAO 2, HERO
- Layout: texto-esquerda+imagem-direita / centralizado / full-image
- Badge/tag: texto se houver
- Titulo principal: texto exato
- Subtitulo: texto exato
- CTA primario: texto e estilo
- CTA secundario: texto se houver
- Imagem/mockup: descricao
- Social proof: tipo e posicao

SECAO 3, [NOME]
- ...

(continuar para cada secao)
```

### Passo 3: Identificar Paleta e Tipografia

**Cores, Extrair do visual do PDF:**

| Elemento | Cor observada | Classe Tailwind equivalente |
|----------|--------------|----------------------------|
| Background principal | (ex: escuro, quase preto) | `bg-slate-950` |
| Background secoes | (ex: cinza claro) | `bg-gray-50` |
| Texto titulo | (ex: branco) | `text-white` |
| Texto corpo | (ex: cinza medio) | `text-gray-400` |
| Cor primaria (CTAs) | (ex: roxo/azul) | `bg-indigo-600` |
| Cor secundaria | (ex: rosa/verde) | `bg-pink-500` |
| Bordas/divisores | (ex: cinza sutil) | `border-gray-800` |
| Gradientes | (ex: roxo → rosa) | `from-purple-600 to-pink-600` |

**Tipografia, Mapear do visual:**

| Elemento | Tamanho estimado | Peso | Classe Tailwind |
|----------|-----------------|------|-----------------|
| H1 (hero) | ~60-80px | Extra bold | `text-6xl md:text-8xl font-black` |
| H2 (secoes) | ~36-48px | Bold | `text-4xl md:text-5xl font-bold` |
| H3 (cards) | ~20-24px | Semibold | `text-xl font-semibold` |
| Body | ~16px | Regular | `text-base` |
| Caption | ~14px | Regular | `text-sm text-gray-500` |

**Fontes, Identificar ou aproximar:**
- Se reconhecer a fonte: usar a mesma do Google Fonts
- Se nao reconhecer: aproximar pela categoria:
  - Sans-serif geometrica → Inter, Geist, DM Sans
  - Sans-serif humanista → Plus Jakarta Sans, Nunito
  - Serif moderna → Playfair Display, Lora
  - Monospace → JetBrains Mono, Fira Code

### Passo 4: Implementar Secao por Secao

**Regra de ouro: Fidelidade ao layout original + upgrade com animacoes.**

A implementacao deve ser:
1. **Fiel ao layout**: mesma ordem de secoes, mesma hierarquia
2. **Fiel ao conteudo**: copiar textos, titulos, CTAs exatamente como no PDF
3. **Fiel as cores**: replicar a paleta observada
4. **Melhorada com animacoes**: adicionar Framer Motion scroll reveals, hover effects
5. **Responsiva**: o PDF mostra desktop, mas o codigo deve funcionar em mobile

```tsx
// Estrutura padrao de implementacao por secao
// Para cada secao identificada no PDF:

{/* ===== SECAO [N]: [NOME] ===== */}
<section className="py-24 [background-classes]">
  <div className="max-w-7xl mx-auto px-6">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      viewport={{ once: true }}
    >
      {/* Conteudo extraido do PDF */}
    </motion.div>
  </div>
</section>
```

### Passo 5: Imagens e Assets

**Para imagens do PDF que nao estao disponiveis:**
- **NUNCA usar placeholders vazios.** Gerar imagens similares com IA (DALL-E, ou buscar em bancos de imagem) para que a pagina fique completa na primeira entrega.
- Buscar fotos/videos similares nos bancos gratuitos:
  ```bash
  python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py "descricao da imagem" --type photo
  ```
- Se nao encontrar similar, gerar com IA descrevendo o que aparece no PDF.
- Avisar o usuario quais imagens foram geradas/substituidas, para que ele troque se quiser.
- Para icones: usar Lucide ou Heroicons com variantes **detalhadas e profissionais** (strokeWidth adequado, tamanhos generosos). NUNCA usar icones simples demais ou genericos que parecem amadores.

**Para logos de marcas/parceiros vistos no PDF:**
- Usar Simple Icons (SVG) se disponivel
- Se nao reconhecer, buscar o SVG oficial online antes de usar generico

### Passo 6: Refinamento e Fidelidade

**Checklist de fidelidade ao PDF:**
- [ ] Todas as secoes do PDF estao presentes no codigo
- [ ] Ordem das secoes e identica
- [ ] Textos copiados fielmente (titulos, CTAs, descricoes)
- [ ] Paleta de cores replicada
- [ ] Espacamento e proporcoes respeitados
- [ ] Layout de grid/colunas replicado
- [ ] Elementos visuais (badges, icones, dividers) presentes

**Upgrades automaticos (nao presentes no PDF estatico):**
- [ ] Scroll reveal em todas as secoes (Framer Motion)
- [ ] Hover effects em cards e botoes
- [ ] Responsividade mobile
- [ ] Dark mode (se aplicavel)
- [ ] Animacoes de entrada na hero
- [ ] NumberTicker em stats (se houver numeros)
- [ ] Transicoes suaves em links e botoes

### Exemplo de Prompt Interno

Quando receber um PDF, processar mentalmente assim:

```
1. LER: Read do PDF completo (todas as paginas)
2. MAPEAR: Listar cada secao com nome, tipo e conteudo
3. PALETA: Identificar 5-8 cores dominantes → mapear para Tailwind
4. TIPOGRAFIA: Identificar fonte, tamanhos, pesos → mapear para Tailwind
5. LAYOUT: Identificar grid (1 col, 2 col, bento, etc.)
6. IMPLEMENTAR: Codigo secao por secao, top-down
7. ANIMAR: Adicionar Framer Motion em tudo
8. REVISAR: Comparar visualmente com o PDF
```

### Dicas para PDFs de Diferentes Tipos

**PDF de Landing Page (marketing):**
- Foco em conversao: CTAs chamativos, social proof, urgencia
- Copiar textos de venda exatamente
- Manter a sequencia persuasiva (dor → solucao → prova → oferta)

**PDF de Dashboard/App (interface):**
- Foco em funcionalidade: sidebar, menus, tabelas, graficos
- Usar shadcn/ui para componentes de UI
- Implementar estados (hover, active, selected)

**PDF de Portfolio/Institucional (branding):**
- Foco em estetica: espacamento generoso, tipografia forte
- Respeitar white space do original
- Manter tom e voz do conteudo

**PDF com multiplas paginas:**
- Ler TODAS as paginas antes de comecar
- Mapear a navegacao entre paginas
- Implementar como SPA com sections ou como multi-page

---
