Git Browse
==========

Open repositories, directories, and files in the browser. See also,
[git-reviewers][].

![image][]

This is a script that can be added as a gitconfig alias to easily browse
repositories on Git hosting services (e.g. github). It is built to model
[arcanist's browse][] command. It is specifically designed to have no
dependencies so it should be easily installable and very portable.

If you're looking to browse different github repositories, you might
like [hub browse][].

Installation
------------

### HomeBrew (preferred for MacOS)

If you use Homebrew, you can install git-browse through the
[homebrew-albertyw tap][]:

    brew install albertyw/albertyw/git-browse

### Manual

If you don't use Homebrew, first clone this repository to somewhere on
your system (perhaps in your [dotfiles][] repository), then run
`<REPOSITORY_LOCATION>/install.sh`.

Usage
-----

    $ git browse -h
    'browse' is aliased to '!~/.dotfiles/scripts/git/git-browse/git_browse/browse.py --path=${GIT_PREFIX:-./}'
    usage: browse.py [-h] [--path PATH] [-d] [-s] [-v] [target]

    Open repositories, directories, and files in the browser.
    https://github.com/albertyw/git-browse

    positional arguments:
      target             file, directory, git hash, or git branch you wish to
                         browse

    optional arguments:
      -h, --help         show this help message and exit
      --path PATH        relative path to the current git repository
      -d, --dry-run      Do not open the url in the brower, and only print to
                         stdout
      -s, --sourcegraph  Open objects in sourcegraph
      -v, --version      show program's version number and exit

### Examples

| Command                 | Opens                                                           |
|-------------------------|-----------------------------------------------------------------|
| `git browse`            | <https://github.com/albertyw/git-browse>                        |
| `git browse README.rst` | <https://github.com/albertyw/git-browse/blob/master/README.rst> |

+----------------------------+---------

  [git-reviewers]:
  [image]: https://user-images.githubusercontent.com/3151040/28054498-e7cb0746-65c9-11e7-882e-dbf612f5b075.gif
  [arcanist's browse]: https://github.com/phacility/arcanist/blob/master/src/workflow/ArcanistBrowseWorkflow.php
  [hub browse]: https://github.com/github/hub/blob/master/commands/browse.go
  [homebrew-albertyw tap]: https://github.com/albertyw/homebrew-albertyw
  [dotfiles]: https://github.com/albertyw/dotfiles
