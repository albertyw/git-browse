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


class TestGetRepositoryHost(unittest.TestCase):
    pass


class TestGetFocusObject(unittest.TestCase):
    pass


class TestOpenURL(unittest.TestCase):
    pass
