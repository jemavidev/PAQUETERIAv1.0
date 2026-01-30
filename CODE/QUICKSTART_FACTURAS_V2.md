# 🚀 Quick Start - Sistema de Facturas V2

Guía rápida para poner en marcha el sistema de facturas.

## 📋 Pre-requisitos

- PostgreSQL corriendo
- Python 3.9+
- pdftotext instalado (`apt-get install poppler-utils` en Linux)

## 🔧 Instalación

### 1. Aplicar migración de base de datos

```bash
cd CODE
alembic upgrade head
```

Esto creará las tablas:
- `invoices_v2`
- `invoice_products_v2`

### 2. Verificar que las rutas están registradas

Las rutas ya están incluidas en `main.py`:
- API: `/api/v2/invoices/*`
- Web: `/invoices-v2/*`

### 3. Reiniciar el servidor

```bash
# Si usas Docker
docker-compose restart web

# Si usas uvicorn directamente
uvicorn src.main:app --reload
```

## 🧪 Probar el Sistema

### Opción 1: Usar el script de prueba

```bash
cd CODE
python test_invoice_v2_system.py
```

Este script probará la extracción de datos de los PDFs de ejemplo.

### Opción 2: Usar la interfaz web

1. Abrir navegador en: `http://localhost:8000/invoices-v2/facturas`
2. Hacer clic en "Cargar Factura"
3. Seleccionar un PDF de proveedor
4. El sistema extraerá automáticamente: CUFE, Proveedor, Fecha, Número, Total

### Opción 3: Usar la API directamente

```bash
# Cargar factura de proveedor
curl -X POST "http://localhost:8000/api/v2/invoices/facturas/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/factura.pdf"

# Listar facturas
curl "http://localhost:8000/api/v2/invoices/facturas"

# Cargar archivo DIAN
curl -X POST "http://localhost:8000/api/v2/invoices/cufe/{CUFE}/upload-dian" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/dian.pdf"

# Listar productos
curl "http://localhost:8000/api/v2/invoices/productos"
```

## 📊 Acceder a las Vistas

### TAB 1: FACTURAS
`http://localhost:8000/invoices-v2/facturas`

Funciones:
- ✅ Cargar PDFs de proveedores
- ✅ Ver lista de facturas
- ✅ Editar datos
- ✅ Eliminar facturas

### TAB 2: CUFE
`http://localhost:8000/invoices-v2/cufe`

Funciones:
- ✅ Ver códigos CUFE
- ✅ Cargar archivos DIAN
- ✅ Ver detalles completos
- ✅ Link a validación DIAN

### TAB 3: PRODUCTOS
`http://localhost:8000/invoices-v2/productos`

Funciones:
- ✅ Buscar productos
- ✅ Filtrar por proveedor/fecha
- ✅ Ver historial de compras
- ✅ Exportar a CSV

## 🔍 Verificar que Funciona

### 1. Verificar tablas en base de datos

```sql
-- Ver facturas
SELECT cufe, proveedor_nombre, numero_factura, total_factura, estado 
FROM invoices_v2 
LIMIT 10;

-- Ver productos
SELECT id, cufe, descripcion, cantidad, precio_unitario, total_item 
FROM invoice_products_v2 
LIMIT 10;

-- Estadísticas
SELECT 
    COUNT(*) as total_facturas,
    SUM(CASE WHEN estado = 'completo' THEN 1 ELSE 0 END) as completas,
    SUM(CASE WHEN estado = 'pendiente_dian' THEN 1 ELSE 0 END) as pendientes
FROM invoices_v2;
```

### 2. Verificar API

```bash
# Health check
curl http://localhost:8000/health

# Estadísticas
curl http://localhost:8000/api/v2/invoices/statistics
```

### 3. Verificar logs

```bash
# Ver logs del servidor
docker-compose logs -f web

# Buscar errores
docker-compose logs web | grep ERROR
```

## 🐛 Troubleshooting

### Error: "No module named 'pdftotext'"

```bash
# Instalar poppler-utils
apt-get update && apt-get install -y poppler-utils
```

### Error: "Table 'invoices_v2' doesn't exist"

```bash
# Aplicar migración
cd CODE
alembic upgrade head
```

### Error: "No se pudo extraer el CUFE"

- Verificar que el PDF contiene un código de 96 caracteres hexadecimales
- Probar con el script de prueba para ver el texto extraído
- Revisar logs para más detalles

### Los productos no se extraen

- El parser es genérico y puede necesitar ajustes
- Revisar el campo `dian_datos_raw` en la base de datos
- Ajustar patrones en `pdf_parser_service.py` si es necesario

## 📚 Documentación Completa

Ver: `CODE/docs/SISTEMA_FACTURAS_V2.md`

## 🎯 Flujo de Trabajo Típico

1. **Recibir factura del proveedor** (PDF por email/WhatsApp)
2. **Cargar en TAB FACTURAS** → Sistema extrae CUFE automáticamente
3. **Ir a página DIAN** → Buscar CUFE → Descargar archivo oficial
4. **Cargar en TAB CUFE** → Sistema extrae TODOS los datos + productos
5. **Consultar en TAB PRODUCTOS** → Ver catálogo completo

## ✅ Checklist de Verificación

- [ ] Migración aplicada correctamente
- [ ] Servidor reiniciado
- [ ] Puedo acceder a `/invoices-v2/facturas`
- [ ] Puedo cargar un PDF de proveedor
- [ ] Se extrae el CUFE correctamente
- [ ] Puedo cargar un archivo DIAN
- [ ] Se extraen los productos
- [ ] Puedo ver productos en TAB PRODUCTOS
- [ ] Puedo buscar y filtrar productos

## 🆘 Soporte

Si tienes problemas:

1. Revisar logs: `docker-compose logs -f web`
2. Verificar base de datos: `psql -U postgres -d paquetex`
3. Probar script de prueba: `python test_invoice_v2_system.py`
4. Revisar documentación completa en `docs/SISTEMA_FACTURAS_V2.md`

---

**¡Listo! El sistema está funcionando.** 🎉
