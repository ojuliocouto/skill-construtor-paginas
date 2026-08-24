# construtor-paginas

A Claude Code skill for **building, cloning, and versioning** high-quality web pages, with a strict copy-first workflow, built-in design quality gates, an adversarial multi-agent audit, and anti-AI-slop enforcement.

Stacks: **React, Next.js, Vue, Svelte, HTML+Tailwind**. Ships with color palettes, design styles, font pairings, Framer Motion / Motion patterns, a MagicUI catalog, a copy-paste effects library, and a mandatory quality-scoring gate before any page is delivered.

> Fully generic. No client-specific brand, token, asset, or path is baked into the repo. Per-project context lives locally (see [Project memory](#project-memory)).

---

## Table of contents

- [Why this over a generic prompt](#why-this-over-a-generic-prompt)
- [When it activates](#when-it-activates-4-mandatory-triggers)
- [The four paths](#the-four-paths)
- [Prerequisites & onboarding](#prerequisites--onboarding-step-0)
- [Installation](#installation)
- [The 6-step flow](#the-6-step-flow)
- [Quality gate](#quality-gate-before-delivery)
- [Adversarial audit wave](#adversarial-audit-wave-step-4)
- [Cloning rules](#cloning-rules-live-site-or-pdf)
- [Effects catalog](#effects-catalog)
- [Pairs with (skills, MCPs, tools)](#pairs-with-skills-mcps-tools)
- [Project memory](#project-memory)
- [Repository layout](#repository-layout)
- [Reference files](#reference-files)
- [License](#license)

---

## Why this over a generic prompt

A "generic" page-building skill is usually a single system prompt ("you are an expert web designer, build a beautiful responsive page with Tailwind"). The model reads it and starts coding. No process, no quality gate, no memory. This skill is a **production pipeline with quality control** instead. The differences:

| | Generic prompt | construtor-paginas |
|---|----------------|--------------------|
| **Process** | jumps straight to code | gated 6-step flow with forced stops; copy → design → code, copy locked before any markup |
| **Audit** | same context that built it (biased), or none | adversarial wave of 7 parallel subagents (design, assets, visual, motion, mobile, CRO, a11y) + synthesis that **blocks delivery** on any critical |
| **Anti-slop** | none (so it produces the "AI look") | explicit 15 visual AI tells + Taste Gate scoring (ship only at avg ≥ 4.0) |
| **Design source** | invents hex codes and fonts on the fly | queries a real design DB (50 styles, 21 palettes, 50 font pairings) via `search.py` |
| **Cloning** | "gets inspired", approximate | fidelity: real colors via `getComputedStyle`, real logo download, never invents identity |
| **Memory** | forgets every session | persists project brand tokens + session learnings locally, resumes where it left off |
| **Onboarding** | assumes tools exist or fails | checks MCPs/plugins, guides install, always has a documented fallback |
| **Integrations** | text only | Stitch (wireframe), 21st.dev (components), Pexels/Lottie assets, AI image (nanobanana), video (Veo), PDF→page |

### When the generic prompt is actually better

Honesty matters more than selling this. Reach for a plain prompt when:

- The page is trivial or throwaway and you want it **fast** (the 6-step process is overhead).
- You have **no setup** (the MCPs and API keys here are optional but unlock the best parts).
- You want zero opinionation and full manual control.

This skill wins on **consistency, fidelity, and anti-slop** for real client work; it costs **speed and lightness** on trivial pages.

---

## When it activates: 4 mandatory triggers

The skill **auto-activates** (and can be enforced by an optional `UserPromptSubmit` hook) whenever you want to:

1. **Create a new page** (landing, sales page, institutional, e-commerce home, dashboard, portfolio)
2. **Clone an existing page** (from a live URL or a PDF): "clone this page", "copy this site", "replicate this layout"
3. **Improve a page that already exists and will keep existing**: "improve this page", "optimize it", "raise conversion", "redo", "v2", "redesign"
4. **Edit something specific on an existing page**: "change the headline", "change the button colour", "fix the price", "add an FAQ section", "fix it on mobile"

Any of the four runs the skill **before any code**. No slash command needed: just describe what you want. To invoke explicitly: `/construtor-paginas`.

---

## The four paths

**The skill routes before it executes** and states the chosen path in its first reply. This matters: running the full 6-step ritual to change one headline is as wrong as improvising a brand new page. Each path has its own flow and its own gate.

| Path | Starts from | Copy | Wireframe (Stitch) | Closing gate |
|------|-------------|------|--------------------|--------------|
| **1. CREATE from scratch** | a brief | written fresh (Step 1) | yes | full 6-step flow + adversarial wave (7 lenses) |
| **2. CLONE** (URL or PDF) | a live URL / PDF | reproduced exactly | no (structure is given) | **fidelity gate**: original and clone side by side |
| **3. IMPROVE** | an existing page | kept/improved | no (structure exists) | **improvement gate**: before and after scored per dimension, nothing may get worse |
| **4. EDIT** (surgical change) | an existing page | untouched unless asked | no | **regression checklist + proof of the changed spot**. No COPY LOCK, no wireframe, no 7-lens wave |

CREATE, CLONE and IMPROVE share the Step 3 build (21st.dev components) and the Step 4 quality gate with the adversarial audit. EDIT deliberately does not: a one-line change does not re-audit the whole page.

---

## Prerequisites & onboarding (Step 0)

On activation the skill runs a **prerequisite check** and tells you what to install before proceeding.

**Nothing is hard-blocked.** Every dependency has a documented fallback, so you can run the skill on a clean machine with no API key at all and still get a page: components get hand written instead of pulled from 21st.dev, the taste gate runs on the manual rubric, and images come from AI generation or from you. The skill will offer to install what is missing and tell you what it is degrading, then carry on. Installing the optional pieces raises the ceiling of the result; it is not a gate to get started.

### What you need before anything

| Requirement | Why | Required? |
|---|---|---|
| **Node.js 18+** | runs the MCPs, the CLI tools and the scripts | **required** |
| **Python 3.9+** | design bank search, asset search, hooks | **required** |
| **Playwright** (`npm install -g playwright && npx playwright install chromium`) | delivery proof, identity extraction on clone, video gate. **The skill requires a screenshot of the result on every path**, so without this you cannot close a delivery | **required in practice** |
| **git** | cloning this repo, versioning your page | **required** |

### Optional, raises quality

| Dependency | Type | Role | Fallback if missing |
|------------|------|------|---------------------|
| **Stitch** | MCP (`mcp__stitch__*`) | wireframe (Step 2) | lay the structure straight in code |
| **21st.dev Magic** | MCP (`mcp__magic__*`) | UI components (Step 3) | hand-write components (shadcn/Tailwind) |
| **design-taste-frontend** | skill | anti-slop gate (Step 4) | manual scoring rubric (4.0b) |
| **frontend-design** | skill | aesthetic direction before code (Step 2) | run with design-taste-frontend only |
| **redesign-existing-projects** | skill | audit-first for clone/redesign | manual 5-dimension audit |
| **high-end-visual-design** | skill | premium finish | optional |
| **animate** | skill | motion and micro-interaction (Step 4) | animate by hand with Framer Motion |
| **impeccable** | CLI (`npx`) | UI refinement | optional |
| **PEXELS_API_KEY** | env | stock video/photo search | generate with AI or ask the user |
| **ffmpeg** | CLI | video gate for pages that embed video | skip the video gate |

Install commands surfaced by the skill:

```bash
# 21st.dev Magic (components): free API key at https://21st.dev
claude mcp add magic --env API_KEY=<your-21st-key> -- npx -y @21st-dev/magic@latest

# Google Stitch (wireframe): global binary stitch-mcp
npm install -g stitch-mcp && claude mcp add stitch -- stitch-mcp proxy

# Taste Skills (anti-slop): from https://www.tasteskill.dev/
#   design-taste-frontend, redesign-existing-projects, high-end-visual-design

# impeccable (CLI, optional): no install, runs via npx
npx impeccable --version

# Pexels (assets, optional, free): key at https://www.pexels.com/api/
echo 'export PEXELS_API_KEY="<your-key>"' >> ~/.zshrc && source ~/.zshrc
```

---

## Installation

```bash
git clone https://github.com/ojuliocouto/skill-construtor-paginas.git ~/.claude/skills/construtor-paginas
```

The skill activates automatically on the next Claude Code session.

### Optional: force the 3 triggers with a hook

`hooks/pagina-skill-inject.py` is a `UserPromptSubmit` hook that detects the create, clone and redesign triggers and injects a forced reminder to run the skill (so it never depends on the model "remembering"). Wire it in `settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command", "command": "python3 <caminho-deste-repo>/hooks/pagina-skill-inject.py" } ] }
    ]
  }
}
```

(Copy `hooks/pagina-skill-inject.py` to `~/.claude/scripts/` or point the command at this repo's path.)

---

## The 6-step flow

Copy first, design second, code third. Each step has a gate and a forced stop before the next.

| Step | Name | What happens | Tools / skills |
|------|------|--------------|----------------|
| 0 | Understand & inventory | classify page, map sections, audit copy, inventory assets (incl. **lead destination**: form endpoint / checkout URL) | `Read` (PDF), Google Docs/Sheets (requires external local scripts, not bundled), `github-search.py` |
| 1 | Copy & message | VoC mining, before/after, message hierarchy, **copy lock** | `copy-pagina-vendas` (optional) |
| 2 | Direct | palette, font pairing, per-section layout, **wireframe** | **Stitch**, `redesign-existing-projects` (clone/v2) |
| 3 | Build | section by section, real assets, motion | **21st.dev Magic**, `assets-search.py`, nanobanana, Veo |
| 4 | Verify & ship | adversarial audit wave + quality gate + deploy | `design-taste-frontend`, `impeccable`, Workflow |
| 5 | Measure & iterate | post-launch metrics, iterate against benchmark | analytics |

> For **e-commerce / retail homes** (not high-ticket sales pages), Steps 0/1 collapse: skip copy lock / offer / checkout / per-section video. Focus on real brand identity, product cards with ratings, category & gender nav, brand grid, first-purchase coupon, trust strip.

---

## Quality gate (before delivery)

1. **Design Laws** (`references/design-laws.md`): no absolute bans applied unless explicitly requested.
2. **Taste Gate** (`references/taste-gate.md`): score 6 design dimensions (1-5); deliver at avg ≥ 4.0.
3. **AI Slop Test**: "Does this look AI-generated? Is there a detail only someone with taste would add?"
4. **Anti-vibe-coding** (`references/anti-vibe-coding.md`): 5 substance signals **+ 15 visual AI tells**. Footer-legal / broken-checkout failures **block delivery**.
5. **Taste Skill**: run `design-taste-frontend` on the finished page; clones/redesigns use `redesign-existing-projects` (audit-first) at Step 2; premium finish via `high-end-visual-design`.
6. **impeccable** (CLI): `npx impeccable detect <url>` / `critique` / `polish`.

### The 15 visual AI tells (the "AI look" checklist)

Flag and fix before shipping: mono uppercase kicker labels with a square/bar · giant decorative number ("01") · stroke outline word behind content · blurred radial glow blob · animated speed streaks · stats block in the hero · price in mono font · "ENTER" hint in the search box · diffuse colored glow on button hover · mixed languages in copy · single-metaphor "marketing-ese" copy · exaggerated hover rotation on product photos · decorative icon separators · repeated diagonal-clip + gradient sections · tiny logo (<56px).

**Master rule:** when cloning a real store, the reference for "good" is the niche competitor, not Dribbble/SaaS landing pages.

---

## Adversarial audit wave (Step 4)

The audit is **never** done by the same context that built the page (builders don't see their own mistakes). Step 4 fans out **7 adversarial subagents in parallel**, each with one independent lens, then a synthesis agent consolidates the gate. Orchestrated via the `Workflow` tool. Full protocol, schema, and skeleton in `references/audit-agents.md`.

| Agent | Lens | Blocks delivery (critical) if |
|-------|------|-------------------------------|
| `design-critic` | taste / anti-slop (runs `design-taste-frontend`) | taste < 4.0, **3+ visual AI tells**, broken footer/checkout |
| `assets-auditor` | real image/mockup/video presence | text+gradient+SVG only, SaaS without a mockup, lead magnet without the material mockup |
| `visual-auditor` | hierarchy, palette, spacing, desktop grid | letter format, side-by-side collapsed to one column |
| `motion-auditor` | scroll reveal, hover, hero entrance, counters | static hero, no feedback, dead hover |
| `mobile-auditor` | 320/375/768px, JS hamburger | layout breaks, dead hamburger, overflow |
| `cro-auditor` | CTAs, form, offer, message match, Hook/Story/Offer | weak CTA, broken form/checkout, no message match |
| `a11y-auditor` | focus, labels, alt, ARIA, 4.5:1 contrast, no emoji | critical WCAG failure, emoji on page |

**Gate:** any critical → `deploy_liberado: false`, returns the fix list, builder fixes and re-runs only the failed lenses. No criticals but any score < 8.0 → ship with polish notes. If the `Workflow` tool is unavailable, it falls back to manual scoring (Step 4.0b) and logs that the wave was skipped.

---

## Cloning rules (live site or PDF)

- **Keep the original identity.** Extract exact brand colors via `getComputedStyle` in the browser; download the **real logo** from the site. Never invent palette/logo unless explicitly asked.
- **White-background product photos** only go on light/white surfaces (they blend invisibly). On dark surfaces they become "white boxes": a top AI tell.
- Preserve IA, slugs, nav labels, and analytics events (see the audit-first Redesign Protocol).
- **PDF clone:** read **every** page first (in 20-page blocks for large PDFs), extract layout, section order, exact copy, and assets before writing any code.

---

## Effects catalog

`references/efeitos-avancados.md` has copy-paste effects. Notable:

- **Gradient Border Beam**: variant 4b (auto-rotating, `@property` + conic-gradient + mask ring) and **variant 4c (border glow that follows the cursor)**. One `mousemove` listener powers a whole grid.
- 3D tilt, text scramble, magnetic cursor, noise texture, blob morph, confetti, aurora, glassmorphism spotlight, parallax, animated counters, floating orbs.

Rule: minimum 2 effects per page (1 background + 1 interaction), maximum 2 per section. The primary CTA must have at least an elaborate hover plus confetti or magnetic.

---

## Pairs with (skills, MCPs, tools)

| Name | Type | Status | When |
|------|------|--------|------|
| **Stitch** | MCP | `claude mcp add` (see onboarding) | wireframe (Step 2) |
| **21st.dev Magic** | MCP | `claude mcp add` + API key | components (Step 3) |
| `design-taste-frontend` | skill | [tasteskill.dev](https://www.tasteskill.dev/) | anti-slop gate (Step 4) |
| `redesign-existing-projects` | skill | tasteskill.dev | audit-first for clone/redesign (Step 2) |
| `high-end-visual-design` | skill | tasteskill.dev | premium finish (Step 4) |
| `impeccable` | CLI | `npx impeccable` (no install) | deep refinement (Step 4) |
| `copy-pagina-vendas` | skill | optional | sales copy before building (Step 1) |

---

## Project memory

After each successful session the skill saves context to:

- `references/projects/<slug>.md`: per-project brand tokens, palette, stack, deploy, funnel
- `references/sessions/<date>-<slug>.md`: what was done, learnings, files changed

On the next session for the same project it reads these and continues where it left off.

> **These folders are local-only (gitignored).** Only the neutral `EXAMPLE.md` templates are tracked. No client data is ever pushed to the repo. Copy `EXAMPLE.md` to start a new project/session record.

To resume: *"Continue working on the [project name] page"*.

---

## Repository layout

```
construtor-paginas/
├── SKILL.md                      # the skill (activation, 6 steps, gates, audit wave)
├── README.md                     # this file
├── hooks/pagina-skill-inject.py  # optional UserPromptSubmit trigger hook
├── scripts/
│   ├── search.py                 # query the design DB (styles, colors, fonts)
│   ├── github-search.py          # find templates/components on GitHub
│   └── assets-search.py          # videos (Pexels), photos, Lottie, illustrations, icons
├── data/                         # CSVs: 50 styles, 21 palettes, 50 font pairings, UX guidelines
└── references/                   # specialized guides (auditing, effects, page types, ...)
    ├── audit-agents.md           # adversarial wave protocol + schema
    ├── projects/EXAMPLE.md       # per-project template (rest is local/gitignored)
    └── sessions/EXAMPLE.md       # per-session template (rest is local/gitignored)
```

---

## Reference files

| File | Purpose |
|------|---------|
| `references/audit-agents.md` | Adversarial audit wave: 7 lenses + synthesis, schema, Workflow skeleton |
| `references/design-laws.md` | Color (OKLCH), typography, motion rules |
| `references/anti-vibe-coding.md` | 5 substance signals + 15 visual AI tells + fixes |
| `references/taste-gate.md` · `references/scoring-system.md` | Quality scoring rubric |
| `references/page-types.md` | Page-type decision tree + section templates |
| `references/efeitos-avancados.md` | Copy-paste effects (incl. border beam 4b/4c) |
| `references/visual-excellence.md` | Premium gradients, backgrounds, glassmorphism |
| `references/animacoes-avancadas.md` | Advanced Framer Motion / Motion patterns |
| `references/magicui-components.md` | MagicUI component catalog |
| `references/mobile-checklist-detailed.md` · `references/desktop-layout-rules.md` | Responsive + desktop grid rules |
| `references/strategist-audit.md` · `references/cta-placement-map.md` | Conversion / funnel audit |
| `data/colors.csv` · `data/styles.csv` · `data/typography.csv` | Palettes, styles, font pairings |

---

## License

Proprietary. Exclusive to **Júlio Couto / iAutomate**. All rights reserved. No redistribution, resale, or reuse without express permission.
