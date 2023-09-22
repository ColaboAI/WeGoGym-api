from pydantic import BaseModel, ConfigDict

from .hashtag import Hashtag


class AudioRead(BaseModel):
    id: int
    title: str
    artist_name: str
    audio_url: str
    cover_image_url: str
    hashtag: list[Hashtag]

    model_config = ConfigDict(
        from_attributes=True,
    )


class AudioCreate(BaseModel):
    title: str
    artist_name: str
    hashtag: list[str]
