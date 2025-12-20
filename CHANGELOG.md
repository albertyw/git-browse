Changelog
=========

v2.15.0 (2025-12-17)
--------------------

 - Support opening Uber Phabricator repositories in Github
 - Add support for python 3.14
 - Update dependencies
 - Fix test warnings/deprecations
 - Switch from codeclimate to qlty


v2.14.2 (2025-06-08)
--------------------

 - Support reading Uber arcconfig files with `conduit.uri`s
 - Update dependencies


v2.14.1 (2025-04-01)
--------------------

 - Fix opening uber godocs URLs
 - Update dependencies
 - Backfill test coverage


v2.14.0 (2025-03-03)
--------------------

 - Support browsing Uber Github URLs
 - Support browsing Uber ObjectConfig URLs
 - Update dependencies


v2.13.11 (2024-10-26)
---------------------

 - Add support for python 3.13
 - Update dependencies
 - Remove pyup


v2.13.10 (2024-04-19)
---------------------

 - Fix reading uber java monorepo sourcegraph URLs
 - Update dependencies


v2.13.9 (2024-01-28)
--------------------

 - Switch from deprecated sourcegraph.uberinternal.com to sg.uberinternal.com


v2.13.8 (2024-01-28)
--------------------

 - Update dependencies
 - Various cleanup


v2.13.7 (2023-10-15)
--------------------

 - Switch from setup.py to pyproject.toml
 - Update dependencies


v2.13.6 (2023-05-08)
--------------------

 - Update dependencies
 - Explicitly support python 3.11
 - Cleanup


v2.13.5 (2022-10-05)
--------------------

 - Switch from pkg.go.dev to godocs.io
 - Cleanup
 - Update dependencies


v2.13.4 (2022-07-30)
--------------------

 - Update python packaging
 - Test python packaging
 - Update dependencies


v2.13.3 (2022-02-15)
--------------------

 - Remove possibility of double slashes when generating phabricator URLs
 - Drop support for python 3.6; add support for python 3.10
 - Update dependencies


v2.13.2 (2021-10-02)
--------------------

 - Default to sourcegraph links if phabricator configuration is not available
 - Update readme


v2.13.1 (2021-09-05)
--------------------

 - Try to read default branch from git configuration for generating bitbucket, github, and gitlab URLs


v2.13.0 (2021-09-03)
--------------------

 - Add support for gitlab repositories


v2.12.1 (2021-08-17)
--------------------

 - Refactor browse.py into multiple files


v2.12.0 (2021-08-03)
--------------------

 - Removed support for opening Phabricator Differentials and Maniphest tasks
 - Remove dependency on Arcanist when opening Phabricator URLs
 - Many refactors


v2.11.0 (2021-07-15)
--------------------

 - Add support for bitbucket repositories
 - Update dependencies


v2.10.0 (2021-06-14)
--------------------

 - Add support for running git browse on git submodules
 - Update dependencies
 - Other cleanup


v2.9.2 (2021-02-22)
-------------------

 - Switch CI from codeship to Drone
 - Update dependencies


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
