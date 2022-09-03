from app.models.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship


audio_hashtag_association_table = Table(
    "association",
    Base.metadata,
    Column("audio_id", Integer, ForeignKey("audio.id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtag.id"), primary_key=True),
)


class Hashtag(Base):
    __tablename__ = "hashtag"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    audio = relationship(
        "Audio", secondary=audio_hashtag_association_table, back_populates="hashtag"
    )
