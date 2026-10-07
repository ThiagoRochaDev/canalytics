#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/python -m pip install -r apps/api/requirements.lock
  npm --prefix apps/web ci
fi
if [ ! -f apps/web/dist/index.html ]; then
  npm --prefix apps/web run build
fi
printf 'Canalytics: http://localhost:8093\n'
exec .venv/bin/python -m uvicorn canalytics.main:app --app-dir apps/api --host 127.0.0.1 --port 8093 --workers 1 --no-access-log
