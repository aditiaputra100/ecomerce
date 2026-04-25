from app.main import app


if __name__ == "__main__":
    import uvicorn

    from app.config import settings

    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
