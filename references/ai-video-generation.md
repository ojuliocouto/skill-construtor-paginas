# AI Video Generation para Landing Pages

> **Duas rotas, e elas não competem.** Este arquivo cobre a rota Replicate
> (WAN 2.1), que é a barata e roda por script próprio. Para a conta assinada do
> **Higgsfield** (mais modelos, `aspect_ratio` e `resolution` como parâmetro,
> image-to-video melhor), ver **[higgsfield.md](higgsfield.md)**, e ler de lá
> as 5 regras de vídeo em página, que valem para as duas rotas:
> uma trilha = uma proporção, gerar no tamanho da caixa, seed anotado, pôster
> com hash próprio, e pôster do herói com `preload` porque ele é o elemento de LCP.

Workflow completo para gerar vídeos com IA (Replicate WAN 2.1) e embedar em páginas de alto impacto.
Aprovado em produção em um site institucional real (março/2026).

---

## Modelos disponíveis (Replicate)

| Modelo | Tipo | Endpoint | Uso |
|--------|------|----------|-----|
| `wavespeedai/wan-2.1-t2v-480p` | Text→Video | `/v1/models/{model}/predictions` | Hero background, texturas, natureza genérica |
| `wavespeedai/wan-2.1-i2v-480p` | Image→Video | `/v1/models/{model}/predictions` | Animar fotos reais do produto/local |

**Token:** `~/.claude/skills/criativo-imagem-ia/config.json` → campo `REPLICATE_API_TOKEN`

---

## Script de geração: `generate-videos.py`

```python
#!/usr/bin/env python3
import json, time, urllib.request, urllib.error, os, sys
from pathlib import Path
from datetime import datetime

TOKEN = json.load(open(Path.home()/'.claude'/'skills'/'criativo-imagem-ia'/'config.json'))['REPLICATE_API_TOKEN']
OUT   = Path('./videos')
OUT.mkdir(exist_ok=True)

HEADERS = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json',
    # NUNCA adicionar 'Prefer': 'wait', causa timeout na conexão!
}

JOBS = [
    # Text-to-Video
    {
        'id': 'hero_bg',
        'model': 't2v',
        'out': 'hero-bg.mp4',
        'prompt': '...',
        'negative_prompt': 'people, text, logo, urban, blurry',
        'aspect_ratio': '16:9',
    },
    # Image-to-Video (animar foto existente)
    {
        'id': 'product_anim',
        'model': 'i2v',
        'out': 'product-animated.mp4',
        'image_url': 'https://exemplo.com/foto.jpg',
        'prompt': 'Gentle breeze, light shifting...',
        'negative_prompt': 'people, shaking camera, blurry',
        'aspect_ratio': '16:9',
    },
]

def start_job(job):
    model_map = {
        't2v': 'wavespeedai/wan-2.1-t2v-480p',
        'i2v': 'wavespeedai/wan-2.1-i2v-480p',
    }
    model = model_map[job['model']]
    input_data = {
        'prompt': job['prompt'],
        'negative_prompt': job.get('negative_prompt', ''),
        'aspect_ratio': job.get('aspect_ratio', '16:9'),
        'fast_mode': 'Balanced',
        'sample_steps': 25,
    }
    if job['model'] == 'i2v':
        input_data['image'] = job['image_url']

    url = f'https://api.replicate.com/v1/models/{model}/predictions'
    data = json.dumps({'input': input_data}).encode()
    req = urllib.request.Request(url, data=data, headers=HEADERS, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
            pred_id = resp.get('id')
            print(f'  [{job["id"]}] Started → {pred_id}')
            return pred_id
    except Exception as e:
        print(f'  [{job["id"]}] ERROR: {e}')
        return None
```

**CRÍTICO:** `timeout=60` no `start_job()`, nunca usar `Prefer: wait` no header (fica aguardando resposta síncrona e o urllib dá timeout em 30s).

---

## Pipeline FFmpeg (otimização para web)

```bash
mkdir -p opt

for f in nome-do-video outro-video; do
  # H.264 otimizado (compatibilidade máxima)
  ffmpeg -i "${f}.mp4" \
    -c:v libx264 -crf 26 -preset slow \
    -movflags +faststart -an \
    -vf scale=1280:-2 \
    "opt/${f}.mp4" -y

  # WebM VP9 (menor tamanho em browsers modernos)
  ffmpeg -i "${f}.mp4" \
    -c:v libvpx-vp9 -crf 35 -b:v 0 -an \
    -vf scale=1280:-2 \
    "opt/${f}.webm" -y

  # Poster (frame 2s para evitar frame preto inicial)
  ffmpeg -i "${f}.mp4" \
    -ss 00:00:02 -vframes 1 \
    -vf scale=1280:-2 -q:v 3 \
    "opt/${f}-poster.jpg" -y
done
```

**Tamanhos típicos após otimização (vídeo 5s 480p):**
- `.mp4`: 400 KB: 2.2 MB
- `.webm`: 220 KB: 2.4 MB
- `-poster.jpg`: 58 KB: 204 KB

---

## HTML embed: padrões corretos

### Hero background (cobre a seção inteira)
```html
<section class="hero">
  <!-- ANTES de qualquer outro elemento -->
  <video class="hero-video-bg"
    autoplay muted loop playsinline
    preload="none"
    poster="hero-bg-poster.jpg"
    aria-hidden="true">
    <source src="hero-bg.webm" type="video/webm">
    <source src="hero-bg.mp4" type="video/mp4">
  </video>
  <!-- demais camadas (overlay, orbs, content...) -->
</section>
```

```css
.hero { position: relative; overflow: hidden; isolation: isolate; }
.hero-video-bg {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover; z-index: 0; opacity: 0.35;
}
/* overlay fica acima do video */
.hero-overlay { position: absolute; inset: 0; z-index: 2; }
/* conteúdo acima de tudo */
.hero-content { position: relative; z-index: 5; }

/* Mobile e reduced-motion: esconder vídeo (performance) */
@media (max-width: 768px) {
  .hero-video-bg { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .hero-video-bg { display: none; }
}
```

### Substituir imagem estática por vídeo (card/seção)
```html
<!-- Antes: img -->
<!-- Depois: video com mesmo tamanho -->
<video autoplay muted loop playsinline
  preload="none"
  poster="produto-poster.jpg"
  aria-label="Descrição acessível do vídeo"
  style="width:100%; height:520px; object-fit:cover; display:block;">
  <source src="produto.webm" type="video/webm">
  <source src="produto.mp4" type="video/mp4">
</video>
```

**Regras:**
- `autoplay muted loop playsinline`: obrigatório para autoplay funcionar em todos os browsers
- `preload="none"`: para vídeos abaixo do fold (não carrega até usuário chegar)
- `preload="auto"`: para o vídeo principal/hero visible (garante que carrega rápido)
- `poster`: sempre definir para evitar flash branco/preto antes do vídeo carregar
- `aria-hidden="true"` em vídeos decorativos | `aria-label` em vídeos de conteúdo
- `style="border-radius:inherit"` em vídeos dentro de containers com border-radius

---

## Prompts por tipo de negócio

### Natureza / Madeireiras / Sustentabilidade
```
# Hero forest (t2v)
Lush green pine forest in Southern Brazil, tall Pinus elliottii trees,
golden morning sunlight filtering through branches, gentle wind moving
treetops, peaceful atmosphere, cinematic wide shot, smooth camera
movement, 4K, photorealistic

# Animating product image (i2v)
Warm afternoon, gentle breeze moving outdoor plants, golden light
shifting on wooden deck surface, peaceful outdoor scene, cinematic

# Wood texture close-up (t2v)
Extreme close-up of natural wood grain texture, warm amber and brown
tones, light slowly moving across the surface revealing the grain
patterns, abstract and elegant, macro photography, smooth motion
```

### Tecnologia / SaaS / IA
```
# Dark tech bg (t2v)
Abstract dark digital landscape, flowing data streams in deep blue
and purple, neural network nodes connecting, cinematic depth of field,
smooth ambient motion, no text, no UI

# Dashboard animation (i2v)
Subtle animations appearing on dashboard, charts updating smoothly,
data flowing in, professional and clean, office ambient light
```

### Arquitetura / Imóveis / Premium
```
# Exterior shot (i2v)
Golden hour light shifting across modern facade, subtle cloud
movement in sky, trees swaying gently in background, luxury feel,
wide establishing shot

# Interior lifestyle (i2v)
Afternoon sunlight slowly moving across modern living room,
subtle dust particles floating, serene and luxurious atmosphere,
cinematic color grade
```

### Alimentos / Restaurantes
```
# Food product (i2v)
Steam rising gently from fresh dish, warm kitchen lighting,
bokeh background, appetizing and inviting, slow smooth camera
```

### Negative prompts universais (reutilizar)
```
people, text, logo, watermark, blurry, low quality, shaking camera,
ugly, distorted, pixelated, noise artifacts
```

---

## Checklist de integração

### Pré-geração
- [ ] Definir quais seções ganham vídeo (máx 3 por página para não pesar)
- [ ] Escolher modelo certo: **i2v** se tem foto real; **t2v** se precisa criar do zero
- [ ] Coletar URLs das imagens originais (para i2v): devem ser públicas
- [ ] Escrever prompts específicos para o nicho

### Pós-geração
- [ ] Otimizar com FFmpeg (H.264 + WebM + poster)
- [ ] Verificar tamanhos: hero-bg < 2MB, outros < 1MB cada
- [ ] Copiar arquivos para a pasta da landing page
- [ ] Embedar HTML com `preload="none"` (abaixo do fold) ou `preload="auto"` (hero)
- [ ] Testar em mobile: deve mostrar apenas o poster (vídeo oculto)
- [ ] Testar `prefers-reduced-motion`: vídeo deve ser oculto
- [ ] Verificar que conteúdo sobre o vídeo está com `z-index` correto

### Deploy
- [ ] Incluir .mp4, .webm e -poster.jpg no deploy
- [ ] Verificar que arquivos foram carregados: `curl -sL URL | grep "nome-video"`

---

## Custos estimados (Replicate)

| Modelo | Custo por vídeo (5s, 480p) | Observação |
|--------|---------------------------|------------|
| `wan-2.1-t2v-480p` | ~$0.08: 0.15 | Depende do tempo de GPU |
| `wan-2.1-i2v-480p` | ~$0.06: 0.12 | Ligeiramente mais rápido |

**4 vídeos por landing page:** ~$0.30, 0.50 (custo irrelevante dado o impacto visual)

---

## Anti-patterns

- **NUNCA `Prefer: wait` no header**: provoca timeout em 30s; usar polling assíncrono
- **NUNCA vídeo sem poster**: flash preto/branco arruína a first impression
- **NUNCA autoplay sem muted**: browsers bloqueiam autoplay com som
- **NUNCA `preload="auto"` em todos os vídeos**: carrega tudo de uma vez, LCP piora
- **NUNCA vídeo em mobile sem esconder**: consome dados, quebra experience em 3G/4G
- **NUNCA opacity > 0.5 em hero background**: o vídeo domina e dificulta leitura do texto
- **NUNCA omitir `playsinline`**: iOS abre em fullscreen sem ele

---

## Vídeos longos: Encadeamento com xfade (FFmpeg)

WAN 2.1 gera clips de ~5.3s. Para looping de 10s, gerar 2 clips e encadear:

```bash
# OBRIGATORIO: normalizar resolução e fps dos clips antes do xfade
# offset = duração_do_clip_A - duração_do_fade (ex: 5.366 - 1.0 = 4.366)

ffmpeg -i clip-a.mp4 -i clip-b.mp4 \
  -filter_complex "
    [0:v]scale=1280:720,fps=30[v0];
    [1:v]scale=1280:720,fps=30[v1];
    [v0][v1]xfade=transition=fade:duration=1:offset=4.366[vout]
  " \
  -map "[vout]" -c:v libx264 -crf 24 -preset slow \
  -movflags +faststart -an \
  video-final.mp4 -y
```

**Por que normalizar com `scale` e `fps` antes do xfade:**
- Se os clips tiverem resolução/fps diferentes o xfade falha com "Invalid argument"
- Sempre usar `scale=1280:720,fps=30` em ambos os inputs como pré-filtro

**Resultado:** clip de ~9.7s com crossfade fade suave de 1s no meio.

---

## Vídeos de fundo para seções sólidas

Para seções com `background: cor-sólida` (ex: verde, preto), adicionar video background com `opacity: 0.07`.

```html
<!-- Dentro da section, ANTES do conteúdo -->
<video class="section-video-bg lazy-video"
  autoplay muted loop playsinline preload="none"
  poster="ambient-poster.jpg" aria-hidden="true">
  <source data-src="ambient.webm" type="video/webm">
  <source data-src="ambient.mp4" type="video/mp4">
</video>
```

```css
.section-video-bg {
  position: absolute; inset: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  z-index: 0; opacity: 0.07;
  pointer-events: none;
}
/* Seção precisa de position:relative + isolation */
.stats-section, .processo-section, .cta-section { isolation: isolate; }
/* Conteúdo da seção deve ter z-index > 0 */
.stats-inner, .processo-inner, .cta-inner { position: relative; z-index: 1; }
```

**Opacidade por tipo de seção:**
- Fundo escuro (verde, preto) → `opacity: 0.07-0.10`
- Fundo claro (branco, creme) → `opacity: 0.04-0.06`
- Nunca ultrapassar 0.15 → domina e prejudica legibilidade

---

## Lazy load obrigatório para vídeos abaixo do fold

```html
<!-- Script antes de </body> -->
<script>(function(){
  if(window.matchMedia('(max-width:767px)').matches) return;
  if(!('IntersectionObserver' in window)) return;
  var obs = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      if(!e.isIntersecting) return;
      var v = e.target;
      v.querySelectorAll('source[data-src]').forEach(function(s){
        if(!s.src){ s.src = s.dataset.src; }
      });
      v.load();
      v.play().catch(function(){});
      obs.unobserve(v);
    });
  }, { rootMargin: '300px 0px' });
  document.querySelectorAll('video.lazy-video').forEach(function(v){ obs.observe(v); });
})();</script>
```

**Regra:** vídeo acima do fold = `src` direto + `preload="auto"`. Vídeo abaixo do fold = `data-src` + classe `.lazy-video` + `preload="none"`.
