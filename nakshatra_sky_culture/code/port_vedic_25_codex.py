from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "vedic_sky_culture"
TARGET = ROOT / "vedic_25_codex"
ILLUSTRATIONS = TARGET / "illustrations"


DESCRIPTION_MD = """# Vedic Codex

## Introduction

Vedic sky culture with some commonly known constellations related to Nakshatra-s.

## Description

### <notr>Rashi (राशिः)</notr>

The sidereal zodiac is an imaginary belt of 360 degrees, divided into 12 equal parts of 30 degrees each. Each part is called a sign or rashi. Their names are shown in brackets.

In Vedic astronomy there are two systems of measuring time, lunar calendar and solar calendar. In both cases one year is divided into 12 months or masa-s. The names of the solar months originated from these constellation names.

### <notr>Nakshatra (नक्षत्रम्)</notr>

In Hindu tradition the ecliptic is divided into 27 parts of approximately 13°20', which correspond with 27 asterisms known as the nakshatra-s. In the earliest extant layers of the tradition this number is 28. This division is critical for ritual timing and for determining the birth lunar mansion. Since these asterisms define areas in the sky, they are also technically constellations.

surya-siddhanta and vedanga-jyotisha specify start coordinates for the 13°20' divisions using particular stars. See the penultimate paragraph on [this archive.org page](https://archive.org/stream/HistoryOfCalendarPanchangaCommittee/History-of-Calendar-Panchanga-Committee#page/n42/mode/1up).

The earliest complete nakshatra lists are found in the Taittiriya-shruti and the Atharvaveda, where they are recited as part of the nakshatreshti ritual which places the deities of the pantheon in these celestial compartments. Some scholars opine that by the early medieval period, nakshatra identification had changed to a small degree from the Vedic period.

In mythology the Nakshatras are considered to be the 27 daughters of Daksha Prajapati and wives of Chandra, the moon god. Daksha found that Soma overly favored Rohini over the others. For this, Daksha cursed him to wither away. Chandra then worshipped Shiva and received the boon that during a lunar month he would wax for fifteen days and wane for fifteen days.

The names of the lunar months originated from the 12 divisions in which the full moon or purnima occurs. Unlike a solar day, a lunar day or the moon's position in a nakshatra does not depend on sunrise or moonrise, so a lunar day may begin at any time of a solar day. Like other ancient cultures, Vedic people developed intercalation systems, most notably the insertion of an extra lunar month to correct the mismatch between lunar and solar year.

A few yogatara-s or prominent asterisms in the nakshatra-s lie slightly outside their constellation boundaries. Any resulting problem for ritual timing or astrology must then be solved by other means, and some people propose alternate identifications for such yogatara-s.

| Solar Months | Lunar Months | Modern | Season |
| --- | --- | --- | --- |
| Mesa | Vaishakha | Apr-May | Grishma (Summer) |
| Vrishabha | Jyeshtha | May-June | Grishma (Summer) |
| Mithuna | Ashadha | June-July | Varsha (Monsoon) |
| Karkata | Shravana | July-Aug | Varsha (Monsoon) |
| Simha | Bhadra | Aug-Sept | Sharad (Autumn) |
| Kanya | Ashvin | Sept-Oct | Sharad (Autumn) |
| Tula | Kartik | Oct-Nov | Hemanta (Pre-Winter) |
| Vrischika | Agahana | Nov-Dec | Hemanta (Pre-Winter) |
| Dhanu | Pausha | Dec-Jan | Shishira (Winter) |
| Makara | Magha | Jan-Feb | Shishira (Winter) |
| Kumbha | Phalguna | Feb-Mar | Vasanta (Spring) |
| Mina | Chaitra | Mar-Apr | Vasanta (Spring) |
| - | Adhika | Leap month | - |

### Navagraha - Nine planets

They observed that some celestial bodies move independently relative to the background stars and called them graha-s. The sun and moon are also treated as graha-s. The lunar nodes were likewise named as graha-s because they are important for calculating eclipses. The names of Vedic weekdays originated from these planetary names.

| Graha | Designation | Name of Solar days |
| --- | --- | --- |
| <notr>Surya</notr> (Sun) | Sun god | <notr>Ravivasara</notr> (Sunday) |
| <notr>Chandra/Soma</notr> (Moon) | Moon god | <notr>Somavasara</notr> (Monday) |
| <notr>Mangala</notr> (Mars) | God of war | <notr>Mangalavasara</notr> (Tuesday) |
| <notr>Budha</notr> (Mercury) | Son of Moon | <notr>Budhavasara</notr> (Wednesday) |
| <notr>Brihaspati/Guru</notr> (Jupiter) | Teacher of Gods | <notr>Guruvasara</notr> (Thursday) |
| <notr>Shukra</notr> (Venus) | Mentor of Demons | <notr>Shukravasara</notr> (Friday) |
| <notr>Shani</notr> (Saturn) | God of Misfortune | <notr>Shanivasara</notr> (Saturday) |
| <notr>Rahu</notr> | lunar node | - |
| <notr>Ketu</notr> | lunar node | - |

## Contributors

- Tanmoy Saha
- Contributors from the [sanskrit-coders community](https://github.com/sanskrit-coders).

## External links

- [Nakshatra](https://sa.wikipedia.org/wiki/नक्षत्रम्) article at Sanskrit Wikipedia
- [Nakshatra](http://en.wikipedia.org/wiki/Nakshatra) article at English Wikipedia
- [History Of Calendar-Panchanga Committee Report](https://archive.org/stream/HistoryOfCalendarPanchangaCommittee/History-of-Calendar-Panchanga-Committee#page/n77/mode/2up)
- [Possible period of the design of Nakshatras and Abhijit](http://www.tifr.res.in/~archaeo/papers/Others/Possible%20period%20of%20the%20design%20of%20Nakshatras.pdf)
"""


MIGRATION_NOTES_MD = """# Migration Notes

- Source folder: `vedic_sky_culture`
- Target folder: `vedic_25_codex`
- Reference schema: Stellarium 25 `indian` sky culture installed under `/Applications/Stellarium.app/Contents/Resources/skycultures/indian`
- Preserved active legacy constellation records from `constellationship.fab` as Stellarium 25 `constellations`
- Preserved active legacy `C01`-`C04` asterism records from `asterism_lines.fab` as Stellarium 25 `asterisms`
- Mirrored the active nakshatra constellation records `N01`-`N28` into `asterisms` to match Stellarium 25's `indian` package model
- Copied only the two legacy illustration assets referenced by `constellationsart.fab`
- `C01`, `C02`, and `C04` remain unlabeled because the legacy folder does not provide active labels for them
- `i3.json` is emitted as a compact mirror of `index.json` for compatibility with the installed Stellarium 25 package layout
- `zodiac` and `lunar_system` were not invented in this pass because the legacy source does not contain active Stellarium 25-ready definitions for them
"""


PRONOUNCE_MAP = {
    "N01": "Ashvini",
    "N02": "Bharani",
    "N03": "Krittika",
    "N04": "Rohini",
    "N05": "Mrigashira",
    "N06": "Ardra",
    "N07": "Punarvasu",
    "N08": "Pushya",
    "N09": "Ashlesha",
    "N10": "Magha",
    "N11": "Purva phalguni",
    "N12": "Uttara phalguni",
    "N13": "Hasta",
    "N14": "Chitra",
    "N15": "Svati",
    "N16": "Vishakhe",
    "N17": "Anuradha",
    "N18": "Jyeshtha",
    "N19": "Mula",
    "N20": "Purva ashadha",
    "N21": "Uttara ashadha",
    "N22": "Shravana",
    "N23": "Dhanishtha",
    "N24": "Shatabhisha",
    "N25": "Purva bhadrapada",
    "N26": "Uttara bhadrapada",
    "N27": "Revati",
    "N28": "Abhijit",
    "Shim": "Shimshumara",
    "Matsya": "Matsya",
    "C03": "Saptarshi",
}


def image_size(path: Path) -> list[int]:
    output = subprocess.check_output(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
        text=True,
    )
    width = int(re.search(r"pixelWidth: (\d+)", output).group(1))
    height = int(re.search(r"pixelHeight: (\d+)", output).group(1))
    return [width, height]


def parse_line_records(path: Path, legacy_prefix: bool) -> list[tuple[str, list[list[int]]]]:
    records = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        key = parts[0]
        values = list(map(int, parts[3:] if legacy_prefix else parts[2:]))
        if len(values) == 1:
            values = [values[0], values[0]]
        segments = []
        for index in range(0, len(values), 2):
            start, end = values[index], values[index + 1]
            if segments and segments[-1][-1] == start:
                segments[-1].append(end)
            else:
                segments.append([start, end])
        records.append((key, segments))
    return records


def parse_constellation_names(path: Path) -> dict[str, dict[str, str]]:
    names = {}
    pattern = re.compile(r'^(\S+)\s+"([^"]+)"\s+_\("([^"]*)"\)$')
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("##"):
            continue
        match = pattern.match(line)
        if match:
            key, native, english = match.groups()
            names[key] = {"native": native, "english": english}
    return names


def parse_asterism_names(path: Path) -> dict[str, str]:
    names = {}
    pattern = re.compile(r'^(\S+)\s+_\("([^"]*)"\)$')
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if match:
            key, native = match.groups()
            names[key] = native
    return names


def parse_star_names(path: Path) -> dict[str, list[dict[str, str]]]:
    names = {}
    pattern = re.compile(r'^(\d+)\|_\("([^"]+)"\)$')
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("##"):
            continue
        match = pattern.match(line)
        if match:
            hip, native = match.groups()
            names[f"HIP {hip}"] = [{"native": native, "english": native}]
    return names


def parse_planet_names(path: Path) -> dict[str, list[dict[str, str]]]:
    names = {}
    pattern = re.compile(r'^(\S+)\s+"([^"]+)"\s+_\("([^"]+)"\)$')
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("##"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        english_name, pronounce, native = match.groups()
        if native == ".":
            continue
        translator_comment = "the Moon" if english_name == "Moon" else english_name
        names[f"NAME {english_name}"] = [
            {
                "native": native,
                "pronounce": pronounce,
                "english": pronounce,
                "translators_comments": translator_comment,
            }
        ]
    return names


def parse_art(path: Path) -> dict[str, dict[str, object]]:
    art = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        key = parts[0]
        filename = parts[1]
        values = list(map(int, parts[2:]))
        anchors = []
        for index in range(0, len(values), 3):
            anchors.append(
                {
                    "pos": [values[index], values[index + 1]],
                    "hip": values[index + 2],
                }
            )
        art[key] = {
            "file": filename,
            "size": image_size(LEGACY / filename),
            "anchors": anchors,
        }
    return art


def build_named_object(
    object_id: str,
    key: str,
    lines: list[list[int]],
    name_map: dict[str, dict[str, str]] | None,
    art_map: dict[str, dict[str, object]],
) -> dict[str, object]:
    obj: dict[str, object] = {"id": object_id, "lines": lines}
    if key in art_map:
        art = art_map[key]
        obj["image"] = {
            "file": f"illustrations/{art['file']}",
            "size": art["size"],
            "anchors": art["anchors"],
        }
    if name_map and key in name_map:
        native = name_map[key]["native"]
        english = name_map[key]["english"]
        # Legacy files sometimes store transliteration in the second column and
        # Devanagari in the third; prefer the Devanagari form as the native label.
        if not re.search(r"[\u0900-\u097F]", native) and re.search(r"[\u0900-\u097F]", english):
            native, english = english, native
        common_name = {
            "native": native,
            "english": english,
        }
        pronounce = PRONOUNCE_MAP.get(key)
        if pronounce:
            common_name["pronounce"] = pronounce
        obj["common_name"] = common_name
    return obj


def build_output() -> dict[str, object]:
    constellation_records = parse_line_records(LEGACY / "constellationship.fab", legacy_prefix=False)
    asterism_records = parse_line_records(LEGACY / "asterism_lines.fab", legacy_prefix=True)
    constellation_names = parse_constellation_names(LEGACY / "constellation_names.eng.fab")
    asterism_names = parse_asterism_names(LEGACY / "asterism_names.eng.fab")
    art_map = parse_art(LEGACY / "constellationsart.fab")

    constellations = [
        build_named_object(
            f"CON vedic_25_codex {key}",
            key,
            lines,
            constellation_names,
            art_map,
        )
        for key, lines in constellation_records
    ]

    asterisms = [
        build_named_object(
            f"AST vedic_25_codex {key}",
            key,
            lines,
            constellation_names,
            art_map,
        )
        for key, lines in constellation_records
        if key.startswith("N")
    ]

    for key, lines in asterism_records:
        if key not in asterism_names:
            continue
        entry = build_named_object(
            f"AST vedic_25_codex {key}",
            key,
            lines,
            None,
            art_map,
        )
        common_name = {
            "native": asterism_names[key],
            "english": asterism_names[key],
        }
        pronounce = PRONOUNCE_MAP.get(key)
        if pronounce:
            common_name["pronounce"] = pronounce
        entry["common_name"] = common_name
        asterisms.append(entry)

    common_names = {}
    common_names.update(parse_star_names(LEGACY / "star_names.fab"))
    common_names.update(parse_planet_names(LEGACY / "planet_names.fab"))

    return {
        "id": "vedic_25_codex",
        "region": "Asia",
        "native_lang": "sa",
        "classification": ["traditional"],
        "fallback_to_international_names": False,
        "asterisms_comment": (
            "Port of legacy Stellarium 0.22 vedic_sky_culture. "
            "Active uncommented legacy records were preserved; unnamed legacy "
            "asterisms remain unlabeled."
        ),
        "asterisms": asterisms,
        "constellations": constellations,
        "common_names": common_names,
    }


def write_outputs() -> None:
    TARGET.mkdir(exist_ok=True)
    ILLUSTRATIONS.mkdir(exist_ok=True)

    data = build_output()
    (TARGET / "index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (TARGET / "i3.json").write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    (TARGET / "description.md").write_text(DESCRIPTION_MD, encoding="utf-8")
    (TARGET / "description.en.md").write_text(DESCRIPTION_MD, encoding="utf-8")
    (TARGET / "MIGRATION_NOTES.md").write_text(MIGRATION_NOTES_MD, encoding="utf-8")

    for filename in ("img_sisumara.png", "img_matsya.png"):
        shutil.copy2(LEGACY / filename, ILLUSTRATIONS / filename)


if __name__ == "__main__":
    write_outputs()
