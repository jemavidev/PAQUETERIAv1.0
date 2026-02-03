# 🔍 Cómo Diagnosticar la Extracción de PDFs

## Problema

Las facturas no están capturando correctamente la información:
- Proveedor aparece como "-"
- Total aparece como "$0"
- Número de factura no se detecta

## Método de Extracción Actual

El sistema usa **2 pasos**:

### 1. Extracción de Texto (pdfplumber)
```python
import pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    text = pdf.pages[0].extract_text()
```

Esto convierte el PDF en texto plano.

### 2. Búsqueda con Regex
```python
# Ejemplo: buscar proveedor
pattern = r'(?:Razón Social)[\s:]+([A-ZÁ-Ú\s&.]+SAS)'
match = re.search(pattern, text)
```

Esto busca patrones específicos en el texto.

## 🛠️ Script de Diagnóstico

Creé un script que te muestra **exactamente** qué está extrayendo:

### Uso:

```bash
cd CODE
python3 diagnostico_extraccion_pdf.py "ruta/al/archivo.pdf"
```

### Ejemplo con tus facturas:

```bash
# Diagnosticar una factura específica
python3 diagnostico_extraccion_pdf.py "CUFE/FACTURAS/ad00454539650892500016306.pdf"

# O cualquier otra
python3 diagnostico_extraccion_pdf.py "CUFE/FACTURAS/FV09006851640112400000125.pdf"
```

### Qué muestra el script:

1. **Texto extraído** (primeros 2000 caracteres)
   - Así puedes ver si el PDF se está leyendo correctamente

2. **Información detectada**
   - ✅ CUFE: 8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad
   - ❌ Proveedor: NO DETECTADO
   - ✅ Total: 24300.00

3. **Búsqueda manual de patrones**
   - Muestra líneas que contienen palabras clave
   - Ejemplo: "Línea 5: Razón Social: PAPYRUS SOLUCIONES INTEGRALES SAS"

4. **Sugerencias**
   - Te dice qué buscar manualmente en el PDF

## 📋 Ejemplo de Salida

```
================================================================================
📄 Analizando: factura_ejemplo.pdf
================================================================================

1️⃣  TEXTO EXTRAÍDO (primeros 2000 caracteres):
--------------------------------------------------------------------------------
FACTURA ELECTRÓNICA DE VENTA
FEV-12345

Razón Social: PAPYRUS SOLUCIONES INTEGRALES SAS
NIT: 900123456-1
Dirección: Calle 123 #45-67

Fecha: 2025-01-15
Número: FEV-12345

Total a pagar: $24.300

... (Total: 5432 caracteres)

================================================================================

2️⃣  INFORMACIÓN DETECTADA:
--------------------------------------------------------------------------------
✅ CUFE                : 8cf8ec5366fa9eaccea38cdffdfa0a7690edbaf31b89adce444ca0a322d19e50a79c86d67e0fbc81609dc9451975f0ad
✅ Proveedor           : PAPYRUS SOLUCIONES INTEGRALES SAS
✅ NIT                 : 900123456-1
✅ Fecha               : 2025-01-15 00:00:00
✅ Número Factura      : FEV-12345
✅ Total               : 24300

================================================================================

3️⃣  BÚSQUEDA MANUAL DE PATRONES:
--------------------------------------------------------------------------------

🔍 Buscando Proveedor/Emisor:
  Línea 3: Razón Social: PAPYRUS SOLUCIONES INTEGRALES SAS
  Línea 4: NIT: 900123456-1

🔍 Buscando Número:
  Línea 2: FEV-12345
  Línea 8: Número: FEV-12345

🔍 Buscando Total:
  Línea 15: Total a pagar: $24.300

================================================================================

4️⃣  SUGERENCIAS:
--------------------------------------------------------------------------------
✅ Todos los campos fueron detectados correctamente
```

## 🔧 Cómo Mejorar la Extracción

Una vez que ejecutes el diagnóstico en tus PDFs, podrás ver:

### Si el texto se extrae correctamente:
- ✅ El PDF es legible
- ❌ Los patrones regex no coinciden → Necesitamos ajustar los patrones

### Si el texto NO se extrae:
- ❌ El PDF puede ser una imagen escaneada
- 🔧 Solución: Necesitarías OCR (Tesseract)

### Si los patrones no coinciden:
- 🔧 Necesitamos agregar nuevos patrones específicos para tus facturas
- Te puedo ayudar a crear patrones personalizados basados en el diagnóstico

## 📝 Próximos Pasos

1. **Ejecuta el diagnóstico** en 2-3 facturas que no se están leyendo bien
2. **Comparte la salida** conmigo
3. **Ajustaré los patrones** para que funcionen con tus facturas específicas

## 💡 Ejemplo de Comando

```bash
# Ir a la carpeta CODE
cd CODE

# Diagnosticar una factura
python3 diagnostico_extraccion_pdf.py "../CUFE/FACTURAS/ad00454539650892500016306.pdf"

# O si estás en la raíz del proyecto
python3 CODE/diagnostico_extraccion_pdf.py "CUFE/FACTURAS/ad00454539650892500016306.pdf"
```

## 🎯 Objetivo

Con este diagnóstico podremos:
1. Ver exactamente qué texto se está extrayendo
2. Identificar por qué los patrones no coinciden
3. Crear patrones personalizados para tus facturas
4. Mejorar la tasa de extracción del 30% actual a 90%+
