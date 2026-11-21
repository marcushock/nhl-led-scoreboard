#!/bin/bash
# Interactive config.json setup (Pi Zero and others without nhl_setup).

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${DIR}/.." || exit 1

PYTHON="python3"
if [ -x "$HOME/nhlsb-venv/bin/python3" ]; then
  PYTHON="$HOME/nhlsb-venv/bin/python3"
fi

exec "$PYTHON" scripts/sbtools/config_setup.py "$@"