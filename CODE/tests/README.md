# Tests - PAQUETES EL CLUB v2.0

## Descripción

Tests de comportamiento para el sistema de autenticación refactorizado.

Estos tests verifican **comportamiento real del usuario**, no implementación interna.

## Estructura

```
tests/
├── e2e/                          # Tests end-to-end con Playwright
│   ├── conftest.py              # Configuración y fixtures
│   ├── test_auth_flows.py       # Tests de flujos de autenticación
│   ├── test_no_loops.py         # Tests anti-loop
│   └── test_ajax_401.py         # Tests de AJAX 401
├── integration/                  # Tests de integración
│   ├── test_middleware.py       # Tests del middleware
│   └── test_auth_endpoints.py   # Tests de endpoints
├── requirements-test.txt         # Dependencias de testing
└── README.md                     # Este archivo
```

## Instalación

### 1. Instalar dependencias

```bash
cd CODE
pip install -r tests/requirements-test.txt
```

### 2. Instalar navegadores de Playwright

```bash
playwright install chromium
```

## Ejecución

### Ejecutar todos los tests

```bash
cd CODE
pytest tests/ -v
```

### Ejecutar solo tests E2E

```bash
pytest tests/e2e/ -v
```

### Ejecutar test específico

```bash
pytest tests/e2e/test_auth_flows.py::test_login_normal_sin_loop -v
```

### Ejecutar con navegador visible (para debugging)

```bash
pytest tests/e2e/ -v --headed
```

### Ejecutar con modo lento (para ver qué pasa)

```bash
pytest tests/e2e/ -v --headed --slowmo=1000
```

### Generar reporte HTML

```bash
pytest tests/ --html=report.html --self-contained-html
```

### Ejecutar con cobertura

```bash
pytest tests/ --cov=src/app --cov-report=html
```

## Tests Disponibles

### Tests E2E (End-to-End)

#### test_auth_flows.py

- ✅ `test_login_normal_sin_loop`: Login exitoso sin loops
- ✅ `test_login_page_no_auto_refresh`: Página de login estable
- ✅ `test_authenticated_user_redirected_from_login`: Auto-redirect desde login
- ✅ `test_expired_token_shows_message`: Mensaje de sesión expirada
- ✅ `test_multiple_tabs_share_session`: Sesión compartida entre pestañas
- ✅ `test_protected_route_requires_auth`: Rutas protegidas requieren auth
- ✅ `test_public_routes_accessible_without_auth`: Rutas públicas accesibles

## Fixtures Disponibles

### `base_url`
URL base de la aplicación (default: `http://localhost:8000`)

### `browser`
Navegador Chromium de Playwright

### `context`
Contexto de navegador limpio para cada test

### `page`
Página limpia para cada test

### `authenticated_context`
Contexto con usuario autenticado (cookies de sesión)

### `expired_token_context`
Contexto con token expirado

## Helpers

### `count_requests_to_url(page, url_pattern, duration_ms)`
Contar requests a una URL en un período de tiempo

```python
auth_me_count = await count_requests_to_url(page, "/api/auth/me", 3000)
assert auth_me_count <= 1, "Demasiadas llamadas"
```

### `wait_for_no_network_activity(page, timeout)`
Esperar a que no haya actividad de red

```python
await wait_for_no_network_activity(page, 2000)
```

### `assert_no_console_errors(page)`
Verificar que no hay errores en consola

```python
await assert_no_console_errors(page)
```

## Debugging

### Ver navegador durante tests

```bash
pytest tests/e2e/ -v --headed
```

### Pausar ejecución en un punto

```python
await page.pause()  # Abre inspector de Playwright
```

### Capturar screenshot

```python
await page.screenshot(path="debug.png")
```

### Ver logs de consola

Los logs de consola se imprimen automáticamente:

```python
page.on("console", lambda msg: print(f"[CONSOLE] {msg.type}: {msg.text}"))
```

## Troubleshooting

### Error: "Playwright not installed"

```bash
playwright install chromium
```

### Error: "Connection refused"

Asegúrate de que la aplicación esté corriendo:

```bash
cd CODE
docker-compose up -d
# O
uvicorn src.main:app --reload
```

### Error: "Test timeout"

Aumenta el timeout en `conftest.py`:

```python
page.set_default_timeout(30000)  # 30 segundos
```

### Tests fallan en CI/CD

Asegúrate de que Playwright esté instalado en CI:

```yaml
- name: Install Playwright
  run: playwright install chromium --with-deps
```

## Integración con CI/CD

Ver ejemplo en `.github/workflows/test.yml`

## Mejores Prácticas

### 1. Tests deben ser independientes

Cada test debe poder ejecutarse solo:

```bash
pytest tests/e2e/test_auth_flows.py::test_login_normal_sin_loop -v
```

### 2. Limpiar estado entre tests

Usa fixtures que limpian cookies y contexto:

```python
@pytest.fixture
async def page(context: BrowserContext):
    page = await context.new_page()
    yield page
    await page.close()
```

### 3. Usar selectores estables

Preferir IDs sobre clases:

```python
# Bueno ✅
await page.locator("#username_or_email").fill("jesus")

# Malo ❌
await page.locator(".input-field").first.fill("jesus")
```

### 4. Esperar elementos antes de interactuar

```python
# Bueno ✅
await expect(page.locator("#submit")).to_be_visible()
await page.locator("#submit").click()

# Malo ❌
await page.locator("#submit").click()  # Puede fallar si no está visible
```

### 5. Verificar comportamiento, no implementación

```python
# Bueno ✅
assert "/auth/login" not in page.url, "No debería redirigir a login"

# Malo ❌
assert "checkAuthStatus" in page.content(), "Función debe existir"
```

## Mantenimiento

### Agregar nuevo test

1. Crear archivo en `tests/e2e/test_*.py`
2. Escribir test con decorador `@pytest.mark.e2e`
3. Ejecutar: `pytest tests/e2e/test_*.py -v`
4. Verificar que pasa
5. Commit y push

### Actualizar tests después de cambios

1. Ejecutar todos los tests: `pytest tests/ -v`
2. Si fallan, verificar si es regresión o cambio esperado
3. Actualizar tests según sea necesario
4. Documentar cambios

## Recursos

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Contacto

Para preguntas o problemas, contactar al equipo de desarrollo.
