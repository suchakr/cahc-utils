#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
REPO_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORK_VIDEOS_DIR="$REPO_ROOT/out/work-videos"
HIRES_DIR="$WORK_VIDEOS_DIR/hires"
WEB_DIR="$WORK_VIDEOS_DIR/web"
FINAL_DIR="$REPO_ROOT/out"

mkdir -p "$WEB_DIR"

find_input_videos() {
  found=0

  for f in "$HIRES_DIR"/*.posttrim.mp4; do
    [ -f "$f" ] || continue
    found=1
    printf '%s\n' "$f"
  done

  for f in "$HIRES_DIR"/*.mp4; do
    [ -f "$f" ] || continue
    case "$f" in
      *.pretrim.mp4|*.posttrim.mp4) continue ;;
    esac

    stem=$(basename "$f" .mp4)
    [ -f "$HIRES_DIR/$stem.posttrim.mp4" ] && continue

    found=1
    printf '%s\n' "$f"
  done

  [ "$found" -eq 1 ]
}

find_input_videos | while IFS= read -r f
do
  case "$f" in
    *.posttrim.mp4) name=$(basename "$f" .posttrim.mp4) ;;
    *.mp4) name=$(basename "$f" .mp4) ;;
    *) continue ;;
  esac
  web_out="$WEB_DIR/${name}.mp4"
  final_out="$FINAL_DIR/${name}.mp4"

  echo "-> $name"

  # 1. Compress from hires/ to web/ (if not already done)
  if [ ! -f "$web_out" ]; then
    echo "  Compressing to $web_out..."
    ffmpeg -y -i "$f" -vcodec libx264 -crf 30 -preset slow -vf "scale=-2:720" -r 24 -pix_fmt yuv420p -an "$web_out" 2>&1 | tail -2
  fi

  # 2. Determine how many seconds to trim off the start for this specific video
  case "$name" in
    s11) trim="7" ;;
    s12) trim="5.5" ;;
    s13) trim="6" ;;
    s14) trim="7" ;;
    s21) trim="7" ;;
    s22) trim="5" ;;
    s23) trim="10" ;;
    s24) trim="7" ;;
    s25) trim="7" ;;
    *)   trim="0" ;;
  esac

  # 3. Trim from web/ to out/ (if not already done)
  if [ ! -f "$final_out" ]; then
    echo "  Trimming ${trim}s -> $final_out"
    if [ "$trim" = "0" ]; then
      cp "$web_out" "$final_out"
    else
      ffmpeg -y -ss "$trim" -i "$web_out" -c copy "$final_out" 2>&1 | tail -2
    fi
  else
    echo "  Final $final_out already exists. Skipping trim."
  fi

done
