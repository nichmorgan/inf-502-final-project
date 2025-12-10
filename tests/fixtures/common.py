"""Common fixtures shared across all test modules."""

import pytest
from faker import Faker


@pytest.fixture
def faker() -> Faker:
    """Provide a Faker instance for dynamic data generation."""
    return Faker()
