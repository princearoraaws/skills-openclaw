#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="${1:-$HOME/ocmemog}"
REPO_URL="https://github.com/simbimbo/ocmemog.git"
if [ -d "$REPO_DIR/.git" ]; then
  git -C "$REPO_DIR" pull --ff-only
else
  git clone "$REPO_URL" "$REPO_DIR"
fi
python3 -m venv "$REPO_DIR/.venv"
"$REPO_DIR/.venv/bin/pip" install -r "$REPO_DIR/requirements.txt"
echo "ocmemog repo prepared at $REPO_DIR"
echo "Next: start sidecar and run: openclaw plugins install -l $REPO_DIR && openclaw plugins enable memory-ocmemog"
