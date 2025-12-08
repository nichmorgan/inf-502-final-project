from dependency_injector import containers, providers
from github import Github
from github.Auth import Token as GithubToken
from app.use_cases import GetRepoSummaryUseCase, GetRepoTimeseriesUseCase
from app.adapters import GithubGateway
from app.infrastructure.config.settings import Settings
from app.domain.enums import RepoProvider


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])

    github_token = providers.Singleton(
        GithubToken, config.GITHUB_TOKEN.required().as_(str)
    )
    github_client = providers.Singleton(Github, auth=github_token)
    github_gateway = providers.Factory(GithubGateway, client=github_client)

    repo_gateway_selector = providers.Aggregate(
        {RepoProvider.GITHUB: github_gateway},
    )

    get_repo_summary_use_case = providers.Factory(
        GetRepoSummaryUseCase,
        gateway_selector=repo_gateway_selector,
    )

    get_repo_timeseries_use_case = providers.Factory(
        GetRepoTimeseriesUseCase,
        gateway_selector=repo_gateway_selector,
    )
