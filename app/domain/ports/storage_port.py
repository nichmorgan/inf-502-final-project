from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.domain.base import BaseCrudEntity

TModel = TypeVar("TModel", bound=BaseCrudEntity)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TFilter = TypeVar("TFilter", bound=BaseModel)


class StoragePort(ABC, Generic[TModel, TCreate, TUpdate, TFilter]):
    """
    Abstract interface for basic CRUD operations.
    """

    @abstractmethod
    async def create_one(self, entity: TCreate) -> TModel:
        """
        Creates a new entity in the database.

        Args:
            entity (TCreate): The entity to create.

        Returns:
            TModel: The created entity, possibly with updated fields like ID.
        """
        pass

    @abstractmethod
    async def get_one(self, entity_id: Any) -> TModel | None:
        """
        Retrieves an entity by its unique identifier.

        Args:
            entity_id (Any): The ID of the entity to retrieve.

        Returns:
            TModel | None: The retrieved entity, or None if not found.
        """
        pass

    @abstractmethod
    async def get_many(
        self,
        filter_dict: TFilter | None,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TModel]:
        """
        Retrieves filtered entities with pagination.

        Args:
            filter_dict: (TFilter | None): The filter to apply to the query.
            skip (int): The number of entities to skip.
            limit (int): The maximum number of entities to return.

        Returns:
            List[TModel]: A list of entities.
        """
        pass

    @abstractmethod
    async def update_one(self, entity_id: Any, entity: TUpdate) -> TModel | None:
        """
        Updates an existing entity.

        Args:
            entity_id (Any): The ID of the entity to update.
            entity (TUpdate): The updated entity data.

        Returns:
            Optional[TModel]: The updated entity, or None if the entity was not found.
        """
        pass

    @abstractmethod
    async def delete_one(self, entity_id: Any) -> bool:
        """
        Deletes an entity by its unique identifier.

        Args:
            entity_id (Any): The ID of the entity to delete.

        Returns:
            bool: True if the entity was deleted, False otherwise.
        """
