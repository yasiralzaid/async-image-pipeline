import os
import io
import boto3
from celery import Celery
from PIL import Image

# get broker and backend from environment variables
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# minio configuration
minio_url = os.getenv("MINIO_URL", "http://localhost:9000")
minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")

# initialize celery app
celery_app = Celery(
    "tasks",
    broker=broker_url,
    backend=backend_url
)

# initialize s3 client for minio
s3_client = boto3.client(
    "s3",
    endpoint_url=minio_url,
    aws_access_key_id=minio_access_key,
    aws_secret_access_key=minio_secret_key
)

bucket_name = "processed-images"

@celery_app.task
def process_image_task(filename: str, image_bytes: bytes):
    # create bucket if it does not exist
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        s3_client.create_bucket(Bucket=bucket_name)

    # open image using pillow
    image = Image.open(io.BytesIO(image_bytes))
    
    # convert to grayscale
    grayscale_image = image.convert("L")
    
    # save processed image to an in-memory buffer
    output_buffer = io.BytesIO()
    # default to jpeg if format is missing
    image_format = image.format or "JPEG"
    grayscale_image.save(output_buffer, format=image_format)
    output_buffer.seek(0)
    
    # upload to minio
    processed_filename = f"processed_{filename}"
    s3_client.upload_fileobj(
        output_buffer,
        bucket_name,
        processed_filename,
        ExtraArgs={"ContentType": f"image/{image_format.lower()}"}
    )
    
    return {"status": "completed", "filename": processed_filename}