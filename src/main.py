from fastapi import FastAPI

from src.config import APP_TITLE, APP_VERSION


def create_app() -> FastAPI:
    return FastAPI(title=APP_TITLE, version=APP_VERSION)


app = create_app()
