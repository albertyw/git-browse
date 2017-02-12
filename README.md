Git Browse
==========

[![PyPI](https://img.shields.io/pypi/v/git-browse.svg)](https://github.com/albertyw/git-browse)
[![PyPI](https://img.shields.io/pypi/pyversions/git-browse.svg)]()

[ ![Codeship Status for albertyw/git-browse](https://codeship.com/projects/fbd67810-b952-0134-2c2e-166255a25182/status?branch=master)](https://codeship.com/projects/194945)
[![Dependency Status](https://gemnasium.com/badges/github.com/albertyw/git-browse.svg)](https://gemnasium.com/github.com/albertyw/git-browse)
[![Code Climate](https://codeclimate.com/github/albertyw/git-browse/badges/gpa.svg)](https://codeclimate.com/github/albertyw/git-browse)
[![Test Coverage](https://codeclimate.com/github/albertyw/git-browse/badges/coverage.svg)](https://codeclimate.com/github/albertyw/git-browse/coverage)

Open repositories, directories, and files in the browser

This is a script that can be added as a gitconfig alias to easily browse
repositories on Git hosting services (e.g. github).  It is built to model
[arcanist's] (https://github.com/phacility/arcanist)
[browse](https://github.com/phacility/arcanist/blob/master/src/workflow/ArcanistBrowseWorkflow.php)
command.  It is specifically designed to have no dependencies so it should be
easily installable and very portable.

Installation
------------

You need to first clone this repository somewhere on your system (perhaps in
your [dotfiles](https://github.com/albertyw/dotfiles)) repository.

```bash
git clone git@github.com:albertyw/git-browse $REPOSITORY_LOCATION
git config --global \
    alias.browse \
    "!"$REPOSITORY_LOCATION"/git_browse/browse.py --path=\${GIT_PREFIX:-./}"
```

Usage
-----

```
Usage: git browse [object]
```

If `[object]` is omitted, the root repository page will be opened.
If `[object]` is a directory or file, then that object will be opened.

Development
-----------

```bash
pip install -r requirements-test.txt
coverage run setup.py test
coverage report
flake8
```

Publishing
----------

```bash
sudo apt-get install pandoc
pip install twine pypandoc
python setup.py sdist bdist_wheel
twine upload dist/*
```
