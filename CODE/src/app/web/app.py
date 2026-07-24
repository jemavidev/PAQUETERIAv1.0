# -*- coding: utf-8 -*-
"""
App factory de la capa web del rebuild (clean-room, ADR-0004).

Arranca SIN credenciales AWS y sin importar el `config`/app viejos. Crece ruta por
ruta; eventualmente reemplaza `src/main.py` (strangler fig).
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes.announce import router as announce_router
from .routes.health import router as health_router

_WEB_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _WEB_DIR / "static"


def create_app() -> FastAPI:
    app = FastAPI(title="PAQUETEX — rebuild PaqueteXv.2")
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    app.include_router(health_router)
    app.include_router(announce_router)
    return app


app = create_app()
