Git Browse
==========

[ ![Codeship Status for albertyw/git-browse](https://codeship.com/projects/fbd67810-b952-0134-2c2e-166255a25182/status?branch=master)](https://codeship.com/projects/194945)
[![Dependency Status](https://gemnasium.com/badges/github.com/albertyw/git-browse.svg)](https://gemnasium.com/github.com/albertyw/git-browse)

Open repositories, directories, and files in the browser

This is a script that can be added as a gitconfig alias to easily browse
repositories on Git hosting services (e.g. github).  It is built to model
[arcanist's] (https://github.com/phacility/arcanist)
[browse](https://github.com/phacility/arcanist/blob/master/src/workflow/ArcanistBrowseWorkflow.php)
command.

Installation
------------

```bash
TODO
```

Usage
-----

```
Usage: python browse.py [object]
```

Development
-----------

```bash
pip install coverage flake8
flake8
coverage run -m unittest
coverage report
```
