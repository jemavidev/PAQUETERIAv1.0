# Status de Vistas - Refactorización

**Actualizado:** 2026-05-01  
**Rama actual:** refactor/announce-new

---

## 📊 Progress General

| Métrica | Valor |
|---------|-------|
| Vistas Totales | ~25 |
| En progreso | 1 |
| Completadas | 0 |
| Pendientes | ~24 |
| % Completado | 4% |

---

## 🔄 En Progreso

### Announce - New Version (PROTEGIDA)

| Vista | Archivo | Status | Cambios | Notas |
|-------|---------|--------|---------|-------|
| Anuncio Mejorado | `announce/announce_new.html` | 🔄 En progreso | Badges → /packages | Solo usuarios autenticados |

**Cambios realizados:**
- ✅ Template copiada de `announce_quick.html`
- ✅ Badges redirigen a `/packages?id=tracking_code` (en lugar de `/search?auto_search=...`)
- ✅ Icono actualizado (búsqueda → paquete)
- ✅ Ruta `/announce-new` agregada en `public.py` (PROTEGIDA)
- ✅ Autenticación obligatoria (redirige a login si no está logeado)

**Ruta backend:**
```python
@router.get("/announce-new")  # → solo usuarios autenticados
```

---

## ⏳ Pendientes

### Packages (Gestión de Paquetes)
| Vista | Archivo | Status | Cambios | Notas |
|-------|---------|--------|---------|-------|
| Lista de paquetes | `packages/list.html` | ⏳ Pendiente | TBD | Tablas con paginación |
| Crear paquete | `packages/new.html` | ⏳ Pendiente | TBD | Formulario |
| [Otros] | [Otros] | ⏳ Pendiente | TBD | A definir |

---

## 📝 Notas Técnicas

### `/announce-new` vs `/announce-papyrus`

| Aspecto | announce-papyrus | announce-new |
|--------|------------------|--------------|
| **Autenticación** | ❌ Pública | ✅ Protegida |
| **Usuarios** | Anónimos | Solo registrados |
| **Badges redirigen** | `/search?auto_search=XXX` | `/packages?id=XXX` |
| **Flujo** | Buscar paquetes | Recibir paquetes |
| **Look & Feel** | Mismo | Idéntico |

### Flujo de /announce-new

```
Usuario registrado entra a /announce-new
    ↓
Ingresa teléfono
    ↓
Sistema busca clientes (BD)
    ↓
Si existen paquetes previos:
    ↓
Muestra badges con tracking codes
    ↓
Click en badge → /packages?id=tracking_code
    ↓
Se abre modal de recepción
```

---

## ✅ Checklist

- [x] Template copiada
- [x] URLs actualizadas (badges)
- [x] Ruta backend creada
- [x] Autenticación configurada
- [x] Documentación actualizada
- [ ] Testing manual (próximo paso)
- [ ] Merge a LIVE-PROD

---

**Próximos pasos:**
1. Testing en navegador
2. Verificar que `/packages?id=...` cargue correctamente
3. Verificar que autenticación funciona
4. Merge a LIVE-PROD

**Rama:** refactor/announce-new  
**Última actualización:** 2026-05-01 10:25:00
