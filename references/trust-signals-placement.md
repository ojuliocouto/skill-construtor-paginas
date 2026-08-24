# Sinais de Confianca: Placement e Implementacao

Trust signals removem objecoes silenciosas. Um usuario pode gostar da oferta mas nao comprar porque sente inseguranca. Trust signals eliminam esse atrito sem que o usuario precise pedir.

---

## Os 8 Tipos de Trust Signals

| Tipo | Poder de Conversao | Quando usar |
|------|---------------------|-------------|
| Badge de garantia (visual) | Alto | Toda pagina de venda |
| Logos de pagamento | Alto | Proxima ao preco/checkout |
| Selos de seguranca (SSL, etc) | Medio-alto | Paginas com formulario ou checkout |
| Mencoes em midia/imprensa | Alto | Quando disponivel |
| Premios e certificacoes | Medio | Segmentos formais (saude, financas) |
| Logos de clientes / parceiros | Medio | Paginas B2B ou alta credibilidade |
| CNPJ / Razao Social | Medio | Mercado BR: gera confianca |
| Numero de alunos/clientes | Medio (varia) | Quando plausivel e especifico |

---

## Mapa de Placement por Posicao na Pagina

### 1. Hero (Logo abaixo do CTA)

**O que colocar:** Avatar stack + numero de alunos OU logos de midia pequenos

```tsx
// Avatar stack + contador
<div className="flex items-center gap-3 mt-6">
  <div className="flex -space-x-2">
    {avatars.map((src, i) => (
      <img key={i} src={src} alt="" className="w-8 h-8 rounded-full border-2 border-white object-cover" style={{ zIndex: 5 - i }} />
    ))}
  </div>
  <span className="text-sm text-gray-500">
    <strong className="text-gray-900">+2.400 alunos</strong> ja transformaram seus resultados
  </span>
</div>

// Logos de midia (alternativa)
<div className="flex items-center gap-2 mt-6">
  <span className="text-xs text-gray-400 uppercase tracking-wide">Como visto em</span>
  {mediaLogos.map(logo => (
    <img key={logo.name} src={logo.src} alt={logo.name} className="h-5 opacity-40 grayscale" />
  ))}
</div>
```

---

### 2. Social Proof Bar (Stats)

**O que colocar:** Numeros de impacto, nao "logos" aqui, mas metricas reais

```tsx
// 4 stats com NumberTicker
// Cada stat: numero + label descritivo
// Ex: "2.400+" + "alunos formados"
// Ex: "98%" + "satisfacao comprovada"
// Ex: "R$50M+" + "faturados pelos alunos"
```

---

### 3. Proxima ao Preco (CRITICO)

**O que colocar:** Logos de pagamento + badge de seguranca

```tsx
// Logo abaixo do preco ou do botao de CTA
<div className="flex flex-col items-center gap-3 mt-4">
  {/* Logos de pagamento */}
  <div className="flex items-center gap-2 flex-wrap justify-center">
    <img src="/icons/visa.svg" alt="Visa" className="h-6 opacity-60" />
    <img src="/icons/mastercard.svg" alt="Mastercard" className="h-6 opacity-60" />
    <img src="/icons/pix.svg" alt="PIX" className="h-6 opacity-60" />
    <img src="/icons/boleto.svg" alt="Boleto" className="h-5 opacity-60" />
    <img src="/icons/amex.svg" alt="Amex" className="h-5 opacity-60" />
  </div>
  {/* Microcopy de seguranca */}
  <p className="text-xs text-gray-400 flex items-center gap-1">
    <LockIcon className="w-3 h-3" /> Pagamento 100% seguro via Hotmart
  </p>
</div>
```

---

### 4. Garantia (POSICAO CRITICA: ANTES do CTA Final)

A garantia DEVE aparecer antes do botao de compra mais importante (CTA 7 ou 8). Nunca no footer, nunca pos-compra.

```tsx
function GuaranteeBadge({ days = 7 }: { days?: number }) {
  return (
    <div className="flex items-center gap-4 p-6 rounded-2xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-white/5 max-w-2xl mx-auto">
      {/* Badge visual */}
      <div className="flex-shrink-0 w-20 h-20 rounded-full bg-green-100 dark:bg-green-950/50 border-2 border-green-500/30 flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-black text-green-600 leading-none">{days}</span>
        <span className="text-xs font-bold text-green-600 uppercase tracking-wide">dias</span>
      </div>

      {/* Texto */}
      <div>
        <h4 className="font-bold text-gray-900 dark:text-white mb-1">
          Garantia Incondicional de {days} Dias
        </h4>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Se por qualquer motivo voce nao ficar satisfeito, devolvemos 100% do seu investimento. Sem perguntas. Sem burocracia.
        </p>
      </div>
    </div>
  )
}
```

**Placement correto:**
```
[Value Stack com preco]
[Garantia Badge]          ← AQUI
[CTA Botao Principal]
[Logos de pagamento]
```

---

### 5. Midia / "Como Visto Em" (Se disponivel)

**Posicionamento:** Duas opcoes validas:
- Logo abaixo do hero (antes do primeiro scroll) - impacto imediato
- Dentro da secao "Sobre o Mentor" - valida credibilidade pessoal

```tsx
function MediaMentions({ logos }: { logos: Array<{src: string; name: string}> }) {
  return (
    <div className="py-8 border-y border-gray-100 dark:border-white/5">
      <p className="text-center text-xs text-gray-400 uppercase tracking-widest mb-6">
        Como visto em
      </p>
      <div className="flex items-center justify-center gap-8 flex-wrap">
        {logos.map(logo => (
          <img
            key={logo.name}
            src={logo.src}
            alt={logo.name}
            className="h-6 md:h-8 opacity-35 grayscale hover:opacity-60 hover:grayscale-0 transition-all duration-300"
          />
        ))}
      </div>
    </div>
  )
}
```

---

### 6. Footer

**O que colocar:** CNPJ/empresa + links legais + plataformas de pagamento

```tsx
<footer className="py-8 border-t border-gray-100 dark:border-white/5">
  <div className="max-w-6xl mx-auto px-6">
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-400">
      {/* Dados legais BR */}
      <div className="text-center md:text-left">
        <p>© 2026 Nome da Empresa. CNPJ: XX.XXX.XXX/0001-XX</p>
        <p>Razao Social Ltda, Rua/Av, Cidade - Estado</p>
      </div>

      {/* Links */}
      <div className="flex items-center gap-4">
        <a href="/privacidade" className="hover:text-gray-600 transition-colors">Privacidade</a>
        <a href="/termos" className="hover:text-gray-600 transition-colors">Termos</a>
        <a href="/contato" className="hover:text-gray-600 transition-colors">Contato</a>
      </div>

      {/* Plataforma */}
      <div className="flex items-center gap-2">
        <span>Vendas processadas por</span>
        <img src="/icons/hotmart-gray.svg" alt="Hotmart" className="h-4 opacity-40" />
      </div>
    </div>
  </div>
</footer>
```

---

## Checklist de Trust Signals

Antes de entregar, verificar:

- [ ] Badge de garantia visivel e posicionado ANTES do CTA principal de compra
- [ ] Logos de pagamento presentes proximos ao preco/CTA
- [ ] Se tem formulario: microcopy de privacidade ("seus dados estao protegidos")
- [ ] Se tem numero de alunos: numero plausivel e contextualizado
- [ ] Footer tem CNPJ/empresa (obrigatorio no mercado BR)
- [ ] Footer tem links de privacidade e termos (obrigatorio LGPD)
- [ ] Se tem midia/imprensa: presente de forma visivel (nao enterrado no footer)
- [ ] Logos de pagamento incluem PIX (muito comum no mercado BR)
- [ ] Plataforma de pagamento identificada (Hotmart, Kiwify, etc.): familiaridade gera confianca

---

## Erros Comuns de Trust Signals

| Erro | Impacto | Correcao |
|------|---------|----------|
| Garantia so como texto (sem badge visual) | Passa despercebida | Sempre badge visual com numero de dias em destaque |
| Logos de pagamento no footer | Longe do momento de decisao | Mover para logo abaixo do botao de compra |
| CNPJ faltando | Desconfianca em compras BR (especialmente alto ticket) | Sempre incluir no footer |
| Numero de alunos implausivel | Destroi credibilidade de todos os outros sinais | Ser conservador e especifico ("847 alunos na ultima turma") |
| Sem microcopy de seguranca no formulario | Abandono de form por medo de spam | Adicionar "Seus dados estao protegidos e nao serao compartilhados" |
