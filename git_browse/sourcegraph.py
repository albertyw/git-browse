from typing import Match, Optional, Type

from git_browse import phabricator, typedefs


class SourcegraphHost(typedefs.Host):
    PUBLIC_SOURCEGRAPH_URL = 'https://sourcegraph.com/'
    UBER_SOURCEGRAPH_URL = 'https://sourcegraph.uberinternal.com/'
    user: str = ''
    repository: str = ''

    def __init__(self, host: str, repository: str):
        self.host_class: Optional[Type[typedefs.Host]] = None
        self.host = host
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'typedefs.Host':
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

    def set_host_class(self, host_class: Type[typedefs.Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: 'typedefs.GitObject') -> str:
        sourcegraph_url = self.PUBLIC_SOURCEGRAPH_URL
        if self.host_class == phabricator.PhabricatorHost:
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
            focus_hash: 'typedefs.GitObject') -> str:
        repository_url = "%s/-/commit/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'typedefs.GitObject') -> str:
        repository_url = "%s/-/tree/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: 'typedefs.GitObject'
    ) -> str:
        repository_url = "%s/-/blob/%s" % (
            repository_url,
            focus_object.identifier
        )
        return repository_url
