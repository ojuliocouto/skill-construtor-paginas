// Cópia do script de "texto linha a linha" da v7 (pagina-studio-v7/_app.js:118-147), sem mudança de lógica.
// Única troca: o seletor do item da lista, '.dor-lista li', virou '[data-escada] > *' (nome neutro).
// Defeito medido (06/10/2026, v7 no ar, 1440 px): o script divide ANTES da fonte da página chegar e
// nunca mede de novo, então um trecho gerado pode quebrar em duas linhas ("porque" sozinho).
// Usado só por scripts/test-linhas.cjs, para provar que o teste fica vermelho com este código.
(function () {
  var reduz = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var linhasOriginais = [];
  function dividirLinhas() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-linhas]'), function (n, k) {
      if (linhasOriginais[k] === undefined) linhasOriginais[k] = n.textContent.trim();
      var texto = linhasOriginais[k];
      n.classList.remove('dividido');
      n.textContent = '';
      var palavras = texto.split(/\s+/), spans = [];
      palavras.forEach(function (w, i) { var sp = document.createElement('span'); sp.textContent = w; n.appendChild(sp); spans.push(sp); if (i < palavras.length - 1) n.appendChild(document.createTextNode(' ')); });
      var grupos = [], topo = null;
      spans.forEach(function (sp) { var t = sp.offsetTop; if (topo === null || Math.abs(t - topo) > 4) { grupos.push([]); topo = t; } grupos[grupos.length - 1].push(sp.textContent); });
      n.textContent = '';
      var item = n.closest('[data-escada] > *'), base = item ? Array.prototype.indexOf.call(item.parentNode.children, item) * 0.45 : 0;
      grupos.forEach(function (g, i) {
        var l = document.createElement('span'); l.className = 'linha';
        l.textContent = g.join(' '); l.style.setProperty('--d', (base + i * 0.14) + 's');
        n.appendChild(l); if (i < grupos.length - 1) n.appendChild(document.createTextNode(' '));
      });
      n.classList.add('dividido');
    });
  }
  if (!reduz) {
    dividirLinhas();
    var larguraAnterior = window.innerWidth, tempo;
    window.addEventListener('resize', function () {
      if (window.innerWidth === larguraAnterior) return;
      larguraAnterior = window.innerWidth; clearTimeout(tempo);
      tempo = setTimeout(function () { var vis = Array.prototype.map.call(document.querySelectorAll('[data-linhas]'), function (n) { return n.classList.contains('visivel'); }); dividirLinhas(); Array.prototype.forEach.call(document.querySelectorAll('[data-linhas]'), function (n, i) { if (vis[i]) n.classList.add('visivel'); }); }, 150);
    });
  }
})();
