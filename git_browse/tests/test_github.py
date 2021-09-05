import pathlib
import unittest

from git_browse import github, typedefs
from git_browse.tests import test_util

BASE_DIRECTORY = pathlib.Path(__file__).parents[2]


class TestGithubHost(unittest.TestCase):
    def setUp(self) -> None:
        self.github_host = github.GithubHost(
            typedefs.GitConfig('', 'master'),
            'albertyw',
            'git-browse',
        )
        self.repository_url = 'https://github.com/albertyw/git-browse'
        self.focus_object = typedefs.FocusObject('/')
        self.focus_hash = typedefs.FocusHash(test_util.get_tag())

    def test_init(self) -> None:
        git_config = typedefs.GitConfig('', 'master')
        host = github.GithubHost(git_config, 'user', 'repository')
        self.assertEqual(host.git_config, git_config)
        self.assertEqual(host.user, 'user')
        self.assertEqual(host.repository, 'repository')

    def test_get_url(self) -> None:
        url = self.github_host.get_url(self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_root_url(self) -> None:
        url = self.github_host.root_url(self.repository_url, self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_directory_url(self) -> None:
        self.focus_object.identifier = 'asdf/'
        url = self.github_host.directory_url(
            self.repository_url,
            self.focus_object
        )
        self.assertEqual(
            url,
            'https://github.com/albertyw/git-browse/tree/master/asdf/'
        )

    def test_file_url(self) -> None:
        self.focus_object.identifier = 'README.md'
        url = self.github_host.file_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url,
            'https://github.com/albertyw/git-browse/blob/master/README.md'
        )

    def test_commit_hash_url(self) -> None:
        url = self.github_host.commit_hash_url(
            self.repository_url,
            self.focus_hash
        )
        self.assertEqual(
            url,
            'https://github.com/albertyw/git-browse/commit/%s'
            % test_util.get_tag()
        )
