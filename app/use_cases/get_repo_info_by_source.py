import asyncio
from datetime import datetime

from dependency_injector.providers import Aggregate

from app.domain import dto, entities
from app.domain.ports import RepoPort
from app.infrastructure import schemas
from app.shared.types import RepoInfoStorage


class GetRepoInfoBySourceUseCase:
    def __init__(
        self,
        gateway_selector: Aggregate[RepoPort],
        storage: RepoInfoStorage,
        time_to_live_seconds: int = 60 * 60,
    ):
        self.__selector = gateway_selector
        self.__storage = storage
        self.__ttl = time_to_live_seconds

    async def __get_from_db(
        self, source: dto.RepoSourceEntity
    ) -> entities.RepoInfoEntity | None:
        filter_ = schemas.FilterRepoInfoSchema(full_name=source.full_name)
        if result := await self.__storage.get_many(filter_, limit=1):
            item = result[0]
            since_last_update = (item.updated_at or datetime.now()) - item.created_at
            if since_last_update.total_seconds() < self.__ttl:
                return item
            await self.__storage.delete_one(item.id)

        return None

    async def __get_from_gateway(
        self, source: dto.RepoSourceEntity
    ) -> entities.RepoInfoEntity:
        if source.provider not in self.__selector.providers:
            raise ValueError("Unsupported provider")

        gateway = self.__selector(source.provider)

        def fill_timeseries(ts_dict: dict) -> list[entities.TimeseriesDataPoint]:
            if not ts_dict:
                return []

            sorted_dates = sorted(ts_dict.keys())
            result = []
            last_value = 0

            for date in sorted_dates:
                value = ts_dict.get(date, last_value)
                result.append(entities.TimeseriesDataPoint(date=date, value=value))
                last_value = value

            return result

        return entities.RepoInfoEntity(
            open_prs_count=await gateway.get_open_pull_requests_count(
                owner=source.owner, repo=source.repo
            ),
            open_prs=fill_timeseries(
                await gateway.get_timeseries_open_pull_requests(
                    owner=source.owner, repo=source.repo
                )
            ),
            closed_prs_count=await gateway.get_closed_pull_requests_count(
                owner=source.owner, repo=source.repo
            ),
            closed_prs=fill_timeseries(
                await gateway.get_timeseries_closed_pull_requests(
                    owner=source.owner, repo=source.repo
                )
            ),
            users_count=await gateway.get_users_count(
                owner=source.owner, repo=source.repo
            ),
            users=fill_timeseries(
                await gateway.get_timeseries_users(owner=source.owner, repo=source.repo)
            ),
            oldest_pr=await gateway.get_oldest_pull_request_date(owner=source.owner, repo=source.repo),  # type: ignore
            **source.model_dump(),
        )

    async def execute(self, source: dto.RepoSourceEntity) -> entities.RepoInfoEntity:
        """
        Executes the use case to get repository information.

        Args:
            source (entities.RepoSourceEntity): The source entity of the repository.

        Returns:
            entities.RepoInfoEntity: The repository information entity.
        """

        if db_item := await self.__get_from_db(source):
            return db_item

        gateway_item = await self.__get_from_gateway(source)
        create_item = schemas.CreateRepoInfoSchema(**gateway_item.model_dump())
        new_item = await self.__storage.create_one(create_item)
        return new_item

    def execute_sync(self, source: dto.RepoSourceEntity) -> entities.RepoInfoEntity:
        return asyncio.run(self.execute(source))
