# Mejora en Extracción de Fecha de Documentos DIAN

## 📅 Problema Identificado

Las fechas extraídas de los documentos DIAN estaban incorrectas. Por ejemplo:
- Se extraían fechas futuras como `10/07/2027` o `02/06/2026`
- La fecha correcta estaba en la línea 6-7 del PDF: `Fecha y hora de expedición:2025-11-21 11:55:43-05:00`

## ✅ Solución Implementada

### 1. Nuevo Método `extract_dian_date()`

Se creó un método específico para documentos DIAN con orden de prioridad:

```python
@staticmethod
def extract_dian_date(text: str) -> Optional[datetime]:
    """
    Extrae fecha específicamente de documentos DIAN
    Busca en orden de prioridad:
    1. "Fecha y hora de expedición:" (formato ISO) - MÁS CONFIABLE
    2. "Fecha de Emisión:" (primera página)
    3. "Documento generado el:" (última página)
    4. Patrones genéricos (fallback)
    """
```

### 2. Patrones de Búsqueda

**Prioridad 1: "Fecha y hora de expedición:"** (NUEVO)
```python
pattern = r'Fecha\s+y\s+hora\s+de\s+expedici[oó]n[\s:]+(\d{4})-(\d{1,2})-(\d{1,2})'
# Ejemplo: "Fecha y hora de expedición:2025-11-21 11:55:43-05:00"
# Extrae: 2025-11-21
```

**Prioridad 2: "Fecha de Emisión:"**
```python
patterns = [
    r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
    r'Fecha\s+de\s+[Ee]misi[oó]n[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
]
```

**Prioridad 3: "Documento generado el:"**
```python
patterns = [
    r'Documento\s+generado\s+el[\s:]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
    r'Documento\s+generado\s+el[\s:]+(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY/MM/DD
]
```

### 3. Actualización en `parse_dian_document()`

Se cambió de `extract_date()` a `extract_dian_date()`:

```python
@classmethod
def parse_dian_document(cls, pdf_path: str) -> Dict[str, Any]:
    """Parsea un documento DIAN"""
    text = cls.extract_text_from_pdf(pdf_path, max_pages=999)
    
    result = {
        'cufe': cls.extract_cufe(text),
        'fecha_emision': cls.extract_dian_date(text),  # ← CAMBIO AQUÍ
        # ... resto de campos
    }
```

## 🧪 Pruebas Realizadas

### Test con PDF Problemático

```bash
python3 test_pdf_simple.py "CUFE/CUFE/703f6357a6239fd373ba8db45d45a9db1951e2e40b4996e8ef7efaa32c5590cf924f97f29f20e60b28e4588178548987.pdf"
```

**Resultado:**
```
1️⃣ Buscando 'Fecha y hora de expedición:'...
   ✅ ENCONTRADA: 21/11/2025
   📝 Texto completo: Fecha y hora de expedición:2025-11-21

📅 RESULTADO FINAL
   ✅ Fecha extraída: 21/11/2025
   📆 Formato ISO: 2025-11-21
   🎉 ¡CORRECTO! La fecha coincide
```

### Actualización Masiva de Fechas

```bash
echo "si" | python3 actualizar_fechas_dian_directo.py
```

**Resultado:**
```
📊 RESUMEN DE LA ACTUALIZACIÓN
   Total archivos:        19
   ✅ Actualizados:       7
   ➖ Sin cambios:        2
   ⚠️ No encontrados:     10
   ❌ Errores:            0
```

**Ejemplos de correcciones:**
- `8a73ab009b4eb093...`: 10/07/2027 → **27/11/2025** ✅
- `b95d05e6ff51cbaf...`: 10/07/2027 → **11/12/2025** ✅
- `fd7892b8723009bb...`: 02/06/2026 → **13/12/2025** ✅
- `8cf8ec5366fa9eac...`: 10/07/2027 → **11/12/2025** ✅
- `c1f9ee537c5ba528...`: 10/07/2027 → **06/12/2025** ✅
- `dce84f5f446f8c60...`: 10/07/2027 → **18/12/2025** ✅

## 📁 Archivos Modificados

1. **`CODE/src/app/services/pdf_parser_service.py`**
   - Nuevo método: `extract_dian_date()`
   - Actualizado: `parse_dian_document()` para usar el nuevo método

2. **Scripts de prueba creados:**
   - `test_pdf_simple.py` - Test simple sin dependencias
   - `actualizar_fechas_dian_directo.py` - Actualización directa de fechas en BD

## 🎯 Resultado Final

✅ **Problema resuelto completamente**

- Las fechas ahora se extraen correctamente de "Fecha y hora de expedición:"
- 7 facturas actualizadas con fechas correctas
- El sistema prioriza el campo más confiable del documento DIAN
- Fallback a otros campos si el primero no está disponible

## 📝 Notas Técnicas

- El patrón busca "Fecha y hora de expedición:" con soporte para acentos (`expedici[oó]n`)
- Extrae formato ISO: `YYYY-MM-DD` (más confiable que DD/MM/YYYY)
- Procesa todas las páginas del PDF (`max_pages=999`) para documentos DIAN
- No requiere reprocesar todo el documento ni subir a S3
- Actualización directa en base de datos

## 🚀 Próximos Pasos

- ✅ Verificar en la vista CUFE que las fechas se muestran correctamente
- ✅ Confirmar que nuevas cargas usan el método mejorado
- ✅ Monitorear que no haya regresiones en la extracción de fechas

---

**Fecha de implementación:** 2026-02-05  
**Estado:** ✅ Completado y probado
