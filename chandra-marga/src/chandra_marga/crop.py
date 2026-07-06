"""Tile-crop geometry for the centered-at-horizon framing convention.

Convention (validated interactively this session): the Stellarium camera is
centered on (az=moon.azimuth, alt=0) every event, so the horizon at the
moon's azimuth sits at the exact pixel center of every screenshot,
regardless of the moon's actual altitude that night. This makes the tile
crop a FIXED pixel rectangle, computed purely from:
  - the live FOV (horizontal) Stellarium was primed with
  - the actual capture resolution
  - the desired tile width/height/floor, in degrees

ppd (pixels per degree) = capture_width_px / fov_deg
(validated: matches actual pixel measurements to within ~1px at FOV=50 and
FOV=64.7385 on 3024x1898 captures).
"""

from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

DEFAULT_BASE_URL = "http://127.0.0.1:8090/api"

# Validated defaults (this session): floor -2deg avoids clipping the moon
# just above the horizon; 15x17deg comfortably avoids the on-screen title
# overlay bleeding into the tile, for a 3024x1898 capture at FOV~65deg.
DEFAULT_TILE_WIDTH_DEG = 15.0
DEFAULT_TILE_HEIGHT_DEG = 17.0
DEFAULT_TILE_FLOOR_DEG = -2.0


def get_live_fov(base_url: str = DEFAULT_BASE_URL, timeout: float = 5.0) -> float:
    """Query Stellarium Remote Control for the currently primed FOV (deg).

    Raises on any network/parsing error -- callers should catch and fall
    back to an explicit --fov override if Stellarium isn't reachable.
    """
    with urllib.request.urlopen(f"{base_url}/main/status", timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return float(data["view"]["fov"])


@dataclass(frozen=True)
class TileBox:
    left: int
    top: int
    width: int
    height: int
    ppd: float
    fov_deg: float

    def as_box(self) -> tuple[int, int, int, int]:
        """PIL-style (left, upper, right, lower) box for Image.crop()."""
        return (self.left, self.top, self.left + self.width, self.top + self.height)


def compute_tile_box(
    capture_width_px: int,
    capture_height_px: int,
    fov_deg: float,
    tile_width_deg: float = DEFAULT_TILE_WIDTH_DEG,
    tile_height_deg: float = DEFAULT_TILE_HEIGHT_DEG,
    floor_deg: float = DEFAULT_TILE_FLOOR_DEG,
) -> TileBox:
    """Compute the fixed pixel crop box for the centered-at-horizon convention.

    The frame center (capture_width_px/2, capture_height_px/2) corresponds
    to (az=moon_az, alt=0). The tile spans [floor_deg, floor_deg + tile_height_deg]
    in altitude, centered horizontally.
    """
    ppd = capture_width_px / fov_deg
    center_x = capture_width_px / 2.0
    center_y = capture_height_px / 2.0
    top_deg = floor_deg + tile_height_deg  # altitude at the top edge of the tile

    width_px = round(tile_width_deg * ppd)
    height_px = round(tile_height_deg * ppd)
    left = round(center_x - width_px / 2.0)
    top = round(center_y - top_deg * ppd)

    return TileBox(left=left, top=top, width=width_px, height=height_px, ppd=ppd, fov_deg=fov_deg)


def crop_image(src: Path, box: TileBox, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as img:
        cropped = img.crop(box.as_box())
        cropped.save(dst, "JPEG")


def get_image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as img:
        return img.size
