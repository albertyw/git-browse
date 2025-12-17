import json
import pathlib

from git_browse import typedefs


UBER_HOST = "(?P<host>code\\.uber\\.internal)"
UBER_CONFIG_HOST = "(?P<host>objectconfig)"
UBER_SSH_GITOLITE_URL = "gitolite@%s:%s" % (
    UBER_HOST,
    typedefs.REPOSITORY_REGEX,
)
UBER_HTTPS_GITOLITE_URL = "https://%s/%s/%s" % (
    UBER_HOST,
    typedefs.USER_REGEX,
    typedefs.REPOSITORY_REGEX,
)
UBER_OC_URL = "oc://%s/%s" % (
    UBER_CONFIG_HOST,
    typedefs.REPOSITORY_REGEX,
)
DEFAULT_BRANCH = "master"


class PhabricatorHost(typedefs.Host):
    user: str = ""
    repository: str = ""

    def __init__(self) -> None:
        self.phabricator_url = ""
        self.repository_callsign = ""
        self.default_branch = ""

    @staticmethod
    def create(git_config: typedefs.GitConfig) -> typedefs.Host:
        # Fix circular import
        from git_browse import browse  # noqa: PLC0415

        host = PhabricatorHost()
        host._parse_arcconfig(browse.get_repository_root())
        return host

    def set_host_class(self, host_class: type[typedefs.Host]) -> None:
        return

    def _parse_arcconfig(self, repository_root: pathlib.Path) -> None:
        arcconfig_file = repository_root / ".arcconfig"
        try:
            with open(arcconfig_file, "r") as handle:
                data = handle.read()
        except FileNotFoundError as err:
            raise FileNotFoundError(
                'Cannot find a ".arcconfig" file to parse '
                "for repository configuration.  Expected file at %s."
                % arcconfig_file,
            ) from err
        try:
            arcconfig_data = json.loads(data)
        except json.decoder.JSONDecodeError as err:
            raise RuntimeError('Cannot parse ".arcconfig" file as json') from err
        self.repository_callsign = arcconfig_data.get("repository.callsign")
        if not self.repository_callsign:
            raise RuntimeError("Cannot get repository callsign")
        self.phabricator_url = arcconfig_data.get("phabricator.uri")
        if not self.phabricator_url:
            self.phabricator_url = arcconfig_data.get("conduit_uri")
            if not self.phabricator_url:
                raise RuntimeError("Cannot get phabricator url")
        self.phabricator_url = self.phabricator_url.rstrip("/")
        default_branch = arcconfig_data.get(
            "git.default-relative-commit", DEFAULT_BRANCH,
        )
        if "/" in default_branch:
            default_branch = default_branch.split("/", 1)[1]
        self.default_branch = default_branch

    def get_url(self, git_object: typedefs.GitObject) -> str:
        if git_object.is_commit_hash():
            return self.commit_hash_url(git_object)
        if git_object.is_root():
            return self.root_url(git_object)
        return self.file_url(git_object)

    def commit_hash_url(self, focus_hash: typedefs.GitObject) -> str:
        repository_url = "%s/r%s%s" % (
            self.phabricator_url,
            self.repository_callsign,
            focus_hash.identifier,
        )
        return repository_url

    def root_url(self, focus_object: typedefs.GitObject) -> str:
        repository_url = "%s/diffusion/%s/repository/%s/" % (
            self.phabricator_url,
            self.repository_callsign,
            self.default_branch,
        )
        return repository_url

    def file_url(self, focus_object: typedefs.GitObject) -> str:
        repository_url = "%s/diffusion/%s/browse/%s/%s" % (
            self.phabricator_url,
            self.repository_callsign,
            self.default_branch,
            focus_object.identifier,
        )
        return repository_url
