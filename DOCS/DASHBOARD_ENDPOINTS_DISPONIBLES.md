# 📊 Dashboard Mejorado - Endpoints y Funcionalidades

## 🎯 Resumen de Mejoras

Se ha mejorado el dashboard administrativo de PAQUETEX con las siguientes características:

### ✨ Nuevas Funcionalidades

1. **Vista por Tabs**: Organización en 4 secciones principales
   - Vista General
   - Usuarios
   - Paquetes
   - Métricas de Negocio
   - Sistema

2. **Health Check en Tiempo Real**: Monitoreo del estado del sistema

3. **Auto-refresh**: Actualización automática cada 5 minutos

4. **Enlaces Directos a APIs**: Acceso rápido a todos los endpoints

---

## 🔌 Endpoints API Disponibles

### 1. Dashboard Principal

**Endpoint:** `GET /api/admin/dashboard`

**Parámetros:**
- `period_days` (opcional): Número de días para el período (default: 30, min: 1, max: 365)

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "system_overview": {
      "total_users": 0,
      "active_users": 0,
      "total_packages": 0,
      "total_customers": 0,
      "total_messages": 0,
      "total_notifications": 0,
      "total_reports": 0
    },
    "user_management": {
      "users_by_role": {
        "ADMIN": 0,
        "operator": 0,
        "user": 0
      },
      "users_by_status": {
        "active": 0,
        "inactive": 0
      },
      "recent_users": 0
    },
    "business_metrics": {
      "packages_by_status": {},
      "new_customers": 0,
      "messages_by_status": {},
      "total_sms_sent": 0,
      "total_sms_cost_cop": 0,
      "reports_generated": 0
    },
    "system_health": {
      "failed_reports": 0,
      "inactive_users": 0,
      "unprocessed_packages": 0,
      "pending_messages": 0,
      "system_status": "healthy"
    },
    "recent_activity": []
  },
  "generated_at": "2025-11-21T10:00:00",
  "generated_by": "admin"
}
```

**Uso:**
```bash
curl -X GET "http://localhost:8000/api/admin/dashboard?period_days=30" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --cookie "access_token=YOUR_TOKEN"
```

---

### 2. Health Check del Sistema

**Endpoint:** `GET /api/admin/system/health`

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T10:00:00",
  "checks": {
    "database": "ok",
    "users": "ok",
    "packages": "ok",
    "messages": "ok",
    "notifications": "ok",
    "reports": "ok"
  },
  "metrics": {
    "failed_reports": 0,
    "inactive_users": 0,
    "unprocessed_packages": 0,
    "pending_messages": 0
  }
}
```

**Estados posibles:**
- `healthy`: Todo funcionando correctamente
- `warning`: Advertencias detectadas
- `error`: Errores críticos

---

### 3. Información del Sistema

**Endpoint:** `GET /api/admin/system/info`

**Respuesta:**
```json
{
  "success": true,
  "system_info": {
    "version": "3.1.0",
    "environment": "production",
    "database": "connected",
    "uptime": "5 days",
    "memory_usage": "512 MB"
  }
}
```

---

### 4. Gestión de Usuarios

#### Listar Usuarios

**Endpoint:** `GET /api/admin/users`

**Parámetros:**
- `skip` (opcional): Offset para paginación (default: 0)
- `limit` (opcional): Límite de resultados (default: 50, max: 100)
- `role` (opcional): Filtrar por rol (ADMIN, OPERADOR, USUARIO)
- `is_active` (opcional): Filtrar por estado (true/false)
- `search` (opcional): Buscar por username, email o nombre

**Respuesta:**
```json
{
  "users": [
    {
      "id": "1",
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Administrador",
      "phone": "+573001234567",
      "role": "ADMIN",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00",
      "last_login": "2025-11-21T10:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

#### Crear Usuario

**Endpoint:** `POST /api/admin/users`

**Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@example.com",
  "full_name": "Nuevo Usuario",
  "password": "password123",
  "role": "USUARIO",
  "phone": "+573001234567",
  "is_active": true
}
```

#### Actualizar Usuario

**Endpoint:** `PUT /api/admin/users/{user_id}`

#### Activar/Desactivar Usuario

**Endpoint:** `POST /api/admin/users/{user_id}/toggle-status`

#### Resetear Contraseña

**Endpoint:** `POST /api/admin/users/{user_id}/reset-password`

**Body:**
```json
{
  "new_password": "nueva_password123"
}
```

#### Eliminar Usuario

**Endpoint:** `DELETE /api/admin/users/{user_id}`

---

### 5. Configuración del Sistema

#### Obtener Configuración

**Endpoint:** `GET /api/admin/config`

#### Actualizar Configuración

**Endpoint:** `PUT /api/admin/config`

---

### 6. Auditoría y Logs

**Endpoint:** `GET /api/admin/audit/logs`

**Parámetros:**
- `skip` (opcional): Offset para paginación
- `limit` (opcional): Límite de resultados
- `action` (opcional): Filtrar por tipo de acción
- `user` (opcional): Filtrar por usuario

**Respuesta:**
```json
{
  "logs": [
    {
      "id": "1",
      "action": "USER_CREATED",
      "user": "admin",
      "timestamp": "2025-11-21T10:00:00",
      "details": "Usuario creado: nuevo_usuario"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 50
}
```

---

### 7. Estadísticas Detalladas

**Endpoint:** `GET /api/admin/stats/detailed`

**Parámetros:**
- `period_days` (opcional): Número de días (default: 30)

**Respuesta:**
```json
{
  "success": true,
  "detailed_stats": {
    "...": "Incluye todos los datos del dashboard",
    "performance_indicators": {
      "user_growth_rate": 0,
      "package_processing_efficiency": 0,
      "customer_satisfaction_score": 0,
      "system_uptime_percentage": 99.9
    },
    "resource_usage": {
      "database_connections": "normal",
      "cache_hit_rate": 95.5,
      "api_response_time_avg": 245,
      "error_rate": 0.1
    }
  }
}
```

---

### 8. Limpieza de Datos

**Endpoint:** `POST /api/admin/cleanup`

**Parámetros:**
- `days_old` (opcional): Días de antigüedad (default: 90, min: 30, max: 365)
- `dry_run` (opcional): Simulación sin eliminar (default: true)

**Respuesta:**
```json
{
  "success": true,
  "message": "Limpieza simulada exitosamente",
  "result": {
    "old_packages": 10,
    "old_messages": 50,
    "old_notifications": 100
  },
  "dry_run": true
}
```

---

## 🎨 Estructura del Dashboard Mejorado

### Tab 1: Vista General
- **Métricas Principales**: Usuarios, Paquetes, Clientes, Mensajes
- **Métricas SMS**: SMS enviados, costos, notificaciones
- **Actividad Reciente**: Últimas acciones en el sistema

### Tab 2: Usuarios
- **Usuarios por Rol**: Distribución de administradores, operadores y usuarios
- **Estado de Usuarios**: Activos vs inactivos
- **Acciones Rápidas**: Crear usuario, ver inactivos, lista completa

### Tab 3: Paquetes
- **Paquetes por Estado**: Anunciados, Recibidos, Entregados, etc.
- **Enlaces Rápidos**: Acceso directo a filtros por estado

### Tab 4: Métricas de Negocio
- **Clientes Nuevos**: En el período seleccionado
- **Reportes Generados**: Total de reportes
- **Mensajes por Estado**: Distribución de mensajes

### Tab 5: Sistema
- **Health Check**: Estado de todos los componentes
- **Métricas de Salud**: Reportes fallidos, usuarios inactivos, paquetes sin procesar
- **Enlaces de Administración**: Acceso directo a todos los endpoints API

---

## 🔗 Enlaces Rápidos en el Dashboard

El dashboard incluye enlaces directos a:

1. **Health Check**: `/api/admin/system/health`
2. **Info del Sistema**: `/api/admin/system/info`
3. **Configuración**: `/api/admin/config`
4. **Logs de Auditoría**: `/api/admin/audit/logs`
5. **Estadísticas Detalladas**: `/api/admin/stats/detailed`
6. **Dashboard API**: `/api/admin/dashboard?period_days=30`

---

## 🚀 Cómo Usar el Nuevo Dashboard

### 1. Acceso

Navega a: `http://localhost:8000/admin`

**Requisitos:**
- Usuario autenticado
- Rol: ADMIN o OPERADOR

### 2. Navegación

- Usa los **tabs** en la parte superior para cambiar entre secciones
- El **badge de estado** muestra el health del sistema en tiempo real
- Botón de **refresh** para actualizar datos manualmente
- **Auto-refresh** cada 5 minutos

### 3. Interacción

- Haz clic en las **tarjetas** para ver más detalles
- Usa los **enlaces rápidos** para acceder a funcionalidades específicas
- Los **enlaces API** abren los endpoints en una nueva pestaña

---

## 📝 Notas Importantes

### Permisos

- **ADMIN**: Acceso completo a todas las funcionalidades
- **OPERADOR**: Acceso a dashboard y estadísticas (sin gestión de usuarios)
- **USUARIO**: Sin acceso al dashboard administrativo

### Seguridad

- Todos los endpoints requieren autenticación
- Los endpoints de administración verifican el rol del usuario
- Las cookies de sesión se validan en cada petición

### Rendimiento

- El dashboard carga datos de forma asíncrona
- Auto-refresh configurable (default: 5 minutos)
- Caché de datos para mejorar velocidad

---

## 🐛 Troubleshooting

### El dashboard no carga datos

1. Verifica que estés autenticado
2. Comprueba que tu rol sea ADMIN o OPERADOR
3. Revisa la consola del navegador para errores
4. Verifica que el backend esté funcionando: `/api/admin/system/health`

### Health check muestra "error"

1. Verifica la conexión a la base de datos
2. Revisa los logs del servidor
3. Comprueba que todos los servicios estén activos

### No puedo acceder a ciertos endpoints

1. Verifica tu rol de usuario
2. Comprueba que tengas los permisos necesarios
3. Revisa que el token de autenticación sea válido

---

## 📞 Soporte

Para más información o soporte, contacta al equipo de desarrollo.
