#!/usr/bin/env python3

import configparser
import os
import re
import subprocess
import sys
import webbrowser


USER_REGEX = '(?P<user>[\w\.@:\/~_-]+)'
REPOSITORY_REGEX = '(?P<repository>[\w\.@:\/~_-]+)'
GITHUB_SSH_URL = 'git@github.com:%s/%s' % (USER_REGEX, REPOSITORY_REGEX)
GITHUB_HTTPS_URL = 'https://github.com/%s/%s' % (USER_REGEX, REPOSITORY_REGEX)
UBER_PHABRICATOR_SSH_URL = 'gitolite@code.uber.internal'


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

    def get_url(self, focus_object):
        repository_url = "%s%s/%s" % (
            self.GITHUB_URL,
            self.user,
            self.repository
        )
        if focus_object.is_root():
            return self.root_url(repository_url, focus_object)
        if focus_object.is_directory:
            return self.directory_url(repository_url, focus_object)
        return self.file_url(repository_url, focus_object)

    def root_url(self, repository_url, focus_object):
        return repository_url

    def directory_url(self, repository_url, focus_object):
        repository_url = "%s/tree/master/%s" % (
            repository_url,
            focus_object.path
        )
        return repository_url

    def file_url(self, repository_url, focus_object):
        repository_url = "%s/blob/master/%s" % (
            repository_url,
            focus_object.path
        )
        return repository_url


class UberPhabricatorHost(object):
    def __init__(self, user, repository):
        pass

    @staticmethod
    def create(url_regex_match):
        return UberPhabricatorHost(None, None)

    def get_url(self, focus_object):
        path = focus_object.path
        # arc browse requires an object, provide the root object by default
        if focus_object.is_root():
            path = '.'
        command = ['arc', 'browse']
        if path:
            command.append(path)
        return command


HOST_REGEXES = {
    GITHUB_SSH_URL: GithubHost,
    GITHUB_HTTPS_URL: GithubHost,
    UBER_PHABRICATOR_SSH_URL: UberPhabricatorHost,
}


class FocusObject(object):
    def __init__(self, path):
        self.path = path

    def is_root(self):
        return self.path == os.sep

    @property
    def is_directory(self):
        return self.path[-1] == os.sep

    @staticmethod
    def default():
        return FocusObject(os.sep)


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


def get_focus_object_path(sys_argv):
    for argv in sys_argv:
        if argv[:7] == '--path=':
            path_override = argv[7:]
            path = os.path.join(os.getcwd(), path_override)
            sys_argv.remove(argv)
            return path
    return os.getcwd()


def get_focus_object(sys_argv, path):
    focus_object = sys_argv[1:]
    if not focus_object:
        return FocusObject.default()
    directory = path
    object_path = os.path.join(directory, focus_object[0])
    object_path = os.path.normpath(object_path)
    if not os.path.exists(object_path):
        error = "specified file does not exist: %s" % object_path
        raise FileNotFoundError(error)
    is_dir = os.path.isdir(object_path) and object_path[-1] != os.sep
    object_path = os.path.relpath(object_path, get_repository_root())
    if is_dir:
        object_path += os.sep
    return FocusObject(object_path)


def open_url(url):
    print(url)
    if url.__class__ is list:
        subprocess.call(url)
        return
    if sys.platform == 'darwin':
        webbrowser.open(url)


def main():
    host = get_repository_host()
    path = get_focus_object_path(sys.argv)
    focus_object = get_focus_object(sys.argv, path=path)
    url = host.get_url(focus_object)
    open_url(url)


if __name__ == "__main__":
    main()
