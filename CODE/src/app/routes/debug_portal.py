# -*- coding: utf-8 -*-
"""
Debug endpoint para verificar configuración del portal de clientes
"""

from fastapi import APIRouter
from app.config_routes import PUBLIC_ROUTES, API_PUBLIC_ROUTES, is_public_route, is_api_public_route

router = APIRouter(
    prefix="/api/debug",
    tags=["Debug Portal"]
)


@router.get("/portal-routes")
async def debug_portal_routes():
    """Endpoint público para verificar rutas del portal"""
    
    portal_html_routes = [r for r in PUBLIC_ROUTES if 'customer-portal' in r]
    portal_api_routes = [r for r in API_PUBLIC_ROUTES if 'customer-portal' in r]
    
    return {
        "portal_html_routes": sorted(portal_html_routes),
        "portal_api_routes": sorted(portal_api_routes),
        "test_results": {
            "/customer-portal": is_public_route("/customer-portal"),
            "/customer-portal/verify": is_public_route("/customer-portal/verify"),
            "/customer-portal/dashboard": is_public_route("/customer-portal/dashboard"),
            "/api/customer-portal/request-otp": is_api_public_route("/api/customer-portal/request-otp"),
            "/api/customer-portal/verify-otp": is_api_public_route("/api/customer-portal/verify-otp"),
        },
        "total_public_routes": len(PUBLIC_ROUTES),
        "total_api_public_routes": len(API_PUBLIC_ROUTES)
    }
