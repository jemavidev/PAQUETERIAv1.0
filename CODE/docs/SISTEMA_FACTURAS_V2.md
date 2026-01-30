# Sistema de Facturas V2

Sistema completo de gestión de facturas electrónicas con 3 tabs: FACTURAS, CUFE y PRODUCTOS.

## 📋 Descripción General

Este sistema permite gestionar facturas de proveedores y archivos DIAN de forma estructurada, con extracción automática de datos y seguimiento de productos.

### Flujo de Trabajo

```
1. TAB FACTURAS
   ↓
   Usuario carga PDF del proveedor
   ↓
   Sistema extrae: CUFE, Proveedor, Fecha, Número, Total
   ↓
   Factura creada con estado "pendiente_dian"

2. TAB CUFE
   ↓
   Usuario descarga archivo DIAN (manualmente desde web DIAN)
   ↓
   Usuario carga archivo DIAN al sistema
   ↓
   Sistema extrae TODOS los datos (emisor, productos, totales)
   ↓
   Factura actualizada con estado "completo"
   ↓
   Productos insertados en base de datos

3. TAB PRODUCTOS
   ↓
   Vista consolidada de todos los productos
   ↓
   Filtros avanzados y búsqueda
   ↓
   Historial de compras por producto
```

## 🗂️ Estructura de Archivos

### Modelos
- `CODE/src/app/models/invoice_v2.py` - Modelos SQLAlchemy (InvoiceV2, InvoiceProductV2)

### Servicios
- `CODE/src/app/services/pdf_parser_service.py` - Parser genérico de PDFs
- `CODE/src/app/services/invoice_v2_service.py` - Lógica de negocio

### Rutas
- `CODE/src/app/routes/invoices_v2_routes.py` - API REST
- `CODE/src/app/routes/invoices_v2_web_routes.py` - Vistas HTML

### Vistas
- `CODE/src/templates/invoices_v2/layout.html` - Layout base
- `CODE/src/templates/invoices_v2/facturas.html` - TAB FACTURAS
- `CODE/src/templates/invoices_v2/cufe.html` - TAB CUFE
- `CODE/src/templates/invoices_v2/productos.html` - TAB PRODUCTOS

### Migraciones
- `CODE/alembic/versions/20260130_create_invoice_system_v2.py` - Migración de base de datos

## 🚀 Instalación

### 1. Aplicar migración de base de datos

```bash
cd CODE
alembic upgrade head
```

### 2. Registrar rutas en main.py

Agregar en `CODE/src/main.py`:

```python
from .app.routes import invoices_v2_routes, invoices_v2_web_routes

# Registrar rutas API
app.include_router(invoices_v2_routes.router)

# Registrar rutas web
app.include_router(invoices_v2_web_routes.router)
```

### 3. Instalar dependencias (si es necesario)

```bash
pip install pdftotext  # Para extracción de texto de PDFs
```

## 📊 Modelo de Datos

### Tabla: invoices_v2

**Campos principales:**
- `cufe` (PK) - Código único de 96 caracteres (inmutable)
- `archivo_proveedor_url` - URL del PDF del proveedor
- `archivo_dian_url` - URL del PDF de DIAN

**Datos del proveedor (extraídos del PDF):**
- `proveedor_nombre`
- `proveedor_nit`
- `fecha_emision`
- `numero_factura`
- `total_factura`
- `proveedor_datos_raw` (JSONB) - Datos adicionales

**Datos DIAN (extraídos del archivo DIAN):**
- `dian_validado` - Boolean
- `dian_emisor_*` - Datos del emisor
- `dian_adquiriente_*` - Datos del comprador
- `dian_total_*` - Totales financieros
- `dian_datos_raw` (JSONB) - Datos completos

**Estado:**
- `estado` - pendiente_dian, completo, error, sin_dian

### Tabla: invoice_products_v2

**Campos:**
- `id` (PK)
- `cufe` (FK) - Relación con factura (ON DELETE CASCADE)
- `codigo_producto` - EAN/UPC
- `descripcion`
- `cantidad`
- `precio_unitario`
- `iva_porcentaje`
- `iva_valor`
- `total_item`
- `fecha_compra`

## 🔌 API Endpoints

### TAB FACTURAS

```
POST   /api/v2/invoices/facturas/upload
GET    /api/v2/invoices/facturas
GET    /api/v2/invoices/facturas/{cufe}
PUT    /api/v2/invoices/facturas/{cufe}
DELETE /api/v2/invoices/facturas/{cufe}
```

### TAB CUFE

```
POST   /api/v2/invoices/cufe/{cufe}/upload-dian
GET    /api/v2/invoices/cufe
GET    /api/v2/invoices/cufe/{cufe}/full
```

### TAB PRODUCTOS

```
GET    /api/v2/invoices/productos
GET    /api/v2/invoices/productos/{codigo_producto}/history
```

### Estadísticas

```
GET    /api/v2/invoices/statistics
```

## 🌐 Vistas Web

```
/invoices-v2/facturas   - TAB FACTURAS
/invoices-v2/cufe       - TAB CUFE
/invoices-v2/productos  - TAB PRODUCTOS
```

## 🎯 Características

### TAB FACTURAS
- ✅ Carga de PDFs de proveedores
- ✅ Extracción automática de CUFE, Proveedor, Fecha, Número, Total
- ✅ Edición de campos (excepto CUFE)
- ✅ Eliminación en cascada
- ✅ Filtros por estado, fecha, búsqueda
- ✅ Vista de archivos PDF

### TAB CUFE
- ✅ Lista de códigos CUFE con estado de validación
- ✅ Carga de archivos DIAN
- ✅ Extracción completa de datos (emisor, productos, totales)
- ✅ Actualización automática de toda la información
- ✅ Vista detallada con todos los datos
- ✅ Link directo a validación DIAN
- ✅ Estadísticas (pendientes, completos, productos)

### TAB PRODUCTOS
- ✅ Catálogo completo de productos
- ✅ Filtros avanzados (descripción, código, proveedor, fechas)
- ✅ Historial de compras por producto
- ✅ Exportación a CSV
- ✅ Paginación
- ✅ Link a factura original

## 🔒 Reglas de Negocio

1. **CUFE es inmutable** - No se puede editar una vez creado
2. **CUFE es único** - No se pueden duplicar facturas
3. **Eliminación en cascada** - Al eliminar una factura se eliminan todos sus productos
4. **Archivo DIAN es la fuente de verdad** - Sobrescribe datos del proveedor
5. **Todos los campos son editables excepto CUFE**

## 🧪 Pruebas

### Probar extracción de PDF proveedor

```python
from src.app.services.pdf_parser_service import PDFParserService

parser = PDFParserService()
result = parser.parse_provider_invoice('path/to/factura.pdf')
print(result)
```

### Probar extracción de PDF DIAN

```python
result = parser.parse_dian_document('path/to/dian.pdf')
print(result)
```

## 📝 Notas Técnicas

### Parser Genérico
El parser está diseñado para adaptarse a diferentes formatos de proveedores:
- Usa múltiples patrones regex
- Estrategias de búsqueda por anchors
- Normalización automática de datos
- Manejo de errores robusto

### Almacenamiento Flexible
Los campos `proveedor_datos_raw` y `dian_datos_raw` (JSONB) permiten:
- Guardar datos adicionales sin modificar el esquema
- Debugging y auditoría
- Futuras extensiones

### Búsqueda Eficiente
- Índices en campos clave (CUFE, fecha, proveedor)
- Índice GIN para búsqueda de texto en descripciones
- Paginación en todas las vistas

## 🐛 Troubleshooting

### Error: "No se pudo extraer el CUFE"
- Verificar que el PDF contiene un código de 96 caracteres hexadecimales
- Revisar que el PDF no está protegido o encriptado

### Error: "El CUFE no coincide"
- Asegurarse de cargar el archivo DIAN correcto para la factura
- Verificar que el CUFE en ambos archivos es el mismo

### Productos no se extraen correctamente
- El parser de productos es genérico y puede necesitar ajustes
- Revisar el campo `dian_datos_raw` para ver el texto completo
- Ajustar patrones en `_extract_productos()` si es necesario

## 🔄 Próximas Mejoras

- [ ] OCR para PDFs escaneados
- [ ] Validación automática con API DIAN
- [ ] Descarga automática de archivos DIAN
- [ ] Análisis de precios y tendencias
- [ ] Alertas de productos duplicados
- [ ] Integración con sistema de inventario
- [ ] Reportes y dashboards

## 📞 Soporte

Para dudas o problemas, revisar:
1. Logs de la aplicación
2. Campo `dian_datos_raw` para debugging
3. Documentación de DIAN: https://www.dian.gov.co/
