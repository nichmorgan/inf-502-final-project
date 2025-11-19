from dependency_injector import containers, providers
from github import Github
from app.use_cases import GetRepoSummaryUseCase
from app.adapters import GithubGateway, RepoGatewaySelector


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    github_client = providers.Singleton(Github)
    github_gateway = providers.Factory(GithubGateway, client=github_client)

    repo_gateway_selector = providers.Singleton(RepoGatewaySelector, github_gateway)

    get_repo_summary_use_case = providers.Singleton(
        GetRepoSummaryUseCase,
        gateway_selector=repo_gateway_selector,
    )
