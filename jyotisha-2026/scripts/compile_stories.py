from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from jyotisha_2026.paths import LAB_ROOT, REPO_ROOT


SLUG = "nakshatra-precession-explorer"


def story_roots(slug: str) -> tuple[Path, Path]:
    root = REPO_ROOT / "stories" / slug
    return root, root / "compiled"


def compile_story_sources(slug: str) -> list[dict[str, Any]]:
    _root, _compiled_root = story_roots(slug)
    command = ["node", str(REPO_ROOT / "scripts" / "compile-vysu.mjs"), slug]
    result = subprocess.run(command, cwd=REPO_ROOT, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")


def browser_vysu_compiler_source() -> str:
    source = (REPO_ROOT / "scripts" / "vysu-compiler.mjs").read_text(encoding="utf-8")
    source = source.replace(
        "export function compileVyomaSutra(source, options = {}) {",
        "compileVyomaSutra = function compileVyomaSutraStage1(source, options = {}) {",
    )
    source = source.replace("export function ", "function ")
    return "// BEGIN VYOMASUTRA COMPILER\n{\n" + source + "\n}\n// END VYOMASUTRA COMPILER"


def patch_embedded_compiler(text: str) -> tuple[str, bool]:
    compiler = browser_vysu_compiler_source()
    marked_pattern = re.compile(
        r"// BEGIN VYOMASUTRA COMPILER\n.*?\n// END VYOMASUTRA COMPILER",
        re.DOTALL,
    )
    if marked_pattern.search(text):
        return marked_pattern.sub(lambda _match: compiler, text, count=1), True

    legacy_pattern = re.compile(
        r"\n      \{\nconst VALID_ACTIONS = new Set\(\[.*?\n\}\n\n(?=      function mergeSettings)",
        re.DOTALL,
    )
    if legacy_pattern.search(text):
        replacement = "\n      " + compiler + "\n\n"
        return legacy_pattern.sub(lambda _match: replacement, text, count=1), True
    return text, False


def refresh_browser_compiler_assets(slug: str) -> bool:
    page_root = LAB_ROOT / slug
    source_path = REPO_ROOT / "scripts" / "vysu-compiler.mjs"
    changed = False

    js_path = page_root / "assets" / "js" / "vysu-compiler.mjs"
    if js_path.exists():
        js_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        changed = True

    for path in [page_root / "index.html", page_root / "assets" / "js" / "three-explorer.js"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        patched, did_patch = patch_embedded_compiler(text)
        if did_patch:
            path.write_text(patched, encoding="utf-8")
            changed = True
    return changed


def patch_lab_story_data(slug: str, compiled_stories: list[dict[str, Any]]) -> bool:
    page_path = LAB_ROOT / slug / "index.html"
    if not page_path.exists():
        return False

    text = page_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'(<script id="story-data" type="application/json">)(.*?)(</script>)',
        re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        return False

    ordered = sorted(
        compiled_stories,
        key=lambda story: (float(story.get("order", 9999)), str(story.get("title", story["id"]))),
    )
    replacement = match.group(1) + json.dumps(ordered, ensure_ascii=False) + match.group(3)
    page_path.write_text(pattern.sub(lambda _match: replacement, text, count=1), encoding="utf-8")
    write_json(LAB_ROOT / slug / "stories.json", ordered)
    refresh_browser_compiler_assets(slug)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile build-time VyomaSutra stories.")
    parser.add_argument("slug", nargs="?", default=SLUG)
    args = parser.parse_args()

    stories = compile_story_sources(args.slug)
    patched = patch_lab_story_data(args.slug, stories)
    print(f"Compiled {len(stories)} story source(s) for {args.slug}.")
    if patched:
        print(f"Patched {LAB_ROOT / args.slug / 'index.html'} and wrote stories.json.")


if __name__ == "__main__":
    main()
