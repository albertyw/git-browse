#!/usr/bin/python3

import configparser
import os
import re


GITHUB_SSH_URL = 'git@github.com:(?P<user>[\w\.@:\/~_-]+)/(?P<repository>[\w\.@:\/~_-]+)'
GITHUB_HTTPS_URL = 'https://github.com/(?P<user>[\w\.@:\/~_-]+)/(?P<repository>[\w\.@:\/~_-]+)'
HOST_REGEXES = [GITHUB_SSH_URL, GITHUB_HTTPS_URL]


class GithubHost(object):
    GITHUB_URL = "https://github.com/"

    def __init__(self, user, repository):
        self.user = user
        self.repository = repository

    def get_url(self, focus_object):
        repository_url = "%s%s/%s" % (
            self.GITHUB_URL,
            self.user,
            self.repository
        )
        if focus_object.is_root:
            return self.root_url(repository_url, focus_object)
        if focus_object.is_directory:
            return self.directory_url(repository_url, focus_object)
        return self.file_url(repository_url, focus_object)

    def root_url(self, repository_url, focus_object):
        return repository_url

    def directory_url(self, repository_url, focus_object):
        repository_url = "%s/tree/master%s" % (
            repository_url,
            focus_object.path
        )
        return repository_url

    def file_url(self, repository_url, focus_object):
        repository_url = "%s/blob/master%s" % (
            repository_url,
            focus_object.path
        )
        return repository_url


class FocusObject(object):
    def __init__(self, path):
        self.path = path

    @property
    def is_root(self):
        return self.path == '/'

    @property
    def is_directory(self):
        return self.path[-1] == '/'


def get_git_config():
    current_directory = ''
    new_directory = os.getcwd()
    while current_directory != new_directory:
        current_directory = new_directory
        git_config = os.path.join(current_directory, '.git', 'config')
        if os.path.exists(git_config):
            return os.path.normpath(git_config)
        new_directory = os.path.join(current_directory, '..')
        new_directory = os.path.normpath(new_directory)
    raise FileNotFoundError('.git/config file not found')


def get_git_url(git_config_file):
    config = configparser.ConfigParser()
    config.read(git_config_file)
    try:
        git_url = config['remote "origin"']['url']
    except KeyError:
        raise RuntimeError("git config file not parseable")
    return git_url


def parse_git_url(git_url):
    for regex in HOST_REGEXES:
        match = re.search(regex, git_url)
        if match:
            break
    if not match:
        raise ValueError("git url not parseable")
    repository = match.group('repository')
    if repository[-4:] == '.git':
        repository = repository[:-4]
    host = GithubHost(match.group('user'), repository)
    return host


def get_repository_host():
    git_config_file = get_git_config()
    git_url = get_git_url(git_config_file)
    repo_host = parse_git_url(git_url)
    return repo_host


def get_focus_object():
    pass


def open_url(url):
    pass


def main():
    host = get_repository_host()
    focus_object = get_focus_object()
    url = host.get_url(focus_object)
    open_url(url)


if __name__ == '__main__':
    main()
