# Checklist Pre-Entrega

> AUXILIAR de build, NAO e o portao. O portao de entrega e a wave de auditoria (Step 4.0).
> Use esta lista pra chegar limpo na wave; a decisao de entregar e da wave (`deploy_liberado`).

### Qualidade Visual
- [ ] ZERO emojis na pagina inteira (usar SVG - Heroicons/Lucide)
- [ ] Icones de um set consistente, detalhados e profissionais (nada "simples demais" ou generico)
- [ ] Icones com tamanho generoso (min 20x20, ideal 24x24+) e strokeWidth adequado
- [ ] Logos corretos (verificar Simple Icons)
- [ ] Hover states nao causam layout shift
- [ ] Todos clicaveis tem `cursor-pointer`

### Interacao
- [ ] Transicoes suaves (150-300ms)
- [ ] Focus states visiveis para navegacao por teclado
- [ ] Loading states (skeleton/spinner)

### Light/Dark Mode
- [ ] Texto com contraste suficiente (4.5:1 minimo)
- [ ] Elementos glass/transparentes visiveis em light mode
- [ ] Bordas visiveis em ambos os modos

### Layout
- [ ] Elementos flutuantes com espacamento das bordas
- [ ] Sem conteudo escondido atras de navbar fixa
- [ ] Responsivo em 320px, 768px, 1024px, 1440px
- [ ] Sem scroll horizontal em mobile

### Acessibilidade
- [ ] Todas imagens tem alt text
- [ ] Inputs de form tem labels
- [ ] Cor nao e o unico indicador
- [ ] `prefers-reduced-motion` respeitado
- [ ] Skip links para navegacao por teclado

### Performance
- [ ] Hero image < 200KB
- [ ] Pagina total < 2MB
- [ ] Lazy load abaixo do fold
- [ ] Componentes pesados com dynamic import (SSR: false)
- [ ] TODAS as imagens convertidas para WebP (`cwebp -q 82`)
- [ ] Tailwind compilado para CSS puro (NUNCA usar cdn.tailwindcss.com em producao)
- [ ] `preconnect` para Google Fonts
- [ ] `will-change` em animacoes criticas (marquee, hero blur, glow)
- [ ] Marquee pausa quando fora da viewport (IntersectionObserver)

### Deploy (Cloudflare Pages / Hosting)
- [ ] Todos os paths de assets sao relativos (sem `/` inicial)
- [ ] OG/Twitter meta tags com URLs absolutas
- [ ] `theme-color` meta tag definida
- [ ] Testou a pagina publicada (nao apenas local)

### CRO / Conversao
- [ ] Hero prende atencao em 3 segundos (animacao de entrada + visual forte)
- [ ] Countdown evergreen funcionando (reseta meia-noite)
- [ ] Social proof visivel acima do fold (avatares, numeros, estrelas)
- [ ] Multiplos CTAs ao longo da pagina (8+), todos apontam para checkout
- [ ] Botoes de CTA/checkout DISPARAM de verdade (testado por clique, nao placeholder)
- [ ] Sticky CTA mobile aparece ao scrollar e some no checkout
- [ ] `no-js` fallback (conteudo visivel sem JavaScript)

### Legal / Compliance (Anti-Vibe-Coding)
- [ ] Footer com links legais reais (Termos de Uso, Politica de Privacidade)
- [ ] Dados de contato/identificacao (e-mail, CNPJ ou responsavel) presentes
- [ ] Badges/selos so se tiverem dado/funcao real por tras (nada de "● online" decorativo)

---
