#!/usr/bin/env python3
"""Cliente do Higgsfield para assets de página.

POR QUE ELE EXISTE, e não só o documento: `references/higgsfield.md` descreve as
regras, mas regra que depende de alguém lembrar de aplicar não se aplica. Aqui as
três que mais custaram caro viram código:

  - o MANIFESTO grava seed, prompt, modelo e proporção de cada clipe. Sem isso,
    regenerar "o mesmo clipe" devolve outro e a página muda sem ninguém pedir;
  - o nome do arquivo carrega HASH DO CONTEÚDO, porque o edge do Cloudflare
    cacheia por caminho e arquivo com nome igual e bytes novos continua servindo
    o velho;
  - o pôster tem HASH PRÓPRIO, nunca derivado do mp4. Derivar foi o que levou
    seis pôsteres a 404 num projeto real quando os vídeos foram reencodados.

Higgsfield é OPCIONAL: requer conta própria (cloud.higgsfield.ai) e plano
pago. Sem conta, use a rota via Replicate em references/ai-video-generation.md.

USO
    export HF_API_KEY_ID=...       # sua key ID, nunca commitar
    export HF_API_KEY_SECRET=...   # seu secret, nunca commitar

    # ver a requisição sem gastar crédito
    python3 higgsfield.py --dry-run --prompt "..." --preset "slow push in"

    # gerar de verdade, com a lista toda de uma vez (crédito não faz rollover)
    python3 higgsfield.py --lote lote.json --saida ./public/assets/v

AUTENTICAÇÃO
    Authorization: Key <KEY_ID>:<KEY_SECRET>     (formato novo)
    hf-api-key / hf-secret                       (legado, ainda aceito)
    O par se cria em cloud.higgsfield.ai. Server-side sempre.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE = "https://platform.higgsfield.ai"

# Endpoints que interessam pra página. O DoP é o diferencial (image-to-video com
# preset de câmera); os outros entram quando não há keyframe de onde partir.
ENDPOINTS = {
    "dop": "/higgsfield-ai/dop",
    "veo-i2v": "/veo3.1/image-to-video",
    "veo-t2v": "/veo3.1",
    "veo-t2v-fast": "/veo3.1/fast",
    "kling-t2v": "/kling-video/v2.5-turbo/pro/text-to-video",
    "seedance-i2v": "/bytedance/seedance/v1/lite/image-to-video",
}

# Presets do DoP que servem pra FUNDO DE SEÇÃO: contínuos, sem clímax. Ver a
# seção 9 do references/higgsfield.md. Preset com clímax rouba a leitura do texto.
PRESETS_WEB = ["slow push in", "slow push out", "slow orbit", "lateral drift", "subtle parallax"]

# Negativos que valem pra qualquer asset de página. Texto gerado por IA dentro do
# vídeo é o carimbo mais rápido de "isso é IA", e ainda briga com a tipografia real.
NEG_PADRAO = (
    "text, letters, typography, watermark, logo, subtitles, "
    "fast motion, hard cuts, flashing, morphing, distorted faces, extra limbs"
)


def cabecalhos() -> dict:
    kid = os.environ.get("HF_API_KEY_ID")
    ksec = os.environ.get("HF_API_KEY_SECRET")
    if not kid or not ksec:
        sys.exit(
            "faltam HF_API_KEY_ID e HF_API_KEY_SECRET no ambiente.\n"
            "Higgsfield e opcional e requer conta propria:\n"
            "  1. crie uma conta em cloud.higgsfield.ai\n"
            "  2. escolha um plano pago (o gratuito nao libera uso comercial)\n"
            "  3. gere o par de credenciais no painel da conta\n"
            "  4. exporte: export HF_API_KEY_ID=... e export HF_API_KEY_SECRET=...\n"
            "Nunca commitar a chave no repositorio.\n"
            "Sem conta propria, use a rota via Replicate em references/ai-video-generation.md."
        )
    return {"Authorization": f"Key {kid}:{ksec}", "Content-Type": "application/json"}


def monta_corpo(a: argparse.Namespace) -> dict:
    """Monta o body. `aspect_ratio` e `resolution` são obrigatórios de propósito:
    são exatamente os dois parâmetros que evitam, na origem, o clipe cortado e o
    arquivo maior que a caixa."""
    corpo = {
        "prompt": a.prompt,
        "aspect_ratio": a.aspect,
        "resolution": a.resolution,
        "duration": a.duration,
        "negative_prompt": a.negative or NEG_PADRAO,
    }
    if a.seed:
        corpo["seed"] = a.seed
    if a.image_url:
        corpo["image_url"] = a.image_url
    if a.preset:
        # o preset entra no campo E é repetido no texto: fazer os dois é o que dá
        # resultado repetível (ver seção 9 do reference)
        corpo["preset"] = a.preset
        if a.preset.lower() not in corpo["prompt"].lower():
            corpo["prompt"] = f"{corpo['prompt']}. {a.preset}"
    if a.image_url and "preserve the original" not in corpo["prompt"].lower():
        # sem esta linha o modelo redesenha a cena em vez de só mover a câmera
        corpo["prompt"] += ". Preserve the original face, lighting and geometry"
    return corpo


def pede(url: str, corpo: dict | None, headers: dict, metodo: str = "POST"):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(url, data=dados, headers=headers, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo_erro = e.read().decode()[:400]
        return e.code, {"erro": corpo_erro}
    except Exception as e:  # rede caiu, DNS, timeout
        return 0, {"erro": str(e)}


def espera(request_id: str, headers: dict, limite_s: int = 900) -> dict:
    """Polling com backoff. UM retry só e cache antes de qualquer segunda tentativa:
    o Higgsfield tem histórico de bloqueio."""
    espera_s, gasto = 3, 0
    while gasto < limite_s:
        status, corpo = pede(f"{BASE}/requests/{request_id}/status", None, headers, "GET")
        if status == 0:
            return {"estado": "erro_de_rede", **corpo}
        estado = str(corpo.get("status") or corpo.get("state") or "").lower()
        if estado in ("completed", "succeeded", "success", "done"):
            return {"estado": "pronto", **corpo}
        if estado in ("failed", "error", "canceled", "cancelled"):
            return {"estado": "falhou", **corpo}
        time.sleep(espera_s)
        gasto += espera_s
        espera_s = min(espera_s * 1.5, 20)
    return {"estado": "estourou_o_tempo", "request_id": request_id}


def hash_conteudo(caminho: str, n: int = 8) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()[:n]


def baixa_e_nomeia(url: str, saida: str, base: str) -> tuple[str, str]:
    """Baixa, renomeia com o hash do CONTEÚDO e extrai um pôster com hash PRÓPRIO.
    Dois arquivos, dois hashes, dois ciclos de vida."""
    os.makedirs(saida, exist_ok=True)
    tmp = os.path.join(saida, f".{base}.tmp.mp4")
    urllib.request.urlretrieve(url, tmp)

    hv = hash_conteudo(tmp)
    mp4 = os.path.join(saida, f"{base}.{hv}.mp4")
    os.replace(tmp, mp4)

    # pôster do primeiro quadro, hash calculado sobre ELE, não sobre o mp4.
    # ffmpeg ausente NAO pode travar aqui: o credito do clipe ja foi gasto no
    # download acima, entao a falta do ffmpeg so pula o poster e nunca impede
    # o manifesto de ser gravado.
    ptmp = os.path.join(saida, f".{base}.tmp.webp")
    poster = ""
    if not shutil.which("ffmpeg"):
        print("  aviso: ffmpeg nao encontrado no PATH, pulando geracao de poster (mp4 e manifesto seguem normalmente)")
    else:
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-frames:v", "1", "-q:v", "80", ptmp],
                check=False,
            )
        except OSError as e:
            print(f"  aviso: falha ao rodar ffmpeg para o poster ({e}), pulando poster")
        if os.path.exists(ptmp):
            hp = hash_conteudo(ptmp)
            poster = os.path.join(saida, f"{base}.{hp}.webp")
            os.replace(ptmp, poster)
    return mp4, poster


def anota(saida: str, registro: dict) -> None:
    """Manifesto. É ele que torna a regeneração reproduzível."""
    caminho = os.path.join(saida, "_higgsfield.json")
    dados = []
    if os.path.exists(caminho):
        try:
            dados = json.load(open(caminho, encoding="utf-8"))
        except Exception:
            dados = []
    dados.append(registro)
    json.dump(dados, open(caminho, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def uma(a: argparse.Namespace, headers: dict | None) -> dict:
    corpo = monta_corpo(a)
    endpoint = ENDPOINTS.get(a.modelo, a.modelo)
    url = BASE + endpoint

    if a.dry_run:
        print(f"POST {url}")
        print("headers: Authorization: Key <KEY_ID>:<KEY_SECRET>")
        print(json.dumps(corpo, ensure_ascii=True, indent=1))
        if a.preset and a.preset not in PRESETS_WEB:
            print(f"\nAVISO: '{a.preset}' nao esta na lista de presets de FUNDO DE SECAO.")
            print(f"       preset com climax rouba a leitura do texto. seguros: {', '.join(PRESETS_WEB)}")
        return {"dry_run": True, "url": url, "corpo": corpo}

    status, resp = pede(url, corpo, headers)
    if status not in (200, 201, 202):
        return {"estado": "recusado", "http": status, **resp}
    rid = resp.get("request_id") or resp.get("id")
    if not rid:
        return {"estado": "sem_request_id", "resposta": resp}
    print(f"  submetido: {rid}")

    fim = espera(rid, headers)
    if fim.get("estado") != "pronto":
        return {"estado": fim.get("estado"), "request_id": rid, "detalhe": fim}

    url_out = fim.get("url") or (fim.get("result") or {}).get("url") or fim.get("output")
    if not url_out:
        return {"estado": "sem_url_de_saida", "request_id": rid, "resposta": fim}

    mp4, poster = baixa_e_nomeia(url_out, a.saida, a.nome or "hf")
    reg = {
        "nome": a.nome, "request_id": rid, "modelo": a.modelo, "endpoint": endpoint,
        "prompt": corpo["prompt"], "negative_prompt": corpo["negative_prompt"],
        "seed": corpo.get("seed"), "preset": a.preset,
        "aspect_ratio": a.aspect, "resolution": a.resolution, "duration": a.duration,
        "mp4": os.path.basename(mp4), "poster": os.path.basename(poster),
        "creditos": fim.get("credits") or fim.get("cost"),
    }
    anota(a.saida, reg)
    print(f"  ok: {os.path.basename(mp4)}  poster {os.path.basename(poster)}")
    return {"estado": "pronto", **reg}


def main() -> int:
    p = argparse.ArgumentParser(description="Cliente Higgsfield para assets de pagina")
    p.add_argument("--prompt")
    p.add_argument("--modelo", default="dop", help=f"atalho ou path. atalhos: {', '.join(ENDPOINTS)}")
    p.add_argument("--preset", help=f"preset de camera do DoP. seguros pra fundo: {', '.join(PRESETS_WEB)}")
    p.add_argument("--image-url", help="keyframe pra image-to-video")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--resolution", default="1080")
    p.add_argument("--duration", type=int, default=5)
    p.add_argument("--seed", type=int)
    p.add_argument("--negative")
    p.add_argument("--nome", default="hf", help="base do nome do arquivo")
    p.add_argument("--saida", default="./assets")
    p.add_argument("--lote", help="JSON com uma lista de jobs: gera tudo de uma vez")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    headers = None if a.dry_run else cabecalhos()

    if a.lote:
        try:
            jobs = json.load(open(a.lote, encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"arquivo de lote nao encontrado: {a.lote}")
        except json.JSONDecodeError as e:
            sys.exit(f"JSON invalido em {a.lote}: {e}")
        # leva de uma vez porque credito nao faz rollover: o que sobra no ciclo morre
        print(f"leva de {len(jobs)} clipe(s)")
        razoes = {j.get("aspect", a.aspect) for j in jobs}
        if len(razoes) > 1:
            print(f"AVISO: a leva tem {len(razoes)} proporcoes ({', '.join(sorted(razoes))}).")
            print("       uma trilha = UMA proporcao, senao o `cover` corta o que nao bate.")
        saida = []
        for j in jobs:
            sub = argparse.Namespace(**{**vars(a), **j, "lote": None})
            print(f"- {sub.nome}")
            saida.append(uma(sub, headers))
        ruins = [s for s in saida if s.get("estado") not in ("pronto", None) and not s.get("dry_run")]
        print(f"\nconcluido: {len(saida) - len(ruins)}/{len(saida)}")
        return 1 if ruins else 0

    if not a.prompt:
        p.error("--prompt e obrigatorio quando nao se usa --lote")
    r = uma(a, headers)
    return 0 if r.get("estado") in ("pronto",) or r.get("dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())
