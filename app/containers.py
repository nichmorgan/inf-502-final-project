import logging
from pathlib import Path

from dependency_injector import containers, providers
from github import Auth, Github

from app import use_cases
from app.adapters.gateways import GithubGateway
from app.adapters.storage import PickleStorage
from app.domain import entities, enums
from app.infrastructure import schemas
from app.infrastructure.config.settings import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[Settings()])  # type: ignore

    configure_logging = providers.Resource(
        logging.basicConfig,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    github_token = providers.Factory(Auth.Token, token=config.GITHUB_TOKEN)
    github_client = providers.Singleton(
        Github,
        auth=github_token,
    )

    repo_gateway_selector = providers.Aggregate(
        {
            enums.RepoProvider.GITHUB: providers.Factory(
                GithubGateway, client=github_client
            )
        },
    )

    repo_info_storage = providers.Singleton(
        PickleStorage[
            entities.RepoInfoEntity,
            schemas.CreateRepoInfoSchema,
            schemas.UpdateRepoInfoSchema,
            schemas.FilterRepoInfoSchema,
        ],
        path=config.STORAGE_FOLDER.as_(lambda x: Path(x) / "repo_info.pickle"),
    )

    get_repo_info_by_source_use_case = providers.Factory(
        use_cases.GetRepoInfoBySourceUseCase,
        gateway_selector=repo_gateway_selector,
        storage=repo_info_storage,
        time_to_live_seconds=config.CACHE_TTL_SECONDS,
    )

    get_repo_info_by_id_use_case = providers.Factory(
        use_cases.GetRepoInfoByIdUseCase,
        storage=repo_info_storage,
    )

    @classmethod
    def default(cls):
        container = cls()
        container.init_resources()

        # Temporary fix
        assert isinstance(container.config.GITHUB_TOKEN(), str)

        return container
