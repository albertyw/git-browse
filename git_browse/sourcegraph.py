from typing import Optional

from git_browse import phabricator, typedefs


PUBLIC_SOURCEGRAPH_URL = "https://sourcegraph.com/"
UBER_SOURCEGRAPH_URL = "https://sg.uberinternal.com/"


class SourcegraphHost(typedefs.Host):
    user: str = ""
    repository: str = ""

    def __init__(
        self,
        git_config: typedefs.GitConfig,
        host: str,
        repository: str,
    ):
        self.host_class: Optional[type[typedefs.Host]] = None
        self.git_config = git_config
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
        return SourcegraphHost(git_config, host, repository)

    def set_host_class(self, host_class: type[typedefs.Host]) -> None:
        self.host_class = host_class

    def get_url(self, git_object: typedefs.GitObject) -> str:
        if self.host_class == phabricator.PhabricatorHost:
            repository_url = "%s%s/%s" % (
                UBER_SOURCEGRAPH_URL,
                self.format_uber_host(self.host),
                self.format_phabricator_repository(),
            )
        else:
            repository_url = "%s%s/%s" % (
                PUBLIC_SOURCEGRAPH_URL,
                self.host,
                self.repository,
            )
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
        repository_url = "%s/-/commit/%s" % (
            repository_url,
            focus_hash.identifier,
        )
        return repository_url

    def directory_url(
        self, repository_url: str, focus_object: typedefs.GitObject,
    ) -> str:
        repository_url = "%s/-/tree/%s" % (
            repository_url,
            focus_object.identifier,
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: typedefs.GitObject,
    ) -> str:
        repository_url = "%s/-/blob/%s" % (
            repository_url,
            focus_object.identifier,
        )
        return repository_url

    def format_uber_host(self, host: str) -> str:
        if host == "objectconfig":
            return "code.uber.internal/uber-objectconfig"
        else:
            return "%s/uber-code" % self.host

    def format_phabricator_repository(self) -> str:
        if self.repository == "lm/fievel":
            return "java-code"
        return self.repository.replace("/", "-").replace("@", "---")
