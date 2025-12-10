from pydantic import BaseModel, Field, computed_field


class RepoSourceEntity(BaseModel):
    provider: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.provider}/{self.owner}/{self.repo}"
