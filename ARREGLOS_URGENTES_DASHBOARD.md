# Arreglos Urgentes - Dashboard Administrativo

**Fecha:** 2025-01-24  
**Prioridad:** ALTA

## 🐛 PROBLEMAS IDENTIFICADOS

### 1. Tab "Clientes" - Botón redirige incorrectamente
**Problema:** Botón "Ver Todos los Clientes" redirige a `/customers` que redirige a `/` (home)  
**Causa:** Ruta `/customers` en `public.py` redirige a home  
**Solución:** Cambiar botón para que apunte a `/customers/manage` (ruta correcta en `protected.py`)

### 2. Tab "Settings" - Muestra vista separada
**Problema:** Tab Settings probablemente redirige a `/settings` en lugar de mostrar contenido inline  
**Solución:** Cargar contenido de settings dentro del tab sin redireccionar

### 3. Rutas duplicadas `/customers`
**Problema:** Existe `/customers` en `public.py` (redirige a home) y `/customers/manage` en `protected.py` (correcto)  
**Solución:** Eliminar o corregir la ruta `/customers` en `public.py`

## ✅ SOLUCIONES A IMPLEMENTAR

### Arreglo 1: Corregir botón de Clientes en Dashboard
**Archivo:** `CODE/src/templates/admin/admin_dashboard.html`  
**Línea:** ~627  
**Cambio:**
```html
<!-- ANTES -->
<button onclick="window.location.href='/customers'">Ver Todos los Clientes</button>

<!-- DESPUÉS -->
<button onclick="window.location.href='/customers/manage'">Ver Todos los Clientes</button>
```

### Arreglo 2: Corregir ruta /customers en public.py
**Archivo:** `CODE/src/app/routes/public.py`  
**Línea:** 85-89  
**Cambio:**
```python
# ANTES
@router.get("/customers")
async def customers_page(request: Request):
    """Página de anunciar paquetes - Redirige a la página principal"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

# DESPUÉS
@router.get("/customers")
async def customers_page(request: Request):
    """Redirige a gestión de clientes"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/customers/manage", status_code=302)
```

### Arreglo 3: Verificar tab Settings
**Archivo:** `CODE/src/templates/admin/admin_dashboard.html`  
**Buscar:** Tab settings content  
**Verificar:** Que no tenga `window.location.href` o redirecciones

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Cambiar botón "Ver Todos los Clientes" a `/customers/manage`
- [ ] Corregir ruta `/customers` para que redirija a `/customers/manage`
- [ ] Verificar que tab Settings no tenga redirecciones
- [ ] Hacer commit de cambios
- [ ] Deploy a staging
- [ ] Probar manualmente cada botón
- [ ] Verificar que no haya más redirecciones incorrectas

## 🎯 RESULTADO ESPERADO

Después de estos arreglos:
1. ✅ Botón "Ver Todos los Clientes" → Lleva a `/customers/manage` (gestión de clientes)
2. ✅ Ruta `/customers` → Redirige a `/customers/manage` (en lugar de home)
3. ✅ Tab Settings → Muestra contenido inline sin redireccionar

---

**Nota:** Estos son arreglos rápidos. La implementación completa del Dashboard Unificado V2 se hará después.
