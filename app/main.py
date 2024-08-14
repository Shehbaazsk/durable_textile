from fastapi import FastAPI
from app.apis.user.routes import user_router
from app.config.middleware import LoggingMiddleware


def create_application():
    application = FastAPI()
    application.add_middleware(LoggingMiddleware)
    application.include_router(user_router, prefix='/api')
    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Hi, I am FastAPI"}
