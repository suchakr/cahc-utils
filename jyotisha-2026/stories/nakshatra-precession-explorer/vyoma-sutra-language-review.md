# VyomaSutra Language Review and Improvement Proposal

Status: review draft
Related files:

- `stories/nakshatra-precession-explorer/vyoma-sutra-prd.md`
- `stories/nakshatra-precession-explorer/SKILL.md`
- `src/jyotisha_2026/vysu.py`
- `lab/nakshatra-precession-explorer/index.html`

## Purpose

This note captures a review of the current VyomaSutra grammar, Python compiler, browser compiler, and example scripts. It is intended as an inline-commentable proposal before implementation changes.

The goal is to improve the language safely:

- preserve strict story JSON as the runtime contract
- reduce authoring friction
- improve cognitive coherence
- add expressive sugar with clear lowerings
- support stronger visual primitives
- separate time-travel speed from visual-effect speed
- add vector and screen-location primitives without becoming a general programming language

## Current Context

VyomaSutra is a forgiving authoring language for 3D sky stories. It compiles to story JSON consumed by the existing story runner.

Current authoring sources live as `.vysu` files under `stories/nakshatra-precession-explorer/`. Build-time compilation is handled by `src/jyotisha_2026/vysu.py`. Browser-side scratch compilation is currently embedded in the generated lab page.

The current implementation has useful baseline support:

- metadata comments: `# title:`, `# version:`, `# featured:`, `# group:`, `# tags:`, `# order:`
- stage setup: `stage blank night year -1800`
- camera: `camera pos ... target ... fov ...`
- visibility: `show`, `hide`, `reveal`, `rollout`, `fade`
- caption: `caption "..." 1200:250:350`
- time travel: `travel -1800 to -800 5000: step 100`
- flash: `flash NP 2000:`
- grid: `grid ecliptic 10 blue`
- sequencing: `wait 500` and `;`

## Compiler Strategy

### Recommendation

Move toward one real compiler implementation, preferably JavaScript/TypeScript, with Python as an optional thin build wrapper only if needed.

Given the new lab now has Node dependencies in addition to `uv`, the earlier reason to maintain a full Python compiler is weaker. A JS-only compiler can be the source of truth because:

- the interactive editor already needs browser-side compilation
- language UX features such as inline warnings, syntax highlighting, quick previews, and autocomplete are naturally JS-side
- one implementation avoids Python/browser drift
- build-time story compilation can run under Node just like frontend builds
- strict JSON remains the runtime boundary, so the rest of the app does not need to care which compiler produced it

> I agree with this. Since the lab already depends on Node, this is a no-brainer. Let us remove the python compiler completely.
>
> **State: accepted.** The compiler source of truth should be JS/TS. The Python compiler should be removed as part of the JS compiler migration, not preserved as a parallel linter.

### Safe Migration Plan

Delete the Python compiler as part of the JS compiler migration:

> Why . The python compiler is just a linter and needs to catch up with JS all the time with very little value added.
>
> **State: accepted.** Revised plan removes the Python compiler instead of keeping it as a wrapper/linter.

1. Extract current browser compiler into source under `apps/` or a shared JS module.
2. Add a Node CLI such as `node scripts/compile-vysu.mjs nakshatra-precession-explorer`.
3. Add golden tests that compile all current `.vysu` files and compare meaningful JSON output.
4. Replace `scripts/compile_stories.py` with the Node compiler flow.
5. Remove `src/jyotisha_2026/vysu.py`.
6. Update authoring docs and package scripts so the supported command path is Node-based.

### Why Not Keep Two Compilers?

Two full compilers are costly here because the language is evolving. Drift has already appeared:

- the PRD documents `style`, `over`, explicit timing modifiers, camera presets, and mid-story `stage`
- the browser compiler implements some `style` support
- the Python compiler does not implement `style`
- Python treats all `stage` statements as initial-state mutation, even mid-story

Two compilers only make sense if a shared grammar/test suite exists and both are required independently. For this lab, the better engineering tradeoff is one compiler plus tests.

## Productive Review Workflow

Use this Markdown file for inline comments and decision tracking.

For review and fix cycles, prefer one continuing Codex/agent session for a single coherent design pass. A continuing session is better when:

- comments refer to earlier tradeoffs
- the grammar is being refined incrementally
- the same files are being edited repeatedly
- implementation follows directly from agreed decisions

Start a fresh session when:

- switching from language design to unrelated app work
- the prior thread has become very long or stale
- you want an independent review of the accepted grammar
- implementation has already landed and the next task is validation or cleanup

Recommended pattern:

1. Use one running session for this design document and one or two comment/fix rounds.
2. Once grammar decisions settle, start a fresh implementation session with the finalized doc as context.
3. Use another fresh session for independent review after implementation.

This balances continuity for design with cleaner context for coding and review.

## Main Risks in Current Language

### Spec and Implementation Drift

The PRD is ahead of the compiler. That is acceptable during design, but unsafe when scripts start using promised syntax.

> I agree. I would like the implementation and PRD ( including grammar) to be in sync. So delta improvements should be in tandem in both the places.
>
> **State: accepted.** After this review draft stabilizes, patch PRD, SKILL, implementation, and tests together for each grammar delta.

Examples:

- `style nsAxis yellow` appears in `precession-explorer.vysu`, but build-time Python currently warns on `style`.
- mid-story `stage blank night year -4000` looks like a runtime reset, but Python currently mutates initial state instead.
- `over 900`, `after 500 show ...`, and `travel year -1800 to -800 over 5000` are documented but not fully implemented in Python.

Recommendation: make warnings explicit and testable. Unsupported documented syntax should either compile correctly or warn loudly.

### Implicit Timing Can Become Hard to Read

Current scripts rely heavily on implicit `+0`, `wait`, and cue duration side effects. This is compact, but authors can lose track of whether commands overlap or sequence.

Recommendation: keep implicit timing for compact scripts, but add explicit timing forms:

```text
+500 caption "1800 BCE" over 1200
after 500 show stars fade over 900
at 12000 travel -1800 to -800 over 5000 step 100y
```

### Target Addressability Is Too Coarse

Current targets cover major groups, but storytelling wants primitive targets:

- one nakshatra sector
- one nakshatra label
- one star or marker
- one arc segment
- one screen label following a world target

Recommendation: implement target hierarchy before adding many new commands.

## Design Principles

1. JSON remains the executable runtime format.
2. Every sugar has a documented canonical lowering.
3. Commands should read as visual narration, not application internals.
4. Timing, visual effects, and epoch travel must be separate concepts.
5. New language features should be declarative unless there is a proven need for control flow.
6. Unknown or ignored input should warn with line-specific messages.
7. One compiler should define the contract.

## Proposed Grammar

This grammar is intentionally small. It should be broad enough for authoring and narrow enough to compile safely.

> small yet expressive and easy to read - this is the sweet spot for vyoma sutra.
>
> **State: accepted.** Keep the language declarative and compact; reject features that require general programming semantics unless there is a demonstrated authoring need.

```ebnf
program          ::= line*
line             ::= ws* statementList? comment? newline
statementList    ::= statement (";" statement)*
statement        ::= timedStatement | command | timedBlock

timedStatement   ::= timing command
timedBlock       ::= timing "{" statementList "}"
timing           ::= "at" time
                   | "after" duration
                   | signedDuration

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
                   | flashStmt
                   | effectStmt
                   | drawStmt
                   | fullscreenStmt
                   | defaultsStmt

stageStmt        ::= ("stage" | "scene") stageArg*
stageArg         ::= "blank" | "all" | lightArg | yearArg | cameraPreset
lightArg         ::= "night" | "twilight" | "day"
yearArg          ::= ("year" | "epoch") number

visibilityStmt   ::= visibilityVerb targetList transitionArg*
visibilityVerb   ::= "show" | "hide" | "reveal" | "rollout" | "fade"
transitionArg    ::= modeArg | orderArg | directionArg | durationArg | easeArg
modeArg          ::= "instant" | "fade" | "stagger" | "rollout" | "draw"
orderArg         ::= "default" | "ecliptic" | "reverse-ecliptic" | "north-to-south" | "south-to-north"
directionArg     ::= "forward" | "reverse"
easeArg          ::= "ease" identifier

styleStmt        ::= "style" targetList styleArg+
styleArg         ::= styleKey value | sugarStyle
sugarStyle       ::= colorSpec | alphaSpec | "font+" number? | "font-" number? | "line+" number? | "line-" number?

cameraStmt       ::= ("camera" | "move" | "cut") cameraSpec durationArg?
cameraSpec       ::= cameraPreset | cameraArgs | cameraRelative
cameraArgs       ::= ("pos" vec3)? ("target" vec3)? ("fov" number)?
cameraRelative   ::= "look" targetExpr ("from" cameraViewArg*)?
cameraViewArg    ::= "distance" number | "height" number | "az" number | "fov" number

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
targetFollow     ::= "at" "target" targetExpr deltaArg*
clearStmt        ::= "clear" ("label" identifier | "labels")

waitStmt         ::= "wait" duration

flashStmt        ::= ("flash" | "pulse" | "blink" | "glow") targetList effectArg*
effectArg        ::= durationArg | repeatArg | "gap" duration | colorSpec | alphaSpec
repeatArg        ::= number "x"

effectStmt       ::= "effects" speedSpec
defaultsStmt     ::= "defaults" defaultArg+
defaultArg       ::= "tempo" speedSpec | "effects" speedSpec | "travel" travelRate

drawStmt         ::= "draw" drawKind identifier? drawArg*
drawKind         ::= "point" | "line" | "arc" | "band" | "label"
drawArg          ::= "from" locationExpr | "to" locationExpr | "at" locationExpr
                   | "text" quotedText | styleArg | durationArg

fullscreenStmt   ::= "fullscreen" | "theater" | "exitFullscreen" | "canvas"

targetList       ::= targetExpr (targetSeparator targetExpr)*
targetSeparator  ::= "," | "and"
targetExpr       ::= targetAtom | rangeTarget
targetAtom       ::= sigilNak | namedTarget | dottedTarget | groupTarget
sigilNak         ::= ("$" | "*" | "@") identifier
namedTarget      ::= identifier
dottedTarget     ::= identifier ("." identifier | "." number)+
groupTarget      ::= "sky" | "guides" | "poles" | "seasons"
rangeTarget      ::= targetAtom ".." targetAtom

locationExpr     ::= vec3 | targetExpr | screenLocation
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
alphaSpec        ::= "%" number | number "%" | number
vec3             ::= number "," number "," number
signedVec2       ::= signedNumber "," signedNumber
quotedText       ::= '"' text '"'
signedDuration   ::= ("+" | "-") duration
```

### Implementation Stage Grammars

The grammar above is the full vNext direction. Implement it in no more than two additive stages.

Stage 1 grammar should be the current language plus the immediately useful coherence fixes:

```ebnf
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
                   | flashStmt
                   | effectStmt
                   | fullscreenStmt
                   | defaultsStmt

visibilityStmt   ::= visibilityVerb targetList transitionArg*
styleStmt        ::= "style" targetList styleArg+
flashStmt        ::= ("flash" | "pulse") targetList effectArg*
captionStmt      ::= ("caption" | "say" | "title") quotedText captionArg*
labelStmt        ::= "label" identifier quotedText labelArg*
clearStmt        ::= "clear" ("label" identifier | "labels")

targetList       ::= targetAtom (("," | "and") targetAtom)*
targetAtom       ::= sigilNak | namedTarget | dottedTarget | groupTarget
groupTarget      ::= "sky" | "guides" | "poles" | "seasons"
durationArg      ::= "over" duration | legacyDurationTuple | bareDuration
```

Stage 1 explicitly includes:

- JS/TS compiler as source of truth
- current script compatibility
- `at`/`after`/`+` timing
- timed blocks
- `over`
- target lists
- `style`
- persistent `label` and `clear label(s)`
- group targets
- `pulse` as safe repeated flash

Stage 2 adds the richer visual language:

```ebnf
command          ::= stage1Command | drawStmt
drawStmt         ::= "draw" drawKind identifier? drawArg*
drawKind         ::= "point" | "line" | "arc" | "band" | "label"

targetExpr       ::= targetAtom | rangeTarget
rangeTarget      ::= targetAtom ".." targetAtom
targetAtom       ::= sigilNak | namedTarget | dottedTarget | groupTarget | primitiveTarget
primitiveTarget  ::= "star." identifier
                   | "marker." identifier
                   | "nak." identifier primitiveNakPart?
                   | "sector." number primitiveSectorPart?

flashStmt        ::= ("flash" | "pulse" | "blink" | "glow") targetList effectArg*
```

Stage 2 explicitly includes:

- `draw`
- target ranges with `..`
- primitive target hierarchy
- `blink` and `glow`
- optional numeric vector math for camera/generated geometry

## Proposed Target Hierarchy

Group targets:

```text
sky
guides
poles
seasons
ecliptic
equatorial
polarItems
```

Existing canonical targets remain supported:

```text
eclipticGrid
equatorialGrid
eclipticNakSegments
eclipticBand
eclipticDividers
eclipticLabels
eclipticPoles
stars
nakshatras
nakshatraLines
nakshatraLabels
polarItems
northPolarItems
southPolarItems
poleTrack
precessionCircle
seasonalFrame
overlay
referencePlanes
eclipticPlane
equatorialPlane
nsAxis
NEP SEP NP SP
equator VE SS AE WS
agastya thuban polaris matsya sisumara
```

New primitive targets:

```text
star.<id-or-alias>
marker.<id-or-alias>
nak.<id-or-alias>
nak.<id-or-alias>.sector
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

Nakshatra sigils remain:

```text
$ash     # sector only
*ash     # star group plus stick figure
@ash     # sector plus star group plus stick figure
```

> grammar is good . Can it lifted in one go or we build in incremental additive stages. If Incremental addtive - I would like to to see no more than 2 stages. What would the grammars of Stages 1,2 look like?. Draw in stage 2
>
> **State: accepted with refinement.** Use no more than two implementation stages. Stage 1 should cover compiler migration, parity, timing blocks, target lists, style, persistent labels, and current-script compatibility. Stage 2 should cover `draw`, target ranges, primitive target hierarchy, richer effects, and optional numeric vector math.

> what does timing of styeStmt or Effect stmts do?. Do they apply immediately or are staged?
>
> **State: clarified.** Timed `style` and `effects/defaults` apply at their scheduled cue time. `style` persists until changed, cleared, or reset by stage/scene policy. `effects/defaults` affects following cues from that scheduled point.

> what happens to statements without time spec
>
> **State: clarified.** No time spec means "start now" at the current block scheduling point. It does not mean "after the previous cue." `;` separates statements but does not sequence them.

> On caption we 1000:250:300 notation for duration fadeIn fadeOut .. is this special only for captions or can we use it for other statements too? While I recall adding the sugar , I have my regrets now. To be backwrd compatible with all previous stories and scripts .. aybe we honor it but warn that we may remove it in future or suggest the way out.
>
> **State: accepted.** Keep tuple syntax as `legacyDurationTuple` for compatibility. Canonical new syntax is `over 1000 fadeIn 250 fadeOut 300` or `over 1000 fade 250:300`. For non-caption commands, tuple values beyond duration should be ignored or warned; do not expand tuple-fade semantics further.

> The identifier part is not clear - I assume these must be enumenrated with aliases
>
> **State: accepted.** Grammar can say `identifier`, but semantics must resolve identifiers through registries: targets, aliases, camera presets, label ids, effect names, nakshatra ids, marker ids, and future draw object ids.

> Can there be rangeTargets like ash-mrigashira or ash-mrig ? Or star.104-109 etc ? How to represent that in grammar?
>
> **State: accepted with syntax choice.** Use `..` for ranges, not `-`: `nak.ash..nak.mrg`, `sector.1..sector.5`, `star.104..star.109`. Range resolution must be registry-backed.

> I assume this is a superset of current VyomaSutra grammar and old scripts should continue to work . Or do we have to auto migrate? The past dependencies are only the canned vyomaSutra scripts and they do not use the complex features we are planning to add.
>
> **State: accepted.** vNext should be a superset for current canned scripts. Auto-migration/formatting is useful later, but current scripts should compile without requiring manual migration.

> Captions are not persistent now. There is a need to a long lived captions/labels . This can be used for eg keeping the title/ subtitles , or labels on planets,rasi etc which are not part of the 3d scene . It will be nice to have a separate syntax for it. How to tie this to scene changes?
>
> **State: accepted.** Added `label` and `clear label(s)` syntax. Labels are persistent UI/screen or target-following annotations. They persist until replaced by the same id, explicitly cleared, or cleared by scene/stage reset policy.

## Proposed Sugars and Lowerings

### Scene Setup

```text
scene blank night -1800
```

Canonical:

```text
stage blank night year -1800
```

### Camera Cuts and Moves

```text
cut top
move perspective over 1200
camera look nak.ash from distance 250 height 18 fov 38
```

Canonical:

- `cut` lowers to a camera cue with duration `0`
- `move` lowers to a camera cue with supplied/default duration
- `camera look ...` computes `pos`, `target`, and `fov` at compile time

### Common Groups

```text
show sky
hide guides
show poles
```

Canonical:

- `sky`: stars, nakshatras, eclipticNakSegments
- `guides`: grids, referencePlanes, overlay
- `poles`: eclipticPoles, northPolarItems, poleTrack

The exact group expansion should live in a semantic table.

### Effects

```text
pulse NP 3x over 1800
blink VE 2x over 400 gap 150
glow poleTrack over 1200 gold
```

Canonical:

- `pulse`: repeated `flash` cues
- `blink`: controlled hide/show or flash sequence
- `glow`: temporary style plus flash, then restore if restore support exists

If restore support does not exist yet, `glow` should warn or lower only to `flash`.

### Repetition and Generated Stories

Do not add `foreach` or a bespoke `tour` macro to VyomaSutra.

The declarative story-language test rules both out:

- `foreach` turns VyomaSutra into a small programming language and invites variables, filters, conditionals, scope, nested loops, and debugging generated timing.
- `tour naks` is safer than `foreach`, but too bespoke. It solves one verbose script rather than a general language need.

If a canned story is repetitive, use an external generator that emits ordinary readable `.vysu`. The generated story remains inspectable, compilable, and editable without loop semantics in the language.

## Timing Model

Keep current implicit timing but add explicit forms.

Rules:

- first emitted cue defaults to `at: 0`
- later emitted cues default to `at: "+0"`
- absence of timing means "start now", not "after the previous cue"
- `;` separates statements but does not imply sequencing
- multiple un-timed statements on the same line or adjacent lines start concurrently unless delayed
- `wait 500` adds delay before next emitted cue
- `+500 command` is sugar for relative timing
- `after 500 command` is canonical relative timing
- `at 12000 command` is absolute timing
- timing operators can apply to blocks: `at 1000 { opA; opB; +100 opC }`
- inside a timed block, `at N` is local to the block base, not global story time
- inside a timed block, `+N` and `after N` are local relative offsets
- `over 900` is duration, never cue position
- `step 100y` is sampling granularity, not travel speed
- `rate 200y/s` is travel speed

Examples:

```text
caption "A" over 1000
after 500 caption "B" over 1000
+250 flash NP over 900
at 12000 travel -4000 to -2800 rate 200y/s step 50y
```

Grouped timing is the preferred way to set up scenes without repeating `at N`:

```text
at 0 {
  caption "Start"
  reveal $naks
  +50 reveal *naks
}

at 1000 {
  show equator, ecliptic.circle, nsAxis
  +100 flash NP
}
```

The block sets a local time origin. In `at 1000 { +100 flash NP }`, the flash is scheduled at global `1100`.

Inner `at` is allowed, but it is local to the enclosing block:

```text
at 1000 {
  opA
  opB
  +100 opC
  at 50 opD
}
```

This schedules:

- `opA` at global `1000`
- `opB` at global `1000`
- `opC` at global `1100`
- `opD` at global `1050`

This is valid. The compiler should not require source order to match scheduled order inside a block. Authors may still choose chronological source order when it improves readability:

```text
at 1000 {
  opA
  opB
  at 50 opD
  at 100 opC
}
```

Example mental model:

```text
caption "Start"; reveal $naks; +400 reveal *naks
```

This lowers to:

- `caption "Start"` at `0`
- `reveal $naks` at `+0`, so it starts at the same story time as the caption
- `reveal *naks` at `+400`, so it starts 400ms after the previous scheduling point

If the desired meaning is "caption first, then reveal sector, then reveal stars", write explicit sequencing:

```text
caption "Start" over 1000
after 1000 reveal $naks
after 400 reveal *naks
```

or use `wait`:

```text
caption "Start" over 1000
wait 1000
reveal $naks
wait 400
reveal *naks
```

## Time Travel Speed

Separate travel speed from animation duration.

Supported forms:

```text
travel -4000 to -2800 over 7s step 100y
travel -4000 to -2800 rate 200y/s step 50y
travel -4000 to -2800 rate slow
```

Lowering:

- `over` writes cue `duration`
- `rate` computes duration from year span unless `over` is also present
- if both `over` and `rate` are present, warn and let `over` win
- `step` controls epoch sampling

## Visual Effect Speed

Support global and local effect speed.

```text
defaults effects normal
effects 0.75x
show naks rollout slow
flash NP quick
caption "Pole drift" over slow
```

Suggested named speeds:

```text
quick  = 500ms
normal = 1000ms
slow   = 1800ms
grand  = 3000ms
```

These names should be semantic table values, not hard-coded across the compiler.

## Target Collections

The more important "vector" need is target collections, not numeric `x,y,z` vector math. Any command that accepts a target should accept one or more targets, including just-in-time composed target lists.

Examples:

```text
flash equator, ecliptic.circle, nsAxis over 1200
show stars and naks and eclipticNakSegments rollout over 3000
style NP, SP, NEP, SEP yellow alpha .8
pulse VE, SS, AE, WS 2x over 1600
```

Canonical lowering:

- one source statement may lower to one cue with a `targets` array if the runtime supports it
- otherwise it lowers to one ordinary cue per target, all with the same timing
- all targets in a single target list start concurrently unless the command explicitly supports staggering

Target collections can be implicit or explicit.

Implicit collections:

```text
sky
guides
poles
seasons
naks
```

Explicit collections:

```text
equator, ecliptic.circle, nsAxis
VE, SS, AE, WS
$ash, *ash
```

Named collections should be possible later:

```text
targets solsticeMarkers = VE, SS, AE, WS
flash solsticeMarkers over 1200
```

Target ranges should use `..`, not `-`, to avoid ambiguity with hyphenated aliases and subtraction-like reading:

```text
flash nak.ash..nak.mrg over 2000
show sector.1..sector.5 rollout
flash star.104..star.109
```

Range resolution must be registry-backed. For example, nakshatra ranges use canonical nakshatra order, sectors use numeric order, and star ranges only work if the star registry has stable numeric ids.

## Numeric Vector Operations

Numeric vector operations are still useful for cameras and generated geometry, but they should be secondary.

If added, keep them compile-time only at first:

```text
let origin = 0,0,0
let top = pos 0,325,0.1 target origin fov 42
camera top
camera offset current by 0,20,0
```

Do not add arbitrary expressions or function calls until the compiler has a typed AST and test coverage.

## Screen Location Specification

Add explicit screen anchors for captions and labels.

Numeric keypad anchors:

```text
7 8 9
4 5 6
1 2 3
```

Direction anchors:

```text
NW N NE
W  C E
SW S SE
```

Examples:

```text
caption "1800 BCE" at screen 9 dx -24 dy 32
caption "Pole drift" at screen NE dx -20 dy 20
label NP "moving pole" at target NP dx 12 dy -8
```

Rules:

- screen `dx`/`dy` are pixels
- world offsets must use `world` or vector syntax
- target-following labels should declare their target explicitly

## Warning Rules

Warnings are part of the language contract.

Warn on:

- unknown command
- unknown target
- ambiguous alias
- unsupported property
- invalid number or unit
- ignored token
- unsupported sugar
- mid-story `stage` if runtime lowering is not implemented
- `rate` plus `over` conflict
- screen location on a command that cannot display screen UI
- primitive target that parses but has no runtime resolver yet

Silent ignore is acceptable only for:

- whitespace
- comments
- metadata comments
- redundant separators

## Safe PRD and Implementation Plan

### Source of Truth

This review document is the temporary working surface. It should not remain the long-term source of truth.

After one or two more review rounds:

1. Promote accepted Stage 1 grammar and semantics into `vyoma-sutra-prd.md`.
2. Reduce this review file to historical rationale, or mark it superseded.
3. Patch `SKILL.md` only with implemented, safe-to-author syntax.
4. Land compiler changes and grammar fixtures in the same implementation branch.

The PRD should then be the source of truth for grammar and semantics. The implementation and tests should be treated as the executable source of truth.

### Fallback Strategy

Do not build a second legacy parser fallback unless tests prove it is needed.

A fallback parser is probably overengineering because:

- there are only a few current `.vysu` assets
- vNext is intended to be backward compatible
- two parser paths can recreate the Python/JS drift problem inside JS
- golden tests over the current scripts provide a cheaper safety net

Use compatibility tests instead:

- compile every current `.vysu` source with the new compiler
- compare normalized story JSON against current output where behavior should remain unchanged
- check warnings are deterministic and expected
- manually run the lab stories after compiler migration

If a current script breaks, fix the vNext parser or add a narrow compatibility rule. Avoid a broad "try new parser, then old parser" strategy.

### Modular Compiler Shape

The JS/TS compiler should be modular even without a fallback parser.

Recommended modules:

- `tokenize`: comments, strings, separators, braces
- `parse`: statements, timed blocks, target lists, values
- `resolve`: target aliases, group targets, ranges, camera presets, labels
- `lower`: AST to strict story JSON cues/state
- `validate`: story JSON shape and semantic warnings
- `formatWarnings`: stable author-facing diagnostics
- `fixtures`: golden input/output examples

This makes it easy to support old and new syntax in one grammar without keeping two compilers.

### Stage 1 Implementation

Stage 1 should make the revised grammar usable while keeping scope bounded:

- extract the browser compiler into a source JS/TS module
- add a Node CLI for story compilation
- remove `src/jyotisha_2026/vysu.py`
- replace the Python story compile flow with the Node CLI
- add fixtures for all current `.vysu` scripts
- support current syntax as a compatibility subset
- implement `at`, `after`, leading `+/-`, and timed blocks
- implement `over`
- implement target lists with comma and `and`
- implement `style`
- implement `label` and `clear label(s)`
- implement group targets
- implement `pulse` as repeated flash
- make warning output deterministic

Stage 1 should not include `draw`, primitive target ranges, loop/macro constructs, or numeric vector expressions.

### Stage 2 Implementation

Stage 2 adds richer visual authoring after Stage 1 is stable:

- primitive target hierarchy: `nak.*`, `sector.*`, `star.*`, `marker.*`
- range targets with `..`
- `draw point|line|arc|band|label`
- `blink` and `glow`
- camera-relative helpers if still needed
- optional numeric vector math for camera/generated geometry
- editor autocomplete/highlighting from semantic registries

## Open Questions

1. Should the canonical compiler be plain JS or TypeScript?

   > it should be TS. We want to use it in other tools too. If TS infra needs are beyond node. JS is good enough.
   >
   > **State: accepted.** Prefer TypeScript for reusable compiler modules. Fall back to plain JS only if TS setup creates disproportionate infrastructure churn.

2. Should the compatibility command remain `uv run python scripts/compile_stories.py ...`, wrapping Node, or should story compilation become explicitly Node-based?

   > I think it should become explicitly node based.
   >
   > **State: accepted.** Story compilation should be explicitly Node-based. Do not keep a Python wrapper.

3. Should `show` default to target-specific animation while `reveal` means intentional animation, or should they remain aliases?

   > Explain this question with examples
   >
   > **State: accepted.** Keep `show` and `reveal` aliases in Stage 1. Use explicit modes for intent: `show naks rollout`, `show stars fade`, `show grid instant`.
   >
   > Explanation: the question is whether `show` and `reveal` should mean the same thing.
   >
   > Option A: keep them aliases. This is simpler:
   >
   > ```text
   > show naks
   > reveal naks
   > ```
   >
   > Both lower to the same reveal cue using target defaults.
   >
   > Option B: distinguish intent:
   >
   > ```text
   > show naks      # make visible using the target's normal/default transition
   > reveal naks    # perform a more deliberate visual reveal, e.g. rollout/draw where available
   > ```
   >
   > This gives more semantic richness but creates another authoring distinction to remember. Decision: keep aliases for now.

4. Should `cut` be a separate command or just `camera <preset> over 0` sugar?

   > Sugar is better. Your call on how to handle this
   >
   > **State: accepted.** Treat `cut <preset>` as sugar for `camera <preset> over 0`. Keep `camera <preset> over 0` as canonical.

5. Which group target expansions should be canonical for `sky`, `guides`, `poles`, and `seasons`?

   > guides should be the equator, ecliptic, and NS axis. I am not sure about the others.
   >
   > **State: partially accepted.** Define `guides` as equator, ecliptic, and nsAxis. Leave `sky`, `poles`, and `seasons` undecided until target hierarchy is finalized.

6. Should vector variables be allowed before target hierarchy is fully implemented?
   > Not yet. Camera positions can be set as presets, and we can have aliases that point to camera positions.
   >
   > **State: accepted.** Do not add vector variables yet. Use camera presets and aliases for camera positions.
