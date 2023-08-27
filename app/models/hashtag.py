from typing import TYPE_CHECKING
from app.models import Base
from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import relationship, mapped_column, Mapped

if TYPE_CHECKING:
    from .audio import Audio

audio_hashtag_association_table = Table(
    "audio_hashtag_association",
    Base.metadata,
    Column("audio_id", Integer, ForeignKey("audio.id"), primary_key=True),
    Column("hashtag_id", Integer, ForeignKey("hashtag.id"), primary_key=True),
)


class Hashtag(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    audio: Mapped["Audio"] = relationship("Audio", secondary=audio_hashtag_association_table, back_populates="hashtag")  # type: ignore
