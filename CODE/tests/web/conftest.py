# -*- coding: utf-8 -*-
"""
Fixtures de la capa web (rebuild PaqueteXv.2).

Reutiliza el arnés compartido (`tests/conftest.py` → Postgres efímero construido
con `alembic upgrade head`). Expone un `client` de FastAPI `TestClient` sobre el
app nuevo, con la dependencia de sesión sustituida por una atada a la BD migrada.

Aislamiento por test: la sesión del request corre dentro de una transacción
externa con `join_transaction_mode="create_savepoint"`, de modo que los `commit`
de las rutas liberan un savepoint y el `rollback` externo deshace todo al final.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.web.app import create_app
from app.web.db import get_db


@pytest.fixture()
def client(migrated_db_url):
    app = create_app()

    engine = create_engine(migrated_db_url)
    connection = engine.connect()
    outer = connection.begin()
    TestSession = sessionmaker(
        bind=connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )

    def _override_get_db():
        db = TestSession()
        try:
            yield db
            db.commit()  # libera un savepoint; la transacción externa sigue viva
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        if outer.is_active:
            outer.rollback()
        connection.close()
        engine.dispose()
