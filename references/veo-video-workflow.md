# Veo Video Workflow: Geração + Compressão + Embed

Workflow completo para gerar vídeos com Veo 2/3 (Gemini), otimizar para web e embedar em páginas de alta performance.

---

## Quando Usar Vídeo

| Situação | Usar? | Alternativa |
|----------|-------|-------------|
| Hero background (dark page) | ✅ SIM: impacto enorme | FloatingOrbs CSS |
| Hero background (light page) | ⚠️ Seletivo: olhar LCP | Gradiente animado |
| Feature showcase | ✅ SIM: melhor que screenshot | Safari mockup estático |
| Seção de CTA | ✅ SIM: vídeo curto de produto | Imagem estática |
| Mobile | ❌ NUNCA: custo de dados | Poster WebP estático |
| Background de texto longo | ❌: prejudica leitura | Noise texture |

**Regra de ouro:** Vídeo no hero = LCP em risco. Medir sempre com `preload="none"` + poster rápido.

---

## Setup: API Key

```bash
# Mesma variável do nanobanana, já configurada
echo $GEMINI_API_KEY

# Se não estiver disponível, verificar:
cat ~/.claude/skills/nanobanana/config.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('GEMINI_API_KEY',''))"
```

---

## Script de Geração: Veo 2

```python
#!/usr/bin/env python3
"""
Script: generate-veo.py
Uso: python3 generate-veo.py "prompt do vídeo" --aspect 16:9 --duration 5
"""

import os
import sys
import time
import json
import base64
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

def get_api_key():
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        config_path = Path.home() / '.claude' / 'skills' / 'nanobanana' / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                key = json.load(f).get('GEMINI_API_KEY')
    if not key:
        raise ValueError("GEMINI_API_KEY não encontrada")
    return key

def generate_video(prompt: str, aspect_ratio: str = '16:9', duration: int = 5, model: str = 'veo-2.0-generate-001') -> Path:
    api_key = get_api_key()

    # Verificar modelos disponíveis:
    # - veo-2.0-generate-001: disponível, gratuito (limite de uso)
    # - veo-3.0-generate-preview: preview, pode estar restrito

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo?key={api_key}"

    payload = json.dumps({
        "prompt": {"text": prompt},
        "videoConfig": {
            "durationSeconds": duration,
            "aspectRatio": aspect_ratio,  # "16:9", "9:16", "1:1"
            "numberOfVideos": 1,
        }
    }).encode()

    req = urllib.request.Request(url, data=payload, method='POST')
    req.add_header('Content-Type', 'application/json')

    print(f"Iniciando geração: '{prompt[:60]}...'")
    print(f"Modelo: {model} | Aspect: {aspect_ratio} | Duração: {duration}s")

    try:
        with urllib.request.urlopen(req) as response:
            operation = json.loads(response.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"API Error {e.code}: {error_body}")

    operation_name = operation.get('name')
    print(f"Operation: {operation_name}")

    # Polling até completar
    poll_url = f"https://generativelanguage.googleapis.com/v1beta/{operation_name}?key={api_key}"

    for attempt in range(60):  # timeout: 5 minutos
        time.sleep(5)

        req_poll = urllib.request.Request(poll_url)
        with urllib.request.urlopen(req_poll) as resp:
            status = json.loads(resp.read())

        if status.get('done'):
            break

        if attempt % 6 == 0:
            print(f"Aguardando... {(attempt+1)*5}s")
    else:
        raise TimeoutError("Timeout após 5 minutos")

    # Extrair vídeo
    response_data = status.get('response', {})
    candidates = response_data.get('generatedSamples', [])

    if not candidates:
        raise ValueError(f"Sem resultado. Status: {json.dumps(status, indent=2)}")

    video_b64 = candidates[0].get('video', {}).get('videoData')
    mime_type = candidates[0].get('video', {}).get('mimeType', 'video/mp4')

    # Salvar
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    ext = 'mp4' if 'mp4' in mime_type else 'mp4'
    output_path = Path(f'/tmp/veo-{timestamp}.{ext}')

    with open(output_path, 'wb') as f:
        f.write(base64.b64decode(video_b64))

    print(f"✅ Vídeo salvo: {output_path}")
    print(f"   Tamanho bruto: {output_path.stat().st_size / 1024 / 1024:.1f}MB")
    return output_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', nargs='?', default="Abstract dark tech neural network, flowing purple light streams, cinematic, 4K")
    parser.add_argument('--aspect', default='16:9', choices=['16:9', '9:16', '1:1'])
    parser.add_argument('--duration', type=int, default=5, choices=[5, 8])
    parser.add_argument('--model', default='veo-2.0-generate-001')
    args = parser.parse_args()

    path = generate_video(args.prompt, args.aspect, args.duration, args.model)
    print(f"\nPróximo passo: python3 optimize-veo.py '{path}'")
```

---

## Script de Otimização: ffmpeg Pipeline

```bash
#!/bin/bash
# Script: optimize-veo.sh
# Uso: bash optimize-veo.sh /tmp/veo-20260307-123456.mp4 [output-name]

INPUT="$1"
NAME="${2:-hero-video}"
OUTPUT_DIR="$(dirname "$INPUT")"

if [ -z "$INPUT" ]; then
  echo "Uso: bash optimize-veo.sh <input.mp4> [nome-base]"
  exit 1
fi

echo "=== Otimizando: $INPUT ==="

# MP4, H.264, para máxima compatibilidade
echo "→ Gerando MP4..."
ffmpeg -i "$INPUT" \
  -vf "scale=1280:-2" \
  -c:v libx264 \
  -crf 28 \
  -preset slow \
  -profile:v main \
  -movflags +faststart \
  -an \
  -y "$OUTPUT_DIR/${NAME}.mp4" 2>/dev/null

MP4_SIZE=$(du -sh "$OUTPUT_DIR/${NAME}.mp4" | cut -f1)
echo "   MP4: $MP4_SIZE"

# WebM, VP9, melhor compressão para Chrome/Firefox
echo "→ Gerando WebM..."
ffmpeg -i "$OUTPUT_DIR/${NAME}.mp4" \
  -c:v libvpx-vp9 \
  -crf 35 \
  -b:v 0 \
  -deadline good \
  -cpu-used 2 \
  -an \
  -y "$OUTPUT_DIR/${NAME}.webm" 2>/dev/null

WEBM_SIZE=$(du -sh "$OUTPUT_DIR/${NAME}.webm" | cut -f1)
echo "   WebM: $WEBM_SIZE"

# Poster WebP, frame do meio do vídeo
echo "→ Gerando poster WebP..."
DURATION=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$INPUT" 2>/dev/null)
MID=$(echo "$DURATION / 2" | bc -l 2>/dev/null || echo "2")

ffmpeg -ss "$MID" -i "$INPUT" \
  -vframes 1 \
  -f image2 \
  -y "/tmp/poster-raw.jpg" 2>/dev/null

if command -v cwebp &>/dev/null; then
  cwebp -q 82 "/tmp/poster-raw.jpg" -o "$OUTPUT_DIR/${NAME}-poster.webp" 2>/dev/null
  POSTER_SIZE=$(du -sh "$OUTPUT_DIR/${NAME}-poster.webp" | cut -f1)
  echo "   Poster WebP: $POSTER_SIZE"
else
  ffmpeg -ss "$MID" -i "$INPUT" \
    -vframes 1 \
    -vf "scale=1280:-2" \
    -y "$OUTPUT_DIR/${NAME}-poster.jpg" 2>/dev/null
  echo "   Poster JPG (instalar cwebp para WebP)"
fi

echo ""
echo "✅ Arquivos gerados em: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR/${NAME}"*
echo ""
echo "Copiar para o projeto:"
echo "  cp $OUTPUT_DIR/${NAME}.mp4 public/videos/"
echo "  cp $OUTPUT_DIR/${NAME}.webm public/videos/"
echo "  cp $OUTPUT_DIR/${NAME}-poster.webp public/videos/"
```

```python
# Versão Python (cross-platform, sem bash)
# Script: optimize-veo.py
# Uso: python3 optimize-veo.py /tmp/veo-xxx.mp4 hero-video

import subprocess
import sys
from pathlib import Path

def optimize_video(input_path: str, output_name: str = 'hero-video') -> dict:
    inp = Path(input_path)
    out_dir = inp.parent

    results = {}

    # MP4 H.264
    mp4_out = out_dir / f"{output_name}.mp4"
    subprocess.run([
        'ffmpeg', '-i', str(inp),
        '-vf', 'scale=1280:-2',
        '-c:v', 'libx264',
        '-crf', '28',
        '-preset', 'slow',
        '-profile:v', 'main',
        '-movflags', '+faststart',
        '-an',
        '-y', str(mp4_out)
    ], capture_output=True)
    results['mp4'] = mp4_out
    print(f"✅ MP4: {mp4_out.stat().st_size / 1024:.0f}KB")

    # WebM VP9
    webm_out = out_dir / f"{output_name}.webm"
    subprocess.run([
        'ffmpeg', '-i', str(mp4_out),
        '-c:v', 'libvpx-vp9',
        '-crf', '35',
        '-b:v', '0',
        '-deadline', 'good',
        '-cpu-used', '2',
        '-an',
        '-y', str(webm_out)
    ], capture_output=True)
    results['webm'] = webm_out
    print(f"✅ WebM: {webm_out.stat().st_size / 1024:.0f}KB")

    # Poster WebP
    poster_out = out_dir / f"{output_name}-poster.webp"
    subprocess.run([
        'ffmpeg', '-ss', '2', '-i', str(inp),
        '-vframes', '1',
        '-f', 'image2',
        '-y', '/tmp/poster-raw.jpg'
    ], capture_output=True)
    subprocess.run(['cwebp', '-q', '82', '/tmp/poster-raw.jpg', '-o', str(poster_out)],
                   capture_output=True)
    results['poster'] = poster_out
    print(f"✅ Poster: {poster_out.stat().st_size / 1024:.0f}KB")

    return results

if __name__ == '__main__':
    input_path = sys.argv[1] if len(sys.argv) > 1 else None
    output_name = sys.argv[2] if len(sys.argv) > 2 else 'hero-video'

    if not input_path:
        print("Uso: python3 optimize-veo.py <input.mp4> [nome-base]")
        sys.exit(1)

    files = optimize_video(input_path, output_name)
    print(f"\nArquivos em: {Path(files['mp4']).parent}")
```

---

## Embed Correto na Página

### HTML puro

```html
<!-- CORRETO: WebM primeiro (melhor compressão), MP4 fallback, poster, sem audio -->
<video
  autoplay
  muted
  loop
  playsinline
  preload="none"
  poster="videos/hero-poster.webp"
  class="absolute inset-0 w-full h-full object-cover"
  aria-hidden="true"
>
  <source src="videos/hero-video.webm" type="video/webm">
  <source src="videos/hero-video.mp4" type="video/mp4">
</video>
```

### React / TSX

```tsx
interface HeroBgVideoProps {
  webmSrc: string
  mp4Src: string
  posterSrc: string
  className?: string
  objectPosition?: string
}

function HeroBgVideo({
  webmSrc,
  mp4Src,
  posterSrc,
  className = '',
  objectPosition = 'center'
}: HeroBgVideoProps) {
  return (
    <video
      autoPlay
      muted
      loop
      playsInline
      preload="none"
      poster={posterSrc}
      aria-hidden="true"
      className={`absolute inset-0 w-full h-full object-cover ${className}`}
      style={{ objectPosition }}
    >
      <source src={webmSrc} type="video/webm" />
      <source src={mp4Src} type="video/mp4" />
    </video>
  )
}

// Uso no hero:
function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden bg-slate-950">
      {/* Vídeo de background, esconder no mobile */}
      <div className="hidden md:block absolute inset-0">
        <HeroBgVideo
          webmSrc="/videos/hero-video.webm"
          mp4Src="/videos/hero-video.mp4"
          posterSrc="/videos/hero-poster.webp"
        />
        {/* Overlay para garantir legibilidade do texto */}
        <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm" />
      </div>

      {/* Conteúdo */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-32">
        <h1>Headline aqui</h1>
      </div>
    </section>
  )
}
```

---

## CSS Obrigatório para Mobile

```css
/* globals.css, SEMPRE incluir */
@media (max-width: 768px) {
  video.bg-video,
  video[aria-hidden="true"],
  .hero-video {
    display: none !important;
  }
}

/* Reduced motion, desabilitar autoplay */
@media (prefers-reduced-motion: reduce) {
  video {
    display: none !important;
  }
}
```

---

## Prompts Efetivos para Veo 2

### Background de Hero (dark tech)
```
Abstract dark technology background, neural network visualization, flowing purple and indigo light
particles through a deep space environment, ultra smooth 4K cinematic motion, no text, no faces,
loopable, subtle and atmospheric, professional corporate aesthetic
```

### Background de Hero (business/growth)
```
Abstract financial data visualization, blue and white light streams, clean minimal motion, dark
navy background, flowing upward growth lines, corporate tech aesthetic, seamless loop, 4K,
no faces, no text
```

### Produto SaaS (dashboard animado)
```
Modern SaaS dashboard interface animation, dark glassmorphism design, data visualizations
updating in real time, purple accent colors, smooth transitions, professional software UI,
top-down perspective, 4K resolution
```

### WhatsApp / Automação
```
WhatsApp conversation bubbles flowing smoothly, green message bubbles on dark background,
automated responses appearing in sequence, clean minimal aesthetic, top-down view, no faces,
smooth animation, 4K
```

### Energia / Motivação (desafios)
```
Dynamic energy particles exploding from center, orange and amber fire colors on black background,
epic cinematic motion, dramatic atmosphere, loopable, 4K, no faces, no text, abstract powerful
visualization
```

### Workflow / Automação abstrata
```
Abstract workflow automation visualization, connected nodes and flowing data streams, purple and
blue gradient colors, dark background, smooth particle motion, loopable, 4K, no people
```

---

## Checklist de Vídeo

```
Antes de gerar:
[ ] Definir onde o vídeo será usado (hero, feature, CTA)
[ ] Definir aspect ratio (16:9 desktop, 9:16 stories/vertical)
[ ] Prompt com: tema + cores + atmosfera + "no faces, no text, loopable, 4K"

Após gerar:
[ ] Rodar optimize-veo.sh, MP4 + WebM + Poster
[ ] MP4 < 2MB por vídeo (máx 3MB se necessário)
[ ] WebM ~30-40% menor que MP4
[ ] Poster WebP < 80KB

No código:
[ ] preload="none" NO HTML (não bloqueia LCP)
[ ] poster= aponta para WebP do frame
[ ] muted + autoplay + loop + playsinline, todos 4 obrigatórios
[ ] aria-hidden="true" (vídeo decorativo, não informativo)
[ ] display:none no mobile (CSS media query)
[ ] Overlay de gradiente/blur sobre o vídeo (texto precisa ser legível)
[ ] Fallback visual (background color/gradient quando vídeo não carrega)
[ ] Testar LCP com video, deve ser < 2.5s
```

---

## Targets de Performance

| Arquivo | Target | Máximo aceitável |
|---------|--------|-----------------|
| MP4 hero (16:9, 5s) | < 1.5MB | 3MB |
| WebM hero | < 1MB | 2MB |
| Poster WebP | < 80KB | 150KB |
| MP4 feature (looping curto) | < 500KB | 1MB |

---

## Fallback quando Veo não está disponível

```tsx
// Usar FloatingOrbs + AuroraBackground como fallback visual equivalente
// Veja: references/efeitos-avancados.md#9-aurora-background

// Ou vídeo stock do Pexels:
// python3 ~/.claude/skills/construtor-paginas/scripts/assets-search.py "dark tech abstract" --type video
```

---

## Notas sobre Modelos

| Modelo | Status | Qualidade | Disponibilidade |
|--------|--------|-----------|-----------------|
| `veo-2.0-generate-001` | ✅ Disponível | Alta | API pública com limites |
| `veo-3.0-generate-preview` | ⚠️ Preview | Muito alta | Pode estar restrito: testar primeiro |

Para verificar modelos disponíveis:
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" \
  | python3 -c "import json,sys; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'veo' in m['name'].lower()]"
```
