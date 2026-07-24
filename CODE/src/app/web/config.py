# -*- coding: utf-8 -*-
"""
Settings mínimos de la capa web del rebuild (clean-room, ADR-0004).

NO importa `app.config` (que exige credenciales AWS S3 al arrancar). Solo expone
lo que la capa web necesita: la conexión a la BD desde `DATABASE_URL`, leída de
forma perezosa (el app puede importarse sin la variable puesta).
"""

import os


def database_url() -> str:
    """La URL de la BD desde el entorno. Se lee al usarse, no al importar."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL no está definido (requerido por la capa web del rebuild)."
        )
    return url
