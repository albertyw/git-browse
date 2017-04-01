from pathlib import Path
import os
import unittest

from git_browse import browse


directory = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.normpath(os.path.join(directory, '..', '..'))
TEST_DIR = 'testdir'
TEST_DIR_PATH = os.path.join(REPO_PATH, 'testdir')
ARCCONFIG_PATH = os.path.join(REPO_PATH, '.arcconfig')
GIT_URLS = [
    (
        'git@github.com:albertyw/git-browse',
        None,
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'git@github.com:albertyw/git-browse.git',
        None,
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'https://github.com/albertyw/git-browse.git',
        None,
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'https://github.com/albertyw/git-browse',
        None,
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'git@github.com:albertyw/git-browse',
        'README.md',
        'https://github.com/albertyw/git-browse/blob/master/README.md',
        False
    ),
    (
        'git@github.com:albertyw/git-browse',
        TEST_DIR,
        'https://github.com/albertyw/git-browse/tree/master/testdir/',
        False
    ),
    (
        'git@github.com:albertyw/git-browse',
        'v2.0.0',
        'https://github.com/albertyw/git-browse/commit/' +
        'f5631b4c423f2fa5c9c4b64853607f1727d4b7a9',
        False
    ),
    (
        'gitolite@code.uber.internal:a/b',
        None,
        ['arc', 'browse', '.'],
        True
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'README.md',
        ['arc', 'browse', 'README.md'],
        True
    ),
    (
        'gitolite@code.uber.internal:a/b',
        TEST_DIR,
        ['arc', 'browse', TEST_DIR+'/'],
        True
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'v2.0.0',
        ['arc', 'browse', 'f5631b4c423f2fa5c9c4b64853607f1727d4b7a9'],
        True
    )
]


class TestGitURLs(unittest.TestCase):
    def setUp(self):
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self):
        os.rmdir(TEST_DIR_PATH)
        if os.path.exists(ARCCONFIG_PATH):
            os.remove(ARCCONFIG_PATH)


def generate_test(*test_data):
    git_url, target_path, host_url, arcconfig = test_data

    def test(self):
        if arcconfig:
            Path(ARCCONFIG_PATH).touch()
        host = browse.get_repository_host()
        sys_argv = ['git-browse.py']
        if target_path:
            sys_argv.append(target_path)
        focus_object = browse.get_git_object(sys_argv, REPO_PATH)
        url = host.get_url(focus_object)
        self.assertEqual(host_url, url)
    return test


for i, test_data in enumerate(GIT_URLS):
    test_method = generate_test(*test_data)
    test_method.__name__ = 'test_git_url_%s' % i
    setattr(TestGitURLs, test_method.__name__, test_method)
