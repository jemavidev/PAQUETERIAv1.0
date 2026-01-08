# Optimizaciones de Rendimiento CRUD - Papyrus

**Fecha:** 2026-01-08  
**Versión:** 2.0.0

## Resumen de Cambios

### 1. Índices de Base de Datos
Se crearon índices optimizados para las tablas más consultadas:

```sql
-- Packages (tabla principal)
idx_packages_customer_id, idx_packages_status, idx_packages_created_at,
idx_packages_tracking_number, idx_packages_guide_number

-- Customers
idx_customers_phone, idx_customers_full_name, idx_customers_is_active

-- Messages, Notifications, Package History
Índices en foreign keys y campos de filtrado frecuente
```

**Archivo:** `scripts/database/create_performance_indexes.sql`

### 2. Cache Manager Optimizado
- TTLs ajustados para mejor balance rendimiento/frescura:
  - Lista de paquetes: 60s (antes 15s)
  - Detalle de paquete: 300s
  - Estadísticas: 300s
  - Dashboard: 60s

**Archivo:** `src/app/cache_manager.py`

### 3. Background Tasks para Notificaciones
Las notificaciones SMS y Email ahora se envían en background, sin bloquear las operaciones CRUD.

**Archivo:** `src/app/services/background_tasks_service.py`

### 4. Eager Loading Consistente
Se agregó eager loading en el servicio de paquetes para evitar N+1 queries:

```python
EAGER_LOAD_OPTIONS = [
    joinedload(Package.customer),
    selectinload(Package.file_uploads)
]
```

### 5. Pool de Conexiones Optimizado
- Producción: pool_size=15, max_overflow=10
- Staging: pool_size=5, max_overflow=3
- Pool recycle aumentado a 30 minutos en producción

## Cómo Aplicar

```bash
# En el servidor papyrus
ssh papyrus
cd /path/to/CODE
bash scripts/database/run_performance_optimizations.sh
docker-compose restart app
```

## Métricas Esperadas

| Operación | Antes | Después |
|-----------|-------|---------|
| Listar paquetes | ~500ms | ~100ms |
| Cambiar estado | ~800ms | ~200ms |
| Buscar clientes | ~300ms | ~80ms |

## Monitoreo

Verificar logs después de aplicar:
```bash
docker-compose logs -f app | grep -E "(Cache|HIT|MISS|BG)"
```
