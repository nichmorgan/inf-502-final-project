from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from app.adapters.gateways.github_gateway import GithubGateway


@pytest.fixture
def mock_github_client(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def github_gateway(mock_github_client: MockerFixture):
    return GithubGateway(client=mock_github_client)


@pytest.mark.asyncio
async def test_get_open_pull_requests_count(
    github_gateway: GithubGateway, mock_github_client: MockerFixture
):
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value
    mock_repo.get_pulls.return_value.totalCount = 5

    # Act
    count = await github_gateway.get_open_pull_requests_count(owner=owner, repo=repo)

    # Assert
    assert count == 5
    mock_github_client.get_repo.assert_called_once_with(f"{owner}/{repo}", lazy=False)
    mock_repo.get_pulls.assert_called_once_with(state="open")


@pytest.mark.asyncio
async def test_get_closed_pull_requests_count(
    github_gateway: GithubGateway, mock_github_client: MockerFixture
):
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value
    mock_repo.get_pulls.return_value.totalCount = 10

    # Act
    count = await github_gateway.get_closed_pull_requests_count(owner=owner, repo=repo)

    # Assert
    assert count == 10
    mock_repo.get_pulls.assert_called_once_with(state="closed")


@pytest.mark.asyncio
async def test_get_users_count(
    github_gateway: GithubGateway, mock_github_client: MockerFixture
):
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value
    mock_repo.get_contributors.return_value.totalCount = 20

    # Act
    count = await github_gateway.get_users_count(owner=owner, repo=repo)

    # Assert
    assert count == 20
    mock_repo.get_contributors.assert_called_once()


@pytest.mark.asyncio
async def test_get_oldest_pull_request_date(
    github_gateway: GithubGateway,
    mock_github_client: MockerFixture,
    mocker: MockerFixture,
):
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value
    mock_pr = mocker.MagicMock()
    mock_pr.created_at = datetime(2024, 1, 1)
    mock_repo.get_pulls.return_value.get_page.return_value = [mock_pr]

    # Act
    date = await github_gateway.get_oldest_pull_request_date(owner=owner, repo=repo)

    # Assert
    assert date == datetime(2024, 1, 1)
    mock_repo.get_pulls.assert_called_once_with(sort="created", direction="asc")


@pytest.mark.asyncio
async def test_get_oldest_pull_request_date_no_prs(
    github_gateway: GithubGateway, mock_github_client: MockerFixture
):
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value
    mock_repo.get_pulls.return_value.get_page.return_value = []

    # Act
    date = await github_gateway.get_oldest_pull_request_date(owner=owner, repo=repo)

    # Assert
    assert date is None
    mock_repo.get_pulls.assert_called_once_with(sort="created", direction="asc")


def test_github_gateway_initializes_with_client(mock_github_client: MockerFixture):
    # Act
    gateway = GithubGateway(client=mock_github_client)

    # Assert
    assert gateway is not None
