# Nakshatra Precession Story Authoring Skill

Use this when authoring or editing build-time 3D stories for the `nakshatra-precession-explorer` lab page.

## Goal

Create valid VyomaSutra or story JSON that drives the existing 3D sky without writing JavaScript. Stories should be small, readable, and easy to tune in the page's Stories dock.

## Files

- Put author-facing stories in `stories/nakshatra-precession-explorer/`.
- Prefer `<id>.vysu` as source. Use `# title: ...`, `# version: 1`, and optional discovery metadata comments such as `# featured: true`, `# group: Tours`, `# tags: nakshatra, sectors`, and `# order: 20`.
- Generated JSON lives in `stories/nakshatra-precession-explorer/compiled/`; do not hand-edit compiled files.
- Legacy `<id>.json` files are still accepted and copied into `compiled/`.
- Run `uv run python scripts/compile_stories.py nakshatra-precession-explorer` after story-only edits. This avoids the astropy-heavy page rebuild and patches the existing lab page story payload.
- The fast compiler treats current `.vysu`/root `.json` files as the source of truth: stale compiled files and stale embedded page stories are removed from the generated story inventory.
- Run `uv run python scripts/nakshatra_precession_explorer.py` only when data, page structure, generated stories, or major assets change.
- The generated deployable page emits `assets/css/explorer.css` as the live CSS and `assets/js/three-explorer.js` as an inspectable copy of the inline 3D/VyomaSutra module. The module stays inline in `index.html` so `file://` viewing remains functional.
- Run the lab through `netlify dev --dir lab` from the `jyotisha-2026` repo root for behavior closest to deploy.

## Required Shape

```json
{
  "id": "story-id",
  "title": "Story Title",
  "version": 1,
  "initial": {},
  "cues": []
}
```

Required keys are `id`, `title`, `version`, and `cues`. `initial` is optional.

For `.vysu`, `id` comes from the filename stem and `title` comes from `# title: ...`.

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

## Formal-ish Grammar

```text
Story =
  {
    "id": string,
    "title": string,
    "version": number,
    "initial"?: StatePatch,
    "cues": Cue[] | CueMap
  }

CueMap =
  { Time: CueWithoutTime }

Cue =
  CaptionCue | SetCue | RevealCue | HideCue | CameraCue | EpochTravelCue |
  FlashCue | FullscreenCue

Time =
  number | numeric-string | signed-relative-string

CueBase =
  { "at"?: Time, "after"?: number }

CaptionCue =
  CueBase & {
    "action": "caption",
    "text": string,
    "duration"?: ms,
    "fadeIn"?: ms,
    "fadeOut"?: ms
  }

SetCue =
  CueBase & {
    "action": "set",
    "state": StatePatch,
    "duration"?: ms
  }

RevealCue =
  CueBase & {
    "action": "reveal",
    "target": Target,
    "mode"?: Mode,
    "order"?: Order,
    "direction"?: Direction,
    "duration"?: ms
  }

HideCue =
  RevealCue with "action": "hide"

CameraCue =
  CueBase & {
    "action": "camera",
    "camera": CameraPatch,
    "duration"?: ms
  }

EpochTravelCue =
  CueBase & {
    "action": "epochTravel",
    "from": year,
    "to": year,
    "step"?: years,
    "duration"?: ms
  }

FlashCue =
  CueBase & {
    "action": "flash",
    "target": Target,
    "duration"?: ms
  }

FullscreenCue =
  CueBase & {
    "action": "fullscreen" | "exitFullscreen"
  }
```

Types:

```text
Mode = "instant" | "fade" | "stagger" | "rollout"
Order = "default" | "ecliptic" | "reverse-ecliptic"
Direction = "forward" | "reverse"

Target =
  "eclipticGrid" | "equatorialGrid" | "eclipticNakSegments" |
  "referencePlanes" | "eclipticPlane" | "equatorialPlane" |
  "nsAxis" | "eclipticBand" | "eclipticDividers" |
  "eclipticLabels" | "eclipticPoles" | "stars" | "nakshatras" |
  "nakshatraLines" | "nakshatraLabels" | "polarItems" |
  "northPolarItems" | "southPolarItems" | "poleTrack" |
  "precessionCircle" | "seasonalFrame" | "overlay" |
  "NEP" | "SEP" | "NP" | "SP" |
  "equator" | "VE" | "SS" | "AE" | "WS" |
  "agastya" | "thuban" | "polaris" | "matsya" | "sisumara" |
  sigil-nakshatra-target
```

Use array `cues` for real stories. `CueMap` is accepted for compact experiments, but JSON cannot repeat keys like `"+500"`.

## Timing

Prefer ordered array cues.

- `3000` or `"3000"` means absolute milliseconds from story start.
- `"+500"` means 500ms after the previous cue ends.
- `"-300"` means 300ms before the previous cue ends.
- If a cue omits `duration`, scheduling still uses the action's default duration.
- `after` is supported as legacy relative timing, but prefer signed `at`.
- Keyed-object cues are accepted for quick experiments, but avoid them for real stories because JSON cannot repeat keys like `"+500"`.

## Actions

Use only these actions:

- `caption`: show centered fading text.
- `set`: apply a partial 3D settings patch.
- `reveal`: transition a named visual layer to visible.
- `hide`: transition a named visual layer to hidden.
- `camera`: animate camera position and/or target.
- `epochTravel`: animate epoch from one year to another.
- `flash`: briefly emphasize a target without changing durable visibility.
- `fullscreen` / `exitFullscreen`: enter or leave theater view for the 3D canvas.

Do not invent actions. Do not include JavaScript.

Every cue must have an `action`. A cue with a `camera` object but no `"action": "camera"` is invalid and will not run.

VyomaSutra also supports `style ...`; it compiles to JSON `set` cues, not a separate runtime action.

## Defaults

Action defaults:

| Action | Default duration |
| --- | ---: |
| `caption` | `1200` |
| `set` | `0` |
| `reveal` | target-specific |
| `hide` | target-specific |
| `camera` | `1000` |
| `epochTravel` | `5000` |
| `flash` | `900` |

Transition defaults:

| Target | Default mode | Default order | Default duration |
| --- | --- | --- | ---: |
| `eclipticGrid` | `stagger` | `default` | `1000` |
| `equatorialGrid` | `stagger` | `default` | `1000` |
| `eclipticNakSegments` | composite | `ecliptic` | target parts |
| `referencePlanes` | `fade` | `default` | `700` |
| `eclipticPlane` | `fade` | `default` | `700` |
| `equatorialPlane` | `fade` | `default` | `700` |
| `nsAxis` | `fade` | `default` | `700` |
| `ecliptic` | composite | `ecliptic` | target parts |
| `eclipticBand` | `fade` | `ecliptic` | `900` |
| `eclipticDividers` | `rollout` | `ecliptic` | `1200` |
| `eclipticLabels` | `stagger` | `ecliptic` | `1200` |
| `eclipticPoles` | `fade` | `default` | `600` |
| `stars` | `fade` | `default` | `900` |
| `nakshatras` | `rollout` | `ecliptic` | `1800` |
| `nakshatraLines` | `rollout` | `ecliptic` | `1800` |
| `nakshatraLabels` | `stagger` | `ecliptic` | `1200` |
| `polarItems` | `rollout` | `default` | `1600` |
| `northPolarItems` | `rollout` | `default` | `1200` |
| `southPolarItems` | `rollout` | `default` | `1200` |
| `poleTrack` | `rollout` | `default` | `1100` |
| `precessionCircle` | `fade` | `default` | `900` |
| `seasonalFrame` | `rollout` | `default` | `1300` |
| `overlay` | `fade` | `default` | `500` |

Implementation note: `rollout` currently stages objects or groups in order; it is not yet true geometric line drawing along each polyline. For `stars`, rollout reveals one nakshatra star group at a time, followed by special stars such as Agastya. For `nakshatras`, rollout reveals one complete stick figure at a time.

## Reveal and Hide

Prefer `reveal`/`hide` when a story should stage visual layers. They update the underlying `ui.show...` state when the transition finishes.

Minimal form:

```json
{
  "at": "+300",
  "action": "reveal",
  "target": "nakshatras"
}
```

Optional overrides:

```json
{
  "at": "+300",
  "action": "hide",
  "target": "nakshatras",
  "mode": "rollout",
  "direction": "reverse",
  "duration": 1200
}
```

Supported targets:

- `eclipticGrid`
- `equatorialGrid`
- `eclipticNakSegments`
- `referencePlanes`
- `eclipticPlane`
- `equatorialPlane`
- `nsAxis`
- `eclipticBand`
- `eclipticDividers`
- `eclipticLabels`
- `eclipticPoles`
- `stars`
- `nakshatras`
- `nakshatraLines`
- `nakshatraLabels`
- `polarItems`
- `northPolarItems`
- `southPolarItems`
- `poleTrack`
- `precessionCircle`
- `seasonalFrame`
- `overlay`
- `NEP`, `SEP`, `NP`, `SP`
- `equator`, `VE`, `SS`, `AE`, `WS`
- `agastya`, `thuban`, `polaris`, `matsya`, `sisumara`
- sigil nakshatra targets such as `$ash`, `*ash`, and `@ash` for flash/focus-style cues

Supported modes are `instant`, `fade`, `stagger`, and `rollout`. Most stories should omit `mode`, `order`, `direction`, and `duration`; defaults are target-specific.

## Useful State Patches

`set` cues accept partial patches under `state`.

```json
{
  "at": "+300",
  "action": "set",
  "state": {
    "ui": {
      "showGrid": true,
      "showEquatorialGrid": false,
      "showReferencePlanes": false,
      "showNsAxis": false,
      "showEclipticBand": true,
      "showEclipticDividers": true,
      "showEclipticLabels": true,
      "showEclipticPoles": true,
      "showStars": true,
      "showNakshatraLines": true,
      "showNakshatraLabels": true,
      "showPolarItems": true,
      "showNorthPolarItems": true,
      "showSouthPolarItems": true,
      "showPoleTrack": true,
      "showSeasonalFrame": true,
      "showOverlay": true
    }
  }
}
```

Patch only what changes. Avoid dumping the full settings object unless the story intentionally resets the scene.

`StatePatch` may include:

```text
StatePatch =
  {
    "lightPreset"?: "night" | "twilight" | "day",
    "epochYear"?: number,
    "camera"?: CameraPatch,
    "ui"?: UiPatch,
    "grid"?: object,
    "reference"?: object,
    "ecliptic"?: object,
    "stars"?: object,
    "nakshatras"?: object,
    "polarItems"?: object,
    "poleTrack"?: object,
    "seasonal"?: object,
    "overlay"?: object
  }

CameraPatch =
  {
    "position"?: { "x"?: number, "y"?: number, "z"?: number },
    "target"?: { "x"?: number, "y"?: number, "z"?: number },
    "fov"?: number,
    "minDistance"?: number,
    "maxDistance"?: number
  }

UiPatch =
  {
    "showGrid"?: boolean,
    "showEquatorialGrid"?: boolean,
    "showReferencePlanes"?: boolean,
    "showEclipticPlane"?: boolean,
    "showEquatorialPlane"?: boolean,
    "showNsAxis"?: boolean,
    "showEclipticBand"?: boolean,
    "showEclipticDividers"?: boolean,
    "showEclipticLabels"?: boolean,
    "showEclipticPoles"?: boolean,
    "showStars"?: boolean,
    "showNakshatraLines"?: boolean,
    "showNakshatraLabels"?: boolean,
    "showPolarItems"?: boolean,
    "showNorthPolarItems"?: boolean,
    "showSouthPolarItems"?: boolean,
    "showNEP"?: boolean,
    "showSEP"?: boolean,
    "showNP"?: boolean,
    "showSP"?: boolean,
    "showPoleTrack"?: boolean,
    "showSeasonalFrame"?: boolean,
    "showOverlay"?: boolean
  }
```

Use `set` for instant state changes. Prefer explicit actions when behavior matters:

- instant year jump: `set.state.epochYear`
- animated year travel: `epochTravel`
- instant camera jump: `set.state.camera`

Grid density is a debug/settings property, not a separate story action:

```json
{
  "grid": {
    "eclipticStepDeg": 30,
    "equatorialStepDeg": 30
  }
}
```

Lower step values make denser grids. Keep values in the practical `5` to `90` degree range.

VyomaSutra also supports compact grid tuning:

```text
grid ecliptic 15 blue
grid equatorial 15 red
```

These compile to `set` patches for grid density/color and turn on the chosen grid.

VyomaSutra safe style examples:

```text
style equatorialGrid color red alpha %28
style nsAxis color #a7b4c7 alpha .35
style naks color #8eaccb alpha .8 fontSize 5
style stars alpha %80 starSize 2.6
```
- animated camera move: `camera`
- instant visibility change: `set.state.ui.show...`
- staged visibility change: `reveal` or `hide`

## Camera Cues

Camera cues may be partial. Missing coordinates keep their current values.

```json
{
  "at": "+500",
  "action": "camera",
  "duration": 1200,
  "camera": {
    "position": { "x": -147.464, "y": 73.504, "z": 234.757 },
    "target": { "x": 0, "y": 0, "z": 0 }
  }
}
```

This is also valid when only one coordinate changes:

```json
{
  "at": "+500",
  "action": "camera",
  "duration": 800,
  "camera": {
    "position": { "x": 10 }
  }
}
```

For tolerance while tuning, `camera` cues also accept `state.camera`, but prefer the direct `camera` shape above.

## Captions

```json
{
  "at": 300,
  "action": "caption",
  "text": "Visualize Precession",
  "duration": 1200,
  "fadeIn": 250,
  "fadeOut": 350
}
```

Keep captions short. They should support the visual, not narrate everything.

`fadeIn` and `fadeOut` set the actual opacity-transition duration in milliseconds. `duration` is the total caption lifetime from cue start; fade-out begins at `duration - fadeOut`.

VyomaSutra captions accept color names/hex colors and `size NUMBER`, for example `caption "Thuban era" gold size 4 1500:300:300`.

## Epoch Travel

```json
{
  "at": "+500",
  "action": "epochTravel",
  "from": -1800,
  "to": -800,
  "step": 100,
  "duration": 5000
}
```

Use epoch values available in the explorer range. `step` should usually match the page epoch step.

## Authoring Rules

- Start with a small `initial` state if the scene needs a clean stage.
- Use relative `at` values after the first cue to make timing edits cheap.
- Prefer a sequence of simple cues over one large patch.
- Use `set` for instant state changes; use `reveal`/`hide` for staged visibility changes.
- `set.duration` is accepted but currently discrete; do not rely on it for smooth layer visibility.
- Test in the 3D Stories dock, then copy tuned JSON back into the story file.
