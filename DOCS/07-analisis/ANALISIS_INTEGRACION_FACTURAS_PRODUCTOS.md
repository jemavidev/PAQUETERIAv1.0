# 📊 Análisis y Propuesta de Integración: Facturas de Proveedores y Productos

**Fecha:** 15 de Enero, 2026  
**Objetivo:** Integrar completamente el sistema de facturas de proveedores con el catálogo de productos

---

## 🎯 ENTENDIMIENTO DEL PROBLEMA

### Contexto Actual

Tienes **DOS SISTEMAS SEPARADOS** que hablan de lo mismo pero no están conectados:

1. **Sistema de Productos** (`products` table)
   - Productos sincronizados desde DynamiaERP
   - Catálogo de lo que vendes
   - Precios, existencias, clasificación

2. **Sistema de Facturas** (`invoices`, `invoice_items` tables)
   - Facturas de compra a proveedores
   - Items comprados (productos)
   - Precios de compra, IVA, totales

3. **Sistema de Facturas de Proveedores** (`supplier_invoices` table)
   - PDFs originales de proveedores
   - Extracción de CUFE
   - Descarga de DIAN
   - **NO ESTÁ CONECTADO** con los otros dos

### El Problema

**Los 3 sistemas hablan de LO MISMO pero no se comunican:**

```
PDF Proveedor → CUFE → PDF DIAN → Factura Procesada → Items Comprados
                                                           ↓
                                                      ¿Son productos del catálogo?
                                                      ¿Los compró Papyrus (NIT 901210008)?
                                                      ¿Cuál es la trazabilidad completa?
```

---

## 🔍 ANÁLISIS DE LA SITUACIÓN ACTUAL

### ✅ Lo que SÍ funciona

1. **Extracción de CUFE** de PDFs de proveedores
2. **Generación de link DIAN** para descargar PDF oficial
3. **Procesamiento de facturas** desde PDF DIAN
4. **Extracción de items** (productos) de facturas
5. **Sincronización de productos** desde DynamiaERP
6. **Almacenamiento en S3** de PDFs

### ❌ Lo que NO funciona

1. **NO hay relación** entre `supplier_invoices` y `invoices`
   - Cuando procesas un PDF DIAN, no sabes de qué `supplier_invoice` vino

2. **NO hay relación** entre `invoice_items` y `products`
   - Cuando compras un producto, no sabes si está en tu catálogo
   - No puedes comparar precio de compra vs precio de venta

3. **NO hay validación** de que el comprador sea Papyrus (NIT 901210008)
   - Cualquier factura se procesa sin verificar el NIT del comprador

4. **NO hay trazabilidad completa**
   - No puedes saber: "Este producto del catálogo, ¿cuándo lo compramos? ¿A qué precio? ¿De qué proveedor?"

5. **PDFs no accesibles**
   - Según tu reporte, no puedes ver los PDFs guardados

---

## 🎯 OBJETIVOS DE LA INTEGRACIÓN

### 1. Trazabilidad Completa del CUFE

```
supplier_invoice (PDF original)
    ↓ (cufe)
invoice (Factura procesada DIAN)
    ↓ (items)
invoice_items (Productos comprados)
    ↓ (codigo)
products (Catálogo)
```

### 2. Validación de Comprador (Papyrus)

- Toda factura debe tener `buyer_nit = "901210008"`
- Si no es Papyrus → Marcar como **IRREGULARIDAD**

### 3. Relación Productos Comprados ↔ Catálogo

- Cada `invoice_item` debe intentar vincularse con `product`
- Si no existe en catálogo → Marcar como **IRREGULARIDAD**

### 4. Acceso a PDFs

- Ver PDF original del proveedor
- Ver PDF oficial de DIAN
- Ambos desde la interfaz

---

## 📋 CAMBIOS NECESARIOS

### FASE 1: Modelo de Datos (Base de Datos)

#### 1.1. Agregar campos a `invoices`

```python
class Invoice(Base):
    # ... campos existentes ...
    
    # NUEVO: Relación con supplier_invoice
    supplier_invoice_id = Column(Integer, ForeignKey("supplier_invoices.id"), nullable=True, index=True)
    supplier_invoice = relationship("SupplierInvoice", back_populates="processed_invoice")
    
    # NUEVO: Datos del comprador (Papyrus)
    buyer_nit = Column(String(20), nullable=True, index=True)
    buyer_razon_social = Column(String(255), nullable=True)
    
    # NUEVO: Validación de comprador
    is_papyrus_buyer = Column(Boolean, default=False, index=True)
```

#### 1.2. Agregar relación inversa a `supplier_invoices`

```python
class SupplierInvoice(Base):
    # ... campos existentes ...
    
    # MODIFICAR: Relación bidireccional
    processed_invoice = relationship("Invoice", back_populates="supplier_invoice", uselist=False)
```

#### 1.3. Agregar campos a `invoice_items`

```python
class InvoiceItem(Base):
    # ... campos existentes ...
    
    # NUEVO: Relación con producto del catálogo
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    product = relationship("Product")
    
    # NUEVO: Indicador de match
    matched_with_catalog = Column(Boolean, default=False, index=True)
    match_confidence = Column(Float, default=0.0)  # 0.0 a 1.0
    match_method = Column(String(50), nullable=True)  # 'codigo', 'codigo_barra', 'nombre', 'manual'
```

#### 1.4. Nueva tabla de irregularidades específicas

```python
class IrregularityType(enum.Enum):
    # ... existentes ...
    COMPRADOR_NO_ES_PAPYRUS = "comprador_no_es_papyrus"
    PRODUCTO_NO_EN_CATALOGO = "producto_no_en_catalogo"
    PRECIO_COMPRA_MAYOR_VENTA = "precio_compra_mayor_venta"
```

### FASE 2: Extracción de Datos del Comprador

#### 2.1. Modificar `PDFExtractorService`

```python
class ExtractedInvoiceData:
    # ... campos existentes ...
    
    # NUEVO: Datos del comprador
    buyer_nit: str = None
    buyer_razon_social: str = None
    buyer_direccion: str = None
```

#### 2.2. Extraer datos del comprador del PDF

```python
def extract_buyer_info(self, text: str) -> Dict:
    """Extrae información del comprador (Papyrus)"""
    # Buscar sección "Adquiriente" o "Comprador"
    # Extraer NIT, razón social, dirección
    pass
```

### FASE 3: Validación de Comprador

#### 3.1. Validar que el comprador sea Papyrus

```python
def validate_buyer(self, data: ExtractedInvoiceData) -> Tuple[bool, str]:
    """Valida que el comprador sea Papyrus"""
    PAPYRUS_NIT = "901210008"
    
    buyer_nit_clean = self.normalize_nit(data.buyer_nit)
    
    if buyer_nit_clean != PAPYRUS_NIT:
        return False, f"Comprador {buyer_nit_clean} no es Papyrus ({PAPYRUS_NIT})"
    
    return True, "Comprador válido"
```

### FASE 4: Matching de Productos

#### 4.1. Servicio de matching

```python
class ProductMatchingService:
    """Servicio para vincular items de facturas con productos del catálogo"""
    
    def match_item_with_product(self, item: InvoiceItem) -> Tuple[Optional[Product], float, str]:
        """
        Intenta vincular un item con un producto del catálogo.
        
        Returns:
            (producto, confianza, método)
        """
        # Método 1: Por código exacto
        if item.codigo:
            product = self.db.query(Product).filter(
                Product.codigo == item.codigo
            ).first()
            if product:
                return product, 1.0, 'codigo'
        
        # Método 2: Por código de barras
        if item.codigo:
            product = self.db.query(Product).filter(
                Product.codigo_barra == item.codigo
            ).first()
            if product:
                return product, 0.95, 'codigo_barra'
        
        # Método 3: Por nombre (fuzzy matching)
        if item.descripcion:
            # Búsqueda de texto completo
            products = self.db.query(Product).filter(
                Product.nombre.ilike(f'%{item.descripcion[:50]}%')
            ).limit(5).all()
            
            if products:
                # Calcular similitud
                best_match = None
                best_score = 0.0
                
                for product in products:
                    score = self._calculate_similarity(item.descripcion, product.nombre)
                    if score > best_score and score > 0.7:  # Umbral 70%
                        best_match = product
                        best_score = score
                
                if best_match:
                    return best_match, best_score, 'nombre'
        
        return None, 0.0, None
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud entre dos textos (Levenshtein, etc.)"""
        # Implementar algoritmo de similitud
        pass
```

### FASE 5: Flujo Completo Integrado

#### 5.1. Nuevo flujo de procesamiento

```python
def process_supplier_invoice_complete(
    self,
    supplier_invoice_id: int,
    dian_pdf_path: str,
    user_id: int = None
) -> Tuple[Invoice, List[Dict]]:
    """
    Procesa una factura de proveedor de forma completa:
    1. Extrae datos del PDF DIAN
    2. Valida comprador (Papyrus)
    3. Crea factura
    4. Vincula items con productos del catálogo
    5. Detecta irregularidades
    6. Actualiza supplier_invoice
    """
    
    # 1. Extraer datos
    extracted, warnings = self.extractor.extract_from_pdf(dian_pdf_path)
    
    # 2. Validar comprador
    is_papyrus, buyer_msg = self.validate_buyer(extracted)
    
    # 3. Crear factura
    invoice = self.save_invoice(
        data=extracted,
        user_id=user_id,
        supplier_invoice_id=supplier_invoice_id,
        buyer_nit=extracted.buyer_nit,
        buyer_razon_social=extracted.buyer_razon_social,
        is_papyrus_buyer=is_papyrus
    )
    
    # 4. Vincular items con productos
    matching_service = ProductMatchingService(self.db)
    match_results = []
    
    for item in invoice.items:
        product, confidence, method = matching_service.match_item_with_product(item)
        
        if product:
            item.product_id = product.id
            item.matched_with_catalog = True
            item.match_confidence = confidence
            item.match_method = method
            
            match_results.append({
                'item_id': item.id,
                'product_id': product.id,
                'confidence': confidence,
                'method': method
            })
        else:
            # Crear irregularidad
            irregularity = InvoiceIrregularity(
                invoice_id=invoice.id,
                item_id=item.id,
                tipo=IrregularityType.PRODUCTO_NO_EN_CATALOGO.value,
                severidad=IrregularitySeverity.WARNING.value,
                descripcion=f"Producto '{item.descripcion}' no encontrado en catálogo"
            )
            self.db.add(irregularity)
    
    # 5. Crear irregularidad si no es Papyrus
    if not is_papyrus:
        irregularity = InvoiceIrregularity(
            invoice_id=invoice.id,
            tipo=IrregularityType.COMPRADOR_NO_ES_PAPYRUS.value,
            severidad=IrregularitySeverity.ERROR.value,
            descripcion=buyer_msg
        )
        self.db.add(irregularity)
    
    # 6. Actualizar supplier_invoice
    supplier_invoice = self.db.query(SupplierInvoice).get(supplier_invoice_id)
    supplier_invoice.status = SupplierInvoiceStatus.PROCESSED
    supplier_invoice.processed_invoice_id = invoice.id
    supplier_invoice.processed_at = datetime.now()
    
    self.db.commit()
    
    return invoice, match_results
```

### FASE 6: Interfaz de Usuario

#### 6.1. Vista de factura con trazabilidad completa

```html
<!-- supplier_invoices.html -->
<div class="invoice-traceability">
    <h3>Trazabilidad Completa</h3>
    
    <!-- PDF Original -->
    <div class="trace-step">
        <span class="badge">1</span>
        <strong>PDF Original del Proveedor</strong>
        <a href="/api/supplier-invoices/{{ invoice.supplier_invoice_id }}/pdf" target="_blank">
            <i class="fas fa-file-pdf"></i> Ver PDF
        </a>
        <p>Subido: {{ invoice.supplier_invoice.uploaded_at }}</p>
        <p>CUFE: {{ invoice.supplier_invoice.cufe_short }}</p>
    </div>
    
    <!-- PDF DIAN -->
    <div class="trace-step">
        <span class="badge">2</span>
        <strong>PDF Oficial DIAN</strong>
        <a href="/api/invoices/{{ invoice.id }}/view-pdf" target="_blank">
            <i class="fas fa-file-pdf"></i> Ver PDF
        </a>
        <p>Descargado: {{ invoice.supplier_invoice.dian_downloaded_at }}</p>
    </div>
    
    <!-- Factura Procesada -->
    <div class="trace-step">
        <span class="badge">3</span>
        <strong>Factura Procesada</strong>
        <p>Proveedor: {{ invoice.supplier.razon_social }}</p>
        <p>Comprador: {{ invoice.buyer_razon_social }}</p>
        {% if invoice.is_papyrus_buyer %}
            <span class="badge badge-success">✓ Papyrus</span>
        {% else %}
            <span class="badge badge-danger">✗ No es Papyrus</span>
        {% endif %}
    </div>
    
    <!-- Items / Productos -->
    <div class="trace-step">
        <span class="badge">4</span>
        <strong>Productos Comprados</strong>
        <table>
            <thead>
                <tr>
                    <th>Código</th>
                    <th>Descripción</th>
                    <th>Cantidad</th>
                    <th>Precio Compra</th>
                    <th>En Catálogo</th>
                    <th>Precio Venta</th>
                    <th>Margen</th>
                </tr>
            </thead>
            <tbody>
                {% for item in invoice.items %}
                <tr>
                    <td>{{ item.codigo }}</td>
                    <td>{{ item.descripcion }}</td>
                    <td>{{ item.cantidad }}</td>
                    <td>${{ item.precio_unitario|number_format }}</td>
                    <td>
                        {% if item.matched_with_catalog %}
                            <span class="badge badge-success">
                                ✓ {{ item.match_confidence * 100 }}%
                            </span>
                            <a href="/products/{{ item.product_id }}">Ver</a>
                        {% else %}
                            <span class="badge badge-warning">✗ No encontrado</span>
                        {% endif %}
                    </td>
                    <td>
                        {% if item.product %}
                            ${{ item.product.precio_venta|number_format }}
                        {% else %}
                            -
                        {% endif %}
                    </td>
                    <td>
                        {% if item.product %}
                            {% set margen = ((item.product.precio_venta - item.precio_unitario) / item.precio_unitario * 100) %}
                            <span class="{% if margen > 0 %}text-success{% else %}text-danger{% endif %}">
                                {{ margen|round(1) }}%
                            </span>
                        {% else %}
                            -
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

### FASE 7: Endpoints API

#### 7.1. Nuevos endpoints

```python
# Ver PDF original de supplier_invoice
@router.get("/api/supplier-invoices/{id}/pdf")
async def get_supplier_invoice_pdf(id: int):
    """Retorna el PDF original del proveedor"""
    pass

# Ver PDF DIAN de factura procesada
@router.get("/api/invoices/{id}/view-pdf")
async def view_invoice_pdf(id: int):
    """Retorna el PDF oficial de DIAN"""
    pass

# Procesar supplier_invoice completo
@router.post("/api/supplier-invoices/{id}/process-complete")
async def process_supplier_invoice_complete(id: int, dian_pdf: UploadFile):
    """Procesa una supplier_invoice con el PDF de DIAN"""
    pass

# Vincular item con producto manualmente
@router.post("/api/invoice-items/{item_id}/link-product")
async def link_item_to_product(item_id: int, product_id: int):
    """Vincula manualmente un item con un producto del catálogo"""
    pass

# Análisis de compras de un producto
@router.get("/api/products/{id}/purchase-history")
async def get_product_purchase_history(id: int):
    """Obtiene historial de compras de un producto"""
    pass
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Semana 1: Base de Datos y Modelos
- [ ] Migración: Agregar campos a `invoices`
- [ ] Migración: Agregar campos a `invoice_items`
- [ ] Migración: Agregar nuevos tipos de irregularidades
- [ ] Actualizar modelos SQLAlchemy

### Semana 2: Extracción y Validación
- [ ] Modificar `PDFExtractorService` para extraer datos del comprador
- [ ] Implementar validación de comprador (Papyrus)
- [ ] Crear `ProductMatchingService`
- [ ] Implementar algoritmo de matching

### Semana 3: Integración Completa
- [ ] Modificar `InvoiceService.save_invoice()` para incluir validaciones
- [ ] Crear `process_supplier_invoice_complete()`
- [ ] Implementar vinculación automática de items con productos
- [ ] Crear irregularidades automáticas

### Semana 4: Interfaz y Endpoints
- [ ] Crear vista de trazabilidad completa
- [ ] Implementar endpoints de PDFs
- [ ] Agregar columnas de matching en tablas
- [ ] Dashboard con estadísticas de matching

### Semana 5: Testing y Ajustes
- [ ] Probar con facturas reales
- [ ] Ajustar algoritmo de matching
- [ ] Optimizar consultas
- [ ] Documentación

---

## 📊 BENEFICIOS DE LA INTEGRACIÓN

### 1. Trazabilidad Completa
- Sabes exactamente de dónde viene cada dato
- PDF original → CUFE → PDF DIAN → Factura → Items → Productos

### 2. Control de Compras
- Solo facturas a nombre de Papyrus
- Alertas automáticas si no es Papyrus

### 3. Análisis de Rentabilidad
- Precio de compra vs precio de venta
- Margen de ganancia por producto
- Proveedores más económicos

### 4. Gestión de Catálogo
- Productos comprados que no están en catálogo
- Sugerencias de nuevos productos
- Actualización de precios de compra

### 5. Auditoría y Compliance
- Todos los PDFs accesibles
- Trazabilidad completa
- Irregularidades documentadas

---

## ❓ PREGUNTAS PARA TI

1. **¿Dónde están los PDFs actualmente?**
   - ¿En S3? ¿Localmente? ¿No se están guardando?

2. **¿Qué tan importante es el matching automático?**
   - ¿Prefieres manual o automático?
   - ¿Qué nivel de confianza mínimo?

3. **¿Qué hacer con facturas que no son de Papyrus?**
   - ¿Rechazar? ¿Marcar como irregularidad? ¿Permitir?

4. **¿Qué hacer con productos no encontrados en catálogo?**
   - ¿Crear automáticamente? ¿Marcar para revisión? ¿Ignorar?

5. **¿Prioridad de implementación?**
   - ¿Qué fase es más urgente?

---

## 🎯 RECOMENDACIÓN

**Implementar en este orden:**

1. **URGENTE:** Arreglar acceso a PDFs (Fase 6 parcial)
2. **ALTA:** Agregar campos de comprador y validación (Fases 1-3)
3. **MEDIA:** Matching de productos (Fases 4-5)
4. **BAJA:** Interfaz completa de trazabilidad (Fase 6 completa)

---

**¿Tienes dudas? ¿Quieres que empiece con alguna fase específica?**
