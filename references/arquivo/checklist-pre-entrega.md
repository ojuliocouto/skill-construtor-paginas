# Checklist Pre-Entrega

> AUXILIAR de build, NÃO é o portão. O portão de entrega e a wave de auditoria (Step 4.0).
> Use esta lista pra chegar limpo na wave; a decisão de entregar e da wave (`deploy_liberado`).

### Qualidade Visual
- [ ] ZERO emojis na página inteira (usar SVG - Heroicons/Lucide)
- [ ] Ícones de um set consistente, detalhados e profissionais (nada "simples demais" ou genérico)
- [ ] Ícones com tamanho generoso (min 20x20, ideal 24x24+) e strokeWidth adequado
- [ ] Logos corretos (verificar Simple Icons)
- [ ] Hover states não causam layout shift
- [ ] Todos clicáveis tem `cursor-pointer`

### Interação
- [ ] Transições suaves (150-300ms)
- [ ] Focus states visíveis para navegação por teclado
- [ ] Loading states (skeleton/spinner)

### Light/Dark Mode
- [ ] Texto com contraste suficiente (4.5:1 mínimo)
- [ ] Elementos glass/transparentes visíveis em light mode
- [ ] Bordas visíveis em ambos os modos

### Layout
- [ ] Elementos flutuantes com espaçamento das bordas
- [ ] Sem conteúdo escondido atrás de navbar fixa
- [ ] Responsivo em 320px, 768px, 1024px, 1440px
- [ ] Sem scroll horizontal em mobile

### Acessibilidade
- [ ] Todas imagens tem alt text
- [ ] Inputs de form tem labels
- [ ] Cor não é o único indicador
- [ ] `prefers-reduced-motion` respeitado
- [ ] Skip links para navegação por teclado

### Performance
- [ ] Hero image < 200KB
- [ ] Página total < 2MB
- [ ] Lazy load abaixo do fold
- [ ] Componentes pesados com dynamic import (SSR: false)
- [ ] TODAS as imagens convertidas para WebP (`cwebp -q 82`)
- [ ] Tailwind compilado para CSS puro (NUNCA usar cdn.tailwindcss.com em produção)
- [ ] `preconnect` para Google Fonts
- [ ] `will-change` em animações críticas (marquee, hero blur, glow)
- [ ] Marquee pausa quando fora da viewport (IntersectionObserver)

### Deploy (Cloudflare Pages / Hosting)
- [ ] Todos os paths de assets são relativos (sem `/` inicial)
- [ ] OG/Twitter meta tags com URLs absolutas
- [ ] `theme-color` meta tag definida
- [ ] Testou a página publicada (não apenas local)

### CRO / Conversão
- [ ] Hero prende atenção em 3 segundos (animação de entrada + visual forte)
- [ ] Countdown evergreen funcionando (reseta meia-noite)
- [ ] Social proof visível acima do fold (avatares, números, estrelas)
- [ ] Múltiplos CTAs ao longo da página (8+), todos apontam para checkout
- [ ] Botões de CTA/checkout DISPARAM de verdade (testado por clique, não placeholder)
- [ ] Sticky CTA mobile aparece ao scrollar e some no checkout
- [ ] `no-js` fallback (conteúdo visível sem JavaScript)

### Legal / Compliance (Anti-Vibe-Coding)
- [ ] Footer com links legais reais (Termos de Uso, Política de Privacidade)
- [ ] Dados de contato/identificacao (e-mail, CNPJ ou responsável) presentes
- [ ] Badges/selos só se tiverem dado/funcao real por trás (nada de "● online" decorativo)

---
