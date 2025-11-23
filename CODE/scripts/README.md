# Scripts del Proyecto

Esta carpeta contiene scripts de utilidad organizados por categoría.

## 📁 Estructura

### `/maintenance` - Scripts de Mantenimiento
Scripts para tareas de mantenimiento del sistema:
- `cleanup_database.py` - Limpieza de base de datos
- `clear_cache.py` - Limpieza de caché
- `performance_monitor.py` - Monitor de rendimiento
- `fix_deliver_function.py` - Corrección de función de entrega
- `check_announcements.py` - Verificación de anuncios

### `/optimization` - Scripts de Optimización
Scripts para optimizar el rendimiento:
- `optimize_database.sql` - Optimización de base de datos
- `optimize_customers_query.sql` - Optimización de consultas de clientes
- `optimize_deliver.js` - Optimización de entregas

### `/testing` - Scripts de Testing
Scripts de prueba y testing (reservado para futuros tests)

## 🚀 Uso

Ejecuta los scripts desde el directorio raíz del proyecto:

```bash
# Ejemplo: Limpiar base de datos
python CODE/scripts/maintenance/cleanup_database.py

# Ejemplo: Ejecutar optimización SQL
psql -d database_name -f CODE/scripts/optimization/optimize_database.sql
```

## 📝 Notas

- Los scripts de mantenimiento deben ejecutarse con precaución en producción
- Los scripts de optimización SQL deben revisarse antes de aplicar
- Siempre hacer backup antes de ejecutar scripts de modificación
