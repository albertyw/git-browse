#!/usr/bin/python3


class GithubHost(object):
    def __init__(self, user, repository):
        self.user = user
        self.repository = repository

    def get_url(self, focus_object):
        pass


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
