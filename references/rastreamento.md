# Rastreamento: Meta Pixel, GA4 e os eventos da página

Seção e do PLANO (`references/plano.md`). Vale quando o plano diz `Pixel pedido: Meta e GA4`
(ou só um dos dois). Com `Pixel pedido: nenhum`, a página sai sem nada disso e o
`gate-rastreamento.py` passa direto.

## Onde o aluno pega cada ID

| Ferramenta | Onde pega | Formato | Se não tiver |
|---|---|---|---|
| Meta Pixel | Gerenciador de Eventos da Meta (business.facebook.com/events_manager), Fontes de dados, Conectar dados, Web; o ID aparece no topo do conjunto de dados | 15 ou 16 dígitos | Crie o conjunto de dados nessa tela (é gratuito e precisa de um portfólio empresarial). Sem anúncio na Meta, marque só GA4 |
| GA4 | analytics.google.com, Administrador, Fluxos de dados, Web; o "ID da métrica" | `G-` e 10 letras ou números | Crie a propriedade e o fluxo Web na mesma tela (gratuito, com a conta Google do negócio) |

**Nenhum ID entra neste repositório, no PLANO.md nem em print do plano.** No texto, o modelo é
`G-XXXXXXXXXX`. O ID real só entra no `window.RASTREIO` do projeto do aluno, na hora de montar a
página, e a página funciona sem ele: com o campo vazio, nada carrega e nada mede (o gate avisa).

## O snippet, no fim do `<head>`

Sem comentário dentro dele: o `gate-publicacao.py` reprova comentário no HTML publicado.

```html
<script>window.RASTREIO = { metaPixel: "", ga4: "" };</script>
<script>
(function () {
  var c = window.RASTREIO || {};
  if (c.metaPixel) {
    !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
      s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', c.metaPixel);
    fbq('track', 'PageView');
  }
  if (c.ga4) {
    var g = document.createElement('script');
    g.async = true;
    g.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(c.ga4);
    document.head.appendChild(g);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    gtag('js', new Date());
    gtag('config', c.ga4);
  }
  var padraoMeta = { clique_whatsapp: 'Contact', envio_formulario: 'Lead' };
  var padraoGa4 = { envio_formulario: 'generate_lead' };
  function enviar(nome, extra) {
    extra = extra || {};
    if (window.fbq && c.metaPixel) {
      fbq('trackCustom', nome, extra);
      if (padraoMeta[nome]) fbq('track', padraoMeta[nome]);
    }
    if (window.gtag && c.ga4) {
      gtag('event', nome, extra);
      if (padraoGa4[nome]) gtag('event', padraoGa4[nome]);
    }
  }
  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-evento]');
    if (!el || el.tagName === 'FORM') return;
    enviar(el.getAttribute('data-evento'), { rotulo: (el.textContent || '').trim().slice(0, 60) });
  });
  document.addEventListener('submit', function (e) {
    var f = e.target.closest('[data-evento]');
    if (f) enviar(f.getAttribute('data-evento'));
  });
  var marcos = { 50: 'rolagem_50', 90: 'rolagem_90' }, feitos = {};
  addEventListener('scroll', function () {
    var h = document.documentElement, p = (h.scrollTop + innerHeight) / h.scrollHeight * 100;
    for (var m in marcos) if (p >= Number(m) && !feitos[m]) { feitos[m] = 1; enviar(marcos[m]); }
  }, { passive: true });
})();
</script>
```

## Os eventos, ligados por data-atributo

| Evento | Onde vai | Meta (padrão) | GA4 (padrão) |
|---|---|---|---|
| `clique_whatsapp` | `data-evento="clique_whatsapp"` em TODO link `wa.me` ou `api.whatsapp.com` | Contact | evento próprio |
| `clique_cta` | `data-evento="clique_cta"` no botão principal que não é WhatsApp (o da primeira dobra, o de rolar para a oferta, o do checkout) | evento próprio | evento próprio |
| `rolagem_50` e `rolagem_90` | o próprio snippet, quando a pessoa passa de 50% e 90% da página | evento próprio | evento próprio |
| `envio_formulario` | `data-evento="envio_formulario"` na tag `<form>` | Lead | generate_lead |

Exemplo: `<a href="https://wa.me/55DDNUMERO" data-evento="clique_whatsapp">Agendar pelo WhatsApp</a>`.

## O gate

`node <dir-da-skill>/scripts/py.mjs gate-rastreamento.py --dist <dir>/dist --plano <dir>/PLANO.md`

Lê o pedido no PLANO.md e reprova a `dist/` sem o `window.RASTREIO`, sem o carregador de cada
ferramenta pedida, sem o ouvinte de `[data-evento]`, sem os marcos de rolagem, com link de
WhatsApp sem `clique_whatsapp`, sem nenhum `clique_cta` ou com formulário sem
`envio_formulario`. Para conferir que dispara: com o ID preenchido, abra a página com a
extensão Meta Pixel Helper ou o DebugView do GA4 e clique em cada botão.

## No domínio final

Endereço de teste com `noindex` também mede, mas mistura visita sua com visita real: filtre o
seu IP no GA4 (Administrador, Fluxos de dados, Configurar tag, Definir tráfego interno) ou só
preencha os IDs quando a página for para o domínio do cliente.
