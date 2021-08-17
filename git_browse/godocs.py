from typing import Match, Optional, Type

from . import phabricator, types


class GodocsHost(types.Host):
    PUBLIC_GODOCS_URL = 'https://pkg.go.dev/'
    UBER_GODOCS_URL = 'https://eng.uberinternal.com/docs/api/go/pkg/'
    user: str = ''
    repository: str = ''

    def __init__(self, host: str, repository: str):
        self.host_class: Optional[Type[types.Host]] = None
        self.host = host
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'types.Host':
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

    def set_host_class(self, host_class: Type[types.Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: 'types.GitObject') -> str:
        godocs_url = self.PUBLIC_GODOCS_URL
        if self.host_class == phabricator.PhabricatorHost:
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
            focus_hash: 'types.GitObject') -> str:
        raise NotImplementedError("Cannot look up commits in godocs")

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'types.GitObject') -> str:
        repository_url = "%s/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: 'types.GitObject'
    ) -> str:
        raise NotImplementedError("Cannot look up individual files in godocs")
