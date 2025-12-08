from typing import Callable
from app.use_cases.ports.repo_port import RepoPort

__all__ = ["RepoGatewaySelector"]

GatewayCallable = Callable[[str, str], RepoPort]


class RepoGatewaySelector:
    def __init__(self, **providers) -> None:
        self.__gateways_map = providers

    @property
    def providers(self) -> list[str]:
        return list(self.__gateways_map.keys())

    def select_gateway(self, provider: str) -> GatewayCallable | None:
        return self.__gateways_map.get(provider)
