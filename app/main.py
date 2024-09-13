from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.apis.collection.routes import collection_router
from app.apis.user.routes import user_router
from app.config.middleware import LoggingMiddleware


def create_application():
    application = FastAPI()
    application.add_middleware(LoggingMiddleware)
    application.include_router(user_router, prefix="/api")
    application.include_router(collection_router, prefix="/api")
    return application


app = create_application()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"message": "Hi, I am FastAPI"}


@app.get("/static/{filename}")
async def get_static_file(filename: str):
    return FileResponse(f"../uploads/{filename}")
