# 🚀 Guía Rápida: Activar Sistema de Trazabilidad

## ⚡ Pasos para Activar

### 1. Ejecutar Migración de Base de Datos

```bash
cd CODE
alembic upgrade head
```

**Esto agregará:**
- 10 nuevas columnas a la tabla `invoice_products_v2`
- 5 índices para mejorar performance de queries

**Tiempo estimado:** < 5 segundos

---

### 2. Verificar Migración

```bash
# Ver estado de migraciones
alembic current

# Debería mostrar: add_traceability_001
```

---

### 3. Probar con Facturas Nuevas

1. Ve al tab **CUFE** en `/invoices/cufe`
2. Sube un archivo DIAN de una factura
3. El sistema automáticamente:
   - Extrae los productos
   - Calcula trazabilidad para cada uno
   - Guarda con datos enriquecidos

4. Ve al tab **PRODUCTOS** en `/invoices/productos`
5. Verás las nuevas columnas:
   - **Precio Unit.** con promedio
   - **Variación** con badge de color
   - **Compras** con contador

---

### 4. Migrar Productos Existentes (Opcional)

Si ya tienes facturas cargadas y quieres recalcular su trazabilidad:

```bash
cd CODE

# Opción 1: Prueba rápida con 3 facturas
python quick_test_migration.py

# Opción 2: Migración completa (todas las facturas)
python migrate_reprocess_products.py

# Opción 3: Menú interactivo
bash COMANDOS_RAPIDOS.sh
# Selecciona opción 3: "Migrar productos (reprocesar)"
```

---

## 🎨 Qué Verás en la UI

### Tab PRODUCTOS

**Columna "Precio Unit.":**
```
$12,000
Prom: $11,000
```

**Columna "Variación":**
- 🔴 `↑ 20.0%` = Precio subió (rojo)
- 🟢 `↓ 15.5%` = Precio bajó (verde)
- 🔵 `→ 0.0%` = Precio igual (azul)
- ⚪ `Primera` = Primera compra (gris)

**Columna "Compras":**
- `1x` = 1 compra (gris)
- `5x` = 5 compras (azul)
- `10x` = 10+ compras (morado)

### Modal de Historial

Click en el botón ⏰ de cualquier producto para ver:

**Estadísticas:**
- Código del producto
- Total de compras
- Precio promedio
- Rango de precios (mín - máx)

**Historial:**
- Cada compra numerada (#1, #2, #3...)
- Variación respecto a compra anterior
- Todos los detalles (proveedor, factura, fecha, precio, etc.)

---

## 🔍 Verificar que Funciona

### Test 1: Cargar Primera Factura
1. Sube una factura DIAN con productos
2. Ve al tab PRODUCTOS
3. Deberías ver "Primera" en la columna Variación
4. Compras debería mostrar "1x"

### Test 2: Cargar Segunda Factura del Mismo Producto
1. Sube otra factura con el mismo código de producto
2. Ve al tab PRODUCTOS
3. Deberías ver:
   - Variación con ↑, ↓ o → según el precio
   - Precio promedio calculado
   - Compras mostrando "2x"

### Test 3: Ver Historial
1. Click en el botón ⏰ de un producto
2. Deberías ver:
   - Estadísticas generales
   - Lista de todas las compras
   - Variaciones entre compras

---

## 🐛 Solución de Problemas

### Error: "relation does not exist"
```bash
# La migración no se ejecutó correctamente
cd CODE
alembic upgrade head
```

### No veo las columnas nuevas
```bash
# Verificar que la migración se aplicó
cd CODE
alembic current

# Si no muestra "add_traceability_001", ejecutar:
alembic upgrade head
```

### Los productos no tienen trazabilidad
- **Productos nuevos:** Se calcula automáticamente al cargar DIAN
- **Productos existentes:** Ejecutar script de migración:
  ```bash
  cd CODE
  python migrate_reprocess_products.py
  ```

### Error al calcular trazabilidad
- El sistema continúa funcionando sin trazabilidad
- Revisa los logs para ver el error específico
- Los productos se guardan de todas formas

---

## 📊 Ejemplo Completo

### Escenario: Comprar el mismo producto 3 veces

**Compra 1 (2025-01-15):**
- Proveedor: DISTRIBUIDORA ABC
- Precio: $10,000
- Variación: `Primera` (gris)
- Compras: `1x`

**Compra 2 (2025-02-01):**
- Proveedor: DISTRIBUIDORA ABC
- Precio: $12,000
- Variación: `↑ 20.0%` (rojo)
- Precio promedio: $11,000
- Compras: `2x`

**Compra 3 (2025-02-15):**
- Proveedor: PROVEEDOR XYZ
- Precio: $9,500
- Variación: `↓ 20.8%` (verde)
- Precio promedio: $10,500
- Compras: `3x`

**En el historial verás:**
- Precio mínimo: $9,500
- Precio máximo: $12,000
- Precio promedio: $10,500
- Total compras: 3
- Comparación entre proveedores

---

## ✅ Checklist de Activación

- [ ] Ejecutar `alembic upgrade head`
- [ ] Verificar con `alembic current`
- [ ] Cargar una factura DIAN de prueba
- [ ] Verificar que aparecen las columnas nuevas en PRODUCTOS
- [ ] Probar el modal de historial
- [ ] (Opcional) Migrar productos existentes

---

## 🎯 Próximos Pasos

Una vez activado el sistema de trazabilidad:

1. **Cargar más facturas** para ver cómo se acumula el historial
2. **Comparar precios** entre proveedores
3. **Identificar tendencias** de precios
4. **Tomar decisiones** informadas de compra
5. **Negociar** con proveedores usando datos históricos

---

**¡Listo!** El sistema de trazabilidad está activado y funcionando. 🎉
