from git_browse import typedefs


GITLAB_HOST = "(?P<host>gitlab\\.com)"
GITLAB_SSH_URL = "git@%s:%s/%s" % (
    GITLAB_HOST,
    typedefs.USER_REGEX,
    typedefs.REPOSITORY_REGEX,
)
GITLAB_HTTPS_URL = "https://%s/%s/%s" % (
    GITLAB_HOST,
    typedefs.USER_REGEX,
    typedefs.REPOSITORY_REGEX,
)
GITLAB_URL = "https://gitlab.com/"


class GitlabHost(typedefs.Host):
    user: str = ""
    repository: str = ""

    def __init__(
        self,
        git_config: typedefs.GitConfig,
        user: str,
        repository: str,
    ) -> None:
        self.git_config = git_config
        self.user = user
        self.repository = repository

    @staticmethod
    def create(git_config: typedefs.GitConfig) -> typedefs.Host:
        assert git_config.url_regex_match
        repository = git_config.url_regex_match.group("repository")
        if repository[-4:] == ".git":
            repository = repository[:-4]
        user = git_config.url_regex_match.group("user")
        return GitlabHost(git_config, user, repository)

    def set_host_class(self, host_class: type[typedefs.Host]) -> None:
        return

    def get_url(self, git_object: typedefs.GitObject) -> str:
        repository_url = "%s%s/%s" % (GITLAB_URL, self.user, self.repository)
        if git_object.is_commit_hash():
            return self.commit_hash_url(repository_url, git_object)
        if git_object.is_root():
            return self.root_url(repository_url, git_object)
        if git_object.is_directory():
            return self.directory_url(repository_url, git_object)
        return self.file_url(repository_url, git_object)

    def commit_hash_url(
        self, repository_url: str, focus_hash: "typedefs.GitObject"
    ) -> str:
        repository_url = "%s/-/commit/%s" % (
            repository_url,
            focus_hash.identifier,
        )
        return repository_url

    def root_url(
        self, repository_url: str, focus_object: typedefs.GitObject
    ) -> str:
        return repository_url

    def directory_url(
        self, repository_url: str, focus_object: "typedefs.GitObject"
    ) -> str:
        repository_url = "%s/-/tree/%s/%s" % (
            repository_url,
            self.git_config.default_branch,
            focus_object.identifier,
        )
        return repository_url

    def file_url(
        self, repository_url: str, focus_object: typedefs.GitObject
    ) -> str:
        repository_url = "%s/-/blob/%s/%s" % (
            repository_url,
            self.git_config.default_branch,
            focus_object.identifier,
        )
        return repository_url
