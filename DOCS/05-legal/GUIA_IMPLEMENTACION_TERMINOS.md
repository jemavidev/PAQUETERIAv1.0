# GUÍA DE IMPLEMENTACIÓN - TÉRMINOS Y CONDICIONES
## PAQUETES EL CLUB

**Documento Técnico para Desarrolladores**

---

## 1. ARCHIVOS CREADOS

Se han creado 3 documentos principales:

1. **TERMINOS_Y_CONDICIONES_COMPLETO.md** (Documento legal completo)
2. **POLITICAS_PRIVACIDAD.md** (Política de privacidad detallada)
3. **RESUMEN_TERMINOS_CONDICIONES.md** (Versión simplificada para usuarios)

---

## 2. RUTAS A CREAR EN EL SITIO WEB

### 2.1 Rutas Públicas Necesarias

Agregar en `CODE/src/app/routes/public.py`:

```python
@router.get("/terms")
async def terms_page(request: Request):
    """Página de Términos y Condiciones"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/terms.html", context)

@router.get("/privacy")
async def privacy_page(request: Request):
    """Página de Política de Privacidad"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/privacy.html", context)

@router.get("/terms/summary")
async def terms_summary_page(request: Request):
    """Página de Resumen de Términos"""
    context = get_auth_context_from_request(request)
    return templates.TemplateResponse("general/terms-summary.html", context)
```

---

## 3. TEMPLATES HTML A CREAR

### 3.1 Estructura de Carpetas
```
CODE/src/templates/general/
├── help.html (✅ Ya actualizado)
├── terms.html (⚠️ Crear)
├── privacy.html (⚠️ Crear)
├── terms-summary.html (⚠️ Crear)
├── cookies.html (✅ Ya existe)
└── policies.html (✅ Ya existe)
```

---

## 4. PRÓXIMOS PASOS

### Paso 1: Crear Templates HTML
Convertir los archivos .md a HTML usando el mismo estilo de `help.html`

### Paso 2: Actualizar Navegación
Agregar enlaces en footer y menús principales

### Paso 3: Agregar Checkbox de Aceptación
En formularios de registro/anuncio

### Paso 4: Implementar Modal de Términos
Para primera vez que usa el servicio

---

## 5. SUGERENCIAS ADICIONALES

- Agregar versión PDF descargable
- Implementar sistema de versiones
- Crear página de comparación de cambios
- Agregar búsqueda dentro de términos
- Implementar breadcrumbs
- Agregar índice flotante en desktop

---

**Documentos listos para revisión legal e implementación técnica**
