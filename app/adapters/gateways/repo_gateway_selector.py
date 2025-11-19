from typing import Type
from app.use_cases.ports.repo_port import RepoPort

__all__ = ["RepoGatewaySelector"]


class RepoGatewaySelector:
    def __init__(self, *gateways: Type[RepoPort]) -> None:
        self.__providers_map = {str(gateway.provider): gateway for gateway in gateways}

    @property
    def providers(self) -> list[str]:
        return list(self.__providers_map.keys())

    def select_gateway(self, provider: str) -> Type[RepoPort] | None:
        return self.__providers_map.get(provider)
