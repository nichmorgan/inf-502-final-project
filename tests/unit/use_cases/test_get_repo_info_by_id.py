"""Tests for GetRepoInfoByIdUseCase."""

from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from app.domain import entities
from app.use_cases.get_repo_info_by_id import GetRepoInfoByIdUseCase


@pytest.fixture
def mock_storage(mocker: MockerFixture):
    """Mock storage."""
    storage = mocker.AsyncMock()
    return storage


@pytest.fixture
def use_case(mock_storage):
    """Create use case instance."""
    return GetRepoInfoByIdUseCase(storage=mock_storage)


@pytest.mark.asyncio
async def test_execute_returns_items_for_valid_ids(
    use_case: GetRepoInfoByIdUseCase, mock_storage: MockerFixture
):
    """Test that execute returns items for valid IDs."""
    # Arrange
    entity1 = entities.RepoInfoEntity(
        id="1",
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
        created_at=datetime.now(),
    )
    entity2 = entities.RepoInfoEntity(
        id="2",
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
        created_at=datetime.now(),
    )

    async def get_one_side_effect(id):
        if id == 1:
            return entity1
        elif id == 2:
            return entity2
        return None

    mock_storage.get_one.side_effect = get_one_side_effect

    # Act
    result = await use_case.execute([1, 2])

    # Assert
    assert len(result) == 2
    assert entity1 in result
    assert entity2 in result


@pytest.mark.asyncio
async def test_execute_filters_out_none_results(
    use_case: GetRepoInfoByIdUseCase, mock_storage: MockerFixture
):
    """Test that execute filters out None results for invalid IDs."""
    # Arrange
    entity1 = entities.RepoInfoEntity(
        id="1",
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
        created_at=datetime.now(),
    )

    async def get_one_side_effect(id):
        if id == 1:
            return entity1
        return None

    mock_storage.get_one.side_effect = get_one_side_effect

    # Act
    result = await use_case.execute([1, 999])

    # Assert
    assert len(result) == 1
    assert entity1 in result


@pytest.mark.asyncio
async def test_execute_handles_empty_list(
    use_case: GetRepoInfoByIdUseCase, mock_storage: MockerFixture
):
    """Test that execute handles empty list."""
    # Act
    result = await use_case.execute([])

    # Assert
    assert result == []
    mock_storage.get_one.assert_not_called()


@pytest.mark.asyncio
async def test_execute_handles_duplicate_ids(
    use_case: GetRepoInfoByIdUseCase, mock_storage: MockerFixture
):
    """Test that execute handles duplicate IDs by deduplicating."""
    # Arrange
    entity1 = entities.RepoInfoEntity(
        id="1",
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
        created_at=datetime.now(),
    )

    mock_storage.get_one.return_value = entity1

    # Act
    result = await use_case.execute([1, 1, 1])

    # Assert
    assert len(result) == 1
    mock_storage.get_one.assert_called_once_with(1)


def test_execute_sync_calls_execute(
    use_case: GetRepoInfoByIdUseCase, mock_storage: MockerFixture
):
    """Test that execute_sync properly calls async execute."""
    # Arrange
    entity1 = entities.RepoInfoEntity(
        id="1",
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
        created_at=datetime.now(),
    )
    mock_storage.get_one.return_value = entity1

    # Act
    result = use_case.execute_sync([1])

    # Assert
    assert len(result) == 1
