#!/bin/bash
set -e

PRJ='standalone_server'
VENV="_py_env"

if [ ! -d "$VENV" ]; then
  echo "Creating '$VENV'..."
  pyvenv "$VENV"
fi

test -e "$VENV/bin/pip" || { echo "FATAL: missing pip from venv!"; exit 1; }

echo "Installing dependencies..."
"$VENV/bin/pip" install -r djlfs_batch/requirements.txt

if [ -f $PRJ/db.sqlite3 ]; then
  echo "Migrating DB..."
else
  echo "Creating DB '$PRJ/db.sqlite3'..."
fi
"$VENV/bin/python" $PRJ/manage.py migrate

echo ""
echo "Installed and ready."
echo "To clean up and start again from a pristine state, simply:"
echo "  rm -rf _py_env"
echo "  rm -f $PRJ/db.sqlite3"
echo ""
echo "Running test server..."
"$VENV/bin/python" $PRJ/manage.py runserver
