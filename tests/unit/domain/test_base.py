"""Tests for domain base classes."""

from datetime import datetime

import pytest

from app.domain.base import BaseCrudEntity


class TestEntity(BaseCrudEntity):
    """Test entity for testing BaseCrudEntity."""

    name: str


def test_base_crud_entity_with_id():
    """Test creating a BaseCrudEntity with ID."""
    # Arrange & Act
    now = datetime.now()
    entity = TestEntity(id=1, name="test", created_at=now)

    # Assert
    assert entity.id == 1
    assert entity.name == "test"
    assert entity.created_at == now
    assert entity.updated_at is None


def test_base_crud_entity_with_updated_at():
    """Test BaseCrudEntity with updated_at."""
    # Arrange & Act
    now = datetime.now()
    entity = TestEntity(id=1, name="test", created_at=now, updated_at=now)

    # Assert
    assert entity.id == 1
    assert entity.updated_at == now
