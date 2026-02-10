# QUICK START: Sistema de Validación y Corrección Manual

## ✅ BACKEND COMPLETADO

El sistema de validación y corrección manual está **completamente implementado en el backend**.

---

## 🚀 CÓMO USAR (API)

### 1. Validar una factura

```bash
curl http://localhost:8000/api/v2/invoices/cufe/{cufe}/validate
```

**Respuesta**:
```json
{
  "has_warnings": true,
  "warnings": [
    {
      "field": "dian_total_neto",
      "field_label": "Total a pagar",
      "severity": "critical",
      "message": "Total no extraído del PDF",
      "current_value": null,
      "suggestion": "Ingresar total manualmente"
    }
  ],
  "validation_score": 60,
  "source": "PDF"
}
```

### 2. Corregir campos

```bash
curl -X PATCH http://localhost:8000/api/v2/invoices/cufe/{cufe}/correct \
  -H "Content-Type: application/json" \
  -d '{
    "dian_total_neto": 1234567.89,
    "dian_subtotal": 1037368.98,
    "dian_total_iva": 197198.91
  }'
```

---

## 🚧 FRONTEND PENDIENTE

Para completar la implementación, necesitas agregar la UI en:

**Archivo**: `CODE/src/templates/invoices_v2/cufe.html`

**Pasos**:
1. Agregar badge ⚠️ en columna Estado
2. Agregar modal de corrección
3. Agregar funciones JavaScript

**Ver**: `RESUMEN_IMPLEMENTACION_VALIDACION.md` para código completo

---

## 📄 DOCUMENTACIÓN

- `SISTEMA_VALIDACION_CORRECCION_MANUAL.md` - Documentación completa
- `RESUMEN_IMPLEMENTACION_VALIDACION.md` - Resumen de implementación
- `test_validation_ui_demo.html` - Demo visual de componentes UI
- `CAMPOS_AFECTADOS_CASOS_EDGE.md` - Análisis de campos problemáticos

---

**Estado**: Backend ✅ | Frontend 🚧
