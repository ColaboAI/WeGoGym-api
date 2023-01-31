from uuid import UUID
from pydantic import BaseModel, Field


class CurrentUser(BaseModel):
    id: UUID = Field(None, description="ID")

    class Config:
        validate_assignment = True
