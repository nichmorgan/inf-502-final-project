import pytest
from datetime import datetime

from app.use_cases.ports.repo_port import RepoPort


class ConcreteRepoPort(RepoPort):
    """Concrete implementation of RepoPort for testing."""

    def __init__(self, owner: str, repo: str) -> None:
        super().__init__(owner, repo)

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
    port = ConcreteRepoPort(owner, repo)

    # Assert
    assert port._owner == owner
    assert port._repo == repo


def test_repo_port_cannot_be_instantiated():
    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        RepoPort("owner", "repo")  # type: ignore


def test_repo_port_abstract_methods_must_be_implemented():
    # Arrange
    class IncompleteGateway(RepoPort):
        # Missing implementations of abstract methods
        pass

    # Act & Assert
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        IncompleteGateway("owner", "repo")  # type: ignore


def test_concrete_repo_port_methods():
    # Arrange
    port = ConcreteRepoPort("owner", "repo")

    # Act & Assert
    assert port.get_open_pull_requests_count() == 10
    assert port.get_closed_pull_requests_count() == 20
    assert port.get_users_count() == 5
    assert port.get_oldest_pull_request_date() == datetime(2024, 1, 1)
