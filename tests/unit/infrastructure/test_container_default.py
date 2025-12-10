"""Tests for Container.default() factory method."""

import os

import pytest

from app.containers import Container


def test_container_default_creates_and_initializes():
    """Test that Container.default() creates and initializes a container."""
    # Act
    container = Container.default()

    # Assert
    assert container is not None
    # Verify that the github token was configured (reads from actual settings)
    assert isinstance(container.config.GITHUB_TOKEN(), str)


def test_container_default_initializes_resources(mocker):
    """Test that Container.default() initializes resources."""
    # Arrange
    mocker.patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_456"})

    # Act
    container = Container.default()

    # Assert - resources should be initialized
    # We can verify by checking that we can access providers
    assert hasattr(container, "github_client")
    assert hasattr(container, "repo_gateway_selector")


def test_container_default_validates_github_token(mocker):
    """Test that Container.default() validates GITHUB_TOKEN is a string."""
    # Arrange
    mocker.patch.dict(os.environ, {"GITHUB_TOKEN": "valid_token"})

    # Act - should not raise
    container = Container.default()

    # Assert
    assert isinstance(container.config.GITHUB_TOKEN(), str)
