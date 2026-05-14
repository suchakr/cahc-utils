# Nakshatra Precession Story Authoring Skill

Use this when authoring or editing build-time 3D stories for the `nakshatra-precession-explorer` lab page.

## Goal

Create valid VyomaSutra that drives the existing 3D sky without writing JavaScript or hand-authored JSON. Stories should be small, readable, and easy to tune in the page's Stories dock.

## Files

- Put author-facing stories in `stories/nakshatra-precession-explorer/`.
- Prefer `<id>.vysu` as source. Use `# title: ...`, `# version: 1`, and optional discovery metadata comments such as `# featured: true`, `# group: Tours`, `# tags: nakshatra, sectors`, and `# order: 20`.
- JSON is an internal runner/debug format, not the authoring target for this skill.
- Legacy `<id>.json` files may exist, but do not create new stories in JSON unless explicitly asked.
- The accepted vNext compiler is TypeScript-first and Node-based. Use the project Node compile command after it lands, expected shape: `node scripts/compile-vysu.mjs nakshatra-precession-explorer`.
- The old Python compiler should be removed after the Node compiler and compatibility fixtures pass; do not add new VyomaSutra grammar features to Python.
- The fast compiler treats current `.vysu` files as the authoring source of truth and should prevent stale embedded stories from remaining visible.
- Run `uv run python scripts/nakshatra_precession_explorer.py` only when data, page structure, generated stories, or major assets change.
- The generated deployable page emits `assets/css/explorer.css` as the live CSS and `assets/js/three-explorer.js` as an inspectable copy of the inline 3D/VyomaSutra module. The module stays inline in `index.html` so `file://` viewing remains functional.
- Run the lab through `netlify dev --dir lab` from the `jyotisha-2026` repo root for behavior closest to deploy.

## Discovery Metadata

Build-time `.vysu` files can start with metadata comments:

```text
# title: Tour of Nakshatras
# version: 1
# featured: true
# group: Tours
# tags: nakshatra, sectors, star-shapes
# order: 20
```

- `# featured: true` makes the story eligible for the top 3D story pill row.
- The pill row shows at most five featured stories after applying the search filter.
- The Stories dock select uses the same searchable story inventory.
- `# group:`, `# tags:`, `# order:`, title, and id are searchable or sortable metadata only; they do not change runtime behavior.

## VyomaSutra Stage 1 Grammar

Use this authoring surface for new `.vysu` work. Stage 2 ideas such as `draw`, target ranges, `blink`, `glow`, primitive target hierarchy, and numeric vector math should warn until implemented.

```text
program          ::= line*
line             ::= statementList? comment? newline
statementList    ::= statement (";" statement)*
statement        ::= timedStatement | command | timedBlock

timedStatement   ::= timing command
timedBlock       ::= timing "{" statementList "}"
timing           ::= "at" time | "after" duration | signedDuration

command          ::= stageStmt | visibilityStmt | styleStmt | cameraStmt |
                     travelStmt | gridStmt | captionStmt | labelStmt |
                     clearStmt | waitStmt | seqStmt | flashStmt | effectStmt |
                     fullscreenStmt | defaultsStmt

visibilityStmt   ::= visibilityVerb targetList transitionArg*
visibilityVerb   ::= "show" | "hide" | "reveal" | "rollout" | "fade"
styleStmt        ::= "style" targetList styleArg+
flashStmt        ::= ("flash" | "pulse") targetList effectArg*
captionStmt      ::= ("caption" | "say" | "title") quotedText captionArg*
labelStmt        ::= "label" identifier quotedText labelArg*
clearStmt        ::= "clear" ("label" identifier | "labels")

targetList       ::= targetAtom (("," | "and") targetAtom)*
targetAtom       ::= sigilNak | namedTarget | dottedTarget | groupTarget
groupTarget      ::= "guides" | "sky" | "poles" | "seasons"
durationArg      ::= "over" duration | legacyDurationTuple | bareDuration
seqStmt          ::= ("seq" | "sequence") duration
```

Target lists require commas. `and` is readability sugar. Do not use bare-space target lists, because command properties become ambiguous.

## Timing

- Each scope has a timing cursor. Top-level starts at `0`; each timed block starts with a local cursor at its block base.
- No timing means "start at the current scope cursor" and does not advance the cursor.
- `;` separates statements but does not sequence them.
- `wait 500` advances the current scope cursor by 500 ms and emits nothing.
- `seq 200` at top level sets the default sequence step for later timed blocks.
- `seq 200` inside a timed block advances the block clock by 200 ms before each following emitted command.
- `seq 0` disables sequence stepping in that scope.
- `+500 command` advances the current scope cursor by 500 ms, then schedules the command there.
- `after 500 command` is canonical relative timing and behaves like `+500 command`.
- `at 12000 command` is absolute timing in the current scope and does not move the cursor.
- `over 900` is duration, never cue position.
- Timing operators can apply to blocks. Inside a timed block, `at N` is local to the block base, while `+N` and `after N` advance the block-local cursor.

```text
at 0 {
  caption "Start" over 1000
  reveal $naks
  +50 reveal *naks
}

at 1000 {
  show equator, ecliptic.circle, nsAxis
  +100 flash NP
  at 50 caption "local block time" over 800
}

after 1111 { caption "relative block A" }
after 2222 { caption "relative block B at 3333 ms" }

seq 333
at 2000 {
  stage blank twilight year -1800
  camera pos -147.464,73.504,234.757 target 0,0,0 fov 48
  seq 100
  caption "Sequenced caption"
}
```

## Commands

Use VyomaSutra commands, not JSON action objects:

- `caption`: show fading text.
- `show` / `reveal`: transition a named visual layer to visible.
- `hide`: transition a named visual layer to hidden.
- `style`: apply visual styling and persist until changed, cleared, or reset.
- `camera` / `move`: animate camera position and/or target.
- `travel` / `epochTravel`: animate epoch from one year to another.
- `flash`: briefly emphasize a target without changing durable visibility.
- `pulse`: repeated flash emphasis.
- `label`, `clear label`, `clear labels`: persistent annotations.
- `fullscreen` / `exitFullscreen`: enter or leave theater view for the 3D canvas.
- `cut <preset>` is sugar for `camera <preset> over 0`.
- `show` and `reveal` are aliases in Stage 1; use explicit modes such as `show naks rollout`, `show stars fade`, or `show grid instant` when intent matters.

Do not invent commands. Do not include JavaScript.

## Defaults

Command defaults:

| Command       | Default duration |
| ------------- | ---------------: |
| `caption`     |           `1200` |
| `reveal`      |  target-specific |
| `hide`        |  target-specific |
| `camera`      |           `1000` |
| `epochTravel` |           `5000` |
| `flash`       |            `900` |

Transition defaults:

| Target                | Default mode | Default order | Default duration |
| --------------------- | ------------ | ------------- | ---------------: |
| `eclipticGrid`        | `stagger`    | `default`     |           `1000` |
| `equatorialGrid`      | `stagger`    | `default`     |           `1000` |
| `eclipticNakSegments` | composite    | `ecliptic`    |     target parts |
| `referencePlanes`     | `fade`       | `default`     |            `700` |
| `eclipticPlane`       | `fade`       | `default`     |            `700` |
| `equatorialPlane`     | `fade`       | `default`     |            `700` |
| `nsAxis`              | `fade`       | `default`     |            `700` |
| `ecliptic`            | composite    | `ecliptic`    |     target parts |
| `eclipticBand`        | `fade`       | `ecliptic`    |            `900` |
| `eclipticDividers`    | `rollout`    | `ecliptic`    |           `1200` |
| `eclipticLabels`      | `stagger`    | `ecliptic`    |           `1200` |
| `eclipticPoles`       | `fade`       | `default`     |            `600` |
| `stars`               | `fade`       | `default`     |            `900` |
| `nakshatras`          | `rollout`    | `ecliptic`    |           `1800` |
| `nakshatraLines`      | `rollout`    | `ecliptic`    |           `1800` |
| `nakshatraLabels`     | `stagger`    | `ecliptic`    |           `1200` |
| `polarItems`          | `rollout`    | `default`     |           `1600` |
| `northPolarItems`     | `rollout`    | `default`     |           `1200` |
| `southPolarItems`     | `rollout`    | `default`     |           `1200` |
| `poleTrack`           | `rollout`    | `default`     |           `1100` |
| `precessionCircle`    | `fade`       | `default`     |            `900` |
| `seasonalFrame`       | `rollout`    | `default`     |           `1300` |
| `overlay`             | `fade`       | `default`     |            `500` |

Implementation note: `rollout` currently stages objects or groups in order; it is not yet true geometric line drawing along each polyline. For `stars`, rollout reveals one nakshatra star group at a time, followed by special stars such as Agastya. For `nakshatras`, rollout reveals one complete stick figure at a time.

## Reveal and Hide

Prefer `reveal`/`hide` when a story should stage visual layers:

```text
reveal nakshatras
hide nakshatras rollout reverse over 1200
show equator, ecliptic.circle, nsAxis
```

Supported targets:

- `eclipticGrid`
- `equatorialGrid`
- `@referencePlanes` (`referencePlanes`, `refs`)
- `eclipticPlane`
- `equatorialPlane`
- `nsAxis`
- `@eclipticNakSegments` (`eclipticNakSegments`, `nakSegments`, `naksSegments`, `eclipticSegments`)
- `eclipticBand`, `eclipticDividers`, `eclipticLabels`
- `@eclipticPoles` (`eclipticPoles`), `NEP`, `SEP`
- `stars`
- `@naks` (`naks`, `nak`, `nakshatra`, `nakshatras`) = stars + lines + labels
- `*naks` = nakshatra stars/dots
- `$naks` = nakshatra stick/line figures
- `nakshatraLabels`
- `@polarItems` (`polarItems`)
- `@northPolarItems` (`northPolarItems`, `northPolar`)
- `@southPolarItems` (`southPolarItems`, `southPolar`)
- `@poleTrack` (`poleTrack`, `polePath`)
- `precessionCircle`
- `@seasonalFrame` (`seasonalFrame`, `seasons`, `rtu`, `rtus`)
- `overlay`
- `NP`, `SP`
- `equator`, `VE`, `SS`, `AE`, `WS`
- `agastya`, `thuban`, `polaris`, `matsya`, `sisumara`
- sigil nakshatra targets such as `$ash`, `*ash`, and `@ash` for flash/focus-style cues

Stage 2 memory: dotted forms such as `nak.ash`, `nak.ash.stars`, `sector.1.label`, `star.thuban`, and `poleTrack.circle` are intentionally not implemented yet. They should warn in Stage 1.

Any command that accepts a target may accept a comma-separated target list:

```text
show equator, nsAxis
flash $ash, *ash over 650
style NP, SP yellow alpha .8
```

Supported modes are `instant`, `fade`, `stagger`, and `rollout`. Most stories should omit `mode`, `order`, `direction`, and `duration`; defaults are target-specific.

## Stage and Style

Use `stage` for scene setup and `style` for visual tuning:

```text
stage blank night year -1800
style equatorialGrid color red alpha %28
style nsAxis, equator color #a7b4c7 alpha .35
style @naks color #8eaccb alpha .8 labelSize 5
style *naks dotSize 2.6 dotAlpha %80
show NP color gold labelSize 5 labelAlpha %80 over 900
```

Use compact grid tuning when needed:

```text
grid ecliptic 15 blue
grid equatorial 15 red
```

Lower step values make denser grids. Keep values in the practical `5` to `90` degree range.

## Camera

Camera commands may be partial. Missing coordinates keep their current values.

```text
camera pos -147.464,73.504,234.757 target 0,0,0 fov 45 over 900
camera topDome over 1200
cut topDome
```

`cut <preset>` is sugar for `camera <preset> over 0`. Unsupported preset names must warn.

## Captions

Keep captions short. They should support the visual, not narrate everything.

`fadeIn` and `fadeOut` set the actual opacity-transition duration in milliseconds. `duration` is the total caption lifetime from cue start; fade-out begins at `duration - fadeOut`.

VyomaSutra captions accept color names/hex colors and `size NUMBER`. Prefer explicit duration and fade syntax:

```text
caption "Thuban era" gold size 4 over 1500 fadeIn 300 fadeOut 300
caption "Thuban era" gold size 4 over 1500 fade 300:300
```

The legacy tuple form `1500:300:300` is still accepted for compatibility. For non-caption commands, tuple values beyond duration should warn or be ignored.

Persistent labels use separate syntax:

```text
label title "Visualize Precession" at screen 8 dy 24
label pole "Moving pole" at target NP dx 12 dy -8
clear label pole
clear labels
```

## Epoch Travel

Use epoch values available in the explorer range. `step` should usually match the page epoch step.

In VyomaSutra, `over` controls total travel animation duration, `rate` controls epoch speed, and `step` controls sampling granularity:

```text
travel year -1800 to -800 over 5000 step 100y
travel year -4000 to -2800 rate 200y/s step 50y
```

## Authoring Rules

- Start with `stage blank ...` if the scene needs a clean stage.
- Use timed blocks for scene setup when several commands share a local time origin.
- Prefer a sequence of simple cues over one large patch.
- Prefer target lists over repeated identical commands when the same command applies to multiple targets.
- Do not use `foreach` or bespoke macros such as `tour naks`; generated canned stories should emit ordinary readable `.vysu`.
- Use `stage` for scene setup, `style` for visual tuning, and `reveal`/`hide` for staged visibility changes.
- Test in the 3D Stories dock, then keep the `.vysu` source as the authoring truth.

> Should the story authoring skill even worry about the story JSON ?
>
> I think the skill should just output the VyomaSutra. This will make the skill more focused and easier to maintain. It will also make it easier to test the skill.
>
> **State: accepted.** This skill should focus on VyomaSutra authoring. JSON is an internal runner/debug format and belongs in the PRD/compiler implementation notes, not as the main skill surface.

> The JSON layer is an implementation detail. The skill should not need to know about it. It should just output VyomaSutra. The design and implementation of JSON should be done by the story runner ( 3D stories dock) or some such. The story runner will be responsible for converting the VyomaSutra to JSON and then running the story.
>
> **State: accepted.** New stories authored through this skill should be `.vysu`; direct JSON should only be used when explicitly requested for debugging or legacy compatibility.
