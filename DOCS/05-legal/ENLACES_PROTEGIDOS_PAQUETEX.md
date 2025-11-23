# 🔐 Enlaces Protegidos (Requieren Autenticación) - PAQUETEX

## 📋 Lista Completa de Rutas Protegidas

Esta es la lista completa de todos los enlaces, URLs y endpoints que requieren autenticación en PAQUETEX. Estas rutas solo son accesibles para usuarios autenticados.

---

## 🔑 REQUISITOS DE ACCESO

### Niveles de Autenticación

| Nivel | Descripción | Rutas |
|-------|-------------|-------|
| **Usuario Autenticado** | Cualquier usuario con sesión activa | Perfil, Configuración |
| **Operador** | Usuario con rol OPERADOR | Paquetes, Clientes, Recepción |
| **Administrador** | Usuario con rol ADMIN | Admin, Usuarios, Todas las anteriores |

---

## 🏠 DASHBOARD Y ADMINISTRACIÓN

### Panel de Administración

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/admin` | GET | ADMIN | Panel principal de administración |
| `/dashboard` | GET | ADMIN | Redirige a `/admin` |
| `/settings` | GET | Autenticado | Configuración del usuario |
| `/settings` | POST | Autenticado | Guardar configuración |

---

## 👤 GESTIÓN DE PERFIL

### Vistas de Perfil

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/profile` | GET | Autenticado | Ver perfil del usuario |
| `/profile/edit` | GET | Autenticado | Formulario de edición de perfil |
| `/profile/change-password` | GET | Autenticado | Formulario de cambio de contraseña |

### API de Perfil

| Endpoint | Método | Acceso | Descripción |
|----------|--------|--------|-------------|
| `/profile` | GET/HEAD | Autenticado | Obtener información del perfil |
| `/profile/edit` | POST | Autenticado | Actualizar perfil (formulario) |
| `/profile/update` | POST | Autenticado | Actualizar perfil (JSON) |
| `/profile/api/change-password` | POST | Autenticado | Cambiar contraseña |

---

## 👥 GESTIÓN DE USUARIOS (ADMIN)

### Vistas de Usuarios

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/admin/users` | GET | ADMIN | Lista de usuarios con paginación |

### API de Usuarios

| Endpoint | Método | Acceso | Descripción |
|----------|--------|--------|-------------|
| `/admin/users/search` | GET | ADMIN | Buscar usuarios |
| `/api/admin/users/search` | GET | ADMIN | Buscar usuarios (API) |
| `/admin/users/create` | POST | ADMIN | Crear nuevo usuario |
| `/admin/users/update` | POST | ADMIN | Actualizar usuario |
| `/admin/users/delete` | POST | ADMIN | Eliminar usuario |
| `/admin/users/toggle-status` | POST | ADMIN | Activar/Desactivar usuario |
| `/admin/users/reset-password` | POST | ADMIN | Restablecer contraseña |

---

## 📦 GESTIÓN DE PAQUETES

### Vistas de Paquetes

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/packages` | GET | Autenticado | Lista de paquetes |
| `/packages/{package_id}` | GET | Autenticado | Detalle de paquete |
| `/receive` | GET | Autenticado | Formulario de recepción |

### API de Paquetes

| Endpoint | Método | Acceso | Descripción |
|----------|--------|--------|-------------|
| `/api/packages` | GET | Autenticado | Obtener todos los paquetes |
| `/api/packages/{tracking_number}/history` | GET | Autenticado | Historial del paquete |
| `/api/dashboard/packages` | GET | Autenticado | Paquetes para dashboard |
| `/api/announcements/{announcement_id}/create-package` | POST | Autenticado | Crear paquete desde anuncio |

---

## 📢 GESTIÓN DE ANUNCIOS

### Vistas de Anuncios

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/announcements/{announcement_id}` | GET | Autenticado | Detalle de anuncio |
| `/announcements/guide/{guide_number}` | GET | Autenticado | Detalle por número de guía |

---

## 👨‍👩‍👧‍👦 GESTIÓN DE CLIENTES

### Vistas de Clientes

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/customers/manage` | GET | Autenticado | Lista de clientes (10 por página) |
| `/customers/create` | GET | Autenticado | Formulario crear cliente |
| `/customers/edit/{customer_id}` | GET | Autenticado | Formulario editar cliente |
| `/customers-management` | GET | Autenticado | Redirige a `/admin` |

### Parámetros de Paginación

```
/customers/manage?page=1&limit=10&search=nombre
```

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| page | int | 1 | Número de página |
| limit | int | 10 | Clientes por página |
| search | string | "" | Término de búsqueda |

---

## 📊 EVENTOS DE PAQUETES

### API de Eventos

| Endpoint | Método | Acceso | Descripción |
|----------|--------|--------|-------------|
| `/api/package-events/package/{package_id}` | GET | Autenticado | Historial por paquete |
| `/api/package-events/tracking/{tracking_number}` | GET | Autenticado | Eventos por tracking |
| `/api/package-events/guide/{guide_number}` | GET | Autenticado | Eventos por guía |
| `/api/package-events/code/{tracking_code}` | GET | Autenticado | Eventos por código |
| `/api/package-events/customer/phone/{phone}` | GET | Autenticado | Eventos por teléfono |
| `/api/package-events/operator/{operator_id}` | GET | Autenticado | Eventos por operador |
| `/api/package-events/filter` | POST | Autenticado | Filtrar eventos |
| `/api/package-events/search` | GET | Autenticado | Buscar eventos |
| `/api/package-events/recent` | GET | Autenticado | Eventos recientes |
| `/api/package-events/statistics` | GET | Autenticado | Estadísticas de eventos |
| `/api/package-events/deliveries` | GET | Autenticado | Eventos de entregas |
| `/api/package-events/operator/{operator_id}/summary` | GET | Autenticado | Resumen de operador |
| `/api/package-events/{event_id}` | GET | Autenticado | Evento por ID |

---

## 🔧 DEBUG Y DESARROLLO

### Vistas de Debug

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/debug-standalone` | GET | Público | Dashboard de debug |
| `/test-simple` | GET | Autenticado | Test simple |
| `/api/test-profile-auth` | GET | Autenticado | Test de autenticación |

### API de Debug

| Endpoint | Método | Acceso | Descripción |
|----------|--------|--------|-------------|
| `/debug-standalone/api/system-metrics` | GET | Público | Métricas del sistema |
| `/debug-standalone/api/services-status` | GET | Público | Estado de servicios |
| `/debug-standalone/api/database-info` | GET | Público | Info de base de datos |
| `/debug-standalone/api/api-info` | GET | Público | Info de API |

---

## 🔐 AUTENTICACIÓN Y SESIÓN

### Rutas de Autenticación

| Ruta | Método | Acceso | Descripción |
|------|--------|--------|-------------|
| `/logout` | GET | Autenticado | Cerrar sesión |

### Cookies de Sesión

| Cookie | Descripción | Duración |
|--------|-------------|----------|
| `access_token` | Token de acceso | 24 horas |
| `user_id` | ID del usuario | 24 horas |
| `user_name` | Nombre del usuario | 24 horas |
| `user_role` | Rol del usuario | 24 horas |

---

## 📱 NAVEGACIÓN DEL HEADER (Autenticado)

### Enlaces Visibles para Usuarios Autenticados

| Enlace | URL | Descripción | Rol Requerido |
|--------|-----|-------------|---------------|
| Logo | `/announce` | Volver a inicio | Todos |
| Paquetes | `/packages` | Gestión de paquetes | Todos |
| Mensajes | `/messages` | Sistema de mensajes | Todos |
| Clientes | `/customers/manage` | Gestión de clientes | Todos |
| Consulta | `/search` | Búsqueda de paquetes | Todos |

### Dropdown de Usuario

| Enlace | URL | Descripción |
|--------|-----|-------------|
| Perfil | `/profile` | Ver perfil |
| Cerrar Sesión | `/logout` | Salir del sistema |

---

## 📊 CONFIGURACIÓN DE USUARIO

### Preferencias Disponibles

#### Notificaciones
- Email notifications
- Push notifications
- SMS notifications
- Notificar paquete recibido
- Notificar paquete entregado
- Notificar mensajes

#### Privacidad
- Perfil público
- Compartir datos de actividad

#### Interfaz
- Tema (light/dark)
- Idioma (es/en)
- Items por página (10/20/50/100)

#### Dashboard
- Mostrar estadísticas
- Mostrar actividad reciente
- Mostrar gráficos

---

## 🔄 FLUJO DE TRABAJO DE PAQUETES

### Estados de Paquetes

```
ANUNCIADO → RECIBIDO → EN_ALMACEN → ENTREGADO
                    ↓
                CANCELADO
```

### Transiciones Permitidas

| Estado Actual | Estados Permitidos |
|---------------|-------------------|
| ANUNCIADO | RECIBIDO, CANCELADO |
| RECIBIDO | EN_ALMACEN, ENTREGADO, CANCELADO |
| EN_ALMACEN | ENTREGADO, CANCELADO |
| ENTREGADO | (Final) |
| CANCELADO | (Final) |

---

## 📋 ROLES Y PERMISOS

### Matriz de Permisos

| Funcionalidad | USUARIO | OPERADOR | ADMIN |
|---------------|---------|----------|-------|
| Ver perfil propio | ✅ | ✅ | ✅ |
| Editar perfil propio | ✅ | ✅ | ✅ |
| Cambiar contraseña propia | ✅ | ✅ | ✅ |
| Ver paquetes | ✅ | ✅ | ✅ |
| Crear paquetes | ❌ | ✅ | ✅ |
| Editar paquetes | ❌ | ✅ | ✅ |
| Ver clientes | ✅ | ✅ | ✅ |
| Crear clientes | ❌ | ✅ | ✅ |
| Editar clientes | ❌ | ✅ | ✅ |
| Ver usuarios | ❌ | ❌ | ✅ |
| Crear usuarios | ❌ | ❌ | ✅ |
| Editar usuarios | ❌ | ❌ | ✅ |
| Eliminar usuarios | ❌ | ❌ | ✅ |
| Restablecer contraseñas | ❌ | ❌ | ✅ |
| Ver estadísticas | ✅ | ✅ | ✅ |
| Acceder a admin | ❌ | ❌ | ✅ |

---

## 🗺️ MAPA DE NAVEGACIÓN (Autenticado)

```
Usuario Autenticado
│
├── Header
│   ├── Logo → /announce
│   ├── Paquetes → /packages
│   ├── Mensajes → /messages
│   ├── Clientes → /customers/manage
│   ├── Consulta → /search
│   └── Dropdown Usuario
│       ├── Perfil → /profile
│       └── Cerrar Sesión → /logout
│
├── /profile (Perfil)
│   ├── Ver información
│   ├── Editar → /profile/edit
│   └── Cambiar contraseña → /profile/change-password
│
├── /settings (Configuración)
│   ├── Notificaciones
│   ├── Privacidad
│   ├── Interfaz
│   └── Dashboard
│
├── /packages (Paquetes)
│   ├── Lista de paquetes
│   ├── Detalle → /packages/{id}
│   └── Recibir → /receive
│
├── /customers/manage (Clientes)
│   ├── Lista de clientes (paginada)
│   ├── Crear → /customers/create
│   └── Editar → /customers/edit/{id}
│
└── /admin (Solo ADMIN)
    ├── Dashboard
    ├── Usuarios → /admin/users
    │   ├── Lista (paginada)
    │   ├── Buscar
    │   ├── Crear
    │   ├── Editar
    │   ├── Eliminar
    │   └── Restablecer contraseña
    └── Estadísticas
```

---

## 📊 PAGINACIÓN

### Rutas con Paginación

| Ruta | Items por Página | Parámetros |
|------|------------------|------------|
| `/admin/users` | 20 | `?page=1&limit=20` |
| `/customers/manage` | 10 | `?page=1&limit=10&search=` |
| `/api/dashboard/packages` | 8 | `?page=1&limit=8&search=` |

### Estructura de Respuesta de Paginación

```json
{
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🔍 BÚSQUEDA Y FILTROS

### Endpoints de Búsqueda

| Endpoint | Parámetro | Descripción |
|----------|-----------|-------------|
| `/admin/users/search` | `q` | Buscar usuarios |
| `/customers/manage` | `search` | Buscar clientes |
| `/api/package-events/search` | `q` | Buscar eventos |

### Campos de Búsqueda

**Usuarios:**
- Username
- Email
- Teléfono
- Nombre completo
- Rol
- Estado (activo/inactivo)

**Clientes:**
- Nombre
- Teléfono
- Email
- Dirección

**Paquetes:**
- Tracking number
- Guide number
- Access code
- Nombre del cliente

---

## 📈 ESTADÍSTICAS Y REPORTES

### Endpoints de Estadísticas

| Endpoint | Descripción | Parámetros |
|----------|-------------|------------|
| `/api/package-events/statistics` | Estadísticas generales | `date_from`, `date_to` |
| `/api/package-events/deliveries` | Entregas por período | `date_from`, `date_to` |
| `/api/package-events/operator/{id}/summary` | Resumen de operador | `date_from`, `date_to` |

---

## 🔒 SEGURIDAD

### Validaciones de Seguridad

1. **No auto-eliminación**: Un usuario no puede eliminarse a sí mismo
2. **No auto-desactivación**: Un usuario no puede desactivarse a sí mismo
3. **Protección de último admin**: No se puede degradar al último administrador
4. **Verificación de contraseña**: Se requiere contraseña actual para cambiarla
5. **Unicidad de username/email**: No se permiten duplicados

### Headers de Seguridad

Todas las rutas protegidas verifican:
- Cookie `access_token` válida
- Usuario activo (`is_active = true`)
- Rol apropiado para la ruta

---

## 📝 FORMATOS DE DATOS

### Usuario

```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "phone": "string",
  "role": "ADMIN|OPERADOR|USUARIO",
  "is_active": boolean,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### Paquete

```json
{
  "id": "uuid",
  "tracking_number": "string",
  "guide_number": "string",
  "access_code": "string",
  "customer_name": "string",
  "customer_phone": "string",
  "status": "ANUNCIADO|RECIBIDO|EN_ALMACEN|ENTREGADO|CANCELADO",
  "package_type": "normal|extra_dimensioned",
  "package_condition": "ok|damaged|opened",
  "announced_at": "ISO8601",
  "received_at": "ISO8601",
  "delivered_at": "ISO8601"
}
```

### Cliente

```json
{
  "id": "uuid",
  "first_name": "string",
  "last_name": "string",
  "full_name": "string",
  "phone": "string",
  "email": "string",
  "address": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

---

## 🌍 URLS DE PRODUCCIÓN

### Dominio Principal

```
https://paquetex.papyrus.com.co
```

### Rutas Protegidas Principales

| Ruta | URL Completa |
|------|--------------|
| Admin | `https://paquetex.papyrus.com.co/admin` |
| Perfil | `https://paquetex.papyrus.com.co/profile` |
| Paquetes | `https://paquetex.papyrus.com.co/packages` |
| Clientes | `https://paquetex.papyrus.com.co/customers/manage` |
| Configuración | `https://paquetex.papyrus.com.co/settings` |

---

## 📊 RESUMEN ESTADÍSTICO

### Total de Rutas por Categoría

| Categoría | Cantidad |
|-----------|----------|
| Vistas de Perfil | 3 |
| API de Perfil | 4 |
| Vistas de Admin | 1 |
| API de Usuarios | 7 |
| Vistas de Paquetes | 3 |
| API de Paquetes | 4 |
| Vistas de Anuncios | 2 |
| Vistas de Clientes | 4 |
| API de Eventos | 13 |
| Debug | 7 |
| **TOTAL** | **48+** |

### Rutas por Nivel de Acceso

| Nivel | Cantidad |
|-------|----------|
| Cualquier Autenticado | ~30 |
| Solo ADMIN | ~15 |
| Debug/Dev | ~7 |

---

## ✅ VERIFICACIÓN DE ACCESO

### Checklist de Pruebas

#### Sin Autenticación
- [ ] Intentar acceder a `/admin` → Redirige a `/auth/login`
- [ ] Intentar acceder a `/profile` → Redirige a `/auth/login`
- [ ] Intentar acceder a `/packages` → Redirige a `/auth/login`
- [ ] Intentar acceder a `/customers/manage` → Redirige a `/auth/login`

#### Con Autenticación (Usuario)
- [ ] Acceder a `/profile` → ✅ Permitido
- [ ] Acceder a `/settings` → ✅ Permitido
- [ ] Acceder a `/packages` → ✅ Permitido
- [ ] Acceder a `/admin` → ❌ Acceso denegado

#### Con Autenticación (Admin)
- [ ] Acceder a `/admin` → ✅ Permitido
- [ ] Acceder a `/admin/users` → ✅ Permitido
- [ ] Crear usuarios → ✅ Permitido
- [ ] Eliminar usuarios → ✅ Permitido

---

## 📝 NOTAS IMPORTANTES

### Redirecciones

- `/dashboard` → `/admin`
- `/customers-management` → `/admin`
- Rutas sin autenticación → `/auth/login?redirect={ruta_original}`

### Parámetros de Redirección

Después del login, el usuario es redirigido a:
```
/auth/login?redirect=/packages
```

Tras autenticarse exitosamente, va a `/packages`

### Cookies de Sesión

Duración: **24 horas**

Al cerrar sesión (`/logout`), se eliminan todas las cookies y se redirige a `/auth/login`

---

**Fecha de Generación**: 2025-01-XX  
**Versión**: 4.0  
**Estado**: ✅ Completo y Actualizado  
**Tipo**: Rutas Protegidas (Requieren Autenticación)
