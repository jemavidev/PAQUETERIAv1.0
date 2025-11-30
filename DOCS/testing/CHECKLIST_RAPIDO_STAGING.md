# ✅ Checklist Rápido - Pruebas Staging

**Fecha:** 2024-11-29  
**Commits:** f9b3910 hasta d0754e5

---

## 🤖 Pruebas Automatizadas

```bash
./test-staging-commits.sh
```

- [x] 10/10 pruebas pasadas
- [x] Flags de debug deshabilitados
- [x] Archivos modificados verificados
- [x] Documentación completa

---

## 👤 Pruebas Manuales Críticas

### 1. DevTools Desktop
- [ ] Abrir https://staging.jemavi.co/packages
- [ ] Presionar F12
- [ ] Verificar: NO se bloquea
- [ ] Verificar: Solo logs esenciales en consola

### 2. DevTools Móvil
- [ ] Con DevTools abierto, presionar Ctrl+Shift+M
- [ ] Cambiar entre dispositivos (iPhone, Android)
- [ ] Verificar: NO se bloquea
- [ ] Verificar: NO hay miles de logs

### 3. WhatsApp con Link
- [ ] En /packages, clic en botón verde de WhatsApp
- [ ] Verificar mensaje incluye:
  ```
  Hola [NOMBRE], te contacto por tu paquete.
  Puedes consultar el estado aquí:
  https://staging.jemavi.co/search?auto_search=[TRACKING]
  ```

### 4. Auto Search
- [ ] Copiar link del mensaje de WhatsApp
- [ ] Abrir en nueva pestaña
- [ ] Verificar: Búsqueda se ejecuta automáticamente
- [ ] Verificar: Muestra resultado del paquete

### 5. WhatsApp desde Modales
- [ ] Clic en "Recibir" → verificar link de WhatsApp
- [ ] Clic en "Entregar" → verificar link de WhatsApp
- [ ] Ambos deben incluir el link de búsqueda

---

## 🚀 Ejecución Rápida

### Opción 1: Script Interactivo (Recomendado)
```bash
./pruebas-manuales-interactivas.sh
```
Te guía paso a paso por todas las pruebas.

### Opción 2: Manual
Sigue el checklist arriba y marca cada item.

---

## 📊 Criterios de Éxito

Para aprobar staging:
- ✅ Todas las pruebas automatizadas pasan (10/10)
- ✅ DevTools NO se bloquea (desktop y móvil)
- ✅ WhatsApp incluye link de búsqueda
- ✅ Auto search funciona
- ✅ No hay regresiones

---

## 🎯 Resultado Esperado

Si todo pasa:
```
✅ STAGING APROBADO
→ Listo para merge a main
→ Listo para deploy a producción
```

Si algo falla:
```
❌ REVISAR PROBLEMAS
→ Ver logs en consola
→ Revisar documentación
→ Ejecutar fix correspondiente
```

---

## 📞 Soporte

Documentación completa:
- `PLAN_PRUEBAS_STAGING_2024-11-29.md` - Plan detallado
- `RESUMEN_PRUEBAS_STAGING.md` - Resumen ejecutivo
- `FIX_BROWSER_FREEZE_2024-11-29.md` - Fix DevTools
- `WHATSAPP_LINK_ACTUALIZADO.md` - Fix WhatsApp

Scripts:
- `test-staging-commits.sh` - Pruebas automatizadas
- `pruebas-manuales-interactivas.sh` - Guía interactiva
