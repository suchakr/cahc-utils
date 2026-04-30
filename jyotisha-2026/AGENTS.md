# AGENTS.md

## Purpose

This repository is an agentic exploration lab. Prefer low-churn execution: turn prompts into exploration briefs, code, outputs, and index updates with minimal user file handling.

## Core Rules

- Use `uv` for environment and dependency discipline.
- Prefer `uv run python ...` for runnable scripts.
- Prefer `uv add ...` and `uv sync` for dependency changes.
- Do not create ad hoc virtualenv workflows unless explicitly asked.
- Treat `lab/` as the publishable browsing surface.
- Keep repo structure lightweight. Add architecture only when repeated reuse justifies it.

## Exploration Intake Workflow

When the user proposes a new study or visualization:

1. Interpret it as a request to create a new exploration unless the user says otherwise.
2. Ask concise clarifying questions only where assumptions would materially affect the result.
3. Choose a clear slug.
4. Use `uv run python scripts/new_exploration.py "<title>" --slug <slug>` when it fits.
5. Create an exploration brief at `explorations/<slug>.md`.
6. Create or update a runnable script in `scripts/`.
7. Put outputs in `lab/<slug>/`.
8. Add an entry to `lab/index.html`.

## Titles, Slugs, and Paths

- In the UI, use human-readable titles as the visible labels.
- Use slugs only for paths, filenames, sharing, and internal identity.
- When linking exploration content inside `lab/`, prefer explicit file targets such as `.../index.html` rather than folder paths, because local `file://` browsing may fall back to directory listings.

## Upstream Datasets

- `../datasets/` is a read-only upstream source.
- Agents may read from `../datasets/` but must not write there.
- At exploration start, check whether useful upstream seed files already exist before inventing new inputs.
- Seed examples worth checking early:
  - `../datasets/n28_good_meta.csv`
  - `../datasets/nakshatras/n28_good_meta.csv`
  - `../datasets/naks-visible-rising-az.tsv`
  - `../datasets/nakshatras/naks-visible-rising-az.tsv`
  - `../datasets/kuru_naksrise_-1500.csv`
  - `../datasets/naks_sun_rise_set/kuru_naksrise_-1500.csv`
  - `../datasets/n90_heliacal_rising_times_for_-1600.csv`
  - `../datasets/nakshatras/n27_full_meta.csv`

If an upstream dataset becomes a recurring dependency, add a short note to `memory/datasets.md`.

## Documentation Churn Policy

- Do not update `README.md` for routine explorations.
- Do not update `AGENTS.md` unless the workflow itself changed.
- Use `memory/` only for durable cross-exploration context.
- Most new work should touch:
  - `explorations/<slug>.md`
  - `scripts/<slug>.py` or a clearly related reusable helper
  - `lab/<slug>/...`
  - `lab/index.html`

## Lab UX

- `lab/` should start with sensible branding and navigation.
- Keep the UX easy to tune later by prompt without structural rewrites.
- Prefer clean static HTML, CSS, and light JavaScript over framework complexity.
- `lab/index.html` is a browsing shell, not a landing-page essay.
- Use a narrow exploration list on the left and the exploration reading surface on the right.
- Each exploration page should make it easy to find plots, tables, and narration in one scroll.
- Prefer low-ceremony presentation inside exploration pages:
  - light separators instead of card-heavy boxed layouts
  - compact spacing
  - if tabs already label the active mode, do not repeat the same label again as a bold body heading
  - download/open affordances only where they are genuinely useful
- Inline preview tables are preferred over forcing a separate open/download step for routine inspection.
- If an asset link under `file://` behaves like a normal browser open rather than a download, do not label it as a guaranteed download action.

## Reader-Facing Content

- Do not surface implementation chatter or setup-conversation artifacts in reader-facing narration.
- Summaries should describe the result, not the conversation that produced it.
- Prefer flat, readable bullets or short prose over awkward nested list structures.

## Plotting Conventions

- Matplotlib defaults are usually too small for this lab; enlarge titles, axes, ticks, and legends for comfortable reading.
- Add subtle reference guides when they carry domain meaning.
  - Example: azimuth `90°`, declination `0°`.
- If event timestamps may be reused in Stellarium or similar tools, include Julian Dates in exported tables.
