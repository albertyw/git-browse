from abc import ABCMeta, abstractmethod
import os
from typing import Match, Type


class Host(metaclass=ABCMeta):
    @property
    @abstractmethod
    def user(self) -> str:
        pass

    @user.setter
    def user(self, user: str) -> None:
        pass

    @property
    @abstractmethod
    def repository(self) -> str:
        pass

    @repository.setter
    def repository(self, repository: str) -> None:
        pass

    @staticmethod
    @abstractmethod
    def create(url_regex_match: Match[str]) -> 'Host':
        pass

    @abstractmethod
    def set_host_class(self, host_class: 'Type[Host]') -> None:
        pass

    @abstractmethod
    def get_url(self, git_object: 'GitObject') -> str:
        pass


class GitObject(object):
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
    def default() -> 'FocusObject':
        return FocusObject(os.sep)


class FocusHash(GitObject):
    def is_commit_hash(self) -> bool:
        return True
