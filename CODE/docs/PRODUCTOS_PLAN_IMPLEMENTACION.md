# Plan de Implementación - Sistema de Productos PAQUETEX

## 📋 Resumen del Proyecto

Implementar un sistema completo de gestión de productos sincronizados desde DynamiaERP con las siguientes características:

- ✅ Almacenar TODOS los campos de productos (60+ campos)
- ✅ Vista de tabla interactiva con columnas configurables
- ✅ Drag & drop para reordenar columnas
- ✅ Búsqueda y filtrado eficiente
- ✅ Paginación optimizada
- ✅ Preparado para edición in-place (futuro)
- ✅ Edición por lotes (futuro)
- ✅ Look & feel consistente con PAQUETEX

## 🎯 Columnas por Defecto a Mostrar

1. Código Único (codigo)
2. Referencia (referencia)
3. Nombre (nombre)
4. Línea (linea_nombre)
5. Tipo (tipo_nombre)
6. Costo (costo_aproximado)
7. Precio de Venta (precio_venta)
8. Cantidad Inicial (existencias_totales)
9. Marca (marca_nombre)
10. Descripción (descripcion)
11. Stock Mínimo (existencias_minimas)
12. Stock Máximo (existencias_maximas)
13. Código de Barras (codigo_barra)

---

## 📊 Estado de Implementación

### ✅ FASE 1: Base de Datos y Modelos (COMPLETADO)

#### Tarea 1.1: Migración de Base de Datos ✅
**Archivo:** `CODE/alembic/versions/add_products_table.py`

**Completado:**
- ✅ Tabla `products` con 60+ campos
- ✅ Tabla `product_column_config` para configuración de columnas por usuario
- ✅ Tabla `product_sync_log` para historial de sincronizaciones
- ✅ Índices optimizados para búsqueda y filtrado
- ✅ Índice de texto completo (full-text search) en español
- ✅ Campos JSONB para datos flexibles

**Campos incluidos:**
- Información básica (8 campos)
- Precios y costos (8 campos)
- Impuestos (4 campos)
- Inventario (4 campos)
- Clasificación (9 campos)
- Estados (7 campos)
- Configuración de ventas (7 campos)
- Domicilios (4 campos)
- Comisiones (4 campos)
- Configuraciones avanzadas (11 campos)
- Gestión (7 campos)
- Auditoría (14 campos)

#### Tarea 1.2: Modelos SQLAlchemy ✅
**Archivo:** `CODE/src/app/models/product.py`

**Completado:**
- ✅ Modelo `Product` con todos los campos
- ✅ Modelo `ProductColumnConfig` para configuración de columnas
- ✅ Modelo `ProductSyncLog` para logs
- ✅ Método `to_dict()` para serialización
- ✅ Índices y relaciones

#### Tarea 1.3: Servicio de Sincronización ✅
**Archivo:** `CODE/src/app/services/product_sync_service.py`

**Completado:**
- ✅ Clase `ProductSyncService`
- ✅ Método `fetch_all_products_from_dynamia()`
- ✅ Método `map_dynamia_to_local()` con mapeo completo
- ✅ Método `sync_products()` con manejo de errores
- ✅ Logging de sincronizaciones
- ✅ Manejo de transacciones por lotes
- ✅ Filtros opcionales (activo, vendible, etc.)

---

### ⏳ FASE 2: API Endpoints (PENDIENTE)

#### Tarea 2.1: Endpoints de Productos ⬜
**Archivo a crear:** `CODE/src/app/routes/products.py`

**Por implementar:**
```python
# Endpoints necesarios:
GET    /api/products                    # Listar productos con filtros y paginación
GET    /api/products/{id}               # Obtener producto por ID
POST   /api/products/sync               # Sincronizar desde DynamiaERP
GET    /api/products/search             # Búsqueda avanzada
GET    /api/products/filters            # Obtener opciones de filtros
GET    /api/products/export             # Exportar a Excel/CSV
POST   /api/products/batch-update       # Actualización por lotes (futuro)
```

**Características requeridas:**
- Paginación eficiente (limit/offset)
- Filtros múltiples (categoría, marca, precio, stock, etc.)
- Búsqueda de texto completo
- Ordenamiento por cualquier columna
- Respuesta optimizada (solo campos necesarios)

#### Tarea 2.2: Endpoints de Configuración de Columnas ⬜
**Archivo a crear:** `CODE/src/app/routes/product_columns.py`

**Por implementar:**
```python
GET    /api/products/columns/config     # Obtener configuración de columnas del usuario
POST   /api/products/columns/config     # Guardar configuración de columnas
PUT    /api/products/columns/reorder    # Reordenar columnas
POST   /api/products/columns/reset      # Resetear a configuración por defecto
```

#### Tarea 2.3: Endpoints de Sincronización ⬜
**Archivo a crear:** `CODE/src/app/routes/product_sync.py`

**Por implementar:**
```python
GET    /api/products/sync/status        # Estado de última sincronización
GET    /api/products/sync/history       # Historial de sincronizaciones
POST   /api/products/sync/start         # Iniciar sincronización
GET    /api/products/sync/progress      # Progreso de sincronización en curso
```

---

### ⏳ FASE 3: Frontend - Vistas HTML (PENDIENTE)

#### Tarea 3.1: Vista Principal de Productos ⬜
**Archivo a crear:** `CODE/src/app/templates/products/list.html`

**Componentes necesarios:**
- Header con título y botón de sincronización
- Barra de búsqueda global
- Filtros laterales o superiores
- Tabla de productos con columnas configurables
- Paginación
- Indicadores de estado (sincronizando, errores, etc.)

#### Tarea 3.2: Componente de Tabla Interactiva ⬜
**Archivo a crear:** `CODE/src/app/static/js/products-table.js`

**Funcionalidades:**
- Renderizado eficiente de tabla
- Drag & drop de columnas
- Resize de columnas
- Ordenamiento por columna (click en header)
- Selección de filas (para edición por lotes)
- Scroll virtual para grandes datasets
- Edición in-place (preparado para futuro)

#### Tarea 3.3: Componente de Configuración de Columnas ⬜
**Archivo a crear:** `CODE/src/app/static/js/column-config.js`

**Funcionalidades:**
- Modal/panel de configuración
- Lista de columnas disponibles
- Checkbox para mostrar/ocultar
- Drag & drop para reordenar
- Botón "Resetear a default"
- Guardar configuración automáticamente

#### Tarea 3.4: Componente de Búsqueda y Filtros ⬜
**Archivo a crear:** `CODE/src/app/static/js/products-filters.js`

**Funcionalidades:**
- Búsqueda de texto con debounce
- Filtros por categoría/línea
- Filtros por marca
- Filtros por rango de precio
- Filtros por stock (disponible, bajo, agotado)
- Filtros por estado (activo, inactivo)
- Aplicar/limpiar filtros
- Indicador de filtros activos

---

### ⏳ FASE 4: Estilos CSS (PENDIENTE)

#### Tarea 4.1: Estilos de Tabla de Productos ⬜
**Archivo a crear:** `CODE/src/app/static/css/products.css`

**Estilos necesarios:**
- Tabla responsive
- Headers con indicadores de ordenamiento
- Filas con hover effect
- Columnas redimensionables
- Indicadores de drag & drop
- Estados visuales (activo, inactivo, destacado)
- Badges para categorías y marcas

#### Tarea 4.2: Estilos de Filtros y Búsqueda ⬜
**Estilos necesarios:**
- Barra de búsqueda moderna
- Panel de filtros colapsable
- Chips para filtros activos
- Botones de acción
- Indicadores de carga

#### Tarea 4.3: Estilos de Modal de Configuración ⬜
**Estilos necesarios:**
- Modal overlay
- Lista de columnas con drag handles
- Checkboxes personalizados
- Botones de acción

---

### ⏳ FASE 5: Funcionalidades Avanzadas (FUTURO)

#### Tarea 5.1: Edición In-Place ⬜
**Descripción:**
- Click en celda para editar
- Validación en tiempo real
- Guardar automáticamente o con confirmación
- Indicador de cambios no guardados
- Deshacer cambios

#### Tarea 5.2: Edición por Lotes ⬜
**Descripción:**
- Selección múltiple de productos
- Panel de edición masiva
- Campos editables en lote
- Preview de cambios
- Confirmación antes de aplicar
- Progreso de actualización

#### Tarea 5.3: Sincronización Bidireccional ⬜
**Descripción:**
- Detectar cambios locales
- Enviar cambios a DynamiaERP
- Resolver conflictos
- Sincronización automática programada

#### Tarea 5.4: Exportación Avanzada ⬜
**Descripción:**
- Exportar a Excel con formato
- Exportar a CSV
- Exportar a PDF
- Seleccionar columnas a exportar
- Aplicar filtros actuales

---

## 🔧 Tareas Técnicas Adicionales

### Tarea T.1: Ejecutar Migración de Base de Datos ⬜
```bash
cd CODE
alembic upgrade head
```

### Tarea T.2: Actualizar requirements.txt ⬜
Agregar dependencias necesarias:
- openpyxl (para Excel)
- pandas (para manipulación de datos)
- celery (para tareas asíncronas - opcional)

### Tarea T.3: Configurar Variables de Entorno ⬜
Ya configuradas en `.env`:
- ✅ DYNAMIA_TOKEN
- ✅ DYNAMIA_API_URL
- ✅ DYNAMIA_ACCOUNT_ID

### Tarea T.4: Crear Comando de Sincronización ⬜
**Archivo a crear:** `CODE/scripts/sync_products.py`
Script CLI para sincronizar productos manualmente

### Tarea T.5: Agregar Ruta en main.py ⬜
Registrar routers de productos en la aplicación principal

---

## 📝 Archivos Creados

### ✅ Completados:
1. `CODE/alembic/versions/add_products_table.py` - Migración de BD
2. `CODE/src/app/models/product.py` - Modelos SQLAlchemy
3. `CODE/src/app/services/product_sync_service.py` - Servicio de sincronización
4. `CODE/docs/PRODUCTOS_PLAN_IMPLEMENTACION.md` - Este documento

### ⬜ Por Crear:
5. `CODE/src/app/routes/products.py` - Endpoints de productos
6. `CODE/src/app/routes/product_columns.py` - Endpoints de columnas
7. `CODE/src/app/routes/product_sync.py` - Endpoints de sincronización
8. `CODE/src/app/templates/products/list.html` - Vista principal
9. `CODE/src/app/static/js/products-table.js` - Tabla interactiva
10. `CODE/src/app/static/js/column-config.js` - Configuración de columnas
11. `CODE/src/app/static/js/products-filters.js` - Búsqueda y filtros
12. `CODE/src/app/static/css/products.css` - Estilos
13. `CODE/scripts/sync_products.py` - Script CLI

---

## 🎨 Especificaciones de Diseño

### Look & Feel
- Seguir el diseño actual de PAQUETEX
- Colores: Azul primario (#3B82F6), grises para texto
- Tipografía: Sistema actual de PAQUETEX
- Espaciado: Consistente con el resto de la app
- Iconos: Font Awesome o similar

### Tabla de Productos
- Headers fijos al hacer scroll
- Filas alternadas para mejor legibilidad
- Hover effect en filas
- Indicadores visuales de estado
- Responsive (colapsar columnas en móvil)

### Interacciones
- Drag & drop suave con feedback visual
- Transiciones CSS para cambios de estado
- Loading spinners durante operaciones
- Toasts para notificaciones
- Confirmaciones para acciones destructivas

---

## 🚀 Orden de Implementación Sugerido

### Sprint 1 (Actual)
1. ✅ Migración de BD
2. ✅ Modelos
3. ✅ Servicio de sincronización
4. ⬜ Ejecutar migración
5. ⬜ Endpoints básicos de productos

### Sprint 2
6. ⬜ Endpoints de columnas
7. ⬜ Vista HTML básica
8. ⬜ Tabla simple sin drag & drop
9. ⬜ Búsqueda básica

### Sprint 3
10. ⬜ Drag & drop de columnas
11. ⬜ Configuración de columnas
12. ⬜ Filtros avanzados
13. ⬜ Paginación optimizada

### Sprint 4
14. ⬜ Estilos finales
15. ⬜ Optimizaciones de performance
16. ⬜ Testing
17. ⬜ Documentación de usuario

### Sprint 5 (Futuro)
18. ⬜ Edición in-place
19. ⬜ Edición por lotes
20. ⬜ Sincronización bidireccional

---

## 📊 Métricas de Éxito

- ✅ Todos los campos de DynamiaERP almacenados
- ⬜ Sincronización completa en < 30 segundos (1827 productos)
- ⬜ Búsqueda con resultados en < 500ms
- ⬜ Tabla renderiza 50 productos en < 200ms
- ⬜ Drag & drop fluido (60fps)
- ⬜ Configuración de columnas persiste correctamente
- ⬜ Responsive en móviles y tablets

---

## 🔄 Próximos Pasos Inmediatos

1. **Ejecutar migración de BD:**
   ```bash
   cd CODE
   alembic upgrade head
   ```

2. **Probar sincronización:**
   ```python
   from app.services.product_sync_service import ProductSyncService
   from app.database import SessionLocal
   
   db = SessionLocal()
   service = ProductSyncService(db)
   result = service.sync_products()
   print(result)
   ```

3. **Crear endpoints de API** (Tarea 2.1)

4. **Crear vista HTML básica** (Tarea 3.1)

---

## 📞 Notas y Consideraciones

### Performance
- Usar paginación del lado del servidor
- Implementar caché para filtros frecuentes
- Índices de BD ya optimizados
- Considerar virtualización de tabla para > 1000 filas

### Seguridad
- Validar permisos de usuario
- Sanitizar inputs de búsqueda
- Rate limiting en sincronización
- Logs de auditoría para cambios

### Escalabilidad
- Preparado para millones de productos
- Sincronización incremental (futuro)
- Caché de Redis (opcional)
- CDN para assets estáticos

---

**Última actualización:** 2026-01-13  
**Estado general:** 25% completado (Fase 1 completa)  
**Próxima tarea:** Ejecutar migración y crear endpoints de API
