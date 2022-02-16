import json
import os
import pathlib
import tempfile
from typing import cast
import unittest
from unittest.mock import patch

from git_browse import phabricator, typedefs
from git_browse.tests import test_util


class TestPhabricatorHost(unittest.TestCase):
    def setUp(self) -> None:
        self.phabricator_host = phabricator.PhabricatorHost()
        self.phabricator_url = 'https://example.com'
        self.repository_callsign = 'ASDF'
        self.default_branch = 'master'
        self.phabricator_host.phabricator_url = self.phabricator_url
        self.phabricator_host.repository_callsign = self.repository_callsign
        self.phabricator_host.default_branch = self.default_branch
        self.focus_object = typedefs.FocusObject('/')
        self.focus_hash = typedefs.FocusHash(test_util.get_tag())

        self.arcconfig_data = {
            'phabricator.uri': self.phabricator_url,
            'repository.callsign': self.repository_callsign,
            'git.default-relative-commit': 'origin/master',
        }
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir_name = pathlib.Path(self.temp_dir.name)
        self.arcconfig_file = self.temp_dir_name / '.arcconfig'
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(self.arcconfig_data))

    def tearDown(self) -> None:
        os.remove(self.arcconfig_file)
        self.temp_dir.cleanup()

    def test_create(self) -> None:
        repo = 'gitolite@code.uber.internal:a/b'
        git_config = typedefs.GitConfig(repo, 'master')
        git_config.try_url_match(phabricator.UBER_SSH_GITOLITE_URL)
        with patch('git_browse.browse.get_repository_root') as mock_root:
            mock_root.return_value = self.temp_dir_name
            host = phabricator.PhabricatorHost.create(git_config)
        phabricator_host = cast(phabricator.PhabricatorHost, host)
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
        self.phabricator_host.set_host_class(phabricator.PhabricatorHost)

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

    def test_parse_arcconfig_no_callsign(self) -> None:
        del self.arcconfig_data['repository.callsign']
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(self.arcconfig_data))
        with self.assertRaises(RuntimeError):
            self.phabricator_host._parse_arcconfig(self.temp_dir_name)

    def test_parse_arcconfig_no_url(self) -> None:
        del self.arcconfig_data['phabricator.uri']
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(self.arcconfig_data))
        with self.assertRaises(RuntimeError):
            self.phabricator_host._parse_arcconfig(self.temp_dir_name)

    def test_parse_arcconfig_url_trailing_slash(self) -> None:
        self.arcconfig_data['phabricator.uri'] += '/'
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(self.arcconfig_data))
        self.phabricator_host._parse_arcconfig(self.temp_dir_name)
        self.assertEqual(
            self.phabricator_host.phabricator_url,
            self.phabricator_url,
        )

    def test_parse_arcconfig_no_default_branch(self) -> None:
        del self.arcconfig_data['git.default-relative-commit']
        with open(self.arcconfig_file, 'w') as handle:
            handle.write(json.dumps(self.arcconfig_data))
        self.phabricator_host._parse_arcconfig(self.temp_dir_name)
        self.assertEqual(self.phabricator_host.default_branch, 'master')

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
