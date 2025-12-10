"""Tests for infrastructure schemas."""

from datetime import datetime

from app.infrastructure.schemas import (
    CreateRepoInfoSchema,
    FilterRepoInfoSchema,
    UpdateRepoInfoSchema,
)


def test_create_repo_info_schema():
    """Test creating a CreateRepoInfoSchema."""
    # Arrange & Act
    schema = CreateRepoInfoSchema(
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
    )

    # Assert
    assert schema.provider == "github"
    assert schema.owner == "test_owner"
    assert schema.repo == "test_repo"
    assert schema.open_prs_count == 10


def test_update_repo_info_schema():
    """Test creating an UpdateRepoInfoSchema."""
    # Arrange & Act
    schema = UpdateRepoInfoSchema(open_prs_count=15)

    # Assert
    assert schema.open_prs_count == 15


def test_filter_repo_info_schema():
    """Test creating a FilterRepoInfoSchema."""
    # Arrange & Act
    schema = FilterRepoInfoSchema(full_name="github/owner/repo")

    # Assert
    assert schema.full_name == "github/owner/repo"


def test_filter_repo_info_schema_optional_fields():
    """Test FilterRepoInfoSchema with no fields."""
    # Arrange & Act
    schema = FilterRepoInfoSchema()

    # Assert
    assert schema.model_dump(exclude_unset=True) == {}
