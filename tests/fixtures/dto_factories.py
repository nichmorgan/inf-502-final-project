"""Polyfactory-based factories for DTOs."""

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory

from app.domain.dto import RepoSourceEntity


class RepoSourceEntityFactory(ModelFactory[RepoSourceEntity]):
    """Factory for RepoSourceEntity."""

    __model__ = RepoSourceEntity

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


@pytest.fixture
def repo_source_factory():
    """Provide RepoSourceEntity factory instance."""
    return RepoSourceEntityFactory()
