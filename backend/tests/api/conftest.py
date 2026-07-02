from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.data import models  # noqa: F401
from app.data.database import Base, get_session
from app.main import app
from app.routes.obligations import get_storage_gateway
from tests.fakes import FakeStorage


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_session() -> Iterator:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_storage_gateway] = lambda: FakeStorage()
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
