import json
import os
import pathlib
import re
import shutil
import sys
import tempfile
from typing import List, cast
import unittest
from unittest.mock import MagicMock, patch

from git_browse import browse
from git_browse.tests import test_util

BASE_DIRECTORY = pathlib.Path(__file__).parents[2]


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


class TestBitbucketHost(unittest.TestCase):
    def setUp(self) -> None:
        self.host = browse.BitbucketHost('albertyw', 'git-browse')
        self.repository_url = 'https://bitbucket.org/albertyw/git-browse'
        self.focus_object = browse.FocusObject('/')
        self.focus_hash = browse.FocusHash(test_util.get_tag())

    def test_init(self) -> None:
        host = browse.BitbucketHost('user', 'repository')
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
            'https://bitbucket.org/albertyw/git-browse/src/master/asdf/'
        )

    def test_file_url(self) -> None:
        self.focus_object.identifier = 'README.md'
        url = self.host.file_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url,
            'https://bitbucket.org/albertyw/git-browse/src/master/README.md'
        )

    def test_commit_hash_url(self) -> None:
        url = self.host.commit_hash_url(
            self.repository_url,
            self.focus_hash
        )
        self.assertEqual(
            url,
            'https://bitbucket.org/albertyw/git-browse/commits/%s'
            % test_util.get_tag()
        )


class TestPhabricatorHost(unittest.TestCase):
    def setUp(self) -> None:
        self.phabricator_host = browse.PhabricatorHost()
        self.phabricator_url = 'https://example.com'
        self.repository_callsign = 'ASDF'
        self.default_branch = 'master'
        self.phabricator_host.phabricator_url = self.phabricator_url
        self.phabricator_host.repository_callsign = self.repository_callsign
        self.phabricator_host.default_branch = self.default_branch
        self.focus_object = browse.FocusObject('/')
        self.focus_hash = browse.FocusHash(test_util.get_tag())

        arcconfig_data = {
            'phabricator.uri': self.phabricator_url,
            'repository.callsign': self.repository_callsign,
            'git.default-relative-commit': 'origin/master',
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = pathlib.Path(self.temp_dir.name)
        self.arcconfig_file = self.temp_dir_name / '.arcconfig'
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(arcconfig_data))

    def tearDown(self) -> None:
        os.remove(self.arcconfig_file)
        self.temp_dir.cleanup()

    def test_create(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b'
        match = re.search(browse.UBER_SSH_GITOLITE_URL, repo)
        assert match is not None
        with patch('git_browse.browse.get_repository_root') as mock_root:
            mock_root.return_value = self.temp_dir_name
            host = browse.PhabricatorHost.create(match)
        phabricator_host = cast(browse.PhabricatorHost, host)
        self.assertEqual(
            phabricator_host.phabricator_url,
            self.phabricator_url,
        )
        self.assertEqual(
            phabricator_host.repository_callsign,
            self.repository_callsign,
        )
        self.assertEqual(
            phabricator_host.default_branch,
            self.default_branch,
        )

    def test_set_host_class(self) -> None:
        self.phabricator_host.set_host_class(browse.PhabricatorHost)

    def test_parse_arcconfig(self) -> None:
        self.phabricator_host._parse_arcconfig(self.temp_dir_name)
        self.assertEqual(
            self.phabricator_host.phabricator_url,
            self.phabricator_url,
        )
        self.assertEqual(
            self.phabricator_host.repository_callsign,
            self.repository_callsign,
        )

    def test_parse_arcconfig_no_config(self) -> None:
        random_path = pathlib.Path('asdf')
        with self.assertRaises(FileNotFoundError):
            self.phabricator_host._parse_arcconfig(random_path)

    def test_parse_arcconfig_invalid_config(self) -> None:
        with open(self.arcconfig_file, 'w') as handle:
            handle.write('asdf')
        with self.assertRaises(RuntimeError):
            self.phabricator_host._parse_arcconfig(self.temp_dir_name)

    def test_get_url(self) -> None:
        url = self.phabricator_host.get_url(self.focus_object)
        self.assertEqual(
            url,
            'https://example.com/diffusion/ASDF/repository/master/',
        )

    def test_root_url(self) -> None:
        url = self.phabricator_host.root_url(
            self.focus_object,
        )
        self.assertEqual(
            url,
            'https://example.com/diffusion/ASDF/repository/master/',
        )

    def test_file_url(self) -> None:
        self.focus_object.identifier = 'README.md'
        url = self.phabricator_host.file_url(
            self.focus_object,
        )
        self.assertEqual(
            url,
            'https://example.com/diffusion/ASDF/browse/master/README.md',
        )

    def test_commit_hash_url(self) -> None:
        url = self.phabricator_host.commit_hash_url(
            self.focus_hash
        )
        self.assertEqual(
            url,
            'https://example.com/rASDF%s'
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
        expected = BASE_DIRECTORY / '.git' / 'config'
        self.assertEqual(directory, expected)

    def test_submodule_get(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        config_dir = BASE_DIRECTORY / '.git'
        data = 'gitdir: %s' % config_dir
        with open(pathlib.Path(temp_dir.name) / '.git', 'w') as handle:
            handle.write(data)
        os.chdir(temp_dir.name)
        directory = browse.get_git_config()
        expected = config_dir / 'config'
        self.assertEqual(directory, expected)
        temp_dir.cleanup()


class GetGitURL(unittest.TestCase):
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
        git_url = browse.get_git_url(self.git_config_file_name)
        git_url = git_url.replace('.git', '')
        expected = [
            'git@github.com:albertyw/git-browse',
            'https://github.com/albertyw/git-browse',
        ]
        self.assertIn(git_url, expected)

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
        config_file_name = pathlib.Path(config_file.name)
        git_url = browse.get_git_url(config_file_name)
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
        self.assertTrue(focus_object.__class__ is browse.FocusHash)

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
        self.assertTrue(focus_hash.__class__ is browse.FocusHash)
        focus_hash = cast(browse.FocusHash, focus_hash)
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
