#!/usr/bin/env python3

try:
    import configparser
except ImportError:
    raise ImportError("Must be using Python 3")

import argparse
import os
import re
import subprocess
import sys
import webbrowser


USER_REGEX = '(?P<user>[\w\.@:\/~_-]+)'
REPOSITORY_REGEX = '(?P<repository>[\w\.@:\/~_-]+)'
GITHUB_SSH_URL = 'git@github.com:%s/%s' % (USER_REGEX, REPOSITORY_REGEX)
GITHUB_HTTPS_URL = 'https://github.com/%s/%s' % (USER_REGEX, REPOSITORY_REGEX)
UBER_GITOLITE_URL = 'gitolite@code.uber.internal:%s' % (REPOSITORY_REGEX)


class GithubHost(object):
    GITHUB_URL = "https://github.com/"

    def __init__(self, user, repository):
        self.user = user
        self.repository = repository

    @staticmethod
    def create(url_regex_match):
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        user = url_regex_match.group('user')
        return GithubHost(user, repository)

    def get_url(self, git_object):
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

    def commit_hash_url(self, repository_url, focus_hash):
        repository_url = "%s/commit/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def root_url(self, repository_url, focus_object):
        return repository_url

    def directory_url(self, repository_url, focus_object):
        repository_url = "%s/tree/master/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(self, repository_url, focus_object):
        repository_url = "%s/blob/master/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def valid_focus_object(self, arg):
        return None


class PhabricatorHost(object):
    PHABRICATOR_OBJECT_REGEX = '^[DT][0-9]+$'

    def __init__(self):
        pass

    @staticmethod
    def create(url_regex_match=None):
        return PhabricatorHost()

    def get_url(self, git_object):
        path = git_object.identifier
        # arc browse requires an object, provide the root object by default
        if git_object.is_root():
            path = '.'
        command = ['arc', 'browse']
        if path:
            command.append(path)
        return command

    def valid_focus_object(self, arg):
        if re.search(self.PHABRICATOR_OBJECT_REGEX, arg):
            return PhabricatorObject(arg)
        return None


HOST_REGEXES = {
    GITHUB_SSH_URL: GithubHost,
    GITHUB_HTTPS_URL: GithubHost,
    UBER_GITOLITE_URL: PhabricatorHost,
}


class GitObject(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def is_commit_hash(self):
        return False

    def is_root(self):
        return False

    def is_directory(self):
        return False


class FocusObject(GitObject):
    def is_root(self):
        return self.identifier == os.sep

    def is_directory(self):
        return self.identifier[-1] == os.sep

    @staticmethod
    def default():
        return FocusObject(os.sep)


class FocusHash(GitObject):
    def is_commit_hash(self):
        return True


class PhabricatorObject(GitObject):
    pass


def get_repository_root():
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


def get_git_config():
    repository_root = get_repository_root()
    git_config_path = os.path.join(repository_root, '.git', 'config')
    return git_config_path


def get_git_url(git_config_file):
    config = configparser.ConfigParser()
    config.read(git_config_file)
    try:
        git_url = config['remote "origin"']['url']
    except KeyError:
        raise RuntimeError("git config file not parseable")
    return git_url


def parse_git_url(git_url):
    for regex, host_class in HOST_REGEXES.items():
        match = re.search(regex, git_url)
        if match:
            break
    if not match:
        raise ValueError("git url not parseable")
    host = host_class.create(match)
    return host


def get_repository_host():
    git_config_file = get_git_config()
    git_url = get_git_url(git_config_file)
    repo_host = parse_git_url(git_url)
    return repo_host


def get_git_object(focus_object, path, host):
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


def get_commit_hash(identifier):
    command = ['git', 'show', identifier]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    out, err = process.communicate()
    if process.returncode != 0:
        return None
    commit_hash = out.split("\n")[0].split(" ")[1]
    return FocusHash(commit_hash)


def open_url(url, dry_run=False):
    print(url)
    if dry_run:
        return
    if url.__class__ is list:
        subprocess.call(url)
        return
    if sys.platform == 'darwin':
        webbrowser.open(url)


def main():
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
    args = parser.parse_args()

    host = get_repository_host()
    path = os.path.join(os.getcwd(), args.path)
    git_object = get_git_object(args.target, path, host)
    url = host.get_url(git_object)
    open_url(url, args.dry_run)


if __name__ == "__main__":
    main()
