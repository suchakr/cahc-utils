# jyotisha-2026

Agentic workspace for astronomy explorations, visualizations, and small utilities built with `astropy`, `stellarium`, and `uv`.

## Layout

- `src/jyotisha_2026/` reusable Python helpers
- `scripts/` runnable entrypoints for explorations and maintenance
- `lab/` the primary browsing surface for local use and Netlify publish
- `explorations/` one brief per exploration idea
- `memory/` compact durable context for humans and agents
- `references/` domain notes and external method references
- `tmp/` scratch space

## Operating Model

Humans describe an exploration in plain language. Agents are expected to:

1. Clarify the question only where scientific assumptions are missing.
2. Create or update an exploration brief in `explorations/`.
3. Implement or extend code under `src/` and `scripts/`.
4. Generate browseable outputs under `lab/<slug>/`.
5. Update `lab/index.html`.

## Browsing Model

- `lab/index.html` is a two-pane browser, not a homepage.
- Exploration titles are the visible navigation labels.
- Slugs are for paths, sharing, filenames, and agent identity.
- Each exploration should expose plots, embedded narration, and a table preview in one reading flow.
- When tabs already name the active view, do not repeat large in-body section titles for the same view.
- Large tables should be previewed inline and kept complete in CSV form.
- When browsing directly via `file://`, browsers can behave differently from HTTP for folder paths and asset links. Use explicit file paths where needed.

A minimal scaffold helper is available:

```bash
uv run python scripts/new_exploration.py "Agastya rise and set across epochs and latitudes"
```

## Agent Environment

This repository uses `uv` discipline for agent work.

- Run scripts with `uv run python ...`
- Manage dependencies with `uv add` and `uv sync`
- Keep dependency truth in `pyproject.toml`

## Publishing

`lab/` is the publish root for both local browsing and Netlify CLI deploys.

- Draft deploy: `./deploy.sh`
- Production deploy: `./deploy.sh --prod`

## Current Status

The lab is intentionally lightweight, but no longer empty:

- `heliacal-rising-27-naks` is the first completed plotting exploration.
- `nakshatra-precession-explorer` is the current active foundation, with accepted `Table` and `2D Sky` views and a `3D Sky` view that exists as a development baseline rather than final live polish.
