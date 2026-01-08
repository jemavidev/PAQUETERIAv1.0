# Especificación: Dashboard Administrativo Unificado V2

**Fecha:** 2025-01-24  
**Objetivo:** Replantear completamente el dashboard `/admin` para que TODO el contenido esté en una sola vista con tabs funcionales

## 🎯 PROBLEMA ACTUAL

1. Tab "Clientes" → Botones redirigen a `/announce` (incorrecto)
2. Tab "Settings" → Muestra vista separada en lugar de contenido integrado
3. Tabs "Usuarios", "Paquetes", "Mensajes" → Solo muestran vista rápida con botón "Ver Todos" que redirige
4. **NO HAY CONTENIDO REAL** dentro de cada tab, solo redireccionamientos

## ✅ SOLUCIÓN PROPUESTA

Crear un dashboard donde **CADA TAB** contenga el contenido completo de esa sección, SIN redireccionamientos.

### Tab 1: 📊 Dashboard (Estadísticas)
**Contenido:** Mantener las 37 estadísticas actuales organizadas en 6 secciones
- ✅ Ya funciona correctamente
- No requiere cambios

### Tab 2: 👥 Usuarios (Gestión Completa)
**Contenido:** Lista completa de usuarios con gestión integrada
- **Lista de usuarios** con paginación (tabla completa)
- **Búsqueda** en tiempo real
- **Botones de acción** por usuario:
  - ✏️ Editar (modal inline)
  - 🔒 Cambiar contraseña (modal inline)
  - 🔄 Activar/Desactivar
  - 🗑️ Eliminar
- **Botón "Crear Usuario"** (modal inline)
- **Filtros:** Por rol, estado activo/inactivo
- **Sin redirecciones** - Todo en la misma página

### Tab 3: 📦 Paquetes (Gestión Completa)
**Contenido:** Lista completa de paquetes con gestión integrada
- **Lista de paquetes** con paginación (tabla completa)
- **Búsqueda** por tracking, cliente, guía
- **Filtros:** Por estado, tipo, fecha
- **Botones de acción** por paquete:
  - 👁️ Ver detalle (modal inline)
  - ✏️ Editar estado
  - 📍 Ver ubicación
- **Estadísticas rápidas** en la parte superior
- **Sin redirecciones** - Todo en la misma página

### Tab 4: 🏢 Clientes (Gestión Completa)
**Contenido:** Lista completa de clientes con gestión integrada
- **Lista de clientes** con paginación (tabla completa)
- **Búsqueda** por nombre, teléfono, email
- **Botones de acción** por cliente:
  - ✏️ Editar (modal inline)
  - 👁️ Ver paquetes del cliente
  - 📊 Ver estadísticas del cliente
- **Botón "Crear Cliente"** (modal inline)
- **Estadísticas rápidas** en la parte superior
- **Sin redirecciones** - Todo en la misma página

### Tab 5: 💬 Mensajes (Gestión Completa)
**Contenido:** Lista completa de mensajes SMS con gestión integrada
- **Lista de mensajes** con paginación (tabla completa)
- **Búsqueda** por destinatario, contenido
- **Filtros:** Por estado (enviado, pendiente, fallido), fecha
- **Botón "Enviar Mensaje"** (modal inline)
- **Estadísticas de SMS** en la parte superior
- **Sin redirecciones** - Todo en la misma página

### Tab 6: ⚙️ Settings (Configuración Integrada)
**Contenido:** Configuración del sistema integrada
- **Sección 1: Configuración General**
  - Nombre del sistema
  - URL base
  - Zona horaria
  - Idioma
- **Sección 2: Tarifas**
  - Tarifa normal
  - Tarifa extra dimensionado
  - Tarifa almacenamiento
- **Sección 3: SMS**
  - Proveedor SMS
  - Credenciales
  - Plantillas de mensajes
- **Sección 4: Notificaciones**
  - Email SMTP
  - Configuración de alertas
- **Botón "Guardar Cambios"** al final
- **Sin redirecciones** - Todo en la misma página

## 🔧 IMPLEMENTACIÓN TÉCNICA

### Estructura del Template
```html
<div id="tab-dashboard-content" class="tab-content active">
    <!-- Estadísticas actuales (37 métricas) -->
</div>

<div id="tab-users-content" class="tab-content hidden">
    <!-- Tabla completa de usuarios + modales -->
</div>

<div id="tab-packages-content" class="tab-content hidden">
    <!-- Tabla completa de paquetes + modales -->
</div>

<div id="tab-customers-content" class="tab-content hidden">
    <!-- Tabla completa de clientes + modales -->
</div>

<div id="tab-messages-content" class="tab-content hidden">
    <!-- Tabla completa de mensajes + modales -->
</div>

<div id="tab-settings-content" class="tab-content hidden">
    <!-- Formulario de configuración -->
</div>
```

### JavaScript para Tabs
```javascript
function switchTab(tabName) {
    // Ocultar todos los contenidos
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
        content.classList.remove('active');
    });
    
    // Mostrar el contenido seleccionado
    document.getElementById(`tab-${tabName}-content`).classList.remove('hidden');
    document.getElementById(`tab-${tabName}-content`).classList.add('active');
    
    // Actualizar estilos de tabs
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.classList.remove('border-papyrus-blue', 'text-papyrus-blue');
        tab.classList.add('border-transparent', 'text-gray-500');
    });
    
    document.getElementById(`tab-${tabName}`).classList.add('border-papyrus-blue', 'text-papyrus-blue');
    document.getElementById(`tab-${tabName}`).classList.remove('border-transparent', 'text-gray-500');
    
    // Cargar datos si es necesario
    if (tabName === 'users') loadUsers();
    if (tabName === 'packages') loadPackages();
    if (tabName === 'customers') loadCustomers();
    if (tabName === 'messages') loadMessages();
}
```

### APIs Necesarias
1. **GET /api/admin/users** - Lista de usuarios con paginación
2. **POST /api/admin/users** - Crear usuario
3. **PUT /api/admin/users/{id}** - Actualizar usuario
4. **DELETE /api/admin/users/{id}** - Eliminar usuario
5. **GET /api/packages** - Lista de paquetes con paginación
6. **GET /api/customers** - Lista de clientes con paginación
7. **POST /api/customers** - Crear cliente
8. **PUT /api/customers/{id}** - Actualizar cliente
9. **GET /api/messages** - Lista de mensajes con paginación
10. **POST /api/messages** - Enviar mensaje

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Fase 1: Preparación
- [ ] Crear APIs faltantes para cada sección
- [ ] Verificar que todas las APIs devuelvan JSON correcto
- [ ] Crear modales reutilizables (crear, editar, eliminar)

### Fase 2: Tab Usuarios
- [ ] Tabla completa con paginación
- [ ] Búsqueda en tiempo real
- [ ] Modal crear usuario
- [ ] Modal editar usuario
- [ ] Modal cambiar contraseña
- [ ] Botones activar/desactivar
- [ ] Botón eliminar con confirmación

### Fase 3: Tab Paquetes
- [ ] Tabla completa con paginación
- [ ] Búsqueda y filtros
- [ ] Modal ver detalle
- [ ] Cambio de estado inline
- [ ] Estadísticas rápidas

### Fase 4: Tab Clientes
- [ ] Tabla completa con paginación
- [ ] Búsqueda en tiempo real
- [ ] Modal crear cliente
- [ ] Modal editar cliente
- [ ] Ver paquetes del cliente
- [ ] Estadísticas rápidas

### Fase 5: Tab Mensajes
- [ ] Tabla completa con paginación
- [ ] Búsqueda y filtros
- [ ] Modal enviar mensaje
- [ ] Estadísticas de SMS

### Fase 6: Tab Settings
- [ ] Formulario de configuración general
- [ ] Formulario de tarifas
- [ ] Formulario de SMS
- [ ] Formulario de notificaciones
- [ ] Guardar cambios

### Fase 7: Testing
- [ ] Probar cada tab individualmente
- [ ] Probar navegación entre tabs
- [ ] Probar todas las acciones (crear, editar, eliminar)
- [ ] Probar en móvil, tablet, desktop
- [ ] Verificar que NO haya redirecciones

## 🎨 DISEÑO

- **Colores:** Mantener paleta actual (papyrus-blue, papyrus-green)
- **Iconos:** Usar Heroicons (ya implementados)
- **Responsive:** Mobile-first con Tailwind CSS
- **Modales:** Usar Tailwind UI modales con backdrop
- **Tablas:** Diseño limpio con hover states
- **Paginación:** Botones anterior/siguiente + números de página

## ⚠️ REGLAS IMPORTANTES

1. **NUNCA usar `window.location.href`** dentro de los tabs
2. **NUNCA usar `<a href="/otra-ruta">`** dentro de los tabs
3. **TODO debe ser AJAX** con fetch() o XMLHttpRequest
4. **Los modales deben abrirse/cerrarse** sin recargar la página
5. **La paginación debe ser AJAX** sin recargar la página
6. **Los filtros deben ser AJAX** sin recargar la página
7. **SIEMPRE mostrar página HTML 403** cuando no hay permisos (NUNCA JSON)

## 📊 RESULTADO ESPERADO

Un dashboard donde el usuario puede:
1. Ver estadísticas generales (tab Dashboard)
2. Gestionar usuarios completos (tab Usuarios) - crear, editar, eliminar, buscar
3. Gestionar paquetes completos (tab Paquetes) - ver, filtrar, cambiar estado
4. Gestionar clientes completos (tab Clientes) - crear, editar, ver paquetes
5. Gestionar mensajes SMS (tab Mensajes) - ver historial, enviar nuevos
6. Configurar el sistema (tab Settings) - cambiar tarifas, SMS, notificaciones

**TODO en una sola página `/admin` sin redirecciones.**

## 🔒 MANEJO DE PERMISOS

Si un usuario sin permisos (no ADMIN ni OPERADOR) intenta acceder:
- ❌ **NO mostrar JSON** con error
- ✅ **SÍ mostrar página HTML 403** con diseño profesional
- La página 403 incluye:
  - Icono de candado animado
  - Mensaje claro: "Acceso Denegado"
  - Explicación de por qué no puede acceder
  - Botones para volver al dashboard o ir atrás
  - Enlaces de ayuda y contacto

**Template:** `CODE/src/templates/errors/403.html` (ya creado)

---

¿Apruebas esta especificación? Si estás de acuerdo, procedo a implementar el nuevo dashboard completo.
