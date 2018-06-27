import os
import unittest
from unittest.mock import patch

from git_browse import browse


directory = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.normpath(os.path.join(directory, '..', '..'))
TEST_DIR = 'testdir'
TEST_DIR_PATH = os.path.join(REPO_PATH, 'testdir')
GIT_URLS = [
    (
        'git@github.com:albertyw/git-browse',
        '',
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'git@github.com:albertyw/git-browse.git',
        '',
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'https://github.com/albertyw/git-browse.git',
        '',
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'https://github.com/albertyw/git-browse',
        '',
        'https://github.com/albertyw/git-browse',
        False
    ),
    (
        'git@github.com:albertyw/git-browse',
        'README.rst',
        'https://github.com/albertyw/git-browse/blob/master/README.rst',
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
        '',
        ['arc', 'browse', '.'],
        True
    ),
    (
        'gitolite@config.uber.internal:a/b',
        '',
        ['arc', 'browse', '.'],
        True
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'README.rst',
        ['arc', 'browse', 'README.rst'],
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
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'D123',
        ['arc', 'browse', 'D123'],
        True
    ),
    (
        'gitolite@code.uber.internal:a',
        'README.rst',
        ['arc', 'browse', 'README.rst'],
        True
    ),
    (
        'https://code.uber.internal/x/y',
        'README.rst',
        ['arc', 'browse', 'README.rst'],
        True
    ),
]


class TestGitURLs(unittest.TestCase):
    def setUp(self):
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self):
        os.rmdir(TEST_DIR_PATH)


def generate_test(*test_data):
    git_url, target_path, host_url, arcconfig = test_data

    @patch('git_browse.browse.get_git_url')
    def test(self, mock_get_git_url):
        mock_get_git_url.return_value = git_url
        host = browse.get_repository_host()
        focus_object = browse.get_git_object(target_path, REPO_PATH, host)
        url = host.get_url(focus_object)
        self.assertEqual(host_url, url)
    return test


for i, test_data in enumerate(GIT_URLS):
    test_method = generate_test(*test_data)
    test_method.__name__ = 'test_git_url_%s' % i
    setattr(TestGitURLs, test_method.__name__, test_method)
