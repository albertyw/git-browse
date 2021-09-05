import os
import pathlib
import unittest

from git_browse import sourcegraph, phabricator, typedefs

BASE_DIRECTORY = pathlib.Path(__file__).parents[2]


class SourcegraphHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = sourcegraph.SourcegraphHost(
            typedefs.GitConfig('', 'master'),
            'code.uber.internal',
            'asdf',
        )
        self.obj.host_class = phabricator.PhabricatorHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, 'code.uber.internal')
        self.assertEqual(self.obj.repository, 'asdf')

    def test_create(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b'
        git_config = typedefs.GitConfig(repo, 'master')
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, 'a/b')

    def test_create_dot_git(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b.git'
        git_config = typedefs.GitConfig(repo, 'master')
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        obj = sourcegraph.SourcegraphHost.create(git_config)
        self.assertEqual(obj.repository, 'a/b')

    def test_get_url_commit(self) -> None:
        git_object = typedefs.FocusHash('abcd')
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/commit/abcd'
        )

    def test_get_url_root(self) -> None:
        git_object = typedefs.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL + 'code.uber.internal/asdf'
        )

    def test_get_url_directory(self) -> None:
        git_object = typedefs.FocusObject('zxcv' + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/tree/zxcv/'
        )

    def test_get_url_file(self) -> None:
        git_object = typedefs.FocusObject('zxcv')
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            sourcegraph.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/blob/zxcv'
        )
