import boto3
from fastapi import HTTPException, UploadFile
from app.core.config import settings
from app.utils.ecs_log import logger

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

bucket_name = settings.S3_BUCKET


# TODO: Use this function to upload multiple files
def upload_files_to_s3(
    files: list[UploadFile], prefix: str, acl: str = "public-read"
) -> list[str]:
    """
    Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    if not files:
        return []
    out = []
    for i, file in enumerate(files):
        try:
            file_key = f"{prefix}_{i}"
            url = upload_image_to_s3(file, file_key, acl)
            if url:
                out.append(url)
        except Exception as e:
            logger.debug(e)
            raise e
    return out


def upload_image_to_s3(file: UploadFile, file_key: str, acl: str) -> str | None:
    """
    Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html
    """
    if not file:
        return None

    try:
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file_key,
            ExtraArgs={
                "ContentType": file.content_type,
            },
        )
        url = f"https://{bucket_name}.s3.ap-northeast-2.amazonaws.com/{file_key}"
        return url
    except Exception as e:
        logger.debug(e)
        raise HTTPException(status_code=500, detail="Failed to upload image to S3")
