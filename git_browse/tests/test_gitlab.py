import unittest

from git_browse import gitlab, typedefs
from git_browse.tests import test_util


class TestGitlabHost(unittest.TestCase):
    def setUp(self) -> None:
        self.host = gitlab.GitlabHost(
            typedefs.GitConfig('', 'main'),
            'albertyw',
            'git-browse',
        )
        self.repository_url = 'https://gitlab.com/albertyw/git-browse'
        self.focus_object = typedefs.FocusObject('/')
        self.focus_hash = typedefs.FocusHash(test_util.get_tag())

    def test_init(self) -> None:
        git_config = typedefs.GitConfig('', 'master')
        host = gitlab.GitlabHost(git_config, 'user', 'repository')
        self.assertEqual(host.git_config, git_config)
        self.assertEqual(host.user, 'user')
        self.assertEqual(host.repository, 'repository')

    def test_get_url(self) -> None:
        url = self.host.get_url(self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_root_url(self) -> None:
        url = self.host.root_url(self.repository_url, self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_directory_url(self) -> None:
        self.focus_object.identifier = 'asdf/'
        url = self.host.directory_url(
            self.repository_url,
            self.focus_object
        )
        self.assertEqual(
            url,
            'https://gitlab.com/albertyw/git-browse/-/tree/main/asdf/'
        )

    def test_file_url(self) -> None:
        self.focus_object.identifier = 'README.md'
        url = self.host.file_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url,
            'https://gitlab.com/albertyw/git-browse/-/blob/main/README.md'
        )

    def test_commit_hash_url(self) -> None:
        url = self.host.commit_hash_url(
            self.repository_url,
            self.focus_hash
        )
        self.assertEqual(
            url,
            'https://gitlab.com/albertyw/git-browse/-/commit/%s'
            % test_util.get_tag()
        )
