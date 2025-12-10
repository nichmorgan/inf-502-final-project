"""Polyfactory-based factories for schemas."""

from datetime import datetime, timedelta

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from app.infrastructure.schemas.repo_info_schema import (
    CreateRepoInfoSchema,
    FilterRepoInfoSchema,
    UpdateRepoInfoSchema,
)

from .entity_factories import TimeseriesDataPointFactory


class CreateRepoInfoSchemaFactory(ModelFactory[CreateRepoInfoSchema]):
    """Factory for CreateRepoInfoSchema."""

    __model__ = CreateRepoInfoSchema

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
        return cls.__faker__.word() + "-" + cls.__faker__.word()

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
    def open_prs(cls) -> list:
        """Generate open PRs timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 5))

    @classmethod
    def closed_prs(cls) -> list:
        """Generate closed PRs timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 5))

    @classmethod
    def users(cls) -> list:
        """Generate users timeseries."""
        return TimeseriesDataPointFactory.batch(size=cls.__random__.randint(0, 5))


class UpdateRepoInfoSchemaFactory(ModelFactory[UpdateRepoInfoSchema]):
    """Factory for UpdateRepoInfoSchema."""

    __model__ = UpdateRepoInfoSchema


class FilterRepoInfoSchemaFactory(ModelFactory[FilterRepoInfoSchema]):
    """Factory for FilterRepoInfoSchema."""

    __model__ = FilterRepoInfoSchema

    @classmethod
    def full_name(cls) -> str | None:
        """Generate a full repository name."""
        if cls.__random__.choice([True, False]):
            provider = cls.__faker__.random_element(["github"])
            owner = cls.__faker__.user_name()
            repo = cls.__faker__.word() + "-" + cls.__faker__.word()
            return f"{provider}/{owner}/{repo}"
        return None


@pytest.fixture
def create_repo_info_schema_factory():
    """Provide CreateRepoInfoSchema factory instance."""
    return CreateRepoInfoSchemaFactory()


@pytest.fixture
def update_repo_info_schema_factory():
    """Provide UpdateRepoInfoSchema factory instance."""
    return UpdateRepoInfoSchemaFactory()


@pytest.fixture
def filter_repo_info_schema_factory():
    """Provide FilterRepoInfoSchema factory instance."""
    return FilterRepoInfoSchemaFactory()


