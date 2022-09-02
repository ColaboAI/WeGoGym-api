from email.policy import default
from sqlalchemy import Column, Integer, String
from app.session import Base

# TODO: User relationship to be added


class Audio(Base):
    __tablename__ = "audio"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    artist_name = Column(String(100), nullable=False)
    audio_url = Column(String(256), nullable=False)
    hash_tags = Column(String(256), nullable=False, default="")
