from uuid import UUID
from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: UUID | None = Field(None, description="ID")
    is_superuser: bool = Field(False, description="Is Superuser")

    class Config:
        validate_assignment = True
