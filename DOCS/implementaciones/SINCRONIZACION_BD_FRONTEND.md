# Sincronización de BD desde el Frontend

## Descripción

Implementación completa de un botón en el frontend (userDropdown) que permite a los administradores en el entorno de staging sincronizar la base de datos de producción con staging mediante una interfaz visual con logs en tiempo real.

## Archivos Creados/Modificados

### Backend

1. **`src/app/routes/admin_sync.py`** (NUEVO)
   - Endpoint `/api/admin/sync-database` (POST)
   - Endpoint `/api/admin/sync-database/status` (GET)
   - Streaming de logs en tiempo real usando Server-Sent Events (SSE)
   - Validaciones de seguridad (solo staging + admin)
   - Rate limiting (1 ejecución cada 5 minutos)

2. **`src/main.py`** (MODIFICADO)
   - Registro del router `admin_sync_router`

3. **`src/app/utils/auth_context.py`** (MODIFICADO)
   - Agregada variable `environment` al contexto de templates

### Frontend

4. **`src/templates/components/authenticated-navbar.html`** (MODIFICADO)
   - Botón "🔄 Sincronizar BD" en userDropdown
   - Solo visible para admin en staging

5. **`src/templates/components/sync-database-modal.html`** (NUEVO)
   - Modal interactivo con 3 estados:
     - Estado inicial (advertencias y confirmación)
     - Estado de progreso (logs en tiempo real)
     - Estado de finalización (éxito o error)

6. **`src/templates/base/base.html`** (MODIFICADO)
   - Inclusión del modal de sincronización

### Scripts

7. **`scripts/database/sync_production_to_staging.sh`** (YA EXISTÍA)
   - Script bash que ejecuta la sincronización
   - Modificado para soportar modo `--auto` (sin confirmación)

## Flujo de Funcionamiento

### 1. Usuario hace clic en "Sincronizar BD"

```
Usuario (Admin en Staging)
    ↓
Clic en botón del userDropdown
    ↓
Se abre modal con advertencias
```

### 2. Confirmación y Ejecución

```
Usuario confirma
    ↓
POST /api/admin/sync-database
    ↓
Backend valida:
  - ¿Es staging?
  - ¿Es admin?
  - ¿Pasó el cooldown?
    ↓
Ejecuta script bash con --auto
```

### 3. Streaming de Logs

```
Script bash ejecutándose
    ↓
Logs en tiempo real vía SSE
    ↓
Frontend recibe y muestra logs
    ↓
Barra de progreso se actualiza
```

### 4. Finalización

```
Script termina
    ↓
Frontend muestra resultado
    ↓
Usuario puede recargar página
```

## Seguridad

### Validaciones Implementadas

1. **Entorno**: Solo funciona en `ENVIRONMENT=staging`
2. **Rol**: Solo usuarios con `role=admin`
3. **Rate Limiting**: 1 ejecución cada 5 minutos
4. **Auditoría**: Logs de quién ejecutó la sincronización

### Datos Sanitizados

El script bash sanitiza automáticamente:
- Contraseñas de usuarios
- Tokens de API
- Tokens de sesión
- Tokens de recuperación

## Uso

### Desde el Frontend

1. Iniciar sesión como admin en staging
2. Hacer clic en el avatar de usuario (esquina superior derecha)
3. Seleccionar "🔄 Sincronizar BD"
4. Leer advertencias y confirmar
5. Esperar a que termine (ver logs en tiempo real)
6. Recargar página para ver datos actualizados

### Desde la Terminal (alternativa)

```bash
cd PAQUETERIAv1.0/scripts/database
./sync_production_to_staging.sh
```

## Endpoints API

### GET /api/admin/sync-database/status

Obtener estado de sincronización.

**Respuesta:**
```json
{
  "can_sync": true,
  "last_sync": "2026-02-26T15:30:00",
  "cooldown_remaining_minutes": 0,
  "environment": "staging"
}
```

### POST /api/admin/sync-database

Ejecutar sincronización con streaming de logs.

**Respuesta:** Server-Sent Events (SSE)
```
data: {"type": "info", "message": "Iniciando sincronización..."}
data: {"type": "success", "message": "✓ Dump completado"}
data: {"type": "warning", "message": "⚠ Datos sensibles sanitizados"}
data: {"type": "complete", "message": "done"}
```

## Tipos de Mensajes SSE

- `info`: Información general (color gris)
- `success`: Operación exitosa (color verde)
- `warning`: Advertencia (color amarillo)
- `error`: Error (color rojo)
- `complete`: Finalización (con valor "done" o "error")

## Interfaz de Usuario

### Modal - Estado Inicial

```
╔════════════════════════════════════════╗
║  🔄 Sincronizar Base de Datos          ║
╠════════════════════════════════════════╣
║                                        ║
║  ⚠️ ADVERTENCIA:                       ║
║  • La BD de staging será ELIMINADA    ║
║  • Se restaurarán datos de producción ║
║  • Las contraseñas serán sanitizadas  ║
║  • Puede tardar varios minutos        ║
║                                        ║
║  ℹ️ INFORMACIÓN:                       ║
║  • Solo disponible en staging         ║
║  • Verás logs en tiempo real          ║
║                                        ║
║  [Cancelar]  [Iniciar Sincronización] ║
╚════════════════════════════════════════╝
```

### Modal - En Progreso

```
╔════════════════════════════════════════╗
║  🔄 Sincronizar Base de Datos          ║
╠════════════════════════════════════════╣
║                                        ║
║  Sincronizando...              45%    ║
║  ████████████░░░░░░░░░░░░░░░░         ║
║                                        ║
║  ┌──────────────────────────────────┐ ║
║  │ ✓ Dump completado: 2.3MB         │ ║
║  │ ✓ Datos sensibles sanitizados    │ ║
║  │ ▶ Eliminando BD de staging...    │ ║
║  │                                  │ ║
║  └──────────────────────────────────┘ ║
║                                        ║
║  [Cerrar (en progreso...)]            ║
╚════════════════════════════════════════╝
```

### Modal - Completado

```
╔════════════════════════════════════════╗
║  🔄 Sincronizar Base de Datos          ║
╠════════════════════════════════════════╣
║                                        ║
║  ✅ Sincronización Completada          ║
║                                        ║
║  La base de datos se ha sincronizado  ║
║  exitosamente.                        ║
║                                        ║
║  Recarga la página para ver los datos ║
║  actualizados.                        ║
║                                        ║
║  [Cerrar]  [Recargar Página]          ║
╚════════════════════════════════════════╝
```

## Troubleshooting

### Error: "Esta funcionalidad solo está disponible en el entorno de staging"

**Causa:** Intentando ejecutar en producción o desarrollo.

**Solución:** Verificar que `ENVIRONMENT=staging` en el `.env`.

### Error: "Solo los administradores pueden ejecutar esta acción"

**Causa:** Usuario no tiene rol de admin.

**Solución:** Cambiar rol del usuario a `admin` en la BD.

### Error: "Debes esperar X minutos antes de ejecutar otra sincronización"

**Causa:** Rate limiting activo.

**Solución:** Esperar el tiempo indicado o reiniciar el servidor para resetear el contador.

### Error: "Script no encontrado"

**Causa:** El script bash no existe en la ruta esperada.

**Solución:** Verificar que existe `scripts/database/sync_production_to_staging.sh`.

### Logs no se muestran en tiempo real

**Causa:** Buffering de nginx o proxy.

**Solución:** El header `X-Accel-Buffering: no` ya está configurado. Verificar configuración de nginx.

## Dependencias

### Backend
- FastAPI
- asyncio (para subprocess asíncrono)
- subprocess (para ejecutar script bash)

### Frontend
- Fetch API (para SSE)
- Tailwind CSS (para estilos)
- Alpine.js (para interactividad del dropdown)

### Sistema
- PostgreSQL client (`pg_dump`, `psql`)
- SSH client
- Bash

## Configuración Requerida

### Variables de Entorno

```bash
# En staging
ENVIRONMENT=staging
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=staging
```

### Acceso SSH

```bash
# ~/.ssh/config
Host staging
    HostName staging.jemavi.co
    User ubuntu
    IdentityFile ~/.ssh/id_rsa

Host papyrus
    HostName papyrus.jemavi.co
    User ubuntu
    IdentityFile ~/.ssh/id_rsa
```

## Logs de Auditoría

Cada sincronización genera un log en el servidor:

```
[AUDIT] Sincronización BD iniciada por admin_user (admin@example.com)
```

## Mejoras Futuras

1. **Historial de Sincronizaciones**
   - Guardar en BD cada sincronización
   - Mostrar historial en el modal
   - Estadísticas de uso

2. **Sincronización Selectiva**
   - Opción de sincronizar solo ciertas tablas
   - Filtros por fecha
   - Sincronización incremental

3. **Notificaciones**
   - Email al completar sincronización
   - Notificación push en el navegador
   - Integración con Slack/Discord

4. **Programación**
   - Sincronización automática programada
   - Cron jobs configurables desde UI
   - Sincronización nocturna automática

5. **Comparación de Datos**
   - Diff entre producción y staging
   - Visualización de diferencias
   - Sincronización selectiva basada en diff

## Notas Importantes

⚠️ **IMPORTANTE**: Esta funcionalidad solo debe usarse en staging. Nunca en producción.

✅ **RECOMENDACIÓN**: Ejecutar sincronización en horarios de bajo tráfico.

📊 **TAMAÑO**: El proceso puede tardar de 2 a 10 minutos dependiendo del tamaño de la BD.

🔒 **SEGURIDAD**: Las contraseñas son sanitizadas automáticamente. Los usuarios no podrán iniciar sesión hasta que restablezcan sus contraseñas.

## Changelog

### v1.0.0 (2026-02-26)
- Implementación inicial
- Botón en userDropdown
- Modal interactivo con 3 estados
- Streaming de logs en tiempo real
- Validaciones de seguridad
- Rate limiting
- Sanitización de datos sensibles
