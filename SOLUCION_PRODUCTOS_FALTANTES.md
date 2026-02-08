# 🔧 Solución: Productos Faltantes

**Fecha**: 2026-02-08  
**Problema**: Solo 18 de 90 productos se estaban extrayendo  
**Causa**: Parser no reconocía formato de 3 facturas  
**Estado**: ✅ SOLUCIONADO

---

## 🔍 Diagnóstico

### Situación Inicial:
- **4 facturas DIAN cargadas**
- **Solo 1 factura** con productos extraídos (18 productos)
- **3 facturas** sin productos (0 productos cada una)
- **Total esperado**: ~90 productos
- **Total actual**: 18 productos

### Facturas Afectadas:
1. ✅ SOLUCIONES MAF S.A.S. (006D-611) - 18 productos extraídos
2. ❌ PAPYRUS SOLUCIONES INTEGRALES SAS (2FE-438) - 0 productos
3. ❌ DISTRIBUIDORA PAPYRUS S.A.S (FE-15778) - 0 productos
4. ❌ PAPYRUS SOLUCIONES INTEGRALES S.A.S. (FELN-1141) - 0 productos

---

## 🐛 Causa del Problema

### Formato NO Reconocido:

Las 3 facturas sin productos tienen un formato diferente:

```
Nro Código Descripción U/M Cantidad Precio Descuento Recargo IVA_valor IVA_% Total
1   631668 BOLSA DE PAPEL SELVA 33H-20CTG-25 A9 REF:9141 94 6,00 $ 840,34 $ 0,00 $ 0,00 $ 957,99 19.00 $ 5.042,04
```

**Características**:
- Descripción **entre** código y unidad de medida
- Unidad de medida como **código numérico** (94 = NIU)
- Múltiples valores monetarios (precio, descuento, recargo, IVA, total)

### Parser Anterior:

Solo reconocía 2 formatos:
1. `Nro [Código] U/M Cantidad Precio` (descripción en línea anterior/siguiente)
2. `Nro Código Descripción U/M | número Cantidad Precio` (formato POS)

**NO reconocía**: `Nro Código Descripción U/M_código Cantidad Precio...`

---

## ✅ Solución Implementada

### Cambios en `pdf_parser_service.py`:

**Agregado FORMATO 0** (nuevo patrón):

```python
# FORMATO 0: Nuevo formato con descripción entre código y U/M
# Formato: Nro Código Descripción U/M Cantidad Precio Descuento Recargo IVA_valor IVA_% Total
match_formato_nuevo = re.match(
    r'^(\d{1,3})\s+(\d{3,13})\s+(.+?)\s+(\d{2,3})\s+([0-9]+[.,][0-9]{2})\s+\$\s*([0-9.,]+)',
    line
)
```

**Características**:
- ✅ Extrae descripción completa entre código y U/M
- ✅ Mapea códigos de unidad (94→NIU, 10→PK, 11→BX, 01→UND)
- ✅ Extrae IVA porcentaje correctamente
- ✅ Extrae total del item (último valor monetario)

### Pruebas Realizadas:

```bash
python3 test_regex_productos.py
```

**Resultado**:
```
✅ Línea 1: 631668 - BOLSA DE PAPEL SELVA... - 6.0 NIU - $840.34 - 19% IVA - $5,042.04
✅ Línea 2: 631669 - BOLSA PAPEL CARROS... - 2.0 NIU - $840.34 - 19% IVA - $1,680.68
✅ Línea 3: 631655 - BOLSA PAPEL TROPICAL... - 2.0 NIU - $840.34 - 19% IVA - $1,680.68
```

---

## 🚀 Pasos para Aplicar la Solución

### OPCIÓN A: Reprocesar desde la Interfaz Web (RECOMENDADO)

1. **Reiniciar el servidor** para cargar el parser actualizado:
   ```bash
   # Si usas uvicorn directamente
   pkill -f uvicorn
   cd CODE
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   
   # O si usas docker
   docker-compose restart
   ```

2. **Ir al TAB CUFE**: http://localhost:8000/invoices/cufe

3. **Para cada factura sin productos**:
   - Buscar la factura (PAPYRUS SOLUCIONES, DISTRIBUIDORA PAPYRUS, etc.)
   - Click en "Cargar DIAN"
   - Volver a subir el mismo archivo PDF DIAN
   - El sistema detectará que ya existe y **reprocesará** los productos

4. **Verificar en TAB PRODUCTOS**: http://localhost:8000/invoices/productos
   - Deberías ver ~90 productos en total

---

### OPCIÓN B: Reprocesar desde Script (Alternativa)

Si prefieres reprocesar automáticamente sin resubir archivos:

1. **Asegurarte que el servidor está detenido**

2. **Ejecutar script de reprocesamiento**:
   ```bash
   cd CODE
   python3 -c "
   import os
   from dotenv import load_dotenv
   from sqlalchemy import create_engine, text
   
   load_dotenv()
   engine = create_engine(os.getenv('DATABASE_URL'))
   
   # Eliminar productos de las 3 facturas problemáticas
   with engine.connect() as conn:
       conn.execute(text('DELETE FROM invoice_products_v2 WHERE cufe IN (SELECT cufe FROM invoices_v2 WHERE estado = \"completo\" AND cufe NOT IN (SELECT DISTINCT cufe FROM invoice_products_v2 WHERE cufe LIKE \"6ee372e2%\"))'))
       conn.commit()
       print('✅ Productos antiguos eliminados')
   "
   ```

3. **Reiniciar servidor** (cargará parser actualizado)

4. **Resubir archivos DIAN** en TAB CUFE

---

## 📊 Resultado Esperado

### Antes:
```
Total productos: 18
  - SOLUCIONES MAF: 18 productos
  - PAPYRUS SOLUCIONES: 0 productos
  - DISTRIBUIDORA PAPYRUS: 0 productos
  - PAPYRUS SOLUCIONES (FELN): 0 productos
```

### Después:
```
Total productos: ~90
  - SOLUCIONES MAF: 18 productos
  - PAPYRUS SOLUCIONES: ~24 productos (estimado)
  - DISTRIBUIDORA PAPYRUS: ~24 productos (estimado)
  - PAPYRUS SOLUCIONES (FELN): ~24 productos (estimado)
```

---

## 🧪 Verificación

### 1. Verificar que el parser está actualizado:
```bash
cd CODE
grep -A 5 "FORMATO 0: Nuevo formato" src/app/services/pdf_parser_service.py
```

Debería mostrar el nuevo patrón.

### 2. Verificar productos en BD:
```bash
cd CODE
python3 -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM invoice_products_v2'))
    total = result.scalar()
    print(f'Total productos: {total}')
    
    result = conn.execute(text('''
        SELECT i.proveedor_nombre, COUNT(p.id) 
        FROM invoices_v2 i 
        LEFT JOIN invoice_products_v2 p ON i.cufe = p.cufe 
        WHERE i.estado = \"completo\" 
        GROUP BY i.proveedor_nombre
    '''))
    for row in result:
        print(f'  - {row[0]}: {row[1]} productos')
"
```

### 3. Verificar en interfaz web:
- http://localhost:8000/invoices/productos
- Deberías ver ~90 productos
- Buscar por código: 631668, 631669, 631655, etc.

---

## 📝 Archivos Modificados

1. **`CODE/src/app/services/pdf_parser_service.py`**:
   - Agregado FORMATO 0 para nuevo patrón
   - Mejorado regex de IVA
   - Mapeo de códigos de unidad de medida

2. **Archivos de prueba creados**:
   - `CODE/test_regex_productos.py` - Prueba del regex
   - `CODE/reprocesar_facturas_sin_productos.py` - Script de reprocesamiento

---

## 💡 Recomendación

**Usa OPCIÓN A** (reprocesar desde interfaz web):

1. Reinicia el servidor
2. Ve al TAB CUFE
3. Resubir los 3 archivos PDF DIAN problemáticos
4. Verifica en TAB PRODUCTOS que ahora tienes ~90 productos

Es más simple y seguro que ejecutar scripts directamente en la BD.

---

## 🎯 Próximos Pasos

Una vez que tengas los ~90 productos:

1. **Verificar calidad de datos**: Todos los productos deben tener código, descripción, precio, etc.
2. **Decidir sobre trazabilidad**: ¿Agregar campos de trazabilidad a la BD?
3. **Mejorar visualización**: Agregar columnas faltantes en TAB PRODUCTOS
4. **Cargar más facturas**: Para tener historial y poder calcular variaciones de precio

---

**Creado**: 2026-02-08  
**Estado**: Solución implementada, pendiente aplicar  
**Acción requerida**: Reiniciar servidor y reprocesar facturas
