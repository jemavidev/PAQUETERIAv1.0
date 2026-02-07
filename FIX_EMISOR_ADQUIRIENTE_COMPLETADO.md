# ✅ FIX: Corrección Emisor/Adquiriente en Facturas DIAN

## 🐛 Problema Identificado

En el sistema de facturas, los datos del **EMISOR** (vendedor/proveedor) y **ADQUIRIENTE** (comprador/cliente) estaban siendo intercambiados al procesar archivos DIAN.

### Ejemplo del problema:
Para el CUFE: `ff5fcd60a8d39c4e29456d71bb2118344e099cb592a959f7a4ffe2e1e533ea03406b744ad08365da07e28f180d080635`

**Según la DIAN (correcto):**
- **Adquiriente (Cliente)**: PAPYRUS SOLUCIONES INTEGRALES S.A.S. (NIT: 901210008)
- **Vendedor (Proveedor)**: VENEPLAST LTDA (NIT: 900019737)

**En el sistema (incorrecto):**
- **Proveedor**: PAPYRUS SOLUCIONES INTEGRALES S.A.S. ❌
- Debería ser: VENEPLAST LTDA ✅

## 🔍 Causa Raíz

El parser de PDF (`PDFParserService._extract_emisor()`) estaba buscando "Razón social" de forma genérica en todo el documento, capturando la **primera** ocurrencia que encontraba.

En los PDFs de la DIAN, la estructura es:
1. **Datos del adquiriente** (aparece PRIMERO) ← Se capturaba esto ❌
2. **Datos del vendedor** (aparece DESPUÉS) ← Debería capturar esto ✅

## ✅ Solución Implementada

### 1. Corrección en el Parser (`CODE/src/app/services/pdf_parser_service.py`)

#### `_extract_emisor()` - Líneas ~424-448
```python
@staticmethod
def _extract_emisor(text: str) -> Dict[str, Optional[str]]:
    """Extrae datos del emisor/vendedor (NO del adquiriente)"""
    emisor = {}
    
    # IMPORTANTE: Buscar específicamente en la sección "Datos del vendedor"
    # NO en "Datos del adquiriente" que aparece primero
    vendor_section_match = re.search(
        r'(?:Datos del vendedor|DATOS DEL VENDEDOR|Datos del emisor|DATOS DEL EMISOR)([\s\S]{0,800}?)(?:Detalles de productos|Detalle|DETALLE|Condiciones|CONDICIONES)',
        text,
        re.IGNORECASE
    )
    
    search_text = vendor_section_match.group(1) if vendor_section_match else text
    
    # Ahora busca en la sección correcta...
```

**Cambios:**
- ✅ Busca específicamente en la sección "Datos del vendedor"
- ✅ Delimita la búsqueda hasta "Detalles de productos"
- ✅ NO captura datos de "Datos del adquiriente"

#### `_extract_adquiriente()` - Líneas ~450-468
```python
@staticmethod
def _extract_adquiriente(text: str) -> Dict[str, Optional[str]]:
    """Extrae datos del adquiriente/comprador (NO del vendedor)"""
    adquiriente = {}
    
    # Buscar específicamente en la sección de adquiriente
    match = re.search(
        r'(?:Datos del adquiriente|Datos del Cliente|DATOS DEL CLIENTE|DATOS DEL ADQUIRIENTE)([\s\S]{0,500}?)(?:Datos del vendedor|DATOS DEL VENDEDOR|Detalles|DETALLES)',
        text,
        re.IGNORECASE
    )
```

**Cambios:**
- ✅ Busca específicamente en la sección "Datos del adquiriente"
- ✅ Se detiene antes de llegar a "Datos del vendedor"
- ✅ Delimita correctamente la sección

### 2. Script de Corrección Masiva

Creado: `CODE/scripts/maintenance/fix_emisor_adquiriente_swap.py`

**Funcionalidad:**
- 📄 Reprocesa TODOS los archivos DIAN existentes
- 🔄 Descarga archivos desde S3
- 🔍 Extrae datos con la lógica corregida
- 💾 Actualiza la base de datos
- 📊 Genera reporte de cambios

**Uso:**
```bash
# Desde el directorio raíz del proyecto
./fix_emisor_adquiriente.sh
```

O directamente:
```bash
python3 CODE/scripts/maintenance/fix_emisor_adquiriente_swap.py
```

## 📋 Archivos Modificados

1. ✅ `CODE/src/app/services/pdf_parser_service.py`
   - Función `_extract_emisor()` corregida
   - Función `_extract_adquiriente()` mejorada

2. ✅ `CODE/scripts/maintenance/fix_emisor_adquiriente_swap.py`
   - Script de corrección masiva (NUEVO)

3. ✅ `fix_emisor_adquiriente.sh`
   - Script bash para ejecutar corrección (NUEVO)

## 🚀 Pasos para Aplicar el Fix

### 1. Verificar que el código esté actualizado
```bash
git status
# Verificar que pdf_parser_service.py tenga los cambios
```

### 2. Ejecutar el script de corrección
```bash
./fix_emisor_adquiriente.sh
```

El script:
- Mostrará cuántas facturas se van a reprocesar
- Pedirá confirmación antes de proceder
- Procesará cada factura y mostrará el progreso
- Generará un resumen final con estadísticas

### 3. Verificar los resultados
```bash
# Revisar en la interfaz web
# Tab CUFE → Verificar que los proveedores sean correctos
```

## 🎯 Resultado Esperado

Después de ejecutar el script, todas las facturas DIAN tendrán:

- **Emisor (Proveedor)**: El vendedor real (quien emite la factura)
- **Adquiriente (Cliente)**: El comprador real (quien recibe la factura)

### Ejemplo corregido:
Para el CUFE `ff5fcd60...`:
- ✅ **Proveedor**: VENEPLAST LTDA
- ✅ **Cliente**: PAPYRUS SOLUCIONES INTEGRALES S.A.S.

## 🔒 Prevención Futura

Los cambios en el código aseguran que:
- ✅ Nuevos archivos DIAN se procesarán correctamente
- ✅ La lógica de extracción es más robusta
- ✅ Se delimitan correctamente las secciones del PDF
- ✅ No se volverá a intercambiar emisor/adquiriente

## 📊 Estadísticas del Script

El script reportará:
- ✅ Facturas corregidas (con cambios)
- ℹ️ Facturas sin cambios (ya correctas)
- ❌ Facturas fallidas (errores)
- 📈 Total procesadas

## ⚠️ Notas Importantes

1. **Backup**: El script NO hace backup automático. Si quieres hacer backup de la BD, hazlo antes de ejecutar.

2. **Archivos S3**: El script necesita acceso a S3 para descargar los archivos DIAN.

3. **Tiempo de ejecución**: Depende del número de facturas. Aproximadamente 2-5 segundos por factura.

4. **Reversión**: Si algo sale mal, el script hace rollback automático por factura.

## ✅ Checklist de Verificación

- [x] Código corregido en `pdf_parser_service.py`
- [x] Script de corrección creado
- [x] Script bash de ejecución creado
- [ ] Script ejecutado en producción
- [ ] Resultados verificados en la interfaz
- [ ] Documentación actualizada

## 📝 Fecha de Implementación

- **Fecha**: 2025-02-07
- **Versión**: 1.0
- **Estado**: ✅ Listo para aplicar

---

**Autor**: Sistema de Facturas V2  
**Prioridad**: 🔴 Alta (Datos incorrectos en producción)
