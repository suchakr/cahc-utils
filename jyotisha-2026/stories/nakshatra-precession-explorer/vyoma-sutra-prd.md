# VyomaSutra PRD

Status: implemented baseline; evolving grammar
Parent exploration: `nakshatra-precession-explorer`
Compiled target: story JSON described in `SKILL.md`

## Name

`VyomaSutra` is the working name.

- `Vyoma` signals sky/space.
- `Sutra` signals compact declarative utterance.
- The name does not by itself signal programmability, so the product copy should always say: "VyomaSutra is a forgiving mini-language for authoring 3D sky stories."

Alternatives considered:

- `SkySutra`: clearer to English readers, less culturally precise.
- `JyotiScript`: strongly programmable, but too generic and less poetic.
- `VyomaScript`: clear but less elegant.
- `DrishyaSutra`: emphasizes visual narration, but less explicitly sky-focused.

Decision: use `VyomaSutra` unless user testing shows the name hides the scripting purpose.

## Purpose

Make story authoring less syntax-heavy than JSON while preserving JSON as the stable runtime format.

Humans should be able to write compact, forgiving lines such as:

```text
caption "Visualize Precession"
show eclipticNakSegments
rollout stars
rollout naks
camera topDome 1200:
travel -1800 to -800 5000: step 100
```

The interpreter compiles these lines into the existing story JSON. The generated JSON remains inspectable, editable, and runnable in the current Stories dock.

## Reference Pattern

This follows the rbdraw mini-language approach as inspiration, not as a spec:

- examples first
- permissive aliases
- formal-ish grammar
- best-effort parsing
- useful warnings instead of brittle failure where possible
- syntax highlighting as a later editor improvement

## User Problem

Current story JSON is powerful but cognitively expensive:

- repeated braces and quoting slow down exploratory tuning
- cue timing syntax is easy to mistype
- camera and style patches are verbose
- target names require exact recall
- small mistakes can silently make a cue ineffective unless validation catches them

VyomaSutra should let the user express intent quickly, then compile into strict JSON.

## Non-Goals

- Do not replace JSON runtime.
- Do not add arbitrary JavaScript.
- Do not make a fully general programming language.
- Do not solve movie export in this phase.
- Do not require a build system.

## Lifecycle

Phase 1:

- user writes or pastes VyomaSutra text in a scratch/editor surface
- build-time story sources may live as `stories/nakshatra-precession-explorer/<id>.vysu`
- `uv run python scripts/compile_stories.py nakshatra-precession-explorer` compiles `.vysu` to `stories/nakshatra-precession-explorer/compiled/*.json` without astropy
- the fast compiler also patches `lab/nakshatra-precession-explorer/index.html` story data and writes `lab/nakshatra-precession-explorer/stories.json`
- story inventory is file-backed: current `.vysu`/root `.json` sources replace the generated story list, so stale compiled or embedded stories do not remain visible
- browser interpreter compiles it just in time to story JSON
- compiled JSON is shown for inspection
- user runs compiled JSON in the existing story runner
- no browser-side save semantics beyond existing manual file edits
- generated CSS is emitted under `lab/nakshatra-precession-explorer/assets/css/`; an inspectable copy of the 3D/VyomaSutra module is emitted under `assets/js/`, while the executable module remains inline for `file://` compatibility

Phase 2:

- syntax highlighting
- line numbers
- inline warnings
- alias suggestions
- copy compiled JSON button
- fuller grammar extraction so browser and Python compilers share one spec/test corpus

Phase 3:

- browser-side story drafts
- export `.json`
- optional named camera presets

## Design Principles

- JSON is the canonical executable format.
- VyomaSutra is forgiving authoring sugar.
- Every meaningful primitive target should be addressable.
- Common story-level groups should be short and memorable.
- Aliases are expected, not exceptional.
- Unknown lines should produce actionable warnings.
- The compiler should prefer doing the unsurprising thing.

## Language Contract

VyomaSutra should be specified as one language contract with four auditable layers:

1. Core grammar: which sentence shapes can be parsed.
2. Semantic tables: which commands, targets, aliases, and properties exist.
3. Lowering rules: how parsed statements become strict story JSON.
4. Warning rules: how invalid, unsupported, ambiguous, or ignored input is reported.

The core authoring pattern is:

```text
<when?> <command> <target?> <properties-or-sugar...>
```

Examples:

```text
stage blank night year -1800
after 500 show stars fade over 900
style nsAxis color yellow opacity .8
camera pos -147.464,73.504,234.757 target 0,0,0 fov 45 over 900
travel year -1800 to -800 over 5000 step 100
flash @ash over 650
```

`stage` is a state command, not just file metadata. If `stage` appears before any emitted cue, it sets `story.initial`. If it appears after emitted cues, it should compile to a runtime `set` cue at that point. Current implementation only has the initial-state behavior; mid-story `stage` must not remain silently misleading.

Build-time files may include discovery metadata comments:

```text
# title: Visualize Precession
# version: 1
# featured: true
# group: Precession
# tags: intro, seasonal-frame
# order: 10
```

`featured` makes the story eligible for the top 3D story pill row. The UI shows up to five featured matches and uses the same search text for the top pills and the Stories dock select. If the project grows to dozens or hundreds of stories, this keeps the visible chrome small while preserving quick lookup by title, id, group, or tags.

## Core Grammar

```ebnf
program        ::= line*
line           ::= ws* statementList? comment? newline
statementList  ::= statement (";" statement)*
comment        ::= "#" text
                 ; but #RGB and #RRGGBB are color tokens, not comments

statement      ::= stageStmt
                 | visibilityStmt
                 | styleStmt
                 | cameraStmt
                 | travelStmt
                 | gridStmt
                 | captionStmt
                 | waitStmt
                 | fullscreenStmt
                 | flashStmt
                 | timedStmt

timedStmt      ::= when statement
when           ::= "at" number | "after" number | signedRelative

stageStmt      ::= "stage" stageArg*
stageArg       ::= "blank" | "all" | lightArg | yearArg | cameraPreset
lightArg       ::= "night" | "twilight" | "day"
yearArg        ::= ("year" | "epoch") number

visibilityStmt ::= visibilityVerb targetSpec transitionArg*
visibilityVerb ::= "show" | "hide" | "reveal" | "rollout" | "fade"
transitionArg  ::= modeArg | durationArg | orderArg | directionArg
modeArg        ::= "instant" | "fade" | "stagger" | "rollout"
durationArg    ::= durationSpec | "over" durationSpec | bareMs
durationSpec   ::= number ":" number? ":" number?
                 | number ":" number?
                 | number ":"
bareMs         ::= number
orderArg       ::= "ecliptic" | "reverse-ecliptic" | "north-to-south" | "south-to-north"
directionArg   ::= "forward" | "reverse"

styleStmt      ::= "style" targetSpec styleArg+
styleArg       ::= key value | sugarStyle
sugarStyle     ::= "font+" number? | "font-" number? | "lineThick" number? | "lineThin" number? | "flash"

cameraStmt     ::= "camera" (cameraPreset | cameraJson | cameraArgs) durationArg?
cameraPreset   ::= identifier
cameraArgs     ::= ("pos" vec3)? ("target" vec3)? ("fov" number)?

travelStmt     ::= ("travel" | "epochTravel") ("year" | "epoch")? number "to" number durationArg? ("step" number)?
gridStmt       ::= "grid" ("ecliptic" | "ecl" | "equatorial" | "equator" | "eq") number colorSpec?
captionStmt    ::= ("caption" | "say" | "title") captionArg*
captionArg     ::= quotedText | durationArg | colorSpec | "size" number | alphaSpec | locationSpec | fadeArg
fadeArg        ::= "fadeIn" number | "fadeOut" number
waitStmt       ::= "wait" number ("ms")?
flashStmt      ::= "flash" targetSpec durationArg?
fullscreenStmt ::= "fullscreen" | "theater" | "exitFullscreen" | "canvas"

targetSpec     ::= sigilNak | namedTarget | dottedTarget
sigilNak       ::= ("$" | "*" | "@") naksString
namedTarget    ::= identifier
dottedTarget   ::= identifier ("." identifier)+
colorSpec      ::= colorName | hexColor | rgbColor
hexColor       ::= "#" hex{3,6}
alphaSpec      ::= "%" number | number "%"
sizeSpec       ::= sizeWord | number "px" | "font+" number? | "font-" number?
locationSpec   ::= anchor | "@" number ":" number | vec3 | "@" targetSpec
vec3           ::= number "," number "," number
quotedText     ::= '"' text '"'
signedRelative ::= ("+" | "-") number
```

The grammar intentionally accepts broad shapes. Semantic tables decide which target-specific and command-specific properties are meaningful. The tables below are the intended language contract; current Python and browser compilers have known parity gaps and should converge to this contract.

## Semantic Tables

### Commands

| Command | Shape | Lowers to | Notes |
| --- | --- | --- | --- |
| `stage` | `stage <stage-props...>` | `initial` or `set` | Initial before first cue; runtime reset/set after emitted cues. |
| `show`, `reveal` | `show <target> <transition-props...>` | `reveal` | Uses target defaults unless mode/order/duration are supplied. |
| `hide` | `hide <target> <transition-props...>` | `hide` | Uses target defaults. |
| `rollout` | `rollout <target> <transition-props...>` | `reveal` | Sugar for `show <target> rollout`. |
| `fade` | `fade <target> <transition-props...>` | `reveal` | Sugar for `show <target> fade`. |
| `flash` | `flash <target> <transition-props...>` | `flash` | Temporary emphasis; must not change durable visibility. |
| `style` | `style <target> <style-props...>` | `set` | Valid props are target-dependent. |
| `camera` | `camera <camera-props...>` | `camera` | Supports `pos`, `target`, `fov`, `over`; presets are planned. |
| `caption`, `say`, `title` | `caption "text" <caption-props...>` | `caption` | Quoted text is required. |
| `travel`, `epochTravel` | `travel year <from> to <to> <travel-props...>` | `epochTravel` | `year` is optional sugar. |
| `grid` | `grid <kind> <step> <color?>` | `set` | Also reveals the chosen grid. |
| `wait` | `wait <ms>` | pending timing | Adds delay before next emitted cue. |
| `fullscreen`, `theater` | bare command | `fullscreen` | Theater/canvas affordance. |
| `exitFullscreen`, `canvas` | bare command | `exitFullscreen` | Leaves theater/canvas mode. |

### Command Properties

| Property | Type | Commands | Canonical meaning |
| --- | --- | --- | --- |
| `at` | ms | all emitting commands | Absolute cue time. |
| `after` | ms | all emitting commands | Relative delay before this cue. |
| `over` | ms | `show`, `hide`, `flash`, `camera`, `caption`, `travel` | Duration. |
| `mode` / bare mode | enum | `show`, `hide`, `flash` | `instant`, `fade`, `stagger`, `rollout`. |
| `order` / bare order | enum | `show`, `hide`, `flash` | `default`, `ecliptic`, `reverse-ecliptic`, `north-to-south`, `south-to-north`. |
| `direction` / bare direction | enum | `show`, `hide`, `flash` | `forward`, `reverse`. |
| `fadeIn` | ms | `caption` | Caption fade-in time. |
| `fadeOut` | ms | `caption` | Caption fade-out time. |
| `pos` | vec3 | `camera` | Camera position. |
| `target` | vec3 | `camera` | Camera look target. |
| `fov` | number | `camera` | Camera field of view. |
| `step` | number | `travel`, `grid` | Year sampling for travel; degree spacing for grid. |
| `blank` | flag | `stage` | Reset visible layers to off. |
| `night`, `twilight`, `day` | enum | `stage` | Light preset. |
| `year`, `epoch` | number | `stage`, `travel` | Epoch year. |

### Target Registry

Runtime group targets:

| Canonical target | Aliases | Commands | Style props |
| --- | --- | --- | --- |
| `eclipticGrid` | `eclGrid`, `eclGridWire` | `show`, `hide`, `flash`, `style`, `grid` | `color`, `lineColor`, `opacity`, `alpha` |
| `equatorialGrid` | `eqGrid`, `equatorGrid`, `eq` | `show`, `hide`, `flash`, `style`, `grid` | `color`, `lineColor`, `opacity`, `alpha` |
| `referencePlanes` | `refs` | `show`, `hide`, `flash` | pending |
| `eclipticPlane` | none | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha` |
| `equatorialPlane` | none | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha` |
| `nsAxis` | `axis`, `nsaxis` | `show`, `hide`, `flash`, `style` | `color`, `lineColor`, `opacity`, `alpha` |
| `eclipticNakSegments` | `nakSegments`, `naksSegments`, `eclipticSegments` | `show`, `hide`, `flash`, `style` | `color`, `lineColor`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `eclipticBand` | none | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha` |
| `eclipticDividers` | `sectorDividers` | `show`, `hide`, `flash` | pending |
| `eclipticLabels` | `sectorLabels` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `eclipticPoles` | none | `show`, `hide`, `flash` | pending |
| `stars` | none | `show`, `hide`, `flash`, `style` | `opacity`, `alpha`, `starSize`, `pointSize` |
| `nakshatras` | `naks`, `nak`, `nakshatra` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `nakshatraLines` | pending aliases | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha` |
| `nakshatraLabels` | pending aliases | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `polarItems` | none | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `northPolarItems` | `northPolar` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `southPolarItems` | `southPolar` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `poleTrack` | `polePath` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `fontSize`, `font+`, `font-` |
| `precessionCircle` | `precession` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `fontSize`, `font+`, `font-` |
| `seasonalFrame` | `seasons`, `rtu`, `rtus` | `show`, `hide`, `flash`, `style` | `color`, `opacity`, `alpha`, `labelAlpha`, `fontSize`, `font+`, `font-` |
| `overlay` | none | `show`, `hide`, `style` | `opacity`, `alpha`, `fontSize`, `font+`, `font-` |

Runtime primitive targets:

| Canonical target | Aliases | Meaning |
| --- | --- | --- |
| `NEP`, `SEP` | lowercase accepted | Ecliptic pole marker/label. |
| `NP`, `SP` | lowercase accepted | Moving celestial pole marker/label. |
| `equator` | none | Seasonal/celestial equator line. |
| `VE`, `SS`, `AE`, `WS` | lowercase accepted | Equinox/solstice seasonal markers. |
| `agastya` | `canopus` | Special star item. |
| `thuban` | `abhayaDhruva` | North polar special star/item. |
| `polaris` | `matsyaDhruva` | North polar special star/item. |
| `matsya` | none | Polar figure/item. |
| `sisumara` | `shishumara`, `shimshumara` | Polar figure/item. |

Planned but not yet implemented primitive addressability:

```text
star.<id-or-alias>
nak.<id-or-alias>
nak.<id-or-alias>.stars
nak.<id-or-alias>.lines
nak.<id-or-alias>.label
sector.<number>
sector.<number>.band
sector.<number>.divider
sector.<number>.label
ecliptic.band
ecliptic.circle
ecliptic.dividers
ecliptic.labels
ecliptic.poles
poleTrack.circle
poleTrack.arc
poleTrack.dot
poleTrack.labels
polarItems.north.lines
polarItems.north.labels
polarItems.north.stars
polarItems.south.lines
polarItems.south.labels
polarItems.south.stars
```

### Nakshatra Sigils

Nakshatra aliases should support full transliteration, 3+ character prefixes, and current internal ids where useful. Special aliases:

| Alias | Nakshatra |
| --- | --- |
| `pph` | Purvaphalguni |
| `uph` | Uttaraphalguni |
| `pas` | Purvashadha |
| `uas` | Uttarashadha |
| `ppr`, `pbh` | Purvaproshthapada / Purvabhadrapada |
| `upr`, `ubh` | Uttaraproshthapada / Uttarabhadrapada |
| `abh`, `n28` | Abhijit |

| Sigil | Meaning |
| --- | --- |
| `$ash` | Nakshatra sector only. |
| `*ash` | Nakshatra star group plus stick figure. |
| `@ash` | Sector plus star group plus stick figure. |

### Value Types

| Type | Examples | Notes |
| --- | --- | --- |
| `ms` | `650`, `650:` | Milliseconds. Bare numbers are accepted where duration is expected. |
| duration tuple | `1200:250:350` | `duration:fadeIn:fadeOut` for captions; duration only elsewhere. |
| alpha | `.5`, `%50`, `50%` | Clamped to 0..1. |
| color | `yellow`, `#8eaccb` | Named colors and hex colors. |
| vec3 | `0,325,0.1` | No spaces inside the vector token. |
| number | `45`, `-1800`, `2.6` | Parsed as integer only where the target JSON expects integer years. |

## Sugar

Sugar must always have a documented canonical equivalent.

| Sugar | Canonical equivalent | Where legal |
| --- | --- | --- |
| `650:` | `over 650` | duration-bearing commands |
| `1200:250:350` | `over 1200 fadeIn 250 fadeOut 350` | `caption` |
| `yellow` | `color yellow` | `style` when a color is expected |
| `%50` | `opacity .5` | `style`, `caption` |
| `font+ 2` | increase current/default `fontSize` by 2 | label-bearing style targets |
| `font- 1` | decrease current/default `fontSize` by 1 | label-bearing style targets |
| `rollout stars` | `show stars rollout` | visibility commands |
| `fade stars` | `show stars fade` | visibility commands |

Unsupported sugar should warn. It should not silently disappear.

## Lowering Rules

Visibility:

```text
show target        -> JSON action "reveal" using target defaults
hide target        -> JSON action "hide" using target defaults
reveal target      -> JSON action "reveal" using target defaults
rollout target     -> JSON action "reveal", mode "rollout"
fade target        -> JSON action "reveal", mode "fade"
```

Style:

```text
style naks color #8eaccb alpha .8
style equatorialGrid color red alpha %28
style stars alpha %80 starSize 2.6
```

compiles to a partial `set.state` patch against the canonical settings block.

Phase 1 implemented style knobs are intentionally safe: `color`, `lineColor`, `alpha`, `opacity`, `labelAlpha`, `fontSize`, `font+`, `font-`, `starSize`, and `pointSize`. True line width remains pending because WebGL line width is unreliable without fat-line geometry.

Grid density:

```text
grid ecliptic 15 blue
grid equatorial 15 red
```

compiles to grid density/color `set` patches and turns on the chosen grid. Lower step values make denser grids.

Stage:

```text
stage blank night year -1800
```

before the first emitted cue contributes to `story.initial`. The same statement after emitted cues compiles to a `set` cue that applies the blank UI patch, light preset, and epoch at that point in the story.

Caption:

```text
caption "Visualize Precession" 1200:250:350
```

compiles to:

```json
{
  "action": "caption",
  "text": "Visualize Precession",
  "duration": 1200,
  "fadeIn": 250,
  "fadeOut": 350
}
```

Travel:

```text
travel -1800 to -800 over 5000 step 100
```

compiles to `epochTravel`.

Camera:

```text
camera topDome over 1200
```

should compile to a camera cue using a named preset.

Current implementation does not yet implement camera presets. Until presets exist, accepted camera syntax should use explicit `pos`, `target`, and/or `fov`, and unsupported preset names must warn.

Flash:

```text
flash precessionCircle 1500:
flash @ash 650:
```

compiles to a `flash` cue. Flash is temporary emphasis; it should not change durable visibility.

Fullscreen:

```text
fullscreen
exitFullscreen
```

compiles to `fullscreen` / `exitFullscreen` story cues for theater viewing of the 3D canvas.

## Timing Sugar

Phase 1 may use one cue per line with implicit relative timing.

Rules:

- first line defaults to `at: 0`
- each following line defaults to `at: "+0"`
- `wait 500` inserts delay before the next emitted cue
- `;` separates statements on the same line
- explicit `at 3000` and `after 500` are planned canonical timing modifiers
- bare `over 500` or `500:` means duration, not cue position

Example:

```text
caption "A" 1000
wait 500
caption "B" 1000
```

## Warning Rules

- Unknown command: warn and skip line.
- Unknown target: warn, keep line uncompiled.
- Ambiguous alias: warn with candidates.
- Invalid number: warn and use default when safe.
- Missing quoted text for caption: error and skip line.
- Unknown style key: warn and skip style key.
- Empty line/comment: ignore.
- Unsupported property for a known target: warn with supported properties.
- Unsupported sugar for a command or target: warn and skip that sugar.
- Valid syntax with no semantic meaning: warn and skip the statement or property.
- Mid-story `stage` in an implementation that cannot lower it to a cue: warn.
- Compiler warnings must be visible in both browser and build-time flows.

Silent ignore is only acceptable for whitespace, comments, metadata comments, and redundant separators.

## Examples

Valid and meaningful:

```text
# Start clean
stage blank night year -1800

caption "Visualize Precession" 1200:
show eclipticGrid
show eclipticNakSegments
rollout stars
rollout naks

caption "1800 BCE"
travel year -1800 to -800 over 5000 step 100
```

Valid and meaningful style:

```text
style naks color #8eaccb alpha .8 font+ 2
style eclipticNakSegments alpha .25
style nsAxis color yellow
flash VE
```

Valid and meaningful primitive/sigil targets:

```text
hide NEP
show SEP
flash NP
flash $ash 650:
flash *ash 650:
flash @ash 650:
```

Valid syntax but currently unsupported semantics, with warnings:

```text
style sector.3 color #d4a56a alpha .35
rollout nak.ashvayuk
show star.agastya
camera topDome over 1200
```

Invalid or unsupported input, with warnings:

```text
style nsAxis pointSize 4
caption Missing quotes
show notARealTarget
unknownVerb stars
```

## Editor UX Later

Use rbdraw as the model:

- syntax highlighting
- line numbers
- comments
- invalid tokens left unstyled
- copy compiled JSON
- run compiled story
- no build step if possible

## Acceptance Criteria

- A human can author a basic precession story in fewer than 15 lines.
- Common aliases like `naks`, `eclipticGrid`, `eclipticNakSegments`, `rtus`, `Agastya`, `NEP`, `NP` compile correctly.
- Every primitive in the target hierarchy is addressable by canonical name.
- The compiler emits strict story JSON accepted by the existing runner.
- Compilation warnings are readable and line-specific.
- The original JSON authoring flow remains available.

## Open Questions

- Should `show` be instant and `reveal` animated, or should `show` pick target defaults?
- Should camera presets live in JSON, code, or a separate `camera-presets.json`?
- How should individual nakshatra aliases be generated and disambiguated?
- Should syntax highlighting be built before browser-side save semantics?
- Should `style` persist as story state or only apply during the current story run?
