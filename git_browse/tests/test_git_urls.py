import os
import pathlib
import json
from typing import Callable, NamedTuple, cast
import unittest
from unittest.mock import MagicMock, patch

from git_browse import browse
from git_browse.typedefs import GitConfig
from git_browse.tests import test_util


class TestConfig(NamedTuple):
    git_config: GitConfig
    target_path: str
    host_url: str


REPO_PATH = pathlib.Path(__file__).parents[2]
TEST_DIR = 'testdir'
TEST_DIR_PATH = REPO_PATH / TEST_DIR
ARCCONFIG_PATH = REPO_PATH / '.arcconfig'
GIT_URLS: list[TestConfig] = [
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', ''),
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse.git', ''),
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('https://github.com/albertyw/git-browse.git', ''),
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('https://github.com/albertyw/git-browse', ''),
        '',
        'https://github.com/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', 'master'),
        'README.md',
        'https://github.com/albertyw/git-browse/blob/master/README.md',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', 'master'),
        TEST_DIR,
        'https://github.com/albertyw/git-browse/tree/master/testdir/',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', 'main'),
        'README.md',
        'https://github.com/albertyw/git-browse/blob/main/README.md',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', 'main'),
        TEST_DIR,
        'https://github.com/albertyw/git-browse/tree/main/testdir/',
    ),
    TestConfig(
        GitConfig('git@github.com:albertyw/git-browse', ''),
        test_util.get_tag(),
        'https://github.com/albertyw/git-browse/commit/' +
        test_util.get_tag_commit_hash(),
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', ''),
        '',
        'https://bitbucket.org/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse.git', ''),
        '',
        'https://bitbucket.org/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig(
            'https://albertyw@bitbucket.org/albertyw/git-browse.git', '',
        ),
        '',
        'https://bitbucket.org/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('https://albertyw@bitbucket.org/albertyw/git-browse', ''),
        '',
        'https://bitbucket.org/albertyw/git-browse',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', 'master'),
        'README.md',
        'https://bitbucket.org/albertyw/git-browse/src/master/README.md',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', 'master'),
        TEST_DIR,
        'https://bitbucket.org/albertyw/git-browse/src/master/testdir/',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', 'main'),
        'README.md',
        'https://bitbucket.org/albertyw/git-browse/src/main/README.md',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', 'main'),
        TEST_DIR,
        'https://bitbucket.org/albertyw/git-browse/src/main/testdir/',
    ),
    TestConfig(
        GitConfig('git@bitbucket.org:albertyw/git-browse', ''),
        test_util.get_tag(),
        'https://bitbucket.org/albertyw/git-browse/commits/' +
        test_util.get_tag_commit_hash(),
    ),
    TestConfig(
        GitConfig('gitolite@code.uber.internal:a/b', ''),
        '',
        'https://example.com/diffusion/ABCD/repository/master/',
    ),
    TestConfig(
        GitConfig('gitolite@config.uber.internal:a/b', ''),
        '',
        'https://example.com/diffusion/ABCD/repository/master/',
    ),
    TestConfig(
        GitConfig('gitolite@code.uber.internal:a/b', ''),
        'README.md',
        'https://example.com/diffusion/ABCD/browse/master/README.md',
    ),
    TestConfig(
        GitConfig('gitolite@code.uber.internal:a/b', ''),
        TEST_DIR,
        'https://example.com/diffusion/ABCD/browse/master/testdir/',
    ),
    TestConfig(
        GitConfig('gitolite@code.uber.internal:a/b', ''),
        test_util.get_tag(),
        'https://example.com/rABCD' + test_util.get_tag_commit_hash(),
    ),
    TestConfig(
        GitConfig('gitolite@code.uber.internal:a', ''),
        'README.md',
        'https://example.com/diffusion/ABCD/browse/master/README.md',
    ),
    TestConfig(
        GitConfig('https://code.uber.internal/x/y', ''),
        'README.md',
        'https://example.com/diffusion/ABCD/browse/master/README.md',
    ),
]


class TestGitURLs(unittest.TestCase):
    def setUp(self) -> None:
        os.mkdir(TEST_DIR_PATH)
        self.mock_arcconfig()

    def tearDown(self) -> None:
        os.rmdir(TEST_DIR_PATH)
        os.remove(ARCCONFIG_PATH)

    def mock_arcconfig(self) -> None:
        data = {
            'phabricator.uri': 'https://example.com',
            'repository.callsign': 'ABCD',
            'git.default-relative-commit': 'origin/master',
        }
        with open(ARCCONFIG_PATH, 'w') as handle:
            handle.write(json.dumps(data))


def generate_test(test_config: TestConfig) -> Callable[[], None]:
    @patch('git_browse.browse.get_git_config_data')
    def test(
        self: TestGitURLs,
        mock_get_git_config_data: MagicMock
    ) -> None:

        mock_get_git_config_data.return_value = test_config.git_config
        host = browse.get_repository_host()
        focus_object = browse.get_git_object(
            test_config.target_path, pathlib.Path(REPO_PATH), host
        )

        url = host.get_url(focus_object)
        self.assertEqual(test_config.host_url, url)

    test = cast(Callable[[], None], test)
    return test


for i, test_config in enumerate(GIT_URLS):
    test_method = generate_test(test_config)
    test_method.__name__ = 'test_git_url_%s' % i
    setattr(TestGitURLs, test_method.__name__, test_method)
