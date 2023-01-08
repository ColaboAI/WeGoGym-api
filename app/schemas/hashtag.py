from pydantic import BaseModel


class Hashtag(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
