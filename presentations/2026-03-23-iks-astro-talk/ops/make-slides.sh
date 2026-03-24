#!/opt/homebrew/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

MARP_BIN="${MARP_BIN:-/opt/homebrew/bin/marp}"
OUT_DIR="${OUT_DIR:-$REPO_ROOT/out}"

if [[ ! -x "$MARP_BIN" ]]; then
  echo "marp not found at: $MARP_BIN" >&2
  echo "Set MARP_BIN=/path/to/marp and rerun." >&2
  exit 1
fi

build_one() {
  local stem="$1"
  local src="${REPO_ROOT}/${stem}.md"
  local html="${OUT_DIR}/${stem}.html"
  local pdf="${OUT_DIR}/${stem}.pdf"

  echo "Building ${stem}.md -> $html"
  "$MARP_BIN" --html --allow-local-files "$src" -o "$html"

  echo "Building ${stem}.md -> $pdf"
  "$MARP_BIN" --pdf --allow-local-files "$src" -o "$pdf"
}

mkdir -p "$OUT_DIR"

build_one "slides-session-1"
build_one "slides-session-2"

echo
echo "Done:"
echo "  ${OUT_DIR}/slides-session-1.html"
echo "  ${OUT_DIR}/slides-session-1.pdf"
echo "  ${OUT_DIR}/slides-session-2.html"
echo "  ${OUT_DIR}/slides-session-2.pdf"
