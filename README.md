# construtor-paginas (v3)

A Claude Code skill that builds, clones, improves and edits web pages so they come out at the level of the best real pages in their niche, not just "passing the checks".

Version 3 depends on **three things, and only three**:

1. **The `frontend-design` skill**, actually invoked to write a visual plan before any code.
2. **Adversarial auditors**: 9 independent lenses that hunt for defects, including one that compares the page against the references.
3. **Research of real references**: 6 to 10 real pages, opened in a headless browser, screenshotted and read before any visual decision.

Everything else (21st.dev, Stitch, Higgsfield, image generators, brand kits, extra design skills, paid MCPs) is optional and never blocks anything.

> The skill's operating text (`SKILL.md`, `references/`) is written in Brazilian Portuguese. This README is the English overview.

---

## What it is

- A **router** (`SKILL.md`, under 300 lines) that picks one of five paths and sends the agent to the file with that path's flow:

| Path | File | Use when |
|---|---|---|
| CREATE (`CRIAR`) | `references/caminhos/criar.md` | no page exists yet |
| CLONE (`CLONAR`) | `references/caminhos/clonar.md` | reproduce a live URL or a PDF faithfully |
| CLONE + ELEVATE (`CLONAR + ELEVAR`) | `references/caminhos/clonar-elevar.md` | "clone it and make it great": identity kept, composition raised |
| IMPROVE (`MELHORAR`, includes visual variants) | `references/caminhos/melhorar.md` | the page exists and must get better without regressions |
| EDIT (`EDITAR`) | `references/caminhos/editar.md` | one specific change, nothing else |

- A **gated CREATE flow** in eight steps, each one blocking the next:

| Step | Output | Blocking gate |
|---|---|---|
| a. Briefing | what the business sells, to whom, the offer, price, the action, and the real material that exists (photos, logo, testimonials, contact). Anything missing becomes a client to-do, never an invention | `gate-etapas.py registrar 0` |
| b. Reference research | 6 to 10 real pages (at least 2 from the same kind of business, 2 high-level design references), first fold and a mid-page section screenshotted, each one read on composition, typography, imagery and rhythm, plus the principle to borrow | `gate-referencias.py` (6 real, distinct, non-blank screenshots marked as read) |
| c. Visual plan | `plano-visual.md` written through the `frontend-design` skill: direction, 4 to 6 named hex colors, type scale, how imagery enters, section rhythm, signature element, and what changed in the self-review pass | `gate-etapas.py registrar 2` |
| d. Copy | section copy using only facts from the briefing (short local-service model included) | `gate-etapas.py registrar 3` |
| e. Build | HTML + compiled Tailwind by default (React only when the project truly needs it), hero first and checked against the plan, freely licensed images chosen by what the references taught, license recorded | `gate-etapas.py registrar 4` |
| f. Mechanical gates | no uppercase kicker or decorative numbers, dead utility classes, 12 real viewports (including one-line buttons up to 768 px and a button within 2 screens on phones), occluded text, symmetry of parallel items and columns (`gate-simetria.mjs`), on-screen text (widows, lowercase starts, repeated colored italics: `gate-texto.mjs`), every promise backed by a briefing line (`gate-verdade.py`), a publish folder with nothing but the page (`montar-dist.py` + `gate-publicacao.py`), page identity, tool usage, references | each exit code recorded in `wave.py gate` |
| g. Auditors | 9 lenses: `design-critic`, `assets-auditor`, `visual-auditor`, `motion-auditor`, `responsive-auditor`, `cro-auditor`, `a11y-auditor`, `content-auditor`, `comparacao-referencias`, run by an independent auditor subagent when the environment allows. A self-review score never releases delivery | `wave.py checar` (every lens and gate ran) and `wave.py rodada` (the review cycle, which answers AUDITORIA INDEPENDENTE PENDENTE while any lens is `--origem autoavaliacao`) |
| h. Proof | desktop 1440 and mobile 390 screenshots read by the agent, main interaction clicked, delivery block | `gate-etapas.py registrar 5` |

- **Auditors run as independent subagents when the environment allows it** (one per lens, in parallel, none seeing the others). When it does not, the same checks run sequentially, one lens at a time, and the record says it was a self-review.
- **The `comparacao-referencias` lens** puts the page next to the strongest references, axis by axis. If it fails, the cycle refuses to close no matter how high the other scores are, and the agent goes back to the visual plan.

## What it is not

- Not a template pack or a component library. It produces pages from a brief, not from presets.
- Not a design database that decides for you. The bundled database (`data/*.csv` + `scripts/search.py`) is an optional lookup; it never chooses the palette or the type.
- Not a copier of other sites. References teach principles; copying another brand's copy, layout, logo, photos or exact palette is forbidden.
- Not a fact generator. Prices, numbers, credentials and testimonials that are not in the brief never appear on the page.
- Not a deploy tool. Deploying is optional; without a hosting account the delivery is local and the deploy is a declared pending item.

---

## Prerequisites

| Requirement | Why | Required |
|---|---|---|
| **Python 3.8+** | gates, audit registry, reference gate | yes |
| **Node.js 18+** | Playwright, screenshots, visual gates | yes |
| **Playwright with Chromium** (`npm i -g playwright && npx playwright install chromium`) | reference screenshots and delivery proof | yes |
| **`frontend-design` skill** (`npx -y skills add anthropics/skills --skill frontend-design --agent claude-code`) | the visual plan | yes |
| A web search tool in the agent session | finding the reference pages | yes (any search tool works) |
| ffmpeg | video gate, only for pages with video | optional |
| 21st.dev, Stitch, Higgsfield, Pexels key, extra design skills | optional reinforcements | optional |

Check everything with one command. Only the four critical items can fail it:

```bash
python3 <skill-dir>/scripts/checar-ferramentas.py              # critical + quick local optionals
python3 <skill-dir>/scripts/checar-ferramentas.py --opcionais  # also MCPs, Higgsfield, network
```

## Installation

```bash
git clone https://github.com/ojuliocouto/skill-construtor-paginas.git ~/.claude/skills/construtor-paginas
npx -y skills add anthropics/skills --skill frontend-design --agent claude-code
npm i -g playwright && npx playwright install chromium
python3 <skill-dir>/scripts/checar-ferramentas.py   # <skill-dir> = where you cloned it
```

The skill activates on the next Claude Code session whenever you ask to create, clone, improve or edit a page. Optional: `hooks/pagina-skill-inject.py` is a `UserPromptSubmit` hook that injects a reminder to run the skill when it detects those intents. Wire it in `settings.json`:

```json
{ "hooks": { "UserPromptSubmit": [ { "hooks": [ { "type": "command", "command": "python3 <skill-dir>/hooks/pagina-skill-inject.py" } ] } ] } }
```

---

## Onboarding: the first page

1. Run the checker. Fix any critical item it reports (the fix command is printed).
2. Ask for the page in plain words ("create a page for my pilates studio in Niterói"). The agent declares the path and asks the six briefing questions.
3. The agent searches the web for real pages, captures them:
   ```bash
   node <skill-dir>/scripts/capturar-referencias.mjs --projeto <page-dir> --tipo mesmo-negocio <url> <url>
   node <skill-dir>/scripts/capturar-referencias.mjs --projeto <page-dir> --tipo design <url> <url>
   ```
   reads every screenshot, writes the reading into `referencias/referencias.json`, and runs `gate-referencias.py`.
4. It invokes `frontend-design`, writes `plano-visual.md`, then the copy, then builds.
5. It runs the gates and the 9 lenses, closes the review cycle, and delivers with screenshots it has actually looked at.

---

## Repository layout

```
SKILL.md                       router (v3.0.0)
CHANGELOG.md                   v2 -> v3 migration
references/
  caminhos/                    one file per path: criar, clonar, clonar-elevar, melhorar, editar
  pesquisa-de-referencias.md   how to find, capture, read and record references
  auditores.md                 the 9 lenses, verdict schema, cycle rules, taste pass
  preferencias-de-design.md    taste rules measured on real corrections (generic)
  anti-vibe-coding.md          the V1 to V15 visual AI tells
  copy-servico-local.md        short copy model for local services
  page-types.md                section models per page type
  assets-sem-chave.md          freely licensed photos and how to credit them
  gate-etapas.md               evidence fields per step
  arquivo/                     v2 references, outside the flow (kept for lookup only)
  projects/EXAMPLE.md          per-project template (real files are local, gitignored)
  sessions/EXAMPLE.md          per-session template (real files are local, gitignored)
scripts/                       gates, capture, audit registry, tests
data/                          optional design database (CSV)
hooks/pagina-skill-inject.py   optional trigger hook
```

## Tests

Run from the repository root:

```bash
python3 scripts/test-checar-ferramentas.py
python3 scripts/test-uso-ferramentas.py
python3 scripts/test-gate-referencias.py
python3 scripts/test-wave.py
python3 scripts/test-gate-etapas.py
python3 scripts/test-gate-sem-kicker.py
python3 scripts/test-classes-mortas.py
python3 scripts/test-search.py
python3 scripts/test-docs.py
python3 scripts/test-preferencias.py
python3 scripts/test-publicacao.py
python3 scripts/test-gate-verdade.py
python3 scripts/test-imagens.py
node scripts/test-capturar-referencias.cjs
node scripts/test-gates-visuais.cjs
node scripts/test-print-cabecalho.cjs
node --test scripts/extrai-identidade.test.mjs
```

The visual tests use Chromium, ffmpeg and local synthetic pages. They prove that each gate fails on the defect it exists for; they do not approve a client's design. Reading the screenshots stays mandatory.

## Security

- No secret, token, account ID or client data lives in this repository. Optional tools read their keys from the environment (for example `TWENTYFIRST_API_KEY`, `PEXELS_API_KEY`); the checker never prints them.
- Client material, project memory and session notes (`references/projects/*`, `references/sessions/*`, `evidencias/`, owner-specific preferences) are gitignored.
- The reference capture never logs in, never clicks cookie or consent banners and never accepts terms.
- Pages built outside their final domain ship with `noindex`, so a test copy of a real client's page does not compete with the client in search.

## License

Proprietary. Exclusive to **Júlio Couto / iAutomate**. All rights reserved. No redistribution, resale, or reuse without express permission.
