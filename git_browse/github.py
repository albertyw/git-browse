from typing import Match, Type

from git_browse import typedefs


GITHUB_HOST = '(?P<host>github\\.com)'
GITHUB_SSH_URL = 'git@%s:%s/%s' % \
    (GITHUB_HOST, typedefs.USER_REGEX, typedefs.REPOSITORY_REGEX)
GITHUB_HTTPS_URL = 'https://%s/%s/%s' % \
    (GITHUB_HOST, typedefs.USER_REGEX, typedefs.REPOSITORY_REGEX)


class GithubHost(typedefs.Host):
    GITHUB_URL = "https://github.com/"
    user: str = ''
    repository: str = ''

    def __init__(self, user: str, repository: str) -> None:
        self.user = user
        self.repository = repository

    @staticmethod
    def create(url_regex_match: Match[str]) -> 'typedefs.Host':
        repository = url_regex_match.group('repository')
        if repository[-4:] == '.git':
            repository = repository[:-4]
        user = url_regex_match.group('user')
        return GithubHost(user, repository)

    def set_host_class(self, host_class: Type[typedefs.Host]) -> None:
        return

    def get_url(self, git_object: 'typedefs.GitObject') -> str:
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
            focus_hash: 'typedefs.GitObject') -> str:
        repository_url = "%s/commit/%s" % (
            repository_url,
            focus_hash.identifier
        )
        return repository_url

    def root_url(
        self, repository_url: str, focus_object: 'typedefs.GitObject'
    ) -> str:
        return repository_url

    def directory_url(
            self,
            repository_url: str,
            focus_object: 'typedefs.GitObject') -> str:
        repository_url = "%s/tree/%s/%s" % (
            repository_url,
            "master",
            focus_object.identifier
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: 'typedefs.GitObject'
    ) -> str:
        repository_url = "%s/blob/%s/%s" % (
            repository_url,
            "master",
            focus_object.identifier
        )
        return repository_url
