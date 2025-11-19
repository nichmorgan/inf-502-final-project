from datetime import datetime
from urllib.parse import urlparse
from github import Github
from app.use_cases.ports.repo_port import RepoPort

__all__ = ["GithubGateway"]


class GithubGateway(RepoPort):
    provider = "github"

    def __init__(self, client: Github, owner: str, repo: str) -> None:
        super().__init__(owner, repo)
        self.__repo = client.get_repo(f"{owner}/{repo}", lazy=True)

    def get_open_pull_requests_count(self) -> int:
        return self.__repo.get_pulls(state="open").totalCount

    def get_closed_pull_requests_count(self) -> int:
        return self.__repo.get_pulls(state="closed").totalCount

    def get_users_count(self) -> int:
        return self.__repo.get_contributors().totalCount

    def get_oldest_pull_request_date(self) -> datetime | None:
        response = self.__repo.get_pulls(sort="created", direction="asc")
        if pr_list := response.get_page(0):
            return pr_list[0].created_at
        return None
