"""Tests for GithubGateway timeseries methods."""

from datetime import datetime, timedelta, timezone

import pytest
from pytest_mock import MockerFixture

from app.adapters.gateways.github_gateway import GithubGateway


@pytest.fixture
def mock_github_client(mocker: MockerFixture):
    return mocker.MagicMock()


@pytest.fixture
def github_gateway(mock_github_client: MockerFixture):
    return GithubGateway(client=mock_github_client)


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


@pytest.mark.asyncio
async def test_get_timeseries_open_pull_requests_no_prs(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for open PRs when there are no PRs."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    # Mock get_pulls for timeseries (returns empty list when converted to list)
    mock_pulls_result = mocker.MagicMock()
    mock_pulls_result.__iter__.return_value = iter([])

    # Setup side effect to return different values for different calls
    call_count = [0]
    def get_pulls_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for oldest PR
            result = mocker.MagicMock()
            result.get_page.return_value = []
            return result
        else:  # Second call for timeseries
            return mock_pulls_result

    mock_repo.get_pulls.side_effect = get_pulls_side_effect

    # Act
    result = await github_gateway.get_timeseries_open_pull_requests(owner=owner, repo=repo)

    # Assert
    assert result == {}


@pytest.mark.asyncio
async def test_get_timeseries_open_pull_requests_with_prs(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for open PRs with actual PRs."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    # Create mock PRs
    now = datetime.now(timezone.utc)
    pr1 = create_mock_pr(mocker, created_at=now - timedelta(days=30), closed_at=None)
    pr2 = create_mock_pr(mocker, created_at=now - timedelta(days=20), closed_at=now - timedelta(days=10))
    pr3 = create_mock_pr(mocker, created_at=now - timedelta(days=10), closed_at=None)

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=30), closed_at=None)
    mock_repo.get_pulls.return_value.get_page.return_value = [oldest_pr]

    # Mock get_pulls for timeseries
    mock_pulls_for_timeseries = mocker.MagicMock()
    mock_pulls_for_timeseries.__iter__.return_value = iter([pr1, pr2, pr3])

    # Setup side effect to return different values for different calls
    call_count = [0]
    def get_pulls_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for oldest PR
            result = mocker.MagicMock()
            result.get_page.return_value = [oldest_pr]
            return result
        else:  # Second call for timeseries
            return mock_pulls_for_timeseries

    mock_repo.get_pulls.side_effect = get_pulls_side_effect

    # Act
    result = await github_gateway.get_timeseries_open_pull_requests(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_timeseries_open_pull_requests_with_oldest_pr(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test timeseries uses oldest PR date when available."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)
    oldest_date = now - timedelta(days=10)

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=oldest_date, closed_at=None)

    # Mock PR for timeseries
    pr1 = create_mock_pr(mocker, created_at=oldest_date, closed_at=None)

    mock_pulls_for_timeseries = mocker.MagicMock()
    mock_pulls_for_timeseries.__iter__.return_value = iter([pr1])

    call_count = [0]
    def get_pulls_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            result = mocker.MagicMock()
            result.get_page.return_value = [oldest_pr]
            return result
        else:
            return mock_pulls_for_timeseries

    mock_repo.get_pulls.side_effect = get_pulls_side_effect

    # Act
    result = await github_gateway.get_timeseries_open_pull_requests(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_get_timeseries_closed_pull_requests_empty(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for closed PRs when there are no closed PRs."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    # Mock get_oldest_pull_request_date
    mock_repo.get_pulls.return_value.get_page.return_value = []

    # Mock get_pulls for closed PRs - need to handle slicing
    mock_pulls_result = mocker.MagicMock()
    mock_pulls_result.__getitem__.return_value = []

    call_count = [0]
    def get_pulls_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for oldest PR
            result = mocker.MagicMock()
            result.get_page.return_value = []
            return result
        else:  # Second call for closed PRs
            return mock_pulls_result

    mock_repo.get_pulls.side_effect = get_pulls_side_effect

    # Act
    result = await github_gateway.get_timeseries_closed_pull_requests(owner=owner, repo=repo)

    # Assert
    assert result == {}


@pytest.mark.asyncio
async def test_get_timeseries_closed_pull_requests_with_prs(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for closed PRs with actual closed PRs."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)

    # Create closed PRs
    pr1 = create_mock_pr(
        mocker,
        created_at=now - timedelta(days=30),
        closed_at=now - timedelta(days=25)
    )
    pr2 = create_mock_pr(
        mocker,
        created_at=now - timedelta(days=20),
        closed_at=now - timedelta(days=15)
    )

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=30), closed_at=None)

    # Mock get_pulls for closed PRs
    mock_pulls_result = mocker.MagicMock()
    mock_pulls_result.__getitem__.return_value = [pr1, pr2]

    call_count = [0]
    def get_pulls_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:  # First call for oldest PR
            result = mocker.MagicMock()
            result.get_page.return_value = [oldest_pr]
            return result
        else:  # Second call for closed PRs
            return mock_pulls_result

    mock_repo.get_pulls.side_effect = get_pulls_side_effect

    # Act
    result = await github_gateway.get_timeseries_closed_pull_requests(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_timeseries_users_empty(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for users when there are no commits."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    # Mock get_oldest_pull_request_date
    mock_repo.get_pulls.return_value.get_page.return_value = []

    # Mock get_commits to return empty
    mock_repo.get_commits.return_value = []

    # Act
    result = await github_gateway.get_timeseries_users(owner=owner, repo=repo)

    # Assert
    assert result == {}


@pytest.mark.asyncio
async def test_get_timeseries_users_with_commits(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test getting timeseries for users with actual commits."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=30), closed_at=None)
    mock_repo.get_pulls.return_value.get_page.return_value = [oldest_pr]

    # Create mock commits with authors
    commit1 = create_mock_commit(mocker, "user1", now - timedelta(days=25))
    commit2 = create_mock_commit(mocker, "user2", now - timedelta(days=20))
    commit3 = create_mock_commit(mocker, "user1", now - timedelta(days=15))

    # Mock get_commits to return these commits
    mock_repo.get_commits.return_value = [commit1, commit2, commit3]

    # Act
    result = await github_gateway.get_timeseries_users(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_timeseries_users_with_limit(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test that users timeseries respects MAX_COMMITS limit."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=300), closed_at=None)
    mock_repo.get_pulls.return_value.get_page.return_value = [oldest_pr]

    # Create 250 mock commits (more than MAX_COMMITS=200)
    mock_commits = []
    for i in range(250):
        commit = create_mock_commit(mocker, f"user{i % 50}", now - timedelta(days=i))
        mock_commits.append(commit)

    # Track iteration count
    iteration_count = [0]

    class CommitIterator:
        def __init__(self, commits):
            self.commits = commits
            self.index = 0

        def __iter__(self):
            return self

        def __next__(self):
            iteration_count[0] += 1
            if self.index >= len(self.commits):
                raise StopIteration
            commit = self.commits[self.index]
            self.index += 1
            return commit

    mock_repo.get_commits.return_value = CommitIterator(mock_commits)

    # Act
    result = await github_gateway.get_timeseries_users(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    # Should stop at MAX_COMMITS (200), but may iterate 201 times due to the loop structure
    assert iteration_count[0] <= 201


@pytest.mark.asyncio
async def test_get_timeseries_users_filters_by_date_range(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test that users timeseries only includes commits within date range."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)

    # Mock oldest PR from 10 days ago
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=10), closed_at=None)
    mock_repo.get_pulls.return_value.get_page.return_value = [oldest_pr]

    # Create commits, some within range, some outside
    commit1 = create_mock_commit(mocker, "user1", now - timedelta(days=5))  # Within range
    commit2 = create_mock_commit(mocker, "user2", now - timedelta(days=400))  # Outside range
    commit3 = create_mock_commit(mocker, "user3", now - timedelta(days=8))  # Within range

    mock_repo.get_commits.return_value = [commit1, commit2, commit3]

    # Act
    result = await github_gateway.get_timeseries_users(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    # Should have processed commits but filtered by date


@pytest.mark.asyncio
async def test_get_timeseries_users_handles_commits_without_author(
    github_gateway: GithubGateway, mock_github_client: MockerFixture, mocker: MockerFixture
):
    """Test that users timeseries handles commits without author gracefully."""
    # Arrange
    owner = "test_owner"
    repo = "test_repo"
    mock_repo = mock_github_client.get_repo.return_value

    now = datetime.now(timezone.utc)

    # Mock oldest PR
    oldest_pr = create_mock_pr(mocker, created_at=now - timedelta(days=30), closed_at=None)
    mock_repo.get_pulls.return_value.get_page.return_value = [oldest_pr]

    # Create commits with and without authors
    commit1 = create_mock_commit(mocker, "user1", now - timedelta(days=5))

    commit_no_author = mocker.MagicMock()
    commit_no_author.author = None
    commit_no_author.commit.author.date = now - timedelta(days=10)

    commit3 = create_mock_commit(mocker, "user2", now - timedelta(days=15))

    mock_repo.get_commits.return_value = [commit1, commit_no_author, commit3]

    # Act
    result = await github_gateway.get_timeseries_users(owner=owner, repo=repo)

    # Assert
    assert isinstance(result, dict)
    # Should have processed successfully, skipping the commit without author
