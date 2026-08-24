import uuid
from fastapi import FastAPI, UploadFile, File, status
from celery.result import AsyncResult
from app.tasks import process_image_task, celery_app

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

@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    # fetch the task result from the redis backend
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status
    }
    
    # add the result data if the task finished successfully
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.info)
        
    return response