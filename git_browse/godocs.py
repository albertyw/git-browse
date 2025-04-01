from typing import Optional

from git_browse import phabricator, typedefs


PUBLIC_GODOCS_URL = "https://godocs.io/"
UBER_GODOCS_URL = "https://engdocs.uberinternal.com/api/go/pkg"


class GodocsHost(typedefs.Host):
    user: str = ""
    repository: str = ""

    def __init__(
        self,
        git_config: typedefs.GitConfig,
        host: str,
        repository: str,
    ):
        self.git_config = git_config
        self.host_class: Optional[type[typedefs.Host]] = None
        self.host = host
        self.repository = repository

    @staticmethod
    def create(git_config: typedefs.GitConfig) -> typedefs.Host:
        assert git_config.url_regex_match
        repository = git_config.url_regex_match.group("repository")
        if repository[-4:] == ".git":
            repository = repository[:-4]
        host = git_config.url_regex_match.group("host")
        try:
            user = git_config.url_regex_match.group("user")
            repository = "%s/%s" % (user, repository)
        except IndexError:
            pass
        return GodocsHost(git_config, host, repository)

    def set_host_class(self, host_class: type[typedefs.Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: typedefs.GitObject) -> str:
        godocs_url = PUBLIC_GODOCS_URL
        repository_url = "%s%s/%s" % (godocs_url, self.host, self.repository)
        if self.host_class == phabricator.PhabricatorHost:
            repository_url = UBER_GODOCS_URL
        if git_object.is_commit_hash():
            return self.commit_hash_url(repository_url, git_object)
        if git_object.is_root():
            return repository_url
        if git_object.is_directory():
            return self.directory_url(repository_url, git_object)
        return self.file_url(repository_url, git_object)

    def commit_hash_url(
        self, repository_url: str, focus_hash: typedefs.GitObject,
    ) -> str:
        raise NotImplementedError("Cannot look up commits in godocs")

    def directory_url(
        self, repository_url: str, focus_object: typedefs.GitObject,
    ) -> str:
        path = focus_object.identifier
        if repository_url == UBER_GODOCS_URL:
            path = '/'.join(path.split('/')[1:])
        repository_url = "%s/%s" % (repository_url, path)
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: typedefs.GitObject,
    ) -> str:
        raise NotImplementedError("Cannot look up individual files in godocs")
