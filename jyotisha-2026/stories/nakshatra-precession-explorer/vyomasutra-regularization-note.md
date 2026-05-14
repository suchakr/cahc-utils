# VyomaSutra Regularization Note

Review artifact. This is the working design note for grammar cleanup before updating the PRD, skill, compiler, or renderer.

## Intent

Make VyomaSutra predictable for authors:

- A bare target name should normally mean one named visual thing.
- A grouped target should be visibly marked with `@`.
- Historical bare group names remain compatibility aliases.
- Every target-taking command should accept one target, one group, or a comma-separated target/group list.
- Styling should use one regular property model for labels, lines, dots, and fills.
- `show ... <style-props>` should be valid sugar for style-and-show at the same scheduled time.
- Existing scripts may break where the old behavior was misleading, but compatibility aliases should preserve reasonable old forms.

## Review Decisions So Far

- `@group` is the canonical group spelling.
- Bare group names such as `naks`, `polarItems`, `seasonalFrame`, and `eclipticNakSegments` remain accepted as legacy aliases.
- No sigil means “one named thing,” except for historical baggage kept for compatibility.
- `*naks` means nakshatra stars/dots.
- `$naks` means nakshatra stick/line figures.
- `@naks` means the whole grouped nakshatra layer: stars + lines + labels.
- `naks` remains accepted as a legacy alias and lowers exactly to `@naks`.
- Authored labels should be first-class style targets if implementation is straightforward.
- Unsupported style props should warn once per source line.
- Authoring UX should eventually include line numbers and enough editor width to make line-numbered warnings actionable.

## Full Proposed Grammar

This grammar is intentionally complete enough for review. Semantic tables still decide whether a target supports a visual part or style property.

```ebnf
program             ::= line*
line                ::= ws* statement-list? comment? newline
statement-list      ::= statement (statement-separator statement)*
statement-separator ::= ";"

comment             ::= "#" text
                      ; except #RGB and #RRGGBB are color tokens inside statements

statement           ::= timed-block
                      | timed-command
                      | command

timed-block         ::= timing "{" block-body "}"
block-body          ::= statement-list?
timed-command       ::= timing command
timing              ::= "at" time
                      | "after" duration
                      | signed-duration

command             ::= stage-stmt
                      | show-stmt
                      | hide-stmt
                      | flash-stmt
                      | style-stmt
                      | camera-stmt
                      | travel-stmt
                      | grid-stmt
                      | caption-stmt
                      | label-stmt
                      | clear-stmt
                      | wait-stmt
                      | seq-stmt
                      | fullscreen-stmt
                      | defaults-stmt
                      | effects-stmt

stage-stmt          ::= ("stage" | "scene") stage-arg*
stage-arg           ::= "blank"
                      | "all"
                      | light
                      | ("year" | "epoch") number
light               ::= "night" | "twilight" | "day"

show-stmt           ::= ("show" | "reveal" | "rollout" | "fade") target-list show-arg*
hide-stmt           ::= "hide" target-list transition-arg*
show-arg            ::= transition-arg | style-prop | compact-style

flash-stmt          ::= ("flash" | "pulse") target-list effect-arg*
style-stmt          ::= "style" target-list (style-prop | compact-style)+

camera-stmt         ::= ("camera" | "move" | "cut") camera-arg*
travel-stmt         ::= ("travel" | "epochTravel") ("year" | "epoch")? number "to" number travel-arg*
grid-stmt           ::= "grid" grid-kind number color?
caption-stmt        ::= ("caption" | "say" | "title") quoted-text caption-arg*
label-stmt          ::= "label" identifier quoted-text label-arg*
clear-stmt          ::= "clear" ("label" identifier | identifier | "labels")
wait-stmt           ::= "wait" duration
seq-stmt            ::= ("seq" | "sequence") duration
fullscreen-stmt     ::= "fullscreen" | "theater" | "exitFullscreen" | "canvas"
defaults-stmt       ::= "defaults" default-arg+
effects-stmt        ::= "effects" effect-default-arg+
```

## Targets

```ebnf
target-list         ::= target (target-separator target)*
target-separator    ::= "," | "and"

target              ::= sigiled-target | bare-target
sigiled-target      ::= "@" identifier | "*" identifier | "$" identifier
bare-target         ::= identifier
```

Clarification: `@identifier` is always a group-target form. There is no conflict with `part-group-target`; `*` and `$` are the part-group sigils, while `@` means “whole group.” `@naks` is therefore the whole nakshatra group, not a third independent part.

Bare targets are resolved by registry, not by grammar:

```text
1. built-in leaf target
2. legacy bare group alias
3. authored label id
```

This intentionally collapses `leaf-target`, `legacy-target`, and `authored-label-target` into one syntactic form. Their distinction is semantic.

Target examples:

```text
NP                   leaf target
VE                   leaf target
precessionCircle     leaf line target
@poleTrack           group containing precessionCircle, pole-track arc/label, NP, and SP
@seasonalFrame       group target
@polarItems          group target
@naks                whole grouped nakshatra layer
*naks                nakshatra stars/dots
$naks                nakshatra lines/stick figures
```

Compatibility aliases:

```text
naks                 legacy alias for @naks
polarItems           legacy alias for @polarItems
seasonalFrame        legacy alias for @seasonalFrame
eclipticNakSegments  legacy alias for @eclipticNakSegments
```

Target-list rule: all target-taking commands use `target-list`. Bare-space target lists are not accepted because they collide with command options and style props.

```vysu
show NP, SP, VE
hide *naks, $naks
flash thuban, polaris
style NP, precessionCircle labelSize 8 labelAlpha 80%
show @seasonalFrame
show @polarItems
```

## Command Options

The previous placeholders `show-options`, `transition-options`, and `effect-options` mean the following:

```ebnf
transition-arg      ::= mode
                      | order
                      | direction
                      | duration-arg
                      | ease-arg

effect-arg          ::= duration-arg
                      | repeat-arg
                      | "gap" duration
                      | style-prop
                      | compact-style

caption-arg         ::= duration-arg
                      | color
                      | alpha
                      | size-arg
                      | screen-location
                      | fade-arg

label-arg           ::= label-anchor
                      | delta-arg
                      | "class" identifier
                      | style-prop
                      | compact-style

camera-arg          ::= "pos" vec3
                      | "position" vec3
                      | "target" vec3
                      | "fov" number
                      | duration-arg
                      | camera-preset

travel-arg          ::= duration-arg
                      | "step" number
                      | "rate" travel-rate
                      | ease-arg

default-arg         ::= "tempo" speed
                      | "effects" speed
                      | "travel" travel-rate

effect-default-arg  ::= speed

duration-arg        ::= "over" duration
                      | legacy-duration-tuple
                      | bare-duration

mode                ::= "instant" | "fade" | "stagger" | "rollout"
order               ::= "default" | "ecliptic" | "reverse-ecliptic" | "north-to-south" | "south-to-north"
direction           ::= "forward" | "reverse"
ease-arg            ::= "ease" identifier
repeat-arg          ::= number "x"
grid-kind           ::= "ecliptic" | "ecl" | "equatorial" | "equator" | "eq"
camera-preset       ::= identifier
travel-rate         ::= number "y/s" | "slow" | "normal" | "fast"
speed               ::= number "x" | "slow" | "normal" | "fast"
```

Canonical duration spelling is `over <duration>`:

```vysu
show NP over 900
show NP over 900:
```

`over 900` and `over 900:` are identical. A bare number in transition/effect position remains a legacy implied duration for backward compatibility:

```vysu
show NP 900
```

That form is accepted but discouraged, especially once inline style props are present. In compact style calls, a bare number always means size/width:

```vysu
show NP lbl(gold 1.2 80%)
```

Here `1.2` is label size and `80%` is label alpha.

`show-arg` intentionally includes both transition args and style props. That enables:

```vysu
show NP rollout over 900 lbl(gold 1.2 80%) dot(ring red 2)
```

Conceptual lowering:

```vysu
style NP lbl(gold 1.2 80%) dot(ring red 2)
show NP rollout over 900
```

at the same scheduled time.

## Visual Parts

Every visual target may expose these parts:

```text
label
line
dot
fill
```

Not every target has every part. Unsupported target/part combinations warn.

Group styling applies to each leaf target in the group:

```vysu
style @polarItems labelAlpha 70%
style @naks labelSize 5 lineAlpha 60% dotSize 2
```

Canonical groups identified by audit:

| Canonical group | Legacy bare alias | Expansion intent |
| --- | --- | --- |
| `@naks` | `naks` | `nakshatraStars` + `nakshatraLines` + `nakshatraLabels` |
| `@polarItems` | `polarItems` | `@northPolarItems` + `@southPolarItems`; fixed/cultural polar items, not moving pole markers |
| `@northPolarItems` | `northPolarItems`, `northPolar` | `sisumara` + `matsya` + `thuban` + `polaris` |
| `@southPolarItems` | `southPolarItems`, `southPolar` | `agastya` and any future south-polar fixed/cultural items |
| `@seasonalFrame` | `seasonalFrame` | `equator` + `VE` + `SS` + `AE` + `WS`; no `NP`/`SP` |
| `@poleTrack` | `poleTrack` | `precessionCircle` + pole-track arc + pole-track label + `NP` + `SP` |
| `@eclipticNakSegments` | `eclipticNakSegments` | `eclipticBand` + `eclipticDividers` + `eclipticLabels` + `eclipticPoles` |
| `@referencePlanes` | `referencePlanes` | `eclipticPlane` + `equatorialPlane` |
| `@eclipticGrid` | `eclipticGrid` | Ecliptic grid parallels + meridians |
| `@equatorialGrid` | `equatorialGrid` | Equatorial grid parallels + meridians |
| `@eclipticPoles` | `eclipticPoles` | `NEP` + `SEP` dots/labels |

`NP` and `SP` are moving pole markers. They are not members of `@seasonalFrame` and not members of `@polarItems`.

`precessionCircle` remains a leaf line target. `@poleTrack` is the group that contains `precessionCircle` and related pole-track visuals.

Draft target registry:

| Canonical form | Kind | Expansion / leaf meaning | Aliases / compatibility |
| --- | --- | --- | --- |
| `NP` | leaf | North moving pole dot/label | `np` |
| `SP` | leaf | South moving pole dot/label | `sp` |
| `NEP` | leaf | North ecliptic pole dot/label | `nep` |
| `SEP` | leaf | South ecliptic pole dot/label | `sep` |
| `VE` | leaf | Vernal equinox marker/label | `ve` |
| `SS` | leaf | Summer solstice marker/label | `ss` |
| `AE` | leaf | Autumnal equinox marker/label | `ae` |
| `WS` | leaf | Winter solstice marker/label | `ws` |
| `equator` | leaf | Seasonal/celestial equator line | none |
| `nsAxis` | leaf | North-south axis line | `axis`, `nsaxis` |
| `precessionCircle` | leaf | Precession circle line | `precession` |
| `eclipticBand` | leaf | Ecliptic band fill/circle | `ecliptic.band` planned |
| `eclipticDividers` | leaf | Ecliptic sector divider lines | `sectorDividers`, `ecliptic.dividers` planned |
| `eclipticLabels` | leaf | Ecliptic sector labels | `sectorLabels`, `ecliptic.labels` planned |
| `eclipticPlane` | leaf | Ecliptic reference plane | none |
| `equatorialPlane` | leaf | Equatorial reference plane | none |
| `stars` | leaf/group-like | Background star field, including non-nakshatra stars | none |
| `nakshatraStars` | leaf/group-like | Nakshatra star/dot groups only | `nakStars`, `naksStars`, `*naks` |
| `nakshatraLines` | leaf/group-like | Nakshatra stick figures only | `$naks` |
| `nakshatraLabels` | leaf/group-like | Nakshatra labels only | `naksLabels`, `nakshatraLabels` |
| `agastya` | leaf | Agastya / Canopus special star item | `canopus` |
| `thuban` | leaf | Thuban special star item | `abhayaDhruva` |
| `polaris` | leaf | Polaris special star item | `matsyaDhruva` |
| `matsya` | leaf | Matsya polar figure/item | none |
| `sisumara` | leaf | Sisumara polar figure/item | `shishumara`, `shimshumara` |
| `overlay` | leaf | Screen overlay/epoch caption layer | none |
| authored label id | leaf | User-created overlay label | declared by `label <id> ...` |
| `@naks` | group | Nakshatra stars + lines + labels | `naks`, `nak`, `nakshatra`, `nakshatras` |
| `@polarItems` | group | North + south fixed/cultural polar items | `polarItems` |
| `@northPolarItems` | group | North fixed/cultural polar items | `northPolarItems`, `northPolar` |
| `@southPolarItems` | group | South fixed/cultural polar items | `southPolarItems`, `southPolar` |
| `@seasonalFrame` | group | Equator + equinox/solstice markers | `seasonalFrame`, `seasons`, `rtu`, `rtus` |
| `@poleTrack` | group | Precession track visuals + `NP`/`SP` | `poleTrack`, `polePath` |
| `@eclipticNakSegments` | group | Ecliptic sector band/dividers/labels/poles | `eclipticNakSegments`, `nakSegments`, `naksSegments`, `eclipticSegments` |
| `@referencePlanes` | group | Ecliptic + equatorial planes | `referencePlanes`, `refs` |
| `@eclipticGrid` | group | Ecliptic grid parallels/meridians | `eclipticGrid`, `eclGrid`, `eclGridWire` |
| `@equatorialGrid` | group | Equatorial grid parallels/meridians | `equatorialGrid`, `equatorGrid`, `eqGrid`, `eq` |
| `@eclipticPoles` | group | `NEP` + `SEP` | `eclipticPoles` |

## Verbose Style Grammar

```ebnf
style-prop          ::= label-prop
                      | line-prop
                      | dot-prop
                      | fill-prop
                      | sugar-prop

label-prop          ::= ("labelColor" | "lblColor") color
                      | ("labelSize"  | "lblSize") number
                      | ("labelAlpha" | "lblAlpha") alpha

line-prop           ::= "lineColor" color
                      | "lineWidth" number
                      | "lineAlpha" alpha
                      | "lineStyle" line-style

dot-prop            ::= "dotColor" color
                      | "dotSize" number
                      | "dotAlpha" alpha
                      | "dotShape" dot-shape

fill-prop           ::= "fillColor" color
                      | "fillAlpha" alpha

sugar-prop          ::= "color" color
                      | "alpha" alpha
                      | "size" number
                      | "fontSize" number
                      | "font" number
```

Sugar-prop rule:

- `labelColor`, `lineColor`, `dotColor`, etc. are precise and preferred.
- Bare `color`, `alpha`, `size`, `font`, and `fontSize` are target-default sugar.
- Every target registry entry should define default part routing for `color`, `alpha`, and `size`.
- If a specific part is styled, unspecified values on that part remain at their current value or default.
- If a target cannot support a requested part, the compiler should warn.

Examples:

```vysu
style NP labelColor gold labelSize 1.2 labelAlpha 80% dotColor red dotSize 2
style precessionCircle lineColor yellow lineWidth 4 lineAlpha 60% labelAlpha 70%
style @naks dotSize 2 lineAlpha 60% labelSize 5
```

## Compact Style Sugar

```ebnf
compact-style       ::= part-call+
part-call           ::= part-name "(" part-token* ")"
part-name           ::= "label" | "lbl" | "line" | "ln" | "dot" | "point" | "fill"
part-token          ::= color | number | alpha | dot-shape | line-style

dot-shape           ::= "circle" | "ring" | "square" | "diamond" | "cross"
line-style          ::= "solid" | "dashed" | "dotted" | "dashdot" | "-" | "--" | ".." | "-."
```

Inference inside `part(...)`:

```text
COLOR_NAME/#hex      color
NUMBER%              alpha
bare number          size or width
circle/ring/...      dot shape
solid/dashed/...     line style
```

Alpha uses trailing percent only:

```text
60%  valid alpha
.6   size, not alpha
%60  not canonical
```

Duplicate properties: last wins. Bad tokens: warn once per source line.

Examples:

```vysu
style NP lbl(gold .8 80%) dot(circle red 2 60%)
style precessionCircle line(dashed yellow 5.5 40%) lbl(gold 7 80%)
show NP lbl(gold 1.2 80%) dot(ring red 2)
```

## Authored Labels

Authored labels accept the same label style props:

```vysu
label msg "Hello" at target NP labelColor gold labelSize 1.2 labelAlpha 80%
label msg "Hello" at target NP lbl(gold 1.2 80%)
```

Authored label ids should be first-class style targets if feasible:

```vysu
style msg labelColor gold labelSize 1.2
hide msg
clear msg
```

Collision rule:

```text
built-in target names win first
authored label ids resolve next
```

`labelColor` should apply both to built-in text sprites and authored overlay labels. The target registry determines which visual part receives it. Examples:

```vysu
style NP labelColor gold              # built-in NP label
style msg labelColor gold             # authored overlay label id
label msg "Hello" at target NP labelColor gold
```

## Timing Grammar

```ebnf
time                 ::= duration
signed-duration      ::= ("+" | "-") duration
duration             ::= number | number "ms" | number "s"
bare-duration        ::= duration
legacy-duration-tuple ::= number ":" number? ":" number?
```

`900` and `900:` are equivalent duration values when parsed in a duration position. `900:` is retained for compatibility with existing duration-tuple sugar.

Timing semantics:

- Top-level starts at `0`.
- Each timed block has a local cursor at its block base.
- `at N` is absolute within the current scope and does not move the cursor.
- `after N` and `+N` advance the current cursor by `N`.
- `wait N` advances the current cursor by `N` and emits nothing.
- `seq N` at top-level sets the default sequence step for future timed blocks.
- `seq N` inside a block advances the block clock by `N` before each following emitted command.
- Top-level relative blocks advance from the previous block's scheduled end.

## Value Grammar

```ebnf
screen-location      ::= ("at" "screen" | "screen") screen-anchor delta-arg*
label-anchor         ::= ("at" "screen" screen-anchor | "screen" screen-anchor)
                      | ("at" "target" target)
target-follow        ::= "at" "target" target delta-arg*
screen-anchor        ::= number | "N" | "NE" | "E" | "SE" | "S" | "SW" | "W" | "NW" | "C"
delta-arg            ::= "dx" signed-number | "dy" signed-number | signed-vec2

fade-arg             ::= "fade" duration (":" duration)?
                      | "fadeIn" duration
                      | "fadeOut" duration
size-arg             ::= "size" number | "font" number | "fontSize" number | number "px"

alpha                ::= number "%"
color                ::= color-name | hex-color
hex-color            ::= "#" hex hex hex (hex hex hex)?
vec3                 ::= number "," number "," number
signed-vec2          ::= signed-number "," signed-number
number               ::= signed decimal number
signed-number        ::= ("+" | "-")? decimal number
identifier           ::= letter (letter | digit | "_" | "-")*
quoted-text          ::= '"' text '"'
ws                   ::= spaces or tabs
newline              ::= "\n" | "\r\n"
```

Disambiguation rules:

```text
1. The grammar parses only sigiled-target and bare-target. Registry lookup resolves target kind.
2. Reserved command/property keywords win in syntactic positions. For example, `at target NP` treats `target` as a keyword, not as a target id.
3. Canonical duration in target commands is `over <duration>`.
4. Bare numeric duration remains accepted in legacy transition/effect positions, but is discouraged.
5. In compact style calls, bare numbers are size/width; trailing percent is alpha.
6. `color`/`alpha`/`size` sugar uses the target registry default part for that target.
```

## Examples

```vysu
show @seasonalFrame
show NP lbl(gold 1.1 90%) dot(ring red 2)
show VE, SS, AE, WS lbl(cyan 7 70%) dot(diamond cyan 1.8)

show *naks dotSize 2 dotAlpha 80%
show $naks lineColor #8eaccb lineAlpha 70%
show @naks lbl(#ccd6f6 5 70%) line(#8eaccb 1.5 60%) dot(white 1.8 80%)

style precessionCircle line(dashed yellow 4 60%) lbl(gold 6 70%)
style @polarItems lbl(gold 5 80%) line(#6f86a1 1.2 55%) dot(circle #9ecbff 2 70%)

label msg "Hello" at target NP lbl(gold 1.2 80%) dx 12 dy -8
style msg lbl(cyan 1.1 60%)
```

## Implementation Plan

1. Add a target registry.
   - Record canonical name, kind (`leaf`/`group`), parts, aliases, expansion, and default part for sugar props.
   - Keep legacy names as aliases.

2. Normalize target parsing.
   - `@group` resolves through group expansion.
   - `target-list` is used by all target-taking directives.
   - Existing bare group names continue to work as compatibility aliases.

3. Add style property parser.
   - Support verbose props.
   - Support compact `lbl(...)`, `line(...)`, `dot(...)`, `fill(...)`.
   - Warn on bad or unsupported tokens once per line.

4. Add style state.
   - Store per-target/part overrides.
   - Preserve existing global settings as defaults.

5. Update renderers.
   - Resolve effective style as `global defaults + group/target overrides`.
   - Apply label/line/dot/fill style independently.

6. Add inline style support to `show`.
   - Compile `show target style-props` into style patch plus reveal cue at the same time.

7. Make authored label ids first-class targets if feasible.
   - Keep `clear label id` and `clear labels`.
   - Allow `style id ...`, `hide id`, and possibly `show id`.

8. Improve warnings and authoring UX.
   - One warning per line.
   - Add line numbers or equivalent warning navigation.
   - Consider draggable canvas/dock divider so the editor can widen.

9. Update canonical docs after review.
   - Condense this note into `vyoma-sutra-prd.md`.
   - Update `SKILL.md` with author-facing grammar and examples.
   - Update explorer help grammar only after implementation.

## Decisions And Remaining Questions

Decisions from review:

- `naks` remains accepted as historical baggage. Canonical docs should prefer `@naks`.
- `naks` lowers exactly to `@naks`: stars + lines + labels.
- `@naks` includes labels by default for regularity.
- `labelColor` applies to both built-in text sprites and authored overlay labels; registry resolution decides the target.
- Unsupported style props warn visibly, once per source line.
- Part shorthand such as `lbl(...)`, `line(...)`, and `dot(...)` is desirable if fully specified.
- Bare numeric duration remains accepted as legacy implied duration, but is discouraged. Canonical examples should use `over`.
- Every target defines default routing for `color`, `alpha`, and `size` sugar; this is a registry requirement, not an open grammar question.

Remaining questions:

- What is the full registry table for each target's default style-part routing?

# Previous Peer Review

Status: retained for provenance. The current proposal above supersedes this review where it differs. In particular, `naks == @naks`, `@naks` includes labels, `precessionCircle` is a leaf, `@poleTrack` contains `NP`/`SP`, and bare numeric duration remains accepted only as discouraged legacy duration syntax.

The active remaining question is no longer grammar ambiguity. It is the implementation registry for default style-part routing.

Prompt:
"Is the proposed full grammar unambigous. Can you list the targets and their aliases"

---

## Ambiguity Analysis

### Grammar is **mostly unambiguous**, but has **three real ambiguity holes**:

#### 1. `leaf-target` vs `legacy-target` vs `authored-label-target` are indistinguishable (critical)

```ebnf
target  ::= leaf-target           ← identifier
          | group-target          ← "@" identifier  ✓ distinct
          | part-group-target     ← "*"/"$" identifier  ✓ distinct
          | legacy-target         ← identifier  ⚡ SAME as leaf-target
          | authored-label-target ← identifier  ⚡ SAME as leaf-target
```

All three — `leaf-target`, `legacy-target`, and `authored-label-target` — parse as a bare `identifier`. The grammar cannot distinguish them syntactically; they are resolved only by a **runtime registry lookup**. This is not an EBNF ambiguity in the classical sense, but the grammar rule is misleading: three alternatives reduce to the same token. It should be collapsed into one rule with a note that the target registry resolves the kind.

#### 2. `command` vs `identifier` collision in `target-list` positions

`camera-preset ::= identifier` and `camera-arg ::= "target" vec3` — the keyword `target` inside `label-anchor` could collide with a target identifier named `target`. The collision rule ("built-in target names win first") resolves this, but it is implicit in the prose, not in the grammar.

#### 3. `bare-duration` inside `show-arg` vs `style-prop` number

In:

```vysu
show NP 900 lbl(gold 1.2 80%)
```

A bare number `900` is ambiguous: is it `bare-duration` or `size` (a sugar-prop)? The grammar's `show-arg` includes both `transition-arg` (which includes `bare-duration`) and `style-prop` (which includes `size number`). Needs a resolution rule (e.g., "bare number at the start of show-args is duration").

---

## Targets & Aliases Table

| Canonical Form          | Kind           | Sigil        | Expansion / Meaning                            | Aliases                              |
| ----------------------- | -------------- | ------------ | ---------------------------------------------- | ------------------------------------ |
| `NP`                    | leaf           | (bare)       | North Pole visual                              | —                                    |
| `SP`                    | leaf           | (bare)       | South Pole visual                              | —                                    |
| `VE`                    | leaf           | (bare)       | Vernal Equinox                                 | —                                    |
| `SS`                    | leaf           | (bare)       | Summer Solstice                                | —                                    |
| `AE`                    | leaf           | (bare)       | Autumnal Equinox                               | —                                    |
| `WS`                    | leaf           | (bare)       | Winter Solstice                                | —                                    |
| `thuban`                | leaf           | (bare)       | Star target                                    | —                                    |
| `polaris`               | leaf           | (bare)       | Star target                                    | —                                    |
| `precessionCircle`      | leaf or group† | (bare) / `@` | Precession circle visual                       | —                                    |
| `@naks`                 | group          | `@`          | Whole nakshatra layer (stars + lines + labels) | `naks` (legacy, expansion TBD)       |
| `*naks`                 | part-group     | `*`          | Nakshatra stars/dots only                      | —                                    |
| `$naks`                 | part-group     | `$`          | Nakshatra stick/line figures only              | —                                    |
| `@seasonalFrame`        | group          | `@`          | Seasonal frame layer                           | `seasonalFrame` (legacy alias)       |
| `@polarItems`           | group          | `@`          | Polar items layer                              | `polarItems` (legacy alias)          |
| `@eclipticNakSegments`  | group          | `@`          | Ecliptic nakshatra segment layer               | `eclipticNakSegments` (legacy alias) |
| `msg` (any authored id) | authored label | (bare)       | Overlay label positioned at a target           | —                                    |

† `precessionCircle` is a **candidate** group (Open Question #3) — not yet formally decided.

---

## Summary of Open Questions Affecting Ambiguity

| Question                                                          | Impact                                           |
| ----------------------------------------------------------------- | ------------------------------------------------ |
| Does `naks` lower to `@naks` or keep historical "lines + labels"? | Affects whether the legacy alias is safe to keep |
| Does `@naks` include labels?                                      | Affects group expansion semantics                |
| Which bare names are formally groups?                             | Determines when `@` is required vs optional      |
| Which targets have a safe default part for bare `color`/`size`?   | Affects sugar-prop resolution                    |

The grammar is **structurally sound** but needs the three prose rules (target-kind resolution, `target` keyword priority, bare-number-in-show-args precedence) made explicit — either as grammar annotations or as a companion disambiguation table in the PRD.
