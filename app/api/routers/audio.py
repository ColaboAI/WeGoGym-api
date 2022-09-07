from typing import Optional
from pydantic import Json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from botocore.exceptions import ClientError
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.hashtag import Hashtag
from app.models.audio import Audio
from app.schemas import AudioRead, AudioCreate
from app.session import get_async_session
from app.utils.aws import s3_client, bucket_name
from app.utils.ecs_log import logger


audio_router = APIRouter()


@audio_router.get("/items", response_model=list[AudioRead])
async def get_audio_items(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Audio).options(selectinload(Audio.hashtag))
    result = await session.execute(stmt)
    return result.scalars().all()


@audio_router.post("/upload", response_model=AudioRead, status_code=201)
async def create_audio(
    file: Optional[UploadFile],
    metadata: Json[AudioCreate] = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    url = None
    if file:
        try:
            key = f"audio/{file.filename}"
            s3_client.upload_fileobj(
                file.file, bucket_name, key, ExtraArgs={"ACL": "public-read"}
            )
            url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{key}"
        except ClientError as e:
            logger.debug(e)

    if url:
        hashtags = metadata.hashtag

        audio_obj = Audio(
            title=metadata.title, artist_name=metadata.artist_name, audio_url=url
        )
        for h in hashtags:
            result = await session.execute(select(Hashtag).where(Hashtag.name == h))
            selected_hashtag = result.scalars().first()
            if selected_hashtag is None:
                hashtag = Hashtag(name=h)
                audio_obj.hashtag.append(hashtag)
                session.add(hashtag)
            else:
                audio_obj.hashtag.append(selected_hashtag)

            try:
                session.add(audio_obj)
            except:
                await session.rollback()
        await session.commit()
        return audio_obj
    else:
        raise HTTPException(status_code=400, detail="업로드 실패")
