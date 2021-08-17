import os
import re
import unittest

from git_browse import github, godocs, typedefs


class TestGodocsHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = godocs.GodocsHost('github.com', 'asdf/qwer')
        self.obj.host_class = github.GithubHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, 'github.com')
        self.assertEqual(self.obj.repository, 'asdf/qwer')

    def test_create(self) -> None:
        repo = 'git@github.com:asdf/qwer'
        match = re.search(github.GITHUB_SSH_URL, repo)
        assert match is not None
        obj = github.GithubHost.create(match)
        self.assertEqual(obj.user, 'asdf')
        self.assertEqual(obj.repository, 'qwer')

    def test_create_dot_git(self) -> None:
        repo = 'git@github.com:asdf/qwer.git'
        match = re.search(github.GITHUB_SSH_URL, repo)
        assert match is not None
        obj = github.GithubHost.create(match)
        self.assertEqual(obj.user, 'asdf')
        self.assertEqual(obj.repository, 'qwer')

    def test_get_url_commit(self) -> None:
        git_object = typedefs.FocusHash('abcd')
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)

    def test_get_url_root(self) -> None:
        git_object = typedefs.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.PUBLIC_GODOCS_URL + 'github.com/asdf/qwer'
        )

    def test_get_url_directory(self) -> None:
        git_object = typedefs.FocusObject('zxcv' + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.PUBLIC_GODOCS_URL +
            'github.com/asdf/qwer/zxcv/'
        )

    def test_get_url_file(self) -> None:
        git_object = typedefs.FocusObject('zxcv')
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)
