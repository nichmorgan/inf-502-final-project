"""Mock implementations for storage-related components."""

from typing import Any

import pytest
from pytest_mock import MockerFixture

from app.adapters.storage.pickle_storage import PickleStorage
from app.domain import entities
from app.domain.ports.storage_port import StoragePort
from app.infrastructure import schemas
from app.shared.types import RepoInfoStorage


@pytest.fixture
def pickle_storage(tmp_path) -> RepoInfoStorage:
    """Create a PickleStorage instance with temp file path."""
    temp_file_path = tmp_path / "test_storage.pickle"

    return PickleStorage[
        entities.RepoInfoEntity,
        schemas.CreateRepoInfoSchema,
        schemas.UpdateRepoInfoSchema,
        schemas.FilterRepoInfoSchema,
    ](path=temp_file_path)


@pytest.fixture
def mock_storage(mocker: MockerFixture, repo_info_entity_factory) -> StoragePort:
    """Create a mock storage with sample data pre-loaded."""
    storage = mocker.AsyncMock(spec=StoragePort)

    # Generate sample data using factory
    sample_entities = repo_info_entity_factory.batch(size=3)
    storage_data = {entity.id: entity for entity in sample_entities}

    async def get_one_side_effect(entity_id: Any):
        return storage_data.get(entity_id)

    async def get_many_side_effect(filter_dict, *, skip: int = 0, limit: int = 100):
        entities_list = list(storage_data.values())
        return entities_list[skip : skip + limit]

    async def create_one_side_effect(entity):
        new_id = max(storage_data.keys(), default=0) + 1
        new_entity = repo_info_entity_factory.build(**entity.model_dump(), id=new_id)
        storage_data[new_id] = new_entity
        return new_entity

    async def update_one_side_effect(entity_id: Any, entity):
        if entity_id not in storage_data:
            return None
        existing = storage_data[entity_id]
        updated_data = existing.model_dump()
        updated_data.update(entity.model_dump(exclude_none=True))
        updated_entity = repo_info_entity_factory.build(**updated_data)
        storage_data[entity_id] = updated_entity
        return updated_entity

    async def delete_one_side_effect(entity_id: Any):
        if entity_id in storage_data:
            del storage_data[entity_id]
            return True
        return False

    storage.get_one.side_effect = get_one_side_effect
    storage.get_many.side_effect = get_many_side_effect
    storage.create_one.side_effect = create_one_side_effect
    storage.update_one.side_effect = update_one_side_effect
    storage.delete_one.side_effect = delete_one_side_effect

    return storage
