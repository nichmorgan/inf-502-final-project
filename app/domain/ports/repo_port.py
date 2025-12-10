from abc import ABC, abstractmethod
from datetime import datetime


class RepoPort(ABC):
    @abstractmethod
    async def get_open_pull_requests_count(self, *, owner: str, repo: str) -> int:
        pass

    @abstractmethod
    async def get_closed_pull_requests_count(self, *, owner: str, repo: str) -> int:
        pass

    @abstractmethod
    async def get_users_count(self, *, owner: str, repo: str) -> int:
        pass

    @abstractmethod
    async def get_oldest_pull_request_date(
        self, *, owner: str, repo: str
    ) -> datetime | None:
        pass

    @abstractmethod
    async def get_timeseries_open_pull_requests(
        self, *, owner: str, repo: str
    ) -> dict[datetime, int]:
        """Returns a dictionary mapping datetime to open PR count."""
        pass

    @abstractmethod
    async def get_timeseries_closed_pull_requests(
        self, *, owner: str, repo: str
    ) -> dict[datetime, int]:
        """Returns a dictionary mapping datetime to closed PR count."""
        pass

    @abstractmethod
    async def get_timeseries_users(
        self, *, owner: str, repo: str
    ) -> dict[datetime, int]:
        """Returns a dictionary mapping datetime to user count."""
        pass
