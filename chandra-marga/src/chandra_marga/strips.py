"""Strip (contact-sheet) assembly from cropped tiles.

Ported from jyotisha/lunar-events-calculator.ipynb's
StellariumIntegration.generate_strips_for_all_leaf_dirs, including its
column-letter (A, B, C...) / row-number (1, 2, 3...) header convention, but
using PIL directly instead of matplotlib -- our tiles are already
uniform-size crops (see crop.py), so no per-cell dynamic sizing is needed.

Naming/placement convention (matches the existing set/ tree, verified by
inspection): the strip is written as a sibling file one level ABOVE its
source leaf directory, named `strip-<safe_name>.jpg` where `safe_name` is
the leaf directory's path relative to `moon-shranga~/`, with `/` replaced
by `-` (e.g. `set-sun9/-527/shukla_pratipada` -> `set-sun9--527-shukla_pratipada`).
"""

from __future__ import annotations

import string
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

DEFAULT_COLS = 7
GUTTER_PX = 12          # spacing between cells (and around the whole grid)
FONT_SCALE = 9          # multiplier on the base font-size formula
BG_COLOR = (255, 255, 255)
LABEL_COLOR = (0, 0, 0)

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/SFNS.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _col_label(i: int) -> str:
    """A, B, ..., Z, AA, AB, ... (only A-Z needed at our scale, but this
    degrades gracefully past 26 columns instead of raising)."""
    letters = string.ascii_uppercase
    label = ""
    i += 1
    while i > 0:
        i, rem = divmod(i - 1, 26)
        label = letters[rem] + label
    return label


def safe_name_for(leaf_dir: Path, moon_shranga_root: Path) -> str:
    rel = leaf_dir.relative_to(moon_shranga_root)
    return str(rel).replace("/", "-").replace("\\", "-")


def strip_output_path(leaf_dir: Path, moon_shranga_root: Path) -> Path:
    safe_name = safe_name_for(leaf_dir, moon_shranga_root)
    return leaf_dir.parent / f"strip-{safe_name}.jpg"


def build_strip(tile_paths: list[Path], output_path: Path, cols: int = DEFAULT_COLS) -> Path:
    """Paste tile_paths (in the given order) into a cols-wide grid, with
    column-letter headers above and row-number labels to the left (matching
    the notebook's convention), and save.

    All tiles are expected to be the same size (true for crop.py's output).
    Rows fill left-to-right, top-to-bottom, in the order tile_paths is given.
    """
    if not tile_paths:
        raise ValueError("build_strip: no tile paths given")

    images = [Image.open(p) for p in tile_paths]
    try:
        tile_w, tile_h = images[0].size
        n = len(images)
        cols = min(cols, n)
        rows = (n + cols - 1) // cols

        font_size = max(14, tile_h // 40) * FONT_SCALE
        font = _load_font(font_size)

        header_h = font_size + 2 * GUTTER_PX
        label_w = font_size * 2 + 2 * GUTTER_PX

        canvas_w = label_w + cols * tile_w + (cols + 1) * GUTTER_PX
        canvas_h = header_h + rows * tile_h + (rows + 1) * GUTTER_PX
        canvas = Image.new("RGB", (canvas_w, canvas_h), BG_COLOR)
        draw = ImageDraw.Draw(canvas)

        for col in range(cols):
            x = label_w + GUTTER_PX + col * (tile_w + GUTTER_PX) + tile_w // 2
            draw.text((x, header_h // 2), _col_label(col), fill=LABEL_COLOR, font=font, anchor="mm")

        for idx, img in enumerate(images):
            row, col = divmod(idx, cols)
            x = label_w + GUTTER_PX + col * (tile_w + GUTTER_PX)
            y = header_h + GUTTER_PX + row * (tile_h + GUTTER_PX)
            canvas.paste(img, (x, y))
            if col == 0:
                draw.text(
                    (label_w // 2, y + tile_h // 2), str(row + 1),
                    fill=LABEL_COLOR, font=font, anchor="mm",
                )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, "JPEG", quality=90)
    finally:
        for img in images:
            img.close()

    return output_path
