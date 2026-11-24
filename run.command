#!/bin/zsh
set -e
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then echo "Установите Python 3 (python.org)"; read '?Нажмите Enter...'; exit 1; fi
if [ ! -f .venv/bin/python ]; then python3 -m venv .venv; fi
source .venv/bin/activate
if ! python -c 'import flask, waitress' >/dev/null 2>&1; then python -m pip install -r requirements.txt; fi
python tools/start.py
