from fastapi import FastAPI

from src.config import APP_TITLE, APP_VERSION, DATABASE_URL
from src.db.engine import create_db_engine, create_session_factory, create_tables


def create_app(database_url: str = DATABASE_URL) -> FastAPI:
    app = FastAPI(title=APP_TITLE, version=APP_VERSION)
    engine = create_db_engine(database_url)
    session_factory = create_session_factory(engine)
    create_tables(engine)
    app.state.session_factory = session_factory
    return app


app = create_app()
