"""
Vista "Avisos especiales" (`.scratch/avisos-especiales`): el ADMIN avisa a mano, por SMS o WhatsApp, a los clientes
con algo pendiente que ciertos días no hay servicio de paquetes. Solo ADMIN (`require_admin`). Las reglas viven en
`app.domain.aviso_especial_service`; esta capa solo arma la pantalla.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.domain.aviso_especial_service import listar_clientes
from app.domain.usuario import Usuario

from ..db import get_db
from ..security import require_admin
from ..templating import templates

router = APIRouter()


@router.get("/administracion/avisos-especiales", response_class=HTMLResponse)
def avisos_especiales(request: Request, db: Session = Depends(get_db), admin: Usuario = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/avisos_especiales.html",
        {"request": request, "admin": admin, "clientes": listar_clientes(db)},
    )
