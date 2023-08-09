from datetime import datetime
from uuid import UUID
from fastapi import UploadFile
from app.utils.ecs_log import logger
from app.utils.aws import s3_client, bucket_name


def upload_image_to_s3(file: UploadFile, uid: UUID) -> str:
    img_url = None
    try:
        image_key = f"profile_pic/{uid}/{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}"
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            image_key,
            ExtraArgs={
                "ContentType": file.content_type,
            },
        )
        img_url = f"https://{bucket_name}.s3.amazonaws.com/{image_key}"
    except Exception as e:
        logger.error(e)
        raise e
    return img_url
