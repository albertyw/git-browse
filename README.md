Git Browse
==========

[![PyPI](https://img.shields.io/pypi/v/git-browse)](https://pypi.org/project/git-browse/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/git-browse)
![PyPI - License](https://img.shields.io/pypi/l/git-browse)

[![Build Status](https://drone.albertyw.com/api/badges/albertyw/git-browse/status.svg)](https://drone.albertyw.com/albertyw/git-browse)
[![Maintainability](https://qlty.sh/gh/albertyw/projects/git-browse/maintainability.svg)](https://qlty.sh/gh/albertyw/projects/git-browse)
[![Code Coverage](https://qlty.sh/gh/albertyw/projects/git-browse/coverage.svg)](https://qlty.sh/gh/albertyw/projects/git-browse)


Open git repositories, commits, directories, and files in the browser. See also,
[git-reviewers](https://github.com/albertyw/git-reviewer).

![Preview](https://user-images.githubusercontent.com/3151040/28054498-e7cb0746-65c9-11e7-882e-dbf612f5b075.gif)

This script can be added as a gitconfig alias to easily browse
repositories on Git hosting services (e.g. github). It is built to model
[arcanist's browse](https://github.com/phacility/arcanist/blob/master/src/workflow/ArcanistBrowseWorkflow.php)
command. It is specifically designed to have no
dependencies so it should be easily installable and very portable.

Git Browse supports opening git repositories, commits, directories, and files:

 - [Bitbucket](https://bitbucket.org/)
 - [Github](https://github.com/)
 - [Gitlab](https://gitlab.com/)
 - [GoDocs](https://godocs.io/)
 - [Phabricator](https://www.phacility.com/phabricator/)
 - [Sourcegraph](https://about.sourcegraph.com/)

Installation
------------

### HomeBrew (preferred for MacOS)

If you use Homebrew, you can install git-browse through the
[homebrew-albertyw tap](https://github.com/albertyw/homebrew-albertyw>):

```bash
brew install albertyw/albertyw/git-browse
```

### Manual

If you don't use Homebrew, first clone this repository to somewhere on
your system (perhaps in your [dotfiles](https://github.com/albertyw/dotfiles) repository), then run
`<REPOSITORY_LOCATION>/install.sh`.

Usage
-----

```
$ git browse -h
'browse' is aliased to '!~/.dotfiles/scripts/git/git-browse/git_browse/browse.py --path=${GIT_PREFIX:-./}'
usage: browse.py [-h] [--path PATH] [-d] [-c] [-s] [-g] [-v] [target]

Open repositories, directories, and files in the browser. https://github.com/albertyw/git-browse

positional arguments:
  target             file, directory, git hash, or git branch you wish to browse

optional arguments:
  -h, --help         show this help message and exit
  --path PATH        relative path to the current git repository
  -d, --dry-run      Do not open the url in the brower, and only print to stdout
  -c, --copy         Copy url to clipboard, if available
  -s, --sourcegraph  Open objects in sourcegraph
  -g, --godocs       Open objects in godocs
  -v, --version      show program's version number and exit
```

### Examples

| Command                           | Opens                                                                                    |
|-----------------------------------|------------------------------------------------------------------------------------------|
| `git browse`                      | <https://github.com/albertyw/git-browse>                                                 |
| `git browse README.md`            | <https://github.com/albertyw/git-browse/blob/master/README.md>                           |
| `git browse git_browse`           | <https://github.com/albertyw/git-browse/tree/master/git_browse/>                         |
| `git browse v1.1.1`               | <https://github.com/albertyw/git-browse/commit/80b219dee0aaa86b378993cbf88511126b813c5f> |
| `git browse --sourcegraph`        | <https://sourcegraph.com/github.com/albertyw/git-browse>
| `git browse --godocs`             | <https://godocs.io/github.com/albertyw/git-browse>
| `git browse` for Bitbucket        | <https://bitbucket.org/albertyw/asdf>
| `git browse` for Gitlab           | <https://gitlab.com/albertyw/asdf>
| `git browse` for Uber Phabricator | <https://code.uberinternal.com/diffusion/rASDF/repository/master/>

Related Projects
----------------

- [git-brws](https://github.com/rhysd/git-brws)
- [hub browse](https://hub.github.com/)
- [git open](https://github.com/paulirish/git-open)
- [open-browser-github.vim](https://github.com/tyru/open-browser-github.vim)

Development
-----------

```bash
pip install -e .[test]
ruff check .
mypy .
coverage run -m unittest
coverage report
```

Publishing
----------

1.  Update changelog and `__version__` variable with a semantic version
2.  Commit changes, create a version tag, and push both
3.  Update [albertyw/homebrew-albertyw](https://github.com/albertyw/homebrew-albertyw)
