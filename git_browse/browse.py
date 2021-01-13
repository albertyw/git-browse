#!/usr/bin/env python3

from abc import ABCMeta, abstractmethod
import argparse
import configparser
import os
import re
import subprocess
from typing import Dict, Match, Optional, Type
import webbrowser


__version__ = '2.9.1'
GITHUB_HOST = '(?P<host>github\\.com)'
UBER_HOST = '(?P<host>code\\.uber\\.internal)'
UBER_CONFIG_HOST = '(?P<host>config\\.uber\\.internal)'
USER_REGEX = '(?P<user>[\\w\\.@:\\/~_-]+)'
REPOSITORY_REGEX = '(?P<repository>[\\w\\.@:\\/~_-]+)'
GITHUB_SSH_URL = 'git@%s:%s/%s' % (GITHUB_HOST, USER_REGEX, REPOSITORY_REGEX)
GITHUB_HTTPS_URL = 'https://%s/%s/%s' % \
    (GITHUB_HOST, USER_REGEX, REPOSITORY_REGEX)
UBER_SSH_GITOLITE_URL = 'gitolite@%s:%s' % (UBER_HOST, REPOSITORY_REGEX)
UBER_SSH_CONFIG_GITOLITE_URL = 'gitolite@%s:%s' % \
    (UBER_CONFIG_HOST, REPOSITORY_REGEX)
UBER_HTTPS_GITOLITE_URL = 'https://%s/%s/%s' % \
    (UBER_HOST, USER_REGEX, REPOSITORY_REGEX)


def copy_text_to_clipboard(text: str) -> None:
    stdin = text.encode('utf-8')
    try:
        subprocess.run(['pbcopy', 'w'], input=stdin, close_fds=True)
    except FileNotFoundError:
        pass


class Host(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user(self) -> str:
        pass

    @user.setter
    def user(self, user: str) -> None:
        pass

    @property
    @abstractmethod
    def repository(self) -> str:
        pass

    @repository.setter
    def repository(self, repository: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        pass

    @abstractmethod
    def set_host_class(self, host_class: 'Type[Host]') -> None:
        pass

    @abstractmethod
    def get_url(self, git_object: 'GitObject') -> str:
        pass

    @abstractmethod
    def valid_focus_object(self, arg: str) -> Optional['GitObject']:
        pass


class GithubHost(Host):
    GITHUB_URL = "https://github.com/"
    user: str = ''
    repository: str = ''

    def __init__(self, user: str, repository: str) -> None:
        self.user = user
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        user = url_regex_match.group('user')
        return GithubHost(user, repository)

    def set_host_class(self, host_class: Type[Host]) -> None:
        return

    def get_url(self, git_object: 'GitObject') -> str:
        repository_url = "%s%s/%s" % (
            self.GITHUB_URL,
            self.user,
            self.repository
        )
        if git_object.is_commit_hash():
            return self.commit_hash_url(repository_url, git_object)
        if git_object.is_root():
            return self.root_url(repository_url, git_object)
        if git_object.is_directory():
            return self.directory_url(repository_url, git_object)
        return self.file_url(repository_url, git_object)

    def commit_hash_url(
            self,
            repository_url: str,
            focus_hash: 'GitObject') -> str:
        repository_url = "%s/commit/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def root_url(self, repository_url: str, focus_object: 'GitObject') -> str:
        return repository_url

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'GitObject') -> str:
        repository_url = "%s/tree/master/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(self, repository_url: str, focus_object: 'GitObject') -> str:
        repository_url = "%s/blob/master/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def valid_focus_object(self, arg: str) -> Optional['GitObject']:
        return None


class PhabricatorHost(Host):
    PHABRICATOR_OBJECT_REGEX = '^[DT][0-9]+$'
    user: str = ''
    repository: str = ''

    def __init__(self) -> None:
        pass

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        return PhabricatorHost()

    def set_host_class(self, host_class: Type[Host]) -> None:
        return

    def get_url(self, git_object: 'GitObject') -> str:
        """
        arc browse will try to open a browser for you.  Instead, configure arc
        browse to send the url to "echo" so that git-browse can open the
        url instead, then reset the arc config
        """
        self.set_arc_browse_echo()
        try:
            url = self.arc_browse_read(git_object)
        finally:
            # Unset arc config even if SubprocessError was encountered earlier
            self.unset_arc_browse_echo()
        return url

    def set_arc_browse_echo(self) -> None:
        command = ['arc', 'set-config', '--local', 'browser', 'echo']
        subprocess.run(command, capture_output=True, check=True)

    def unset_arc_browse_echo(self) -> None:
        command = ['arc', 'set-config', '--local', 'browser', '""']
        subprocess.run(command, capture_output=True, check=True)

    def arc_browse_read(self, git_object: 'GitObject') -> str:
        path = git_object.identifier
        # arc browse requires an object, provide the root object by default
        if git_object.is_root():
            path = '.'
        command = ['arc', 'browse']
        if path:
            command.append(path)
        process = subprocess.run(
            command,
            capture_output=True,
            check=True,
            universal_newlines=True,
        )
        url = process.stdout.strip().split("\n")[-1]
        return url

    def valid_focus_object(self, arg: str) -> Optional['PhabricatorObject']:
        if re.search(self.PHABRICATOR_OBJECT_REGEX, arg):
            return PhabricatorObject(arg)
        return None


class SourcegraphHost(Host):
    PUBLIC_SOURCEGRAPH_URL = 'https://sourcegraph.com/'
    UBER_SOURCEGRAPH_URL = 'https://sourcegraph.uberinternal.com/'
    user: str = ''
    repository: str = ''

    def __init__(self, host: str, repository: str):
        self.host_class: Optional[Type[Host]] = None
        self.host = host
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        host = url_regex_match.group('host')
        try:
            user = url_regex_match.group('user')
            repository = '%s/%s' % (user, repository)
        except IndexError:
            pass
        return SourcegraphHost(host, repository)

    def set_host_class(self, host_class: Type[Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: 'GitObject') -> str:
        sourcegraph_url = self.PUBLIC_SOURCEGRAPH_URL
        if self.host_class == PhabricatorHost:
            sourcegraph_url = self.UBER_SOURCEGRAPH_URL
        repository_url = "%s%s/%s" % (
            sourcegraph_url,
            self.host,
            self.repository
        )
        if git_object.is_commit_hash():
            return self.commit_hash_url(repository_url, git_object)
        if git_object.is_root():
            return repository_url
        if git_object.is_directory():
            return self.directory_url(repository_url, git_object)
        return self.file_url(repository_url, git_object)

    def commit_hash_url(
            self,
            repository_url: str,
            focus_hash: 'GitObject') -> str:
        repository_url = "%s/-/commit/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'GitObject') -> str:
        repository_url = "%s/-/tree/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(self, repository_url: str, focus_object: 'GitObject') -> str:
        repository_url = "%s/-/blob/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def valid_focus_object(self, arg: str) -> Optional['GitObject']:
        return None


class GodocsHost(Host):
    PUBLIC_GODOCS_URL = 'https://pkg.go.dev/'
    UBER_GODOCS_URL = 'https://eng.uberinternal.com/docs/api/go/pkg/'
    user: str = ''
    repository: str = ''

    def __init__(self, host: str, repository: str):
        self.host_class: Optional[Type[Host]] = None
        self.host = host
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        host = url_regex_match.group('host')
        try:
            user = url_regex_match.group('user')
            repository = '%s/%s' % (user, repository)
        except IndexError:
            pass
        return GodocsHost(host, repository)

    def set_host_class(self, host_class: Type[Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: 'GitObject') -> str:
        godocs_url = self.PUBLIC_GODOCS_URL
        if self.host_class == PhabricatorHost:
            godocs_url = self.UBER_GODOCS_URL
        repository_url = "%s%s/%s" % (
            godocs_url,
            self.host,
            self.repository
        )
        if git_object.is_commit_hash():
            return self.commit_hash_url(repository_url, git_object)
        if git_object.is_root():
            return repository_url
        if git_object.is_directory():
            return self.directory_url(repository_url, git_object)
        return self.file_url(repository_url, git_object)

    def commit_hash_url(
            self,
            repository_url: str,
            focus_hash: 'GitObject') -> str:
        raise NotImplementedError("Cannot look up commits in godocs")

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'GitObject') -> str:
        repository_url = "%s/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(self, repository_url: str, focus_object: 'GitObject') -> str:
        raise NotImplementedError("Cannot look up individual files in godocs")

    def valid_focus_object(self, arg: str) -> Optional['GitObject']:
        return None


HOST_REGEXES: Dict[str, Type[Host]] = {
    GITHUB_SSH_URL: GithubHost,
    GITHUB_HTTPS_URL: GithubHost,
    UBER_SSH_GITOLITE_URL: PhabricatorHost,
    UBER_SSH_CONFIG_GITOLITE_URL: PhabricatorHost,
    UBER_HTTPS_GITOLITE_URL: PhabricatorHost,
}


class GitObject(object):
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_commit_hash(self) -> bool:
        return False

    def is_root(self) -> bool:
        return False

    def is_directory(self) -> bool:
        return False


class FocusObject(GitObject):
    def is_root(self) -> bool:
        return self.identifier == os.sep

    def is_directory(self) -> bool:
        return self.identifier[-1] == os.sep

    @staticmethod
    def default() -> 'FocusObject':
        return FocusObject(os.sep)


class FocusHash(GitObject):
    def is_commit_hash(self) -> bool:
        return True


class PhabricatorObject(GitObject):
    pass


def get_repository_root() -> str:
    current_directory = ''
    new_directory = os.getcwd()
    while current_directory != new_directory:
        current_directory = new_directory
        git_config = os.path.join(current_directory, '.git', 'config')
        if os.path.exists(git_config):
            return current_directory
        new_directory = os.path.join(current_directory, '..')
        new_directory = os.path.normpath(new_directory)
    raise FileNotFoundError('.git/config file not found')


def get_git_config() -> str:
    repository_root = get_repository_root()
    git_config_path = os.path.join(repository_root, '.git', 'config')
    return git_config_path


def get_git_url(git_config_file: str) -> str:
    # strict is removed here because gitconfig allows for multiple "fetch" keys
    config = configparser.ConfigParser(strict=False)
    config.read(git_config_file)
    try:
        git_url = config['remote "origin"']['url']
    except KeyError:
        raise RuntimeError("git config file not parseable")
    return git_url


def parse_git_url(
    git_url: str,
    sourcegraph: bool = False,
    godocs: bool = False,
) -> Host:
    for regex, host_class in HOST_REGEXES.items():
        match = re.search(regex, git_url)
        if match:
            break
    if not match:
        raise ValueError("git url not parseable")
    if sourcegraph:
        host = SourcegraphHost.create(match)
        host.set_host_class(host_class)
    elif godocs:
        host = GodocsHost.create(match)
        host.set_host_class(host_class)
    else:
        host = host_class.create(match)
    return host


def get_repository_host(
    sourcegraph: bool = False,
    godocs: bool = False,
) -> Host:
    git_config_file = get_git_config()
    git_url = get_git_url(git_config_file)
    repo_host = parse_git_url(git_url, sourcegraph, godocs)
    return repo_host


def get_git_object(focus_object: str, path: str, host: Host) -> GitObject:
    if not focus_object:
        return FocusObject.default()
    directory = path
    object_path = os.path.join(directory, focus_object)
    object_path = os.path.normpath(object_path)
    if not os.path.exists(object_path):
        focus_hash = get_commit_hash(focus_object)
        if focus_hash:
            return focus_hash
        host_focus_object = host.valid_focus_object(focus_object)
        if host_focus_object:
            return host_focus_object
        error = "specified file does not exist: %s" % object_path
        raise FileNotFoundError(error)
    is_dir = os.path.isdir(object_path) and object_path[-1] != os.sep
    object_path = os.path.relpath(object_path, get_repository_root())
    if is_dir:
        object_path += os.sep
    return FocusObject(object_path)


def get_commit_hash(identifier: str) -> Optional[FocusHash]:
    command = ['git', 'show', identifier, '--no-abbrev-commit']
    process = subprocess.run(
        command,
        capture_output=True,
        universal_newlines=True,
    )
    if process.returncode != 0:
        return None
    commit_hash = process.stdout.split("\n")[0].split(" ")[1]
    return FocusHash(commit_hash)


def open_url(
        url: str,
        dry_run: bool = False,
        copy_clipboard: bool = False,
        ) -> None:
    print(url)
    if copy_clipboard:
        copy_text_to_clipboard(url)
    if not dry_run:
        webbrowser.open(url)


def main() -> None:
    description = "Open repositories, directories, and files in the browser.\n"
    description += "https://github.com/albertyw/git-browse"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'target',
        nargs='?',
        help='file, directory, git hash, or git branch you wish to browse'
    )
    parser.add_argument(
        '--path',
        default='',
        help='relative path to the current git repository'
    )
    parser.add_argument(
        '-d',
        '--dry-run',
        action='store_true',
        help='Do not open the url in the brower, and only print to stdout'
    )
    parser.add_argument(
        '-c',
        '--copy',
        action='store_true',
        help='Copy url to clipboard, if available',
    )
    parser.add_argument(
        '-s',
        '--sourcegraph',
        action='store_true',
        help='Open objects in sourcegraph'
    )
    parser.add_argument(
        '-g',
        '--godocs',
        action='store_true',
        help='Open objects in godocs'
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__,
    )
    args = parser.parse_args()
    if args.sourcegraph and args.godocs:
        print('Sourcegraph and Godocs flags are mutually exclusive')
        return

    host = get_repository_host(args.sourcegraph, args.godocs)
    path = os.path.join(os.getcwd(), args.path)
    git_object = get_git_object(args.target, path, host)
    url = host.get_url(git_object)
    open_url(url, args.dry_run, args.copy)


if __name__ == "__main__":
    main()
