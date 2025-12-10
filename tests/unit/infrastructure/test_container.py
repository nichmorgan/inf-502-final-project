"""Tests for the dependency injection container."""

import pytest
from app.containers import Container


def test_container_has_github_gateway():
    """Test that the container has a github gateway provider."""
    container = Container()

    # Get the gateway selector aggregate
    selector = container.repo_gateway_selector

    # Check that github is in the list of providers
    assert "github" in selector.providers, "GitHub should be in the list of providers"


def test_container_can_get_github_gateway():
    """Test that we can get a github gateway from the container."""
    container = Container()

    # Get the gateway selector aggregate
    selector = container.repo_gateway_selector

    # Get the github gateway provider
    github_provider = selector("github")

    # The provider should not be None
    assert github_provider is not None, "Should be able to get GitHub gateway provider"


def test_container_provides_use_cases():
    """Test that the container provides all required use cases."""
    container = Container()

    # Check that use case providers exist
    assert hasattr(container, "get_repo_info_by_source_use_case")
    assert hasattr(container, "get_repo_info_by_id_use_case")

    # Check that we can get the use cases
    get_by_source = container.get_repo_info_by_source_use_case()
    get_by_id = container.get_repo_info_by_id_use_case()

    assert get_by_source is not None
    assert get_by_id is not None


def test_container_provides_storage():
    """Test that the container provides storage."""
    container = Container()

    # Check that storage provider exists
    assert hasattr(container, "repo_info_storage")

    # Check that we can get the storage
    storage = container.repo_info_storage()
    assert storage is not None
