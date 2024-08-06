from fastapi import FastAPI
from app.apis.user.routes import user_router


def create_application():
    application = FastAPI()
    application.include_router(user_router)
    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Hi, I am FastAPI"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
