import pytest
from datetime import datetime
from nicegui.testing import User
from pytest_mock import MockerFixture
from app.containers import Container
from app.domain.entities.repo import RepoSummaryEntity, RepoSourceEntity
from app.infrastructure.web.pages.comparison import comparison_page


@pytest.fixture
def mock_container(mocker: MockerFixture):
    """Mock the dependency injection container."""
    container = Container()

    # Mock the summary use case
    mock_summary_use_case = mocker.MagicMock()
    mock_summary_use_case.execute.return_value = RepoSummaryEntity(
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs=5,
        closed_prs=10,
        oldest_pr=datetime(2024, 1, 1),
        users=15,
    )

    # Mock the timeseries use case
    mock_timeseries_use_case = mocker.MagicMock()
    mock_timeseries_use_case.execute.return_value = mocker.MagicMock()

    # Mock the gateway selector
    mock_gateway_selector = mocker.MagicMock()
    mock_gateway_selector.providers = ["github"]

    # Override container providers
    container.get_repo_summary_use_case.override(mock_summary_use_case)
    container.get_repo_timeseries_use_case.override(mock_timeseries_use_case)
    container.repo_gateway_selector.override(mock_gateway_selector)

    # Wire the container
    container.wire(modules=["app.infrastructure.web.pages.comparison"])

    yield container

    # Unwire after test
    container.unwire()


@pytest.mark.asyncio
async def test_comparison_page_loads_successfully(user: User, mock_container):
    """Test that the comparison page loads without errors."""
    await user.open("/")

    # Check that the page title is present
    await user.should_see("Repository Comparison")
    await user.should_see("Add Repository")

    # Check that the form elements are present
    await user.should_see("Provider")
    await user.should_see("Owner")
    await user.should_see("Repository")


@pytest.mark.asyncio
async def test_add_repository_button_exists(user: User, mock_container):
    """Test that the add repository button exists."""
    await user.open("/")

    # Check that the button is present
    await user.should_see("Add Repository")


@pytest.mark.asyncio
async def test_add_repository_with_valid_data(user: User, mock_container):
    """Test adding a repository with valid data."""
    await user.open("/")

    # Fill in the form using markers
    user.find(marker="owner_input").type("test_owner")
    user.find(marker="repo_input").type("test_repo")

    # Click the add button
    user.find(marker="add_repository_button").click()

    # Wait for the operation to complete and check for success notification
    await user.should_see("Added github/test_owner/test_repo")


@pytest.mark.asyncio
async def test_add_repository_shows_error_on_exception(user: User, mock_container, mocker: MockerFixture):
    """Test that adding a repository shows an error when an exception occurs."""
    # Make the use case raise an exception
    mock_summary_use_case = mock_container.get_repo_summary_use_case()
    mock_summary_use_case.execute.side_effect = Exception("Test error")

    await user.open("/")

    # Fill in the form using markers
    user.find(marker="owner_input").type("test_owner")
    user.find(marker="repo_input").type("test_repo")

    # Click the add button
    user.find(marker="add_repository_button").click()

    # Wait for the operation to complete and check for error notification
    await user.should_see("Error fetching repository data: Test error")


@pytest.mark.asyncio
async def test_integration_add_repository_without_mocks(user: User, mocker: MockerFixture):
    """Integration test that uses the real container and mocks only the GitHub API."""
    # Mock the GitHub API repository responses
    mock_gh_repo = mocker.MagicMock()

    # Configure mock for summary data
    mock_gh_repo.get_pulls.return_value.totalCount = 5
    mock_gh_repo.get_contributors.return_value.totalCount = 10

    # Configure mock for oldest PR
    mock_pr = mocker.MagicMock()
    mock_pr.created_at = datetime(2024, 1, 1)
    mock_gh_repo.get_pulls.return_value.get_page.return_value = [mock_pr]

    # Configure mock for timeseries - return empty lists
    mock_gh_repo.get_commits.return_value = []

    # Patch at the Github class level before it's instantiated
    mock_github_class = mocker.patch("github.Github", autospec=True)
    mock_github_instance = mock_github_class.return_value
    mock_github_instance.get_repo.return_value = mock_gh_repo

    # Now test with the real application flow
    await user.open("/")

    # Fill in the form using markers
    user.find(marker="owner_input").type("test_owner")
    user.find(marker="repo_input").type("test_repo")

    # Click the add button - this should trigger the real code path
    user.find(marker="add_repository_button").click()

    # Wait for async operations to complete
    import asyncio
    await asyncio.sleep(2)

    # The operation should complete successfully with the fix
    await user.should_see("Added github/test_owner/test_repo")


@pytest.mark.asyncio
async def test_tabs_are_present(user: User, mock_container):
    """Test that both Summary and Timeseries tabs are present."""
    await user.open("/")

    await user.should_see("Summary")
    await user.should_see("Timeseries")
