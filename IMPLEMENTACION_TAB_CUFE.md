# Implementación Tab CUFE - Solución Semi-automática

## 📋 Resumen

Se ha implementado una solución **semi-automática** para la gestión de códigos CUFE y descarga de facturas desde la DIAN.

## ✨ Características Implementadas

### 1. **Tab CUFE Mejorado**
- ✅ Interfaz similar al tab de FACTURAS
- ✅ Estadísticas en tiempo real (Total, Pendientes, Descargados, Procesados)
- ✅ Búsqueda en tiempo real por CUFE, proveedor o número
- ✅ Filtros por estado
- ✅ Tabla con información detallada

### 2. **Flujo Semi-automático**
```
1. Usuario ingresa CUFE (96 caracteres)
   ↓
2. Sistema registra CUFE en BD
   ↓
3. Se abre página de DIAN en nueva pestaña
   ↓
4. Usuario resuelve captcha manualmente
   ↓
5. Usuario descarga PDF desde DIAN
   ↓
6. Usuario sube PDF al sistema
   ↓
7. Sistema procesa e importa automáticamente
```

### 3. **Estados del CUFE**
- 🟡 **Pendiente**: Registrado, esperando descarga
- 🔵 **Descargando**: En proceso
- 🟢 **Descargado**: PDF descargado, listo para procesar
- 🟣 **Procesando**: Extrayendo datos del PDF
- ✅ **Procesado**: Factura importada exitosamente
- 🔴 **Error**: Falló el proceso

### 4. **Funcionalidades**
- ✅ Agregar CUFE con validación de 96 caracteres
- ✅ Contador de caracteres en tiempo real
- ✅ Apertura automática de página DIAN
- ✅ Modal para subir PDF descargado
- ✅ Drag & drop para archivos
- ✅ Procesamiento automático del PDF
- ✅ Extracción de datos (proveedor, número, productos, etc.)
- ✅ Vinculación con factura procesada
- ✅ Copiar CUFE al portapapeles
- ✅ Eliminar registros de CUFE

## 📁 Archivos Creados/Modificados

### Nuevos Archivos
1. **`CODE/src/app/models/cufe.py`**
   - Modelo de base de datos para CufeRecord
   - Enum CufeStatus con estados

2. **`CODE/alembic/versions/create_cufe_records_table.py`**
   - Migración de base de datos
   - Crea tabla `cufe_records`
   - Índices optimizados

3. **`CODE/scripts/run_cufe_migration.sh`**
   - Script para ejecutar migración

### Archivos Modificados
1. **`CODE/src/templates/invoices/_tab_cufe.html`**
   - UI completa del tab CUFE
   - Modales para agregar CUFE y subir PDF
   - JavaScript para manejo de eventos

2. **`CODE/src/templates/invoices/dashboard.html`**
   - Función `loadCufeTab()` actualizada
   - Renderizado de tabla con datos reales

3. **`CODE/src/app/routes/invoices.py`**
   - Nuevos endpoints:
     - `GET /invoices/api/cufe/stats` - Estadísticas
     - `GET /invoices/api/cufe/list` - Lista de CUFEs
     - `POST /invoices/api/cufe/register` - Registrar CUFE
     - `POST /invoices/api/cufe/process-dian-pdf` - Procesar PDF
     - `DELETE /invoices/api/cufe/{id}` - Eliminar CUFE

## 🗄️ Estructura de Base de Datos

### Tabla: `cufe_records`
```sql
CREATE TABLE cufe_records (
    id SERIAL PRIMARY KEY,
    cufe VARCHAR(96) UNIQUE NOT NULL,
    status cufestatus NOT NULL DEFAULT 'pending',
    supplier_name VARCHAR(255),
    invoice_number VARCHAR(100),
    invoice_id INTEGER REFERENCES invoices(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP,
    created_by INTEGER NOT NULL REFERENCES users(id),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

CREATE INDEX ix_cufe_records_cufe ON cufe_records(cufe);
CREATE INDEX ix_cufe_records_status ON cufe_records(status);
CREATE INDEX ix_cufe_records_created_at ON cufe_records(created_at);
```

## 🚀 Instrucciones de Despliegue

### 1. Ejecutar Migración de Base de Datos

#### Opción A: Usando el script
```bash
cd CODE
./scripts/run_cufe_migration.sh
```

#### Opción B: Manual
```bash
cd CODE
alembic upgrade head
```

### 2. Verificar Migración
```bash
# Conectarse a la base de datos
psql -U postgres -d paqueteria

# Verificar tabla
\d cufe_records

# Verificar enum
\dT+ cufestatus
```

### 3. Reiniciar Servicios
```bash
# Si estás en desarrollo
docker-compose restart web

# Si estás en staging/producción
./deploy.sh staging
# o
./deploy.sh papyrus
```

## 📖 Guía de Uso

### Para el Usuario Final

1. **Agregar un CUFE**
   - Ir al tab "CUFE" en el dashboard de facturas
   - Clic en "Agregar CUFE"
   - Pegar el código CUFE (96 caracteres)
   - Clic en "Abrir en DIAN"

2. **Descargar desde DIAN**
   - Se abre automáticamente la página de la DIAN
   - Resolver el captcha manualmente
   - Descargar el PDF

3. **Procesar PDF**
   - Automáticamente se abre modal para subir PDF
   - Arrastrar o seleccionar el PDF descargado
   - Clic en "Procesar PDF"
   - El sistema extrae datos automáticamente

4. **Ver Factura Procesada**
   - Una vez procesado, aparece botón "Ver Factura"
   - Clic para ver detalles completos

### Ejemplo de CUFE
```
9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31
```

## 🔍 Endpoints API

### GET `/invoices/api/cufe/stats`
Obtiene estadísticas de CUFEs
```json
{
  "total": 10,
  "pending": 3,
  "downloaded": 2,
  "processed": 5
}
```

### GET `/invoices/api/cufe/list?limit=50&status=pending`
Lista CUFEs con filtros opcionales
```json
{
  "success": true,
  "cufes": [
    {
      "id": 1,
      "cufe": "9a08220827564c03...",
      "status": "pending",
      "supplier_name": "Proveedor XYZ",
      "invoice_number": "FV-001",
      "invoice_id": null,
      "created_at": "2025-01-19T10:00:00",
      "error_message": null
    }
  ]
}
```

### POST `/invoices/api/cufe/register`
Registra un nuevo CUFE
```json
// Request
{
  "cufe": "9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31"
}

// Response
{
  "success": true,
  "message": "CUFE registrado exitosamente",
  "cufe_id": 1,
  "dian_url": "https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey=..."
}
```

### POST `/invoices/api/cufe/process-dian-pdf`
Procesa PDF descargado de DIAN
```json
// FormData
file: [PDF file]
cufe_id: 1

// Response
{
  "success": true,
  "message": "PDF procesado e importado exitosamente",
  "invoice_id": 123,
  "invoice_number": "FV-001"
}
```

### DELETE `/invoices/api/cufe/{cufe_id}`
Elimina un registro de CUFE
```json
{
  "success": true,
  "message": "CUFE eliminado correctamente"
}
```

## 🧪 Testing

### 1. Probar Registro de CUFE
```bash
curl -X POST http://localhost:8000/invoices/api/cufe/register \
  -H "Content-Type: application/json" \
  -d '{"cufe":"9a08220827564c03bbc2c9dea3d682b50e70391b873c1ef5450af089f8eaad65909182eb584ffd1cde11c18614b27f31"}'
```

### 2. Probar Lista de CUFEs
```bash
curl http://localhost:8000/invoices/api/cufe/list
```

### 3. Probar Estadísticas
```bash
curl http://localhost:8000/invoices/api/cufe/stats
```

## 🐛 Troubleshooting

### Error: "CUFE debe tener 96 caracteres"
- Verificar que el CUFE copiado no tenga espacios o saltos de línea
- El CUFE debe ser exactamente 96 caracteres hexadecimales

### Error: "Este CUFE ya está registrado"
- El CUFE ya existe en el sistema
- Buscar en la tabla para ver su estado actual

### Error al procesar PDF
- Verificar que el PDF sea el descargado de la DIAN
- Revisar logs para ver detalles del error
- El PDF debe contener datos estructurados válidos

### Tabla no existe
```bash
# Ejecutar migración
cd CODE
alembic upgrade head
```

## 📊 Monitoreo

### Consultas SQL Útiles

```sql
-- Ver todos los CUFEs
SELECT id, cufe, status, supplier_name, created_at 
FROM cufe_records 
ORDER BY created_at DESC;

-- Contar por estado
SELECT status, COUNT(*) 
FROM cufe_records 
GROUP BY status;

-- Ver CUFEs con errores
SELECT id, cufe, error_message, retry_count 
FROM cufe_records 
WHERE status = 'error';

-- Ver CUFEs procesados con factura
SELECT cr.id, cr.cufe, cr.supplier_name, i.numero_documento, i.total
FROM cufe_records cr
JOIN invoices i ON cr.invoice_id = i.id
WHERE cr.status = 'processed';
```

## 🎯 Próximas Mejoras (Opcional)

1. **Procesamiento por lotes**
   - Agregar múltiples CUFEs a la vez
   - Abrir todas las páginas de DIAN simultáneamente

2. **Notificaciones**
   - Notificar cuando un CUFE esté listo para procesar
   - Alertas de errores

3. **Historial**
   - Registro de intentos de descarga
   - Auditoría de cambios de estado

4. **Integración con servicio de captchas** (Costo adicional)
   - 2Captcha, Anti-Captcha, etc.
   - Automatización completa

## ✅ Checklist de Verificación

- [ ] Migración ejecutada correctamente
- [ ] Tabla `cufe_records` creada
- [ ] Enum `cufestatus` creado
- [ ] Índices creados
- [ ] Servicios reiniciados
- [ ] Tab CUFE visible en dashboard
- [ ] Botón "Agregar CUFE" funcional
- [ ] Modal de agregar CUFE funcional
- [ ] Validación de 96 caracteres funciona
- [ ] Apertura de página DIAN funciona
- [ ] Modal de subir PDF funciona
- [ ] Procesamiento de PDF funciona
- [ ] Estadísticas se actualizan
- [ ] Filtros funcionan
- [ ] Búsqueda funciona
- [ ] Eliminar CUFE funciona

## 📝 Notas Importantes

1. **Seguridad**: Los CUFEs son únicos y se validan antes de registrar
2. **Performance**: Índices optimizados para búsquedas rápidas
3. **Auditoría**: Se registra quién creó cada CUFE
4. **Errores**: Se guardan mensajes de error para debugging
5. **Reintentos**: Campo `retry_count` para futuros reintentos automáticos

## 🎉 Conclusión

La implementación está completa y lista para usar. El flujo semi-automático permite:
- ✅ Registro rápido de CUFEs
- ✅ Apertura automática de DIAN
- ✅ Usuario resuelve captcha (único paso manual)
- ✅ Procesamiento automático del PDF
- ✅ Importación completa de la factura

**¡Todo listo para desplegar!** 🚀
