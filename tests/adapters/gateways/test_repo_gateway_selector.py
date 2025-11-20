import pytest
from typing import Type
from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.adapters.gateways.github_gateway import GithubGateway
from app.use_cases.ports.repo_port import RepoPort


class MockGitlabGateway(RepoPort):
    """Mock GitLab gateway for testing."""

    def __init__(self, owner: str, repo: str) -> None:
        super().__init__(owner, repo)

    def get_open_pull_requests_count(self) -> int:
        return 0

    def get_closed_pull_requests_count(self) -> int:
        return 0

    def get_users_count(self) -> int:
        return 0

    def get_oldest_pull_request_date(self):
        return None


class MockBitbucketGateway(RepoPort):
    """Mock Bitbucket gateway for testing."""

    def __init__(self, owner: str, repo: str) -> None:
        super().__init__(owner, repo)

    def get_open_pull_requests_count(self) -> int:
        return 0

    def get_closed_pull_requests_count(self) -> int:
        return 0

    def get_users_count(self) -> int:
        return 0

    def get_oldest_pull_request_date(self):
        return None


@pytest.fixture
def mock_github_factory(mocker):
    """Factory function that returns a mock GithubGateway."""
    def factory(owner: str, repo: str):
        mock_client = mocker.MagicMock()
        return GithubGateway(owner, repo, client=mock_client)
    return factory


@pytest.fixture
def selector_with_github_only(mock_github_factory) -> RepoGatewaySelector:
    return RepoGatewaySelector({"github": mock_github_factory})


@pytest.fixture
def selector_with_multiple_gateways(mock_github_factory) -> RepoGatewaySelector:
    return RepoGatewaySelector({
        "github": mock_github_factory,
        "gitlab": MockGitlabGateway,
        "bitbucket": MockBitbucketGateway,
    })


def test_select_gateway_returns_github_for_github_provider(
    selector_with_github_only: RepoGatewaySelector,
    mock_github_factory,
):
    # Arrange
    provider = "github"

    # Act
    gateway = selector_with_github_only.select_gateway(provider)

    # Assert
    assert gateway == mock_github_factory


def test_select_gateway_returns_none_for_unsupported_provider(
    selector_with_github_only: RepoGatewaySelector,
):
    # Arrange
    provider = "gitlab"

    # Act
    gateway = selector_with_github_only.select_gateway(provider)

    # Assert
    assert gateway is None


def test_select_gateway_with_multiple_gateways_github(
    selector_with_multiple_gateways: RepoGatewaySelector,
    mock_github_factory,
):
    # Act
    gateway = selector_with_multiple_gateways.select_gateway("github")

    # Assert
    assert gateway == mock_github_factory


def test_select_gateway_with_multiple_gateways_gitlab(
    selector_with_multiple_gateways: RepoGatewaySelector,
):
    # Act
    gateway = selector_with_multiple_gateways.select_gateway("gitlab")

    # Assert
    assert gateway == MockGitlabGateway


def test_select_gateway_with_multiple_gateways_bitbucket(
    selector_with_multiple_gateways: RepoGatewaySelector,
):
    # Act
    gateway = selector_with_multiple_gateways.select_gateway("bitbucket")

    # Assert
    assert gateway == MockBitbucketGateway


def test_selector_with_no_gateways():
    # Arrange
    selector = RepoGatewaySelector()
    provider = "github"

    # Act
    gateway = selector.select_gateway(provider)

    # Assert
    assert gateway is None


def test_selector_providers_property():
    # Arrange
    selector = RepoGatewaySelector({
        "github": MockGitlabGateway,
        "gitlab": MockGitlabGateway,
        "bitbucket": MockBitbucketGateway,
    })

    # Act
    providers = selector.providers

    # Assert
    assert "github" in providers
    assert "gitlab" in providers
    assert "bitbucket" in providers
    assert len(providers) == 3


def test_selector_providers_property_empty():
    # Arrange
    selector = RepoGatewaySelector()

    # Act
    providers = selector.providers

    # Assert
    assert providers == []
