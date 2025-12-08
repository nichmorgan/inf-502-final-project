from app.domain import RepoSummaryEntity
from app.domain.entities.repo import RepoSourceEntity
from dependency_injector.providers import Aggregate

from app.use_cases.ports.repo_port import RepoPort


class GetRepoSummaryUseCase:
    def __init__(self, gateway_selector: Aggregate[RepoPort]):
        self.__selector = gateway_selector

    def execute(self, source: RepoSourceEntity) -> RepoSummaryEntity:
        if source.provider not in self.__selector.providers:
            raise ValueError("Unsupported provider")

        gateway = self.__selector(source.provider, source.owner, source.repo)

        return RepoSummaryEntity(
            open_prs=gateway.get_open_pull_requests_count(),
            closed_prs=gateway.get_closed_pull_requests_count(),
            oldest_pr=gateway.get_oldest_pull_request_date(),  # type: ignore
            users=gateway.get_users_count(),
            **source.model_dump(),
        )
