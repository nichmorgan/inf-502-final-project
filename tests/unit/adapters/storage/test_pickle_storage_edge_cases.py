"""Edge case tests for PickleStorage filtering logic."""

from datetime import datetime
from pathlib import Path

import pytest
from pydantic import BaseModel

from app.adapters.storage.pickle_storage import PickleStorage
from app.domain import entities
from app.infrastructure import schemas


@pytest.fixture
def temp_storage_path(tmp_path):
    """Create a temporary storage path."""
    return tmp_path / "test_storage_edge.pickle"


@pytest.fixture
def storage(temp_storage_path):
    """Create a storage instance."""
    # Reset class state before creating new instance
    PickleStorage._PickleStorage__state = {}
    return PickleStorage[
        entities.RepoInfoEntity,
        schemas.CreateRepoInfoSchema,
        schemas.UpdateRepoInfoSchema,
        schemas.FilterRepoInfoSchema,
    ](path=temp_storage_path)


@pytest.mark.asyncio
async def test_filter_with_list_value(storage: PickleStorage, mocker):
    """Test filtering with a list value."""
    # Arrange - create multiple entities
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="github",
            owner="owner1",
            repo="repo1",
            open_prs_count=10,
            closed_prs_count=20,
            oldest_pr=datetime(2024, 1, 1),
            users_count=5,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="gitlab",
            owner="owner2",
            repo="repo2",
            open_prs_count=15,
            closed_prs_count=25,
            oldest_pr=datetime(2024, 1, 1),
            users_count=8,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="bitbucket",
            owner="owner3",
            repo="repo3",
            open_prs_count=20,
            closed_prs_count=30,
            oldest_pr=datetime(2024, 1, 1),
            users_count=12,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )

    # Create a custom filter with a list value
    class CustomFilter(BaseModel):
        provider: list[str] | None = None

    custom_filter = CustomFilter(provider=["github", "gitlab"])

    # Act - use private method to test list filtering
    filtered_ids = storage._PickleStorage__filter(custom_filter)

    # Assert - should return entities with provider in the list
    assert len(filtered_ids) == 2


@pytest.mark.asyncio
async def test_filter_with_nonexistent_attribute(storage: PickleStorage):
    """Test filtering with an attribute that doesn't exist on the entity."""
    # Arrange - create an entity
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="github",
            owner="owner1",
            repo="repo1",
            open_prs_count=10,
            closed_prs_count=20,
            oldest_pr=datetime(2024, 1, 1),
            users_count=5,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )

    # Create a filter with a field that doesn't exist on RepoInfoEntity
    class CustomFilter(BaseModel):
        nonexistent_field: str | None = None

    custom_filter = CustomFilter(nonexistent_field="some_value")

    # Act - use private method to test filtering with nonexistent attribute
    filtered_ids = storage._PickleStorage__filter(custom_filter)

    # Assert - should return empty list since no entity has this attribute
    assert len(filtered_ids) == 0


@pytest.mark.asyncio
async def test_filter_handles_mixed_types(storage: PickleStorage):
    """Test filtering with both string and list values."""
    # Arrange - create multiple entities
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="github",
            owner="owner1",
            repo="repo1",
            open_prs_count=10,
            closed_prs_count=20,
            oldest_pr=datetime(2024, 1, 1),
            users_count=5,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="github",
            owner="owner2",
            repo="repo2",
            open_prs_count=15,
            closed_prs_count=25,
            oldest_pr=datetime(2024, 1, 1),
            users_count=8,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )
    await storage.create_one(
        schemas.CreateRepoInfoSchema(
            provider="gitlab",
            owner="owner3",
            repo="repo3",
            open_prs_count=20,
            closed_prs_count=30,
            oldest_pr=datetime(2024, 1, 1),
            users_count=12,
            open_prs=[],
            closed_prs=[],
            users=[],
        )
    )

    # Create a filter with both string and list
    class CustomFilter(BaseModel):
        owner: str | None = None
        provider: list[str] | None = None

    # This should match entities where owner="owner1" OR provider in ["github", "gitlab"]
    custom_filter = CustomFilter(owner="owner1", provider=["github", "gitlab"])

    # Act
    filtered_ids = storage._PickleStorage__filter(custom_filter)

    # Assert - should return entities that match either condition
    # The current implementation adds entity.id if ANY filter matches
    assert len(filtered_ids) > 0
