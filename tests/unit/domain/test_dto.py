"""Tests for domain DTOs."""

import pytest

from app.domain.dto import RepoSourceEntity


def test_repo_source_entity_creation():
    """Test creating a RepoSourceEntity."""
    # Arrange & Act
    entity = RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")

    # Assert
    assert entity.provider == "github"
    assert entity.owner == "test_owner"
    assert entity.repo == "test_repo"


def test_repo_source_entity_full_name():
    """Test the full_name computed field."""
    # Arrange
    entity = RepoSourceEntity(provider="github", owner="test_owner", repo="test_repo")

    # Act
    full_name = entity.full_name

    # Assert
    assert full_name == "github/test_owner/test_repo"


def test_repo_source_entity_full_name_different_values():
    """Test full_name with different values."""
    # Arrange
    entity = RepoSourceEntity(provider="gitlab", owner="my_org", repo="my_project")

    # Act
    full_name = entity.full_name

    # Assert
    assert full_name == "gitlab/my_org/my_project"
