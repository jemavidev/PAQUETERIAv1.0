# 🔄 Diagrama de Flujo - Sincronización Staging

## 📊 Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USUARIO EN NAVEGADOR                         │
│                                                                      │
│  1. Ve botón "🔄 Sincronizar" en header (solo en staging)          │
│  2. Click en el botón                                               │
│  3. Confirma: "¿Deseas sincronizar?"                                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (JavaScript)                             │
│                                                                      │
│  4. Envía: POST /api/staging/sync                                   │
│  5. Inicia polling cada 2 segundos: GET /api/staging/sync/status    │
│  6. Muestra progreso: "Sincronizando... 45%"                        │
│  7. Anima icono (spinning)                                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI en Contenedor)                         │
│                                                                      │
│  8. Recibe POST /api/staging/sync                                   │
│  9. Verifica: ¿Estamos en staging? ✅                               │
│ 10. Crea archivo señal: /tmp/staging_sync_request                   │
│ 11. Retorna: {"status": "started"}                                  │
│                                                                      │
│ 12. Polling GET /api/staging/sync/status cada 5s                    │
│ 13. Lee: /tmp/staging_sync_result                                   │
│ 14. Retorna: {"is_running": true, "progress": 45}                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│           MONITOR EN HOST (sync_staging_monitor.sh)                  │
│                    Servicio systemd corriendo                        │
│                                                                      │
│ 15. Loop infinito: verifica cada 5 segundos                         │
│ 16. Detecta: /tmp/staging_sync_request existe ✅                    │
│ 17. Crea lock: /tmp/staging_sync.lock                              │
│ 18. Ejecuta Docker:                                                 │
│     docker run postgres:17-alpine                                   │
│       pg_dump producción → /tmp/backup.dump                         │
│       pg_restore staging ← /tmp/backup.dump                         │
│ 19. Escribe resultado: /tmp/staging_sync_result                    │
│     - "success" si OK                                               │
│     - "error: mensaje" si falla                                     │
│ 20. Limpia: rm /tmp/staging_sync_request                           │
│ 21. Limpia: rm /tmp/staging_sync.lock                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BACKEND (FastAPI en Contenedor)                         │
│                                                                      │
│ 22. Polling detecta: /tmp/staging_sync_result existe ✅            │
│ 23. Lee contenido: "success"                                        │
│ 24. Actualiza estado: is_running = false, progress = 100           │
│ 25. Retorna: {"is_running": false, "last_result": "success"}       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND (JavaScript)                             │
│                                                                      │
│ 26. Polling detecta: last_result === "success"                     │
│ 27. Detiene polling                                                 │
│ 28. Muestra alert: "✅ Sincronización completada"                  │
│ 29. Recarga página: window.location.reload()                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         USUARIO EN NAVEGADOR                         │
│                                                                      │
│ 30. Ve página recargada con datos actualizados                     │
│ 31. Botón vuelve a estado normal: "🔄 Sincronizar"                 │
│ 32. Tooltip muestra: "Última sincronización: [fecha]"              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Comunicación entre Componentes

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│  NAVEGADOR   │◄───────►│  CONTENEDOR  │◄───────►│     HOST     │
│              │   HTTP  │     APP      │  Files  │   MONITOR    │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │ POST /api/staging/sync  │                         │
      │────────────────────────►│                         │
      │                         │ Crea señal              │
      │                         │────────────────────────►│
      │                         │                         │
      │                         │                    Detecta señal
      │                         │                         │
      │                         │                    Ejecuta Docker
      │                         │                         │
      │                         │                    pg_dump + restore
      │                         │                         │
      │                         │ Escribe resultado       │
      │                         │◄────────────────────────│
      │ GET /api/.../status     │                         │
      │────────────────────────►│                         │
      │                         │ Lee resultado           │
      │◄────────────────────────│                         │
      │ {"progress": 100}       │                         │
      │                         │                         │
```

---

## 📁 Archivos Temporales

```
/tmp/
├── staging_sync_request     ← Señal: "Iniciar sincronización"
│                              Creado por: Contenedor APP
│                              Leído por: Monitor HOST
│                              Eliminado por: Monitor HOST
│
├── staging_sync_result      ← Resultado: "success" o "error: ..."
│                              Creado por: Monitor HOST
│                              Leído por: Contenedor APP
│                              Eliminado por: Contenedor APP
│
└── staging_sync.lock        ← Lock: Evita sincronizaciones simultáneas
                               Creado por: Monitor HOST
                               Eliminado por: Monitor HOST
```

---

## 🎯 Estados del Botón

```
┌─────────────────────────────────────────────────────────────┐
│                    ESTADO: NORMAL                            │
│  [🔄 Sincronizar]                                           │
│  - Color: Azul                                              │
│  - Habilitado: ✅                                           │
│  - Tooltip: "Última sincronización: [fecha]"               │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Click + Confirmar
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  ESTADO: SINCRONIZANDO                       │
│  [⟳ Sincronizando... 45%]                                  │
│  - Icono: Girando (animate-spin)                           │
│  - Deshabilitado: ❌                                        │
│  - Progreso: 0% → 100%                                      │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ Completado
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   ESTADO: COMPLETADO                         │
│  Alert: "✅ Sincronización completada"                      │
│  - Recarga automática de página                            │
│  - Vuelve a estado NORMAL                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Verificaciones de Seguridad

```
┌─────────────────────────────────────────────────────────────┐
│              VERIFICACIÓN EN BACKEND                         │
│                                                              │
│  if environment != "staging":                               │
│      raise HTTPException(403, "Solo en staging")            │
│                                                              │
│  if db_name != "paqueteria_staging":                        │
│      raise HTTPException(403, "Solo en staging")            │
│                                                              │
│  ✅ Producción NUNCA puede ejecutar sincronización          │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Tiempos Estimados

```
┌─────────────────────────────────────────────────────────────┐
│  Tamaño BD          │  Tiempo Estimado                      │
├─────────────────────┼───────────────────────────────────────┤
│  < 100 MB           │  30-60 segundos                       │
│  100-500 MB         │  1-3 minutos                          │
│  > 500 MB           │  3-10 minutos                         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Visualización en el Header

```
┌────────────────────────────────────────────────────────────────┐
│  [Logo] PAQUETEX  [🟡 Staging]  [🔄 Sincronizar]  Paquetes... │
│                                                                 │
│  ↑                ↑              ↑                             │
│  Logo             Badge          Botón (solo en staging)       │
└────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Componentes del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPONENTES                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Frontend (base.html)                                    │
│     - Botón HTML                                            │
│     - JavaScript para polling                               │
│     - Animaciones                                           │
│                                                              │
│  2. Backend (sync_staging.py)                               │
│     - POST /api/staging/sync                                │
│     - GET /api/staging/sync/status                          │
│     - Manejo de archivos señal                              │
│                                                              │
│  3. Monitor (sync_staging_monitor.sh)                       │
│     - Loop infinito (cada 5s)                               │
│     - Detecta señal                                         │
│     - Ejecuta Docker                                        │
│     - Escribe resultado                                     │
│                                                              │
│  4. Servicio (staging-sync-monitor.service)                 │
│     - Systemd service                                       │
│     - Auto-start con el servidor                            │
│     - Auto-restart si falla                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Creado por:** Kiro AI  
**Fecha:** 27 de enero de 2026  
**Propósito:** Documentación visual del sistema de sincronización
