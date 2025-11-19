from datetime import datetime
from pydantic import BaseModel, Field

__all__ = [
    "PullRequestSummaryEntity",
    "UsersSummaryEntity",
    "RepoSummaryEntity",
]


class PullRequestSummaryEntity(BaseModel):
    open_count: int = Field(..., description="Number of open pull requests")
    closed_count: int = Field(..., description="Number of closed pull requests")
    oldest_date: datetime | None


class UsersSummaryEntity(BaseModel):
    count: int = Field(..., description="Number of users")


class RepoSummaryEntity(BaseModel):
    pull_requests: PullRequestSummaryEntity = Field(
        ..., description="Pull requests summary"
    )
    users: UsersSummaryEntity = Field(..., description="Users summary")
