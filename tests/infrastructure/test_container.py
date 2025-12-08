"""Tests for the dependency injection container."""
import pytest
from app.containers import Container
from app.domain.entities.repo import RepoSourceEntity


def test_container_github_gateway_is_callable():
    """Test that the github gateway provider returns a callable factory."""
    container = Container()

    # Get the gateway selector
    selector = container.repo_gateway_selector()

    # Get the github gateway factory
    github_factory = selector.select_gateway("github")

    # The factory should be callable
    assert callable(github_factory), "GitHub gateway factory should be callable"

    # The factory should accept owner and repo as arguments
    # This will fail if the container is misconfigured
    try:
        # We expect this to fail because we don't have a real GitHub token
        # But it should get past the provider configuration
        gateway = github_factory("test_owner", "test_repo")
        # If we got here, the factory signature is correct
        assert True
    except TypeError as e:
        # If we get a TypeError about missing arguments, the container is misconfigured
        if "missing" in str(e).lower() and "required" in str(e).lower():
            pytest.fail(f"Container misconfiguration: {e}")
        # Other TypeErrors might be from GitHub API, which is OK for this test
    except Exception:
        # Other exceptions (like GitHub API errors) are OK for this test
        # We only care that the factory signature is correct
        pass


def test_container_provides_valid_gateway_selector():
    """Test that the container provides a properly configured gateway selector."""
    container = Container()

    selector = container.repo_gateway_selector()

    # Check that github is in the list of providers
    assert "github" in selector.providers, "GitHub should be in the list of providers"

    # Check that we can select the github gateway
    github_factory = selector.select_gateway("github")
    assert github_factory is not None, "Should be able to select GitHub gateway"
