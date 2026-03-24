# `stelplay` PRD + Design

## Status

Draft for review.

## Summary

`stelplay` is a small repo-local CLI for launching Stellarium presentation scripts from this repository using short `sXX` references such as `s11`, `s14`, or `s25`.

It has two execution modes:

- plain playback, which launches the original `.ssc` unchanged
- managed playback, which uses a temporary wrapper to force clean exit after the script completes

Managed playback is used for `--exit` and `--record`. Recording writes high-resolution MP4 output to `./out/work-videos/hires/` by default.

## Motivation

The current direct invocation is correct but verbose:

```bash
/Applications/Stellarium.app/Contents/MacOS/stellarium \
  --startup-script="$PWD/ssc/s25-eqfm-search-visualizer.ssc"
```

The goals of `stelplay` are:

- shorten the command used for rehearsal and demo preparation
- standardize the mapping from `sXX` shorthand to actual `.ssc` filenames
- provide a reliable recording workflow for finite video export
- avoid modifying the original presentation scripts just to support recording

## Users

Primary user:

- the repo author, invoking `./ops/stelplay` from this presentation directory

Expected working directory:

- `/Users/sunder/projects/cahc/cahc-utils/presentations/2026-03-23-iks-astro-talk`

This tool is intentionally scoped to the current repo. It does not attempt cross-repo discovery.

## Product Decisions

- Tool name: `stelplay`
- Invocation style: `./ops/stelplay ...`
- Script scope: only scripts under `./ssc/`
- Script reference style: short `sXX` handles
- Plain playback: no wrapper, no auto-exit
- `--exit`: wrap the target script by copying its contents into a temporary `.ssc` and appending `core.quitStellarium()`
- `--record`: record the run to MP4 and imply `--exit`
- Default recording location: `./out/work-videos/hires/`
- Recording start sync: `stelplay` starts `ffmpeg` 10 seconds after Stellarium launch, and the wrapper waits 10 seconds before beginning scripted content
- Recording tail trim: trim the last 0.75 seconds from the saved MP4 using a fast post-pass
- Recording debug artifacts: retain `<name>.pretrim.mp4` and `<name>.posttrim.mp4` alongside the canonical output
- Existing output files: overwrite
- `--help`: supported and expected

## Goals

- `./ops/stelplay s25` should be the convenient shorthand for launching the corresponding script under `./ssc/`
- all current presentation scripts with `sXX` prefixes should be supported
- Recording should produce a finished MP4 without requiring manual cleanup when the show ends
- The original `.ssc` files should remain unchanged
- Error messages should be concise and actionable

## Non-Goals

- arbitrary script lookup outside `./ssc/`
- playlists or multi-script orchestration
- generalized macOS screen-recording automation beyond this repo's immediate need
- sophisticated window management or presenter-mode choreography
- making plain playback finite by default

## Primary Use Cases

### 1. Plain playback

Use when the user wants a short command that behaves like direct Stellarium launch.

Example:

```bash
./ops/stelplay s25
```

Expected behavior:

- resolve `s25` to `./ssc/s25-eqfm-search-visualizer.ssc`
- launch Stellarium with that script
- preserve the script's own lifecycle
- if the script does not terminate Stellarium, Stellarium remains open

### 2. Managed playback with auto-exit

Use when the user wants the same script to close Stellarium when the presentation run finishes.

Example:

```bash
./ops/stelplay s25 --exit
```

Expected behavior:

- resolve the target script as usual
- create a temporary wrapper `.ssc`
- wrapper copies the original script contents
- wrapper appends `core.quitStellarium()`
- Stellarium is launched with the wrapper, not the original
- original `.ssc` remains untouched

### 3. Recording a finite show

Use when the user wants a video artifact from the run.

Example:

```bash
./ops/stelplay s25 --record
```

Expected behavior:

- resolve `s25`
- derive output path `./out/work-videos/hires/s25.mp4`
- launch Stellarium with a temporary wrapper
- wait 10 seconds after Stellarium launch
- start `ffmpeg`
- let the wrapper wait 10 seconds, then begin the actual scripted content
- wait for Stellarium to exit
- stop `ffmpeg` gracefully so the MP4 finalizes correctly
- retain the raw captured file as `s25.pretrim.mp4`
- trim the last 0.75 seconds from the saved MP4 using a fast post-record pass
- retain the trimmed artifact as `s25.posttrim.mp4`
- copy the trimmed artifact to the canonical output path `./out/work-videos/hires/s25.mp4`
- overwrite any existing `./out/work-videos/hires/s25.mp4`

## CLI Contract

### Command Shape

```text
./ops/stelplay <script-ref> [--exit] [--record[=NAME_OR_PATH]]
./ops/stelplay --help
```

### Script Resolution

`<script-ref>` is intended to be an `sXX` shorthand that resolves to a unique file in `./ssc/`.

Examples:

- `s11` -> `s11-dhruva-pole-drift.ssc`
- `s12` -> `s12-sun-swing.ssc`
- `s13` -> `s13-sun-meridian-high-low.ssc`
- `s14` -> `s14-nakshatra-tour.ssc`
- `s21` -> `s21-moon-swing.ssc`
- `s22` -> `s22-bp-eqfm-best-case.ssc`
- `s23` -> `s23-total-eclipse-india.ssc`
- `s24` -> `s24-pt-eclipse-jaipur.ssc`
- `s25` -> `s25-eqfm-search-visualizer.ssc`

Resolution rule:

- match files under `./ssc/` whose basename begins with the provided reference
- require exactly one match
- fail if there are zero matches
- fail if there are multiple matches

### Option Semantics

### `--exit`

Use managed playback.

Behavior:

- create a temporary wrapper
- wrapper copies the original script contents
- wrapper calls `core.quitStellarium()` at the end

### `--record`

Record the run to MP4 and imply `--exit`.

Behavior:

- launch Stellarium first
- wait 10 seconds
- start recording
- let the wrapper wait 10 seconds, then begin scripted content
- use managed playback so the run is finite
- stop recording after Stellarium exits
- retain a `.pretrim.mp4` debug artifact
- trim the last 0.75 seconds from the saved MP4 using a fast post-record pass
- retain a `.posttrim.mp4` debug artifact
- copy the trimmed result to the requested output path

### `--record=VALUE`

Allow the user to override the recording target.

Interpretation:

- if `VALUE` contains `/` or ends with `.mp4`, treat it as a path and write to that path
- otherwise, treat `VALUE` as a simple recording name and write `./out/work-videos/hires/VALUE.mp4`

Examples:

```bash
./ops/stelplay s25 --record
./ops/stelplay s25 --record=s25
./ops/stelplay s25 --record=eqfm-demo
./ops/stelplay s25 --record=out/takes/eqfm-take-2.mp4
```

## Detailed UX

### Baseline Equivalence

This command:

```bash
./ops/stelplay s25
```

should effectively mean:

```bash
/Applications/Stellarium.app/Contents/MacOS/stellarium \
  --startup-script="$PWD/ssc/s25-eqfm-search-visualizer.ssc"
```

The point of `stelplay` is to preserve that baseline behavior while making it shorter and more uniform.

### Help Output

`--help` should be implemented and should explain:

- usage
- the meaning of `sXX` shorthand
- the distinction between plain playback and managed playback
- the fact that `--record` implies `--exit`
- default recording location and overwrite behavior
- the behavior when no script reference is supplied

Proposed help text:

```text
Usage:
  ./ops/stelplay <script-ref> [--exit] [--record[=NAME_OR_PATH]]
  ./ops/stelplay --help

Description:
  Play a Stellarium .ssc script from ./ssc using a short sXX reference.
  Plain playback launches the original script unchanged.
  Managed playback uses a temporary wrapper to exit Stellarium after the script completes.

No script ref:
  Print usage and list available sXX scripts under ./ssc.

Arguments:
  <script-ref>              Short script reference such as s11, s14, or s25

Options:
  --exit                    Auto-exit Stellarium after the script completes
  --record                  Record to ./out/work-videos/hires/<script-ref>.mp4 and imply --exit
  --record=VALUE            Record to ./out/work-videos/hires/VALUE.mp4, or to VALUE if VALUE looks like a path
  --help                    Show this help message

Examples:
  ./ops/stelplay s11
  ./ops/stelplay s14 --exit
  ./ops/stelplay s23 --record
  ./ops/stelplay s25 --record=eqfm-demo
  ./ops/stelplay s25 --record=out/takes/eqfm-take-2.mp4
```

## Design

### Architecture

The design intentionally separates two execution paths.

### A. Plain Playback Path

Used when the user does not request `--exit` or `--record`.

Characteristics:

- direct launch
- no wrapper
- no interference with original script lifecycle
- simplest path and easiest to trust

### B. Managed Playback Path

Used when the user requests `--exit` or `--record`.

Characteristics:

- create a temporary wrapper script
- wrapper copies the original target script contents
- wrapper appends `core.quitStellarium()`
- launch Stellarium with the wrapper

This keeps lifecycle policy outside the original `.ssc` files while still allowing finite automated runs.

### Recording Model

Recording mode adds screen capture around managed playback.

Expected sequence:

1. resolve the target `.ssc`
2. determine the recording output path
3. create the wrapper script
4. launch Stellarium with the wrapper script
5. wait 10 seconds after Stellarium launch
6. start `ffmpeg` screen recording
7. let the wrapper wait 10 seconds, then begin scripted playback
8. wait for Stellarium to exit
9. send graceful stop to `ffmpeg`
10. keep the raw capture as `<name>.pretrim.mp4`
11. trim the last 0.75 seconds from the raw capture into `<name>.posttrim.mp4` using a fast post-pass
12. copy `<name>.posttrim.mp4` to the canonical output path
13. clean up temporary files

### Logging and Console Noise

Recording mode should keep launcher and child-process terminal output quiet where practical, but this should not be treated as a guarantee that the terminal will be absent from the captured video.

Rationale:

- terminal chatter is distracting during recording
- users may accidentally leave the terminal visible on the recorded display

Practical v1 approach:

- redirect `stelplay` and Stellarium stdout/stderr away from the interactive terminal during recording runs
- keep the terminal visually off the captured display before capture starts

Important limitation:

- quiet logging reduces terminal churn
- it does not solve the separate problem of whether the terminal window itself is visible on the recorded screen

This PRD does not require sophisticated window automation. For v1, a process-level workaround is sufficient:

- make recording runs quiet
- rely on the user to keep the terminal out of the captured area

### Dependencies

Assumed external tools for v1:

- Stellarium binary at `/Applications/Stellarium.app/Contents/MacOS/stellarium`
- `ffmpeg` available on the system path
- `ffprobe` available on the system path for post-record trimming

Recording device selection can use a fixed default in v1, with room for later override if needed.

### Error Handling

The tool should fail clearly in these cases:

- script reference not provided
- `./ssc/` directory missing
- no matching script found
- multiple matching scripts found
- Stellarium binary missing
- `ffmpeg` missing when `--record` is requested
- `ffprobe` missing when `--record` is requested
- recording output path is invalid or unwritable

Suggested error style:

- short
- specific
- with immediate next-step guidance when possible

Examples:

- `No script matched 's26' under ./ssc`
- `Multiple scripts matched 's2': s21-..., s22-..., s23-..., s24-..., s25-...`
- `ffmpeg not found; recording requires ffmpeg on PATH`
- `ffprobe not found; recording trim requires ffprobe on PATH`

## Success Criteria

- `./ops/stelplay s25` launches the correct script with no wrapper behavior
- `./ops/stelplay s25 --exit` exits when the show completes
- `./ops/stelplay s25 --record` produces `./out/work-videos/hires/s25.mp4`
- `./ops/stelplay s25 --record` starts recording 10 seconds after launch, delays scripted content by 10 seconds, and trims the last 0.75 seconds of tail material
- `./ops/stelplay s25 --record` retains `./out/work-videos/hires/s25.pretrim.mp4` and `./out/work-videos/hires/s25.posttrim.mp4` for debugging
- all current `sXX` scripts under `./ssc/` are addressable by shorthand
- invoking `./ops/stelplay` without a script ref prints usage and lists available `sXX` shorthands
- users can understand the tool from `./ops/stelplay --help` alone

## Recommended Implementation Shape

This PRD does not mandate a language, but the preferred implementation shape is a small Python CLI because it offers:

- straightforward argument parsing
- safer temp-file handling
- better process supervision for `ffmpeg` and Stellarium
- cleaner signal handling and cleanup than a minimal shell script

## Additional Decisions

- The `--record=VALUE` rule should be documented explicitly rather than left heuristic-only.
- If the tool is called without a script reference, it should print usage and list the currently available `sXX` script shorthands under `./ssc/`.

## Future Consideration

- A later `--device` option may be useful for selecting the `ffmpeg` AVFoundation source if the fixed v1 default proves inconvenient.
