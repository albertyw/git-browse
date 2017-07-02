Git Browse
==========

|PyPI| |Python Versions|

|Codeship Status for albertyw/git-browse| |Dependency Status| |Code
Climate| |Test Coverage|

Open repositories, directories, and files in the browser

This is a script that can be added as a gitconfig alias to easily browse
repositories on Git hosting services (e.g. github). It is built to model
[arcanist's] (https://github.com/phacility/arcanist)
`browse <https://github.com/phacility/arcanist/blob/master/src/workflow/ArcanistBrowseWorkflow.php>`__
command. It is specifically designed to have no dependencies so it
should be easily installable and very portable.

If you're looking to browse different github repositories, you might
like `hub
browse <https://github.com/github/hub/blob/master/commands/browse.go>`__.

Installation
------------

You need to first clone this repository somewhere on your system
(perhaps in your `dotfiles <https://github.com/albertyw/dotfiles>`__)
repository.

.. code:: bash

    git clone git@github.com:albertyw/git-browse $REPOSITORY_LOCATION
    git config --global \
        alias.browse \
        "!"$REPOSITORY_LOCATION"/git_browse/browse.py --path=\${GIT_PREFIX:-./}"

Usage
-----

::

    Usage: git browse [-h] [--path PATH] [--dry-run] [target]

If ``[target]`` is omitted, the root repository page will be opened. If
``[target]`` is a directory or file, then that object will be opened. If
``[target]`` is a commit hash, then that commit hash will be opened. If
``--path`` is available, then its value is be used to compute the
relative path to the current git repository If ``--dry-run`` is set,
then git-browse will only print out the target url instead of opening it
in a browser

Examples
~~~~~~~~

+----------------------------+----------------------------------------------------------------------------------------+
| Command                    | Opens                                                                                  |
+============================+========================================================================================+
| ``git browse``             | https://github.com/albertyw/git-browse                                                 |
+----------------------------+----------------------------------------------------------------------------------------+
| ``git browse README.rst``  | https://github.com/albertyw/git-browse/blob/master/README.rst                          |
+----------------------------+----------------------------------------------------------------------------------------+
| ``git browse git_browse``  | https://github.com/albertyw/git-browse/tree/master/git_browse/                         |
+----------------------------+----------------------------------------------------------------------------------------+
| ``git browse v1.1.1``      | https://github.com/albertyw/git-browse/commit/80b219dee0aaa86b378993cbf88511126b813c5f |
+----------------------------+----------------------------------------------------------------------------------------+

Development
-----------

.. code:: bash

    pip install -r requirements-test.txt
    coverage run setup.py test
    coverage report
    flake8

Publishing
----------

.. code:: bash

    sudo apt-get install pandoc
    pip install twine
    python setup.py sdist bdist_wheel
    twine upload dist/*

.. |PyPI| image:: https://img.shields.io/pypi/v/git-browse.svg
   :target: https://github.com/albertyw/git-browse
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/git-browse.svg
   :target: https://github.com/albertyw/git-browse
.. |Codeship Status for albertyw/git-browse| image:: https://codeship.com/projects/fbd67810-b952-0134-2c2e-166255a25182/status?branch=master
   :target: https://codeship.com/projects/194945
.. |Dependency Status| image:: https://gemnasium.com/badges/github.com/albertyw/git-browse.svg
   :target: https://gemnasium.com/github.com/albertyw/git-browse
.. |Code Climate| image:: https://codeclimate.com/github/albertyw/git-browse/badges/gpa.svg
   :target: https://codeclimate.com/github/albertyw/git-browse
.. |Test Coverage| image:: https://codeclimate.com/github/albertyw/git-browse/badges/coverage.svg
   :target: https://codeclimate.com/github/albertyw/git-browse/coverage

