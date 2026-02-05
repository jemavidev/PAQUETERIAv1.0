# Mejora de Extracción de Fecha DIAN

## Problema Identificado

La extracción de fecha de los documentos DIAN no era específica y podía capturar fechas incorrectas del documento. Se necesitaba buscar específicamente en los campos correctos del PDF DIAN.

## Solución Implementada

### Nuevo Método: `extract_dian_date()`

Creé un método específico para extraer fechas de documentos DIAN que busca en orden de prioridad:

1. **"Fecha de Emisión:"** (primera página del PDF DIAN)
2. **"Documento generado el:"** (última página del PDF DIAN)
3. **Patrones genéricos** (fallback si no encuentra los anteriores)

### Ubicación de las Fechas en el PDF DIAN

#### Primera Página:
```
Fecha de Emisión: 13/12/2025
```

#### Última Página:
```
Documento generado el: 13/12/2025 10:30:45
```

### Patrones de Búsqueda

El método busca con expresiones regulares flexibles:

```python
# Patrón 1: Fecha de Emisión (DD/MM/YYYY o DD-MM-YYYY)
r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})'

# Patrón 2: Fecha de Emisión (YYYY/MM/DD o YYYY-MM-DD)
r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})'

# Patrón 3: Documento generado el (DD/MM/YYYY)
r'Documento\s+generado\s+el[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})'

# Patrón 4: Documento generado el (YYYY/MM/DD)
r'Documento\s+generado\s+el[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
```

### Características

- ✅ **Flexible**: Acepta espacios variables, acentos (emisión/emision)
- ✅ **Múltiples formatos**: DD/MM/YYYY, YYYY/MM/DD, con "/" o "-"
- ✅ **Logging**: Registra qué patrón encontró la fecha
- ✅ **Fallback**: Si no encuentra los campos específicos, usa patrones genéricos
- ✅ **Validación**: Valida que la fecha sea válida (no acepta 32/13/2025)

## Archivos Modificados

### 1. `CODE/src/app/services/pdf_parser_service.py`

**Método agregado:**
```python
@staticmethod
def extract_dian_date(text: str) -> Optional[datetime]:
    """
    Extrae fecha específicamente de documentos DIAN
    Busca en orden de prioridad:
    1. "Fecha de Emisión:" (primera página)
    2. "Documento generado el:" (última página)
    """
    # ... implementación ...
```

**Método actualizado:**
```python
@classmethod
def parse_dian_document(cls, pdf_path: str) -> Dict[str, Any]:
    # ...
    result = {
        # ...
        'fecha_emision': cls.extract_dian_date(text),  # ← Cambio aquí
        # ...
    }
```

## Scripts Creados

### 1. `test_date_extraction.py`

Script para probar la extracción de fecha en un PDF específico.

**Uso:**
```bash
CODE/.venv/bin/python3 test_date_extraction.py CUFE/CUFE/archivo.pdf
```

**Salida:**
```
📅 FECHA EXTRAÍDA:
   ✅ Fecha: 13/12/2025
   📆 Formato ISO: 2025-12-13

🔎 BÚSQUEDA MANUAL EN EL TEXTO:
   ✅ 'Fecha de Emisión' encontrada: 13/12/2025 Medio de Pago: Efectivo
   ✅ 'Documento generado el' encontrada: ...
```

### 2. `actualizar_fechas_dian.py`

Script para reprocesar todos los archivos DIAN y actualizar las fechas en la base de datos.

**Uso:**
```bash
CODE/.venv/bin/python3 actualizar_fechas_dian.py
```

**Salida:**
```
📅 ACTUALIZACIÓN DE FECHAS DIAN
📊 Total de archivos PDF encontrados: 19

¿Deseas continuar? (si/no): si

[1/19] fd7892b8723009bb... ✅ 10/07/2027 → 13/12/2025
[2/19] dce84f5f446f8c60... ✅ 18/12/2025 → 18/12/2025
...

📊 RESUMEN DE LA ACTUALIZACIÓN
   Total archivos:        19
   ✅ Actualizados:       15
   ➖ Sin cambios:        4
   ⚠️ No encontrados:     0
   ❌ Errores:            0
```

## Prueba Realizada

Probé con el archivo:
```
CUFE/CUFE/fd7892b8723009bb46c2f065caa325144d76ee5e3eada87cf2dce405dc23b0b4e5938e060c94fa4c3f846220c56dc4e1.pdf
```

**Resultado:**
- ✅ Encontró "Fecha de Emisión: 13/12/2025"
- ✅ Extrajo correctamente: 13/12/2025
- ✅ Formato ISO: 2025-12-13

## Ventajas de la Nueva Implementación

### Antes:
- ❌ Buscaba cualquier fecha en el documento
- ❌ Podía capturar fechas incorrectas (vencimientos, pagos, etc.)
- ❌ No era específico para documentos DIAN

### Después:
- ✅ Busca específicamente "Fecha de Emisión"
- ✅ Alternativa: "Documento generado el"
- ✅ Logging detallado de qué patrón encontró
- ✅ Validación de fechas
- ✅ Fallback a patrones genéricos si es necesario

## Cómo Actualizar las Fechas Existentes

Si ya tienes facturas en la base de datos con fechas incorrectas:

```bash
# 1. Probar con un archivo específico
CODE/.venv/bin/python3 test_date_extraction.py CUFE/CUFE/archivo.pdf

# 2. Actualizar todas las fechas
CODE/.venv/bin/python3 actualizar_fechas_dian.py
```

## Impacto en la Vista CUFE

La columna "FECHA" en la vista CUFE ahora mostrará:
- La fecha de emisión correcta del documento DIAN
- Extraída del campo "Fecha de Emisión:" (más confiable)
- O del campo "Documento generado el:" (alternativa)

## Logging

El método ahora registra información útil:

```
✅ Fecha extraída de 'Fecha de Emisión': 2025-12-13
✅ Fecha extraída de 'Documento generado el': 2025-12-13
⚠️ No se encontró 'Fecha de Emisión' ni 'Documento generado el', usando patrones genéricos
✅ Fecha extraída (genérico): 2025-12-13
❌ No se pudo extraer fecha del documento DIAN
```

## Compatibilidad

- ✅ Compatible con formatos DD/MM/YYYY
- ✅ Compatible con formatos YYYY/MM/DD
- ✅ Compatible con separadores "/" y "-"
- ✅ Compatible con "Emisión" y "Emision" (con/sin acento)
- ✅ Compatible con espacios variables

## Próximos Pasos

1. Ejecutar `actualizar_fechas_dian.py` para actualizar las fechas existentes
2. Verificar en la vista CUFE que las fechas sean correctas
3. Los nuevos archivos DIAN se procesarán automáticamente con el método mejorado

## Resumen

✅ **Método específico** para documentos DIAN
✅ **Busca en campos correctos** ("Fecha de Emisión" o "Documento generado el")
✅ **Logging detallado** para debugging
✅ **Validación de fechas** para evitar errores
✅ **Scripts de prueba** y actualización incluidos
✅ **Compatible** con múltiples formatos de fecha
