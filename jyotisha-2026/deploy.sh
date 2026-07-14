#!/usr/bin/env bash
set -euo pipefail

PUBLISH_DIR="lab"
DEFAULT_PORT="8888"

usage() {
  cat <<'EOF'
Usage:
  ./deploy.sh [stage|prod|local] [options] [-- netlify args...]

Modes:
  stage, --stage          Create a Netlify preview deploy. Default mode.
  prod, --prod            Deploy to production.
  local, --local          Start local Netlify dev server.
  dev, --dev              Alias for local.

Options:
  -p, --port PORT         Local server port. Default: 8888.
  -n, --dry-run           Print the resolved command without running it.
  -h, --help              Show this help.

Examples:
  ./deploy.sh
  ./deploy.sh stage
  ./deploy.sh --prod
  ./deploy.sh local --port 8899
  ./deploy.sh --stage -- --message "preview"
EOF
}

mode="stage"
port="$DEFAULT_PORT"
dry_run=0
passthrough=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    prod|--prod)
      mode="prod"
      shift
      ;;
    stage|--stage)
      mode="stage"
      shift
      ;;
    local|--local|dev|--dev)
      mode="local"
      shift
      ;;
    -p|--port)
      if [[ $# -lt 2 || "$2" == -* ]]; then
        echo "Missing port after $1" >&2
        exit 2
      fi
      port="$2"
      shift 2
      ;;
    -n|--dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      passthrough=("$@")
      break
      ;;
    *)
      passthrough+=("$1")
      shift
      ;;
  esac
done

if [[ ! "$port" =~ ^[0-9]+$ || "$port" -lt 1 || "$port" -gt 65535 ]]; then
  echo "Invalid port: $port" >&2
  exit 2
fi

run_command() {
  if [[ "$dry_run" -eq 1 ]]; then
    printf 'Resolved command:'
    printf ' %q' "$@"
    printf '\n'
    return 0
  fi
  exec "$@"
}

port_listener() {
  local check_port="$1"
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"$check_port" -sTCP:LISTEN 2>/dev/null | sed -n '2p' || true
  fi
  return 0
}

port_is_busy() {
  local check_port="$1"
  local listener
  listener="$(port_listener "$check_port")"
  if [[ -n "$listener" ]]; then
    printf '%s\n' "$listener"
    return 0
  fi
  if command -v nc >/dev/null 2>&1 && nc -z 127.0.0.1 "$check_port" >/dev/null 2>&1; then
    return 0
  fi
  curl -fsS --max-time 2 "http://127.0.0.1:${check_port}/" >/dev/null 2>&1
}

case "$mode" in
  prod)
    run_command netlify deploy --dir "$PUBLISH_DIR" --prod "${passthrough[@]}"
    ;;
  stage)
    run_command netlify deploy --dir "$PUBLISH_DIR" "${passthrough[@]}"
    ;;
  local)
    local_url="http://127.0.0.1:${port}/"
    if [[ "$dry_run" -eq 1 ]]; then
      run_command netlify dev --dir "$PUBLISH_DIR" --port "$port" "${passthrough[@]}"
      exit 0
    fi
    listener="$(port_listener "$port")"
    if [[ -n "$listener" ]]; then
      echo "A local server is already listening at $local_url"
      echo "$listener"
      exit 0
    fi
    if port_is_busy "$port" >/dev/null; then
      echo "A local server is already listening at $local_url"
      exit 0
    fi
    echo "Starting local Netlify dev server at $local_url"
    run_command netlify dev --dir "$PUBLISH_DIR" --port "$port" "${passthrough[@]}"
    ;;
esac
