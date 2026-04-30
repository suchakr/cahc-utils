from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
LAB_ROOT = REPO_ROOT / "lab"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
EXPLORATIONS_ROOT = REPO_ROOT / "explorations"
MEMORY_ROOT = REPO_ROOT / "memory"
UPSTREAM_DATASETS_ROOT = (REPO_ROOT / ".." / "datasets").resolve()


def lab_path(*parts: str) -> Path:
    return LAB_ROOT.joinpath(*parts)


def upstream_dataset_path(*parts: str) -> Path:
    return UPSTREAM_DATASETS_ROOT.joinpath(*parts)
