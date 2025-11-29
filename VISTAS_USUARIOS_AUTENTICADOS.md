# 🔐 VISTAS PARA USUARIOS AUTENTICADOS - PAQUETES EL CLUB

## 📋 RESUMEN EJECUTIVO

Este documento identifica todas las vistas y rutas que requieren autenticación en el sistema Paquetes El Club.

**Total de vistas autenticadas identificadas: 25+**

---

## 🎯 CATEGORÍAS DE VISTAS

### 1. 📊 ADMINISTRACIÓN (Admin/Operador)

#### `/admin` - Dashboard Administrativo
- **Template**: `admin/dashboard_enhanced.html`
- **Roles**: ADMIN, OPERADOR
- **Descripción**: Dashboard principal con estadísticas completas
- **Archivo**: `protected.py` y `views.py`

#### `/admin/users` - Gestión de Usuarios
- **Template**: `admin/users.html`
- **Roles**: ADMIN
- **Descripción**: Lista y gestión de usuarios del sistema con paginación
- **Archivo**: `protected.py` y `views.py`

#### `/customers-management` - Gestión de Clientes (Redirect)
- **Redirect**: `/admin`
- **Roles**: ADMIN, OPERADOR
- **Archivo**: `protected.py`

---

### 2. 👥 GESTIÓN DE CLIENTES

#### `/customers/manage` - Gestión de Clientes
- **Template**: `customers/manage.html`
- **Roles**: Todos los autenticados
- **Descripción**: Vista de gestión de clientes con paginación (10 por página) y búsqueda
- **Archivo**: `protected.py`

#### `/customers/create` - Crear Cliente
- **Template**: `customers/create.html`
- **Roles**: Todos los autenticados
- **Descripción**: Formulario para crear nuevo cliente
- **Archivo**: `protected.py`

#### `/customers/edit/{customer_id}` - Editar Cliente
- **Template**: `customers/edit.html`
- **Roles**: Todos los autenticados
- **Descripción**: Formulario para editar cliente existente
- **Archivo**: `protected.py`

---

### 3. 📦 GESTIÓN DE PAQUETES

#### `/packages` - Lista de Paquetes
- **Template**: `packages/packages.html`
- **Roles**: Todos los autenticados
- **Descripción**: Vista principal de gestión de paquetes con configuración de tarifas
- **Archivo**: `protected.py` y `views.py`

#### `/packages/{package_id}` - Detalle de Paquete
- **Template**: `packages/package_detail.html`
- **Roles**: Todos los autenticados
- **Descripción**: Vista detallada de un paquete específico
- **Archivo**: `protected.py` y `views.py`

#### `/receive` - Recibir Paquete
- **Template**: `receive/receive.html`
- **Roles**: Todos los autenticados
- **Descripción**: Formulario para recibir paquetes
- **Archivo**: `views.py`

---

### 4. 📢 ANUNCIOS

#### `/announcements/{announcement_id}` - Detalle de Anuncio
- **Template**: `announce/announcement_detail.html`
- **Roles**: Todos los autenticados
- **Descripción**: Vista detallada de un anuncio específico
- **Archivo**: `protected.py` y `views.py`

#### `/announcements/guide/{guide_number}` - Anuncio por Guía
- **Template**: `announce/announcement_detail.html`
- **Roles**: Todos los autenticados
- **Descripción**: Vista de anuncio buscado por número de guía con datos reales de BD
- **Archivo**: `protected.py` y `views.py`

---

### 5. 👤 PERFIL Y CONFIGURACIÓN

#### `/settings` - Configuración del Usuario
- **Template**: `users/settings.html` o `settings/settings.html`
- **Roles**: Todos los autenticados
- **Descripción**: Página de configuración unificada con preferencias, notificaciones, privacidad e interfaz
- **Archivo**: `protected.py` y `views.py`

#### `/profile` - Perfil del Usuario (Redirect)
- **Redirect**: `/settings?tab=account`
- **Roles**: Todos los autenticados
- **Descripción**: Redirige a la pestaña de cuenta en configuración
- **Archivo**: `views.py`

#### `/profile/edit` - Editar Perfil
- **Template**: `users/edit_profile_page.html`
- **Roles**: Todos los autenticados
- **Descripción**: Formulario de edición de perfil del usuario actual
- **Archivo**: `views.py` y `protected.py`

#### `/profile/change-password` - Cambiar Contraseña (Redirect)
- **Redirect**: `/settings?tab=security`
- **Roles**: Todos los autenticados
- **Descripción**: Redirige a la pestaña de seguridad en configuración
- **Archivo**: `views.py`

---

### 6. 📊 DASHBOARD

#### `/dashboard` - Dashboard del Usuario
- **Template**: `dashboard/dashboard_improved.html`
- **Roles**: USUARIO (redirige a `/admin` si es ADMIN/OPERADOR)
- **Descripción**: Dashboard mejorado para usuarios regulares
- **Archivo**: `views.py`

---

### 7. 🔄 OTRAS RUTAS AUTENTICADAS

#### `/logout` - Cerrar Sesión
- **Redirect**: `/auth/login`
- **Roles**: Todos los autenticados
- **Descripción**: Limpia cookies y redirige al login
- **Archivo**: `protected.py` y `views.py`

#### `/test-simple` - Prueba Simple
- **Response**: JSON
- **Roles**: Todos los autenticados
- **Descripción**: Ruta de prueba simple
- **Archivo**: `protected.py`

---

## 🔌 API ENDPOINTS AUTENTICADOS

### Gestión de Usuarios (Admin)

1. **GET** `/admin/users/search` - Búsqueda de usuarios
2. **POST** `/admin/users/create` - Crear usuario
3. **POST** `/admin/users/update` - Actualizar usuario
4. **POST** `/admin/users/delete` - Eliminar usuario
5. **POST** `/admin/users/toggle-status` - Activar/Desactivar usuario
6. **POST** `/admin/users/reset-password` - Restablecer contraseña

### Gestión de Perfil

7. **POST** `/profile/edit` - Procesar formulario de edición de perfil
8. **POST** `/profile/update` - Actualizar perfil (API JSON)
9. **POST** `/profile/api/change-password` - Cambiar contraseña

### Gestión de Paquetes

10. **POST** `/api/announcements/{announcement_id}/create-package` - Crear paquete desde anuncio
11. **GET** `/api/packages/{tracking_number}/history` - Historial de paquete
12. **GET** `/api/packages` - Obtener todos los paquetes
13. **GET** `/api/dashboard/packages` - Paquetes para dashboard con paginación

### Configuración

14. **POST** `/settings` - Guardar configuración del usuario

### Administración

15. **POST** `/admin/cleanup-database` - Limpiar base de datos (Solo ADMIN)

### Testing

16. **GET** `/test-profile-auth` - Verificar autenticación

---

## 🔐 MECANISMOS DE AUTENTICACIÓN

### Dependencias Utilizadas

1. **`get_current_active_user_from_cookies`**
   - Obtiene usuario desde cookies
   - Usado en la mayoría de vistas web
   - Retorna `User` o lanza `HTTPException 401`

2. **`get_current_admin_user_from_cookies`**
   - Verifica que el usuario sea ADMIN o OPERADOR
   - Usado en rutas administrativas
   - Retorna `User` o lanza `HTTPException 403`

3. **`get_auth_context_required`**
   - Obtiene contexto de autenticación
   - Verifica `is_authenticated`
   - Redirige a login si no está autenticado

4. **`get_auth_context_from_request`**
   - Obtiene contexto sin requerir autenticación
   - Usado en vistas que pueden ser públicas o privadas

---

## 📱 COMPONENTES MÓVILES AUTENTICADOS

### Footer Móvil Autenticado
- **Template**: `components/mobile-footer-authenticated.html`
- **Descripción**: Footer específico para usuarios autenticados en móvil
- **Características**:
  - Navegación rápida a secciones principales
  - Indicador de estado de autenticación
  - Acceso a perfil y configuración

### Navbar Autenticado
- **Template**: `components/authenticated-navbar.html`
- **Descripción**: Barra de navegación para usuarios autenticados
- **Características**:
  - Menú de usuario
  - Notificaciones
  - Acceso rápido a funciones principales

---

## 🎨 TEMPLATES BASE

### Base Template
- **Template**: `base/base.html`
- **Descripción**: Template base que incluye lógica de autenticación
- **Variables de contexto**:
  - `is_authenticated`: Boolean
  - `user`: Objeto User
  - `user_name`: Nombre del usuario
  - `user_role`: Rol del usuario

---

## 📊 ESTADÍSTICAS

### Por Categoría
- **Administración**: 3 vistas
- **Gestión de Clientes**: 3 vistas
- **Gestión de Paquetes**: 3 vistas
- **Anuncios**: 2 vistas
- **Perfil y Configuración**: 4 vistas
- **Dashboard**: 1 vista
- **Otras**: 2 vistas

### Por Rol
- **Todos los autenticados**: 15+ vistas
- **ADMIN**: 6+ vistas exclusivas
- **ADMIN/OPERADOR**: 3+ vistas compartidas

### APIs
- **Total de endpoints API**: 16+
- **Endpoints Admin**: 6
- **Endpoints Usuario**: 10

---

## 🔍 ARCHIVOS PRINCIPALES

1. **`CODE/src/app/routes/protected.py`** (991 líneas)
   - Rutas protegidas principales
   - Gestión de usuarios (admin)
   - Gestión de clientes
   - Gestión de perfil
   - APIs de paquetes

2. **`CODE/src/app/routes/views.py`** (500+ líneas)
   - Vistas generales
   - Dashboard
   - Configuración
   - Perfil

3. **`CODE/src/app/dependencies.py`**
   - Funciones de autenticación
   - Verificación de roles
   - Obtención de usuario desde cookies/token

4. **`CODE/src/app/utils/auth_context.py`** (probablemente)
   - Funciones de contexto de autenticación
   - `get_auth_context_from_request`
   - `get_auth_context_required`

---

## ✅ VERIFICACIÓN DE AUTENTICACIÓN

### Patrón Común en Vistas

```python
@router.get("/ruta")
async def vista(
    request: Request,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    context = get_auth_context_required(request)
    
    if not context["is_authenticated"]:
        return RedirectResponse(url="/auth/login?redirect=/ruta", status_code=302)
    
    # Lógica de la vista...
```

### Verificación de Roles

```python
# Solo ADMIN
if current_user.role.value != "ADMIN":
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado. Solo administradores."
    )

# ADMIN o OPERADOR
if current_user.role not in [UserRole.ADMIN, UserRole.OPERADOR]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acceso denegado. Se requieren permisos de administrador o operador"
    )
```

---

## 🚀 PRÓXIMOS PASOS RECOMENDADOS

1. **Auditoría de Seguridad**: Verificar que todas las rutas sensibles estén protegidas
2. **Documentación de APIs**: Crear documentación OpenAPI/Swagger para los endpoints
3. **Tests de Autenticación**: Crear tests automatizados para verificar la autenticación
4. **Optimización de Permisos**: Revisar y optimizar el sistema de roles y permisos
5. **Logging de Accesos**: Implementar logging de accesos a rutas protegidas

---

## 📝 NOTAS IMPORTANTES

- Todas las vistas autenticadas usan cookies para mantener la sesión
- El token JWT se almacena en la cookie `access_token`
- Las rutas administrativas tienen doble verificación: dependencia + verificación manual
- Algunas rutas tienen redirecciones automáticas según el rol del usuario
- El sistema soporta tanto autenticación por cookies (web) como por Bearer token (API)

---

**Documento generado**: 2024
**Sistema**: Paquetes El Club v3.1
**Autor**: Análisis automático del código fuente
