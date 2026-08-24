# MCPs PREFERENCIAIS: 21st.dev Magic + Google Stitch

**REGRA (reconciliada com o Step 0):** estes MCPs sao OBRIGATORIOS **quando conectados**.
Se nao estiverem disponiveis na sessao (ver checagem de pre-requisitos no Step 0), usar o
fallback documentado, nunca travar. O proibido e ter o MCP conectado e NAO usar.

**Quando o MCP ESTA conectado:**
- **PROIBIDO** construir componente de UI do zero sem antes consultar o 21st.dev.
- **PROIBIDO** comecar a codar pagina nova sem gerar wireframe no Stitch.
- **PROIBIDO** usar logo de empresa hardcoded sem antes buscar no `logo_search`.

**Quando o MCP NAO esta conectado (fallback do Step 0):**
- Sem Stitch → pular wireframe, ir direto pro layout no codigo (Step 2 define o layout por secao mesmo assim).
- Sem 21st.dev → escrever componentes a mao com shadcn/ui + Tailwind + os padroes deste arquivo.
- Sem logo_search → buscar o SVG oficial (Simple Icons) ou recriar vetorial; nunca chutar paths.

Violar a regra (ter o MCP e nao usar) resulta em: mais tempo de build, visual inferior, retrabalho.

---

### 21st.dev Magic MCP: Componentes UI prontos (OBRIGATÓRIO)

**Regra:** Todo componente que vai na página DEVE passar pelo 21st.dev antes de ser escrito manualmente. Se existir um pronto, usar como base. Se não existir, aí sim escrever do zero.

**Ferramentas:**

| Ferramenta | Quando usar |
|------------|-------------|
| `mcp__magic__21st_magic_component_builder` | Qualquer componente específico: "glassmorphism pricing card", "animated hero CTA button", "dark navbar with blur" |
| `mcp__magic__21st_magic_component_inspiration` | Quando não tem referência visual: buscar antes de inventar |
| `mcp__magic__21st_magic_component_refiner` | Componente gerado mas pode melhorar: sempre usar antes de entregar |
| `mcp__magic__logo_search` | QUALQUER logo de empresa/marca na página: nunca construir SVG genérico sem buscar primeiro |

**Protocolo de uso obrigatório:**
```
STEP 3 (BUILDAR), para cada componente:
  1. → 21st_magic_component_inspiration OU builder com descrição específica
  2. Analisar o resultado: adaptar brand tokens, cores, fontes do projeto
  3. Se bom mas pode melhorar → 21st_magic_component_refiner
  4. Só então escrever/adaptar o código final
  5. NUNCA copiar cego: sempre checar brand consistency
```

**Prompts efetivos:**
- `"dark luxury SaaS hero section with floating orbs and gradient text"` → inspiration
- `"glassmorphism card with purple glow border hover effect"` → builder
- `"animated CTA button with shimmer effect dark background"` → builder
- `"modern sticky navbar with blur backdrop dark theme"` → builder
- `"pricing section 3 tiers dark background purple accent"` → inspiration

---

### Google Stitch MCP: Wireframe visual antes do código (OBRIGATÓRIO)

**Regra:** TODA página nova começa com um wireframe no Stitch. Zero exceções. O wireframe é a ponte entre o brief e o código, evita construir estrutura errada.

**Ferramentas:**

| Ferramenta | Quando usar |
|------------|-------------|
| `mcp__stitch__generate_screen_from_text` | **SEMPRE**: primeira ação ao receber um brief de página nova |
| `mcp__stitch__get_screen_image` | Ver o resultado gerado antes de aceitar |
| `mcp__stitch__get_screen_code` | Extrair código base quando o layout está aprovado |
| `mcp__stitch__generate_variants` | Gerar 2-3 variantes para o usuário escolher o estilo |
| `mcp__stitch__edit_screens` | Ajustar o wireframe até estar correto antes de codar |
| `mcp__stitch__list_projects` | Verificar se já existe projeto salvo do mesmo cliente |
| `mcp__stitch__list_screens` | Ver telas já geradas de um projeto existente |
| `mcp__stitch__get_project` | Detalhes de um projeto Stitch |

**Protocolo de uso obrigatório:**
```
STEP 2 (DIRECIONAR), wireframe obrigatório:
  1. → generate_screen_from_text com brief detalhado (tipo, tom, seções, cores, stack)
  2. → get_screen_image: avaliar o resultado
  3. Se não agradou → generate_variants (3 opções) → usuário escolhe
  4. → edit_screens se precisar ajuste fino
  5. → get_screen_code: código base da estrutura aprovada
  6. A partir daqui: refinar com 21st.dev + brand tokens do projeto
```

**Prompt ideal para Stitch:**
```
Ser específico em 4 dimensões:
1. Tipo de negócio: "landing page for WhatsApp API agency"
2. Estilo visual: "dark luxury, deep purple/navy background, #7F41F9 accent"
3. Seções desejadas: "hero split layout, features 3-col grid, integration logos marquee, CTA section"
4. Stack: "React/Tailwind, Framer Motion animations"
```

---

### Workflow Obrigatório: Stitch → 21st.dev → Código Final

```
Brief do usuário
    ↓
[STEP 2] Stitch generate_screen_from_text
    → get_screen_image → aprovar layout
    → (se necessário) generate_variants → escolher
    → get_screen_code → estrutura base
    ↓
[STEP 3] Para cada componente:
    → 21st_magic_component_inspiration OU builder
    → logo_search para cada marca/empresa
    → adaptar brand tokens + refiner se necessário
    ↓
Montar página final: estrutura Stitch + componentes 21st.dev + brand tokens
    ↓
Deploy + validação pós-deploy
```

**Checklist obrigatório antes de entregar qualquer página:**
- [ ] Stitch wireframe gerado e aprovado (ou documentado porque foi pulado)
- [ ] Todos os componentes principais passaram pelo 21st.dev inspiration/builder
- [ ] Todos os logos de marcas buscados via logo_search
- [ ] Componentes finais passaram pelo refiner
- [ ] Brand tokens aplicados consistentemente

---
