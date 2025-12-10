from datetime import datetime

from pydantic import BaseModel, Field, computed_field, field_validator

from app.domain.base import BaseCrudEntity
from app.domain.dto import RepoSourceEntity


class TimeseriesDataPoint(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    value: int = Field(description="Metric value at this date")

    @field_validator("date", mode="before")
    @classmethod
    def _validate_date(cls, v) -> str:
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        return v


class RepoInfoEntity(RepoSourceEntity, BaseCrudEntity):
    open_prs_count: int = Field(description="Number of open pull requests")
    closed_prs_count: int = Field(description="Number of closed pull requests")
    oldest_pr: datetime | None = Field(description="Oldest pull request date")
    users_count: int = Field(description="Number of users")

    open_prs: list[TimeseriesDataPoint] = Field(
        description="Timeseries of open pull requests"
    )
    closed_prs: list[TimeseriesDataPoint] = Field(
        description="Timeseries of closed pull requests"
    )
    users: list[TimeseriesDataPoint] = Field(description="Timeseries of contributors")

    @field_validator("oldest_pr", mode="before")
    @classmethod
    def _validate_oldest_pr(cls, v) -> str:
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        return v

    @computed_field
    @property
    def days_since_oldest_pr(self) -> int | None:
        if self.oldest_pr is None:
            return None
        delta = datetime.now() - self.oldest_pr
        return delta.days
