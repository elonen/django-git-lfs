#!/bin/bash
set -e

VENV="_py_env"

if [ ! -d "$VENV" ]; then
  echo "Creating '$VENV'..."
  pyvenv "$VENV"
fi

test -e "$VENV/bin/pip" || { echo "FATAL: missing pip from venv!"; exit 1; }

echo "Installing dependencies..."
"$VENV/bin/pip" install -r requirements.txt

if [ -f example/db.sqlite3 ]; then
  echo "Migrating DB..."
else
  echo "Creating DB 'example/db.sqlite3'..."
fi
"$VENV/bin/python" example/manage.py migrate

echo ""
echo "Installed and ready."
echo "To clean up and start again from a pristine state, simply:"
echo "  rm -rf _py_env"
echo "  rm -f example/db.sqlite3"
echo ""
echo "Running test server..."
"$VENV/bin/python" example/manage.py runserver
