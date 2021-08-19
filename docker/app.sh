#!/bin/bash

set -eu

PROG="$(basename -- "${0}")"

if (( $# != 1 )); then
    echo "Error: Missing required argument" 1>&2
    echo "Usage: ${PROG} MORPHODICT_LANG_PAIR" 1>&2
    exit 1
fi
MORPHODICT_LANG_PAIR="${1}"

export DJANGO_SETTINGS_MODULE="${MORPHODICT_LANG_PAIR}.site.settings"

# In production, allow any created files/directories to be group-writeable so
# that both the morphodict and morphodict-run users can modify them.
umask 0002

# uwsgi --http-socket is intended to be used behind, e.g., nginx
exec uwsgi --http-socket :8000 \
    --stats :9191 \
    --wsgi-file src/morphodict/site/wsgi.py \
    src/morphodict/site/uwsgi.ini
