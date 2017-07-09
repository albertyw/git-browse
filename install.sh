#!/bin/bash

# Installs this repository so that you can run `git browse` from anywhere in
# your filesystem

# Check if python 3 is installed
if ! command -v python3 > /dev/null 2>&1; then
    echo "You must install python 3 to use git browse"
    echo "On OSX, use 'brew install python3'"
    echo "On Ubuntu/Debian, use 'sudo apt install python3'"
fi

REPOSITORY_LOCATION="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

git config --global \
    alias.browse \
    "!"$REPOSITORY_LOCATION"/git_browse/browse.py --path=\${GIT_PREFIX:-./}"
