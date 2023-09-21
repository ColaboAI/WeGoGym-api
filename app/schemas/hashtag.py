from pydantic import BaseModel, ConfigDict


class Hashtag(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(
        from_attributes=True,
    )
