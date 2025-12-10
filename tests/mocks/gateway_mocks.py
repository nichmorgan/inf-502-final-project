"""Mock implementations for gateway-related components."""

from datetime import datetime, timedelta

import pytest
from faker import Faker
from pytest_mock import MockerFixture

from app.adapters.gateways.github_gateway import GithubGateway
from app.domain.ports.repo_port import RepoPort


@pytest.fixture
def mock_github_client(mocker: MockerFixture):
    """Create a mock GitHub client."""
    return mocker.MagicMock()


@pytest.fixture
def github_gateway(mock_github_client) -> GithubGateway:
    """Create a GithubGateway instance with a mock client."""
    return GithubGateway(client=mock_github_client)


@pytest.fixture
def mock_gateway(mocker: MockerFixture, faker: Faker) -> RepoPort:
    """Create a mock gateway with dynamically generated return values."""
    gateway = mocker.AsyncMock(spec=RepoPort)

    # Use faker for dynamic values
    gateway.get_open_pull_requests_count.return_value = faker.random_int(min=0, max=100)
    gateway.get_closed_pull_requests_count.return_value = faker.random_int(min=0, max=500)
    gateway.get_users_count.return_value = faker.random_int(min=1, max=50)
    gateway.get_oldest_pull_request_date.return_value = faker.date_time_between(
        start_date="-1y", end_date="now"
    )
    gateway.get_timeseries_open_pull_requests.return_value = {}
    gateway.get_timeseries_closed_pull_requests.return_value = {}
    gateway.get_timeseries_users.return_value = {}

    return gateway


@pytest.fixture
def mock_gateway_with_timeseries(mocker: MockerFixture, faker: Faker) -> RepoPort:
    """Create a mock gateway with timeseries data."""
    gateway = mocker.AsyncMock(spec=RepoPort)

    # Generate timeseries data
    base_date = datetime.now() - timedelta(days=30)
    timeseries_open = {
        base_date + timedelta(days=i): faker.random_int(min=0, max=50) for i in range(10)
    }
    timeseries_closed = {
        base_date + timedelta(days=i): faker.random_int(min=0, max=30) for i in range(10)
    }
    timeseries_users = {
        base_date + timedelta(days=i): faker.random_int(min=1, max=20) for i in range(10)
    }

    gateway.get_open_pull_requests_count.return_value = faker.random_int(min=0, max=100)
    gateway.get_closed_pull_requests_count.return_value = faker.random_int(min=0, max=500)
    gateway.get_users_count.return_value = faker.random_int(min=1, max=50)
    gateway.get_oldest_pull_request_date.return_value = base_date
    gateway.get_timeseries_open_pull_requests.return_value = timeseries_open
    gateway.get_timeseries_closed_pull_requests.return_value = timeseries_closed
    gateway.get_timeseries_users.return_value = timeseries_users

    return gateway


@pytest.fixture
def mock_gateway_selector(mocker: MockerFixture, mock_gateway: RepoPort):
    """Create a mock gateway selector."""
    selector = mocker.MagicMock()
    selector.providers = ["github"]
    selector.return_value = mock_gateway
    return selector


def create_mock_pr(mocker: MockerFixture, created_at: datetime, closed_at: datetime | None = None):
    """Helper to create a mock PR object."""
    mock_pr = mocker.MagicMock()
    mock_pr.created_at = created_at
    mock_pr.closed_at = closed_at
    return mock_pr


def create_mock_commit(mocker: MockerFixture, author_login: str, commit_date: datetime):
    """Helper to create a mock commit object."""
    mock_commit = mocker.MagicMock()
    mock_commit.author.login = author_login
    mock_commit.commit.author.date = commit_date
    return mock_commit
