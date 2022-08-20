import os
import pathlib
import re
import shutil
import sys
import tempfile
from typing import cast
import unittest
from unittest.mock import MagicMock, patch

from git_browse import browse, github, sourcegraph, typedefs
from git_browse.tests import test_util

BASE_DIRECTORY = pathlib.Path(__file__).parents[2]


class GetRepositoryRoot(unittest.TestCase):
    def test_get(self) -> None:
        os.chdir(BASE_DIRECTORY)
        directory = browse.get_repository_root()
        self.assertEqual(directory, BASE_DIRECTORY)

    def test_fail_get(self) -> None:
        os.chdir(os.sep)
        with self.assertRaises(FileNotFoundError):
            browse.get_repository_root()


class GetGitConfigPath(unittest.TestCase):
    def test_get(self) -> None:
        os.chdir(BASE_DIRECTORY)
        directory = browse.get_git_config_path()
        expected = BASE_DIRECTORY / '.git' / 'config'
        self.assertEqual(directory, expected)

    def test_submodule_get(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        config_dir = BASE_DIRECTORY / '.git'
        data = 'gitdir: %s' % config_dir
        with open(pathlib.Path(temp_dir.name) / '.git', 'w') as handle:
            handle.write(data)
        os.chdir(temp_dir.name)
        directory = browse.get_git_config_path()
        expected = config_dir / 'config'
        self.assertEqual(directory, expected)
        temp_dir.cleanup()


class GetGitConfigData(unittest.TestCase):
    def setUp(self) -> None:
        git_config_file = BASE_DIRECTORY / '.git' / 'config'
        with open(git_config_file, 'rb') as handle:
            configs = handle.read()
        self.git_config_file = tempfile.NamedTemporaryFile()
        self.git_config_file.write(configs)
        self.git_config_file.seek(0)
        self.git_config_file_name = pathlib.Path(self.git_config_file.name)

    def tearDown(self) -> None:
        self.git_config_file.close()

    def test_url(self) -> None:
        git_config = browse.get_git_config_data(self.git_config_file_name)
        git_url = git_config.git_url.replace('.git', '')
        expected = [
            'git@github.com:albertyw/git-browse',
            'https://github.com/albertyw/git-browse',
        ]
        self.assertIn(git_url, expected)

    def test_bad_url(self) -> None:
        with self.assertRaises(RuntimeError):
            browse.get_git_config_data(BASE_DIRECTORY)

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
        config_file_name = pathlib.Path(config_file.name)
        git_config_data = browse.get_git_config_data(config_file_name)
        expected = 'git@github.com:albertyw/git-browse'
        self.assertEqual(git_config_data.git_url.replace('.git', ''), expected)


class ParseGitURL(unittest.TestCase):
    def setUp(self) -> None:
        self.ssh_url = 'git@github.com:albertyw/git-browse.git'
        self.https_url = 'https://github.com/albertyw/git-browse'
        self.broken_url = 'asdfasdf'
        self.uber_ssh_url = 'gitolite@code.uber.internal:abcd/efgh'

    def test_ssh_url(self) -> None:
        host = browse.parse_git_url(typedefs.GitConfig(self.ssh_url, ''))
        self.check_host(host)

    def test_https_url(self) -> None:
        host = browse.parse_git_url(typedefs.GitConfig(self.https_url, ''))
        self.check_host(host)

    def check_host(self, host: typedefs.Host) -> None:
        self.assertTrue(host.__class__ is github.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')

    def test_sourcegraph_github_host(self) -> None:
        host = browse.parse_git_url(
            typedefs.GitConfig(self.ssh_url, ''),
            use_sourcegraph=True,
        )
        self.assertTrue(host.__class__ is sourcegraph.SourcegraphHost)
        host = cast(sourcegraph.SourcegraphHost, host)
        self.assertEqual(host.host, 'github.com')
        self.assertEqual(host.repository, 'albertyw/git-browse')

    def test_sourcegraph_uber_host(self) -> None:
        host = browse.parse_git_url(
            typedefs.GitConfig(self.uber_ssh_url, ''),
            use_sourcegraph=True,
        )
        self.assertTrue(host.__class__ is sourcegraph.SourcegraphHost)
        host = cast(sourcegraph.SourcegraphHost, host)
        self.assertEqual(host.host, 'code.uber.internal')
        self.assertEqual(host.repository, 'abcd/efgh')

    def test_broken_url(self) -> None:
        with self.assertRaises(ValueError):
            browse.parse_git_url(typedefs.GitConfig(self.broken_url, ''))


class TestGetRepositoryHost(unittest.TestCase):
    def test_repository_host(self) -> None:
        host = browse.get_repository_host()
        self.assertTrue(host.__class__ is github.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')


class TestGetFocusObject(unittest.TestCase):
    def setUp(self) -> None:
        git_config = typedefs.GitConfig('', 'master')
        self.host = github.GithubHost(git_config, 'albertyw', 'git-browse')
        self.placeholder_match = re.match(r'', '')

    def test_default_focus_object(self) -> None:
        focus_object = browse.get_git_object('', pathlib.Path.cwd(), self.host)
        self.assertTrue(focus_object.is_root())
        self.assertTrue(focus_object.is_directory())

    def test_file_focus_object(self) -> None:
        target = 'README.md'
        focus_object = browse.get_git_object(
            target, pathlib.Path.cwd(), self.host,
        )
        self.assertFalse(focus_object.is_root())
        self.assertFalse(focus_object.is_directory())
        self.assertEqual(focus_object.identifier[-10:], 'README.md')

    def test_directory_focus_object(self) -> None:
        focus_object = browse.get_git_object(
            '.', pathlib.Path.cwd(), self.host,
        )
        self.assertFalse(focus_object.is_root())
        self.assertTrue(focus_object.is_directory())

    def test_get_focus_hash(self) -> None:
        focus_object = browse.get_git_object(
            test_util.get_tag(), pathlib.Path.cwd(), self.host
        )
        self.assertTrue(focus_object.__class__ is typedefs.FocusHash)

    def test_nonexistend_focus_object(self) -> None:
        with self.assertRaises(FileNotFoundError):
            browse.get_git_object('asdf', pathlib.Path.cwd(), self.host)


class TestGetCommitHash(unittest.TestCase):
    def test_get_unknown_hash(self) -> None:
        focus_object = '!@#$'
        focus_hash = browse.get_commit_hash(focus_object)
        self.assertEqual(focus_hash, None)

    def test_get_hash(self) -> None:
        focus_hash = browse.get_commit_hash(test_util.get_tag())
        self.assertTrue(focus_hash.__class__ is typedefs.FocusHash)
        focus_hash = cast(typedefs.FocusHash, focus_hash)
        self.assertTrue(focus_hash.identifier)


class TestOpenURL(unittest.TestCase):
    @patch("builtins.print", autospec=True)
    def test_open_url(self, mock_print: MagicMock) -> None:
        browse.open_url('asdf')
        mock_print.assert_called_with('asdf')


class FullTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_sys_argv = sys.argv
        self.test_dir = BASE_DIRECTORY / 'test_dir'
        test_file = self.test_dir / 'test_file'
        os.makedirs(self.test_dir, exist_ok=True)
        with open(test_file, 'w'):
            pass

    def tearDown(self) -> None:
        sys.argv = self.original_sys_argv
        os.chdir(BASE_DIRECTORY)
        shutil.rmtree(self.test_dir)

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
        os.chdir(self.test_dir)
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
        os.chdir(self.test_dir)
        sys_argv = ['asdf', '.']
        expected = (
            'https://github.com/albertyw/git-browse/'
            'tree/master/test_dir/'
        )
        self.check_main(sys_argv, expected, mock_open_url)

    def check_main(
        self, sys_argv: list[str], expected: str, mock_open_url: MagicMock
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
