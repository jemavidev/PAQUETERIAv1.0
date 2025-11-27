# Tests de Comportamiento - Sistema de Autenticación

## Filosofía

Estos tests verifican **comportamiento real del usuario**, no implementación interna.

**Malo** ❌: Verificar que existe una función `checkAuthStatus()`
**Bueno** ✅: Verificar que la página de login NO se refresca automáticamente

## Herramientas

- **Playwright**: Tests end-to-end con navegador real
- **pytest**: Framework de testing
- **Docker**: Ambiente aislado

## Estructura de Tests

```
CODE/tests/
├── e2e/
│   ├── conftest.py              # Configuración de Playwright
│   ├── test_auth_flows.py       # Tests de flujos de autenticación
│   ├── test_no_loops.py         # Tests anti-loop
│   └── test_ajax_401.py         # Tests de AJAX 401
├── integration/
│   ├── test_middleware.py       # Tests del middleware
│   └── test_auth_endpoints.py   # Tests de endpoints
└── requirements-test.txt        # Dependencias de testing
```

## Tests E2E (End-to-End)

### Test 1: Login Normal Sin Loop

**Objetivo**: Verificar que el usuario puede hacer login sin loops de redirección

```python
@pytest.mark.e2e
async def test_login_normal_sin_loop(page: Page, base_url: str):
    """
    Escenario: Usuario no autenticado hace login exitoso
    
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
    await page.wait_for_url(f"{base_url}/auth/login?redirect=/admin")
    
    # Verificar que el formulario está visible
    username_field = page.locator("#username_or_email")
    await expect(username_field).to_be_visible()
    
    # Verificar que NO hay refrescos automáticos
    # Esperar 3 segundos y verificar que la URL no cambió
    await page.wait_for_timeout(3000)
    current_url = page.url
    assert "/auth/login" in current_url, "La página se refrescó inesperadamente"
    
    # Verificar que NO hay llamadas constantes a /api/auth/me
    # Monitorear requests durante 3 segundos
    auth_me_calls = []
    
    def track_requests(request):
        if "/api/auth/me" in request.url:
            auth_me_calls.append(request.url)
    
    page.on("request", track_requests)
    await page.wait_for_timeout(3000)
    
    # Debería haber 0 llamadas (o máximo 1 si hay verificación inicial)
    assert len(auth_me_calls) <= 1, f"Demasiadas llamadas a /api/auth/me: {len(auth_me_calls)}"
    
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
    dashboard_element = page.locator("text=Dashboard")
    await expect(dashboard_element).to_be_visible()
```

### Test 2: Página de Login NO Se Refresca

**Objetivo**: Verificar que la página de login es estable

```python
@pytest.mark.e2e
async def test_login_page_no_auto_refresh(page: Page, base_url: str):
    """
    Escenario: Página de login es estable
    
    Dado que soy un usuario no autenticado
    Cuando accedo a /auth/login
    Entonces veo el formulario de login
    Y la página NO se refresca automáticamente
    Y NO hay llamadas constantes a /api/auth/me
    """
    # Limpiar cookies
    await page.context.clear_cookies()
    
    # Monitorear requests
    auth_me_calls = []
    page_loads = []
    
    def track_requests(request):
        if "/api/auth/me" in request.url:
            auth_me_calls.append({
                "url": request.url,
                "timestamp": page.evaluate("Date.now()")
            })
    
    def track_page_loads(frame):
        if frame == page.main_frame:
            page_loads.append(page.evaluate("Date.now()"))
    
    page.on("request", track_requests)
    page.on("framenavigated", track_page_loads)
    
    # Ir a login
    await page.goto(f"{base_url}/auth/login")
    
    # Verificar que el formulario está visible
    await expect(page.locator("#username_or_email")).to_be_visible()
    
    # Esperar 5 segundos y monitorear
    await page.wait_for_timeout(5000)
    
    # Verificar que NO hay llamadas constantes a /api/auth/me
    assert len(auth_me_calls) <= 1, f"Demasiadas llamadas a /api/auth/me: {auth_me_calls}"
    
    # Verificar que NO hay recargas de página
    assert len(page_loads) == 1, f"La página se recargó {len(page_loads)} veces"
    
    # Verificar que la URL no cambió
    assert page.url == f"{base_url}/auth/login", "La URL cambió inesperadamente"
```

### Test 3: Usuario Autenticado Redirigido Desde Login

**Objetivo**: Verificar auto-redirect cuando ya está autenticado

```python
@pytest.mark.e2e
async def test_authenticated_user_redirected_from_login(page: Page, base_url: str, authenticated_context):
    """
    Escenario: Usuario autenticado no ve formulario de login
    
    Dado que soy un usuario autenticado
    Cuando intento acceder a /auth/login
    Entonces soy redirigido automáticamente a /dashboard
    Y NO veo el formulario de login
    """
    # Usar contexto autenticado (con cookies válidas)
    page = await authenticated_context.new_page()
    
    # Intentar acceder a login
    await page.goto(f"{base_url}/auth/login")
    
    # Verificar redirección automática
    await page.wait_for_url(f"{base_url}/packages", timeout=3000)
    
    # Verificar que NO vemos el formulario de login
    username_field = page.locator("#username_or_email")
    await expect(username_field).not_to_be_visible()
    
    # Verificar que vemos contenido protegido
    protected_content = page.locator("text=Paquetes")
    await expect(protected_content).to_be_visible()
```

### Test 4: Token Expirado Muestra Mensaje

**Objetivo**: Verificar mensaje de sesión expirada

```python
@pytest.mark.e2e
async def test_expired_token_shows_message(page: Page, base_url: str):
    """
    Escenario: Token expirado muestra mensaje claro
    
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
```

### Test 5: AJAX 401 Redirige Correctamente

**Objetivo**: Verificar que llamadas AJAX 401 manejan redirección

```python
@pytest.mark.e2e
async def test_ajax_401_redirects_correctly(page: Page, base_url: str, authenticated_context):
    """
    Escenario: AJAX 401 muestra notificación y redirige
    
    Dado que estoy en una página protegida
    Y mi sesión expira
    Cuando hago una llamada AJAX que retorna 401
    Entonces veo una notificación "Sesión expirada"
    Y soy redirigido a /auth/login
    """
    # Usar contexto autenticado
    page = await authenticated_context.new_page()
    
    # Ir a página protegida
    await page.goto(f"{base_url}/admin")
    await expect(page.locator("text=Dashboard")).to_be_visible()
    
    # Simular expiración de sesión (eliminar cookies)
    await page.context.clear_cookies()
    
    # Hacer una llamada AJAX que debería retornar 401
    response = await page.evaluate("""
        async () => {
            const response = await fetch('/api/packages', {
                credentials: 'include'
            });
            return {
                status: response.status,
                ok: response.ok
            };
        }
    """)
    
    # Verificar que retornó 401
    assert response["status"] == 401, f"Esperaba 401, obtuvo {response['status']}"
    
    # Verificar que aparece notificación
    notification = page.locator("text=Sesión expirada")
    await expect(notification).to_be_visible(timeout=3000)
    
    # Verificar redirección a login
    await page.wait_for_url(f"{base_url}/auth/login", timeout=5000)
```

### Test 6: Múltiples Pestañas Comparten Sesión

**Objetivo**: Verificar que la sesión funciona en múltiples pestañas

```python
@pytest.mark.e2e
async def test_multiple_tabs_share_session(page: Page, base_url: str, authenticated_context):
    """
    Escenario: Sesión compartida entre pestañas
    
    Dado que estoy autenticado en una pestaña
    Cuando abro una nueva pestaña
    Y accedo a una ruta protegida
    Entonces accedo directamente sin pedir login
    """
    # Pestaña 1: Login
    page1 = await authenticated_context.new_page()
    await page1.goto(f"{base_url}/admin")
    await expect(page1.locator("text=Dashboard")).to_be_visible()
    
    # Pestaña 2: Acceder a otra ruta protegida
    page2 = await authenticated_context.new_page()
    await page2.goto(f"{base_url}/packages")
    
    # Verificar que NO pide login
    await expect(page2.locator("text=Paquetes")).to_be_visible(timeout=3000)
    
    # Verificar que NO vemos formulario de login
    username_field = page2.locator("#username_or_email")
    await expect(username_field).not_to_be_visible()
```

## Tests de Integración

### Test 7: Middleware Protege Rutas Correctamente

```python
@pytest.mark.integration
async def test_middleware_protects_routes(client: TestClient):
    """
    Verificar que el middleware protege rutas correctamente
    """
    # Rutas protegidas sin autenticación → 302 redirect
    protected_routes = ["/admin", "/packages", "/profile"]
    
    for route in protected_routes:
        response = client.get(route, follow_redirects=False)
        assert response.status_code == 302, f"Ruta {route} no está protegida"
        assert "/auth/login" in response.headers["location"]
    
    # Rutas públicas sin autenticación → 200 OK
    public_routes = ["/", "/announce", "/search", "/auth/login"]
    
    for route in public_routes:
        response = client.get(route)
        assert response.status_code == 200, f"Ruta {route} no es pública"
```

### Test 8: API Retorna 401 JSON

```python
@pytest.mark.integration
async def test_api_returns_401_json(client: TestClient):
    """
    Verificar que las APIs retornan 401 JSON, no redirect
    """
    # APIs protegidas sin autenticación → 401 JSON
    api_routes = ["/api/packages", "/api/admin/users", "/api/profile"]
    
    for route in api_routes:
        response = client.get(route)
        assert response.status_code == 401, f"API {route} no retorna 401"
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert "detail" in data
        assert "redirect_url" in data or "requires_auth" in data
```

### Test 9: Endpoint Config Retorna Rutas Públicas

```python
@pytest.mark.integration
async def test_config_endpoint_returns_public_routes(client: TestClient):
    """
    Verificar que el endpoint de configuración funciona
    """
    response = client.get("/api/config/public-routes")
    assert response.status_code == 200
    
    data = response.json()
    assert "public_routes" in data
    assert "api_public_routes" in data
    
    # Verificar que contiene rutas esperadas
    assert "/" in data["public_routes"]
    assert "/auth/login" in data["public_routes"]
    assert "/api/auth/login" in data["api_public_routes"]
```

## Fixtures de Pytest

```python
# CODE/tests/e2e/conftest.py

import pytest
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

@pytest.fixture(scope="session")
def base_url():
    """URL base de la aplicación"""
    return "http://localhost:8000"

@pytest.fixture(scope="session")
async def browser():
    """Navegador Playwright"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()

@pytest.fixture
async def context(browser: Browser):
    """Contexto de navegador limpio"""
    context = await browser.new_context()
    yield context
    await context.close()

@pytest.fixture
async def page(context: BrowserContext):
    """Página limpia"""
    page = await context.new_page()
    yield page
    await page.close()

@pytest.fixture
async def authenticated_context(browser: Browser, base_url: str):
    """Contexto con usuario autenticado"""
    context = await browser.new_context()
    page = await context.new_page()
    
    # Hacer login
    await page.goto(f"{base_url}/auth/login")
    await page.locator("#username_or_email").fill("jesus")
    await page.locator("#password").fill("jesusSeaboard12")
    await page.locator("button[type='submit']").click()
    
    # Esperar redirección exitosa
    await page.wait_for_url(f"{base_url}/packages", timeout=5000)
    
    await page.close()
    yield context
    await context.close()
```

## Ejecución de Tests

### Instalación

```bash
cd CODE
pip install -r tests/requirements-test.txt
playwright install chromium
```

### Ejecutar Todos los Tests

```bash
pytest tests/ -v
```

### Ejecutar Solo Tests E2E

```bash
pytest tests/e2e/ -v
```

### Ejecutar Test Específico

```bash
pytest tests/e2e/test_auth_flows.py::test_login_normal_sin_loop -v
```

### Ejecutar con Navegador Visible (Debug)

```bash
pytest tests/e2e/ -v --headed
```

### Generar Reporte HTML

```bash
pytest tests/ --html=report.html --self-contained-html
```

## Integración con CI/CD

```yaml
# .github/workflows/test.yml

name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r CODE/requirements.txt
          pip install -r CODE/tests/requirements-test.txt
          playwright install chromium
      
      - name: Start application
        run: |
          cd CODE
          uvicorn src.main:app --host 0.0.0.0 --port 8000 &
          sleep 5
      
      - name: Run tests
        run: |
          cd CODE
          pytest tests/ -v --html=report.html
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: CODE/report.html
```

## Métricas de Cobertura

### Objetivo: 90% de cobertura en flujos críticos

- ✅ Login normal
- ✅ Login con token expirado
- ✅ Auto-redirect desde login
- ✅ AJAX 401 handling
- ✅ Múltiples pestañas
- ✅ Protección de rutas
- ✅ APIs retornan JSON

## Mantenimiento

### Agregar Nuevo Test

1. Identificar comportamiento a verificar
2. Escribir test en `tests/e2e/test_*.py`
3. Ejecutar test: `pytest tests/e2e/test_*.py::test_name -v`
4. Verificar que pasa
5. Commit y push

### Actualizar Tests Después de Cambios

1. Ejecutar todos los tests: `pytest tests/ -v`
2. Si fallan, verificar si es regresión o cambio esperado
3. Actualizar tests según sea necesario
4. Documentar cambios en CHANGELOG.md

## Conclusión

Estos tests verifican **comportamiento real**, no implementación. Si el comportamiento es correcto, los tests pasan, independientemente de cómo esté implementado internamente.

**Ventajas**:
- Detectan regresiones reales
- No se rompen con refactors internos
- Documentan comportamiento esperado
- Pueden ejecutarse en CI/CD
- Usan navegador real (Playwright)
