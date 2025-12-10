from datetime import datetime

from pydantic import BaseModel, Field


class BaseCrudEntity(BaseModel):
    id: int | None = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime | None = None
