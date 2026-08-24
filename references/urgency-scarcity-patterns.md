# Padroes de Urgencia e Escassez

Urgencia real converte. Urgencia falsa destroi confianca para sempre. Este repositorio cobre os padroes visuais e de copy corretos para cada tipo de urgencia.

---

## Regra de Ouro: Urgencia Real vs Urgencia Falsa

| Urgencia REAL (use) | Urgencia FALSA (nunca use) |
|--------------------|-----------------------------|
| Data de encerramento real e fixa | "Oferta por tempo limitado" sem data |
| Numero real de vagas disponivel | "Vagas limitadas" sem numero |
| Preco que sobe em data especifica | Countdown que reseta ao recarregar |
| Turma que fecha (enrollment period) | "Promocao imperdivel" sem contexto |
| Early bird com data de expiracao | "Ultimas unidades" em produto digital infinito |
| Bonus que some na data X | "Aproveite agora" sem consequencia |

---

## Padrao 1: Countdown Timer

**Quando usar:** Data real de encerramento (lancamento, black friday, turma fechando).

```tsx
'use client'
import { useState, useEffect } from 'react'

function CountdownTimer({ targetDate }: { targetDate: Date }) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 })

  useEffect(() => {
    const calc = () => {
      const diff = targetDate.getTime() - new Date().getTime()
      if (diff <= 0) return setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 })
      setTimeLeft({
        days: Math.floor(diff / (1000 * 60 * 60 * 24)),
        hours: Math.floor((diff / (1000 * 60 * 60)) % 24),
        minutes: Math.floor((diff / (1000 * 60)) % 60),
        seconds: Math.floor((diff / 1000) % 60),
      })
    }
    calc()
    const interval = setInterval(calc, 1000)
    return () => clearInterval(interval)
  }, [targetDate])

  const units = [
    { value: timeLeft.days, label: 'dias' },
    { value: timeLeft.hours, label: 'horas' },
    { value: timeLeft.minutes, label: 'min' },
    { value: timeLeft.seconds, label: 'seg' },
  ]

  return (
    <div className="flex items-center gap-3">
      {units.map(({ value, label }, i) => (
        <div key={label} className="flex items-center gap-3">
          <div className="flex flex-col items-center">
            <div className="bg-gray-950 text-white rounded-xl px-4 py-3 min-w-[64px] text-center">
              <span className="text-3xl font-black tabular-nums">
                {String(value).padStart(2, '0')}
              </span>
            </div>
            <span className="text-xs text-gray-500 mt-1 font-medium">{label}</span>
          </div>
          {i < 3 && <span className="text-2xl font-black text-gray-400 mb-4">:</span>}
        </div>
      ))}
    </div>
  )
}

// Uso:
<CountdownTimer targetDate={new Date('2026-04-01T23:59:59')} />
```

**Posicionamento ideal:**
- No hero, abaixo do CTA (visivel sem scroll)
- No CTA final, acima do botao
- Em sticky header (aparece quando usuario fica > 30s na pagina)

---

## Padrao 2: Vagas Counter

**Quando usar:** Turma ou evento com numero real de vagas.

```tsx
function VagasCounter({ total, available }: { total: number; available: number }) {
  const percentage = ((total - available) / total) * 100

  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 dark:bg-red-950/30 dark:border-red-900/50 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-semibold text-red-700 dark:text-red-400">
          Vagas disponiveis
        </span>
        <span className="text-sm font-black text-red-700 dark:text-red-400">
          {available}/{total}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-red-100 dark:bg-red-900/50 rounded-full overflow-hidden">
        <div
          className="h-full bg-red-500 rounded-full transition-all duration-1000"
          style={{ width: `${percentage}%` }}
        />
      </div>

      <p className="text-xs text-red-600 dark:text-red-400 mt-2">
        {percentage >= 80
          ? `Quase esgotado, apenas ${available} vagas restantes`
          : percentage >= 50
          ? `${available} vagas ainda disponiveis`
          : `${available} vagas abertas nesta turma`}
      </p>
    </div>
  )
}
```

---

## Padrao 3: Sticky Urgency Bar (Top Banner)

**Quando usar:** Lancamentos com deadline. Aparece na parte superior da pagina, segue o scroll.

```tsx
function UrgencyBanner({ message, ctaText, ctaHref }: {
  message: string; ctaText: string; ctaHref: string
}) {
  return (
    <div className="fixed top-0 left-0 right-0 z-[100] bg-gradient-to-r from-red-600 to-orange-600 text-white py-2.5 px-4">
      <div className="max-w-6xl mx-auto flex items-center justify-center gap-4 text-sm">
        <span className="font-medium">{message}</span>
        <a
          href={ctaHref}
          className="bg-white text-red-600 font-bold px-4 py-1 rounded-full text-xs hover:bg-red-50 transition-colors flex-shrink-0"
        >
          {ctaText}
        </a>
      </div>
    </div>
  )
}

// Uso:
<UrgencyBanner
  message="Turma fecha em 48 horas, garanta sua vaga com o valor atual"
  ctaText="Quero entrar"
  ctaHref="#comprar"
/>
// OBRIGATORIO: adicionar pt-10 no body quando usar sticky bar
```

---

## Padrao 4: Early Bird Badge

**Quando usar:** Preco de early bird com data de expiracao.

```tsx
function EarlyBirdBadge({ expiryDate, currentPrice, originalPrice }: {
  expiryDate: string; currentPrice: number; originalPrice: number
}) {
  return (
    <div className="inline-flex items-center gap-2 bg-amber-100 dark:bg-amber-950/40 border border-amber-300 dark:border-amber-700/50 rounded-full px-4 py-2">
      <span className="text-amber-600 dark:text-amber-400">🔥</span>
      <span className="text-sm font-semibold text-amber-700 dark:text-amber-400">
        Early Bird, preco sobe em {expiryDate}
      </span>
      <span className="text-sm text-amber-600 dark:text-amber-500">
        R${currentPrice} <span className="line-through opacity-60">R${originalPrice}</span>
      </span>
    </div>
  )
}
```

---

## Padrao 5: Urgency CTA Section

**Quando usar:** CTA Final com maximo de urgencia. Secao dedicada.

```tsx
export function UrgencyCTASection({
  headline,
  subtext,
  ctaText,
  ctaHref,
  urgencyText,
  guaranteeText
}: {...}) {
  return (
    <section className="relative py-24 overflow-hidden bg-gray-950">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-red-950/30 via-gray-950 to-orange-950/20" />

      <div className="relative max-w-3xl mx-auto px-6 text-center">
        {/* Urgency pill */}
        <div className="inline-flex items-center gap-2 bg-red-500/20 border border-red-500/40 rounded-full px-4 py-2 mb-8">
          <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-red-400 text-sm font-semibold">{urgencyText}</span>
        </div>

        <h2 className="text-4xl md:text-5xl font-black text-white mb-4">{headline}</h2>
        <p className="text-gray-400 text-lg mb-10">{subtext}</p>

        <a
          href={ctaHref}
          className="inline-flex items-center gap-2 px-10 py-5 bg-gradient-to-r from-orange-500 to-red-500 text-white font-bold text-lg rounded-2xl shadow-2xl shadow-orange-500/30 hover:shadow-orange-500/50 hover:-translate-y-0.5 transition-all duration-200"
        >
          {ctaText}
        </a>

        <p className="text-gray-500 text-sm mt-4">{guaranteeText}</p>
      </div>
    </section>
  )
}
```

---

## Copy de Urgencia que Converte (Mercado BR)

### Headlines de urgencia por contexto

| Contexto | Copy |
|----------|------|
| Lancamento com deadline | "Inscricoes encerram [data]. Sem segunda chance." |
| Turma limitada | "Apenas [N] vagas nesta turma. [X] ja reservadas." |
| Early bird | "Valor de lancamento disponivel ate [data]. Depois sobe pra R$[X]." |
| Bonus expirando | "Os bonus somem quando o contador zerar." |
| Ultimo dia | "Hoje e o ultimo dia. Sem excecoes." |
| Evento com data | "O desafio comeca [data]. Quem se inscrever depois perde o dia 1." |

### Copy de microcopy abaixo do CTA (pos-urgencia)

```
"Garantia de 7 dias. Se nao gostar, devolvo tudo."
"Apenas [N] vagas. Pagamento seguro via Hotmart/Kiwify."
"Acesso imediato. Comece ainda hoje."
"Sem fidelidade. Cancele quando quiser."
```

---

## Checklist de Urgencia

- [ ] Urgencia e real (data, numero, evento especifico)
- [ ] Countdown nao reseta ao recarregar (usa data fixa, nao `Date.now() + X`)
- [ ] Copy de urgencia aparece proximo ao CTA principal
- [ ] Urgencia esta no CTA final
- [ ] Se tem vagas counter, o numero e plausivel e atualizado
- [ ] Nao ha mais de 2 elementos de urgencia simultaneos (sobrecarga = descredito)
