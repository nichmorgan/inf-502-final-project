from datetime import datetime

from pydantic import BaseModel

from app.domain.entities.repo import TimeseriesDataPoint

from .base import BaseUpdateSchema


class CreateRepoInfoSchema(BaseModel):
    provider: str
    owner: str
    repo: str
    open_prs_count: int
    closed_prs_count: int
    oldest_pr: datetime | None
    users_count: int
    open_prs: list[TimeseriesDataPoint]
    closed_prs: list[TimeseriesDataPoint]
    users: list[TimeseriesDataPoint]


class UpdateRepoInfoSchema(BaseUpdateSchema):
    open_prs_count: int | None = None
    closed_prs_count: int | None = None
    oldest_pr: str | None = None
    users_count: int | None = None
    open_prs: int | None = None
    closed_prs: int | None = None
    oldest_pr: str | None = None
    users: int | None = None


class FilterRepoInfoSchema(BaseModel):
    full_name: str | None = None
