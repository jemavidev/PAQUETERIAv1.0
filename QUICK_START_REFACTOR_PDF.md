# QUICK START: Refactorizar Parser PDF

## 🎯 OBJETIVO
Hacer que el parser PDF extraiga datos con la misma precisión que el XML (100% confiable).

## ✅ LO QUE YA FUNCIONA
- ✅ Parser XML: 100% funcional (10/10 archivos probados)
- ✅ Parser PDF: Productos funcionando bien (5 formatos soportados)
- ✅ 183 archivos XML + PDF disponibles para testing

## 🔧 LO QUE HAY QUE ARREGLAR

### 1. Totales (CRÍTICO)
**Problema**: Captura valores incorrectos
**Solución**: Buscar "Total factura (=)" en última hoja

### 2. IVA por producto (IMPORTANTE)
**Problema**: No extrae IVA correctamente
**Solución**: Implementar 3 estrategias de extracción

### 3. Estrategia híbrida (RECOMENDADO)
**Problema**: No usa XML cuando está disponible
**Solución**: XML primero, PDF fallback

## 🚀 PASOS RÁPIDOS

### Paso 1: Refactorizar `_extract_totales()`
```bash
# Editar archivo
nano CODE/src/app/services/pdf_parser_service.py

# Buscar método _extract_totales (línea ~550)
# Reemplazar con versión mejorada de REFACTOR_PDF_PARSER_BASADO_EN_XML.md
```

### Paso 2: Mejorar IVA en `_extract_productos()`
```bash
# Mismo archivo, buscar _extract_productos (línea ~650)
# Agregar extracción de IVA con 3 estrategias
```

### Paso 3: Implementar estrategia híbrida
```bash
# Editar servicio principal
nano CODE/src/app/services/invoice_v2_service.py

# Agregar método process_dian_document() con lógica híbrida
```

### Paso 4: Probar
```bash
# Test XML (ya funciona)
python3 test_xml_parser_standalone.py

# Test comparativo (crear si no existe)
python3 test_xml_vs_pdf_comparison.py
```

## 📁 ARCHIVOS CLAVE

### Para leer:
1. `REFACTOR_PDF_PARSER_BASADO_EN_XML.md` - Plan detallado
2. `ANALISIS_XML_ESTRUCTURA_COMPLETA.md` - Estructura XML
3. `CODE/src/app/services/xml_parser_service.py` - Parser XML (referencia)

### Para modificar:
1. `CODE/src/app/services/pdf_parser_service.py` - Parser PDF
2. `CODE/src/app/services/invoice_v2_service.py` - Servicio principal

### Para ejecutar:
1. `test_xml_parser_standalone.py` - Test XML (✅ funciona)
2. `test_xml_vs_pdf_comparison.py` - Test comparativo (crear)

## 💡 TIPS

1. **XML es la verdad**: Siempre que esté disponible, usar XML
2. **PDF es fallback**: Solo cuando no hay XML
3. **Validar siempre**: Comparar XML vs PDF cuando ambos existen
4. **Logging**: Registrar qué fuente se usó (XML o PDF)

## ⏱️ TIEMPO ESTIMADO
- Refactorizar totales: 30 min
- Mejorar IVA: 45 min
- Estrategia híbrida: 1 hora
- Testing: 30 min
**TOTAL: ~3 horas**

## 📊 ÉXITO
- ✅ Parser XML: 100% (10/10)
- ⏳ Parser PDF: Pendiente validar
- ⏳ Coincidencia: Objetivo 95%+

## 🎯 PRÓXIMO PASO
Abrir `CODE/src/app/services/pdf_parser_service.py` y refactorizar `_extract_totales()` (línea ~550).

---
**Fecha**: 10 de Febrero de 2026
**Estado**: Listo para refactorizar
