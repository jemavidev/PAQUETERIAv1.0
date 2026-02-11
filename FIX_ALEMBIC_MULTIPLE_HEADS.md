# Fix Alembic Multiple Heads - COMPLETADO ✅

## Problema
Al ejecutar `alembic upgrade head` se obtenía el error:
```
ERROR [alembic.util.messaging] Multiple head revisions are present for given argument 'head'
```

## Causa
Existían múltiples "heads" (migraciones sin dependientes) en el árbol de migraciones:
- `20260211_092552` - add_tipo_factura
- `20260211_093000` - merge_all_heads (migración de merge incorrecta)
- `536e9b775d34` - merge_traceability_and_invoice_v2
- `add_supplier_invoices` - supplier invoices table

## Solución Aplicada

### 1. Eliminada migración de merge incorrecta
```bash
rm CODE/alembic/versions/20260211_093000_merge_all_heads.py
```

La migración `20260211_093000` estaba mal configurada porque incluía `20260211_092552` en su `down_revision`, pero `20260211_092552` ya dependía de `536e9b775d34`, creando una referencia circular.

### 2. Actualizada migración `20260211_092552` como merge point
Modificado `CODE/alembic/versions/20260211_092552_add_tipo_factura.py` para que sea el único head y unifique todas las ramas:

```python
down_revision = (
    '536e9b775d34',           # merge traceability and invoice_v2
    'add_supplier_invoices',  # supplier invoices table
    'create_customer_prefs',  # customer preferences
    'create_cufe_records',    # cufe records
    'add_incremental_sync',   # incremental sync
    'add_products_001',       # products table
)
```

Esta migración ahora:
- Unifica todas las ramas divergentes
- Agrega el campo `tipo_factura` a la tabla `invoices_v2`
- Es el único head en el árbol de migraciones

## Verificación

### Script de verificación
Creado `verificar_alembic_heads.py` para verificar que solo existe 1 head:

```bash
python3 verificar_alembic_heads.py
```

Resultado:
```
✅ Total de migraciones: 37
✅ Total de heads: 1

✅ CORRECTO: Solo existe 1 head
   Head: 20260211_092552
   Archivo: 20260211_092552_add_tipo_factura.py
```

## Próximos Pasos

### 1. Reiniciar servidor staging
```bash
sudo ./reiniciar_servidor_completo.sh
```

### 2. Verificar que las migraciones se aplican correctamente
El script de deploy ejecutará:
```bash
alembic upgrade head
```

Esto debería funcionar sin errores ahora que solo existe 1 head.

### 3. Verificar funcionalidad
- TAB Productos: Verificar que aparece el selector de "Tipo de Factura"
- TAB Facturas: Verificar que aparece el campo "Tipo de Factura" en el modal de edición
- Por defecto debe mostrar solo productos de reventa

## Archivos Modificados
- ✅ `CODE/alembic/versions/20260211_092552_add_tipo_factura.py` - Actualizado como merge point
- ✅ `CODE/alembic/versions/20260211_093000_merge_all_heads.py` - ELIMINADO
- ✅ `verificar_alembic_heads.py` - Script de verificación creado

## Estado
✅ COMPLETADO - Solo existe 1 head, listo para aplicar migraciones
