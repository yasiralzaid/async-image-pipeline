# Event-Driven Image Processing Pipeline

This is an asynchronous REST API built with FastAPI, Celery, Redis, and MinIO. It's designed to offload heavy workloads (like image processing) to background workers to keep the main web server fast and responsive.

## Asynchronous Task Handling

Without background workers, a heavy image processing task would block the API, forcing the user to wait for a response and potentially causing timeouts during high traffic. To solve this, the architecture uses two main mechanisms:

1. Task Queuing (Redis): When a user uploads an image, the API instantly generates a background task, pushes it to Redis, and returns a 202 Accepted status with a tracking ID. The client isn't left waiting.
2. Background Processing (Celery & MinIO): A separate Celery worker constantly monitors Redis. It picks up pending tasks, converts the images to grayscale using Pillow, and uploads the final processed files to MinIO (a local S3 alternative). 

## Tech Stack

* FastAPI (Python 3.11)
* Celery
* Redis
* MinIO (Object Storage)
* Pillow & Boto3
* Docker & Docker Compose

## Running Locally

The easiest way to run the project is using Docker. You don't need Python or Redis installed locally.

1. Clone the repository and navigate into it.
2. Start the containers:
``` 
docker-compose up --build
```

3. The API will be available at http://localhost:8000/docs (Swagger UI).
4. The MinIO console is available at http://localhost:9001 (Credentials: `minioadmin` / `minioadmin`).

## Testing the Pipeline

To actually see the asynchronous nature of the pipeline in action, the worker includes a temporary 10-second artificial delay.

1. Open the Swagger UI and POST an image to the `/upload` endpoint. You will immediately get back a `task_id`.
2. Quickly copy the `task_id` and execute a GET request on the `/status/{task_id}` endpoint.

Expected result: Initially, you should see a `PENDING` status. If you wait 10 seconds and execute the same status request again, you will see it change to `SUCCESS` with the final MinIO filename.
