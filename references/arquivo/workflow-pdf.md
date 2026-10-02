# Workflow de Copia de Página a partir de PDF

Quando o usuário fornecer um PDF de uma página (screenshot, export, design) e quiser reproduzir como código, siga este workflow sistemático.

### Quando Usar

- Usuário pede para "copiar essa página" e fornece um PDF
- Usuário quer "replicar esse layout" de um PDF
- Usuário quer "converter esse design" em HTML/React
- Usuário tem um PDF de referência e quer uma página igual ou similar
- Usuário quer "clonar" uma página de concorrente/referencia a partir de PDF

### Passo 1: Ler o PDF Completo

**OBRIGATÓRIO: Ler TODAS as páginas do PDF antes de qualquer implementação.**

```
# Usar a tool Read com o caminho do PDF
# Para PDFs pequenos (1-10 páginas): ler tudo de uma vez
Read file_path="/caminho/do/arquivo.pdf"

# Para PDFs grandes (10+ páginas): ler em blocos de 20 páginas
Read file_path="/caminho/do/arquivo.pdf" pages="1-20"
Read file_path="/caminho/do/arquivo.pdf" pages="21-40"
```

**O que extrair na leitura:**
- Layout geral (full-width, centralizado, sidebar, etc.)
- Número e ordem das seções
- Hierarquia do conteúdo (títulos, subtítulos, corpo)
- Textos exatos (headlines, CTAs, descrições)
- Imagens e ícones presentes
- Elementos interativos (botões, formulários, menus)

### Passo 2: Mapear a Estrutura Visual

Após ler o PDF, documentar mentalmente (ou em comentários) cada seção:

```
MAPA DA PÁGINA (extraído do PDF):
================================

SEÇÃO 1, NAVBAR
- Tipo: fixa/flutuante/transparente
- Logo: posição esquerda/centro
- Links: quais e quantos
- CTA navbar: texto do botão
- Estilo: glass/solido/transparente

SEÇÃO 2, HERO
- Layout: texto-esquerda+imagem-direita / centralizado / full-image
- Badge/tag: texto se houver
- Título principal: texto exato
- Subtítulo: texto exato
- CTA primário: texto e estilo
- CTA secundário: texto se houver
- Imagem/mockup: descrição
- Social proof: tipo e posição

SEÇÃO 3, [NOME]
- ...

(continuar para cada seção)
```

### Passo 3: Identificar Paleta e Tipografia

**Cores, Extrair do visual do PDF:**

| Elemento | Cor observada | Classe Tailwind equivalente |
|----------|--------------|----------------------------|
| Background principal | (ex: escuro, quase preto) | `bg-slate-950` |
| Background seções | (ex: cinza claro) | `bg-gray-50` |
| Texto título | (ex: branco) | `text-white` |
| Texto corpo | (ex: cinza médio) | `text-gray-400` |
| Cor primária (CTAs) | (ex: roxo/azul) | `bg-indigo-600` |
| Cor secundária | (ex: rosa/verde) | `bg-pink-500` |
| Bordas/divisores | (ex: cinza sutil) | `border-gray-800` |
| Gradientes | (ex: roxo → rosa) | `from-purple-600 to-pink-600` |

**Tipografia, Mapear do visual:**

| Elemento | Tamanho estimado | Peso | Classe Tailwind |
|----------|-----------------|------|-----------------|
| H1 (hero) | ~60-80px | Extra bold | `text-6xl md:text-8xl font-black` |
| H2 (seções) | ~36-48px | Bold | `text-4xl md:text-5xl font-bold` |
| H3 (cards) | ~20-24px | Semibold | `text-xl font-semibold` |
| Body | ~16px | Regular | `text-base` |
| Caption | ~14px | Regular | `text-sm text-gray-500` |

**Fontes, Identificar ou aproximar:**
- Se reconhecer a fonte: usar a mesma do Google Fonts
- Se não reconhecer: aproximar pela categoria:
  - Sans-serif geométrica → Inter, Geist, DM Sans
  - Sans-serif humanista → Plus Jakarta Sans, Nunito
  - Serif moderna → Playfair Display, Lora
  - Monospace → JetBrains Mono, Fira Code

### Passo 4: Implementar Seção por Seção

**Regra de ouro: Fidelidade ao layout original + upgrade com animações.**

A implementação deve ser:
1. **Fiel ao layout**: mesma ordem de seções, mesma hierarquia
2. **Fiel ao conteúdo**: copiar textos, títulos, CTAs exatamente como no PDF
3. **Fiel as cores**: replicar a paleta observada
4. **Melhorada com animações**: adicionar Framer Motion scroll reveals, hover effects
5. **Responsiva**: o PDF mostra desktop, mas o código deve funcionar em mobile

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

**Para imagens do PDF que não estão disponíveis:**
- **NUNCA usar placeholders vazios.** Gerar imagens similares com IA (DALL-E, ou buscar em bancos de imagem) para que a página fique completa na primeira entrega.
- Buscar fotos/videos similares nos bancos gratuitos:
  ```bash
  python3 <dir-da-skill>/scripts/assets-search.py "descricao da imagem" --type photo
  ```
- Se não encontrar similar, gerar com IA descrevendo o que aparece no PDF.
- Avisar o usuário quais imagens foram geradas/substituidas, para que ele troque se quiser.
- Para ícones: usar Lucide ou Heroicons com variantes **detalhadas e profissionais** (strokeWidth adequado, tamanhos generosos). NUNCA usar ícones simples demais ou genéricos que parecem amadores.

**Para logos de marcas/parceiros vistos no PDF:**
- Usar Simple Icons (SVG) se disponível
- Se não reconhecer, buscar o SVG oficial online antes de usar genérico

### Passo 6: Refinamento e Fidelidade

**Checklist de fidelidade ao PDF:**
- [ ] Todas as seções do PDF estão presentes no código
- [ ] Ordem das seções e idêntica
- [ ] Textos copiados fielmente (títulos, CTAs, descrições)
- [ ] Paleta de cores replicada
- [ ] Espaçamento e proporções respeitados
- [ ] Layout de grid/colunas replicado
- [ ] Elementos visuais (badges, ícones, dividers) presentes

**Upgrades automáticos (não presentes no PDF estático):**
- [ ] Scroll reveal em todas as seções (Framer Motion)
- [ ] Hover effects em cards e botões
- [ ] Responsividade mobile
- [ ] Dark mode (se aplicável)
- [ ] Animações de entrada na hero
- [ ] NumberTicker em stats (se houver números)
- [ ] Transições suaves em links e botões

### Exemplo de Prompt Interno

Quando receber um PDF, processar mentalmente assim:

```
1. LER: Read do PDF completo (todas as páginas)
2. MAPEAR: Listar cada seção com nome, tipo e conteúdo
3. PALETA: Identificar 5-8 cores dominantes → mapear para Tailwind
4. TIPOGRAFIA: Identificar fonte, tamanhos, pesos → mapear para Tailwind
5. LAYOUT: Identificar grid (1 col, 2 col, bento, etc.)
6. IMPLEMENTAR: Código seção por seção, top-down
7. ANIMAR: Adicionar Framer Motion em tudo
8. REVISAR: Comparar visualmente com o PDF
```

### Dicas para PDFs de Diferentes Tipos

**PDF de Landing Page (marketing):**
- Foco em conversão: CTAs chamativos, social proof, urgência
- Copiar textos de venda exatamente
- Manter a sequência persuasiva (dor → solução → prova → oferta)

**PDF de Dashboard/App (interface):**
- Foco em funcionalidade: sidebar, menus, tabelas, gráficos
- Usar shadcn/ui para componentes de UI
- Implementar estados (hover, active, selected)

**PDF de Portfolio/Institucional (branding):**
- Foco em estética: espaçamento generoso, tipografia forte
- Respeitar white space do original
- Manter tom e voz do conteúdo

**PDF com múltiplas páginas:**
- Ler TODAS as páginas antes de começar
- Mapear a navegação entre páginas
- Implementar como SPA com sections ou como multi-page

---
