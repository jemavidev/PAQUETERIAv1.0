# 🚀 Trazabilidad de Productos - Referencia Rápida

## ⚡ Activación en 3 Pasos

```bash
# 1. Ejecutar migración
cd CODE
alembic upgrade head

# 2. Verificar
alembic current
# Debe mostrar: add_traceability_001

# 3. ¡Listo! Cargar facturas y ver trazabilidad
```

---

## 📊 Qué Hace el Sistema

### Automático al Cargar Factura DIAN:
1. ✅ Extrae productos del PDF
2. ✅ Busca compras anteriores del mismo producto
3. ✅ Calcula precio anterior y variación
4. ✅ Calcula precio promedio, mínimo, máximo
5. ✅ Cuenta total de compras
6. ✅ Guarda todo en la base de datos

### En el Tab PRODUCTOS:
- 🔴 Badge rojo `↑ 20%` = Precio subió
- 🟢 Badge verde `↓ 15%` = Precio bajó
- 🔵 Badge azul `→ 0%` = Precio igual
- ⚪ Badge gris `Primera` = Primera compra
- 📊 Precio promedio debajo del precio actual
- 🔢 Contador de compras (`5x`, `10x`)

### En el Modal de Historial (botón ⏰):
- 📈 Estadísticas: total compras, precio promedio, rango
- 📋 Lista completa de todas las compras
- 🔄 Variación entre cada compra
- 👥 Comparación entre proveedores

---

## 🎯 Casos de Uso Rápidos

### "¿Este precio está bien?"
→ Mira el badge de variación y el precio promedio

### "¿Cuántas veces hemos comprado esto?"
→ Mira el badge de compras (`5x`, `10x`)

### "¿Qué proveedor es más barato?"
→ Click en ⏰ para ver historial completo

### "¿El precio está subiendo o bajando?"
→ Mira el badge: 🔴 subió, 🟢 bajó, 🔵 igual

### "¿Cuál es el precio normal?"
→ Mira el precio promedio (en gris)

---

## 🔧 Comandos Útiles

```bash
# Ver estado de migraciones
cd CODE
alembic current

# Ejecutar migración
alembic upgrade head

# Revertir migración (si es necesario)
alembic downgrade -1

# Migrar productos existentes
python migrate_reprocess_products.py

# Prueba rápida (3 facturas)
python quick_test_migration.py

# Menú interactivo
bash COMANDOS_RAPIDOS.sh
```

---

## 📁 Archivos Importantes

### Código
- `CODE/src/app/services/invoice_v2_service.py` - Lógica de cálculo
- `CODE/src/app/models/invoice_v2.py` - Modelo de datos
- `CODE/src/templates/invoices_v2/productos.html` - UI

### Migración
- `CODE/alembic/versions/add_product_traceability_fields.py`

### Scripts
- `CODE/migrate_reprocess_products.py` - Migración completa
- `CODE/quick_test_migration.py` - Prueba rápida

### Documentación
- `EJECUTAR_TRAZABILIDAD.md` - Guía de activación
- `OPCION_A_TRAZABILIDAD_IMPLEMENTADA.md` - Detalles técnicos
- `RESUMEN_COMPLETO_TRAZABILIDAD.md` - Resumen completo

---

## 🐛 Solución Rápida de Problemas

### No veo las columnas nuevas
```bash
cd CODE
alembic upgrade head
```

### Los productos no tienen trazabilidad
- **Nuevos:** Se calcula automáticamente
- **Existentes:** Ejecutar `python migrate_reprocess_products.py`

### Error en migración
```bash
# Ver estado
alembic current

# Ver historial
alembic history

# Forzar a última versión
alembic upgrade head
```

---

## 📊 Ejemplo Visual

```
Producto: ABC123 - TORNILLO M8

Compra 1 (15/01/2025):
  Proveedor: FERRETERÍA XYZ
  Precio: $10,000
  Variación: Primera (gris)
  Compras: 1x

Compra 2 (01/02/2025):
  Proveedor: FERRETERÍA XYZ
  Precio: $12,000
  Variación: ↑ 20.0% (rojo)
  Precio promedio: $11,000
  Compras: 2x

Compra 3 (15/02/2025):
  Proveedor: DISTRIBUIDORA ABC
  Precio: $9,500
  Variación: ↓ 20.8% (verde)
  Precio promedio: $10,500
  Compras: 3x

En el historial:
  - Precio mínimo: $9,500
  - Precio máximo: $12,000
  - Precio promedio: $10,500
  - Total compras: 3
```

---

## ✅ Checklist de Verificación

- [ ] Migración ejecutada (`alembic upgrade head`)
- [ ] Verificado estado (`alembic current`)
- [ ] Cargada factura DIAN de prueba
- [ ] Veo columnas nuevas en tab PRODUCTOS
- [ ] Badges de variación funcionan
- [ ] Modal de historial muestra estadísticas
- [ ] (Opcional) Productos existentes migrados

---

## 🎯 Beneficios Clave

1. **Visibilidad** - Saber exactamente qué, cuándo, dónde y a qué precio
2. **Control** - Detectar cambios de precio inmediatamente
3. **Negociación** - Datos históricos para mejores precios
4. **Planificación** - Predecir costos futuros
5. **Auditoría** - Trazabilidad completa

---

## 📞 Soporte

**Documentación completa:**
- `EJECUTAR_TRAZABILIDAD.md` - Guía paso a paso
- `OPCION_A_TRAZABILIDAD_IMPLEMENTADA.md` - Detalles técnicos
- `RESUMEN_COMPLETO_TRAZABILIDAD.md` - Visión general

**Scripts de ayuda:**
- `COMANDOS_RAPIDOS.sh` - Menú interactivo
- `quick_test_migration.py` - Prueba rápida

---

**¡Sistema listo para usar!** 🎉

Ejecuta `alembic upgrade head` y empieza a cargar facturas.
