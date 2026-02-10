# PLAN DE IMPLEMENTACIÓN: XML y PDF Independientes

## 🎯 OBJETIVO
Permitir que el usuario cargue archivos XML o PDF (o ambos) y el sistema los procese de manera independiente y óptima.

## 📋 CAMBIOS A REALIZAR

### 1. REFACTORIZAR PDF PARSER ✅
**Archivo**: `CODE/src/app/services/pdf_parser_service.py`

#### Cambio 1.1: Mejorar `_extract_totales()` (línea ~550)
- Priorizar "Total factura (=)" como valor definitivo
- Buscar en última hoja del PDF
- Estructura idéntica al XML

#### Cambio 1.2: Mejorar extracción de IVA en `_extract_productos()` (línea ~650)
- Implementar 3 estrategias de extracción
- Calcular IVA desde totales si no está explícito

### 2. CREAR DETECTOR DE TIPO DE ARCHIVO ✅
**Archivo**: `CODE/src/app/services/file_detector_service.py` (NUEVO)

```python
class FileDetectorService:
    @staticmethod
    def detect_file_type(file_path: str) -> str:
        """Detecta si es XML o PDF"""
        # Por extensión
        # Por contenido (magic bytes)
        return 'XML' | 'PDF' | 'UNKNOWN'
```

### 3. MEJORAR MODAL DE CARGA ✅
**Archivo**: `CODE/src/templates/invoices_v2/cufe.html`

#### Cambio 3.1: Aceptar XML y PDF
```html
<input type="file" accept=".pdf,.xml" multiple>
```

#### Cambio 3.2: Mostrar tipo de archivo detectado
- Badge visual (XML = verde, PDF = azul)
- Icono diferente por tipo

#### Cambio 3.3: Información al usuario
```
"Puedes cargar archivos XML (recomendado) o PDF de la DIAN"
"El sistema detectará automáticamente el tipo de archivo"
```

### 4. CREAR ENDPOINT PARA XML ✅
**Archivo**: `CODE/src/app/routes/invoices_v2_routes.py`

```python
@router.post("/cufe/{cufe}/upload-dian-xml")
async def upload_dian_xml(cufe: str, file: UploadFile):
    """Procesa archivo XML de la DIAN"""
    pass
```

### 5. ACTUALIZAR SERVICIO PRINCIPAL ✅
**Archivo**: `CODE/src/app/services/invoice_v2_service.py`

#### Cambio 5.1: Nuevo método `process_xml_document()`
```python
def process_xml_document(self, cufe: str, xml_path: str, file_obj=None):
    """Procesa archivo XML de la DIAN"""
    # Usar XMLParserDIAN
    # Actualizar factura con datos XML
    # Subir XML a S3
    pass
```

#### Cambio 5.2: Modificar `process_dian_document()` para detectar tipo
```python
def process_dian_document(self, cufe: str, file_path: str, file_obj=None):
    """Procesa archivo DIAN (XML o PDF automáticamente)"""
    file_type = FileDetectorService.detect_file_type(file_path)
    
    if file_type == 'XML':
        return self.process_xml_document(cufe, file_path, file_obj)
    elif file_type == 'PDF':
        return self.process_pdf_document(cufe, file_path, file_obj)
    else:
        raise ValueError("Tipo de archivo no soportado")
```

### 6. ACTUALIZAR FRONTEND ✅
**Archivo**: `CODE/src/templates/invoices_v2/cufe.html`

#### Cambio 6.1: JavaScript para detectar tipo
```javascript
function detectFileType(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    return ext === 'xml' ? 'XML' : ext === 'pdf' ? 'PDF' : 'UNKNOWN';
}
```

#### Cambio 6.2: Mostrar badge por tipo
```javascript
function renderFileItem(file) {
    const type = detectFileType(file);
    const badge = type === 'XML' 
        ? '<span class="bg-green-100 text-green-800">XML</span>'
        : '<span class="bg-blue-100 text-blue-800">PDF</span>';
    // ...
}
```

## 🚀 ORDEN DE EJECUCIÓN

1. ✅ Refactorizar `_extract_totales()` en PDF Parser
2. ✅ Mejorar extracción de IVA en PDF Parser
3. ✅ Crear `FileDetectorService`
4. ✅ Crear método `process_xml_document()` en servicio
5. ✅ Modificar `process_dian_document()` para detectar tipo
6. ✅ Actualizar modal HTML (aceptar XML y PDF)
7. ✅ Actualizar JavaScript (detectar y mostrar tipo)
8. ✅ Probar con archivos reales

## ⏱️ TIEMPO ESTIMADO
- Refactorizar PDF Parser: 1 hora
- Crear detector y servicios: 45 minutos
- Actualizar modal y frontend: 45 minutos
- Testing: 30 minutos
**TOTAL: ~3 horas**

## ✅ CRITERIOS DE ÉXITO
- ✅ Modal acepta XML y PDF
- ✅ Sistema detecta tipo automáticamente
- ✅ XML se procesa con 100% precisión
- ✅ PDF se procesa con 95%+ precisión
- ✅ Usuario ve badge del tipo de archivo
- ✅ Ambos tipos se suben a S3 correctamente

---
**¿Proceder con la implementación?**
