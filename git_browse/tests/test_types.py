import unittest

from git_browse import typedefs


class GitObject(unittest.TestCase):
    def test_is_directory(self) -> None:
        obj = typedefs.GitObject('/asdf')
        self.assertFalse(obj.is_directory())


class FocusObject(unittest.TestCase):
    def test_init(self) -> None:
        obj = typedefs.FocusObject('/asdf')
        self.assertEqual(obj.identifier, '/asdf')

    def test_is_root(self) -> None:
        obj = typedefs.FocusObject('/')
        self.assertTrue(obj.is_root())

    def test_is_not_root(self) -> None:
        obj = typedefs.FocusObject('/asdf/')
        self.assertFalse(obj.is_root())

    def test_is_directory(self) -> None:
        obj = typedefs.FocusObject('/asdf/')
        self.assertTrue(obj.is_directory())

    def test_is_not_directory(self) -> None:
        obj = typedefs.FocusObject('/asdf')
        self.assertFalse(obj.is_directory())

    def test_default(self) -> None:
        obj = typedefs.FocusObject.default()
        self.assertTrue(obj.is_root())


class FocusHash(unittest.TestCase):
    def test_init(self) -> None:
        obj = typedefs.FocusHash('abcde')
        self.assertEqual(obj.identifier, 'abcde')

    def test_is_commit_hash(self) -> None:
        obj = typedefs.FocusHash('abcde')
        self.assertTrue(obj.is_commit_hash())
