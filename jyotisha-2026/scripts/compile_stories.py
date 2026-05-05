from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from jyotisha_2026.paths import LAB_ROOT, REPO_ROOT
from jyotisha_2026.vysu import compile_vysu_file, validate_story, write_json


SLUG = "nakshatra-precession-explorer"


def story_roots(slug: str) -> tuple[Path, Path]:
    root = REPO_ROOT / "stories" / slug
    return root, root / "compiled"


def compile_story_sources(slug: str) -> list[dict[str, Any]]:
    root, compiled_root = story_roots(slug)
    compiled_root.mkdir(parents=True, exist_ok=True)
    stories: list[dict[str, Any]] = []
    expected_outputs: set[Path] = set()

    for path in sorted(root.glob("*.vysu")):
        story = compile_vysu_file(path)
        out_path = compiled_root / f"{story['id']}.json"
        expected_outputs.add(out_path)
        write_json(out_path, story)
        stories.append(validate_story(story, out_path))

    for path in sorted(root.glob("*.json")):
        story = json.loads(path.read_text(encoding="utf-8"))
        out_path = compiled_root / path.name
        expected_outputs.add(out_path)
        write_json(out_path, story)
        stories.append(validate_story(story, out_path))

    for stale_path in compiled_root.glob("*.json"):
        if stale_path not in expected_outputs:
            stale_path.unlink()

    return stories


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
