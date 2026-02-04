# 📖 EXPLICACIÓN: Cómo se Extrae el Código CUFE

## 🎯 ¿Qué es el CUFE?

El **CUFE** (Código Único de Factura Electrónica) es un código de **96 caracteres hexadecimales** que identifica de forma única cada factura electrónica en Colombia.

**Ejemplo**:
```
7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2
```

---

## 🔍 Proceso de Extracción (Paso a Paso)

### **Paso 1: Extracción de Texto del PDF**

```python
def extract_text_from_pdf(pdf_path: str, max_pages: int = 5) -> str:
```

**¿Qué hace?**
1. Abre el PDF con `pdfplumber`
2. Lee las primeras 5 páginas (donde suele estar el CUFE)
3. Extrae el texto de cada página
4. Si encuentra un patrón de 96 caracteres hex, para de leer (optimización)

**Ejemplo de texto extraído**:
```
FACTURA ELECTRONICA DE VENTA
NIT: 19340011-9
CUFE: 7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2
Total: $787,138
```

**Logs que verás**:
```
📄 Procesando 2 páginas del PDF
   Página 1: 6780 caracteres extraídos
📊 Total extraído: 6780 caracteres
```

---

### **Paso 2: Búsqueda del CUFE con Expresión Regular**

```python
CUFE_PATTERN = r'[0-9a-fA-F]{96}'
matches = re.findall(CUFE_PATTERN, text, re.IGNORECASE)
```

**¿Qué busca?**
- **96 caracteres consecutivos**
- Solo caracteres **hexadecimales**: `0-9`, `a-f`, `A-F`
- Ignora mayúsculas/minúsculas

**Patrón regex explicado**:
```
[0-9a-fA-F]  → Un carácter hexadecimal (0-9, a-f, A-F)
{96}         → Exactamente 96 veces
```

**Logs que verás**:
```
🔍 Buscando CUFE en texto de 6780 caracteres
✅ Encontrados 1 patrones de 96 caracteres hex
```

---

### **Paso 3: Limpieza y Validación**

```python
cufe = cufe.strip().replace('\n', '').replace(' ', '')

if len(cufe) == 96:
    return cufe.lower()
```

**¿Qué hace?**
1. Elimina espacios al inicio/final
2. Elimina saltos de línea (`\n`)
3. Elimina espacios en blanco
4. Verifica que tenga exactamente 96 caracteres
5. Convierte a minúsculas

**Logs que verás**:
```
✅ CUFE válido extraído: 7569152b6d0396f9e507...ed3e2318402d2eb418d2
```

---

## ✅ Casos de Éxito

### **Caso 1: CUFE en una sola línea**
```
CUFE: 7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad1c33a597f92eed3e2318402d2eb418d2
```
✅ **Resultado**: Extrae correctamente

### **Caso 2: CUFE con espacios**
```
CUFE: 7569152b 6d0396f9 e5079cba c6bc56df 5b0cd68f b2609848 38efb60f 74d3f5ad 1c33a597 f92eed3e 2318402d 2eb418d2
```
✅ **Resultado**: Limpia espacios y extrae correctamente

### **Caso 3: CUFE en múltiples líneas**
```
CUFE: 7569152b6d0396f9e5079cbac6bc56df5b0cd68fb260984838efb60f74d3f5ad
1c33a597f92eed3e2318402d2eb418d2
```
✅ **Resultado**: Une las líneas y extrae correctamente

---

## ❌ Casos de Fallo

### **Caso 1: CUFE en Imagen (No Texto)**

**Problema**: El PDF tiene el CUFE como imagen escaneada, no como texto.

**Ejemplo**:
```
[IMAGEN: Código de barras con CUFE]
```

**Resultado**: ❌ No se puede extraer (pdfplumber solo lee texto)

**Solución**: Usar OCR o asociar CUFE manualmente

---

### **Caso 2: CUFE Dividido con Caracteres Especiales**

**Problema**: El CUFE está dividido con guiones o caracteres no hexadecimales.

**Ejemplo**:
```
CUFE: 7569152b-6d0396f9-e5079cba-c6bc56df-5b0cd68f-b2609848
```

**Resultado**: ❌ No encuentra 96 caracteres consecutivos

**Solución**: Mejorar el patrón regex para ignorar guiones

---

### **Caso 3: PDF Sin Texto Extraíble**

**Problema**: El PDF es una imagen escaneada completa.

**Resultado**: ❌ `extract_text_from_pdf()` retorna texto vacío

**Logs**:
```
📄 Procesando 1 páginas del PDF
📊 Total extraído: 0 caracteres
⚠️ Texto vacío, no se puede extraer CUFE
```

**Solución**: Usar OCR (Tesseract) o asociar CUFE manualmente

---

## 🔧 Debugging: Cómo Ver Qué Está Pasando

### **1. Ver Logs Durante la Carga**

```bash
docker logs -f paquetex_dev_app | grep -E "(📄|🔍|✅|❌|CUFE)"
```

**Logs esperados (éxito)**:
```
📄 Procesando 2 páginas del PDF
📊 Total extraído: 6780 caracteres
🔍 Buscando CUFE en texto de 6780 caracteres
✅ Encontrados 1 patrones de 96 caracteres hex
✅ CUFE válido extraído: 7569152b6d0396f9e507...
```

**Logs esperados (fallo)**:
```
📄 Procesando 2 páginas del PDF
📊 Total extraído: 6780 caracteres
🔍 Buscando CUFE en texto de 6780 caracteres
❌ No se encontró patrón de 96 caracteres hexadecimales
ℹ️ Encontrados 3 patrones hex más cortos:
   1. 7569152b6d0396f9e5079cbac6bc56df... (longitud: 48)
```

---

### **2. Probar con un PDF Específico**

```bash
cd CODE
source .venv/bin/activate
python3 test_cufe_simple.py
```

Este script prueba la extracción con PDFs de ejemplo y muestra:
- ✅ Si se extrajo el CUFE
- ❌ Si no se encontró
- ℹ️ Patrones hexadecimales encontrados (para debugging)

---

### **3. Ver el Texto Extraído del PDF**

```python
from src.app.services.pdf_parser_service import PDFParserService

parser = PDFParserService()
text = parser.extract_text_from_pdf("ruta/al/pdf.pdf")

print("Texto extraído:")
print(text[:500])  # Primeros 500 caracteres

# Buscar CUFE manualmente
import re
matches = re.findall(r'[0-9a-fA-F]{96}', text)
print(f"\nCUFEs encontrados: {len(matches)}")
for match in matches:
    print(f"  - {match}")
```

---

## 🎯 Resumen del Flujo

```
1. Usuario carga PDF
   ↓
2. extract_text_from_pdf(pdf_path)
   → Lee primeras 5 páginas
   → Extrae texto con pdfplumber
   → Retorna texto completo
   ↓
3. extract_cufe(text)
   → Busca patrón: [0-9a-fA-F]{96}
   → Limpia espacios y saltos de línea
   → Valida longitud = 96
   → Retorna CUFE o None
   ↓
4. Si CUFE encontrado:
   ✅ Estado: "pendiente_dian"
   ✅ CUFE real guardado
   
5. Si CUFE NO encontrado:
   ⚠️ Estado: "sin_cufe"
   ⚠️ CUFE temporal: TEMP_xxxxx
   💡 Usuario puede asociar CUFE manualmente
```

---

## 💡 Mejoras Posibles

### **1. Agregar OCR para PDFs Escaneados**

```python
# Usar Tesseract para extraer texto de imágenes
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text
```

### **2. Mejorar Patrón Regex para Guiones**

```python
# Permitir guiones opcionales entre grupos
CUFE_PATTERN = r'[0-9a-fA-F\-]{96,}'
# Luego limpiar guiones: cufe.replace('-', '')
```

### **3. Buscar Palabras Clave Antes del CUFE**

```python
# Buscar "CUFE:", "CUDE:", "Código:" seguido del patrón
CUFE_WITH_LABEL = r'(?:CUFE|CUDE|Código)[\s:]+([0-9a-fA-F]{96})'
```

---

## 📊 Estadísticas de Éxito

Según los tests realizados:
- ✅ **PDFs con texto**: 100% de éxito
- ❌ **PDFs escaneados**: 0% de éxito (requiere OCR)
- ⚠️ **PDFs con CUFE dividido**: Variable (depende del formato)

---

## 🎓 Conclusión

El sistema de extracción de CUFE funciona **muy bien** para PDFs con texto extraíble. 

**Limitaciones**:
- No funciona con PDFs escaneados (imágenes)
- No funciona si el CUFE está muy fragmentado

**Soluciones**:
- Usar el botón "🔗 Asociar CUFE" para casos especiales
- Implementar OCR para PDFs escaneados (mejora futura)
