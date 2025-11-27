# ========================================
# PAQUETES EL CLUB v2.0 - Configuración de Tests E2E
# ========================================
# Archivo: CODE/tests/e2e/conftest.py
# Versión: 2.0.0
# Fecha: 2025-01-27
# ========================================

"""
Configuración de fixtures para tests end-to-end con Playwright.
"""

import pytest
import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def event_loop():
    """Crear event loop para tests async"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def base_url():
    """URL base de la aplicación"""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
async def playwright_instance():
    """Instancia de Playwright"""
    async with async_playwright() as p:
        yield p


@pytest.fixture(scope="session")
async def browser(playwright_instance: Playwright):
    """Navegador Playwright (Chromium)"""
    browser = await playwright_instance.chromium.launch(
        headless=True,  # Cambiar a False para ver el navegador
        slow_mo=50      # Ralentizar para debugging
    )
    yield browser
    await browser.close()


@pytest.fixture
async def context(browser: Browser):
    """Contexto de navegador limpio para cada test"""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="es-CO",
        timezone_id="America/Bogota"
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext):
    """Página limpia para cada test"""
    page = await context.new_page()
    
    # Configurar timeout por defecto
    page.set_default_timeout(10000)  # 10 segundos
    
    # Logging de errores de consola
    page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
    
    yield page
    await page.close()


@pytest.fixture
async def authenticated_context(browser: Browser, base_url: str):
    """
    Contexto con usuario autenticado.
    
    Realiza login y retorna el contexto con cookies de sesión.
    """
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="es-CO",
        timezone_id="America/Bogota"
    )
    
    page = await context.new_page()
    
    try:
        # Ir a página de login
        await page.goto(f"{base_url}/auth/login")
        
        # Llenar formulario
        await page.locator("#username_or_email").fill("jesus")
        await page.locator("#password").fill("jesusSeaboard12")
        
        # Submit
        await page.locator("button[type='submit']").click()
        
        # Esperar redirección exitosa
        await page.wait_for_url(f"{base_url}/packages", timeout=5000)
        
        # Verificar que hay cookies de sesión
        cookies = await context.cookies()
        access_token = next((c for c in cookies if c["name"] == "access_token"), None)
        
        if not access_token:
            raise Exception("Login falló: no se estableció cookie access_token")
        
        print(f"✅ Usuario autenticado exitosamente")
        
    finally:
        await page.close()
    
    yield context
    await context.close()


@pytest.fixture
async def expired_token_context(browser: Browser):
    """
    Contexto con token expirado.
    
    Establece una cookie con token inválido para simular sesión expirada.
    """
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720}
    )
    
    # Establecer cookie con token expirado
    await context.add_cookies([{
        "name": "access_token",
        "value": "expired_token_12345",
        "domain": "localhost",
        "path": "/",
        "expires": -1
    }])
    
    yield context
    await context.close()


# Helpers para tests

async def wait_for_no_network_activity(page: Page, timeout: int = 2000):
    """
    Esperar a que no haya actividad de red.
    
    Útil para verificar que no hay llamadas constantes a APIs.
    """
    await page.wait_for_load_state("networkidle", timeout=timeout)


async def count_requests_to_url(page: Page, url_pattern: str, duration_ms: int = 3000) -> int:
    """
    Contar cuántas requests se hacen a una URL en un período de tiempo.
    
    Args:
        page: Página de Playwright
        url_pattern: Patrón de URL a buscar (ej: "/api/auth/me")
        duration_ms: Duración en milisegundos
    
    Returns:
        Número de requests que coinciden con el patrón
    """
    requests = []
    
    def track_request(request):
        if url_pattern in request.url:
            requests.append(request.url)
    
    page.on("request", track_request)
    await page.wait_for_timeout(duration_ms)
    page.remove_listener("request", track_request)
    
    return len(requests)


async def assert_no_console_errors(page: Page):
    """
    Verificar que no hay errores en la consola.
    """
    errors = []
    
    def track_error(msg):
        if msg.type == "error":
            errors.append(msg.text)
    
    page.on("console", track_error)
    
    # Esperar un momento para capturar errores
    await page.wait_for_timeout(1000)
    
    page.remove_listener("console", track_error)
    
    assert len(errors) == 0, f"Errores en consola: {errors}"
