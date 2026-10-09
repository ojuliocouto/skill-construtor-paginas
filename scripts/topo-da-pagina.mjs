/**
 * O topo da página, definido num lugar só (G22, 3.5.10). Usado pelo gate-responsivo.mjs (primeira tela visível no celular) e
 * pelo medir-dobra.mjs (medida do topo para o gate-imagens). Rodar `await page.evaluate(DETECTAR_TOPO)` cria `window.__topo()`,
 * que devolve { heroi, h1, apoio, botao, linhas }.
 */
/* O que é o topo da página, igual para todas as medidas: herói = a seção que contém o h1; botão principal = [data-cta] do herói
   ou o primeiro link ou botão com caixa DEPOIS do h1 (a marca no topo vem antes do h1 e aponta para o próprio herói: a Torra
   Clara tinha o link "Torra Clara" com caixa 0x0 e o gate antigo o media como botão do herói, passando sempre); apoio = o primeiro
   parágrafo depois do h1 com 40 letras ou mais, fora de figure e de legenda "imagem ilustrativa". */
export const DETECTAR_TOPO = `window.__topo = function () {
  const visivel = (el) => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return false; const c = el.getBoundingClientRect(); return c.width > 1 && c.height > 1; };
  const h1 = [...document.querySelectorAll('h1')].find(visivel) || null;
  const heroi = (h1 && h1.closest('section')) || document.querySelector('section') || document.body;
  const depoisDoH1 = (el) => !h1 || (h1.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING);
  const proprioTopo = (el) => { const h = (el.getAttribute('href') || '').trim(); return h === '#' || h === '/' || h === '#top' || h === '#topo' || (heroi.id && h === '#' + heroi.id); };
  const comCaixa = (el) => { const cs = getComputedStyle(el); return el.hasAttribute('data-cta') || cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) >= 1; };
  const candidatos = [...heroi.querySelectorAll('[data-cta], a, button')].filter((el) => {
    const t = (el.innerText || '').replace(/\\s+/g, ' ').trim();
    const c = el.getBoundingClientRect();
    return visivel(el) && t.length >= 4 && t.length <= 60 && c.width >= 40 && c.height >= 20 && comCaixa(el) && !proprioTopo(el) && !(h1 && el.contains(h1));
  });
  // Sem nenhum com caixa (link de texto), o primeiro link ou botão do herói depois do h1, como antes.
  const semCaixa = [...heroi.querySelectorAll('a[href], button')].find((el) => visivel(el) && !proprioTopo(el) && depoisDoH1(el)) || null;
  const botao = candidatos.find((el) => el.hasAttribute('data-cta')) || candidatos.find(depoisDoH1) || candidatos[0] || semCaixa;
  const AVISO = /imag(?:em|ens)\\s+ilustrativas?/i;
  const apoio = [...heroi.querySelectorAll('p')].find((p) => visivel(p) && depoisDoH1(p) && !p.closest('figure, figcaption') && !AVISO.test(p.textContent || '') && (p.innerText || '').trim().length >= 40) || null;
  // Caixa do TEXTO renderizado (linhas de verdade), não da caixa do elemento: span escondido no celular não conta, padding não conta.
  const linhas = (el) => { if (!el) return null; const r = document.createRange(); r.selectNodeContents(el); const rs = [...r.getClientRects()].filter((q) => q.width > 0.5 && q.height > 0.5); if (!rs.length) return null; return { top: Math.min(...rs.map((q) => q.top)), bottom: Math.max(...rs.map((q) => q.bottom)) }; };
  return { heroi, h1, apoio, botao, linhas };
};`;
