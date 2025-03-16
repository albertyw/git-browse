import os
import unittest
from typing import cast

from git_browse import github, godocs, phabricator, typedefs


class TestGodocsHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = godocs.GodocsHost(
            typedefs.GitConfig("", "master"),
            "github.com",
            "asdf/qwer",
        )
        self.obj.host_class = github.GithubHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, "github.com")
        self.assertEqual(self.obj.repository, "asdf/qwer")

    def test_create(self) -> None:
        repo = "git@github.com:asdf/qwer"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(github.GITHUB_SSH_URL)
        obj = godocs.GodocsHost.create(git_config)
        obj = cast(godocs.GodocsHost, obj)
        self.assertEqual(obj.host, "github.com")
        self.assertEqual(obj.repository, "asdf/qwer")

    def test_create_dot_git(self) -> None:
        repo = "git@github.com:asdf/qwer.git"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(github.GITHUB_SSH_URL)
        obj = godocs.GodocsHost.create(git_config)
        obj = cast(godocs.GodocsHost, obj)
        self.assertEqual(obj.host, "github.com")
        self.assertEqual(obj.repository, "asdf/qwer")

    def test_create_no_user(self) -> None:
        repo = "gitolite@code.uber.internal:asdf"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        obj = godocs.GodocsHost.create(git_config)
        obj = cast(godocs.GodocsHost, obj)
        self.assertEqual(obj.host, "code.uber.internal")
        self.assertEqual(obj.repository, "asdf")

    def test_set_host_class(self) -> None:
        self.obj.set_host_class(github.GithubHost)
        self.assertEqual(self.obj.host_class, github.GithubHost)

    def test_get_url_commit(self) -> None:
        git_object = typedefs.FocusHash("abcd")
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)

    def test_get_url_root(self) -> None:
        git_object = typedefs.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url, godocs.PUBLIC_GODOCS_URL + "github.com/asdf/qwer",
        )

    def test_get_url_directory(self) -> None:
        git_object = typedefs.FocusObject("zxcv" + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url, godocs.PUBLIC_GODOCS_URL + "github.com/asdf/qwer/zxcv/",
        )

    def test_get_url_uber(self) -> None:
        git_object = typedefs.FocusObject("zxcv" + os.sep)
        obj = godocs.GodocsHost(
            typedefs.GitConfig("", "master"),
            "code.uber.internal",
            "asdf",
        )
        obj.host_class = phabricator.PhabricatorHost
        url = obj.get_url(git_object)
        self.assertEqual(
            url, godocs.UBER_GODOCS_URL + "code.uber.internal/asdf/zxcv/",
        )

    def test_get_url_file(self) -> None:
        git_object = typedefs.FocusObject("zxcv")
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)
