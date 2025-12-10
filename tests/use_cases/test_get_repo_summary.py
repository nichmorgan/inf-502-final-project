from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from app.domain import RepoSummaryEntity
from app.domain.entities.repo import RepoSourceEntity
from app.use_cases import GetRepoInfoUseCase
from app.use_cases.ports.repo_port import RepoPort


@pytest.fixture
def mock_gateway_class(mocker: MockerFixture):
    """Mock gateway class that will be returned by the selector."""
    gateway_class = mocker.MagicMock()
    gateway_class.provider_name = "github"
    return gateway_class


@pytest.fixture
def mock_gateway_instance(mocker: MockerFixture):
    """Mock gateway instance that will be created by the gateway class."""
    return mocker.MagicMock(spec=RepoPort)


@pytest.fixture
def mock_gateway_selector(
    mocker: MockerFixture, mock_gateway_class, mock_gateway_instance
):
    """Mock gateway selector that returns the mock gateway class."""
    selector = mocker.MagicMock()
    selector.select_gateway.return_value = mock_gateway_class
    # Configure the gateway class to return the gateway instance when called
    mock_gateway_class.return_value = mock_gateway_instance
    return selector


@pytest.fixture
def use_case(mock_gateway_selector):
    return GetRepoInfoUseCase(gateway_selector=mock_gateway_selector)


def test_execute_with_all_data(
    use_case: GetRepoInfoUseCase,
    mock_gateway_selector: MockerFixture,
    mock_gateway_instance: MockerFixture,
    mock_gateway_class: MockerFixture,
):
    # Arrange
    oldest_date = datetime(2024, 1, 1, 12, 0, 0)
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_instance.get_open_pull_requests_count.return_value = 5  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.return_value = 10  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.return_value = oldest_date  # type: ignore
    mock_gateway_instance.get_users_count.return_value = 15  # type: ignore

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    assert isinstance(result, RepoSummaryEntity)
    assert result.open_prs == 5
    assert result.closed_prs == 10
    assert result.oldest_pr == oldest_date.strftime("%Y-%m-%d")
    assert result.users == 15

    # Verify selector was called with correct provider
    mock_gateway_selector.select_gateway.assert_called_once_with(provider)  # type: ignore

    # Verify gateway was instantiated with correct parameters
    mock_gateway_class.assert_called_once_with(owner, repo)  # type: ignore

    # Verify all gateway methods were called
    mock_gateway_instance.get_open_pull_requests_count.assert_called_once()  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.assert_called_once()  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.assert_called_once()  # type: ignore
    mock_gateway_instance.get_users_count.assert_called_once()  # type: ignore


def test_execute_with_no_oldest_pr_date(
    use_case: GetRepoInfoUseCase,
    mock_gateway_instance: MockerFixture,
):
    # Arrange
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_instance.get_open_pull_requests_count.return_value = 3  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.return_value = 7  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.return_value = None  # type: ignore
    mock_gateway_instance.get_users_count.return_value = 8  # type: ignore

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    assert isinstance(result, RepoSummaryEntity)
    assert result.open_prs == 3
    assert result.closed_prs == 7
    assert result.oldest_pr is None
    assert result.users == 8


def test_execute_with_zero_counts(
    use_case: GetRepoInfoUseCase,
    mock_gateway_instance: MockerFixture,
):
    # Arrange
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_instance.get_open_pull_requests_count.return_value = 0  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.return_value = 0  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.return_value = None  # type: ignore
    mock_gateway_instance.get_users_count.return_value = 0  # type: ignore

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    assert isinstance(result, RepoSummaryEntity)
    assert result.open_prs == 0
    assert result.closed_prs == 0
    assert result.oldest_pr is None
    assert result.users == 0


def test_execute_with_large_numbers(
    use_case: GetRepoInfoUseCase,
    mock_gateway_instance: MockerFixture,
):
    # Arrange
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_instance.get_open_pull_requests_count.return_value = 1000  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.return_value = 5000  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.return_value = datetime(  # type: ignore
        2020, 1, 1
    )
    mock_gateway_instance.get_users_count.return_value = 500  # type: ignore

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    assert result.open_prs == 1000
    assert result.closed_prs == 5000
    assert result.oldest_pr == "2020-01-01"
    assert result.users == 500


def test_execute_gateway_interaction_order(
    use_case: GetRepoInfoUseCase,
    mock_gateway_instance: MockerFixture,
):
    # Arrange
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"
    call_order = []

    mock_gateway_instance.get_open_pull_requests_count.side_effect = (  # type: ignore
        lambda: call_order.append("open_prs") or 5
    )
    mock_gateway_instance.get_closed_pull_requests_count.side_effect = (  # type: ignore
        lambda: call_order.append("closed_prs") or 10
    )
    mock_gateway_instance.get_oldest_pull_request_date.side_effect = (  # type: ignore
        lambda: call_order.append("oldest_date") or datetime(2024, 1, 1)
    )
    mock_gateway_instance.get_users_count.side_effect = (  # type: ignore
        lambda: call_order.append("users") or 15
    )

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    assert result is not None
    assert len(call_order) == 4
    assert "open_prs" in call_order
    assert "closed_prs" in call_order
    assert "oldest_date" in call_order
    assert "users" in call_order


def test_execute_raises_error_for_unsupported_provider(
    use_case: GetRepoInfoUseCase,
    mock_gateway_selector: MockerFixture,
):
    # Arrange
    provider = "unsupported_provider"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_selector.select_gateway.return_value = None  # type: ignore

    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported provider"):
        use_case.execute(RepoSourceEntity(provider=provider, owner=owner, repo=repo))

    mock_gateway_selector.select_gateway.assert_called_once_with(provider)  # type: ignore


def test_execute_creates_correct_entity_hierarchy(
    use_case: GetRepoInfoUseCase,
    mock_gateway_instance: MockerFixture,
):
    # Arrange
    provider = "github"
    owner = "test_owner"
    repo = "test_repo"

    mock_gateway_instance.get_open_pull_requests_count.return_value = 10  # type: ignore
    mock_gateway_instance.get_closed_pull_requests_count.return_value = 20  # type: ignore
    mock_gateway_instance.get_oldest_pull_request_date.return_value = datetime(  # type: ignore
        2023, 5, 1
    )
    mock_gateway_instance.get_users_count.return_value = 30  # type: ignore

    # Act
    result = use_case.execute(
        RepoSourceEntity(provider=provider, owner=owner, repo=repo)
    )

    # Assert
    # Verify the entity structure is correctly composed
    assert isinstance(result, RepoSummaryEntity)
    assert result.open_prs == 10
    assert result.closed_prs == 20
    assert result.oldest_pr == "2023-05-01"
    assert result.users == 30
