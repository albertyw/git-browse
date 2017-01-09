#!/usr/bin/python3


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


def get_repository_host():
    pass


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
