import unittest

from typing import cast
from git_browse import gitlab, typedefs
from git_browse.tests import test_util


class TestGitlabHost(unittest.TestCase):
    def setUp(self) -> None:
        self.host = gitlab.GitlabHost(
            typedefs.GitConfig("", "main"),
            "albertyw",
            "git-browse",
        )
        self.repository_url = "https://gitlab.com/albertyw/git-browse"
        self.focus_object = typedefs.FocusObject("/")
        self.focus_hash = typedefs.FocusHash(test_util.get_tag())

    def test_init(self) -> None:
        git_config = typedefs.GitConfig("", "master")
        host = gitlab.GitlabHost(git_config, "user", "repository")
        self.assertEqual(host.git_config, git_config)
        self.assertEqual(host.user, "user")
        self.assertEqual(host.repository, "repository")

    def test_create(self) -> None:
        git_config = typedefs.GitConfig(self.repository_url, "master")
        git_config.try_url_match(gitlab.GITLAB_HTTPS_URL)
        obj = gitlab.GitlabHost.create(git_config)
        obj = cast(gitlab.GitlabHost, obj)
        self.assertEqual(obj.user, "albertyw")
        self.assertEqual(obj.repository, "git-browse")

    def test_create_dot_git(self) -> None:
        git_config = typedefs.GitConfig(self.repository_url + ".git", "master")
        git_config.try_url_match(gitlab.GITLAB_HTTPS_URL)
        obj = gitlab.GitlabHost.create(git_config)
        obj = cast(gitlab.GitlabHost, obj)
        self.assertEqual(obj.user, "albertyw")
        self.assertEqual(obj.repository, "git-browse")

    def test_set_host_class(self) -> None:
        self.host.set_host_class(gitlab.GitlabHost)

    def test_get_url_commit_hash(self) -> None:
        self.assertTrue(self.focus_hash.is_commit_hash())
        self.assertFalse(self.focus_hash.is_root())
        self.assertFalse(self.focus_hash.is_directory())
        url = self.host.get_url(self.focus_hash)
        self.assertEqual(
            url,
            "https://gitlab.com/albertyw/git-browse/-/commit/%s"
            % test_util.get_tag(),
        )

    def test_get_url_root(self) -> None:
        self.assertFalse(self.focus_object.is_commit_hash())
        self.assertTrue(self.focus_object.is_root())
        self.assertTrue(self.focus_object.is_directory())
        url = self.host.get_url(self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_get_url_directory(self) -> None:
        self.focus_object.identifier = "asdf/"
        self.assertFalse(self.focus_object.is_commit_hash())
        self.assertFalse(self.focus_object.is_root())
        self.assertTrue(self.focus_object.is_directory())
        url = self.host.get_url(self.focus_object)
        self.assertEqual(
            url, "https://gitlab.com/albertyw/git-browse/-/tree/main/asdf/",
        )

    def test_get_url_file(self) -> None:
        self.focus_object.identifier = "README.md"
        self.assertFalse(self.focus_object.is_commit_hash())
        self.assertFalse(self.focus_object.is_root())
        self.assertFalse(self.focus_object.is_directory())
        url = self.host.get_url(self.focus_object)
        self.assertEqual(
            url, "https://gitlab.com/albertyw/git-browse/-/blob/main/README.md",
        )

    def test_root_url(self) -> None:
        url = self.host.root_url(self.repository_url, self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_directory_url(self) -> None:
        self.focus_object.identifier = "asdf/"
        url = self.host.directory_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url, "https://gitlab.com/albertyw/git-browse/-/tree/main/asdf/",
        )

    def test_file_url(self) -> None:
        self.focus_object.identifier = "README.md"
        url = self.host.file_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url, "https://gitlab.com/albertyw/git-browse/-/blob/main/README.md",
        )

    def test_commit_hash_url(self) -> None:
        url = self.host.commit_hash_url(self.repository_url, self.focus_hash)
        self.assertEqual(
            url,
            "https://gitlab.com/albertyw/git-browse/-/commit/%s"
            % test_util.get_tag(),
        )
