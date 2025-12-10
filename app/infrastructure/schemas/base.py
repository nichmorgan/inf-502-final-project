from datetime import datetime

from pydantic import BaseModel, computed_field


class BaseUpdateSchema(BaseModel):
    @computed_field
    @property
    def updated_at(self) -> datetime:
        return datetime.now()
