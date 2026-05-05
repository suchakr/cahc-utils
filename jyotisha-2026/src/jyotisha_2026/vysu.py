from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


VALID_ACTIONS = {
    "caption",
    "set",
    "reveal",
    "hide",
    "camera",
    "epochTravel",
    "flash",
    "fullscreen",
    "exitFullscreen",
}

VALID_TARGETS = {
    "eclipticGrid",
    "equatorialGrid",
    "eclipticNakSegments",
    "eclipticBand",
    "eclipticDividers",
    "eclipticLabels",
    "eclipticPoles",
    "stars",
    "nakshatras",
    "nakshatraLines",
    "nakshatraLabels",
    "polarItems",
    "northPolarItems",
    "southPolarItems",
    "poleTrack",
    "precessionCircle",
    "seasonalFrame",
    "overlay",
    "referencePlanes",
    "eclipticPlane",
    "equatorialPlane",
    "nsAxis",
    "NEP",
    "SEP",
    "NP",
    "SP",
    "equator",
    "VE",
    "SS",
    "AE",
    "WS",
    "agastya",
    "thuban",
    "polaris",
    "matsya",
    "sisumara",
    "shishumara",
}

TARGET_ALIASES = {
    "eclipticgrid": "eclipticGrid",
    "eclgrid": "eclipticGrid",
    "eclgridwire": "eclipticGrid",
    "eclipticnaksegments": "eclipticNakSegments",
    "eclipticnakssegments": "eclipticNakSegments",
    "naksegments": "eclipticNakSegments",
    "nakssegments": "eclipticNakSegments",
    "eclipticsegments": "eclipticNakSegments",
    "eclipticband": "eclipticBand",
    "eclipticdividers": "eclipticDividers",
    "sectordividers": "eclipticDividers",
    "eclipticlabels": "eclipticLabels",
    "sectorlabels": "eclipticLabels",
    "eclipticpoles": "eclipticPoles",
    "eclipticplane": "eclipticPlane",
    "equatorialplane": "equatorialPlane",
    "equatorialgrid": "equatorialGrid",
    "equatorgrid": "equatorialGrid",
    "eqgrid": "equatorialGrid",
    "eq": "equatorialGrid",
    "referenceplanes": "referencePlanes",
    "refs": "referencePlanes",
    "nsaxis": "nsAxis",
    "axis": "nsAxis",
    "nep": "NEP",
    "sep": "SEP",
    "np": "NP",
    "sp": "SP",
    "stars": "stars",
    "naks": "nakshatras",
    "nak": "nakshatras",
    "nakshatra": "nakshatras",
    "nakshatras": "nakshatras",
    "seasonalframe": "seasonalFrame",
    "seasons": "seasonalFrame",
    "rtus": "seasonalFrame",
    "rtu": "seasonalFrame",
    "poletrack": "poleTrack",
    "polepath": "poleTrack",
    "precessioncircle": "precessionCircle",
    "precession": "precessionCircle",
    "overlay": "overlay",
    "polaritems": "polarItems",
    "northpolaritems": "northPolarItems",
    "northpolar": "northPolarItems",
    "southpolaritems": "southPolarItems",
    "southpolar": "southPolarItems",
    "equator": "equator",
    "ve": "VE",
    "ss": "SS",
    "ae": "AE",
    "ws": "WS",
    "agastya": "agastya",
    "canopus": "agastya",
    "thuban": "thuban",
    "abhayadhruva": "thuban",
    "polaris": "polaris",
    "matsyadhruva": "polaris",
    "matsya": "matsya",
    "sisumara": "sisumara",
    "shishumara": "sisumara",
    "shimshumara": "sisumara",
}

BLANK_UI = {
    "showGrid": False,
    "showEquatorialGrid": False,
    "showReferencePlanes": False,
    "showEclipticPlane": False,
    "showEquatorialPlane": False,
    "showNsAxis": False,
    "showEclipticBand": False,
    "showEclipticDividers": False,
    "showEclipticLabels": False,
    "showEclipticPoles": False,
    "showStars": False,
    "showNakshatraLines": False,
    "showNakshatraLabels": False,
    "showPolarItems": False,
    "showNorthPolarItems": False,
    "showSouthPolarItems": False,
    "showNEP": False,
    "showSEP": False,
    "showNP": False,
    "showSP": False,
    "showPoleTrack": False,
    "showSeasonalFrame": False,
    "showOverlay": False,
}

COLOR_NAMES = {
    "white",
    "black",
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "cyan",
    "teal",
    "purple",
    "magenta",
    "pink",
    "gray",
    "grey",
    "gold",
    "brown",
}


class VySuError(ValueError):
    pass


def strip_comment(line: str) -> str:
    quote = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            quote = not quote
        if not quote and ch == "#":
            if re.match(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(\b|\s|$)", line[i:]):
                i += 1
            else:
                return line[:i]
        i += 1
    return line


def parse_metadata(source: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for line in source.splitlines():
        match = re.match(r"^\s*#\s*([a-zA-Z][\w-]*)\s*:\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1).lower()] = match.group(2)
    return metadata


def split_statements(line: str) -> list[str]:
    statements: list[str] = []
    quote = False
    start = 0
    for i, ch in enumerate(line):
        if ch == '"':
            quote = not quote
        if not quote and ch == ";":
            part = line[start:i].strip()
            if part:
                statements.append(part)
            start = i + 1
    tail = line[start:].strip()
    if tail:
        statements.append(tail)
    return statements


def tokenize(statement: str) -> list[str]:
    return re.findall(r'"[^"]*"|\S+', statement)


def parse_duration(token: str | None) -> dict[str, int] | None:
    if not token:
        return None
    match = re.match(r"^(\d+):(\d*)?(?::(\d*)?)?$", str(token))
    if not match:
        return None
    out: dict[str, int] = {"duration": int(match.group(1))}
    if match.group(2):
        out["fadeIn"] = int(match.group(2))
    if match.group(3):
        out["fadeOut"] = int(match.group(3))
    return out


def parse_vec3(token: str | None) -> dict[str, float] | None:
    if not token:
        return None
    try:
        parts = [float(part) for part in token.split(",")]
    except ValueError:
        return None
    if len(parts) != 3:
        return None
    return {"x": parts[0], "y": parts[1], "z": parts[2]}


def parse_alpha(token: str | None) -> float | None:
    raw = str(token or "").strip()
    if re.match(r"^%\d+(?:\.\d+)?$", raw):
        value = float(raw[1:]) / 100
    elif re.match(r"^\d+(?:\.\d+)?%$", raw):
        value = float(raw[:-1]) / 100
    elif re.match(r"^(?:0?\.\d+|1(?:\.0+)?)$", raw):
        value = float(raw)
    elif re.match(r"^\d+(?:\.\d+)?$", raw) and float(raw) <= 1:
        value = float(raw)
    else:
        return None
    return max(0.0, min(1.0, value))


def parse_color(token: str | None) -> str | None:
    raw = str(token or "").strip()
    if re.match(r"^#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?$", raw):
        return raw
    lower = raw.lower()
    if lower in COLOR_NAMES:
        return lower
    return None


def normalize_target(token: str, line_number: int, warnings: list[str]) -> str | None:
    raw = str(token or "").strip()
    if not raw:
        warnings.append(f"Line {line_number}: missing target.")
        return None
    if raw[0] in "$*@":
        return raw
    key = re.sub(r"[._-]", "", raw).lower()
    target = TARGET_ALIASES.get(key, raw)
    if target not in VALID_TARGETS:
        warnings.append(f'Line {line_number}: unsupported target "{raw}".')
        return None
    return target


def merge_patch(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            merge_patch(target[key], value)
        else:
            target[key] = value
    return target


def grid_patch(args: list[str], line_number: int, warnings: list[str]) -> dict[str, Any] | None:
    if len(args) < 2:
        warnings.append(f"Line {line_number}: grid needs kind and step.")
        return None
    kind = args[0].lower()
    try:
        step = float(args[1])
    except ValueError:
        warnings.append(f"Line {line_number}: grid step must be numeric.")
        return None
    color = parse_color(args[2]) if len(args) > 2 else None
    patch: dict[str, Any] = {"grid": {}, "ui": {}}
    if kind in {"ecliptic", "ecl"}:
        patch["grid"]["eclipticStepDeg"] = step
        if color:
            patch["grid"]["parallelColor"] = color
            patch["grid"]["meridianColor"] = color
        patch["ui"]["showGrid"] = True
    elif kind in {"equatorial", "equator", "eq"}:
        patch["grid"]["equatorialStepDeg"] = step
        if color:
            patch["grid"]["equatorialColor"] = color
        patch["ui"]["showEquatorialGrid"] = True
    else:
        warnings.append(f"Line {line_number}: grid kind must be ecliptic or equatorial.")
        return None
    return patch


def compile_vysu(source: str, *, story_id: str, title: str | None = None) -> dict[str, Any]:
    metadata = parse_metadata(source)
    story: dict[str, Any] = {
        "id": story_id,
        "title": title or metadata.get("title") or story_id.replace("-", " ").title(),
        "version": int(metadata.get("version", "1")),
        "vysu": source.rstrip() + "\n",
        "cues": [],
    }
    if metadata.get("featured", "").lower() in {"1", "true", "yes", "y"}:
        story["featured"] = True
    if "group" in metadata:
        story["group"] = metadata["group"]
    if "tags" in metadata:
        story["tags"] = [tag.strip() for tag in metadata["tags"].split(",") if tag.strip()]
    if "order" in metadata:
        try:
            story["order"] = float(metadata["order"])
        except ValueError:
            pass
    initial: dict[str, Any] = {"ui": {}}
    warnings: list[str] = []
    pending_wait = 0
    emitted = 0

    def cue_time() -> int | str:
        nonlocal pending_wait
        if emitted == 0 and pending_wait == 0:
            return 0
        wait = pending_wait
        pending_wait = 0
        return f"+{wait}"

    def add_cue(cue: dict[str, Any]) -> None:
        nonlocal emitted
        story["cues"].append({"at": cue_time(), **cue})
        emitted += 1

    for line_number, line in enumerate(source.splitlines(), start=1):
        if re.match(r"^\s*#\s*[a-zA-Z][\w-]*\s*:", line):
            continue
        for statement in split_statements(strip_comment(line)):
            tokens = tokenize(statement)
            if not tokens:
                continue
            directive = tokens[0].lower()
            args = tokens[1:]

            if directive == "stage":
                i = 0
                while i < len(args):
                    arg = args[i].lower()
                    if arg == "blank":
                        initial["ui"].update(BLANK_UI)
                    elif arg in {"night", "twilight", "day"}:
                        initial["lightPreset"] = arg
                    elif arg in {"year", "epoch"} and i + 1 < len(args):
                        try:
                            initial["epochYear"] = int(float(args[i + 1]))
                            i += 1
                        except ValueError:
                            warnings.append(f"Line {line_number}: stage {arg} needs numeric value.")
                    else:
                        warnings.append(f'Line {line_number}: unknown stage token "{args[i]}".')
                    i += 1
                continue

            if directive == "wait":
                try:
                    pending_wait += int(float(args[0]))
                except (IndexError, ValueError):
                    warnings.append(f"Line {line_number}: wait needs milliseconds.")
                continue

            if directive == "grid":
                patch = grid_patch(args, line_number, warnings)
                if patch:
                    add_cue({"action": "set", "state": patch})
                continue

            if directive in {"fullscreen", "theater"}:
                add_cue({"action": "fullscreen"})
                continue
            if directive in {"exitfullscreen", "canvas"}:
                add_cue({"action": "exitFullscreen"})
                continue

            if directive in {"caption", "say", "title"}:
                cue: dict[str, Any] = {"action": "caption", "duration": 1500, "fadeIn": 300, "fadeOut": 300}
                i = 0
                while i < len(args):
                    arg = args[i]
                    duration = parse_duration(arg)
                    color = parse_color(arg)
                    alpha = parse_alpha(arg)
                    lower = arg.lower()
                    if re.match(r'^".*"$', arg):
                        cue["text"] = arg[1:-1]
                    elif duration:
                        cue.update(duration)
                    elif re.match(r"^\d+$", arg):
                        cue["duration"] = int(arg)
                    elif lower in {"size", "font", "fontsize"} and i + 1 < len(args):
                        try:
                            cue["sizeRem"] = float(args[i + 1])
                            i += 1
                        except ValueError:
                            warnings.append(f"Line {line_number}: {arg} needs numeric size.")
                    elif lower == "fadein" and i + 1 < len(args):
                        cue["fadeIn"] = int(float(args[i + 1]))
                        i += 1
                    elif lower == "fadeout" and i + 1 < len(args):
                        cue["fadeOut"] = int(float(args[i + 1]))
                        i += 1
                    elif color:
                        cue["color"] = color
                    elif alpha is not None:
                        cue["opacity"] = alpha
                    i += 1
                if "text" not in cue:
                    warnings.append(f"Line {line_number}: caption needs quoted text.")
                else:
                    add_cue(cue)
                continue

            if directive in {"show", "reveal", "rollout", "fade", "hide"}:
                if not args:
                    warnings.append(f"Line {line_number}: {directive} needs target.")
                    continue
                target = normalize_target(args[0], line_number, warnings)
                if not target:
                    continue
                cue = {"action": "hide" if directive == "hide" else "reveal", "target": target}
                if directive in {"rollout", "fade"}:
                    cue["mode"] = directive
                for arg in args[1:]:
                    duration = parse_duration(arg)
                    lower = arg.lower()
                    if duration:
                        cue["duration"] = duration["duration"]
                    elif lower in {"instant", "fade", "stagger", "rollout"}:
                        cue["mode"] = lower
                    elif lower in {"ecliptic", "reverse-ecliptic", "reverse", "forward"}:
                        cue["order"] = lower
                add_cue(cue)
                continue

            if directive == "flash":
                if not args:
                    warnings.append(f"Line {line_number}: flash needs target.")
                    continue
                target = normalize_target(args[0], line_number, warnings)
                if not target:
                    continue
                cue = {"action": "flash", "target": target, "duration": 1000}
                for arg in args[1:]:
                    duration = parse_duration(arg)
                    if duration:
                        cue["duration"] = duration["duration"]
                    elif re.match(r"^\d+$", arg):
                        cue["duration"] = int(arg)
                add_cue(cue)
                continue

            if directive == "camera":
                cue: dict[str, Any] = {"action": "camera", "camera": {}, "duration": 1000}
                i = 0
                while i < len(args):
                    lower = args[i].lower()
                    if lower in {"pos", "position"} and i + 1 < len(args):
                        vec = parse_vec3(args[i + 1])
                        if vec:
                            cue["camera"]["position"] = vec
                            i += 1
                    elif lower == "target" and i + 1 < len(args):
                        vec = parse_vec3(args[i + 1])
                        if vec:
                            cue["camera"]["target"] = vec
                            i += 1
                    elif lower == "fov" and i + 1 < len(args):
                        cue["camera"]["fov"] = float(args[i + 1])
                        i += 1
                    else:
                        duration = parse_duration(args[i])
                        if duration:
                            cue["duration"] = duration["duration"]
                        elif re.match(r"^\d+$", args[i]):
                            cue["duration"] = int(args[i])
                    i += 1
                if cue["camera"]:
                    if emitted == 0 and pending_wait == 0:
                        initial["camera"] = cue["camera"]
                        if "duration" in cue:
                            initial["camera"].pop("duration", None)
                    else:
                        add_cue(cue)
                else:
                    warnings.append(f"Line {line_number}: camera needs pos, target, or fov.")
                continue

            if directive in {"travel", "epochtravel"}:
                if len(args) < 3:
                    warnings.append(f"Line {line_number}: travel needs FROM to TO.")
                    continue
                cue: dict[str, Any] = {"action": "epochTravel", "from": int(float(args[0])), "to": int(float(args[2])), "duration": 5000, "step": 100}
                i = 3
                while i < len(args):
                    duration = parse_duration(args[i])
                    if duration:
                        cue["duration"] = duration["duration"]
                    elif args[i].lower() == "step" and i + 1 < len(args):
                        cue["step"] = int(float(args[i + 1]))
                        i += 1
                    elif re.match(r"^\d+$", args[i]):
                        cue["duration"] = int(args[i])
                    i += 1
                add_cue(cue)
                continue

            warnings.append(f'Line {line_number}: unknown directive "{tokens[0]}".')

    if initial.get("ui") or any(key in initial for key in ("lightPreset", "epochYear", "camera")):
        if not initial.get("ui"):
            initial.pop("ui", None)
        story["initial"] = initial
    if warnings:
        story["warnings"] = warnings
    validate_story(story, Path(f"{story_id}.json"))
    return story


def validate_story(story: dict[str, Any], path: Path) -> dict[str, Any]:
    required = ["id", "title", "version", "cues"]
    missing = [key for key in required if key not in story]
    if missing:
        raise VySuError(f"{path}: missing required story keys: {', '.join(missing)}")
    if story["id"] != path.stem:
        raise VySuError(f"{path}: story id must match filename stem")
    if not isinstance(story["cues"], (list, dict)):
        raise VySuError(f"{path}: cues must be a list or keyed object")

    cues = list(enumerate(story["cues"])) if isinstance(story["cues"], list) else list(story["cues"].items())
    for index, cue in cues:
        if not isinstance(cue, dict):
            raise VySuError(f"{path}: cue {index} must be an object")
        if "at" not in cue and "after" not in cue:
            raise VySuError(f"{path}: cue {index} needs at or after")
        action = cue.get("action")
        if action not in VALID_ACTIONS:
            raise VySuError(f"{path}: cue {index} has unknown action {action!r}")
        if action == "caption" and "text" not in cue:
            raise VySuError(f"{path}: cue {index} caption needs text")
        if action == "set" and "state" not in cue:
            raise VySuError(f"{path}: cue {index} set needs state")
        if action in {"reveal", "hide"} and "target" not in cue:
            raise VySuError(f"{path}: cue {index} {action} needs target")
        if action in {"reveal", "hide", "flash"} and "target" in cue:
            target = cue["target"]
            if isinstance(target, str) and not target.startswith(("$", "*", "@")) and target not in VALID_TARGETS:
                raise VySuError(f"{path}: cue {index} has unknown target {target!r}")
        if action == "flash" and "target" not in cue:
            raise VySuError(f"{path}: cue {index} flash needs target")
        if action == "camera" and "camera" not in cue:
            raise VySuError(f"{path}: cue {index} camera needs camera")
        if action == "set" and "state" in cue and isinstance(cue["state"], dict) and "camera" in cue["state"]:
            camera = cue["state"]["camera"]
            if isinstance(camera, dict) and (
                "position" in camera or "target" in camera or "fov" in camera
            ):
                continue
        if action == "epochTravel":
            for key in ["from", "to", "duration"]:
                if key not in cue:
                    raise VySuError(f"{path}: cue {index} epochTravel needs {key}")
    return story


def compile_vysu_file(path: Path) -> dict[str, Any]:
    return compile_vysu(path.read_text(encoding="utf-8"), story_id=path.stem)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
