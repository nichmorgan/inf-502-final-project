"""Mock implementations for use case-related components."""

import pytest
from pytest_mock import MockerFixture

from app.use_cases.get_repo_info_by_id import GetRepoInfoByIdUseCase
from app.use_cases.get_repo_info_by_source import GetRepoInfoBySourceUseCase


@pytest.fixture
def get_repo_info_by_id_use_case(mock_storage):
    """Create GetRepoInfoByIdUseCase with mocked storage."""
    return GetRepoInfoByIdUseCase(storage=mock_storage)


@pytest.fixture
def get_repo_info_by_source_use_case(mock_gateway_selector, mock_storage):
    """Create GetRepoInfoBySourceUseCase with mocked dependencies."""
    return GetRepoInfoBySourceUseCase(
        gateway_selector=mock_gateway_selector,
        storage=mock_storage,
        time_to_live_seconds=3600,
    )
