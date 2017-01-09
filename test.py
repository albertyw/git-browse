import unittest

import browse


class TestGithubHost(unittest.TestCase):
    def test_init(self):
        host = browse.GithubHost('user', 'repository')
        self.assertEqual(host.user, 'user')
        self.assertEqual(host.repository, 'repository')

    def test_get_url(self):
        pass


class TestGetRepositoryHost(unittest.TestCase):
    pass


class TestGetFocusObject(unittest.TestCase):
    pass


class TestOpenURL(unittest.TestCase):
    pass
