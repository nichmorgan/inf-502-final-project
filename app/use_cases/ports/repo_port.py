from abc import ABC, abstractmethod
from datetime import datetime

__all__ = ["RepoPort"]


class RepoPort(ABC):
    def __init__(self, owner: str, repo: str) -> None:
        self._owner = owner
        self._repo = repo

    @abstractmethod
    def get_open_pull_requests_count(self) -> int:
        pass

    @abstractmethod
    def get_closed_pull_requests_count(self) -> int:
        pass

    @abstractmethod
    def get_users_count(self) -> int:
        pass

    @abstractmethod
    def get_oldest_pull_request_date(self) -> datetime | None:
        pass
