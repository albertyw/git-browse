import os
import pathlib
import unittest

from git_browse import github, sourcegraph, phabricator, typedefs

BASE_DIRECTORY = pathlib.Path(__file__).parents[2]


class SourcegraphHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = sourcegraph.SourcegraphHost(
            typedefs.GitConfig("", "master"),
            "github.com",
            "albertyw/git-browse",
        )
        self.uber_obj = sourcegraph.SourcegraphHost(
            typedefs.GitConfig("", "master"),
            "code.uber.internal",
            "asdf/qwer",
        )
        self.uber_obj.host_class = phabricator.PhabricatorHost
        self.uber_obj_java = sourcegraph.SourcegraphHost(
            typedefs.GitConfig("", "master"),
            "code.uber.internal",
            "lm/fievel",
        )
        self.uber_obj_java.host_class = phabricator.PhabricatorHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, "github.com")
        self.assertEqual(self.obj.repository, "albertyw/git-browse")

    def test_create(self) -> None:
        repo = "git@github.com:a/b"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(github.GITHUB_SSH_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, "a/b")

    def test_create_dot_git(self) -> None:
        repo = "git@github.com:a/b.git"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(github.GITHUB_SSH_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, "a/b")

    def test_get_url_commit(self) -> None:
        git_object = typedefs.FocusHash("abcd")
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.PUBLIC_SOURCEGRAPH_URL
            + "github.com/albertyw/git-browse/-/commit/abcd",
        )

    def test_get_url_root(self) -> None:
        git_object = typedefs.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url, sourcegraph.PUBLIC_SOURCEGRAPH_URL + "github.com/albertyw/git-browse"
        )

    def test_get_url_directory(self) -> None:
        git_object = typedefs.FocusObject("git_browse" + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.PUBLIC_SOURCEGRAPH_URL
            + "github.com/albertyw/git-browse/-/tree/git_browse/",
        )

    def test_get_url_file(self) -> None:
        git_object = typedefs.FocusObject("README.md")
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.PUBLIC_SOURCEGRAPH_URL
            + "github.com/albertyw/git-browse/-/blob/README.md",
        )

    def test_uber_init(self) -> None:
        self.assertEqual(self.uber_obj.host, "code.uber.internal")
        self.assertEqual(self.uber_obj.repository, "asdf/qwer")

    def test_uber_create(self) -> None:
        repo = "gitolite@code.uber.internal:a/b"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, "a/b")

    def test_uber_create_dot_git(self) -> None:
        repo = "gitolite@code.uber.internal:a/b.git"
        git_config = typedefs.GitConfig(repo, "master")
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, "a/b")

    def test_uber_get_url_commit(self) -> None:
        git_object = typedefs.FocusHash("abcd")
        url = self.uber_obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL
            + "code.uber.internal/uber-code/asdf-qwer/-/commit/abcd",
        )

    def test_uber_get_url_root(self) -> None:
        git_object = typedefs.FocusObject(os.sep)
        url = self.uber_obj.get_url(git_object)
        self.assertEqual(
            url, sourcegraph.UBER_SOURCEGRAPH_URL
            + "code.uber.internal/uber-code/asdf-qwer"
        )

    def test_uber_get_url_directory(self) -> None:
        git_object = typedefs.FocusObject("zxcv" + os.sep)
        url = self.uber_obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL
            + "code.uber.internal/uber-code/asdf-qwer/-/tree/zxcv/",
        )

    def test_uber_get_url_file(self) -> None:
        git_object = typedefs.FocusObject("zxcv")
        url = self.uber_obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL
            + "code.uber.internal/uber-code/asdf-qwer/-/blob/zxcv",
        )

    def test_uber_java_code(self) -> None:
        git_object = typedefs.FocusObject("zxcv")
        url = self.uber_obj_java.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL
            + "code.uber.internal/uber-code/java-code/-/blob/zxcv",
        )
