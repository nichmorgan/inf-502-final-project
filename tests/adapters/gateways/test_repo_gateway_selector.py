import pytest
from typing import Type
from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.adapters.gateways.github_gateway import GithubGateway
from app.use_cases.ports.repo_port import RepoPort


class MockGitlabGateway(RepoPort):
    """Mock GitLab gateway for testing."""
    provider = "gitlab"

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
    provider = "bitbucket"

    def get_open_pull_requests_count(self) -> int:
        return 0

    def get_closed_pull_requests_count(self) -> int:
        return 0

    def get_users_count(self) -> int:
        return 0

    def get_oldest_pull_request_date(self):
        return None


@pytest.fixture
def selector_with_github_only() -> RepoGatewaySelector:
    return RepoGatewaySelector(GithubGateway)


@pytest.fixture
def selector_with_multiple_gateways() -> RepoGatewaySelector:
    return RepoGatewaySelector(GithubGateway, MockGitlabGateway, MockBitbucketGateway)


def test_select_gateway_returns_github_for_github_provider(
    selector_with_github_only: RepoGatewaySelector,
):
    # Arrange
    provider = "github"

    # Act
    gateway = selector_with_github_only.select_gateway(provider)

    # Assert
    assert gateway == GithubGateway


def test_select_gateway_returns_none_for_unsupported_provider(
    selector_with_github_only: RepoGatewaySelector,
):
    # Arrange
    provider = "gitlab"

    # Act
    gateway = selector_with_github_only.select_gateway(provider)

    # Assert
    assert gateway is None


@pytest.mark.parametrize(
    "provider,expected_gateway",
    [
        ("github", GithubGateway),
        ("gitlab", MockGitlabGateway),
        ("bitbucket", MockBitbucketGateway),
    ],
)
def test_select_gateway_with_multiple_gateways(
    selector_with_multiple_gateways: RepoGatewaySelector,
    provider: str,
    expected_gateway: Type[RepoPort],
):
    # Act
    gateway = selector_with_multiple_gateways.select_gateway(provider)

    # Assert
    assert gateway == expected_gateway


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
    selector = RepoGatewaySelector(GithubGateway, MockGitlabGateway, MockBitbucketGateway)

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
