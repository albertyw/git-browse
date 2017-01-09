import os
import unittest

import browse


class TestGithubHost(unittest.TestCase):
    def setUp(self):
        self.github_host = browse.GithubHost('albertyw', 'git-browse')
        self.repository_url = 'https://github.com/albertyw/git-browse'
        self.focus_object = browse.FocusObject('/')

    def test_init(self):
        host = browse.GithubHost('user', 'repository')
        self.assertEqual(host.user, 'user')
        self.assertEqual(host.repository, 'repository')

    def test_get_url(self):
        url = self.github_host.get_url(self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_root_url(self):
        url = self.github_host.root_url(self.repository_url, self.focus_object)
        self.assertEqual(url, self.repository_url)

    def test_directory_url(self):
        self.focus_object.path = '/asdf/'
        url = self.github_host.directory_url(
            self.repository_url,
            self.focus_object
        )
        self.assertEqual(
            url,
            'https://github.com/albertyw/git-browse/tree/master/asdf/'
        )

    def test_file_url(self):
        self.focus_object.path = '/README.md'
        url = self.github_host.file_url(self.repository_url, self.focus_object)
        self.assertEqual(
            url,
            'https://github.com/albertyw/git-browse/blob/master/README.md'
        )


class FocusObject(unittest.TestCase):
    def test_init(self):
        obj = browse.FocusObject('/asdf')
        self.assertEqual(obj.path, '/asdf')

    def test_is_root(self):
        obj = browse.FocusObject('/')
        self.assertTrue(obj.is_root)

    def test_is_not_root(self):
        obj = browse.FocusObject('/asdf/')
        self.assertFalse(obj.is_root)

    def test_is_directory(self):
        obj = browse.FocusObject('/asdf/')
        self.assertTrue(obj.is_directory)

    def test_is_not_directory(self):
        obj = browse.FocusObject('/asdf')
        self.assertFalse(obj.is_directory)


class GetGitconfig(unittest.TestCase):
    def test_get(self):
        current_directory = os.path.dirname(os.path.realpath(__file__))
        os.chdir(current_directory)
        directory = browse.get_git_config()
        expected = os.path.join(current_directory, '.git', 'config')
        self.assertEqual(directory, expected)

    def test_fail_get(self):
        current_directory = os.sep
        os.chdir(current_directory)
        with self.assertRaises(FileNotFoundError):
            browse.get_git_config()


class GetGitURL(unittest.TestCase):
    def setUp(self):
        self.current_directory = os.path.dirname(os.path.realpath(__file__))
        self.git_config_file = os.path.join(
            self.current_directory,
            '.git',
            'config'
        )

    def test_url(self):
        git_url = browse.get_git_url(self.git_config_file)
        self.assertEqual(git_url, 'git@github.com:albertyw/git-browse')

    def test_bad_url(self):
        with self.assertRaises(RuntimeError):
            browse.get_git_url(self.current_directory)


class ParseGitURL(unittest.TestCase):
    def setUp(self):
        self.ssh_url = 'git@github.com:albertyw/git-browse.git'
        self.https_url = 'https://github.com/albertyw/git-browse'
        self.broken_url = 'asdfasdf'

    def test_ssh_url(self):
        host = browse.parse_git_url(self.ssh_url)
        self.assertTrue(host.__class__ is browse.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')

    def test_https_url(self):
        host = browse.parse_git_url(self.https_url)
        self.assertTrue(host.__class__ is browse.GithubHost)
        self.assertEqual(host.user, 'albertyw')
        self.assertEqual(host.repository, 'git-browse')

    def test_broken_url(self):
        with self.assertRaises(ValueError):
            browse.parse_git_url(self.broken_url)


class TestGetRepositoryHost(unittest.TestCase):
    pass


class TestGetFocusObject(unittest.TestCase):
    pass


class TestOpenURL(unittest.TestCase):
    pass
