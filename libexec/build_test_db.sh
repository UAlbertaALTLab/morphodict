#!/bin/bash

if [ -z "${PIPENV_ACTIVE}" ]; then
    echo "Error: This script must be run in a pipenv." 1>&2
    exit 1
fi

set -eu

export USE_TEST_DB=True

DIR="$(dirname -- "${0}")"

"${DIR}/../CreeDictionary/manage.py" migrate
"${DIR}/../CreeDictionary/manage.py" xmlimport import \
    "${DIR}/../CreeDictionary/res/test_dictionaries/crkeng.xml"

