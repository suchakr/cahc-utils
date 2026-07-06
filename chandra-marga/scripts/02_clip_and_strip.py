#!/usr/bin/env python3
"""Crop raw Stellarium screenshots to tiles, then assemble them into a strip.

Formalizes what was previously an ad hoc sequence of hand-run ImageMagick
`convert` commands (pixel offsets recalculated by hand each time the FOV
changed) into a reproducible, numbered pipeline step.

Usage:
    uv run python scripts/02_clip_and_strip.py <leaf_dir> [options]

Example:
    uv run python scripts/02_clip_and_strip.py \\
        /Users/sunder/projects/cahc/cahc-utils/stel_scripts/moon-shranga~/set-sun9/-527/shukla_pratipada
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from chandra_marga import crop, strips


def find_screenshots(leaf_dir: Path) -> list[Path]:
    """Numbered screenshots only (NN.jpg), sorted numerically -- excludes
    sentinel files (zzz-done.jpg) and anything already in crops~/."""
    files = [f for f in leaf_dir.glob("*.jpg") if re.fullmatch(r"\d+\.jpg", f.name)]
    return sorted(files, key=lambda f: int(f.stem))


def find_existing_tiles(leaf_dir: Path) -> list[Path]:
    """Existing NN-tile.jpg files in leaf_dir/crops~/, sorted numerically."""
    crops_dir = leaf_dir / "crops~"
    files = [f for f in crops_dir.glob("*-tile.jpg") if re.fullmatch(r"\d+-tile\.jpg", f.name)]
    return sorted(files, key=lambda f: int(f.stem.split("-")[0]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("leaf_dir", type=Path, help="Directory of raw NN.jpg screenshots")
    parser.add_argument("--tile-width-deg", type=float, default=crop.DEFAULT_TILE_WIDTH_DEG)
    parser.add_argument("--tile-height-deg", type=float, default=crop.DEFAULT_TILE_HEIGHT_DEG)
    parser.add_argument("--floor-deg", type=float, default=crop.DEFAULT_TILE_FLOOR_DEG)
    parser.add_argument("--fov", type=float, default=None,
                         help="Override FOV (deg); default: query live Stellarium")
    parser.add_argument("--cols", type=int, default=strips.DEFAULT_COLS)
    parser.add_argument("--moon-shranga-root", type=Path, default=None,
                         help="Default: leaf_dir's ancestor named 'moon-shranga~'")
    parser.add_argument("--strip-only", action="store_true",
                         help="Skip re-cropping (no Stellarium/FOV query needed); rebuild the "
                              "strip from existing leaf_dir/crops~/NN-tile.jpg files only. Use "
                              "this to regenerate just the strip (e.g. after a strips.py fix) "
                              "without repeating the Stellarium capture or re-crop step.")
    args = parser.parse_args()

    leaf_dir = args.leaf_dir.resolve()

    if args.strip_only:
        tile_paths = find_existing_tiles(leaf_dir)
        if not tile_paths:
            raise SystemExit(f"No existing crops~/NN-tile.jpg files found in {leaf_dir}")
        print(f"Using {len(tile_paths)} existing tiles from {leaf_dir / 'crops~'} (--strip-only)")
    else:
        screenshots = find_screenshots(leaf_dir)
        if not screenshots:
            raise SystemExit(f"No NN.jpg screenshots found in {leaf_dir}")
        print(f"Found {len(screenshots)} screenshots in {leaf_dir}")

        if args.fov is not None:
            fov_deg = args.fov
            print(f"Using --fov override: {fov_deg} deg")
        else:
            fov_deg = crop.get_live_fov()
            print(f"Queried live Stellarium FOV: {fov_deg} deg")

        capture_w, capture_h = crop.get_image_size(screenshots[0])
        print(f"Capture resolution: {capture_w}x{capture_h}")

        box = crop.compute_tile_box(
            capture_w, capture_h, fov_deg,
            tile_width_deg=args.tile_width_deg,
            tile_height_deg=args.tile_height_deg,
            floor_deg=args.floor_deg,
        )
        print(f"Tile box: {box.width}x{box.height}+{box.left}+{box.top} "
              f"(ppd={box.ppd:.3f}, {args.tile_width_deg}x{args.tile_height_deg}deg, "
              f"floor={args.floor_deg}deg)")

        crops_dir = leaf_dir / "crops~"
        tile_paths = []
        for src in screenshots:
            dst = crops_dir / f"{src.stem}-tile.jpg"
            crop.crop_image(src, box, dst)
            tile_paths.append(dst)
        print(f"Cropped {len(tile_paths)} tiles -> {crops_dir}")

    moon_shranga_root = args.moon_shranga_root
    if moon_shranga_root is None:
        for parent in [leaf_dir, *leaf_dir.parents]:
            if parent.name == "moon-shranga~":
                moon_shranga_root = parent
                break
    if moon_shranga_root is None:
        raise SystemExit(
            "Could not find a 'moon-shranga~' ancestor of leaf_dir; "
            "pass --moon-shranga-root explicitly."
        )

    output_path = strips.strip_output_path(leaf_dir, moon_shranga_root)
    strips.build_strip(tile_paths, output_path, cols=args.cols)
    print(f"Wrote strip ({args.cols} cols) -> {output_path}")


if __name__ == "__main__":
    main()
