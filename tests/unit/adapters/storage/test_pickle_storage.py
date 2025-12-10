"""Tests for PickleStorage."""

import tempfile
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
    return tmp_path / "test_storage.pickle"


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


@pytest.fixture
def sample_create_schema():
    """Create a sample create schema."""
    return schemas.CreateRepoInfoSchema(
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=datetime(2024, 1, 1),
        users_count=5,
        open_prs=[],
        closed_prs=[],
        users=[],
    )


@pytest.mark.asyncio
async def test_create_one(storage: PickleStorage, sample_create_schema):
    """Test creating a new entity."""
    # Act
    result = await storage.create_one(sample_create_schema)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.provider == "github"
    assert result.owner == "test_owner"
    assert result.repo == "test_repo"


@pytest.mark.asyncio
async def test_get_one_existing(storage: PickleStorage, sample_create_schema):
    """Test getting an existing entity."""
    # Arrange
    created = await storage.create_one(sample_create_schema)

    # Act
    result = await storage.get_one(created.id)

    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.provider == "github"


@pytest.mark.asyncio
async def test_get_one_non_existing(storage: PickleStorage):
    """Test getting a non-existing entity."""
    # Act
    result = await storage.get_one(999)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_many_without_filter(storage: PickleStorage, sample_create_schema):
    """Test getting many entities without filter."""
    # Arrange
    await storage.create_one(sample_create_schema)
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

    # Act
    result = await storage.get_many(None)

    # Assert
    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_many_with_filter(storage: PickleStorage):
    """Test getting many entities with filter."""
    # Arrange
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

    # Act
    filter_schema = schemas.FilterRepoInfoSchema(full_name="github/owner1/repo1")
    result = await storage.get_many(filter_schema)

    # Assert
    assert len(result) == 1
    assert result[0].owner == "owner1"


@pytest.mark.asyncio
async def test_get_many_with_pagination(storage: PickleStorage):
    """Test getting many entities with pagination."""
    # Arrange
    for i in range(5):
        await storage.create_one(
            schemas.CreateRepoInfoSchema(
                provider="github",
                owner=f"owner{i}",
                repo=f"repo{i}",
                open_prs_count=10,
                closed_prs_count=20,
                oldest_pr=datetime(2024, 1, 1),
                users_count=5,
                open_prs=[],
                closed_prs=[],
                users=[],
            )
        )

    # Act
    result = await storage.get_many(None, skip=1, limit=2)

    # Assert
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_one_existing(storage: PickleStorage, sample_create_schema):
    """Test updating an existing entity."""
    # Arrange
    created = await storage.create_one(sample_create_schema)
    update_schema = schemas.UpdateRepoInfoSchema(open_prs_count=99)

    # Act
    result = await storage.update_one(created.id, update_schema)

    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.open_prs_count == 99
    assert result.owner == "test_owner"  # Other fields unchanged


@pytest.mark.asyncio
async def test_update_one_non_existing(storage: PickleStorage):
    """Test updating a non-existing entity."""
    # Arrange
    update_schema = schemas.UpdateRepoInfoSchema(open_prs_count=99)

    # Act
    result = await storage.update_one(999, update_schema)

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_delete_one_existing(storage: PickleStorage, sample_create_schema):
    """Test deleting an existing entity."""
    # Arrange
    created = await storage.create_one(sample_create_schema)

    # Act
    result = await storage.delete_one(created.id)

    # Assert
    assert result is True
    assert await storage.get_one(created.id) is None


@pytest.mark.asyncio
async def test_delete_one_non_existing(storage: PickleStorage):
    """Test deleting a non-existing entity."""
    # Act
    result = await storage.delete_one(999)

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_persistence_across_instances(temp_storage_path, sample_create_schema):
    """Test that data persists across storage instances."""
    # Arrange - Create first instance and add data
    storage1 = PickleStorage[
        entities.RepoInfoEntity,
        schemas.CreateRepoInfoSchema,
        schemas.UpdateRepoInfoSchema,
        schemas.FilterRepoInfoSchema,
    ](path=temp_storage_path)
    created = await storage1.create_one(sample_create_schema)

    # Act - Create second instance
    storage2 = PickleStorage[
        entities.RepoInfoEntity,
        schemas.CreateRepoInfoSchema,
        schemas.UpdateRepoInfoSchema,
        schemas.FilterRepoInfoSchema,
    ](path=temp_storage_path)
    result = await storage2.get_one(created.id)

    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.provider == "github"
