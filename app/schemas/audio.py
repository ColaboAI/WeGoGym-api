from pydantic import BaseModel
from fastapi import UploadFile


class AudioRead(BaseModel):
    id: int
    title: str
    artist_name: str
    audio_url: str
    hash_tags: list[str]

    class Config:
        orm_mode = True


class AudioCreate(BaseModel):
    title: str
    artist_name: str
    audio: UploadFile
    hash_tags: list[str]
