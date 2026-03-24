# IKS Astronomy Tutorial Presentation

This repository contains the slide decks, Stellarium scripts, support assets, and operational helpers for the 2026-03-23 IKS astronomy tutorial sessions.

## Published Tutorial Page

For the polished public version of this tutorial, see:

- [CAHC tutorial page](https://cahc.jainuniversity.ac.in/tutorial/astronomy/cosmography/2026/03/23/iabc-tutorial.html)

If you are browsing the material, start with:

- `slides-session-1.md`
- `slides-session-2.md`
- `ssc/` for curated Stellarium demo scripts
- `out/` for built slide PDFs/HTML and exported demo videos

## Repo Map

- `ops/`
  Runnable helper scripts for common workflows.

- `docs/`
  Human-oriented documentation for the repo and its tools.

- `ssc/`
  Talk-ready Stellarium scripts, typically addressed by `sXX` shorthand.

- `scripts/`
  Support scripts, data notes, and benchmark material used during preparation.

- `pics/`
  Slide images and other visual assets.

- `out/`
  Generated outputs such as built slide decks and rendered videos.

## Common Commands

Run these from the repository root:

```bash
./ops/make-slides.sh
./ops/stelplay
./ops/stelplay s14
./ops/stelplay s25 --record
./ops/compress-work-videos.sh
./ops/stage-to-cahc-portal.sh
```

## Recommended Workflow

1. Build slides with `./ops/make-slides.sh`.
2. Rehearse or live-run a Stellarium script with `./ops/stelplay sXX`.
3. Record a finite Stellarium run with `./ops/stelplay sXX --record`.
4. Compress work videos for easier sharing with `./ops/compress-work-videos.sh`.
5. Stage final outputs to the CAHC portal repo with `./ops/stage-to-cahc-portal.sh`.

## Docs

- `docs/ops.md`
  Ordered workflow and script purposes.

- `docs/stelplay-prd.md`
  Design notes and CLI contract for `ops/stelplay`.

- `scripts/README.md`
  Narrow benchmark and environment notes for the support scripts under `scripts/`.

## Notes

- `ops/stage-to-cahc-portal.sh` is author-specific. It copies built assets into a local CAHC website checkout.
- `ops/stelplay` resolves scripts relative to this repository, so it does not depend on the caller's current working directory.
- `out/` is treated as a generated-artifacts directory; helper scripts now live under `ops/` instead of alongside outputs.
