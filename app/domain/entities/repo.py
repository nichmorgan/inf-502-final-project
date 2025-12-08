from datetime import datetime
from pydantic import BaseModel, computed_field, Field, field_validator


__all__ = [
    "RepoSummaryEntity",
    "RepoSourceEntity",
    "RepoTimeseriesEntity",
    "TimeseriesDataPoint",
]


class RepoSourceEntity(BaseModel):
    provider: str
    owner: str
    repo: str

    @computed_field
    @property
    def id(self) -> str:
        return f"{self.provider}/{self.owner}/{self.repo}"

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"


class RepoSummaryEntity(RepoSourceEntity):
    open_prs: int = Field(description="Number of open pull requests")
    closed_prs: int = Field(description="Number of closed pull requests")
    oldest_pr: str | None = Field(description="Oldest pull request date")
    users: int = Field(description="Number of users")

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
        oldest_date = datetime.strptime(self.oldest_pr, "%Y-%m-%d")
        delta = datetime.now() - oldest_date
        return delta.days


class TimeseriesDataPoint(BaseModel):
    date: str = Field(description="Date in YYYY-MM-DD format")
    value: int = Field(description="Metric value at this date")

    @field_validator("date", mode="before")
    @classmethod
    def _validate_date(cls, v) -> str:
        if isinstance(v, datetime):
            return v.strftime("%Y-%m-%d")
        return v


class RepoTimeseriesEntity(RepoSourceEntity):
    open_prs: list[TimeseriesDataPoint] = Field(
        description="Timeseries of open pull requests"
    )
    closed_prs: list[TimeseriesDataPoint] = Field(
        description="Timeseries of closed pull requests"
    )
    users: list[TimeseriesDataPoint] = Field(description="Timeseries of contributors")
