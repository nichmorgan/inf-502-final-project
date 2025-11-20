from datetime import datetime
from pydantic import BaseModel, computed_field
from pydantic import BaseModel, Field, field_validator


__all__ = [
    "RepoSummaryEntity",
    "RepoSourceEntity",
]


class RepoSourceEntity(BaseModel):
    provider: str
    owner: str
    repo: str

    @computed_field
    @property
    def id(self) -> str:
        return f"{self.provider}/{self.owner}/{self.repo}"


class RepoSummaryEntity(RepoSourceEntity):
    open_prs: int = Field(description="Number of open pull requests")
    closed_prs: int = Field(description="Number of closed pull requests")
    oldest_pr: str | None = Field(description="Oldest pull request date")
    users: int = Field(description="Number of users")

    @field_validator("oldest_pr", mode="before")
    @classmethod
    def _validate_oldest_pr(cls, v) -> str:
        if not v:
            return "N/A"
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        return v
