Changelog
=========

v2.9.1 (2021-01-13)
-------------------

 - Change how browsing phabricator urls works.  Instead of entirely offloading the work to arcanist, read arcanist's output.
 - Significant refactors to simplify code and update to more modern python


v2.9.0 (2021-01-12)
-------------------

 - Add a `--copy` option to copy urls to clipboard
 - Allow opening urls in browser on any support platform
 - Various cleanup


v2.8.3 (2020-10-20)
-------------------

 - Fix being able to run on a git repository with multiple fetch configs


v2.8.2 (2020-10-18)
-------------------

 - Fix PyPI description format


v2.8.1 (2020-10-18)
-------------------

 - Dependency updates
 - Switch readme to markdown
 - Explicitly specify python typing in package classifier


v2.8.0 (2020-07-26)
-------------------

 - Add support for opening repositories and directories in godocs
 - Add tests


v2.7.3 (2020-07-08)
-------------------

 - Add full type annotations
 - Many refactors
 - Dependency updates
 - Readme updates


v2.7.2 (2020-02-23)
-------------------

 - Update dependencies
 - Use the public sourcegraph for github repositories


v2.7.1 (2019-02-02)
-------------------

 - Update test dependencies
 - Refactors


v2.7.0 (2018-08-18)
-------------------

 - Add support for sourcegraph
 - Dependency updates


v2.6.0 (2018-06-26)
-------------------

 - Switch from gemnasium to pyup
 - Support code.uber.internal repositories


v2.5.1 (2018-05-05)
-------------------

 - Dependency updates


v2.5.0 (2018-02-23)
-------------------

 - Support Uber https gitolite urls
 - Update documentation
 - Update dependencies


v2.4.3 (2017-12-24)
-------------------

 - Make install.sh accept a path for browse.py
 - Update dependencies


v2.4.2 (2017-11-04)
-------------------

 - Add type annotations and some minor refactoring
 - Update dependencies


v2.4.1 (2017-08-30)
-------------------

 - Support `browse.py -v`
 - Update documentation


v2.4.0 (2017-07-07)
-------------------

 - Add an installation script
 - Bugfix for opening gitolite repositories
 - Dependency cleanup


v2.3.2 (2017-07-02)
-------------------

 - Switch README to rst
 - Add info to README


v2.3.1 (2017-06-03)
-------------------

 - Support phabricator repositories without arcconfig


v2.3.0 (2017-06-03)
-------------------

 - Add support for only printing out URL instead of opening browser in `-d`/`--dry-run` flag
 - Add help info in `-h`/`--help` flag
 - Updated dependencies


v2.2.0 (2017-04-01)
-------------------

 - Support for generic phabricator hosts
 - Better documentation
 - Better error handling
 - Minor refactors and more tests


v2.1.0 (2017-02-19)
-------------------

 - Support browsing commit hashes
 - Refactors
 - Fix dependency on pypandoc


v2.0.1 (2017-02-11)
-------------------

 - Update development dependencies
 - Fix formatting on PyPI by converting markdown readme to reStructuredText
 - Officially support python 3.6


v2.0.0 (2017-02-04)
-------------------

 - First release as a python package
 - Major refactors of repository structure
 - Bring test coverage back to 100%


v1.2.0 (2017-01-24)
-------------------

 - Add support for uber phabricator through arcanist client


v1.1.1 (2017-01-24)
-------------------

 - Minor refactors and fixes


v1.1.0 (2017-01-20)
-------------------

 - Open git-browsed urls in web browser, according to python's
   https://docs.python.org/3/library/webbrowser.html
 - Add tests and debugging


v1.0.1 (2017-01-19)
-------------------

 - Fix shebang in browse.py to make it more portable across environments


v1.0.0 (2017-01-10)
-------------------

 - Initial release
 - Supports reading github repositories
 - Supports outputting the URL to CLI
 - Supports git alias
 - 100% test coverage
