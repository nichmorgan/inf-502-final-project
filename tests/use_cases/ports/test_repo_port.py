import pytest
from datetime import datetime

from app.use_cases.ports.repo_port import RepoPort


class ConcreteRepoPort(RepoPort):
    """Concrete implementation of RepoPort for testing."""
    provider = "test_provider"

    def get_open_pull_requests_count(self) -> int:
        return 10

    def get_closed_pull_requests_count(self) -> int:
        return 20

    def get_users_count(self) -> int:
        return 5

    def get_oldest_pull_request_date(self) -> datetime | None:
        return datetime(2024, 1, 1)


def test_repo_port_initialization():
    # Arrange
    owner = "test_owner"
    repo = "test_repo"

    # Act
    port = ConcreteRepoPort(owner=owner, repo=repo)

    # Assert
    assert port._owner == owner
    assert port._repo == repo


def test_repo_port_provider_attribute():
    # Arrange & Act
    port = ConcreteRepoPort(owner="owner", repo="repo")

    # Assert
    assert port.provider == "test_provider"
    assert ConcreteRepoPort.provider == "test_provider"


def test_repo_port_cannot_be_instantiated():
    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        RepoPort(owner="owner", repo="repo")  # type: ignore


def test_repo_port_requires_provider_attribute():
    # Arrange
    class IncompleteGateway(RepoPort):
        # Missing provider attribute
        def get_open_pull_requests_count(self) -> int:
            return 0

        def get_closed_pull_requests_count(self) -> int:
            return 0

        def get_users_count(self) -> int:
            return 0

        def get_oldest_pull_request_date(self) -> datetime | None:
            return None

    # Act & Assert
    # This should not raise during instantiation, but accessing provider will fail
    gateway = IncompleteGateway(owner="owner", repo="repo")
    # The provider attribute won't exist since it's not defined
    assert not hasattr(gateway, "provider") or gateway.provider is None


def test_repo_port_abstract_methods_must_be_implemented():
    # Arrange
    class IncompleteGateway(RepoPort):
        provider = "incomplete"
        # Missing implementations of abstract methods

    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteGateway(owner="owner", repo="repo")  # type: ignore


def test_concrete_repo_port_methods():
    # Arrange
    port = ConcreteRepoPort(owner="owner", repo="repo")

    # Act & Assert
    assert port.get_open_pull_requests_count() == 10
    assert port.get_closed_pull_requests_count() == 20
    assert port.get_users_count() == 5
    assert port.get_oldest_pull_request_date() == datetime(2024, 1, 1)
