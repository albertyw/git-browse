from __future__ import annotations

from abc import ABCMeta, abstractmethod
import os
import re
from typing import Match, Optional


USER_REGEX = "(?P<user>[\\w\\.@:\\/~_-]+)"
REPOSITORY_REGEX = "(?P<repository>[\\w\\.@:\\/~_-]+)"
ACCOUNT_REGEX = "(?P<account>[\\w\\.@:\\/~_-]+)"


class GitConfig(object):
    def __init__(self, git_url: str, default_branch: str) -> None:
        self.git_url = git_url
        self.default_branch = default_branch
        self.url_regex_match: Optional[Match[str]] = None

    def try_url_match(self, regex: str) -> bool:
        match = re.search(regex, self.git_url)
        if match:
            self.url_regex_match = match
            return True
        return False


class Host(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user(self) -> str:  # pragma: no cover
        pass
    @user.setter
    @abstractmethod
    def user(self, user: str) -> None:  # pragma: no cover
        pass

    @property
    @abstractmethod
    def repository(self) -> str:  # pragma: no cover
        pass

    @repository.setter
    @abstractmethod
    def repository(self, repository: str) -> None:  # pragma: no cover
        pass

    @staticmethod
    @abstractmethod
    def create(git_config: GitConfig) -> Host:  # pragma: no cover
        pass

    @abstractmethod
    def set_host_class(self, host_class: type[Host]) -> None:  # pragma: no cover
        pass

    @abstractmethod
    def get_url(self, git_object: GitObject) -> str:  # pragma: no cover
        pass


class GitObject:
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_commit_hash(self) -> bool:
        return False

    def is_root(self) -> bool:
        return False

    def is_directory(self) -> bool:
        return False


class FocusObject(GitObject):
    def is_root(self) -> bool:
        return self.identifier == os.sep

    def is_directory(self) -> bool:
        return self.identifier[-1] == os.sep

    @staticmethod
    def default() -> FocusObject:
        return FocusObject(os.sep)


class FocusHash(GitObject):
    def is_commit_hash(self) -> bool:
        return True
