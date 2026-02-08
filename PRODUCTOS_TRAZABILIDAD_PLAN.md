# 📊 Sistema de Trazabilidad de Productos - Plan Completo

## 🎯 Objetivo
Crear un sistema completo de trazabilidad de productos que permita:
- Saber dónde, cuándo y a qué precio se compró cada producto
- Comparar precios entre compras y proveedores
- Detectar variaciones de precio (subidas/bajadas)
- Calcular promedios históricos
- Tomar decisiones informadas de compra

---

## ✅ Fase 1: Mejorar Extracción de Productos (COMPLETADO)

### Cambios en `pdf_parser_service.py`
- ✅ Mejorado método `_extract_productos()` para extraer:
  - Código de producto (EAN/UPC o alfanumérico)
  - Descripción completa
  - Cantidad
  - Precio unitario
  - IVA %
  - Total del item
  - Unidad de medida (si disponible)

### Mejoras implementadas:
- Búsqueda más flexible de sección de productos (3 patrones diferentes)
- Extracción de valores monetarios mejorada
- Detección de cantidad, IVA y precios
- Límite aumentado a 100 productos por factura
- Logging mejorado

---

## 🚀 Fase 2: Enriquecer Datos de Productos (SIGUIENTE)

### 2.1 Agregar Campos Calculados al Modelo

**Campos a agregar en `InvoiceProductV2`:**
```python
# Trazabilidad y análisis
proveedor_nombre = Column(String(255), nullable=True)  # Denormalizado para queries rápidas
precio_anterior = Column(Numeric(15, 2), nullable=True)  # Última compra
variacion_precio = Column(Numeric(10, 2), nullable=True)  # % de cambio
variacion_tipo = Column(String(20), nullable=True)  # 'subio', 'bajo', 'igual'
precio_promedio = Column(Numeric(15, 2), nullable=True)  # Promedio histórico
total_compras_producto = Column(Integer, default=0)  # Contador
ultimo_proveedor = Column(String(255), nullable=True)  # Para comparar
dias_desde_ultima_compra = Column(Integer, nullable=True)  # Frecuencia
```

### 2.2 Crear Función de Cálculo de Trazabilidad

**Nueva función en `invoice_v2_service.py`:**
```python
def calculate_product_traceability(self, producto: InvoiceProductV2):
    """
    Calcula datos de trazabilidad para un producto
    - Precio anterior
    - Variación de precio
    - Precio promedio
    - Total de compras
    - Días desde última compra
    """
    # Buscar compras anteriores del mismo código
    # Calcular variaciones
    # Actualizar campos
```

### 2.3 Actualizar Proceso de Carga DIAN

**Modificar `process_dian_document()` para:**
1. Extraer productos del PDF
2. Para cada producto:
   - Buscar historial de compras anteriores
   - Calcular trazabilidad
   - Guardar con datos enriquecidos

---

## 📈 Fase 3: Endpoints de Análisis (FUTURO)

### 3.1 Endpoint: Historial de Precios
```
GET /api/v2/invoices/productos/{codigo}/price-history
```
Retorna:
- Lista de todas las compras con fecha, proveedor, precio
- Gráfica de evolución de precios
- Precio mínimo, máximo, promedio

### 3.2 Endpoint: Comparativa de Proveedores
```
GET /api/v2/invoices/productos/{codigo}/compare-suppliers
```
Retorna:
- Precio por proveedor
- Frecuencia de compra por proveedor
- Mejor proveedor (precio/calidad)

### 3.3 Endpoint: Productos con Mayor Variación
```
GET /api/v2/invoices/productos/price-alerts
```
Retorna:
- Productos con variación > X%
- Productos con precio anormal
- Recomendaciones de compra

### 3.4 Endpoint: Análisis de Ahorro
```
GET /api/v2/invoices/productos/savings-analysis
```
Retorna:
- Ahorro/sobrecosto vs precio promedio
- Mejores y peores compras
- Oportunidades de ahorro

---

## 🎨 Fase 4: Mejoras en UI (FUTURO)

### 4.1 Tab PRODUCTOS - Columnas Adicionales
- Precio anterior
- Variación (% y flecha ↑↓→)
- Precio promedio
- Total compras
- Último proveedor

### 4.2 Modal de Historial Mejorado
- Gráfica de evolución de precios
- Tabla comparativa de proveedores
- Estadísticas (min, max, promedio)
- Alertas de precio

### 4.3 Dashboard de Productos (Nueva Vista)
- Top 10 productos más comprados
- Top 10 con mayor variación de precio
- Alertas de precios anormales
- Gráficas de tendencias

---

## 📊 Fase 5: Reportes y Exportación (FUTURO)

### 5.1 Reportes Automáticos
- Reporte mensual de compras
- Análisis de variación de precios
- Comparativa de proveedores
- Oportunidades de ahorro

### 5.2 Exportación Avanzada
- CSV con datos de trazabilidad
- Excel con gráficas
- PDF con análisis completo

---

## 🔧 Implementación Técnica

### Prioridad 1 (Inmediato):
1. ✅ Mejorar extracción de productos del PDF
2. ⏳ Agregar campos de trazabilidad al modelo
3. ⏳ Crear migración de base de datos
4. ⏳ Implementar cálculo de trazabilidad
5. ⏳ Actualizar proceso de carga DIAN

### Prioridad 2 (Corto plazo):
6. Mejorar endpoint de productos con datos de trazabilidad
7. Actualizar UI del tab PRODUCTOS
8. Mejorar modal de historial

### Prioridad 3 (Mediano plazo):
9. Crear endpoints de análisis
10. Crear dashboard de productos
11. Implementar alertas de precio

### Prioridad 4 (Largo plazo):
12. Reportes automáticos
13. Exportación avanzada
14. Integración con sistema de compras

---

## 📝 Notas Técnicas

### Consideraciones:
- **Denormalización**: Guardar `proveedor_nombre` en productos para queries rápidas
- **Índices**: Crear índices en `codigo_producto`, `fecha_compra`, `proveedor_nombre`
- **Performance**: Calcular trazabilidad solo al insertar/actualizar, no en cada query
- **Caché**: Considerar caché para estadísticas y análisis frecuentes

### Migración de Datos Existentes:
- Recalcular trazabilidad para productos ya existentes
- Script de migración para llenar campos nuevos
- Validar integridad de datos

---

## 🎯 Beneficios Esperados

1. **Visibilidad Total**: Saber exactamente qué, cuándo, dónde y a qué precio se compró
2. **Control de Costos**: Detectar sobrecostos y oportunidades de ahorro
3. **Negociación**: Datos para negociar mejores precios con proveedores
4. **Planificación**: Predecir costos futuros basados en históricos
5. **Auditoría**: Trazabilidad completa para auditorías y reportes

---

**Estado Actual**: Fase 1 completada ✅
**Siguiente Paso**: Implementar Fase 2 - Campos de trazabilidad
