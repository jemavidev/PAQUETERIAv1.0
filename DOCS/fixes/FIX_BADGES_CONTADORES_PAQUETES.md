# 🔧 FIX: Badges de Contadores de Paquetes en /customers/manage

## 📋 Problema Identificado

En la vista `/customers/manage`, los badges que muestran la cantidad de paquetes por estado (Anunciados, Recibidos, Entregados, Cancelados) **NO estaban contando los anuncios** de la tabla `package_announcements_new`.

### Ejemplo del problema:
- Cliente: **JESUS TEST**
- Paquetes reales: **2** (1 anunciado en `package_announcements_new` + 1 en `packages`)
- Paquetes mostrados: **1** (solo contaba el de la tabla `packages`)

## 🔍 Causa Raíz

El endpoint `/api/customers/package-counts/batch` solo consultaba la tabla `packages`, pero los paquetes anunciados que aún no han sido procesados están almacenados en la tabla `package_announcements_new` con `is_processed = False`.

### Arquitectura del Sistema:

```
┌─────────────────────────────────────┐
│  package_announcements_new          │
│  (Anuncios no procesados)           │
│  - is_processed = False             │
│  - is_active = True/False           │
└─────────────────────────────────────┘
           │
           │ (cuando se procesa)
           ▼
┌─────────────────────────────────────┐
│  packages                           │
│  (Paquetes procesados)              │
│  - status = ANUNCIADO/RECIBIDO/etc  │
└─────────────────────────────────────┘
```

## ✅ Solución Implementada

Modificado el endpoint `/api/customers/package-counts/batch` en `CODE/src/app/routes/customers.py` para:

1. **Contar paquetes de la tabla `packages`** (como antes)
2. **Contar anuncios de la tabla `package_announcements_new`** (NUEVO)
   - Anuncios activos (`is_active = True`) → se suman a **ANUNCIADOS**
   - Anuncios cancelados (`is_active = False`) → se suman a **CANCELADOS**

### Código agregado:

```python
# IMPORTANTE: Contar también los anuncios no procesados (activos y cancelados)
announcement_counts = db.query(
    PackageAnnouncementNew.customer_id,
    func.sum(case((PackageAnnouncementNew.is_active == True, 1), else_=0)).label('active_announcements'),
    func.sum(case((PackageAnnouncementNew.is_active == False, 1), else_=0)).label('cancelled_announcements')
).filter(
    PackageAnnouncementNew.customer_id.in_(ids_list),
    PackageAnnouncementNew.is_processed == False
).group_by(PackageAnnouncementNew.customer_id).all()

# Agregar los anuncios a los contadores
for customer_id, active_announcements, cancelled_announcements in announcement_counts:
    customer_id_str = str(customer_id)
    if customer_id_str not in result:
        result[customer_id_str] = {
            'announced': 0,
            'received': 0,
            'delivered': 0,
            'cancelled': 0
        }
    
    # Los anuncios activos se cuentan como ANUNCIADOS
    result[customer_id_str]['announced'] += (active_announcements or 0)
    # Los anuncios cancelados se cuentan como CANCELADOS
    result[customer_id_str]['cancelled'] += (cancelled_announcements or 0)
```

## 📊 Resultado Esperado

Ahora los badges mostrarán:

| Estado | Fuente | Color |
|--------|--------|-------|
| 🟡 **Anunciados** | `packages` (status=ANUNCIADO) + `package_announcements_new` (is_active=True, is_processed=False) | Amarillo |
| 🔵 **Recibidos** | `packages` (status=RECIBIDO) | Azul |
| 🟢 **Entregados** | `packages` (status=ENTREGADO) | Verde |
| 🔴 **Cancelados** | `packages` (status=CANCELADO) + `package_announcements_new` (is_active=False, is_processed=False) | Rojo |

## 🧪 Cómo Probar

1. **Reiniciar el servidor:**
   ```bash
   docker compose restart web
   ```

2. **Ir a la vista de clientes:**
   ```
   https://paquetex.papyrus.com.co/customers/manage
   ```

3. **Verificar el cliente JESUS TEST:**
   - Debería mostrar **2 paquetes** en total
   - El badge de "Anunciados" debería mostrar el paquete de la tabla `package_announcements_new`

4. **Limpiar caché del navegador:**
   - Presionar `Ctrl+F5` o `Cmd+Shift+R` para forzar recarga

## 📁 Archivos Modificados

- ✅ `CODE/src/app/routes/customers.py` - Endpoint `/api/customers/package-counts/batch`

## 🔗 Consistencia con Otros Endpoints

Este fix hace que el endpoint `/package-counts/batch` sea **consistente** con el endpoint `/customers/{customer_id}/packages`, que ya contaba correctamente los anuncios.

## 📝 Notas Adicionales

- El endpoint mantiene su optimización (una sola consulta por tabla)
- No afecta el rendimiento significativamente
- Los anuncios solo se cuentan si `is_processed = False`
- Una vez que un anuncio se procesa y se convierte en paquete, solo se cuenta en la tabla `packages`

---

**Fecha:** 2025-11-26  
**Autor:** Kiro AI Assistant  
**Estado:** ✅ Implementado
