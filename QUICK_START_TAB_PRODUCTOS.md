# QUICK START - TAB Productos

## 🚀 Cómo Probar la Implementación

### 1. Ver Ejemplo Visual (Sin Backend)

Abre el archivo HTML en tu navegador para ver cómo se verán los badges:

```bash
# Opción 1: Abrir directamente
open EJEMPLO_VISUAL_BADGES_PRODUCTOS.html

# Opción 2: Con servidor HTTP simple
python3 -m http.server 8000
# Luego abre: http://localhost:8000/EJEMPLO_VISUAL_BADGES_PRODUCTOS.html
```

### 2. Probar con el Backend

#### Iniciar el servidor
```bash
cd CODE
./start_server.sh
```

#### Acceder al TAB Productos
```
http://localhost:8000/invoices/v2/productos
```

### 3. Verificar la API

#### Listar productos con análisis
```bash
curl -X GET "http://localhost:8000/api/v2/invoices/productos?limit=10" \
  -H "Accept: application/json" \
  | jq '.'
```

#### Buscar productos específicos
```bash
curl -X GET "http://localhost:8000/api/v2/invoices/productos?search=ACEITE&limit=5" \
  -H "Accept: application/json" \
  | jq '.items[] | {descripcion, precio_unitario, iva_porcentaje, variacion_tipo}'
```

#### Ver análisis detallado de un producto
```bash
curl -X GET "http://localhost:8000/api/v2/invoices/productos/123/analisis" \
  -H "Accept: application/json" \
  | jq '.'
```

### 4. Casos de Prueba

#### Caso 1: Producto con IVA
- Busca un producto que tenga `iva_porcentaje > 0`
- Verifica que aparezca el badge verde "+IVA"
- Verifica que el precio muestre "IVA incl."

#### Caso 2: Producto con Descuento
- Busca un producto que tenga `descuento_valor > 0`
- Verifica que aparezca el badge azul con el valor del descuento

#### Caso 3: Producto con Variación de Precio
- Carga la misma factura dos veces con precios diferentes
- Verifica que aparezca el badge rojo (↑) o verde oscuro (↓)

#### Caso 4: Primera Compra
- Carga un producto nuevo que no exista en el sistema
- Verifica que aparezca el badge morado "1ª"

### 5. Verificar Logs

```bash
# Ver logs del servidor
tail -f CODE/logs/app.log

# Buscar logs de productos
grep "productos" CODE/logs/app.log

# Ver cálculos de variación
grep "variacion" CODE/logs/app.log
```

### 6. Debugging

#### Si no aparecen los badges:
1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Network"
3. Recarga la página
4. Busca la petición a `/api/v2/invoices/productos`
5. Verifica que la respuesta incluya los campos:
   - `iva_porcentaje`
   - `descuento_valor`
   - `recargo_valor`
   - `variacion_precio`
   - `variacion_tipo`

#### Si los cálculos son incorrectos:
1. Ejecuta el test de lógica:
   ```bash
   python3 test_variacion_precio_logic.py
   ```
2. Verifica los datos en la base de datos:
   ```sql
   SELECT 
     id, 
     descripcion, 
     codigo_producto, 
     precio_unitario, 
     fecha_compra
   FROM invoice_products_v2
   WHERE codigo_producto = 'TU_CODIGO'
   ORDER BY fecha_compra DESC;
   ```

### 7. Performance

#### Medir tiempo de respuesta:
```bash
time curl -X GET "http://localhost:8000/api/v2/invoices/productos?limit=100" \
  -H "Accept: application/json" \
  -o /dev/null -s
```

#### Si es lento (> 2 segundos):
- Considera agregar índice en `codigo_producto`:
  ```sql
  CREATE INDEX IF NOT EXISTS idx_products_codigo 
  ON invoice_products_v2(codigo_producto);
  ```
- Considera implementar cache de variaciones en Redis

### 8. Datos de Prueba

#### Crear productos con diferentes estados:
```python
# Ejecutar en Python shell
from CODE.src.app.database import SessionLocal
from CODE.src.app.models.invoice_v2 import InvoiceProductV2
from datetime import date
from decimal import Decimal

db = SessionLocal()

# Producto 1: Con IVA
prod1 = InvoiceProductV2(
    cufe="TEST_CUFE_001",
    descripcion="PRODUCTO CON IVA",
    codigo_producto="TEST001",
    cantidad=10,
    precio_unitario=Decimal("10000"),
    iva_porcentaje=Decimal("19"),
    iva_valor=Decimal("1900"),
    total_item=Decimal("11900"),
    fecha_compra=date.today()
)
db.add(prod1)

# Producto 2: Con descuento
prod2 = InvoiceProductV2(
    cufe="TEST_CUFE_002",
    descripcion="PRODUCTO CON DESCUENTO",
    codigo_producto="TEST002",
    cantidad=5,
    precio_unitario=Decimal("20000"),
    descuento_valor=Decimal("2000"),
    total_item=Decimal("18000"),
    fecha_compra=date.today()
)
db.add(prod2)

db.commit()
```

### 9. Checklist de Verificación

- [ ] Los badges se muestran correctamente
- [ ] Los tooltips funcionan al pasar el mouse
- [ ] Los precios muestran "IVA incl." cuando corresponde
- [ ] Las cantidades se muestran sin decimales
- [ ] La búsqueda funciona correctamente
- [ ] La paginación funciona
- [ ] Los badges son responsive en mobile
- [ ] No hay errores en la consola del navegador
- [ ] Los cálculos de variación son correctos
- [ ] El modal de detalle funciona

### 10. Troubleshooting

#### Error: "variacion_tipo is null"
- Verifica que el producto tenga `codigo_producto`
- Verifica que existan compras anteriores del mismo producto

#### Error: "descuento_valor is null"
- Normal si el producto no tiene descuento
- El badge no debería mostrarse

#### Badge de IVA no aparece
- Verifica que `iva_porcentaje > 0`
- Verifica la lógica en `renderProductRow()`

#### Performance lento
- Agrega índices en la base de datos
- Considera cache de variaciones
- Reduce el `limit` de productos por página

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `CODE/logs/app.log`
2. Verifica la consola del navegador (F12)
3. Ejecuta el test de lógica: `python3 test_variacion_precio_logic.py`
4. Revisa la documentación completa: `RESUMEN_TAB_PRODUCTOS_COMPLETADO.md`
