"""A small smoke-test to validate the developer environment quickly.

It imports common third-party libraries and local helper modules used by notebooks.
Run inside the venv after `pip install -r requirements.txt`.
"""

import importlib
import sys

# third-party packages to check
pkgs = [
    'astropy', 'pandas', 'numpy', 'matplotlib', 'scipy', 'seaborn', 'IPython',
    'astropy', 'astroplan', 'joblib', 'tqdm', 'sympy', 'PIL',
]

# local modules to sanity-check import path
local_mods = [
    'JdUtils', 'NaksUtils', 'PlanetPos', 'NasaMoonScrapeUtils', 'vgj_ac_rs', 'SCPUtils'
]

errors = []
for name in pkgs:
    try:
        importlib.import_module(name)
        print(f'OK: {name}')
    except Exception as e:
        errors.append((name, str(e)))

print('\nChecking local modules (from current directory):')
# add this script's parent (jyotisha) to sys.path
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

for name in local_mods:
    try:
        importlib.import_module(name)
        print(f'OK: local {name}')
    except Exception as e:
        errors.append((name, str(e)))

print('\nSummary:')
if not errors:
    print('All imports succeeded. Environment looks good for basic notebook work.')
else:
    print('Some imports failed (displaying up to 10):')
    for n, msg in errors[:10]:
        print(f'  FAIL: {n} -> {msg}')
    raise SystemExit(1)
