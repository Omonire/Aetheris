#!/usr/bin/env bash
# Aetheris launcher for macOS and Linux.
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

export FLASK_DEBUG="${FLASK_DEBUG:-1}"
export PORT="${PORT:-5000}"

echo "Starting Aetheris on http://127.0.0.1:${PORT}"
exec python app.py
