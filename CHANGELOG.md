Changelog
=========

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
