# Nakshatra Precession Story PRD

Status: phase 1 implementation
Parent exploration: `nakshatra-precession-explorer`
Authoring skill: `stories/nakshatra-precession-explorer/SKILL.md`
VyomaSutra PRD: `stories/nakshatra-precession-explorer/vyoma-sutra-prd.md`

## Purpose

Add a declarative story layer to the 3D sky so humans and agents can author guided visual explanations without writing JavaScript. Stories should drive the existing 3D state: visibility, epoch, camera, captions, and timing.

## Lifecycle

Phase 1 stories are build-time assets:

- authors create JSON files in `stories/nakshatra-precession-explorer/`
- the generator validates and embeds them into the exploration page
- each valid story appears as a pill in the 3D toolbar
- clicking a pill runs the story timeline
- the 3D Stories dock can load, edit, run, stop, reload, and copy embedded story JSON, but does not save edits back to disk

Later phases may add browser-side persistence and export, but the JSON schema should remain the same.

## Vocabulary

- `story`: named runnable timeline
- `cue`: one timed event in a story
- `at`: cue time, in milliseconds; numbers and numeric strings are absolute, signed strings are relative to the previous cue end
- `after`: legacy relative time after the previous cue end, in milliseconds
- `action`: cue operation
- `initial`: optional partial 3D state applied before the first cue
- `state`: partial 3D settings patch
- `target`: named visual layer for reveal/hide transitions
- `mode`: optional transition style; defaults are target-specific
- `camera`: camera position and target
- `epochTravel`: animated epoch change
- `caption`: transient centered text
- `reveal`: animated transition to visible
- `hide`: animated transition to hidden

Timing examples:

- `"at": 3000` runs at 3000ms from story start.
- `"at": "3000"` is equivalent to `3000`.
- `"at": "+500"` runs 500ms after the previous cue ends.
- `"at": "-300"` runs 300ms before the previous cue ends, allowing intentional overlap.
- If a cue omits `duration`, relative scheduling still uses the action's default duration.

## JSON Contract

Each story file is named `<id>.json`, and the filename stem must match the JSON `id`.

The canonical story language reference is `stories/nakshatra-precession-explorer/SKILL.md`. It contains the formal-ish grammar, action schemas, timing rules, supported targets, transition defaults, and authoring constraints. This PRD should not duplicate the full grammar.

VyomaSutra is the just-in-time mini-language authoring layer over this JSON contract. Its grammar and UX plan live in `stories/nakshatra-precession-explorer/vyoma-sutra-prd.md`; changes to VyomaSutra syntax should be made there before parser/compiler changes.

## First Scope

Implement only the minimum runner needed for prompt-authored stories:

- render one pill per story
- apply initial state
- show fading captions
- apply partial 3D state patches
- reveal or hide named visual layers with target-specific default transitions
- roll out stars by nakshatra group plus special stars, and nakshatra line art one complete stick figure at a time
- move camera to explicit or partial positions and targets
- animate epoch from one year to another
- cancel active story on manual camera/debug/light interaction
- expose a non-persistent in-page story editor for quick tuning

Phase 1 note: `set` cue `duration` is accepted as part of the schema, but `set` remains discrete. Use `reveal` or `hide` when a story needs staged emergence or disappearance.

## Non-Goals

- no browser-side story persistence yet
- no arbitrary JavaScript in stories
- no movie export yet

## Hello World

`precession-hello.json` proves the first path:

- start with most layers hidden
- show a centered title
- reveal grid, ecliptic, stars, nakshatra line art, seasonal frame, precession circle, and overlay
- animate epoch from `-1800` to `-800`
