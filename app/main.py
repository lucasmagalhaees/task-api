import os
from fastapi import FastAPI

from app.database import engine, Base
from app.tasks import models  # noqa: F401 — registers models with Base
from app.tasks.router import router as tasks_router

os.makedirs("data", exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Task Management API")

app.include_router(tasks_router)


@app.get("/")
def home():
    return {"message": "Welcome to the Task Management API!"}
