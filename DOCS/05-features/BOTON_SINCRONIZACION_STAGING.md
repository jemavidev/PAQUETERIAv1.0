# 🔄 Botón de Sincronización Staging - IMPLEMENTADO

**Fecha:** 27 de enero de 2026  
**Estado:** ✅ FUNCIONANDO

---

## 🎯 Funcionalidad

Un botón en el header de staging que permite sincronizar los datos de producción con un solo clic.

### 🎨 Ubicación

```
[Logo] PAQUETEX  [🟡 Staging]  [🔄 Sincronizar]  Paquetes  Mensajes...
```

El botón aparece **solo en staging**, justo después del badge amarillo.

---

## ✨ Características

### 1. Botón Inteligente
- ✅ **Solo visible en staging** (no aparece en producción)
- ✅ **Icono animado** durante la sincronización
- ✅ **Indicador de progreso** (0% → 100%)
- ✅ **Deshabilitado** mientras sincroniza
- ✅ **Tooltip** con fecha de última sincronización

### 2. Proceso de Sincronización
1. **Click en el botón** → Confirmación
2. **Exporta** datos de producción (`paqueteria_v4`)
3. **Restaura** en staging (`paqueteria_staging`)
4. **Notifica** cuando termina
5. **Recarga** la página automáticamente

### 3. Seguridad
- ✅ **Solo funciona en staging** (verificación en backend)
- ✅ **No puede ejecutarse en producción**
- ✅ **Confirmación** antes de ejecutar
- ✅ **Sincronización unidireccional** (Producción → Staging)

---

## 🔧 Implementación Técnica

### Backend

**Archivo:** `CODE/src/app/routes/sync_staging.py`

**Endpoints:**

1. **POST `/api/staging/sync`**
   - Inicia la sincronización en segundo plano
   - Usa `pg_dump` y `pg_restore`
   - Retorna inmediatamente

2. **GET `/api/staging/sync/status`**
   - Obtiene el estado actual
   - Progreso: 0% → 100%
   - Última sincronización

**Proceso:**
```python
1. Verificar que estamos en staging
2. Exportar producción con pg_dump
3. Restaurar en staging con pg_restore
4. Actualizar estado y progreso
5. Notificar completado
```

### Frontend

**Archivo:** `CODE/src/templates/base/base.html`

**Componentes:**

1. **Botón HTML**
   ```html
   <button id="sync-button">
       <svg>...</svg>
       <span>Sincronizar</span>
   </button>
   ```

2. **JavaScript**
   - Detecta entorno (staging)
   - Muestra/oculta botón
   - Maneja click y confirmación
   - Polling del estado cada 2 segundos
   - Animación del icono
   - Notificación al completar

---

## 📊 Estados del Botón

### Estado Normal
```
[🔄 Sincronizar]
```
- Color: Azul
- Habilitado
- Tooltip: "Última sincronización: [fecha]"

### Sincronizando
```
[⟳ Sincronizando... 45%]
```
- Icono girando
- Deshabilitado
- Progreso visible

### Completado
```
✅ Sincronización completada
```
- Alert de éxito
- Recarga automática de la página

### Error
```
❌ Error en la sincronización
```
- Alert con mensaje de error
- Botón vuelve a estado normal

---

## 🚀 Cómo Usar

### Desde el Navegador

1. **Abrir staging** en el navegador
2. **Ver el botón** "Sincronizar" en el header
3. **Click en el botón**
4. **Confirmar** la acción
5. **Esperar** (muestra progreso)
6. **Página se recarga** automáticamente

### Tiempo Estimado

- Base de datos pequeña (< 100 MB): **30-60 segundos**
- Base de datos mediana (100-500 MB): **1-3 minutos**
- Base de datos grande (> 500 MB): **3-10 minutos**

---

## 🔍 Verificación

### Probar el endpoint manualmente:

```bash
# Ver estado
curl http://localhost:8001/api/staging/sync/status

# Iniciar sincronización
curl -X POST http://localhost:8001/api/staging/sync

# Ver progreso
watch -n 2 'curl -s http://localhost:8001/api/staging/sync/status'
```

---

## ⚠️ Consideraciones

### 1. Datos Sobrescritos
- ⚠️ **Staging se sobrescribe completamente**
- ⚠️ **Cambios en staging se pierden**
- ✅ **Producción nunca se modifica**

### 2. Durante la Sincronización
- ⚠️ **No cerrar el navegador**
- ⚠️ **No reiniciar el servidor**
- ✅ **Puedes seguir usando otras pestañas**

### 3. Frecuencia Recomendada
- 📅 **Diaria:** Para desarrollo activo
- 📅 **Semanal:** Para mantenimiento
- 📅 **Antes de probar:** Features importantes

---

## 🐛 Troubleshooting

### El botón no aparece
- ✅ Verificar que estás en staging
- ✅ Refrescar con Ctrl+Shift+R
- ✅ Ver consola del navegador (F12)

### Sincronización falla
- ✅ Ver logs: `docker logs paqueteria_staging_app`
- ✅ Verificar espacio en disco
- ✅ Verificar conexión a RDS

### Sincronización se queda en 0%
- ✅ Esperar 30 segundos
- ✅ Refrescar la página
- ✅ Intentar de nuevo

---

## 📁 Archivos Modificados

```
CODE/
├── src/
│   ├── app/
│   │   └── routes/
│   │       └── sync_staging.py          ← NUEVO
│   ├── main.py                          ← MODIFICADO (registrar router)
│   ├── app/
│   │   └── config_routes.py             ← MODIFICADO (rutas públicas)
│   └── templates/
│       └── base/
│           └── base.html                ← MODIFICADO (botón + JS)
```

---

## 🎉 Ventajas

✅ **Un solo click** para sincronizar  
✅ **No necesitas SSH** al servidor  
✅ **Indicador visual** de progreso  
✅ **Seguro** (solo funciona en staging)  
✅ **Automático** (recarga al terminar)  
✅ **Fácil de usar** para todo el equipo  

---

## 🔮 Mejoras Futuras (Opcionales)

- [ ] Sincronización selectiva (solo ciertas tablas)
- [ ] Programar sincronizaciones automáticas
- [ ] Historial de sincronizaciones
- [ ] Notificaciones por email
- [ ] Sincronización incremental (solo cambios)

---

**Implementado por:** Kiro AI  
**Fecha:** 27 de enero de 2026  
**Estado:** ✅ FUNCIONANDO EN STAGING
