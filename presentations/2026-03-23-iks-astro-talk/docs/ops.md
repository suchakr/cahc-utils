# Operations Guide

This document explains the main runnable helpers under `ops/`, what order they usually appear in, and what each one produces.

The files in `ops/` are not numbered. The ordering lives here in the docs so filenames can stay descriptive.

## Typical Order

1. Build the slide decks.
2. Rehearse or run a Stellarium script live.
3. Record selected Stellarium sequences.
4. Compress work videos into lighter web-friendly versions.
5. Stage final outputs into the CAHC portal repository.

## Command Summary

### `./ops/make-slides.sh`

Purpose:
Build `slides-session-1.md` and `slides-session-2.md` into HTML and PDF files under `out/`.

Outputs:

- `out/slides-session-1.html`
- `out/slides-session-1.pdf`
- `out/slides-session-2.html`
- `out/slides-session-2.pdf`

Notes:

- Expects Marp at `/opt/homebrew/bin/marp` unless `MARP_BIN` is overridden.
- Safe to rerun.

### `./ops/stelplay`

Purpose:
Launch a curated Stellarium script from `ssc/` using a short `sXX` handle.

Common examples:

```bash
./ops/stelplay
./ops/stelplay s14
./ops/stelplay s14 --exit
./ops/stelplay s25 --record
```

Outputs:

- Plain playback launches Stellarium directly.
- Recording writes high-resolution captures under `out/work-videos/hires/` by default.

Notes:

- Script discovery is repo-relative, so the command can be run from anywhere.
- See `docs/stelplay-prd.md` for the design notes and option contract.

### `./ops/compress-work-videos.sh`

Purpose:
Convert the high-resolution recordings under `out/work-videos/hires/` into lighter web versions, then trim and copy final MP4s into `out/`.

Inputs:

- `out/work-videos/hires/s11.mp4`
- `out/work-videos/hires/s12.mp4`
- `out/work-videos/hires/s13.mp4`
- `out/work-videos/hires/s14.mp4`
- `out/work-videos/hires/s21.mp4`
- `out/work-videos/hires/s22.mp4`
- `out/work-videos/hires/s23.mp4`
- `out/work-videos/hires/s24.mp4`
- `out/work-videos/hires/s25.mp4`

Outputs:

- `out/work-videos/web/*.mp4`
- `out/s11.mp4` through `out/s25.mp4` as available

Notes:

- The trim offsets are currently hard-coded per video.
- Safe to rerun; existing final outputs are skipped.

### `./ops/stage-to-cahc-portal.sh`

Purpose:
Copy built slide and video outputs from `out/` into the author’s local CAHC portal checkout.

Inputs:

- `out/*.html`
- `out/*.pdf`
- `out/*.mp4`

Notes:

- This script is author-specific because the destination path is local to one machine.
- It is useful for publication, not for general audience browsing.

## Directory Intent

- `ops/` contains runnable repo helpers.
- `docs/` contains human-readable explanations and workflow notes.
- `out/` contains generated artifacts only.

That split keeps the repository easier to understand for readers who are new to the project.
