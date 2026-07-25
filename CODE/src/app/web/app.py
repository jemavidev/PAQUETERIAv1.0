# -*- coding: utf-8 -*-
"""
App factory de la capa web del rebuild (clean-room, ADR-0004).

Arranca SIN credenciales AWS y sin importar el `config`/app viejos. Crece ruta por
ruta; eventualmente reemplaza `src/main.py` (strangler fig).
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from .config import secret_key
from .routes.announce import router as announce_router
from .routes.auth import router as auth_router
from .routes.health import router as health_router
from .routes.packages import router as packages_router
from .routes.search import router as search_router

_WEB_DIR = Path(__file__).resolve().parent
_STATIC_DIR = _WEB_DIR / "static"


async def _redirigir_no_autenticado(request: Request, exc: StarletteHTTPException):
    """Un 401 en una ruta con privilegios manda al login; el resto usa el default."""
    if exc.status_code == 401:
        return RedirectResponse("/auth/login", status_code=303)
    return await http_exception_handler(request, exc)


def create_app() -> FastAPI:
    app = FastAPI(title="PAQUETEX — rebuild PaqueteXv.2")
    # Sesión por cookie firmada (el actor de las acciones sale de aquí).
    app.add_middleware(SessionMiddleware, secret_key=secret_key())
    app.add_exception_handler(StarletteHTTPException, _redirigir_no_autenticado)

    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")
    app.include_router(health_router)
    app.include_router(announce_router)
    app.include_router(auth_router)
    app.include_router(packages_router)
    app.include_router(search_router)
    return app


app = create_app()
