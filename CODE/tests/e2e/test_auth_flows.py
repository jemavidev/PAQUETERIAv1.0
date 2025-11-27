# ========================================
# PAQUETES EL CLUB v2.0 - Tests de Flujos de Autenticación
# ========================================
# Archivo: CODE/tests/e2e/test_auth_flows.py
# Versión: 2.0.0
# Fecha: 2025-01-27
# ========================================

"""
Tests end-to-end de flujos de autenticación.

Estos tests verifican COMPORTAMIENTO, no implementación.
"""

import pytest
from playwright.async_api import Page, BrowserContext, expect
from .conftest import count_requests_to_url


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_login_normal_sin_loop(page: Page, base_url: str):
    """
    Test: Usuario no autenticado hace login exitoso sin loops
    
    Escenario:
        Dado que soy un usuario no autenticado
        Cuando accedo a /admin
        Entonces soy redirigido a /auth/login
        Y veo el formulario de login
        Y la página NO se refresca automáticamente
        Cuando ingreso credenciales válidas
        Y hago click en "Iniciar Sesión"
        Entonces soy redirigido a /admin
        Y veo el dashboard
        Y NO entro en loop de redirección
    """
    # Limpiar cookies
    await page.context.clear_cookies()
    
    # Intentar acceder a ruta protegida
    await page.goto(f"{base_url}/admin")
    
    # Verificar redirección a login
    await page.wait_for_url(f"{base_url}/auth/login?redirect=/admin", timeout=5000)
    
    # Verificar que el formulario está visible
    username_field = page.locator("#username_or_email")
    await expect(username_field).to_be_visible()
    
    # Verificar que NO hay refrescos automáticos
    # Esperar 3 segundos y verificar que la URL no cambió
    await page.wait_for_timeout(3000)
    current_url = page.url
    assert "/auth/login" in current_url, "La página se refrescó inesperadamente"
    
    # Verificar que NO hay llamadas constantes a /api/auth/me
    auth_me_count = await count_requests_to_url(page, "/api/auth/me", 3000)
    assert auth_me_count <= 1, f"Demasiadas llamadas a /api/auth/me: {auth_me_count}"
    
    # Hacer login
    await username_field.fill("jesus")
    await page.locator("#password").fill("jesusSeaboard12")
    await page.locator("button[type='submit']").click()
    
    # Verificar redirección a /admin
    await page.wait_for_url(f"{base_url}/admin", timeout=5000)
    
    # Verificar que NO hay loop (esperar 2 segundos y verificar URL)
    await page.wait_for_timeout(2000)
    assert page.url == f"{base_url}/admin", "Entró en loop de redirección"
    
    # Verificar que el dashboard está visible
    # (ajustar selector según tu implementación)
    await expect(page.locator("body")).to_contain_text("Admin")


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_login_page_no_auto_refresh(page: Page, base_url: str):
    """
    Test: Página de login es estable y no se refresca automáticamente
    
    Escenario:
        Dado que soy un usuario no autenticado
        Cuando accedo a /auth/login
        Entonces veo el formulario de login
        Y la página NO se refresca automáticamente
        Y NO hay llamadas constantes a /api/auth/me
    """
    # Limpiar cookies
    await page.context.clear_cookies()
    
    # Monitorear recargas de página
    page_loads = []
    
    def track_page_load(frame):
        if frame == page.main_frame:
            page_loads.append(True)
    
    page.on("framenavigated", track_page_load)
    
    # Ir a login
    await page.goto(f"{base_url}/auth/login")
    
    # Verificar que el formulario está visible
    await expect(page.locator("#username_or_email")).to_be_visible()
    
    # Esperar 5 segundos y monitorear
    await page.wait_for_timeout(5000)
    
    # Verificar que NO hay llamadas constantes a /api/auth/me
    auth_me_count = await count_requests_to_url(page, "/api/auth/me", 3000)
    assert auth_me_count <= 1, f"Demasiadas llamadas a /api/auth/me: {auth_me_count}"
    
    # Verificar que NO hay recargas de página (solo la carga inicial)
    assert len(page_loads) == 1, f"La página se recargó {len(page_loads)} veces"
    
    # Verificar que la URL no cambió
    assert page.url == f"{base_url}/auth/login", "La URL cambió inesperadamente"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_authenticated_user_redirected_from_login(authenticated_context: BrowserContext, base_url: str):
    """
    Test: Usuario autenticado es redirigido automáticamente desde login
    
    Escenario:
        Dado que soy un usuario autenticado
        Cuando intento acceder a /auth/login
        Entonces soy redirigido automáticamente a /packages
        Y NO veo el formulario de login
    """
    # Usar contexto autenticado
    page = await authenticated_context.new_page()
    
    try:
        # Intentar acceder a login
        await page.goto(f"{base_url}/auth/login")
        
        # Verificar redirección automática
        await page.wait_for_url(f"{base_url}/packages", timeout=3000)
        
        # Verificar que NO vemos el formulario de login
        username_field = page.locator("#username_or_email")
        await expect(username_field).not_to_be_visible()
        
        # Verificar que vemos contenido protegido
        await expect(page.locator("body")).to_contain_text("Paquetes")
        
    finally:
        await page.close()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_expired_token_shows_message(page: Page, base_url: str):
    """
    Test: Token expirado muestra mensaje claro
    
    Escenario:
        Dado que tengo un token expirado en cookies
        Cuando accedo a /auth/login
        Entonces veo el mensaje "Tu sesión ha expirado"
        Y las cookies son limpiadas automáticamente
    """
    # Establecer cookie con token expirado
    await page.context.add_cookies([{
        "name": "access_token",
        "value": "expired_token_12345",
        "domain": "localhost",
        "path": "/"
    }])
    
    # Ir a login
    await page.goto(f"{base_url}/auth/login")
    
    # Verificar mensaje de sesión expirada
    expired_message = page.locator("text=Tu sesión ha expirado")
    await expect(expired_message).to_be_visible(timeout=2000)
    
    # Verificar que las cookies fueron limpiadas
    cookies = await page.context.cookies()
    access_token_cookie = next((c for c in cookies if c["name"] == "access_token"), None)
    
    # La cookie debería estar vacía o eliminada
    assert access_token_cookie is None or access_token_cookie["value"] == "", \
        "La cookie no fue limpiada"


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multiple_tabs_share_session(authenticated_context: BrowserContext, base_url: str):
    """
    Test: Sesión compartida entre múltiples pestañas
    
    Escenario:
        Dado que estoy autenticado en una pestaña
        Cuando abro una nueva pestaña
        Y accedo a una ruta protegida
        Entonces accedo directamente sin pedir login
    """
    # Pestaña 1: Verificar que estamos autenticados
    page1 = await authenticated_context.new_page()
    
    try:
        await page1.goto(f"{base_url}/admin")
        await expect(page1.locator("body")).to_contain_text("Admin")
        
        # Pestaña 2: Acceder a otra ruta protegida
        page2 = await authenticated_context.new_page()
        
        try:
            await page2.goto(f"{base_url}/packages")
            
            # Verificar que NO pide login
            await expect(page2.locator("body")).to_contain_text("Paquetes")
            
            # Verificar que NO vemos formulario de login
            username_field = page2.locator("#username_or_email")
            await expect(username_field).not_to_be_visible()
            
        finally:
            await page2.close()
            
    finally:
        await page1.close()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_protected_route_requires_auth(page: Page, base_url: str):
    """
    Test: Rutas protegidas requieren autenticación
    
    Escenario:
        Dado que soy un usuario no autenticado
        Cuando intento acceder a una ruta protegida
        Entonces soy redirigido a /auth/login
        Y el parámetro redirect contiene la URL original
    """
    # Limpiar cookies
    await page.context.clear_cookies()
    
    # Rutas protegidas a probar
    protected_routes = ["/admin", "/packages", "/profile"]
    
    for route in protected_routes:
        await page.goto(f"{base_url}{route}")
        
        # Verificar redirección a login
        await page.wait_for_url(f"{base_url}/auth/login?redirect={route}", timeout=3000)
        
        # Verificar que el formulario está visible
        await expect(page.locator("#username_or_email")).to_be_visible()


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_public_routes_accessible_without_auth(page: Page, base_url: str):
    """
    Test: Rutas públicas son accesibles sin autenticación
    
    Escenario:
        Dado que soy un usuario no autenticado
        Cuando accedo a una ruta pública
        Entonces veo el contenido sin ser redirigido a login
    """
    # Limpiar cookies
    await page.context.clear_cookies()
    
    # Rutas públicas a probar
    public_routes = [
        ("/", "Paquetes"),
        ("/announce", "Anunciar"),
        ("/search", "Buscar"),
    ]
    
    for route, expected_text in public_routes:
        await page.goto(f"{base_url}{route}")
        
        # Verificar que NO fuimos redirigidos a login
        assert "/auth/login" not in page.url, f"Ruta {route} redirigió a login"
        
        # Verificar que vemos contenido esperado
        await expect(page.locator("body")).to_contain_text(expected_text, timeout=3000)
