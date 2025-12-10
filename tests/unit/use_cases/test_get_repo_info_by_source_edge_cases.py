"""Additional edge case tests for GetRepoInfoBySourceUseCase."""

from datetime import datetime, timedelta

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
    gateway.get_timeseries_open_pull_requests.return_value = {
        datetime(2024, 1, 1): 5,
        datetime(2024, 1, 2): 10,
    }
    gateway.get_timeseries_closed_pull_requests.return_value = {
        datetime(2024, 1, 1): 3,
        datetime(2024, 1, 2): 8,
    }
    gateway.get_timeseries_users.return_value = {
        datetime(2024, 1, 1): 2,
        datetime(2024, 1, 2): 4,
    }
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
    storage.delete_one.return_value = True
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
async def test_execute_refreshes_stale_cache(
    use_case: GetRepoInfoBySourceUseCase,
    mock_gateway,
    mock_storage,
):
    """Test that use case refreshes stale cache."""
    # Arrange
    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")

    # Create a stale cached entity (TTL is 3600 seconds = 1 hour)
    # To make it stale: (updated_at or now()) - created_at >= 3600
    # We set created_at 2 hours ago and updated_at 1 minute ago
    # This means: 1 minute since last update - no, wait that's wrong
    # Actually: (updated_at) - created_at = 2 hours - 1 min ≈ 7140 seconds > 3600
    old_created = datetime.now() - timedelta(hours=2)
    recent_updated = datetime.now() - timedelta(minutes=1)
    stale_entity = entities.RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=5,
        closed_prs_count=10,
        oldest_pr=datetime(2024, 1, 1),
        users_count=3,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=old_created,
        updated_at=recent_updated,
    )
    mock_storage.get_many.return_value = [stale_entity]

    # Act
    result = await use_case.execute(source)

    # Assert
    mock_storage.delete_one.assert_called_once_with(stale_entity.id)
    mock_gateway.get_open_pull_requests_count.assert_called_once()
    mock_storage.create_one.assert_called_once()


@pytest.mark.asyncio
async def test_fill_timeseries_with_data(
    use_case: GetRepoInfoBySourceUseCase,
    mock_gateway,
    mock_storage,
):
    """Test that timeseries data is properly filled."""
    # Arrange
    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")
    mock_storage.get_many.return_value = []

    # Act
    result = await use_case.execute(source)

    # Assert
    # Verify that timeseries methods were called
    mock_gateway.get_timeseries_open_pull_requests.assert_called_once()
    mock_gateway.get_timeseries_closed_pull_requests.assert_called_once()
    mock_gateway.get_timeseries_users.assert_called_once()


@pytest.mark.asyncio
async def test_fill_timeseries_with_empty_data(mock_gateway_selector, mock_storage, mock_gateway):
    """Test fill_timeseries with empty timeseries data."""
    # Arrange
    mock_gateway.get_timeseries_open_pull_requests.return_value = {}
    mock_gateway.get_timeseries_closed_pull_requests.return_value = {}
    mock_gateway.get_timeseries_users.return_value = {}

    use_case = GetRepoInfoBySourceUseCase(
        gateway_selector=mock_gateway_selector,
        storage=mock_storage,
        time_to_live_seconds=3600,
    )

    source = dto.RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")
    mock_storage.get_many.return_value = []

    # Act
    result = await use_case.execute(source)

    # Assert
    assert result is not None
