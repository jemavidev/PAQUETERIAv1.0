# ¿Qué Información Necesitas para PAQUETEX?

## 📊 Información Completa Disponible

He analizado la API de DynamiaERP y estos son **TODOS** los datos que puedo obtener de cada producto:

### 🎯 CATEGORÍA 1: Información Básica del Producto
- ✅ **ID único** del producto
- ✅ **Código** del producto
- ✅ **Nombre** completo
- ✅ **Descripción** detallada
- ✅ **Referencia**
- ✅ **Código de barras**
- ✅ **Código de referencia**
- ✅ **Referencia externa**

### 💰 CATEGORÍA 2: Precios y Costos
- ✅ **Precio de venta** al público
- ✅ **Costo aproximado**
- ✅ **Costo efectivo**
- ✅ **Impuesto incluido** (sí/no)
- ✅ **Porcentaje de impuesto** (ej: 19%)
- ✅ **Exento de impuestos** (sí/no)
- ✅ **Precio fijo** (sí/no)
- ✅ **Tiene precio temporal** (sí/no)

### 📦 CATEGORÍA 3: Inventario y Stock
- ✅ **Existencias totales**
- ✅ **Existencias mínimas**
- ✅ **Existencias máximas**
- ✅ **Existencias externas**

### 🏷️ CATEGORÍA 4: Clasificación
- ✅ **Tipo** de producto (PRODUCTO, SERVICIO, etc.)
  - ID del tipo
  - Nombre del tipo
- ✅ **Marca** del producto
  - ID de la marca
  - Nombre de la marca
- ✅ **Línea/Categoría** del producto
  - ID de la línea
  - Nombre de la línea (ej: "PAPELERIA / ESCOLAR")

### ✅ CATEGORÍA 5: Estados y Configuraciones
- ✅ **Activo** (sí/no) - Si el producto está activo
- ✅ **Vendible** (sí/no) - Si se puede vender
- ✅ **Comprable** (sí/no) - Si se puede comprar
- ✅ **Trasladable** (sí/no) - Si se puede trasladar
- ✅ **Visible en web** (sí/no)
- ✅ **Destacado** (sí/no) - Si es producto destacado

### 🛒 CATEGORÍA 6: Configuración de Ventas
- ✅ **Cantidad por defecto** en ventas
- ✅ **Permite descuentos** (sí/no)
- ✅ **Porcentaje de descuento**
- ✅ **Bloquear descuentos** (sí/no)
- ✅ **Modo de precio** (POR_DEFECTO, etc.)
- ✅ **Orden en ventas**

### 🍽️ CATEGORÍA 7: Domicilios y Delivery
- ✅ **Aplica para domicilios** (sí/no)
- ✅ **Para llevar** (sí/no)
- ✅ **Bebida alcohólica** (sí/no)

### 💼 CATEGORÍA 8: Comisiones
- ✅ **Comisionable** (sí/no)
- ✅ **Porcentaje de comisión**
- ✅ **Descontar en comisiones** (sí/no)

### 🔧 CATEGORÍA 9: Configuraciones Avanzadas
- ✅ **Producto compuesto** (sí/no)
- ✅ **Múltiples presentaciones** (sí/no)
- ✅ **Usa números de serie** (sí/no)
- ✅ **Usa balanza** (sí/no)
- ✅ **Usa lotes automáticos** (sí/no)
- ✅ **Permite pedidos** (sí/no)

### 📅 CATEGORÍA 10: Auditoría
- ✅ **Fecha de creación**
- ✅ **Hora de creación**
- ✅ **Usuario creador**
- ✅ **Última actualización**
- ✅ **Fecha con zona horaria**

---

## 🎯 AHORA DIME: ¿Qué Necesitas para PAQUETEX?

Por favor, indica qué información quieres mostrar en PAQUETEX. Puedes elegir:

### Opción A: Información Mínima (Catálogo Básico)
```
□ ID del producto
□ Código
□ Nombre
□ Precio de venta
□ Estado (activo/inactivo)
```

### Opción B: Información Estándar (Recomendada)
```
□ ID del producto
□ Código
□ Nombre
□ Descripción
□ Precio de venta
□ Costo aproximado
□ Impuesto (%)
□ Marca
□ Categoría/Línea
□ Existencias
□ Estado (activo/vendible)
```

### Opción C: Información Completa
```
□ Toda la información básica
□ Precios y costos detallados
□ Inventario completo
□ Clasificación completa
□ Configuraciones de venta
□ Estados y permisos
□ Auditoría
```

### Opción D: Personalizada
Dime exactamente qué campos necesitas de las categorías arriba.

---

## 💡 Preguntas para Definir la Implementación

### 1. ¿Qué quieres hacer con los productos en PAQUETEX?

- [ ] **Solo visualizarlos** (catálogo de consulta)
- [ ] **Usarlos en ventas** (seleccionar productos al vender)
- [ ] **Gestionar inventario** (control de stock)
- [ ] **Crear paquetes** (combinar productos)
- [ ] **Otro:** _________________

### 2. ¿Dónde quieres mostrar los productos?

- [ ] **Página de catálogo** (lista de productos)
- [ ] **Selector en ventas** (al crear una venta)
- [ ] **Dashboard** (productos destacados)
- [ ] **Búsqueda** (buscador de productos)
- [ ] **Otro:** _________________

### 3. ¿Qué filtros necesitas?

- [ ] Por **categoría/línea**
- [ ] Por **marca**
- [ ] Por **precio** (rango)
- [ ] Por **existencias** (disponibles/agotados)
- [ ] Por **estado** (activos/inactivos)
- [ ] **Búsqueda por nombre o código**
- [ ] Otro: _________________

### 4. ¿Necesitas sincronización automática?

- [ ] **Sí** - Sincronizar productos automáticamente cada X tiempo
- [ ] **No** - Sincronizar manualmente cuando sea necesario
- [ ] **Parcial** - Solo sincronizar productos específicos

### 5. ¿Qué acciones quieres hacer con los productos?

- [ ] **Ver detalles** del producto
- [ ] **Agregar a venta** directamente
- [ ] **Editar** información local
- [ ] **Marcar como favorito**
- [ ] **Exportar** a Excel/PDF
- [ ] Otro: _________________

---

## 📋 Ejemplo de Casos de Uso

### Caso 1: Catálogo Simple
**Necesitas:**
- Nombre, código, precio, existencias
- Búsqueda por nombre
- Filtro por categoría
- Botón "Agregar a venta"

### Caso 2: Gestión de Inventario
**Necesitas:**
- Toda la información de inventario
- Existencias actuales, mínimas, máximas
- Alertas de stock bajo
- Historial de movimientos

### Caso 3: Punto de Venta
**Necesitas:**
- Búsqueda rápida por código/nombre
- Precio, impuestos
- Existencias disponibles
- Agregar a venta con cantidad

### Caso 4: E-commerce/Catálogo Web
**Necesitas:**
- Nombre, descripción, precio
- Imágenes (si están disponibles)
- Categoría, marca
- Productos destacados
- Filtros avanzados

---

## 🚀 Próximos Pasos

Una vez me digas qué necesitas, puedo:

1. ✅ **Crear el modelo de base de datos** con los campos que necesites
2. ✅ **Crear el servicio de sincronización** para traer los productos
3. ✅ **Crear los endpoints de API** para consultar productos
4. ✅ **Crear las vistas HTML** para mostrar los productos
5. ✅ **Implementar búsqueda y filtros**
6. ✅ **Integrar con el sistema de ventas** existente

---

## 📝 Plantilla de Respuesta

Copia y completa esto para que sepa exactamente qué necesitas:

```
INFORMACIÓN QUE NECESITO:
□ Opción A / B / C / D (marca una)

CAMPOS ESPECÍFICOS (si elegiste D):
- Campo 1: _________________
- Campo 2: _________________
- Campo 3: _________________
...

USO PRINCIPAL:
□ Visualizar / Vender / Inventario / Otro: _________________

UBICACIÓN EN PAQUETEX:
□ Catálogo / Ventas / Dashboard / Otro: _________________

FILTROS NECESARIOS:
□ Categoría / Marca / Precio / Búsqueda / Otro: _________________

SINCRONIZACIÓN:
□ Automática / Manual / Parcial

ACCIONES:
□ Ver detalles / Agregar a venta / Editar / Otro: _________________

NOTAS ADICIONALES:
_________________
```

---

**¡Dime qué necesitas y lo implemento!** 🚀
