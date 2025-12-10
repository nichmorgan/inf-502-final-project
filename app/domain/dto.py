from pydantic import BaseModel, computed_field


class RepoSourceEntity(BaseModel):
    provider: str
    owner: str
    repo: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.provider}/{self.owner}/{self.repo}"
