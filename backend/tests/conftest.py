import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def default_to_mock_provider(monkeypatch):
    monkeypatch.setenv("APP_LLM_PROVIDER", "mock")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_MAX_OUTPUT_TOKENS", raising=False)
    monkeypatch.delenv("OPENAI_TIMEOUT_SECONDS", raising=False)


@pytest.fixture()
def client(tmp_path):
    test_db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{test_db_path.as_posix()}"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
