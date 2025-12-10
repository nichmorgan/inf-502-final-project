"""Polyfactory-based factories for domain entities."""

from datetime import datetime, timedelta

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain.entities.repo import RepoInfoEntity, TimeseriesDataPoint


class TimeseriesDataPointFactory(ModelFactory[TimeseriesDataPoint]):
    """Factory for TimeseriesDataPoint."""

    __model__ = TimeseriesDataPoint

    @classmethod
    def date(cls) -> str:
        """Generate a random date string."""
        random_date = datetime.now() - timedelta(days=cls.__random__.randint(1, 365))
        return random_date.strftime("%Y-%m-%d")

    @classmethod
    def value(cls) -> int:
        """Generate a random metric value."""
        return cls.__random__.randint(0, 1000)


class RepoInfoEntityFactory(ModelFactory[RepoInfoEntity]):
    """Factory for RepoInfoEntity."""

    __model__ = RepoInfoEntity

    @classmethod
    def provider(cls) -> str:
        """Generate a provider name."""
        return cls.__faker__.random_element(["github"])

    @classmethod
    def owner(cls) -> str:
        """Generate an owner name."""
        return cls.__faker__.user_name()

    @classmethod
    def repo(cls) -> str:
        """Generate a repository name."""
        return cls.__faker__.word()

    @classmethod
    def open_prs_count(cls) -> int:
        """Generate open PRs count."""
        return cls.__random__.randint(0, 100)

    @classmethod
    def closed_prs_count(cls) -> int:
        """Generate closed PRs count."""
        return cls.__random__.randint(0, 500)

    @classmethod
    def users_count(cls) -> int:
        """Generate users count."""
        return cls.__random__.randint(1, 50)

    @classmethod
    def oldest_pr(cls) -> datetime | None:
        """Generate oldest PR date."""
        if cls.__random__.choice([True, False]):
            return datetime.now() - timedelta(days=cls.__random__.randint(30, 365))
        return None

    @classmethod
    def open_prs(cls) -> list[TimeseriesDataPoint]:
        """Generate open PRs timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 10))

    @classmethod
    def closed_prs(cls) -> list[TimeseriesDataPoint]:
        """Generate closed PRs timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 10))

    @classmethod
    def users(cls) -> list[TimeseriesDataPoint]:
        """Generate users timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 10))


@pytest.fixture
def timeseries_datapoint_factory():
    """Provide TimeseriesDataPoint factory instance."""
    return TimeseriesDataPointFactory()


@pytest.fixture
def repo_info_entity_factory():
    """Provide RepoInfoEntity factory instance."""
    return RepoInfoEntityFactory()
