# Fix Dashboard /invoices - Error 500

## Problema Identificado

Los endpoints `/invoices/api/supplier-invoices/stats` y `/invoices/api/supplier-invoices/list` estaban devolviendo error 500 debido a:

1. **Import incorrecto**: Se estaba importando `ImportStatusEnum` desde `app.models.supplier_invoice` cuando el enum correcto es `SupplierInvoiceStatus` desde `app.models.invoice`
2. **Campo incorrecto**: Se intentaba ordenar por `created_at` cuando el campo correcto es `uploaded_at`
3. **Falta de manejo de errores**: No había try-catch adecuado para capturar y loggear errores

## Cambios Realizados

### 1. Corregido endpoint `/api/supplier-invoices/stats`

**Antes:**
```python
from app.models.supplier_invoice import SupplierInvoice, ImportStatusEnum
# ImportStatusEnum no existe en ese módulo
```

**Después:**
```python
from app.models.invoice import SupplierInvoice, SupplierInvoiceStatus, Invoice
# Imports correctos desde el módulo correcto
```

**Estados corregidos:**
- `ImportStatusEnum.PROCESSED` → `SupplierInvoiceStatus.PROCESSED`
- `ImportStatusEnum.UPLOADED, ImportStatusEnum.PENDING` → `SupplierInvoiceStatus.PENDING, SupplierInvoiceStatus.CUFE_EXTRACTED`

### 2. Corregido endpoint `/api/supplier-invoices/list`

**Cambios:**
- Campo de ordenamiento: `created_at` → `uploaded_at`
- Agregado fallback para datos cuando no hay factura procesada
- Mejorado manejo de errores con try-catch anidado
- Agregado logging detallado de errores

**Datos con fallback:**
```python
"fecha_emision": processed_data.get("fecha_emision") or (inv.invoice_date.isoformat() if inv.invoice_date else None),
"proveedor": processed_data.get("proveedor") or inv.supplier_name,
"numero_documento": processed_data.get("numero_documento") or inv.invoice_number,
"total": processed_data.get("total", 0) or (inv.total_amount or 0),
```

### 3. Manejo de Errores Mejorado

Ambos endpoints ahora tienen:
- Try-catch principal que captura cualquier error
- Logging detallado con `exc_info=True` para stack traces
- Respuestas de fallback con datos vacíos en caso de error
- Try-catch interno en el loop de facturas para evitar que una factura problemática rompa toda la lista

## Valores del Enum SupplierInvoiceStatus

```python
class SupplierInvoiceStatus(enum.Enum):
    PENDING = "pending"              # Subida, pendiente de procesar CUFE
    NO_CUFE = "no_cufe"              # Sin CUFE detectado
    CUFE_EXTRACTED = "cufe_extracted"  # CUFE extraído, pendiente descarga DIAN
    DIAN_DOWNLOADED = "dian_downloaded"  # PDF de DIAN descargado
    PROCESSED = "processed"          # Procesada e importada al sistema
    ERROR = "error"                  # Error en el proceso
    DUPLICATE = "duplicate"          # CUFE duplicado
```

## Testing

Se creó script de prueba: `test_dashboard_endpoints.py`

Para ejecutar:
```bash
cd CODE
python ../test_dashboard_endpoints.py
```

## Archivos Modificados

1. `CODE/src/app/routes/invoices.py` - Corregidos endpoints API
2. `CODE/src/templates/invoices/dashboard.html` - Ya estaba correcto (cambio anterior)

## Próximos Pasos

1. Desplegar los cambios a staging
2. Verificar que los endpoints respondan correctamente
3. Verificar que el dashboard cargue los datos
4. Revisar logs del servidor para confirmar que no hay errores

## Comandos de Deploy

```bash
# Desde el directorio raíz del proyecto
./deploy.sh papyrus

# O si usas el sistema de deploy
cd .deploy
./deploy.sh papyrus
```

## Verificación Post-Deploy

1. Abrir https://staging.jemavi.co/invoices
2. Verificar que las estadísticas se carguen (números en las tarjetas)
3. Verificar que la tabla muestre facturas
4. Cambiar entre tabs (Facturas, CUFE, Productos)
5. Revisar la consola del navegador - no debe haber errores 500
