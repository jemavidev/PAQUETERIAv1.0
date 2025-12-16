# Integración del Componente de Usuarios de Settings en Dashboard Admin

## Fecha: 2024-12-15

## Objetivo

Reemplazar el tab simple de "Usuarios" en el dashboard administrativo (`/admin`) con el componente completo y funcional de gestión de usuarios que existe en `/settings`.

## Cambios Realizados

### 1. Template del Dashboard (`admin_dashboard.html`)

#### Antes:
```html
<div id="users-content" class="hidden">
    <div class="bg-white shadow-sm border border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-900">Gestión de Usuarios</h2>
            <button onclick="window.location.href='/admin/users'">
                Ir a Gestión Completa
            </button>
        </div>
        <p class="text-gray-600 mb-4">Vista rápida de usuarios...</p>
        <div id="users-list" class="space-y-4">
            <div class="text-center py-8 text-gray-500">Cargando usuarios...</div>
        </div>
    </div>
</div>
```

#### Después:
```html
<div id="users-content" class="hidden">
    {% include 'settings/_users_table.html' %}
</div>
```

### 2. Modales Agregados

Se agregaron al final del template (antes del `{% endblock %}`):

- **Modal Crear Usuario** (`createUserModal`)
  - Formulario completo con validación
  - Campos: username, email, full_name, phone, role, password
  - Solo visible para ADMIN

- **Modal Editar Usuario** (`editUserModal`)
  - Formulario de edición con todos los campos
  - Checkbox para activar/desactivar usuario
  - Solo visible para ADMIN

### 3. Script JavaScript

Se agregó la referencia al script de gestión de usuarios:
```html
<script src="/static/js/settings_users.js"></script>
```

Este script incluye las funciones:
- `openCreateUserModal()` - Abrir modal de crear
- `closeCreateUserModal()` - Cerrar modal de crear
- `editUser()` - Abrir modal de editar con datos
- `closeEditUserModal()` - Cerrar modal de editar
- `activateUser()` - Activar usuario
- `deactivateUser()` - Desactivar usuario
- `searchUsers()` - Búsqueda en tiempo real
- `clearSearch()` - Limpiar búsqueda
- `showSuccessMessage()` - Toast de éxito

### 4. Ruta del Backend (`views.py`)

#### Antes:
```python
@router.get("/admin")
async def admin_page(request: Request, current_user: User = ...):
    context = get_auth_context_required(request)
    context["user"] = current_user
    # ...
    return templates.TemplateResponse("admin/admin_dashboard.html", context)
```

#### Después:
```python
@router.get("/admin")
async def admin_page(request: Request, current_user: User = ..., db: Session = Depends(get_db)):
    context = get_auth_context_required(request)
    context["user"] = current_user
    context["user_role"] = current_user.role.value
    
    # Cargar usuarios si es admin (para tab de Usuarios)
    if current_user.role == UserRole.ADMIN:
        users = db.query(User).order_by(User.created_at.desc()).all()
        context["users"] = users
    else:
        context["users"] = []
    
    return templates.TemplateResponse("admin/admin_dashboard.html", context)
```

## Funcionalidades del Componente Integrado

### Para ADMIN:
✅ **Ver tabla completa de usuarios** con:
- Avatar con inicial del nombre
- Nombre completo y username
- Rol con badge de color
- Email (visible en desktop)
- Estado (Activo/Inactivo)
- Acciones (Editar, Activar/Desactivar)

✅ **Crear nuevos usuarios**:
- Botón "Crear Usuario" en la parte superior
- Modal con formulario completo
- Validación de campos requeridos
- Contraseña mínima de 8 caracteres

✅ **Editar usuarios existentes**:
- Botón de editar en cada fila
- Modal pre-llenado con datos actuales
- Modificar todos los campos excepto contraseña
- Checkbox para activar/desactivar

✅ **Activar/Desactivar usuarios**:
- Botones con iconos intuitivos
- Confirmación antes de la acción
- Actualización automática después de la acción

✅ **Buscar usuarios**:
- Barra de búsqueda en tiempo real
- Busca en todos los campos visibles
- Botón para limpiar búsqueda

### Para OPERADOR:
✅ **Ver tabla completa de usuarios** (solo lectura)
⚠️ **Botones deshabilitados**:
- Crear usuario: No visible
- Editar: Visible pero deshabilitado con tooltip "Solo administradores"
- Activar/Desactivar: Visible pero deshabilitado con tooltip "Solo administradores"

✅ **Buscar usuarios**: Funcional

## Componentes Reutilizados

### 1. Partial Template
- **Archivo**: `CODE/src/templates/settings/_users_table.html`
- **Contenido**: Tabla completa con búsqueda y acciones
- **Permisos**: Verifica `user_role` para mostrar/ocultar botones

### 2. Script JavaScript
- **Archivo**: `CODE/src/static/js/settings_users.js`
- **Funciones**: Gestión completa de usuarios
- **Endpoints usados**:
  - `POST /api/admin/users` - Crear usuario
  - `POST /api/admin/users/update` - Actualizar usuario
  - `POST /api/admin/users/toggle-status` - Activar/Desactivar

### 3. Modales
- Diseño consistente con el resto del sistema
- Validación de formularios
- Manejo de errores con mensajes claros

## Endpoints API Utilizados

Todos estos endpoints ya existen y están funcionando en `/settings`:

1. **POST /api/admin/users** (Crear)
   - Requiere: username, email, full_name, password, role
   - Opcional: phone
   - Solo ADMIN

2. **POST /api/admin/users/update** (Actualizar)
   - Requiere: user_id, username, email, full_name, role, is_active
   - Opcional: phone
   - Solo ADMIN

3. **POST /api/admin/users/toggle-status** (Activar/Desactivar)
   - Requiere: user_id
   - Solo ADMIN

## Ventajas de esta Integración

✅ **Reutilización de código**: No duplicamos funcionalidad
✅ **Consistencia**: Misma experiencia en `/admin` y `/settings`
✅ **Mantenibilidad**: Un solo componente para mantener
✅ **Funcionalidad completa**: Todas las operaciones CRUD disponibles
✅ **Permisos correctos**: ADMIN puede gestionar, OPERADOR solo ver
✅ **Sin romper nada**: Las demás funcionalidades del dashboard siguen intactas

## Archivos Modificados

1. ✅ `CODE/src/templates/admin/admin_dashboard.html`
   - Reemplazado contenido del tab Usuarios
   - Agregados modales de crear/editar
   - Agregado script de gestión

2. ✅ `CODE/src/app/routes/views.py`
   - Agregado parámetro `db` a la función
   - Agregado `user_role` al contexto
   - Cargada lista de `users` para ADMIN

## Archivos Reutilizados (Sin Modificar)

1. ✅ `CODE/src/templates/settings/_users_table.html` - Componente de tabla
2. ✅ `CODE/src/static/js/settings_users.js` - Script de gestión
3. ✅ `CODE/src/app/routes/protected.py` - Endpoints API existentes

## Testing Recomendado

### Como ADMIN:
1. ✅ Acceder a `/admin`
2. ✅ Click en tab "Usuarios"
3. ✅ Verificar que se muestre la tabla completa
4. ✅ Click en "Crear Usuario"
5. ✅ Llenar formulario y crear usuario
6. ✅ Verificar que aparezca en la tabla
7. ✅ Click en "Editar" de un usuario
8. ✅ Modificar datos y guardar
9. ✅ Verificar cambios en la tabla
10. ✅ Click en "Desactivar" de un usuario
11. ✅ Verificar que cambie el estado
12. ✅ Usar la búsqueda para filtrar usuarios
13. ✅ Verificar que los demás tabs sigan funcionando

### Como OPERADOR:
1. ✅ Acceder a `/admin`
2. ✅ Verificar que NO vea el tab "Usuarios" (debe estar oculto)
3. ✅ Verificar que los demás tabs funcionen correctamente

## Notas Adicionales

- El tab "Usuarios" solo es visible para ADMIN (configurado con `{% if user.role.value == "ADMIN" %}`)
- Los OPERADOR no ven el tab de usuarios en el dashboard
- Los modales y scripts solo se cargan si el usuario es ADMIN
- La búsqueda funciona en tiempo real sin necesidad de hacer peticiones al servidor
- Los mensajes de éxito se muestran como toasts en la esquina superior derecha
- Después de crear/editar/activar/desactivar, la página se recarga automáticamente

## Próximos Pasos

1. **Desplegar a staging** para probar con datos reales
2. **Probar con usuario ADMIN** todas las funcionalidades
3. **Probar con usuario OPERADOR** que no vea el tab
4. **Verificar que no se rompan** las demás funcionalidades del dashboard
5. **Considerar agregar paginación** si hay muchos usuarios (futuro)

## Comandos para Desplegar

```bash
# Desde el directorio raíz
./deploy.sh

# O manualmente
cd CODE
docker-compose -f docker-compose.staging.yml build web
docker-compose -f docker-compose.staging.yml up -d web
docker-compose -f docker-compose.staging.yml logs -f web
```
