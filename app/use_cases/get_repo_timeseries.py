import logging
from app.domain.entities.repo import (
    RepoSourceEntity,
    RepoTimeseriesEntity,
    TimeseriesDataPoint,
)
from app.use_cases.ports.repo_port import RepoPort
from dependency_injector.providers import Aggregate


logger = logging.getLogger(__name__)


class GetRepoTimeseriesUseCase:
    def __init__(self, gateway_selector: Aggregate[RepoPort]):
        self.__selector = gateway_selector

    def execute(self, source: RepoSourceEntity) -> RepoTimeseriesEntity:
        logger.info(f"[USE CASE] Starting timeseries for {source.id}")
        if source.provider not in self.__selector.providers:
            raise ValueError(f"Unsupported provider: {source.provider}")

        logger.info(f"[USE CASE] Creating gateway for {source.id}")
        gateway = self.__selector(source.provider, source.owner, source.repo)

        # Get timeseries data
        logger.info(f"[USE CASE] Fetching open PRs timeseries for {source.id}")
        open_prs_ts = gateway.get_timeseries_open_pull_requests()

        logger.info(f"[USE CASE] Fetching closed PRs timeseries for {source.id}")
        closed_prs_ts = gateway.get_timeseries_closed_pull_requests()

        logger.info(f"[USE CASE] Fetching contributors timeseries for {source.id}")
        users_ts = gateway.get_timeseries_users()

        # Fill missing dates by duplicating previous values
        logger.info(f"[USE CASE] Filling timeseries gaps for {source.id}")

        def fill_timeseries(ts_dict: dict) -> list[TimeseriesDataPoint]:
            if not ts_dict:
                return []

            sorted_dates = sorted(ts_dict.keys())
            result = []
            last_value = 0

            for date in sorted_dates:
                value = ts_dict.get(date, last_value)
                result.append(TimeseriesDataPoint(date=date, value=value))
                last_value = value

            return result

        result = RepoTimeseriesEntity(
            open_prs=fill_timeseries(open_prs_ts),
            closed_prs=fill_timeseries(closed_prs_ts),
            users=fill_timeseries(users_ts),
            **source.model_dump(),
        )

        logger.info(f"[USE CASE] Completed timeseries for {source.id}")
        return result
