from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models import Base
from .hashtag import audio_hashtag_association_table

# TODO: User relationship to be added


class Audio(Base):
    __tablename__ = "audio"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    artist_name = Column(String(100), nullable=False)
    audio_url = Column(String(256), nullable=False)
    cover_image_url = Column(String(256), nullable=False)
    hashtag = relationship(
        "Hashtag", secondary=audio_hashtag_association_table, back_populates="audio"
    )
