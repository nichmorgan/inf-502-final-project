"""Tests for GetRepoInfoBySourceUseCase."""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from pytest_mock import MockerFixture

from app.domain import dto, entities
from app.use_cases.get_repo_info_by_source import GetRepoInfoBySourceUseCase


@pytest.fixture
def mock_gateway(mocker: MockerFixture):
    """Mock gateway."""
    gateway = mocker.AsyncMock()
    gateway.get_open_pull_requests_count.return_value = 10
    gateway.get_closed_pull_requests_count.return_value = 20
    gateway.get_users_count.return_value = 5
    gateway.get_oldest_pull_request_date.return_value = datetime(2024, 1, 1)
    gateway.get_timeseries_open_pull_requests.return_value = {}
    gateway.get_timeseries_closed_pull_requests.return_value = {}
    gateway.get_timeseries_users.return_value = {}
    return gateway


@pytest.fixture
def mock_gateway_selector(mocker: MockerFixture, mock_gateway):
    """Mock gateway selector."""
    selector = mocker.MagicMock()
    selector.providers = ["github"]
    selector.return_value = mock_gateway
    return selector


@pytest.fixture
def mock_storage(mocker: MockerFixture):
    """Mock storage."""
    storage = mocker.AsyncMock()
    storage.get_many.return_value = []
    storage.create_one.return_value = entities.RepoInfoEntity(
        id=1,
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
        created_at=datetime.now(),
    )
    return storage


@pytest.fixture
def use_case(mock_gateway_selector, mock_storage):
    """Create use case instance."""
    return GetRepoInfoBySourceUseCase(
        gateway_selector=mock_gateway_selector,
        storage=mock_storage,
        time_to_live_seconds=3600,
    )


@pytest.mark.asyncio
async def test_execute_fetches_from_gateway_when_not_in_storage(
    use_case: GetRepoInfoBySourceUseCase,
    mock_gateway: AsyncMock,
    mock_storage: AsyncMock,
):
    """Test that use case fetches from gateway when data is not in storage."""
    # Arrange
    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")
    mock_storage.get_many.return_value = []

    # Act
    result = await use_case.execute(source)

    # Assert
    assert result is not None
    mock_storage.get_many.assert_called_once()
    mock_gateway.get_open_pull_requests_count.assert_called_once_with(
        owner="test_owner", repo="test_repo"
    )
    mock_gateway.get_closed_pull_requests_count.assert_called_once_with(
        owner="test_owner", repo="test_repo"
    )
    mock_gateway.get_users_count.assert_called_once_with(
        owner="test_owner", repo="test_repo"
    )
    mock_storage.create_one.assert_called_once()


@pytest.mark.asyncio
async def test_execute_returns_from_storage_when_cache_valid(
    use_case: GetRepoInfoBySourceUseCase,
    mock_gateway: AsyncMock,
    mock_storage: AsyncMock,
):
    """Test that use case returns from storage when cache is valid."""
    # Arrange
    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")
    cached_entity = entities.RepoInfoEntity(
        id=2,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=15,
        closed_prs_count=25,
        oldest_pr=datetime(2024, 1, 1),
        users_count=8,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    mock_storage.get_many.return_value = [cached_entity]

    # Act
    result = await use_case.execute(source)

    # Assert
    assert result == cached_entity
    mock_storage.get_many.assert_called_once()
    mock_gateway.get_open_pull_requests_count.assert_not_called()
    mock_storage.create_one.assert_not_called()


@pytest.mark.asyncio
async def test_execute_raises_error_for_unsupported_provider(
    use_case: GetRepoInfoBySourceUseCase, mock_gateway_selector: MockerFixture
):
    """Test that use case raises error for unsupported provider."""
    # Arrange
    source = dto.RepoSourceEntity(
        provider="unsupported", owner="test_owner", repo="test_repo"
    )
    mock_gateway_selector.providers = ["github"]

    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported provider"):
        await use_case.execute(source)


def test_execute_sync_calls_execute(
    mock_gateway_selector,
    mocker: MockerFixture,
):
    """Test that execute_sync properly calls async execute."""
    # Arrange
    mock_storage = mocker.AsyncMock()
    mock_storage.get_many.return_value = []
    mock_storage.create_one.return_value = entities.RepoInfoEntity(
        id=1,
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
        created_at=datetime.now(),
    )

    use_case = GetRepoInfoBySourceUseCase(
        gateway_selector=mock_gateway_selector,
        storage=mock_storage,
        time_to_live_seconds=3600,
    )

    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")

    # Act
    result = use_case.execute_sync(source)

    # Assert
    assert result is not None
