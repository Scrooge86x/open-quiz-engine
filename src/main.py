from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.attempt_routes import router as attempt_router
from src.api.error_handlers import register_error_handlers
from src.api.quiz_routes import router as quiz_router
from src.config import APP_TITLE, APP_VERSION, DATABASE_URL
from src.db.engine import create_db_engine, create_session_factory, create_tables

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(database_url: str = DATABASE_URL) -> FastAPI:
    app = FastAPI(title=APP_TITLE, version=APP_VERSION)
    engine = create_db_engine(database_url)
    session_factory = create_session_factory(engine)
    create_tables(engine)
    app.state.session_factory = session_factory
    register_error_handlers(app)
    app.include_router(quiz_router)
    app.include_router(attempt_router)
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app


app = create_app()
