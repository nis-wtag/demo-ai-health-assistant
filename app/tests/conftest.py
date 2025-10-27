import pytest
from alembic.command import upgrade
from alembic.config import Config
from core.config import settings
from core.database import Base, get_db
from fastapi.testclient import TestClient
from main import app
from middleware import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database


@pytest.fixture(scope="session")
def db_engine():
    test_db_url = settings.DATABASE_URL

    server_db_url = settings.TEST_SERVER_DATABASE_URL

    engine = create_engine(server_db_url)
    conn = engine.connect()

    if database_exists(test_db_url):
        logger.info(f"Test database {test_db_url} already exists. Dropping...")
        drop_database(test_db_url)

    logger.info(f"Creating test database {test_db_url}")
    create_database(test_db_url)
    conn.close()

    test_engine = create_engine(test_db_url)

    logger.info(f"Running migrations on {test_db_url}...")

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)

    upgrade(alembic_cfg, "head")
    logger.info(f"Test database {test_db_url} created and migration applied.")

    yield test_engine

    logger.info(f"Droping test database {test_db_url}...")
    test_engine.dispose()
    drop_database(test_db_url)
    logger.info(f"Test database {test_db_url} dropped.")


@pytest.fixture(scope="session")
def TestSessionLocal(db_engine):
    return sessionmaker(autoflush=False, bind=db_engine)


@pytest.fixture(scope="function")
def db_session(TestSessionLocal):
    session = TestSessionLocal()
    try:
        session.begin()
        yield session
    finally:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        session.commit()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    del app.dependency_overrides[get_db]
