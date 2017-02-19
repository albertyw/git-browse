import os
import unittest

from git_browse import browse


directory = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.normpath(os.path.join(directory, '..', '..'))
TEST_DIR = 'testdir'
TEST_DIR_PATH = os.path.join(REPO_PATH, 'testdir')
GIT_URLS = [
    (
        'git@github.com:albertyw/git-browse',
        None,
        'https://github.com/albertyw/git-browse'
    ),
    (
        'git@github.com:albertyw/git-browse.git',
        None,
        'https://github.com/albertyw/git-browse'
    ),
    (
        'git@github.com:albertyw/asdf._zxcv',
        None,
        'https://github.com/albertyw/asdf._zxcv'
    ),
    (
        'git@github.com:asdf._zxcv/git-browse',
        None,
        'https://github.com/asdf._zxcv/git-browse'
    ),
    (
        'https://github.com/albertyw/git-browse.git',
        None,
        'https://github.com/albertyw/git-browse'
    ),
    (
        'https://github.com/albertyw/git-browse',
        None,
        'https://github.com/albertyw/git-browse'
    ),
    (
        'git@github.com:albertyw/git-browse',
        'README.md',
        'https://github.com/albertyw/git-browse/blob/master/README.md'
    ),
    (
        'git@github.com:albertyw/git-browse',
        TEST_DIR,
        'https://github.com/albertyw/git-browse/tree/master/testdir/'
    ),
    (
        'git@github.com:albertyw/git-browse',
        'v2.0.0',
        'https://github.com/albertyw/git-browse/commit/' +
        'f5631b4c423f2fa5c9c4b64853607f1727d4b7a9'
    ),
    (
        'gitolite@code.uber.internal:a/b',
        None,
        ['arc', 'browse', '.']
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'README.md',
        ['arc', 'browse', 'README.md']
    ),
    (
        'gitolite@code.uber.internal:a/b',
        TEST_DIR,
        ['arc', 'browse', TEST_DIR+'/']
    ),
    (
        'gitolite@code.uber.internal:a/b',
        'v2.0.0',
        ['arc', 'browse', 'f5631b4c423f2fa5c9c4b64853607f1727d4b7a9']
    )
]


class TestGitURLs(unittest.TestCase):
    def setUp(self):
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self):
        os.rmdir(TEST_DIR_PATH)


def generate_test(*test_data):
    git_url, target_path, host_url = test_data

    def test(self):
        host = browse.parse_git_url(git_url)
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
