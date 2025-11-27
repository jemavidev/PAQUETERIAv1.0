# Plan de Refactor: Sistema de Autenticación

## Objetivo

Rediseñar el sistema de autenticación para eliminar responsabilidades duplicadas y crear una arquitectura clara y mantenible.

## Problemas Actuales

### 1. Responsabilidades Mezcladas
- **Backend**: Middleware + rutas públicas manejan autenticación
- **Frontend**: `auth-redirect.js` verifica autenticación en TODAS las páginas
- **Templates**: `login.html` tiene lógica de verificación

### 2. Verificaciones Duplicadas
- Middleware verifica en cada request
- JavaScript verifica al cargar página
- Template verifica en el backend

### 3. Lógica Frágil
```javascript
// Code smell: excepciones hardcodeadas
if (isProtected && !isPublic && currentPath !== '/auth/login' && currentPath !== '/login') {
    checkAuthStatus();
}
```

### 4. Lista Hardcodeada de Rutas Públicas
- Definida en JavaScript
- Definida en Middleware
- Debe actualizarse en 2 lugares

## Arquitectura Propuesta

### Principio: Separación Clara de Responsabilidades

```
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Middleware: AuthMiddleware                           │  │
│  │ - Protege rutas según configuración                  │  │
│  │ - Redirige páginas HTML a /auth/login                │  │
│  │ - Retorna 401 JSON para APIs                         │  │
│  │ - NO maneja cookies inválidas (eso es del endpoint)  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Endpoint: /auth/login                                │  │
│  │ - Verifica si ya está autenticado → redirect         │  │
│  │ - Limpia cookies inválidas                           │  │
│  │ - Muestra mensaje de sesión expirada                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Endpoint: /api/config/public-routes                  │  │
│  │ - Retorna lista de rutas públicas                    │  │
│  │ - Fuente única de verdad                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ auth-redirect.js                                     │  │
│  │ - SOLO intercepta respuestas 401 de AJAX            │  │
│  │ - NO verifica autenticación al cargar página        │  │
│  │ - Muestra notificación y redirige                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Templates                                            │  │
│  │ - NO verifican autenticación                         │  │
│  │ - Confían en el backend                              │  │
│  │ - Solo UI y lógica de formulario                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Cambios Específicos

### 1. Middleware Simplificado

**Archivo**: `CODE/src/app/middleware/auth_middleware.py` (nuevo)

**Responsabilidades**:
- Verificar autenticación en rutas protegidas
- Redirigir páginas HTML a login
- Retornar 401 JSON para APIs
- Obtener rutas públicas de configuración centralizada

**NO hace**:
- Limpiar cookies (eso es del endpoint /auth/login)
- Verificar tokens expirados (eso es del servicio de auth)

### 2. Configuración Centralizada

**Archivo**: `CODE/src/app/config/routes.py` (nuevo)

```python
PUBLIC_ROUTES = {
    "/",
    "/announce",
    "/search",
    "/auth/login",
    "/auth/register",
    "/auth/forgot-password",
    "/auth/reset-password",
    "/help",
    "/cookies",
    "/terms",
    "/privacy",
    "/policies",
}

STATIC_ROUTES = {
    "/static/",
    "/uploads/",
}

API_PUBLIC_ROUTES = {
    "/api/auth/login",
    "/api/announcements/direct",
    "/api/search",
    "/api/config/public-routes",
    "/health",
    "/metrics",
}
```

### 3. Endpoint de Configuración

**Archivo**: `CODE/src/app/routes/config.py` (nuevo)

```python
@router.get("/api/config/public-routes")
async def get_public_routes():
    """Retorna lista de rutas públicas para el frontend"""
    return {
        "public_routes": list(PUBLIC_ROUTES),
        "api_public_routes": list(API_PUBLIC_ROUTES)
    }
```

### 4. JavaScript Simplificado

**Archivo**: `CODE/src/static/js/auth-redirect.js` (refactorizado)

**Responsabilidades**:
- SOLO interceptar respuestas 401 de fetch/XHR
- Mostrar notificación
- Redirigir a login

**NO hace**:
- Verificar autenticación al cargar página
- Mantener lista de rutas públicas
- Decidir si verificar o no según la ruta

### 5. Template Limpio

**Archivo**: `CODE/src/templates/auth/login.html` (simplificado)

**Responsabilidades**:
- Mostrar formulario
- Manejar submit
- Mostrar mensajes del backend

**NO hace**:
- Verificar si ya está autenticado (eso es del backend)
- Limpiar localStorage (innecesario con cookies httpOnly)

## Almacenamiento de Tokens

### Decisión: Cookies httpOnly

**Razones**:
1. Más seguro (no accesible desde JavaScript)
2. Enviado automáticamente en cada request
3. No necesita sincronización con localStorage

**Eliminar**:
- `localStorage.setItem('access_token', ...)`
- `localStorage.setItem('user_info', ...)`

## Flujos Esperados

### Flujo 1: Usuario No Autenticado Accede a Ruta Protegida

```
1. Usuario → GET /admin
2. Middleware verifica autenticación → NO autenticado
3. Middleware redirige → 302 /auth/login?redirect=/admin
4. Backend /auth/login verifica cookies → ninguna
5. Backend renderiza login.html
6. Usuario ve formulario de login
```

### Flujo 2: Usuario con Token Expirado Accede a Ruta Protegida

```
1. Usuario → GET /admin (con cookie access_token=expired)
2. Middleware verifica autenticación → Token inválido
3. Middleware redirige → 302 /auth/login?redirect=/admin
4. Backend /auth/login verifica cookies → token expirado
5. Backend limpia cookies inválidas
6. Backend renderiza login.html con mensaje "Sesión expirada"
7. Usuario ve formulario con mensaje
```

### Flujo 3: Usuario Autenticado Intenta Acceder a Login

```
1. Usuario → GET /auth/login (con cookie access_token=valid)
2. Backend /auth/login verifica autenticación → autenticado
3. Backend redirige → 302 /dashboard
4. Usuario ve dashboard
```

### Flujo 4: AJAX 401 en Página Protegida

```
1. Usuario en /admin hace fetch('/api/packages')
2. API retorna → 401 JSON {"detail": "Not authenticated"}
3. auth-redirect.js intercepta respuesta 401
4. JavaScript muestra notificación "Sesión expirada"
5. JavaScript redirige → /auth/login?redirect=/admin
6. Usuario ve formulario de login
```

## Migración

### Fase 1: Preparación (Sin Breaking Changes)
1. Crear nueva configuración centralizada
2. Crear nuevo middleware (sin activar)
3. Crear endpoint /api/config/public-routes
4. Agregar tests de comportamiento

### Fase 2: Refactor Backend
1. Reemplazar middleware antiguo por nuevo
2. Simplificar endpoint /auth/login
3. Eliminar lógica duplicada

### Fase 3: Refactor Frontend
1. Simplificar auth-redirect.js
2. Eliminar verificación de login.html
3. Eliminar uso de localStorage

### Fase 4: Limpieza
1. Eliminar archivos antiguos
2. Actualizar documentación
3. Verificar todos los tests

## Tests de Comportamiento

Ver: `DOCS/refactor/TESTS_COMPORTAMIENTO.md`

## Métricas de Éxito

- ✅ Reducción de código: -40% en auth-redirect.js
- ✅ Eliminación de lógica duplicada: 3 → 1 lugar
- ✅ Tests de comportamiento: 100% passing
- ✅ Sin regresiones: Todos los flujos funcionan
- ✅ Mantenibilidad: Nueva ruta pública = 1 cambio (config)

## Cronograma Estimado

- Fase 1: 2 horas
- Fase 2: 3 horas
- Fase 3: 2 horas
- Fase 4: 1 hora
- **Total**: 8 horas (1 día de desarrollo)

## Riesgos

1. **Regresión en flujos existentes**: Mitigado con tests de comportamiento
2. **Cambio en cookies**: Mitigado con migración gradual
3. **Usuarios con sesiones activas**: Mitigado con limpieza automática

## Próximos Pasos

1. Revisar y aprobar este plan
2. Crear tests de comportamiento (ver TESTS_COMPORTAMIENTO.md)
3. Ejecutar Fase 1
4. Validar con tests
5. Continuar con siguientes fases
