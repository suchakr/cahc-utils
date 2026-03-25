#!/bin/sh

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
SOURCE_DIR="$REPO_ROOT/out"
PICS_DIR="$REPO_ROOT/pics"
TARGET_DIR="/Users/sunder/projects/cahcblr.github.io/assets/talks/2026-03-23-iabc"

echo "Staging built assets from $SOURCE_DIR to $TARGET_DIR..."

mkdir -p "$TARGET_DIR"

staged_any=0
for path in "$SOURCE_DIR"/*.mp4 "$SOURCE_DIR"/*.pdf "$SOURCE_DIR"/*.html; do
  [ -e "$path" ] || continue
  cp "$path" "$TARGET_DIR/"
  staged_any=1
done

for path in "$PICS_DIR"/*; do
  [ -e "$path" ] || continue
  cp "$path" "$TARGET_DIR/"
  staged_any=1
done

if [ "$staged_any" -eq 0 ]; then
  echo "No staged assets found under $SOURCE_DIR or $PICS_DIR." >&2
  echo "Build slides or render videos first, then rerun." >&2
  exit 1
fi

echo "Done staging!"
echo ""
echo "---------------------------------------------------------"
echo "NEXT STEPS:"
echo "1. cd /Users/sunder/projects/cahcblr.github.io"
echo "2. Run 'bundle exec jekyll serve' to validate locally."
echo "3. Check the new post and assets at http://localhost:4000"
echo "4. Once validated, 'git add', 'git commit', and 'git push'."
echo "---------------------------------------------------------"
