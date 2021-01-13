import os
from typing import Callable, List, NamedTuple, Union, cast
import unittest
from unittest.mock import MagicMock, patch

from git_browse import browse
from git_browse.tests import test_util


class TestConfig(NamedTuple):
    git_url: str
    target_path: str
    host_url: Union[str, List[str]]


directory = os.path.dirname(os.path.realpath(__file__))
REPO_PATH = os.path.normpath(os.path.join(directory, '..', '..'))
TEST_DIR = 'testdir'
TEST_DIR_PATH = os.path.join(REPO_PATH, 'testdir')
GIT_URLS: List[TestConfig] = [
    TestConfig(
        'git@github.com:albertyw/git-browse',
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        'git@github.com:albertyw/git-browse.git',
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        'https://github.com/albertyw/git-browse.git',
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        'https://github.com/albertyw/git-browse',
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        'git@github.com:albertyw/git-browse',
        'README.md',
        'https://github.com/albertyw/git-browse/blob/master/README.md',
    ),
    TestConfig(
        'git@github.com:albertyw/git-browse',
        TEST_DIR,
        'https://github.com/albertyw/git-browse/tree/master/testdir/',
    ),
    TestConfig(
        'git@github.com:albertyw/git-browse',
        test_util.get_tag(),
        'https://github.com/albertyw/git-browse/commit/' +
        test_util.get_tag_commit_hash(),
    ),
    TestConfig(
        'gitolite@code.uber.internal:a/b',
        '',
        ['arc', 'browse', '.'],
    ),
    TestConfig(
        'gitolite@config.uber.internal:a/b',
        '',
        ['arc', 'browse', '.'],
    ),
    TestConfig(
        'gitolite@code.uber.internal:a/b',
        'README.md',
        ['arc', 'browse', 'README.md'],
    ),
    TestConfig(
        'gitolite@code.uber.internal:a/b',
        TEST_DIR,
        ['arc', 'browse', TEST_DIR+'/'],
    ),
    TestConfig(
        'gitolite@code.uber.internal:a/b',
        test_util.get_tag(),
        ['arc', 'browse', test_util.get_tag_commit_hash()],
    ),
    TestConfig(
        'gitolite@code.uber.internal:a/b',
        'D123',
        ['arc', 'browse', 'D123'],
    ),
    TestConfig(
        'gitolite@code.uber.internal:a',
        'README.md',
        ['arc', 'browse', 'README.md'],
    ),
    TestConfig(
        'https://code.uber.internal/x/y',
        'README.md',
        ['arc', 'browse', 'README.md'],
    ),
]


class TestGitURLs(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(TEST_DIR_PATH)

    def tearDown(self) -> None:
        os.rmdir(TEST_DIR_PATH)


def generate_test(test_config: TestConfig) -> Callable[[], None]:
    @patch('git_browse.browse.get_git_url')
    def test(self: TestGitURLs, mock_get_git_url: MagicMock) -> None:
        mock_get_git_url.return_value = test_config.git_url
        host = browse.get_repository_host()
        focus_object = browse.get_git_object(
            test_config.target_path, REPO_PATH, host
        )
        url = host.get_url(focus_object)
        self.assertEqual(test_config.host_url, url)
    test = cast(Callable[[], None], test)
    return test


for i, test_config in enumerate(GIT_URLS):
    test_method = generate_test(test_config)
    test_method.__name__ = 'test_git_url_%s' % i
    setattr(TestGitURLs, test_method.__name__, test_method)
