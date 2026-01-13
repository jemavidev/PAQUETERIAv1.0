# Guía de Uso - Sistema de Productos

## 📋 Descripción

Sistema completo de gestión de productos sincronizado con DynamiaERP. Permite visualizar, buscar, filtrar y configurar el catálogo de productos.

---

## 🚀 Inicio Rápido

### 1. Verificar que la migración esté aplicada

```bash
cd CODE
alembic current
```

Debe mostrar: `add_products_001 (head)`

### 2. Sincronizar productos desde DynamiaERP

**Opción A: Desde la interfaz web**
1. Acceder a `/products`
2. Click en botón "Sincronizar"
3. Confirmar la acción
4. Esperar a que complete (puede tomar varios minutos)

**Opción B: Desde línea de comandos**
```bash
cd CODE
python test_product_sync.py
```

### 3. Acceder a la interfaz

Navegar a: `http://localhost:8000/products`

---

## 🎯 Funcionalidades

### Tabla de Productos

- **Columnas configurables:** Cada usuario puede elegir qué columnas ver
- **Búsqueda:** Por código, nombre, descripción, código de barras
- **Filtros:**
  - Estado (Activo/Inactivo)
  - Vendible (Sí/No)
  - Destacado (Sí/No)
- **Paginación:** 50 productos por página (configurable)

### Configuración de Columnas

1. Click en "Configurar Columnas"
2. Marcar/desmarcar columnas para mostrar/ocultar
3. Usar flechas ↑↓ para reordenar
4. Click en "Guardar"

### Columnas Disponibles

1. Código Único
2. Referencia
3. Nombre
4. Línea
5. Tipo
6. Costo
7. Precio de Venta
8. Cantidad Inicial
9. Marca
10. Descripción
11. Stock Mínimo
12. Stock Máximo
13. Código de Barras

---

## 🔌 API REST

### Listar Productos

```http
GET /api/products?page=1&page_size=50&search=termo&activo=true
```

**Parámetros:**
- `page`: Número de página (default: 1)
- `page_size`: Tamaño de página (default: 50, max: 100)
- `search`: Término de búsqueda
- `activo`: true/false
- `vendible`: true/false
- `tipo_id`: ID del tipo
- `marca_id`: ID de la marca
- `linea_id`: ID de la línea
- `destacado`: true/false

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "codigo": "PROD001",
      "nombre": "Producto Ejemplo",
      "precio_venta": 10000,
      "existencias_totales": 100,
      ...
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 150,
    "total_pages": 3
  }
}
```

### Ver Detalle de Producto

```http
GET /api/products/{id}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "codigo": "PROD001",
    "nombre": "Producto Ejemplo",
    ...
  }
}
```

### Sincronizar Productos

```http
POST /api/products/sync?activo=true&vendible=true
```

**Requiere:** Rol de administrador

**Parámetros opcionales:**
- `activo`: Sincronizar solo productos activos
- `vendible`: Sincronizar solo productos vendibles
- `visualizable_web`: Sincronizar solo productos visualizables en web

**Respuesta:**
```json
{
  "success": true,
  "message": "Sincronización completada",
  "data": {
    "total": 500,
    "new": 50,
    "updated": 450,
    "errors": 0,
    "duration_seconds": 45.23
  }
}
```

### Búsqueda Avanzada

```http
GET /api/products/search/advanced?q=termo&limit=20
```

**Parámetros:**
- `q`: Término de búsqueda (mínimo 2 caracteres)
- `limit`: Límite de resultados (default: 20, max: 100)

**Respuesta:**
```json
{
  "success": true,
  "data": [...],
  "count": 15
}
```

### Historial de Sincronizaciones

```http
GET /api/products/sync/history?limit=10
```

**Requiere:** Rol de administrador

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "sync_date": "2026-01-13T10:30:00",
      "total_products": 500,
      "new_products": 50,
      "updated_products": 450,
      "errors": 0,
      "duration_seconds": 45.23,
      "status": "SUCCESS"
    }
  ],
  "count": 10
}
```

### Configuración de Columnas

**Obtener configuración:**
```http
GET /api/products/columns/config
```

**Guardar configuración:**
```http
POST /api/products/columns/config
Content-Type: application/json

[
  {
    "column_key": "codigo",
    "column_label": "Código Único",
    "visible": true,
    "order_index": 0
  },
  ...
]
```

---

## 🔧 Configuración

### Variables de Entorno Requeridas

```env
# DynamiaERP API
DYNAMIA_TOKEN=tu_token_aqui
DYNAMIA_API_URL=https://api.dynamiaerp.co
DYNAMIA_ACCOUNT_ID=128

# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

---

## 📊 Estructura de Datos

### Tabla `products`

Almacena todos los campos del producto desde DynamiaERP (60+ campos):

- **Información básica:** código, nombre, referencia, descripción
- **Precios:** precio_venta, costo_aproximado, costo_efectivo
- **Inventario:** existencias_totales, existencias_minimas, existencias_maximas
- **Clasificación:** tipo, marca, línea
- **Estados:** activo, vendible, comprable, destacado
- **Impuestos:** impuesto_incluido, porcentaje_impuesto
- **Y más...**

### Tabla `product_column_config`

Configuración de columnas por usuario:

- `user_id`: ID del usuario
- `column_key`: Clave de la columna
- `column_label`: Etiqueta visible
- `visible`: Si está visible o no
- `order_index`: Orden de visualización

### Tabla `product_sync_log`

Historial de sincronizaciones:

- `sync_date`: Fecha de sincronización
- `total_products`: Total procesados
- `new_products`: Nuevos creados
- `updated_products`: Actualizados
- `errors`: Cantidad de errores
- `duration_seconds`: Duración
- `status`: SUCCESS, PARTIAL_SUCCESS, ERROR

---

## 🐛 Solución de Problemas

### Error: "DATABASE_URL environment variable is required"

**Solución:** Verificar que el archivo `.env` existe y contiene `DATABASE_URL`

```bash
cd CODE
cat .env | grep DATABASE_URL
```

### Error: "Multiple head revisions"

**Solución:** Ejecutar todas las migraciones pendientes

```bash
cd CODE
alembic upgrade heads
```

### La sincronización es muy lenta

**Causas posibles:**
- Muchos productos en DynamiaERP
- Conexión lenta a la API
- Base de datos sin índices

**Solución:** La sincronización hace commit cada 100 productos para optimizar. Es normal que tome varios minutos con catálogos grandes.

### No aparecen productos después de sincronizar

**Verificar:**
1. Que la sincronización completó sin errores
2. Que los filtros no estén ocultando productos
3. Revisar el log de sincronización

```bash
cd CODE
python test_product_sync.py
```

---

## 📝 Notas Importantes

1. **Sincronización:** Solo usuarios administradores pueden sincronizar
2. **Configuración de columnas:** Es individual por usuario
3. **Búsqueda:** Usa índice de texto completo en PostgreSQL para mejor rendimiento
4. **Paginación:** Optimizada para catálogos grandes
5. **Datos:** Se sincronizan TODOS los campos de DynamiaERP (60+)

---

## 🔄 Mantenimiento

### Sincronización Programada

Para sincronizar automáticamente, crear un cron job:

```bash
# Sincronizar todos los días a las 2 AM
0 2 * * * cd /path/to/CODE && python test_product_sync.py >> /var/log/product_sync.log 2>&1
```

### Limpieza de Logs

Los logs de sincronización se acumulan. Limpiar periódicamente:

```sql
-- Mantener solo los últimos 30 días
DELETE FROM product_sync_log 
WHERE sync_date < NOW() - INTERVAL '30 days';
```

---

## 📚 Recursos Adicionales

- **Plan completo:** `PRODUCTOS_PLAN_IMPLEMENTACION.md`
- **Resumen rápido:** `PRODUCTOS_RESUMEN_RAPIDO.md`
- **Código fuente:**
  - Modelos: `src/app/models/product.py`
  - Servicio: `src/app/services/product_sync_service.py`
  - API: `src/app/routes/products.py`
  - Vista: `src/templates/products/list.html`

---

**Versión:** 1.0.0  
**Fecha:** 2026-01-13  
**Estado:** ✅ Operativo
