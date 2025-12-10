"""Tests for domain enums."""

from app.domain.enums import RepoProvider


def test_repo_provider_enum():
    """Test RepoProvider enum."""
    # Assert
    assert RepoProvider.GITHUB == "github"


def test_repo_provider_enum_membership():
    """Test RepoProvider enum membership."""
    # Assert
    assert "github" in [p.value for p in RepoProvider]
