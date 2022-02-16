#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

from git_browse import browse

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='git-browse',

    version=browse.__version__,

    description='Open repositories, directories, and files in the browser',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/albertyw/git-browse',

    author='Albert Wang',
    author_email='git@albertyw.com',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development :: Version Control',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',

        'Typing :: Typed',
    ],

    keywords='github phabricator repository browser',

    package_data={"git_browse": ["py.typed"]},
    packages=find_packages("git_browse", exclude=["tests"]),

    py_modules=["git_browse.browse"],

    install_requires=[],

    test_suite="git_browse.tests",

    # testing requires flake8 and coverage but they're listed separately
    # because they need to wrap setup.py
    extras_require={
        'dev': [],
        'test': [],
    },

    entry_points={
        'console_scripts': [
            'git_browse=git_browse.browse:main',
        ],
    },
)
