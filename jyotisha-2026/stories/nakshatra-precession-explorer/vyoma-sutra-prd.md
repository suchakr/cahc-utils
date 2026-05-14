# VyomaSutra PRD

Status: Stage 1 regularization implemented; Stage 2 forms are warning-only
Parent exploration: `nakshatra-precession-explorer`
Runtime target: transient story JSON consumed by the existing story runner

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

Make story authoring less syntax-heavy than JSON while preserving JSON as the internal runtime format.

Humans should be able to write compact, forgiving lines such as:

```text
caption "Visualize Precession"
show eclipticNakSegments
rollout stars
rollout naks
camera topDome 1200:
travel -1800 to -800 5000: step 100
```

The interpreter compiles these lines into transient story JSON for the existing story runner. That JSON may remain inspectable and editable in the browser for debugging, but it is not the authoring source of truth and does not need browser-side save semantics.

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
- Do not require a Python compiler.
- Do not add loop/control-flow constructs such as `foreach`.
- Do not add bespoke story macros such as `tour naks`.

## Lifecycle

Stage 1:

- user writes or pastes VyomaSutra text in a scratch/editor surface
- build-time story sources may live as `stories/nakshatra-precession-explorer/<id>.vysu`
- a TypeScript compiler is the source of truth; plain JavaScript is acceptable only if TypeScript setup causes disproportionate churn
- story validation and build checks are Node-based, using a CLI such as `node scripts/compile-vysu.mjs nakshatra-precession-explorer`
- the browser can interpret VyomaSutra directly by compiling to transient story JSON just in time for the runner
- generated JSON files are optional debug/test artifacts, not required authoring or save artifacts
- the build should ship current `.vysu` source text and metadata into the lab story inventory so stale embedded stories do not remain visible
- transient compiled JSON may be shown for inspection and manual debugging
- user runs VyomaSutra through the existing story runner
- no browser-side save semantics are required in Stage 1
- generated CSS is emitted under `lab/nakshatra-precession-explorer/assets/css/`; an inspectable copy of the 3D/VyomaSutra module is emitted under `assets/js/`, while the executable module remains inline for `file://` compatibility
- the old Python compiler is removed after the Node compiler and golden compatibility fixtures pass
- no old-parser fallback is kept; vNext is backward compatible with current canned `.vysu` scripts

> I would prefer TypeScript, but I am fine with plain JavaScript if it makes it easier to integrate with the existing app. Let us make a decision based on what is easier to get working now.
>
> **State: accepted.** TypeScript remains preferred for reuse in other tools, but implementation may start as plain JavaScript if that is the fastest low-churn path into the current app.

> Is the generation and store of JSON necessary? Why can't we just interpret the VyomaSutra text directly in the browser? The browser interpreter compiles it just in time to story JSON. We can edit the JSON in the browser if needed. Let us not have save semantics at all. Just run vysu . If needed tweek the JSON in the browser and run again. This is good enough for now. We can add save semantics later if needed.
>
> **State: accepted.** Stage 1 should run VyomaSutra directly in the browser by compiling to transient JSON. Generated JSON is optional for tests/debugging, not a required stored artifact.

Stage 2:

- syntax highlighting
- line numbers
- inline warnings
- alias suggestions
- inspect/copy transient JSON for debugging
- primitive target hierarchy
- target ranges with `..`
- `draw`
- richer effects such as `blink` and `glow`
- optional numeric vector math for camera/generated geometry

Later:

- browser-side story drafts
- export `.json`
- optional named camera presets

## Compiler Implementation Plan

Keep the compiler modular so grammar changes are auditable and testable:

1. Tokenize lines into comments, metadata, quoted text, punctuation, duration tuples, sigils, identifiers, and numbers.
2. Parse statements and timed blocks into a small AST without resolving target meaning.
3. Resolve identifiers through registries for commands, targets, aliases, camera presets, labels, effects, nakshatra ids, and marker ids.
4. Lower the AST into strict in-memory story JSON cues.
5. Validate unsupported properties, ambiguous aliases, Stage 2 syntax, and ignored tokens with deterministic line-specific warnings.
6. Format warnings identically for Node build-time compilation and browser scratch compilation.
7. Add golden fixtures for current `.vysu` scripts before deleting `src/jyotisha_2026/vysu.py`.

Do not keep an old-parser fallback. The current story asset set is small, and vNext is required to be backward compatible with the existing canned scripts. Compatibility should be enforced through fixtures, not by running two compilers.

The CLI exists for validation, tests, build checks, and optional debug output. The browser runner should not depend on pre-generated JSON files in Stage 1.

## Design Principles

- JSON is the internal executable format.
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
3. Lowering rules: how parsed statements become strict transient story JSON.
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

This is the accepted Stage 1 grammar. It is intentionally declarative: timing, target-list, style, label, and effect sugar are supported, but loops and bespoke macros are not.

> Is the ws in `line  ::= ws* statementList? comment? newline` mean white space
>
> **State: accepted.** `ws` means horizontal whitespace: spaces and tabs, not newline. The lexical conventions below make this explicit.

```ebnf
program          ::= line*
line             ::= ws* statementList? comment? newline
statementList    ::= statement (";" statement)*
comment          ::= "#" text
                   ; but #RGB and #RRGGBB are color tokens, not comments

statement        ::= timedStatement | command | timedBlock
timedStatement   ::= timing command
timedBlock       ::= timing "{" statementList "}"
timing           ::= "at" time | "after" duration | signedDuration

command          ::= stageStmt
                   | visibilityStmt
                   | styleStmt
                   | cameraStmt
                   | travelStmt
                   | gridStmt
                   | captionStmt
                   | labelStmt
                   | clearStmt
                   | waitStmt
                   | seqStmt
                   | flashStmt
                   | effectStmt
                   | fullscreenStmt
                   | defaultsStmt

stageStmt        ::= ("stage" | "scene") stageArg*
stageArg         ::= "blank" | "all" | lightArg | yearArg | cameraPreset
lightArg         ::= "night" | "twilight" | "day"
yearArg          ::= ("year" | "epoch") number

visibilityStmt   ::= visibilityVerb targetList transitionArg*
visibilityVerb   ::= "show" | "hide" | "reveal" | "rollout" | "fade"
transitionArg    ::= modeArg | orderArg | directionArg | durationArg | easeArg
modeArg          ::= "instant" | "fade" | "stagger" | "rollout"
orderArg         ::= "default" | "ecliptic" | "reverse-ecliptic" | "north-to-south" | "south-to-north"
directionArg     ::= "forward" | "reverse"
easeArg          ::= "ease" identifier

styleStmt        ::= "style" targetList styleArg+
styleArg         ::= styleKey value | sugarStyle
sugarStyle       ::= colorSpec | alphaSpec | "font+" number? | "font-" number? | "line+" number? | "line-" number?

cameraStmt       ::= ("camera" | "move" | "cut") cameraSpec durationArg?
cameraSpec       ::= cameraPreset | cameraArgs
cameraArgs       ::= ("pos" vec3)? ("target" vec3)? ("fov" number)?

travelStmt       ::= ("travel" | "epochTravel") ("year" | "epoch")? number "to" number travelArg*
travelArg        ::= durationArg | "step" yearDuration | "rate" travelRate | easeArg
travelRate       ::= number "y/s" | "slow" | "normal" | "fast"

gridStmt         ::= "grid" ("ecliptic" | "ecl" | "equatorial" | "equator" | "eq") number colorSpec?
captionStmt      ::= ("caption" | "say" | "title") quotedText captionArg*
captionArg       ::= durationArg | colorSpec | alphaSpec | sizeArg | screenLocation | fadeArg
fadeArg          ::= "fade" duration (":" duration)?
                   | "fadeIn" duration
                   | "fadeOut" duration
sizeArg          ::= "size" number | "font" number | number "px"

labelStmt        ::= "label" identifier quotedText labelArg*
labelArg         ::= colorSpec | alphaSpec | sizeArg | screenLocation | targetFollow | "class" identifier
targetFollow     ::= "at" "target" targetAtom deltaArg*
clearStmt        ::= "clear" ("label" identifier | "labels")

waitStmt         ::= "wait" duration
seqStmt          ::= ("seq" | "sequence") duration
flashStmt        ::= ("flash" | "pulse") targetList effectArg*
effectArg        ::= durationArg | repeatArg | "gap" duration | colorSpec | alphaSpec
repeatArg        ::= number "x"
effectStmt       ::= "effects" speedSpec
defaultsStmt     ::= "defaults" defaultArg+
defaultArg       ::= "tempo" speedSpec | "effects" speedSpec | "travel" travelRate
fullscreenStmt   ::= "fullscreen" | "theater" | "exitFullscreen" | "canvas"

targetList       ::= targetAtom (("," | "and") targetAtom)*
targetAtom       ::= sigilNak | namedTarget | dottedTarget | groupTarget
sigilNak         ::= ("$" | "*" | "@") identifier
namedTarget      ::= identifier
dottedTarget     ::= identifier ("." identifier | "." number)+
groupTarget      ::= "sky" | "guides" | "poles" | "seasons"

screenLocation   ::= "screen" screenAnchor deltaArg*
screenAnchor     ::= number | "N" | "NE" | "E" | "SE" | "S" | "SW" | "W" | "NW" | "C"
deltaArg         ::= "dx" signedNumber | "dy" signedNumber | signedVec2

durationArg      ::= "over" duration | legacyDurationTuple | bareDuration
legacyDurationTuple ::= number ":" number? ":" number?
bareDuration     ::= number | number "ms" | number "s"
duration         ::= number | number "ms" | number "s"
yearDuration     ::= number | number "y"
speedSpec        ::= number "x" | "slow" | "normal" | "fast"

colorSpec        ::= colorName | hexColor | rgbColor
hexColor         ::= "#" hex{3,6}
alphaSpec        ::= "%" number | number "%" | number
vec3             ::= number "," number "," number
signedVec2       ::= signedNumber "," signedNumber
quotedText       ::= '"' text '"'
signedDuration   ::= ("+" | "-") duration
```

Lexical conventions:

- `ws` means spaces and tabs only.
- `newline` ends a source line.
- `text` in comments runs until newline.
- `identifier` starts with a letter or `_`, then contains letters, digits, `_`, or `-`.
- Keywords are matched case-sensitively.
- Target aliases may accept case-insensitive forms through semantic resolution, but the parser should not depend on case folding.

Target lists require comma separators. `and` is allowed as readability sugar, but bare-space target lists are rejected because command arguments and properties become ambiguous.

The grammar intentionally accepts broad shapes. Semantic tables decide which target-specific and command-specific properties are meaningful. The tables below are the intended Stage 1 language contract; the TypeScript compiler and browser compiler should converge on this contract.

Stage 2 adds `draw`, primitive target hierarchy, registry-backed ranges such as `nak.ash..nak.mrg`, richer effects such as `blink` and `glow`, and optional numeric vector math. Those features should warn until implemented.

### Ambiguity Policy

The grammar plus semantic tables must be deterministic enough that the same source always produces one parse and one lowering.

Implementation requirements:

- Validate the Stage 1 grammar with a parser generator or equivalent parser tests before treating it as stable.
- Prefer keyworded properties when positional parsing would be ambiguous.
- Keep comma-separated target lists; do not allow bare-space target lists.
- Resolve aliases through registries after parsing, not by changing grammar shape.
- If one token sequence could lower in two meaningful ways, reject it with a warning and revise the grammar or semantic table.
- If parser-generator validation shows ambiguity, the grammar should be revised before implementation expands the accepted surface.

## Semantic Tables

### Commands

| Command                       | Shape                                          | Lowers to          | Notes                                                                                        |
| ----------------------------- | ---------------------------------------------- | ------------------ | -------------------------------------------------------------------------------------------- |
| `stage`                       | `stage <stage-props...>`                       | `initial` or `set` | Initial before first cue; runtime reset/set after emitted cues.                              |
| `show`, `reveal`              | `show <target-list> <transition-props...>`     | `reveal`           | Aliases in Stage 1; both use target defaults unless mode/order/duration are supplied.        |
| `hide`                        | `hide <target-list> <transition-props...>`     | `hide`             | Uses target defaults.                                                                        |
| `rollout`                     | `rollout <target-list> <transition-props...>`  | `reveal`           | Sugar for `show <target-list> rollout`.                                                      |
| `fade`                        | `fade <target-list> <transition-props...>`     | `reveal`           | Sugar for `show <target-list> fade`.                                                         |
| `flash`                       | `flash <target-list> <transition-props...>`    | `flash`            | Temporary emphasis; must not change durable visibility.                                      |
| `pulse`                       | `pulse <target-list> <effect-props...>`        | repeated `flash`   | Safe repeated emphasis.                                                                      |
| `style`                       | `style <target-list> <style-props...>`         | `set`              | Timed style applies at the scheduled cue time and persists until changed, cleared, or reset. |
| `camera`, `move`              | `camera <camera-props...>`                     | `camera`           | Supports `pos`, `target`, `fov`, `over`; presets are planned.                                |
| `cut`                         | `cut <camera-preset-or-props>`                 | `camera`           | Sugar for camera movement with `over 0`.                                                     |
| `caption`, `say`, `title`     | `caption "text" <caption-props...>`            | `caption`          | Quoted text is required.                                                                     |
| `label`                       | `label <id> "text" <label-props...>`           | `set` or label cue | Persistent UI/screen or target-following annotation.                                         |
| `clear label`, `clear labels` | `clear label <id>`                             | `set` or label cue | Clears one persistent label or all labels.                                                   |
| `travel`, `epochTravel`       | `travel year <from> to <to> <travel-props...>` | `epochTravel`      | `year` is optional sugar.                                                                    |
| `grid`                        | `grid <kind> <step> <color?>`                  | `set`              | Also reveals the chosen grid.                                                                |
| `wait`                        | `wait <ms>`                                    | pending timing     | Adds delay before next emitted cue.                                                          |
| `seq`, `sequence`             | `seq <ms>`                                     | compiler timing    | Top level sets the default step for future timed blocks; inside a block, advances before each following emitted command. |
| `effects`, `defaults`         | speed/default props                            | compiler defaults  | Timed defaults apply at scheduled cue time and affect following cues.                        |
| `fullscreen`, `theater`       | bare command                                   | `fullscreen`       | Theater/canvas affordance.                                                                   |
| `exitFullscreen`, `canvas`    | bare command                                   | `exitFullscreen`   | Leaves theater/canvas mode.                                                                  |

### Command Properties

| Property                     | Type                 | Commands                                                        | Canonical meaning                                                              |
| ---------------------------- | -------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `at`                         | ms                   | all emitting commands                                           | Absolute cue time.                                                             |
| `after`                      | ms                   | all emitting commands                                           | Relative delay before this cue.                                                |
| `over`                       | ms                   | `show`, `hide`, `flash`, `pulse`, `camera`, `caption`, `travel` | Visual/effect/travel duration.                                                 |
| `mode` / bare mode           | enum                 | `show`, `hide`, `flash`                                         | `instant`, `fade`, `stagger`, `rollout`.                                       |
| `order` / bare order         | enum                 | `show`, `hide`, `flash`                                         | `default`, `ecliptic`, `reverse-ecliptic`, `north-to-south`, `south-to-north`. |
| `direction` / bare direction | enum                 | `show`, `hide`, `flash`                                         | `forward`, `reverse`.                                                          |
| `fadeIn`                     | ms                   | `caption`                                                       | Caption fade-in time.                                                          |
| `fadeOut`                    | ms                   | `caption`                                                       | Caption fade-out time.                                                         |
| `fade`                       | `in:out`             | `caption`                                                       | Canonical compact fade pair, as in `fade 250:300`.                             |
| `screen`                     | anchor               | `caption`, `label`                                              | Screen anchor by keypad `1`-`9` or direction marker.                           |
| `dx`, `dy`                   | px                   | `caption`, `label`                                              | Screen or target-following offset.                                             |
| `pos`                        | vec3                 | `camera`                                                        | Camera position.                                                               |
| `target`                     | vec3                 | `camera`                                                        | Camera look target.                                                            |
| `fov`                        | number               | `camera`                                                        | Camera field of view.                                                          |
| `step`                       | number/year duration | `travel`, `grid`                                                | Year sampling for travel; degree spacing for grid.                             |
| `rate`                       | travel rate          | `travel`, `defaults`                                            | Time-travel speed, separate from visual effect duration.                       |
| `blank`                      | flag                 | `stage`                                                         | Reset visible layers to off.                                                   |
| `night`, `twilight`, `day`   | enum                 | `stage`                                                         | Light preset.                                                                  |
| `year`, `epoch`              | number               | `stage`, `travel`                                               | Epoch year.                                                                    |

Identifiers in grammar must resolve through semantic registries: targets, aliases, camera presets, label ids, effect names, nakshatra ids, marker ids, and future draw object ids.

### Target Registry

The source-code registry is the executable source of truth. This PRD table is the language contract the registry must implement.

Target spelling rules:

- Bare names normally mean one named visual target.
- `@name` means a group target. Historical bare group names remain compatibility aliases.
- `*name` means star/dot part-group where supported.
- `$name` means line/stick part-group where supported.
- Any command that accepts a target accepts a comma-separated mix of leaf targets and group targets.

Stage 1 canonical targets:

| Canonical target | Kind | Aliases | Expansion / meaning |
| --- | --- | --- | --- |
| `eclipticGrid` | leaf | `eclGrid`, `eclGridWire` | Ecliptic grid lines |
| `equatorialGrid` | leaf | `equatorGrid`, `eqGrid`, `eq` | Equatorial grid lines |
| `@referencePlanes` | group | `referencePlanes`, `refs` | `eclipticPlane` + `equatorialPlane` |
| `eclipticPlane`, `equatorialPlane` | leaf | none | Reference planes |
| `nsAxis` | leaf | `axis`, `nsaxis` | North-south axis line |
| `@eclipticNakSegments` | group | `eclipticNakSegments`, `nakSegments`, `naksSegments`, `eclipticSegments` | `eclipticBand` + `eclipticDividers` + `eclipticLabels` + `@eclipticPoles` |
| `eclipticBand`, `eclipticDividers`, `eclipticLabels` | leaf | `sectorDividers`, `sectorLabels` where applicable | Ecliptic sector parts |
| `@eclipticPoles` | group | `eclipticPoles` | `NEP` + `SEP` |
| `NEP`, `SEP` | leaf | lowercase accepted | Ecliptic pole dot/label |
| `stars` | leaf/group-like | none | Background star field |
| `*naks` | part-group | `*nak`, `*nakshatra`, `*nakshatras`, `nakshatraStars` | Nakshatra stars/dots only |
| `$naks` | part-group | `$nak`, `$nakshatra`, `$nakshatras`, `nakshatraLines` | Nakshatra stick/line figures only |
| `nakshatraLabels` | leaf/group-like | `naksLabels` | Nakshatra labels only |
| `@naks` | group | `naks`, `nak`, `nakshatra`, `nakshatras`, `@nak`, `@nakshatra`, `@nakshatras` | `*naks` + `$naks` + `nakshatraLabels` |
| `@polarItems` | group | `polarItems` | `@northPolarItems` + `@southPolarItems`; fixed/cultural polar items only |
| `@northPolarItems` | group | `northPolarItems`, `northPolar` | `sisumara` + `matsya` + `thuban` + `polaris` |
| `@southPolarItems` | group | `southPolarItems`, `southPolar` | `agastya` and future south-polar fixed/cultural items |
| `sisumara`, `matsya`, `thuban`, `polaris`, `agastya` | leaf | `shishumara`, `shimshumara`, `abhayaDhruva`, `matsyaDhruva`, `canopus` where applicable | Named polar items |
| `@seasonalFrame` | group | `seasonalFrame`, `seasons`, `rtu`, `rtus` | `equator` + `VE` + `SS` + `AE` + `WS`; no `NP`/`SP` |
| `equator`, `VE`, `SS`, `AE`, `WS` | leaf | lowercase accepted for markers | Seasonal frame leaves |
| `@poleTrack` | group | `poleTrack`, `polePath` | `precessionCircle` + pole-track arc/label + `NP` + `SP` |
| `precessionCircle` | leaf | `precession` | Precession circle line |
| `NP`, `SP` | leaf | lowercase accepted | Moving celestial pole dot/label |
| `overlay` | leaf | none | Screen overlay/caption layer |
| authored label id | leaf | declared by `label <id> ...` | Persistent authored overlay label |

Stage 2 memory: planned but not yet implemented primitive addressability. These forms should warn in Stage 1, not silently compile:

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

| Alias        | Nakshatra                             |
| ------------ | ------------------------------------- |
| `pph`        | Purvaphalguni                         |
| `uph`        | Uttaraphalguni                        |
| `pas`        | Purvashadha                           |
| `uas`        | Uttarashadha                          |
| `ppr`, `pbh` | Purvaproshthapada / Purvabhadrapada   |
| `upr`, `ubh` | Uttaraproshthapada / Uttarabhadrapada |
| `abh`, `n28` | Abhijit                               |

| Sigil  | Meaning                                   |
| ------ | ----------------------------------------- |
| `$ash` | Nakshatra sector only.                    |
| `*ash` | Nakshatra star group plus stick figure.   |
| `@ash` | Sector plus star group plus stick figure. |

### Value Types

| Type           | Examples             | Notes                                                               |
| -------------- | -------------------- | ------------------------------------------------------------------- |
| `ms`           | `650`, `650:`        | Milliseconds. Bare numbers are accepted where duration is expected. |
| duration tuple | `1200:250:350`       | `duration:fadeIn:fadeOut` for captions; duration only elsewhere.    |
| alpha          | `.5`, `%50`, `50%`   | Clamped to 0..1.                                                    |
| color          | `yellow`, `#8eaccb`  | Named colors and hex colors.                                        |
| vec3           | `0,325,0.1`          | No spaces inside the vector token.                                  |
| number         | `45`, `-1800`, `2.6` | Parsed as integer only where the target JSON expects integer years. |

## Sugar

Sugar must always have a documented canonical equivalent.

| Sugar                   | Canonical equivalent                     | Where legal                      |
| ----------------------- | ---------------------------------------- | -------------------------------- |
| `650:`                  | `over 650`                               | duration-bearing commands        |
| `1200:250:350`          | `over 1200 fadeIn 250 fadeOut 350`       | `caption`                        |
| `yellow`                | `color yellow`                           | `style` when a color is expected |
| `%50`                   | `opacity .5`                             | `style`, `caption`               |
| `font+ 2`               | increase current/default `fontSize` by 2 | label-bearing style targets      |
| `font- 1`               | decrease current/default `fontSize` by 1 | label-bearing style targets      |
| `rollout stars`         | `show stars rollout`                     | visibility commands              |
| `fade stars`            | `show stars fade`                        | visibility commands              |
| `cut topDome`           | `camera topDome over 0`                  | camera commands                  |
| `pulse NP 3x over 1200` | repeated `flash NP` cues                 | effect commands                  |

Unsupported sugar should warn. It should not silently disappear.

## Lowering Rules

Visibility and target lists:

```text
show target        -> JSON action "reveal" using target defaults
hide target        -> JSON action "hide" using target defaults
reveal target      -> JSON action "reveal" using target defaults
rollout target     -> JSON action "reveal", mode "rollout"
fade target        -> JSON action "reveal", mode "fade"
show A, B, C       -> one cue per resolved target at the same scheduled time
show A and B       -> same as `show A, B`
```

`show` and `reveal` remain aliases in Stage 1. Intentional animation should be expressed with explicit transition modes: `show naks rollout`, `show stars fade`, `show grid instant`.

Style:

```text
style naks, eclipticNakSegments color #8eaccb alpha .8
style equatorialGrid color red alpha %28
style stars alpha %80 starSize 2.6
```

compiles to partial `set.state` patches against the canonical settings block. A timed `style` applies at its scheduled cue time and persists until changed, cleared, or reset by stage/scene policy.

Stage 1 style knobs are intentionally safe: `color`, `lineColor`, `alpha`, `opacity`, `labelAlpha`, `fontSize`, `font+`, `font-`, `starSize`, and `pointSize`. True line width remains pending because WebGL line width is unreliable without fat-line geometry.

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
caption "Visualize Precession" over 1200 fadeIn 250 fadeOut 350
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
travel -1800 to -800 over 5000 step 100y
travel -1800 to -800 rate 200y/s step 50y
```

compiles to `epochTravel`. `over` controls total animation duration. `rate` controls epoch speed. `step` controls sampling granularity; it is not visual speed.

Camera:

```text
camera topDome over 1200
cut topDome
```

should compile to a camera cue using a named preset.

Current implementation does not yet implement camera presets. Until presets exist, accepted camera syntax should use explicit `pos`, `target`, and/or `fov`, and unsupported preset names must warn.

Flash:

```text
flash precessionCircle 1500:
flash @ash, *mrg over 650
pulse NP 3x over 1500 gap 120
```

`flash` compiles to a `flash` cue. `pulse` compiles to repeated `flash` cues. Both are temporary emphasis; neither should change durable visibility.

Persistent labels:

```text
label title "Visualize Precession" at screen 8 dy 24
label pole "Moving north pole" at target NP dx 12 dy -8
clear label pole
clear labels
```

Labels persist until replaced by the same id, explicitly cleared, or cleared by stage/scene reset policy.

Fullscreen:

```text
fullscreen
exitFullscreen
```

compiles to `fullscreen` / `exitFullscreen` story cues for theater viewing of the 3D canvas.

## Timing Model

Rules:

- first emitted cue defaults to `at: 0`
- each scope has a timing cursor; the top-level cursor starts at `0`, and a timed block starts with its own local cursor at the block base
- absence of timing means "start at the current scope cursor"
- absence of timing does not advance the cursor
- `;` separates statements but does not imply sequencing
- multiple un-timed statements on the same line or adjacent lines start concurrently unless delayed
- `wait 500` advances the current scope cursor by 500 ms and emits nothing
- `seq 200` at top level sets the default sequence step for future timed blocks
- `seq 200` inside a timed block advances the local block clock by 200 ms before each following emitted command
- `seq 0` disables sequence stepping from that point in scope
- `+500 command` is sugar for relative timing: advance the current scope cursor by 500 ms, then schedule the command there
- `after 500 command` is canonical relative timing and behaves like `+500 command`
- `at 12000 command` is absolute timing within the current scope and does not move the cursor
- timing operators can apply to blocks: `at 1000 { opA; opB; +100 opC }`
- inside a timed block, `at N` is local to the block base, not global story time
- inside a timed block, `+N` and `after N` advance the block-local cursor
- bare `over 500` or `500:` means duration, not cue position

Example:

```text
caption "A" over 1000
after 500 caption "B" over 1000
+250 flash NP over 900

at 0 {
  caption "Start"
  reveal $naks
  +50 reveal *naks
}

at 1000 {
  show equator, ecliptic.circle, nsAxis
  +100 flash NP
  at 50 caption "local time inside block" over 800
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

The final block schedules `show` at global `1000`, `flash` at global `1100`, and the inner `caption` at global `1050`. This is valid even though source order is not chronological.

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
- Unsupported Stage 2 syntax such as `draw`, target ranges, `blink`, or `glow`: warn.
- `rate` plus `over` ambiguity: warn if both cannot be honored coherently.
- Screen location on an incompatible command: warn.
- Primitive target parsed without resolver support: warn.
- Compiler warnings must be visible in both browser and build-time flows.

Silent ignore is only acceptable for whitespace, comments, metadata comments, and redundant separators.

## Examples

Valid and meaningful:

```text
# Start clean
stage blank night year -1800

caption "Visualize Precession" 1200:
show eclipticGrid
show eclipticNakSegments, guides
rollout stars
rollout naks

caption "1800 BCE"
travel year -1800 to -800 over 5000 step 100y
```

Valid and meaningful style:

```text
style naks color #8eaccb alpha .8 font+ 2
style eclipticNakSegments alpha .25
style nsAxis, equator color yellow
flash VE, NP
```

Valid and meaningful primitive/sigil targets:

```text
hide NEP
show SEP
flash NP
flash $ash 650:
flash *ash 650:
flash @ash 650:
label pole "Moving pole" at target NP dx 12 dy -8
clear label pole
```

Valid syntax but currently unsupported semantics, with warnings:

```text
style sector.3 color #d4a56a alpha .35
rollout nak.ashvayuk
show star.agastya
draw arc poleTrack.arc gold over 1200
blink VE 2x over 400
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
- inspect/copy transient JSON for debugging
- run VyomaSutra story
- no build step if possible

## Acceptance Criteria

- A human can author a basic precession story in fewer than 15 lines.
- Common aliases like `naks`, `eclipticGrid`, `eclipticNakSegments`, `rtus`, `Agastya`, `NEP`, `NP` compile correctly.
- Current canned `.vysu` scripts compile without manual migration.
- Target-list commands compile one cue per resolved target at the same scheduled time.
- Timed blocks schedule statements using local block time.
- `style`, `label`, `clear label(s)`, `pulse`, `over`, and `rate` have deterministic lowerings or deterministic warnings.
- The browser can run VyomaSutra directly by compiling to transient story JSON accepted by the existing runner.
- The Node CLI validates the same source and can optionally emit debug/golden JSON for tests.
- Compilation warnings are readable and line-specific.
- The original JSON runner/debug path remains available, but JSON is not the primary authoring flow.

## Deferred Decisions

- Canonical expansions for `sky`, `poles`, and `seasons`.
- Camera preset storage location.
- Individual nakshatra alias generation and disambiguation.
- Syntax highlighting versus browser-side draft save priority.
- Stage/scene reset policy for persistent labels.

> From the grammar and the semantic tables is it possible to assert that there is no ambiguity while interpreting the VyomaSutra commands? This could be validated using a parser generator. If not, we need to revise the grammar and semantic tables to eliminate ambiguities.
>
> **State: accepted.** Added an ambiguity policy. Stage 1 should be validated with a parser generator or equivalent parser tests; any detected ambiguity should force grammar/table revision before implementation broadens the language.
