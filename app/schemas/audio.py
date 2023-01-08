from pydantic import BaseModel

from .hashtag import Hashtag


class AudioRead(BaseModel):
    id: int
    title: str
    artist_name: str
    audio_url: str
    cover_image_url: str
    hashtag: list[Hashtag]

    class Config:
        orm_mode = True


class AudioCreate(BaseModel):
    title: str
    artist_name: str
    hashtag: list[str]
class ProtoCreate(BaseModel):
    email: str

class ProtoRead(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True