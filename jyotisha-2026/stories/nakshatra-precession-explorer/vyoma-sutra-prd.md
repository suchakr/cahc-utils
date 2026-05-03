# VyomaSutra PRD

Status: proposed
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
show eclipticGrid
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
- browser interpreter compiles it just in time to story JSON
- compiled JSON is shown for inspection
- user runs compiled JSON in the existing story runner
- no precompile step and no save semantics beyond existing manual file edits

Phase 2:

- syntax highlighting
- line numbers
- inline warnings
- alias suggestions
- copy compiled JSON button

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

## Conceptual Model

VyomaSutra has five kinds of line:

- `stage`: initialize or reset durable state
- `show/hide/reveal`: visibility and animated visibility
- `style`: tune visual appearance
- `camera/travel/caption`: narrative actions
- `wait/comment`: pacing and annotation

Each line compiles to one or more JSON cues.

## Quick Examples

```text
# Start clean
stage blank night year -1800

caption "Visualize Precession" 1200:
show grid
show eclipticGrid
rollout stars
rollout naks

caption "1800 BCE"
travel -1800 to -800 5000: step 100
```

```text
# Tune visual style
style naks color #8eaccb alpha .8 font+ 2
style eclipticGrid alpha .25
style northPolarItems lineColor #6f86a1 lineThin label-
flash VE
```

```text
# Target individual primitives
hide NEP
show SEP
flash NP
style sector.3 color #d4a56a alpha .35
rollout nak.ashvayuk
show star.agastya
show @ash
```

## Target Hierarchy

Group targets:

```text
skyScaffold
siderealLayer
tropicalLayer
stars
nakshatras
naks
polarItems
northPolarItems
southPolarItems
eclipticGrid
equatorialGrid
seasonalFrame
poleTrack
precessionCircle
referencePlanes
eclipticPlane
equatorialPlane
axes
nsAxis
```

Primitive targets:

```text
stars.nakshatraStars
stars.specialStars
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
NEP
SEP

equator.line
equator.grid
equatorialPlane
eclipticPlane

NP
SP
nsAxis

poleTrack.circle
poleTrack.arc
poleTrack.dot
poleTrack.labels

seasonal.markers
seasonal.labels
VE
SS
AE
WS

polarItems.north.lines
polarItems.north.labels
polarItems.north.stars
polarItems.south.lines
polarItems.south.labels
polarItems.south.stars
```

Required individual addressability:

- `NEP`
- `SEP`
- `NP`
- `SP`
- each nakshatra sector
- each nakshatra star group
- each nakshatra line/label group
- each special star, including `Agastya`

## Alias Policy

Aliases should reduce authoring load.

Examples:

| Canonical | Aliases |
| --- | --- |
| `nakshatras` | `naks`, `nak`, `nakshatra` |
| `eclipticGrid` | `eclGrid`, `ecliptic`, `ecl` |
| `equatorialGrid` | `eqGrid`, `equatorGrid`, `eq` |
| `northPolarItems` | `northPolar`, `nPolar`, `npItems` |
| `southPolarItems` | `southPolar`, `sPolar`, `spItems` |
| `seasonalFrame` | `seasons`, `rtu`, `rtus` |
| `poleTrack` | `precessionCircle`, `polePath` |
| `stars.specialStars` | `specialStars` |
| `stars.nakshatraStars` | `nakStars`, `naksStars` |
| `Agastya` | `agastya`, `canopus` |

Nakshatra aliases should support:

- full transliteration: `ashvayuk`, `bharani`, `krittika`
- sigil plus 3+ character prefix: `$ash`, `*bha`, `@kri`
- current internal ids if needed: `N01-Ash`, `N03-Kri`

Special nakshatra aliases:

| Alias | Nakshatra |
| --- | --- |
| `pph` | Pūrvaphālgunī |
| `uph` | Uttaraphālgunī |
| `pas` | Pūrvāṣāḍhā |
| `uas` | Uttarāṣāḍhā |
| `ppr`, `pbh` | Pūrvaproṣṭhapadā / Pūrvabhādrapadā |
| `upr`, `ubh` | Uttaraproṣṭhapadā / Uttarabhādrapadā |
| `abh`, `n28` | Abhijit |

Sigils:

| Sigil | Meaning |
| --- | --- |
| `$ash` | nakshatra sector only |
| `*ash` | nakshatra star group plus stick figure |
| `@ash` | sector plus star group plus stick figure |

## Style Knobs

Common style knobs:

```text
visible
alpha
color
lineColor
lineWidth
lineThick
lineThin
lineStyle
fontSize
font+
font-
labelAlpha
starSize
pointSize
glow
flash
duration
mode
order
direction
```

Allowed line styles:

```text
solid | dashed | dotted
```

Allowed transition modes:

```text
instant | fade | stagger | rollout
```

## Formal-ish Grammar

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
                 | captionStmt
                 | waitStmt
                 | fullscreenStmt
                 | flashStmt

stageStmt      ::= "stage" stageArg*
stageArg       ::= "blank" | "all" | lightArg | yearArg | cameraPreset
lightArg       ::= "night" | "twilight" | "day"
yearArg        ::= ("year" | "epoch") number

visibilityStmt ::= visibilityVerb targetSpec transitionArg*
visibilityVerb ::= "show" | "hide" | "reveal" | "rollout" | "fade"
transitionArg  ::= modeArg | durationArg | orderArg | directionArg
modeArg        ::= "instant" | "fade" | "stagger" | "rollout"
durationArg    ::= durationSpec | "over" durationSpec
durationSpec   ::= number ":" number? ":" number?
                 | number ":" number?
                 | number ":"
orderArg       ::= "ecliptic" | "reverse-ecliptic" | "north-to-south" | "south-to-north"
directionArg   ::= "forward" | "reverse"

styleStmt      ::= "style" targetSpec styleArg+
styleArg       ::= key value | sugarStyle
sugarStyle     ::= "font+" number? | "font-" number? | "lineThick" number? | "lineThin" number? | "flash"

cameraStmt     ::= "camera" (cameraPreset | cameraJson | cameraArgs) durationArg?
cameraPreset   ::= identifier
cameraArgs     ::= ("pos" vec3)? ("target" vec3)? ("fov" number)?

travelStmt     ::= ("travel" | "epochTravel") number "to" number durationArg? ("step" number)?
captionStmt    ::= ("caption" | "say" | "title") captionArg*
captionArg     ::= quotedText | durationArg | colorSpec | sizeSpec | alphaSpec | locationSpec | fadeArg
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
```

## Compile Semantics

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
```

compiles to a partial `set.state` patch against the canonical settings block.

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

compiles to a camera cue using a named preset.

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
- explicit `at 3000` and `after 500` may be added later

Example:

```text
caption "A" 1000
wait 500
caption "B" 1000
```

## Error Handling

- Unknown command: warn and skip line.
- Unknown target: warn, keep line uncompiled.
- Ambiguous alias: warn with candidates.
- Invalid number: warn and use default when safe.
- Missing quoted text for caption: error and skip line.
- Unknown style key: warn and skip style key.
- Empty line/comment: ignore.

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
- Common aliases like `naks`, `eclGrid`, `rtus`, `Agastya`, `NEP`, `NP` compile correctly.
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
