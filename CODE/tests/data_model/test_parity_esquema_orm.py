# -*- coding: utf-8 -*-
"""
Guard de paridad esquema ↔ ORM.

La forma de `personas` se declara en DOS lugares: el modelo ORM
(`app.domain.persona`) y la migración baseline. Este test evita que diverjan:
tras construir la BD con `alembic upgrade head`, `compare_metadata` no debe
encontrar NINGUNA diferencia contra `Base.metadata`. Si alguien cambia el modelo
sin escribir la migración (o al revés), este test lo atrapa antes de que aterricen
más rebanadas sobre el mismo árbol.
"""

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine

from app.domain.base import Base
from app.domain import persona  # noqa: F401  (registra 'personas' en Base.metadata)

pytestmark = pytest.mark.integration


def test_migracion_y_orm_no_divergen(migrated_db_url):
    engine = create_engine(migrated_db_url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diffs = compare_metadata(context, Base.metadata)
    finally:
        engine.dispose()

    assert diffs == [], (
        "El esquema migrado y el modelo ORM divergen (drift de autogenerate). "
        f"Diferencias detectadas: {diffs}"
    )
