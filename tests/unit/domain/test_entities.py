"""Tests for domain entities."""

from datetime import datetime

import pytest

from app.domain.entities.repo import RepoInfoEntity, TimeseriesDataPoint


def test_timeseries_data_point_creation():
    """Test creating a TimeseriesDataPoint."""
    # Arrange & Act
    point = TimeseriesDataPoint(date="2024-01-01", value=10)

    # Assert
    assert point.date == "2024-01-01"
    assert point.value == 10


def test_timeseries_data_point_validates_datetime():
    """Test that TimeseriesDataPoint converts datetime to string."""
    # Arrange
    dt = datetime(2024, 1, 1, 12, 0, 0)

    # Act
    point = TimeseriesDataPoint(date=dt, value=10)

    # Assert
    assert point.date == "2024-01-01"
    assert point.value == 10


def test_repo_info_entity_creation():
    """Test creating a RepoInfoEntity."""
    # Arrange & Act
    entity = RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=datetime(2024, 1, 1),
        users_count=5,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=datetime.now(),
    )

    # Assert
    assert entity.id == 1
    assert entity.provider == "github"
    assert entity.owner == "test_owner"
    assert entity.repo == "test_repo"
    assert entity.open_prs_count == 10
    assert entity.closed_prs_count == 20
    assert entity.users_count == 5


def test_repo_info_entity_validates_oldest_pr_datetime():
    """Test that oldest_pr is validated properly."""
    # Arrange
    dt = datetime(2024, 1, 1, 12, 0, 0)

    # Act
    entity = RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=dt,
        users_count=5,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=datetime.now(),
    )

    # Assert - the validator strips time information
    assert entity.oldest_pr.year == 2024
    assert entity.oldest_pr.month == 1
    assert entity.oldest_pr.day == 1


def test_repo_info_entity_days_since_oldest_pr():
    """Test the days_since_oldest_pr computed field."""
    # Arrange
    old_date = datetime(2024, 1, 1)
    entity = RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=old_date,
        users_count=5,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=datetime.now(),
    )

    # Act
    days = entity.days_since_oldest_pr

    # Assert
    assert days is not None
    assert isinstance(days, int)
    assert days > 0


def test_repo_info_entity_days_since_oldest_pr_none():
    """Test days_since_oldest_pr when oldest_pr is None."""
    # Arrange
    entity = RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=None,
        users_count=5,
        open_prs=[],
        closed_prs=[],
        users=[],
        created_at=datetime.now(),
    )

    # Act
    days = entity.days_since_oldest_pr

    # Assert
    assert days is None


def test_repo_info_entity_with_timeseries():
    """Test RepoInfoEntity with timeseries data."""
    # Arrange
    timeseries = [
        TimeseriesDataPoint(date="2024-01-01", value=10),
        TimeseriesDataPoint(date="2024-01-02", value=15),
    ]

    # Act
    entity = RepoInfoEntity(
        id=1,
        provider="github",
        owner="test_owner",
        repo="test_repo",
        open_prs_count=10,
        closed_prs_count=20,
        oldest_pr=datetime(2024, 1, 1),
        users_count=5,
        open_prs=timeseries,
        closed_prs=timeseries,
        users=timeseries,
        created_at=datetime.now(),
    )

    # Assert
    assert len(entity.open_prs) == 2
    assert len(entity.closed_prs) == 2
    assert len(entity.users) == 2
    assert entity.open_prs[0].date == "2024-01-01"
    assert entity.open_prs[1].value == 15
