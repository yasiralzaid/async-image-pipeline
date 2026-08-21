import uuid
from fastapi import FastAPI, UploadFile, File, status
from app.tasks import process_image_task

# initialize fastapi app
app = FastAPI(title="async image pipeline")

@app.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_image(file: UploadFile = File(...)):
    # generate a unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # read file bytes to pass to celery
    image_bytes = await file.read()
    
    # send task to the celery queue asynchronously
    task = process_image_task.delay(unique_filename, image_bytes)
    
    return {
        "message": "image accepted for processing",
        "task_id": task.id,
        "filename": unique_filename
    }