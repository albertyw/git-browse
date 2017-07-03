#!/bin/bash

# Installs this repository so that you can run `git browse` from anywhere in
# your filesystem

REPOSITORY_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git config --global \
    alias.browse \
    "!"$REPOSITORY_LOCATION"/git_browse/browse.py --path=\${GIT_PREFIX:-./}"
