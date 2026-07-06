"""Export precomputed JD event arrays for Stellarium `.ssc` scripts.

Remote Control's `/scripts/direct` endpoint (used by both `run-file` and
`script-direct`) does not resolve `include()`, so `.ssc` scripts must embed
JD arrays directly. This module writes a conventional `.inc` file (for
reference / potential future include() use) AND produces a copy-pasteable
flat JS array literal for direct embedding into a script.
"""

from __future__ import annotations

import ast
import pprint
from pathlib import Path

from chandra_marga import config


def load_inc_dict(filename: str) -> dict[str, list[float]]:
    """Load a `VAR_NAME = {...}` .inc file (e.g. lunar-set-events--0527.inc)
    and return the dict literal, without executing the file as Python (the
    RHS is a plain dict literal, so `ast.literal_eval` is sufficient and safe).
    """
    inc_file = config.STEL_SCRIPTS_DIR / filename
    text = inc_file.read_text()
    _, _, rhs = text.partition("=")
    return ast.literal_eval(rhs.strip())


def write_inc_file(jd_dict: dict[str, list[float]], var_name: str, filename: str) -> Path:
    """Write a `VAR_NAME = {...}` .inc file, matching the existing
    `MOON_SET_JDS = {...}` convention (see lunar-set-events--0527.inc).
    """
    inc_file = config.STEL_SCRIPTS_DIR / filename
    with open(inc_file, "w") as f:
        f.write(f"{var_name} = ")
        pprint.pprint(jd_dict, stream=f, width=120, compact=True)
    return inc_file


def format_js_array(jds: list[float], var_name: str = "JDS", indent: int = 2, per_line: int = 4) -> str:
    """Format a flat JD list as a copy-pasteable JS array literal, matching
    the style already used in a10-moon-shranga-sun9.ssc's inline `JDS = [...]`.
    """
    pad = " " * indent
    lines = [f"{var_name} = ["]
    for i in range(0, len(jds), per_line):
        chunk = jds[i:i + per_line]
        row = ", ".join(repr(float(v)) for v in chunk)
        suffix = "," if i + per_line < len(jds) else ""
        lines.append(f"{pad}{row}{suffix}")
    lines.append("]")
    return "\n".join(lines)
