from app.adapters.gateways.repo_gateway_selector import RepoGatewaySelector
from app.domain import RepoSummaryEntity, PullRequestSummaryEntity, UsersSummaryEntity

__all__ = ["GetRepoSummaryUseCase"]


class GetRepoSummaryUseCase:
    def __init__(self, gateway_selector: RepoGatewaySelector):
        self.__selector = gateway_selector

    def execute(self, provider: str, owner: str, repo: str) -> RepoSummaryEntity:
        gateway_factory = self.__selector.select_gateway(provider)
        if not gateway_factory:
            raise ValueError("Unsupported URL")

        gateway = gateway_factory(owner, repo)
        open_prs = gateway.get_open_pull_requests_count()
        closed_prs = gateway.get_closed_pull_requests_count()
        oldest_pr_date = gateway.get_oldest_pull_request_date()
        users_count = gateway.get_users_count()

        pull_request_summary = PullRequestSummaryEntity(
            open_count=open_prs,
            closed_count=closed_prs,
            oldest_date=oldest_pr_date,
        )
        users_summary = UsersSummaryEntity(count=users_count)

        return RepoSummaryEntity(
            pull_requests=pull_request_summary,
            users=users_summary,
        )
