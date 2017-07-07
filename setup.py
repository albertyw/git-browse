# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from codecs import open
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='git-browse',

    version='2.4.0',

    description='Open repositories, directories, and files in the browser',
    long_description=long_description,

    url='https://github.com/albertyw/git-browse',

    author='Albert Wang',
    author_email='aywang31@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Software Development :: Version Control',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='github phabricator repository browser',

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

    package_data={},

    data_files=[],

    entry_points={
        'console_scripts': [
            'git_browse=git_browse.browse:main',
        ],
    },
)
