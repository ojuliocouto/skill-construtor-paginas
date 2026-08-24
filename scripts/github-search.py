#!/usr/bin/env python3
"""
Busca templates, landing pages e componentes no GitHub.
Usa a API do GitHub via `gh` CLI.

Uso:
  python3 github-search.py "landing page tailwind" [--type repos|code] [--lang html|tsx|vue] [-n 10] [--stars 50] [--sort stars|updated]
  python3 github-search.py "saas template nextjs" --type repos --stars 100 --sort stars
  python3 github-search.py "hero section component" --type code --lang tsx
"""

import subprocess
import json
import argparse
import sys


def search_repos(query: str, lang: str = None, min_stars: int = 10, limit: int = 10, sort: str = "stars"):
    """Busca repositorios no GitHub."""
    search_query = query
    if lang:
        search_query += f" language:{lang}"
    if min_stars > 0:
        search_query += f" stars:>={min_stars}"

    cmd = [
        "gh", "api", "search/repositories",
        "-X", "GET",
        "-f", f"q={search_query}",
        "-f", f"sort={sort}",
        "-f", "order=desc",
        "-f", f"per_page={limit}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Erro ao buscar: {result.stderr.strip()}", file=sys.stderr)
            return []
        data = json.loads(result.stdout)
        return data.get("items", [])
    except FileNotFoundError:
        print("ERRO: `gh` CLI nao encontrado. Instale com: brew install gh && gh auth login", file=sys.stderr)
        return []
    except subprocess.TimeoutExpired:
        print("ERRO: Timeout na busca.", file=sys.stderr)
        return []
    except json.JSONDecodeError:
        print("ERRO: Resposta invalida da API.", file=sys.stderr)
        return []


def search_code(query: str, lang: str = None, limit: int = 10):
    """Busca codigo no GitHub."""
    search_query = query
    if lang:
        lang_map = {
            "tsx": "tsx", "jsx": "jsx", "html": "html",
            "vue": "vue", "svelte": "svelte", "css": "css",
            "typescript": "typescript", "javascript": "javascript",
        }
        mapped = lang_map.get(lang, lang)
        search_query += f" language:{mapped}"

    cmd = [
        "gh", "api", "search/code",
        "-X", "GET",
        "-f", f"q={search_query}",
        "-f", f"per_page={limit}",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"Erro ao buscar: {result.stderr.strip()}", file=sys.stderr)
            return []
        data = json.loads(result.stdout)
        return data.get("items", [])
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return []


def format_repos(items: list) -> str:
    """Formata resultados de repositorios."""
    if not items:
        return "Nenhum resultado encontrado."

    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {len(items)} repositorios encontrados")
    lines.append(f"{'='*70}\n")

    for i, repo in enumerate(items, 1):
        name = repo.get("full_name", "?")
        desc = repo.get("description", "Sem descricao") or "Sem descricao"
        stars = repo.get("stargazers_count", 0)
        lang = repo.get("language", "?") or "?"
        url = repo.get("html_url", "")
        updated = repo.get("updated_at", "")[:10]
        topics = repo.get("topics", [])

        lines.append(f"  {i}. {name}")
        lines.append(f"     stars: {stars:,}  |  {lang}  |  Atualizado: {updated}")
        if desc and len(desc) > 120:
            desc = desc[:117] + "..."
        lines.append(f"     {desc}")
        if topics:
            lines.append(f"     Tags: {', '.join(topics[:8])}")
        lines.append(f"     {url}")
        lines.append(f"     Clone: gh repo clone {name}")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dica: Use 'gh repo clone <repo>' para clonar")
    lines.append("  Dica: Use 'gh repo view <repo> --web' para abrir no navegador")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


def format_code(items: list) -> str:
    """Formata resultados de busca de codigo."""
    if not items:
        return "Nenhum resultado encontrado."

    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {len(items)} arquivos encontrados")
    lines.append(f"{'='*70}\n")

    for i, item in enumerate(items, 1):
        name = item.get("name", "?")
        path = item.get("path", "?")
        repo = item.get("repository", {}).get("full_name", "?")
        url = item.get("html_url", "")
        desc = item.get("repository", {}).get("description", "") or ""

        lines.append(f"  {i}. {repo}/{path}")
        if desc:
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"     {desc}")
        lines.append(f"     {url}")
        lines.append("")

    lines.append(f"{'='*70}")
    lines.append("  Dica: Use 'gh api repos/<repo>/contents/<path>' para ver o codigo")
    lines.append(f"{'='*70}")
    return "\n".join(lines)


# Queries pre-definidas por categoria
PRESET_QUERIES = {
    "landing": "landing page template",
    "landing-tailwind": "landing page tailwind template",
    "landing-nextjs": "landing page nextjs template",
    "landing-react": "landing page react template",
    "saas": "saas template website",
    "saas-nextjs": "saas nextjs starter template",
    "portfolio": "portfolio template developer",
    "portfolio-nextjs": "portfolio nextjs template",
    "dashboard": "dashboard template admin panel",
    "dashboard-nextjs": "dashboard nextjs shadcn",
    "ecommerce": "ecommerce template storefront",
    "blog": "blog template minimal",
    "blog-nextjs": "blog nextjs mdx template",
    "components": "ui components library tailwind",
    "hero": "hero section component landing",
    "pricing": "pricing page component template",
    "auth": "authentication page login template",
    "dark-mode": "dark mode template website",
    "glassmorphism": "glassmorphism ui template",
    "bento": "bento grid layout template",
    "animation": "animated landing page framer motion",
    "startup": "startup landing page template",
    "agency": "agency website template",
    "minimal": "minimal website template clean",
}


def main():
    parser = argparse.ArgumentParser(
        description="Busca paginas e templates no GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Presets disponiveis (use como query):
  landing, landing-tailwind, landing-nextjs, landing-react,
  saas, saas-nextjs, portfolio, portfolio-nextjs,
  dashboard, dashboard-nextjs, ecommerce,
  blog, blog-nextjs, components, hero, pricing, auth,
  dark-mode, glassmorphism, bento, animation,
  startup, agency, minimal

Exemplos:
  python3 github-search.py landing-nextjs
  python3 github-search.py "saas starter kit" --stars 200 --sort stars
  python3 github-search.py "hero section tailwind" --type code --lang tsx
  python3 github-search.py portfolio --lang html -n 20
        """
    )
    parser.add_argument("query", help="Termo de busca ou preset (ex: landing-nextjs, saas)")
    parser.add_argument("--type", choices=["repos", "code"], default="repos", help="Tipo de busca (default: repos)")
    parser.add_argument("--lang", help="Filtrar por linguagem (html, tsx, vue, svelte, css)")
    parser.add_argument("-n", "--limit", type=int, default=10, help="Numero de resultados (default: 10)")
    parser.add_argument("--stars", type=int, default=10, help="Minimo de stars (default: 10, so pra repos)")
    parser.add_argument("--sort", choices=["stars", "updated", "best-match"], default="stars", help="Ordenar por (default: stars)")
    parser.add_argument("--presets", action="store_true", help="Listar todos os presets disponiveis")

    args = parser.parse_args()

    if args.presets:
        print("\nPresets disponiveis:\n")
        for key, val in PRESET_QUERIES.items():
            print(f"  {key:25s} -> \"{val}\"")
        print()
        return

    # Resolver preset ou usar query direta
    query = PRESET_QUERIES.get(args.query, args.query)

    if args.type == "repos":
        items = search_repos(query, lang=args.lang, min_stars=args.stars, limit=args.limit, sort=args.sort)
        print(format_repos(items))
    else:
        items = search_code(query, lang=args.lang, limit=args.limit)
        print(format_code(items))


if __name__ == "__main__":
    main()
