# Mantenimiento de Paquetes

## Descripción General

Este documento describe las funcionalidades de mantenimiento automático y manual para la gestión de paquetes en el sistema.

## 1. Limpieza Automática de Paquetes ANUNCIADOS

### Descripción
El sistema elimina automáticamente los paquetes con estado `ANUNCIADO` que no hayan cambiado de estado en **15 días**. Esta limpieza se ejecuta diariamente de forma automática mediante Celery Beat.

### Configuración

#### Tarea Programada
- **Nombre**: `cleanup-old-announced-packages`
- **Frecuencia**: Cada 24 horas
- **Días de antigüedad**: 15 días (configurable)
- **Cola**: `maintenance`

#### Archivo de Configuración
La tarea está configurada en `CODE/src/app/celery_app.py`:

```python
"cleanup-old-announced-packages": {
    "task": "src.tasks.cleanup_old_announced_packages",
    "schedule": 86400.0,  # Cada 24 horas
    "kwargs": {"days_old": 15},  # Eliminar paquetes ANUNCIADOS con más de 15 días
},
```

### Criterios de Eliminación
Un paquete será eliminado si cumple **TODAS** estas condiciones:
1. Estado actual: `ANUNCIADO`
2. Campo `updated_at` tiene más de 15 días de antigüedad
3. No ha cambiado a otro estado (RECIBIDO, ENTREGADO, CANCELADO)

### Logs
Los logs de la tarea se pueden encontrar en:
- Logs de Celery worker
- Logs de la aplicación principal

Ejemplo de log:
```
🧹 Iniciando limpieza de paquetes ANUNCIADOS con más de 15 días
🗑️ Eliminando paquete ANUNCIADO antiguo: TRK-12345 (última actualización: 2025-11-15)
✅ Limpieza completada: 3 paquetes ANUNCIADOS eliminados
```

## 2. Limpieza Manual de Paquetes ANUNCIADOS

### Script Manual
Para ejecutar la limpieza manualmente, usa el script:

```bash
cd CODE
python scripts/maintenance/cleanup_announced_packages.py
```

### Opciones del Script

#### Modo Dry Run (Prueba)
Ejecuta el script sin hacer cambios, solo muestra qué se eliminaría:

```bash
python scripts/maintenance/cleanup_announced_packages.py --dry-run
```

#### Cambiar Días de Antigüedad
Por defecto elimina paquetes con más de 15 días, pero puedes cambiar este valor:

```bash
# Eliminar paquetes con más de 30 días
python scripts/maintenance/cleanup_announced_packages.py --days 30

# Eliminar paquetes con más de 7 días
python scripts/maintenance/cleanup_announced_packages.py --days 7
```

#### Combinación de Opciones
```bash
# Dry run con 30 días
python scripts/maintenance/cleanup_announced_packages.py --dry-run --days 30
```

### Salida del Script
El script muestra:
1. Lista de paquetes a eliminar con detalles
2. Solicita confirmación antes de eliminar
3. Muestra resumen final con tracking numbers eliminados

Ejemplo:
```
================================================================================
🧹 LIMPIEZA DE PAQUETES ANUNCIADOS
================================================================================
Días de antigüedad: 15
Modo: PRODUCCIÓN (eliminará paquetes)
================================================================================

📅 Fecha límite: 2025-11-28 10:30:00
📦 Paquetes encontrados: 3

================================================================================
PAQUETES A ELIMINAR:
================================================================================
  • Tracking: TRK-12345 | Cliente: Juan Pérez | Última actualización: 2025-11-20 (23 días atrás)
  • Tracking: TRK-12346 | Cliente: María García | Última actualización: 2025-11-18 (25 días atrás)
  • Tracking: TRK-12347 | Cliente: N/A | Última actualización: 2025-11-15 (28 días atrás)
================================================================================

⚠️  ¿Deseas continuar con la eliminación? (s/n): s

🗑️  Eliminando paquete: TRK-12345
🗑️  Eliminando paquete: TRK-12346
🗑️  Eliminando paquete: TRK-12347

✅ Limpieza completada: 3 paquetes ANUNCIADOS eliminados

================================================================================
📊 RESUMEN
================================================================================
Paquetes eliminados: 3
Fecha límite: 2025-11-28T10:30:00
Días de antigüedad: 15
Estado: COMPLETADO
================================================================================

Tracking numbers eliminados:
  • TRK-12345
  • TRK-12346
  • TRK-12347
```

## 3. Ordenamiento de Paquetes

### Cambio Implementado
Los paquetes ahora se ordenan por **fecha de última actualización** (`updated_at`) en lugar de fecha de anuncio (`announced_at`).

### Orden
- **Más reciente primero** (descendente)
- Basado en el campo `updated_at` del modelo `Package`

### Archivos Modificados
1. `CODE/src/app/routes/packages.py` - Endpoint API de paquetes
2. `CODE/src/app/routes/protected.py` - Endpoint de vista protegida

### Comportamiento
Cuando un paquete cambia de estado (ANUNCIADO → RECIBIDO → ENTREGADO), el campo `updated_at` se actualiza automáticamente, haciendo que el paquete aparezca al inicio de la lista.

## 4. Verificación del Sistema

### Verificar Celery Beat
Para verificar que la tarea programada está activa:

```bash
# Ver tareas programadas
celery -A src.app.celery_app inspect scheduled

# Ver tareas activas
celery -A src.app.celery_app inspect active
```

### Verificar Logs de Celery
```bash
# Ver logs del worker
tail -f /var/log/celery/worker.log

# Ver logs de beat
tail -f /var/log/celery/beat.log
```

### Ejecutar Tarea Manualmente desde Celery
```python
from app.tasks import cleanup_old_announced_packages

# Ejecutar inmediatamente
result = cleanup_old_announced_packages.apply_async()

# Ejecutar con parámetros personalizados
result = cleanup_old_announced_packages.apply_async(kwargs={"days_old": 30})
```

## 5. Consideraciones Importantes

### Relaciones en Cascada
Al eliminar un paquete, se eliminan automáticamente (en cascada):
- Mensajes asociados
- Archivos subidos
- Notificaciones
- Historial del paquete
- Eventos del paquete

### Backup
Se recomienda tener backups regulares de la base de datos antes de ejecutar limpiezas masivas.

### Monitoreo
- Revisar logs regularmente para detectar problemas
- Monitorear el número de paquetes eliminados diariamente
- Alertar si el número de eliminaciones es inusualmente alto

## 6. Troubleshooting

### La tarea no se ejecuta automáticamente
1. Verificar que Celery Beat está corriendo:
   ```bash
   ps aux | grep celery
   ```

2. Verificar configuración en `celery_app.py`

3. Reiniciar Celery Beat:
   ```bash
   systemctl restart celery-beat
   ```

### Error al ejecutar el script manual
1. Verificar que estás en el directorio correcto
2. Verificar permisos de ejecución
3. Verificar conexión a la base de datos
4. Revisar logs para más detalles

### Paquetes no se eliminan
1. Verificar que el estado sea exactamente `ANUNCIADO`
2. Verificar que `updated_at` sea mayor a 15 días
3. Ejecutar en modo `--dry-run` para ver qué paquetes se detectan

## 7. Cambios Futuros

Si necesitas modificar el comportamiento:

### Cambiar días de antigüedad por defecto
Editar `CODE/src/app/celery_app.py`:
```python
"cleanup-old-announced-packages": {
    "task": "src.tasks.cleanup_old_announced_packages",
    "schedule": 86400.0,
    "kwargs": {"days_old": 30},  # Cambiar de 15 a 30 días
},
```

### Cambiar frecuencia de ejecución
```python
"cleanup-old-announced-packages": {
    "task": "src.tasks.cleanup_old_announced_packages",
    "schedule": 43200.0,  # Cada 12 horas en lugar de 24
    "kwargs": {"days_old": 15},
},
```

### Deshabilitar limpieza automática
Comentar o eliminar la entrada en `beat_schedule` en `celery_app.py`.

## 8. Contacto y Soporte

Para preguntas o problemas relacionados con el mantenimiento de paquetes, contactar al equipo de desarrollo.
