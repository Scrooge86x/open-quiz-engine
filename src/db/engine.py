from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def create_db_engine(database_url: str) -> Engine:
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    if database_url == "sqlite://":
        engine_kwargs["poolclass"] = StaticPool

    return create_engine(database_url, connect_args=connect_args, **engine_kwargs)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)
