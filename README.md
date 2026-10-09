# construtor-paginas (v3)

A Claude Code skill that builds, clones, improves and edits web pages so they come out at the level of the best real pages in their niche, not just "passing the checks".

Version 3 depends on **three things, and only three**:

1. **The `frontend-design` skill**, actually invoked to write a visual plan before any code.
2. **Adversarial auditors**: 9 independent lenses that hunt for defects, including one that compares the page against the references.
3. **Research of real references**: 6 to 10 real pages, opened in a headless browser, screenshotted and read before any visual decision.

Since v3.4, the CREATE path also has a mandatory **PLAN step** (`references/plano.md`): before any code, the student gets a single `PLANO.md` with the references to mark, 3 clearly different visual directions rendered as real first-fold PNGs, a menu of section formats with thumbnails, the copy with the briefing line behind each sentence, pixel and analytics setup, and the publishing plan, and approves it item by item.

Since v3.5, what made the v7 of the test page far better than the v6 ("correct but generic") is rule and gate: a **signature moment** named in the PLAN (one element tied to the subject, present in 3 or more sections, changing state down the page), a **per-section composition table** (desktop, phone, animation) proved with a pixel-measured board per section (`anim.mjs`, `prancha.py`, `gate-animacao.py`), **rhythm** (no two neighboring sections with the same skeleton, at most one "centered title + cards": `gate-ritmo.mjs`), **real photo before illustration** with no repeated or blurry photo (`gate-imagens.py`), and the symmetry and responsive gates accepting the asymmetry (`data-assimetrico`) and the phone carousel the plan asked for.

Everything else (21st.dev, Stitch, Higgsfield, image generators, brand kits, extra design skills, paid MCPs) is optional and never blocks anything.

> The skill's operating text (`SKILL.md`, `references/`) is written in Brazilian Portuguese. This README is the English overview.

---

## What it is

- A **router** (`SKILL.md`, about 330 lines) that picks one of five paths and sends the agent to the file with that path's flow:

| Path | File | Use when |
|---|---|---|
| CREATE (`CRIAR`) | `references/caminhos/criar.md` | no page exists yet |
| CLONE (`CLONAR`) | `references/caminhos/clonar.md` | reproduce a live URL or a PDF faithfully |
| CLONE + ELEVATE (`CLONAR + ELEVAR`) | `references/caminhos/clonar-elevar.md` | "clone it and make it great": identity kept, composition raised |
| IMPROVE (`MELHORAR`, includes visual variants) | `references/caminhos/melhorar.md` | the page exists and must get better without regressions |
| EDIT (`EDITAR`) | `references/caminhos/editar.md` | one specific change, nothing else |

- A **gated CREATE flow** in eight steps plus the PLAN, each one blocking the next:

| Step | Output | Blocking gate |
|---|---|---|
| a. Briefing | what the business sells, to whom, the offer, price, the action, and the real material that exists (photos, logo, testimonials, contact). Anything missing becomes a client to-do, never an invention | `gate-etapas.py registrar 0` |
| b. Reference research | 6 to 10 real pages (at least 2 from the same kind of business, 2 high-level design references), first fold and a mid-page section screenshotted, each one read on composition, typography, imagery and rhythm, plus the principle to borrow | `gate-referencias.py` (6 real, distinct, non-blank screenshots marked as read) |
| b2. PLAN | `PLANO.md` approved by the student, in 7 sections: a. references (each with what it does well, the ones the student likes marked), b. 3 visual directions made with `frontend-design`, each changing type, palette, imagery and rhythm at once, rendered at 1440 and 390 by `previa-direcoes.mjs` into `plano/direcoes.png` side by side, c. section menu (`references/secoes/`: 18 formats across 8 goals, each with when to use, structure, pitfall and a minimal HTML example turned into a thumbnail) and the order the student picks, d. copy table (sentence -> briefing line), e. Meta Pixel, GA4 and 5 events (`references/rastreamento.md`, no real ID anywhere), f. stack, hosting, domain and what changes on the final domain, g. approval checkboxes; since v3.5 also the signature moment, the per-section composition table and the client material requested | `gate-plano.py` (no building without every box checked) |
| c. Visual plan | `plano-visual.md` written through the `frontend-design` skill: direction, 4 to 6 named hex colors, type scale, how imagery enters, section rhythm, signature element, and what changed in the self-review pass | `gate-etapas.py registrar 2` |
| d. Copy | section copy using only facts from the briefing (short local-service model included) | `gate-etapas.py registrar 3` |
| e. Build | in the order approved in the PLAN, with the tracking snippet when the PLAN asked for it; HTML + compiled Tailwind by default (React only when the project truly needs it), hero first and checked against the plan, freely licensed images chosen by what the references taught, license recorded | `gate-etapas.py registrar 4` |
| f. Mechanical gates | no uppercase kicker or decorative numbers, dead utility classes, 12 real viewports (including one-line buttons up to 768 px and a button within 2 screens on phones), occluded text, symmetry of parallel items and columns (`gate-simetria.mjs`), on-screen text (widows, lowercase starts, repeated colored italics: `gate-texto.mjs`), every promise backed by a briefing line (`gate-verdade.py`), a publish folder with nothing but the page, no internal code comments and site icons generated from the current identity (`montar-dist.py` + `gate-publicacao.py` + `gerar-icones.mjs`), composition (no repeated section skeleton, no wireframe-looking drawings, a timeline that ends at its last marker, a person in the first screen when the audience is people, accent strokes at 3:1: `gate-composicao.mjs`), rhythm (`gate-ritmo.mjs`), per-section animation proof (`anim.mjs` + `prancha.py` + `gate-animacao.py`: at least 2% of pixels change between start and end in 1440 and 390, at most 2 sections share an animation type), images (`gate-imagens.py`: licenses, no repeated photo across sections by perceptual hash and source, sharpness of 100 or more, 60% photo in the first screen, "imagem ilustrativa" visible in the first screen), sticky overlap (`sobreposicao.mjs`), the pixel and the 5 events the PLAN asked for, bound by `data-evento` (`gate-rastreamento.py`), motion seen on a real visit (nothing finishes animating before it enters the screen at 300 px/s, no smooth scroll under reduced motion: `gate-movimento.mjs`), page identity, tool usage, references | each exit code recorded in `wave.py gate` |
| g. Auditors | 9 lenses: `design-critic`, `assets-auditor`, `visual-auditor`, `motion-auditor`, `responsive-auditor`, `cro-auditor`, `a11y-auditor`, `content-auditor`, `comparacao-referencias`, passed in one pass by a single independent auditor subagent when the environment allows, on an evidence package gathered once (`pacote-auditoria.py`), with a cap of 2 rounds. The reference lens also answers, with `--gosto bonito|correto`, whether the page is beautiful or merely correct; "correct" sends it back to the visual plan. A self-review score never releases delivery | `wave.py checar` (every lens and gate ran) and `wave.py rodada` (the review cycle, which answers AUDITORIA INDEPENDENTE PENDENTE while any lens is `--origem autoavaliacao`) |
| h. Proof | desktop 1440 and mobile 390 screenshots read by the agent, a scroll video (desktop and mobile) with its contact sheets read, main interaction clicked, delivery block | `gate-etapas.py registrar 5` |

- **One independent auditor subagent covers the 9 lenses in a single pass** (since 3.5.4; one subagent per lens is an optional mode, only when the user asks for a deep audit). Before calling it, the main session gathers the evidence package once (URL, `dist/`, briefing, PLAN, the screenshots the gates already made, the video proof sheets, the references) and `scripts/pacote-auditoria.py` checks it is complete, so the auditor does not capture the screens again. The cycle has a cap of 2 rounds: round 2 only re-checks the round 1 findings (fixed, not fixed, regression) and nothing else. After it the cycle always closes: approved, `ENTREGA COM RESSALVAS` (leftover findings and the real score are written in the delivery) or `NÃO ENTREGAR: crítico aberto`. A third round only happens if the user asks (`--rodada-extra-pedida`). When no subagent is available, the same checks run sequentially, one lens at a time, and the record says it was a self-review, which never releases delivery.
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
| **Playwright with Chromium** (`npm install -g playwright`, then `npx playwright install chromium`) | reference screenshots and delivery proof | yes |
| **`frontend-design` skill** (`npx -y skills add anthropics/skills --skill frontend-design --agent claude-code -g -y --copy`) | the visual plan | yes |
| A web search tool in the agent session | finding the reference pages | yes (any search tool works) |
| ffmpeg | video gate, only for pages with video | optional |
| 21st.dev, Stitch, Higgsfield, Pexels key, extra design skills | optional reinforcements | optional |

Check everything with one command. Only the four critical items can fail it:

```bash
node <skill-dir>/scripts/py.mjs checar-ferramentas.py              # critical + quick local optionals
node <skill-dir>/scripts/py.mjs checar-ferramentas.py --opcionais  # also MCPs, Higgsfield, network
```

## Installation

```bash
git clone https://github.com/ojuliocouto/skill-construtor-paginas.git ~/.claude/skills/construtor-paginas
npx -y skills add anthropics/skills --skill frontend-design --agent claude-code -g -y --copy
npm install -g playwright
npx playwright install chromium   # on Linux: npx playwright install --with-deps chromium
node <skill-dir>/scripts/py.mjs checar-ferramentas.py   # <skill-dir> = where you cloned it
```

### Windows, macOS and Linux

`scripts/py.mjs` is a small launcher that finds the Python on your machine (its command name differs between Windows, macOS and Linux) and turns on UTF-8 mode. Wherever this guide shows `node <skill-dir>/scripts/py.mjs <script>.py`, that exact command works on any system. `references/sistemas.md` has what changes per system, how to install every prerequisite on Windows, macOS and Linux, and the known errors with their output.

| | Windows | macOS | Linux (Debian/Ubuntu, Fedora) |
|---|---|---|---|
| Node 18+ | `winget install -e --id OpenJS.NodeJS.LTS` | `brew install node` (macOS) | installer or `nvm` from nodejs.org |
| Python 3.8+ | `winget install -e --id Python.Python.3.12` | `brew install python` (macOS) | `sudo apt install python3` / `sudo dnf install python3` |
| Git | `winget install -e --id Git.Git` (ships Git Bash) | Apple Command Line Tools | `sudo apt install git` / `sudo dnf install git` |
| Chromium for Playwright | `npx playwright install chromium` | same | `npx playwright install --with-deps chromium` |
| ffmpeg (optional) | `winget install -e --id Gyan.FFmpeg` | `brew install ffmpeg` (macOS) | `sudo apt install ffmpeg` / `sudo dnf install ffmpeg` |

On Windows, prefer Git Bash (or WSL); PowerShell 5.1 has no `&&`. The `-g` in the `skills add` command matters: without it the `frontend-design` skill is installed into the current folder instead of your user-level skills folder. `checar-ferramentas.py` prints the right install command for your system.

Status: the skill was built on macOS. Since 3.5.5 it has a portability guard (`scripts/test-portabilidade.py`) and a GitHub Actions workflow (`.github/workflows/portabilidade.yml`) that runs the whole suite on `windows-latest`, `ubuntu-latest` and `macos-latest`, plus the portable tests from a Windows folder with an accent and a space in its name (`C:\curso automação\skill`). Until a green run of that workflow is recorded in `CHANGELOG.md`, Windows and Linux are described and guarded, not yet proven on a real machine.

The skill activates on the next Claude Code session whenever you ask to create, clone, improve or edit a page. Optional: `hooks/pagina-skill-inject.py` is a `UserPromptSubmit` hook that injects a reminder to run the skill when it detects those intents. Wire it in `settings.json`:

```json
{ "hooks": { "UserPromptSubmit": [ { "hooks": [ { "type": "command", "command": "node <skill-dir>/scripts/py.mjs <skill-dir>/hooks/pagina-skill-inject.py" } ] } ] } }
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
SKILL.md                       router (v3.5.9)
CHANGELOG.md                   v2 -> v3 migration
references/
  caminhos/                    one file per path: criar, clonar, clonar-elevar, melhorar, editar
  pesquisa-de-referencias.md   how to find, capture, read and record references
  plano.md                     the PLAN step, the PLANO.md template and what its gate checks
  ritmo-e-animacao.md          signature moment, section skeletons and the animation proof
  receitas-de-movimento.md     15 motion recipes extracted from the approved page (HTML, CSS, JS, no-JS and reduced-motion fallbacks)
  receitas/demo.html           one self-contained page that shows every recipe working (opens from disk or over HTTP)
  imagem.md                    real photo before illustration, repetition, sharpness, notice
  densidade-servico-local.md   the 7 copy items of a local-service page
  vh-estavel.md                measured --vh instead of stretched vh
  sticky-e-sobreposicao.md     sticky outside grids that hold full-width blocks
  texto-em-linhas.md           line-by-line text that passes the text gate, li > span
  secoes/                      section format menu: one .md and one minimal .html per format
  rastreamento.md              Meta Pixel and GA4 snippet (IDs as variables) and the 5 events
  auditores.md                 the 9 lenses, verdict schema, cycle rules, taste pass
  preferencias-de-design.md    taste rules measured on real corrections (generic)
  anti-vibe-coding.md          the V1 to V15 visual AI tells
  copy-servico-local.md        short copy model for local services
  page-types.md                section models per page type
  assets-sem-chave.md          freely licensed photos and how to credit them
  gate-etapas.md               evidence fields per step
  arquivo/                     v2 references, outside the flow (kept for lookup only)
  projects/EXAMPLE.md          per-project template (copy it to <project>/contexto-do-projeto.md; real notes never live in the skill folder)
  sessions/EXAMPLE.md          per-session template (copy it to <project>/sessoes/YYYY-MM-DD.md; real notes never live in the skill folder)
scripts/                       gates, capture, audit registry, tests, rodar-testes.mjs (whole suite), test-portabilidade.py (portability guard)
.github/workflows/             portabilidade.yml (suite on Windows, macOS and Linux)
.gitattributes                 LF line endings for scripts
data/                          optional design database (CSV)
hooks/pagina-skill-inject.py   optional trigger hook
```

## What is new in 3.5.9

- `scripts/rodar-gates.mjs` runs every mechanical gate of step f in one command, in parallel (browser cap derived from the machine, 1 to 4), one local server per gate, and prints a single consolidated report with PASS or FAIL per gate, timings and the full failure text; exit code 1 if any gate fails. It only calls the existing gate scripts with their documented arguments. Options: `--so`, `--reprovados` (re-run only the failed ones), `--paralelo`, `--confirmar-sozinho`.
- Measured on a real test page: 426 s serial versus 197 s parallel, with identical verdicts and failure text for all 15 gates on a good page and on a deliberately broken one.
- `assets-search.py --folha sheet.png` builds ONE numbered contact sheet of the result thumbnails (same numbering as the text list), honouring the pause between calls and HTTP 429 handling.
- **Motion gate measures reduced motion.** With `prefers-reduced-motion: reduce`, the gate now fails when any animation or transition is still running after load or while scrolling, and names the element and property. Before, it only checked smooth scrolling, and two real defects passed green.
- Also: `data-assinatura` lets the signature photo repeat across its sections (one photo only), `wave.py reabrir --motivo` reopens round 1 after a large owner-requested change between rounds, the auditor budget counts until the answer arrives, and the session log goes in the project folder, never in the skill folder.
- Known limit: in 1 of 6 runs on a good page, `gate-responsivo` failed only in parallel mode (machine under load); `--confirmar-sozinho` re-runs a failed browser gate alone and takes that verdict. That option was only proven with fake gates.

## What is new in 3.5.8

Fixes from a second end-to-end test (`ACHADOS` N1 to N21): capture, photo search, image, truth and icon gates, motion, click proof, the auditor briefing, the video script, and one new motion recipe.

- **Reference capture sees blank pages.** A new state `vazia` catches a first screen that is a flat sheet (97% or more of one colour: a hero video that did not render) and a middle print that is one colour with photos that never loaded; the script now waits for the visible photos (up to 6 s) before the middle print, and a first screen above 80% of one colour is a warning. Print numbers continue from the highest prefix ever used (folder, `descartados/`, manifest), and `--remover <url>` takes an `ok` reference that does not fit out of the manifest and moves its PNG files.
- **Photo search.** `assets-search.py --type commons` drops police-evidence scans (`EFTA`), dollhouses, horse trailers and museum collections, says how many, and takes `--autor` and `--categoria` (the Commons pays off when you search by author or category). Every item shows a 500 px thumbnail and, when the photo is wide enough, the 1920 px hero URL; the reference explains that the Commons only serves 500, 960, 1280 and 1920 px. A table of starting names per craft unblocks the reference search.
- **Image gate.** The credit is matched to its photo by the origin link in the credit item, so ten photos by one author no longer fail each other; without that link, a quoted title is accepted if it belongs to any photo of the same author, and a title that belongs to none still fails. A real title with a hyphen ("Close-up") passes. "Imagens ilustrativas" (plural) counts as the notice, and the message says whether the text is below the first screen or was not found.
- **Truth gate.** The animated counter of the `vagas-que-se-preenchem` recipe stays inside its sentence and its heading opens its own section; a formatted phone number matches the digits-only number in the brief (a number that is not in the brief, or a promise next to it, still asks for a line).
- **Icon gate.** The message tells you to copy the icon motif, letter by letter, into a `data-desenho` and shows the ones the page has (the check itself is unchanged).
- **Real photo in the signature moment.** New recipe `foto-que-se-monta` (the 16th): a real photo of the product assembles in strips until it is whole, with an optional label on top; reduced motion and no-JS show the full photo. For physical products (furniture, food, real estate, fashion) the signature moment is a real photo, never a drawing; `gate-composicao.mjs --produto-fisico` warns (does not fail) when it is SVG only.
- **Motion gate.** It recognises the safety net inside a larger `<script>`, names the element that arrives still, and explains `animation-delay` in its message. The button contrast check looks at all four sides and says where it measured (a button right below a brand-coloured block no longer fails; a button inside a block of its own colour still does).
- **Click proof and video.** A proof click on an external link (WhatsApp) is cancelled on the page, so the after-print shows the page; the video script validator lists every broken limit at once and prints the limits.
- **Auditor briefing.** `pacote-auditoria.py` now carries the project folder, the 9 lenses, the criteria, the schema, every reference capture and the 360 and 320 px screens.
- Known limits: the stair animation below the mobile fold (N15), `animation-delay` (N16) and chained script edits (N18) are written rules and clearer messages, not new gates; `--produto-fisico` is not switched on by the workflow by itself.

## What is new in 3.5.7

- Late `IntersectionObserver` callbacks no longer play transitions after the person scrolled past (`.instantaneo` jumps to the end state); the motion gate names the first animation it caught off-screen; the visual gate test is split into three files by gate family (same 85 controls, guarded by `test-gates-visuais-cobertura.py`).

## What is new in 3.5.6

Fixes from an end-to-end test where a student built a real page with the skill and logged every stumble (`ACHADOS`, A1 to A13).

- **Reference capture judges what it captured.** `capturar-referencias.mjs` reports `ok`, `bloqueada` (HTTP 401/403/429, "Forbidden", "Just a moment", captcha), `quebrada` (HTTP 400+, no stylesheet applied, empty page) or `coberta` (a modal covering more than 40% of the window after trying to close the cookie notice), with the reason. It exits non-zero until 6 good references exist, and `--limpar-ruins` moves the bad ones out. `gate-referencias.py` fails a reference marked bad and accepts a really short page whose middle print equals its first screen. `references/pesquisa-de-referencias.md` says where to look when search only returns classifieds and shops.
- **Truth gate fits the workflow.** Without `index.html` (copy step) it checks only the support table against the brief and says so; citations may cross `;`, `.` and line breaks (a citation that is not in the brief still fails); image credits (`data-credito`, `id="creditos"` or class `creditos`) and bare licence identifiers are not promises; a missing line prints a ready-to-paste row grouped by section; a PLAN-vs-`sustentacao.md` drift is a warning. A short label such as "5 anos" inherits a promise already supported in the same section, only with the same number and unit.
- **Second photo route.** When Openverse does not answer, `assets-search.py` falls back to the Wikimedia Commons (same output and licence fields, only CC0, CC BY, CC BY-SA and public domain, pause between calls, HTTP 429 handled) and says which route answered; `--type commons` asks for it directly.
- **Icon line in the PLAN.** `Ícone do site: <motivo>` is in the PLAN model, required by `gate-plano.py` and by the stage 2 registration.
- **Commands and text.** The "next command" the scripts print carries the full skill path (`scripts/lancador.py`); every script message has correct accents (`test-acentuacao.py`).
- **Motion recipes.** Colour-panel text matches the code (0.8 + 0.15 + 0.8 = 1.75 s); the signature recipe now defines `colunas`; the pair "title + vertical list" declares `data-assimetrico`; the opening recipe keeps its final state with `.pronto`; tests check that no recipe JS uses an undefined name and that times in the text exist in the code.
- **Second round (A14 to A25).** Credit blocks no longer hide commercial promises; the skip-to-content link is not an action button; fixed-space failures name the elements; `data-assinatura` marks the signature drawing; the contrast gate ignores invisible strokes; the signature recipe has a phone variant and no CSS transition outliving the section; the credits model has a 44 px link pattern; failed registrations tell what to redo in order; `plano-para-secoes.py` builds `secoes.json` from the PLAN; `baixar-fontes.mjs` downloads Google Fonts (latin subset, woff2); the `--click` proof never leaves the test page.
- **Third round.** Timer-driven recipe animations jump to their end state when the section leaves the window (the CI failure); the motion gate proves the page without its script (blocked and 7 s late) and the base recipe ships the safety net; the lens that compares with references lists the weak axes instead of ordering a rebuild; the auditor gets a ready briefing with a time and call budget; stock photos with a person's name in a testimonial fail unless the brief declares a fictional test business; `gerar-og-image.mjs` builds the 1200x630 preview.
- **Fourth round (A30 to A33).** The last audit round orders: open critical or regression = do not deliver, otherwise deliver with caveats (a failed references lens is a caveat, never an order to rebuild); round 2 shows which lens scores were kept from round 1; `gate-etapas.py registrar 5` refuses a cycle that ended in do-not-deliver; `gate-etapas.py revalidar --motivo` handles a mid-way brief change without skipping a stage; the audit package asks whether the brief reflects the person's last request.
- **Proof screenshot waits for the entrance** (up to 4 s, says how long) and freezes finished entrances so the full-page print does not restart them.

## What is new in 3.5.5

- Works on Windows, macOS and Linux, guarded: `scripts/test-portabilidade.py` fails the suite on a Mac-only command, a fixed `/tmp`, text read or written without `encoding=`, a Mac-style loose Python command name, or a shell call in code. It proves itself on planted bad and good examples first.
- Every Python command in the texts is `node <skill-dir>/scripts/py.mjs <script>.py`; `checar-ferramentas.py` prints the install command for the user's own system and names the exact Python that lacks Pillow.
- `node scripts/rodar-testes.mjs` runs the whole suite in one command on any system (`--so-portateis` runs only the tests that need neither a browser nor Pillow/numpy).
- `.github/workflows/portabilidade.yml` runs it on Windows, macOS and Linux with Node 22 and Python 3.12.

## What is new in 3.5.4

- One independent auditor now runs the 9 lenses in a single pass instead of one subagent per lens (the 9 lenses stay as criteria; registration in `wave.py` is still one record per lens).
- `scripts/pacote-auditoria.py` gathers and checks the evidence package once (exit 1 if a required item is missing or older than the last page change); the auditor reads it and does not capture screens again.
- `wave.py rodada` caps the cycle at 2 rounds and always closes after the second one; critical, regression, false content and pending independent audit are never relaxed. A third round only with `--rodada-extra-pedida`.
- Round 2 is a conference of the round 1 findings, not a new audit.

## What is new in 3.5.3

- **Motion recipes** (`references/receitas-de-movimento.md`): the animations of the page the owner approved, as copyable recipes with the exact curve (`cubic-bezier(.2,.8,.2,1)`), durations and delays, the `.no-js` and reduced-motion fallbacks and the mobile cost. The PLAN's animation column now picks a recipe by name or declares `criação nova: <reason>`. `references/receitas/demo.html` runs all of them; `scripts/provar-receitas.mjs` proves in Chromium that every block changes pixels, that nothing is hidden with JavaScript off, and that reduced motion shows the same text. The colour-panel navigation recipe (the effect the owner liked in a prototype) is hardened: it only intercepts plain clicks on marked same-page links, covers 100% of the window, always releases the page (3 s ceiling), keeps focus, URL and the back button working, and is proved by `scripts/provar-painel.mjs`. The line-by-line text recipe re-splits after the font loads and when the width changes (`scripts/test-linhas.cjs` reproduces the defect with the original code).
- **Motion lens aligned with the approved page**: the motion-auditor and AI-tell 2 now reject the SAME generic fade applied to everything, not the number of revealed items; one curve and one duration scale, each item entering when it reaches the screen, plus moments tied to the content.
- **Scroll proof video** (`scripts/gravar-video.js`, `scripts/video/`, `roteiro-pagina.json`): records desktop and mobile from top to bottom at reading pace with Playwright's native recorder (no ffmpeg of your own, no OS-specific tool), plus a contact sheet per profile. Duration band 10 to 90 s in this skill. `gate-etapas.py registrar 5` now requires the two `.webm` files.

## Tests

Run from the repository root, on any system:

```bash
node scripts/rodar-testes.mjs                 # the whole suite, one result per file, exit 1 if any fails
node scripts/rodar-testes.mjs --so-portateis  # only tests that need neither a browser nor Pillow/numpy
node scripts/rodar-testes.mjs --lista         # what would run
```

Or one at a time (the `.py` tests through the launcher, the `.cjs` ones with Node):

```bash
node scripts/py.mjs test-checar-ferramentas.py
node scripts/py.mjs test-uso-ferramentas.py
node scripts/py.mjs test-gate-referencias.py
node scripts/py.mjs test-wave.py
node scripts/py.mjs test-pacote-auditoria.py
node scripts/py.mjs test-gate-etapas.py
node scripts/py.mjs test-gate-sem-kicker.py
node scripts/py.mjs test-classes-mortas.py
node scripts/py.mjs test-search.py
node scripts/py.mjs test-docs.py
node scripts/py.mjs test-preferencias.py
node scripts/py.mjs test-publicacao.py
node scripts/py.mjs test-gate-verdade.py
node scripts/py.mjs test-imagens.py
node scripts/py.mjs test-relatorio.py
node scripts/py.mjs test-gate-plano.py
node scripts/py.mjs test-secoes.py
node scripts/py.mjs test-animacao.py
node scripts/py.mjs test-receitas.py
node scripts/py.mjs test-portabilidade.py
node scripts/test-painel.cjs
node scripts/test-receitas-navegador.cjs
node scripts/test-linhas.cjs
node scripts/test-roteiro-de-video.cjs
node scripts/test-gravar-video-integracao.cjs
node scripts/test-previa-direcoes.cjs
node scripts/test-capturar-referencias.cjs
node scripts/test-gates-visuais-responsivo.cjs   # e -composicao.cjs, -movimento.cjs
node scripts/test-gates-v35.cjs
node scripts/test-print-cabecalho.cjs
node --test scripts/extrai-identidade.test.mjs
```

A test that cannot run on a machine (a local file that is not in Git, a missing browser) prints `PULADO: <reason>` and the summary lists it; in CI a skip for a missing Playwright counts as a failure.

The visual tests use Chromium, ffmpeg and local synthetic pages. They prove that each gate fails on the defect it exists for; they do not approve a client's design. Reading the screenshots stays mandatory.

## Security

- No secret, token, account ID or client data lives in this repository. Optional tools read their keys from the environment (for example `TWENTYFIRST_API_KEY`, `PEXELS_API_KEY`); the checker never prints them.
- Client material, project memory and session notes (`references/projects/*`, `references/sessions/*`, `evidencias/`, owner-specific preferences) are gitignored.
- The reference capture never logs in, never clicks cookie or consent banners and never accepts terms.
- Pages built outside their final domain ship with `noindex`, so a test copy of a real client's page does not compete with the client in search.

## License

Proprietary. Exclusive to **Júlio Couto / iAutomate**. All rights reserved. No redistribution, resale, or reuse without express permission.
