from typing import TYPE_CHECKING
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, mapped_column
from app.models import Base
from .hashtag import audio_hashtag_association_table

# TODO: User relationship to be added


class Audio(Base):
    id = mapped_column(Integer, primary_key=True, index=True)
    title = mapped_column(String(100), nullable=False)
    artist_name = mapped_column(String(100), nullable=False)
    audio_url = mapped_column(String(256), nullable=False)
    cover_image_url = mapped_column(String(256), nullable=False)
    hashtag = relationship("Hashtag", secondary=audio_hashtag_association_table, back_populates="audio")  # type: ignore
