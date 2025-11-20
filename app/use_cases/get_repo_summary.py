from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.domain import RepoSummaryEntity
from app.domain.entities.repo import RepoSourceEntity

__all__ = ["GetRepoSummaryUseCase"]


class GetRepoSummaryUseCase:
    def __init__(self, gateway_selector: RepoGatewaySelector):
        self.__selector = gateway_selector

    def execute(self, source: RepoSourceEntity) -> RepoSummaryEntity:
        gateway_factory = self.__selector.select_gateway(source.provider)
        if not gateway_factory:
            raise ValueError("Unsupported provider")

        gateway = gateway_factory(source.owner, source.repo)

        return RepoSummaryEntity(
            open_prs=gateway.get_open_pull_requests_count(),
            closed_prs=gateway.get_closed_pull_requests_count(),
            oldest_pr=gateway.get_oldest_pull_request_date(),  # type: ignore
            users=gateway.get_users_count(),
            **source.model_dump(),
        )
