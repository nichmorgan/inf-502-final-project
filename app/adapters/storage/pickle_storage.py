import logging
import pickle
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel

from app.domain.base import BaseCrudEntity
from app.domain.ports import StoragePort

TModel = TypeVar("TModel", bound=BaseCrudEntity)
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TFilter = TypeVar("TFilter", bound=BaseModel)


class PickleStorage(
    Generic[TModel, TCreate, TUpdate, TFilter],
    StoragePort[TModel, TCreate, TUpdate, TFilter],
):
    __state: dict[int, TModel] = {}

    def __init__(
        self,
        path: Path,
        *,
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.__path = path
        self.__logger = logger
        self.__load()

    @property
    def __model(self) -> type[TModel]:
        return self.__orig_class__.__args__[0]  # type: ignore

    def __load(self) -> None:
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        if not self.__path.exists():
            return

        with self.__path.open("rb") as f:
            self.__state = pickle.load(f)

    def __save(self) -> None:
        with self.__path.open("wb") as f:
            pickle.dump(self.__state, f)

    def __filter(self, filter_dict: TFilter | None) -> list[int]:
        if not filter_dict:
            return list(self.__state.keys())

        ids = set([])
        for entity in self.__state.values():
            for filter_key, filter_value in filter_dict.model_dump().items():
                if not hasattr(entity, filter_key):
                    continue

                entity_value = getattr(entity, filter_key)

                if isinstance(filter_value, str):
                    if entity_value == filter_value:
                        ids.add(entity.id)
                elif isinstance(filter_value, list):
                    if entity_value in filter_value:
                        ids.add(entity.id)
        return list(ids)

    async def create_one(self, entity: TCreate) -> TModel:
        new_id = len(self.__state) + 1
        new_entity = self.__model(id=new_id, **entity.model_dump())
        self.__state[new_id] = new_entity

        self.__save()

        return new_entity

    async def get_one(self, entity_id: int) -> TModel | None:
        return self.__state.get(entity_id)

    async def get_many(
        self, filter_dict: TFilter | None, *, skip: int = 0, limit: int = 100
    ) -> list[TModel]:
        ids = self.__filter(filter_dict)
        ids = ids[skip : skip + limit]

        return [self.__state[id] for id in ids]

    async def update_one(self, entity_id: int, entity: TUpdate) -> TModel | None:
        if entity_id not in self.__state:
            return None

        self.__state[entity_id] = self.__state[entity_id].model_copy(
            update={
                **entity.model_dump(exclude_unset=True),
            }
        )
        self.__save()

        return self.__state[entity_id]

    async def delete_one(self, entity_id: int) -> bool:
        if entity_id not in self.__state:
            return False

        del self.__state[entity_id]
        self.__save()

        return True
