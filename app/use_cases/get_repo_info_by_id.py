import asyncio

from app.domain.entities.repo import RepoInfoEntity
from app.shared.types import RepoInfoStorage


class GetRepoInfoByIdUseCase:
    def __init__(self, storage: RepoInfoStorage):
        self.__storage = storage

    async def execute(self, ids_list: list[int]) -> list[RepoInfoEntity]:
        id_set = set(ids_list)

        items_list = []
        for id in id_set:
            if item := await self.__storage.get_one(id):
                items_list.append(item)
        return items_list

    def execute_sync(self, ids_list: list[int]) -> list[RepoInfoEntity]:
        return asyncio.run(self.execute(ids_list))
