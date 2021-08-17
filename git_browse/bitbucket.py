from typing import Match, Type

from . import types


BITBUCKET_HOST = '(?P<host>bitbucket\\.org)'
BITBUCKET_SSH_URL = 'git@%s:%s/%s' % \
    (BITBUCKET_HOST, types.USER_REGEX, types.REPOSITORY_REGEX)
BITBUCKET_HTTPS_URL = 'https://%s@%s/%s/%s' % (
    types.ACCOUNT_REGEX, BITBUCKET_HOST, types.USER_REGEX,
    types.REPOSITORY_REGEX
)


class BitbucketHost(types.Host):
    BITBUCKET_URL = "https://bitbucket.org/"
    user: str = ''
    repository: str = ''

    def __init__(self, user: str, repository: str) -> None:
        self.user = user
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'types.Host':
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        user = url_regex_match.group('user')
        return BitbucketHost(user, repository)

    def set_host_class(self, host_class: Type[types.Host]) -> None:
        return

    def get_url(self, git_object: 'types.GitObject') -> str:
        repository_url = "%s%s/%s" % (
            self.BITBUCKET_URL,
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
            focus_hash: 'types.GitObject') -> str:
        repository_url = "%s/commits/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def root_url(
        self, repository_url: str, focus_object: 'types.GitObject'
    ) -> str:
        return repository_url

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'types.GitObject') -> str:
        repository_url = "%s/src/%s/%s" % (
            repository_url,
            "master",
            focus_object.identifier
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: 'types.GitObject'
    ) -> str:
        repository_url = "%s/src/%s/%s" % (
            repository_url,
            "master",
            focus_object.identifier
        )
        return repository_url
