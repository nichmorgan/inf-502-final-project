from app.domain import entities, ports
from app.infrastructure import schemas

RepoInfoStorage = ports.StoragePort[
    entities.RepoInfoEntity,
    schemas.CreateRepoInfoSchema,
    schemas.UpdateRepoInfoSchema,
    schemas.FilterRepoInfoSchema,
]
