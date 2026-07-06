"""Configuration: observer locations and filesystem paths.

Paths are resolved as absolute paths relative to this file's location, so
this package works correctly regardless of the caller's current working
directory (unlike the original notebook, which assumed cwd == jyotisha/).
"""

from pathlib import Path

import astropy.units as u
from astropy.coordinates import EarthLocation

# chandra-marga/src/chandra_marga/config.py -> chandra-marga/ -> cahc-utils/
CAHC_UTILS_ROOT = Path(__file__).resolve().parents[3]
STEL_SCRIPTS_DIR = CAHC_UTILS_ROOT / "stel_scripts"
MOON_SHRANGA_DIR = STEL_SCRIPTS_DIR / "moon-shranga~"
CACHE_DIR = CAHC_UTILS_ROOT / "chandra-marga" / "cache_lunar~"

# Same locations as jyotisha/lunar-events-calculator.ipynb's LunarConfig.
LOCATIONS = {
    "kurukshetra": EarthLocation(lat=29.9697 * u.deg, lon=76.8786 * u.deg, height=0 * u.m),
    "delhi": EarthLocation(lat=28.6139 * u.deg, lon=77.2090 * u.deg, height=216 * u.m),
    "mumbai": EarthLocation(lat=19.0760 * u.deg, lon=72.8777 * u.deg, height=14 * u.m),
    "varanasi": EarthLocation(lat=25.3176 * u.deg, lon=82.9739 * u.deg, height=80 * u.m),
    "ujjain": EarthLocation(lat=23.1765 * u.deg, lon=75.7885 * u.deg, height=494 * u.m),
}

THITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
]


def get_location(name: str) -> EarthLocation:
    """Get a predefined observer location by name (defaults to kurukshetra)."""
    return LOCATIONS.get(name.lower(), LOCATIONS["kurukshetra"])


def thithi_name(thithi_number: int) -> str:
    if 1 <= thithi_number <= 15:
        return THITHI_NAMES[thithi_number - 1]
    return f"Invalid_Thithi_{thithi_number}"


def event_slug(paksha: str, thithi: int) -> str:
    """Build the conventional event key used both as a dict key in .inc files
    (e.g. 'shukla_pratipada', 'krishna_chaturdashi') and as a directory name
    under moon-shranga~/<mode>/<year>/. Matches the naming already used by
    jyotisha/lunar-events-calculator.ipynb's StellariumIntegration.

    Thithi 15 is special-cased: 'purnima' for shukla, 'amavasya' for krishna
    (matching the existing amavasya/purnima dict keys, rather than a
    'shukla_purnima'/'krishna_amavasya' compound name).
    """
    paksha = paksha.lower()
    if thithi == 15:
        return "purnima" if paksha == "shukla" else "amavasya"
    return f"{paksha}_{thithi_name(thithi).lower()}"
