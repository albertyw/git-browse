import os
import re
import shutil
import sys
import tempfile
from typing import List, cast
import unittest
from unittest.mock import MagicMock, patch

from git_browse import browse
from git_browse.tests import test_util

directory = os.path.dirname(os.path.realpath(__file__))
BASE_DIRECTORY = os.path.normpath(os.path.join(directory, '..', '..'))


class TestGithubHost(unittest.TestCase):
    def setUp(self) -> None:
        self.github_host = browse.GithubHost('albertyw', 'git-browse')
        self.repository_url = 'https://github.com/albertyw/git-browse'
        self.focus_object = browse.FocusObject('/')
        self.focus_hash = browse.FocusHash(test_util.get_tag())

    def test_init(self) -> None:
        host = browse.GithubHost('user', 'repository')
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


class SourcegraphHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = browse.SourcegraphHost('code.uber.internal', 'asdf')
        self.obj.host_class = browse.PhabricatorHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, 'code.uber.internal')
        self.assertEqual(self.obj.repository, 'asdf')

    def test_create(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b'
        match = re.search(browse.UBER_SSH_GITOLITE_URL, repo)
        assert match is not None
        obj = browse.SourcegraphHost.create(match)
        self.assertEqual(obj.repository, 'a/b')

    def test_create_dot_git(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b.git'
        match = re.search(browse.UBER_SSH_GITOLITE_URL, repo)
        assert match is not None
        obj = browse.SourcegraphHost.create(match)
        self.assertEqual(obj.repository, 'a/b')

    def test_get_url_commit(self) -> None:
        git_object = browse.FocusHash('abcd')
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/commit/abcd'
        )

    def test_get_url_root(self) -> None:
        git_object = browse.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.UBER_SOURCEGRAPH_URL + 'code.uber.internal/asdf'
        )

    def test_get_url_directory(self) -> None:
        git_object = browse.FocusObject('zxcv' + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/tree/zxcv/'
        )

    def test_get_url_file(self) -> None:
        git_object = browse.FocusObject('zxcv')
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.UBER_SOURCEGRAPH_URL +
            'code.uber.internal/asdf/-/blob/zxcv'
        )

    def test_valid_focus_object(self) -> None:
        valid = self.obj.valid_focus_object('asdf')
        self.assertEqual(valid, None)


class TestGodocsHost(unittest.TestCase):
    def setUp(self) -> None:
        self.obj = browse.GodocsHost('github.com', 'asdf/qwer')
        self.obj.host_class = browse.GithubHost

    def test_init(self) -> None:
        self.assertEqual(self.obj.host, 'github.com')
        self.assertEqual(self.obj.repository, 'asdf/qwer')

    def test_create(self) -> None:
        repo = 'git@github.com:asdf/qwer'
        match = re.search(browse.GITHUB_SSH_URL, repo)
        assert match is not None
        obj = browse.GithubHost.create(match)
        self.assertEqual(obj.user, 'asdf')
        self.assertEqual(obj.repository, 'qwer')

    def test_create_dot_git(self) -> None:
        repo = 'git@github.com:asdf/qwer.git'
        match = re.search(browse.GITHUB_SSH_URL, repo)
        assert match is not None
        obj = browse.GithubHost.create(match)
        self.assertEqual(obj.user, 'asdf')
        self.assertEqual(obj.repository, 'qwer')

    def test_get_url_commit(self) -> None:
        git_object = browse.FocusHash('abcd')
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)

    def test_get_url_root(self) -> None:
        git_object = browse.FocusObject(os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.PUBLIC_GODOCS_URL + 'github.com/asdf/qwer'
        )

    def test_get_url_directory(self) -> None:
        git_object = browse.FocusObject('zxcv' + os.sep)
        url = self.obj.get_url(git_object)
        self.assertEqual(
            url,
            self.obj.PUBLIC_GODOCS_URL +
            'github.com/asdf/qwer/zxcv/'
        )

    def test_get_url_file(self) -> None:
        git_object = browse.FocusObject('zxcv')
        with self.assertRaises(NotImplementedError):
            self.obj.get_url(git_object)

    def test_valid_focus_object(self) -> None:
        valid = self.obj.valid_focus_object('asdf')
        self.assertEqual(valid, None)


class GitObject(unittest.TestCase):
    def test_is_directory(self) -> None:
        obj = browse.GitObject('/asdf')
        self.assertFalse(obj.is_directory())


class FocusObject(unittest.TestCase):
    def test_init(self) -> None:
        obj = browse.FocusObject('/asdf')
        self.assertEqual(obj.identifier, '/asdf')

    def test_is_root(self) -> None:
        obj = browse.FocusObject('/')
        self.assertTrue(obj.is_root())

    def test_is_not_root(self) -> None:
        obj = browse.FocusObject('/asdf/')
        self.assertFalse(obj.is_root())

    def test_is_directory(self) -> None:
        obj = browse.FocusObject('/asdf/')
        self.assertTrue(obj.is_directory())

    def test_is_not_directory(self) -> None:
        obj = browse.FocusObject('/asdf')
        self.assertFalse(obj.is_directory())

    def test_default(self) -> None:
        obj = browse.FocusObject.default()
        self.assertTrue(obj.is_root())


class FocusHash(unittest.TestCase):
    def test_init(self) -> None:
        obj = browse.FocusHash('abcde')
        self.assertEqual(obj.identifier, 'abcde')

    def test_is_commit_hash(self) -> None:
        obj = browse.FocusHash('abcde')
        self.assertTrue(obj.is_commit_hash())


class GetRepositoryRoot(unittest.TestCase):
    def test_get(self) -> None:
        os.chdir(BASE_DIRECTORY)
        directory = browse.get_repository_root()
        self.assertEqual(directory, BASE_DIRECTORY)

    def test_fail_get(self) -> None:
        os.chdir(os.sep)
        with self.assertRaises(FileNotFoundError):
            browse.get_repository_root()


class GetGitConfig(unittest.TestCase):
    def test_get(self) -> None:
        os.chdir(BASE_DIRECTORY)
        directory = browse.get_git_config()
        expected = os.path.join(BASE_DIRECTORY, '.git', 'config')
        self.assertEqual(directory, expected)


class GetGitURL(unittest.TestCase):
    def setUp(self) -> None:
        git_config_file = os.path.join(
            BASE_DIRECTORY,
            '.git',
            'config'
        )
        with open(git_config_file, 'rb') as handle:
            configs = handle.read()
        self.git_config_file = tempfile.NamedTemporaryFile()
        self.git_config_file.write(configs)
        self.git_config_file.seek(0)

    def tearDown(self) -> None:
        self.git_config_file.close()

    def test_url(self) -> None:
        git_url = browse.get_git_url(self.git_config_file.name)
        expected = 'git@github.com:albertyw/git-browse'
        self.assertEqual(git_url.replace('.git', ''), expected)

    def test_bad_url(self) -> None:
        with self.assertRaises(RuntimeError):
            browse.get_git_url(BASE_DIRECTORY)

    def test_multiple_fetch(self) -> None:
        # For https://github.com/albertyw/git-browse/issues/48
        config_contents = (
            '[remote "origin"]\n'
            '    fetch = refs/heads/my_name/*:refs/remotes/origin/my_name/*\n'
            '    fetch = refs/heads/master:refs/remotes/origin/master\n'
            '    url = git@github.com:albertyw/git-browse\n'
        )
        config_file = tempfile.NamedTemporaryFile()
        config_file.write(config_contents.encode('utf-8'))
        config_file.seek(0)
        git_url = browse.get_git_url(config_file.name)
        expected = 'git@github.com:albertyw/git-browse'
        self.assertEqual(git_url.replace('.git', ''), expected)


class ParseGitURL(unittest.TestCase):
    def setUp(self) -> None:
        self.ssh_url = 'git@github.com:albertyw/git-browse.git'
        self.https_url = 'https://github.com/albertyw/git-browse'
        self.broken_url = 'asdfasdf'
        self.uber_ssh_url = 'gitolite@code.uber.internal:abcd/efgh'

    def test_ssh_url(self) -> None:
        host = browse.parse_git_url(self.ssh_url)
        self.check_host(host)

    def test_https_url(self) -> None:
        host = browse.parse_git_url(self.https_url)
        self.check_host(host)

    def check_host(self, host: browse.Host) -> None:
        self.assertTrue(host.__class__ is browse.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')

    def test_sourcegraph_github_host(self) -> None:
        host = browse.parse_git_url(self.ssh_url, sourcegraph=True)
        self.assertTrue(host.__class__ is browse.SourcegraphHost)
        host = cast(browse.SourcegraphHost, host)
        self.assertEqual(host.host, 'github.com')
        self.assertEqual(host.repository, 'albertyw/git-browse')

    def test_sourcegraph_uber_host(self) -> None:
        host = browse.parse_git_url(self.uber_ssh_url, sourcegraph=True)
        self.assertTrue(host.__class__ is browse.SourcegraphHost)
        host = cast(browse.SourcegraphHost, host)
        self.assertEqual(host.host, 'code.uber.internal')
        self.assertEqual(host.repository, 'abcd/efgh')

    def test_broken_url(self) -> None:
        with self.assertRaises(ValueError):
            browse.parse_git_url(self.broken_url)


class TestGetRepositoryHost(unittest.TestCase):
    def test_repository_host(self) -> None:
        host = browse.get_repository_host()
        self.assertTrue(host.__class__ is browse.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')


class TestGetFocusObject(unittest.TestCase):
    def setUp(self) -> None:
        self.host = browse.GithubHost('albertyw', 'git-browse')
        self.placeholder_match = re.match(r'', '')

    def test_default_focus_object(self) -> None:
        focus_object = browse.get_git_object('', os.getcwd(), self.host)
        self.assertTrue(focus_object.is_root())
        self.assertTrue(focus_object.is_directory())

    def test_file_focus_object(self) -> None:
        target = 'README.md'
        focus_object = browse.get_git_object(target, os.getcwd(), self.host)
        self.assertFalse(focus_object.is_root())
        self.assertFalse(focus_object.is_directory())
        self.assertEqual(focus_object.identifier[-10:], 'README.md')

    def test_directory_focus_object(self) -> None:
        focus_object = browse.get_git_object('.', os.getcwd(), self.host)
        self.assertFalse(focus_object.is_root())
        self.assertTrue(focus_object.is_directory())

    def test_get_focus_hash(self) -> None:
        focus_object = browse.get_git_object(
            test_util.get_tag(), os.getcwd(), self.host
        )
        self.assertTrue(focus_object.__class__ is browse.FocusHash)

    def test_phabricator_object(self) -> None:
        assert self.placeholder_match is not None
        host = browse.PhabricatorHost.create(self.placeholder_match)
        focus_object = browse.get_git_object('D123', os.getcwd(), host)
        self.assertTrue(focus_object.__class__ is browse.PhabricatorObject)

    def test_invalid_phabricator_object(self) -> None:
        assert self.placeholder_match is not None
        phabricator_host = browse.PhabricatorHost.create(
            self.placeholder_match
        )
        with self.assertRaises(FileNotFoundError):
            browse.get_git_object('asdf', os.getcwd(), phabricator_host)

    def test_nonexistend_focus_object(self) -> None:
        with self.assertRaises(FileNotFoundError):
            browse.get_git_object('asdf', os.getcwd(), self.host)


class TestGetCommitHash(unittest.TestCase):
    def test_get_unknown_hash(self) -> None:
        focus_object = '!@#$'
        focus_hash = browse.get_commit_hash(focus_object)
        self.assertEqual(focus_hash, None)

    def test_get_hash(self) -> None:
        focus_hash = browse.get_commit_hash(test_util.get_tag())
        self.assertTrue(focus_hash.__class__ is browse.FocusHash)
        focus_hash = cast(browse.FocusHash, focus_hash)
        self.assertTrue(focus_hash.identifier)


class TestOpenURL(unittest.TestCase):
    @patch("builtins.print", autospec=True)
    def test_open_url(self, mock_print: MagicMock) -> None:
        browse.open_url('asdf')
        mock_print.assert_called_with('asdf')

    @patch("builtins.print", autospec=True)
    @patch("subprocess.call")
    def test_open_subprocess(
        self, mock_call: MagicMock, mock_print: MagicMock
    ) -> None:
        browse.open_url(['asdf'])
        mock_print.assert_called_with(['asdf'])
        mock_call.assert_called_with(['asdf'])

    @patch("builtins.print", autospec=True)
    @patch("subprocess.call")
    def test_dry_open_url(
        self, mock_call: MagicMock, mock_print: MagicMock
    ) -> None:
        browse.open_url(['asdf'], True)
        mock_print.assert_called_with(['asdf'])
        assert not mock_call.called


class FullTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_sys_argv = sys.argv
        self.test_directory = os.path.join(BASE_DIRECTORY, 'test_dir')
        test_file = os.path.join(self.test_directory, 'test_file')
        os.makedirs(self.test_directory, exist_ok=True)
        with open(test_file, 'w'):
            pass

    def tearDown(self) -> None:
        sys.argv = self.original_sys_argv
        os.chdir(BASE_DIRECTORY)
        shutil.rmtree(self.test_directory)

    @patch("git_browse.browse.open_url")
    def test_default(self, mock_open_url: MagicMock) -> None:
        sys_argv = ['asdf']
        expected = 'https://github.com/albertyw/git-browse'
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_file(self, mock_open_url: MagicMock) -> None:
        sys_argv = ['asdf', 'README.md']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'blob/master/README.md'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_subdirectory_file(self, mock_open_url: MagicMock) -> None:
        sys_argv = ['asdf', 'test_dir/test_file']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'blob/master/test_dir/test_file'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_chdir_subdirectory_file(self, mock_open_url: MagicMock) -> None:
        os.chdir(self.test_directory)
        sys_argv = ['asdf', 'test_file']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'blob/master/test_dir/test_file'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_directory(self, mock_open_url: MagicMock) -> None:
        sys_argv = ['asdf', '.']
        expected = 'https://github.com/albertyw/git-browse/tree/master/./'
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_subdirectory(self, mock_open_url: MagicMock) -> None:
        sys_argv = ['asdf', 'test_dir']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'tree/master/test_dir/'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    @patch("git_browse.browse.open_url")
    def test_chdir_subdirectory(self, mock_open_url: MagicMock) -> None:
        os.chdir(self.test_directory)
        sys_argv = ['asdf', '.']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'tree/master/test_dir/'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    def check_main(
        self, sys_argv: List[str], expected: str, mock_open_url: MagicMock
    ) -> None:
        sys.argv = sys_argv
        browse.main()
        mock_open_url.assert_called_with(expected, False, False)

    @patch('sys.stdout.write')
    def test_check_version(self, mock_print: MagicMock) -> None:
        with self.assertRaises(SystemExit):
            sys.argv = ['asdf', '-v']
            browse.main()
        self.assertTrue(mock_print.called)
