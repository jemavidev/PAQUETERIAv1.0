# ✅ Checklist de Despliegue a Producción

## PRE-DESPLIEGUE

### Preparación
- [ ] Leer `RESUMEN_CAMBIOS_PRODUCCION.md`
- [ ] Leer `PRUEBAS_PRE_PRODUCCION.md`
- [ ] Tener acceso SSH a producción
- [ ] Tener backup reciente de BD
- [ ] Notificar al equipo del despliegue

### Backup
- [ ] Backup de base de datos creado
- [ ] Tag de git creado (`v1.0-pre-preferencias`)
- [ ] Backup guardado en lugar seguro
- [ ] Verificar que el backup es válido

---

## DESPLIEGUE

### Código
- [ ] `git pull` en local
- [ ] `git push production main`
- [ ] SSH a producción
- [ ] `git pull` en producción
- [ ] `docker-compose restart backend`
- [ ] Esperar 30 segundos

### Verificación Inmediata
- [ ] Backend está corriendo (`docker ps`)
- [ ] No hay errores en logs (`docker logs`)
- [ ] Health endpoint responde (`curl /health`)
- [ ] Página principal carga

---

## PRUEBAS POST-DESPLIEGUE (CRÍTICAS)

### PRUEBA 1: Portal de Clientes
- [ ] Ir a `/customer/verify`
- [ ] Solicitar OTP con teléfono de prueba
- [ ] Recibir SMS
- [ ] Recibir Email
- [ ] Ingresar código
- [ ] Acceder al dashboard
- [ ] Ver datos del cliente

### PRUEBA 2: Preferencias
- [ ] Ir a tab "Preferencias"
- [ ] Desactivar SMS y Email
- [ ] Guardar
- [ ] Ver mensaje de éxito
- [ ] Recargar página (F5)
- [ ] Verificar que siguen desactivadas

### PRUEBA 3: Bloqueo de Notificaciones
- [ ] Cambiar estado de un paquete del cliente
- [ ] Verificar que NO llega SMS
- [ ] Verificar que NO llega Email
- [ ] Ver logs: "bloqueado por preferencias"

### PRUEBA 4: Reactivar Notificaciones
- [ ] Activar SMS y Email en preferencias
- [ ] Guardar
- [ ] Cambiar estado de otro paquete
- [ ] Verificar que SÍ llega SMS
- [ ] Verificar que SÍ llega Email

### PRUEBA 5: OTP Siempre Se Envía
- [ ] Con preferencias desactivadas
- [ ] Cerrar sesión
- [ ] Solicitar nuevo OTP
- [ ] Verificar que SÍ llega SMS
- [ ] Verificar que SÍ llega Email

### PRUEBA 6: Página de Anuncios
- [ ] Abrir en modo incógnito
- [ ] Ir a `/announce`
- [ ] Llenar formulario
- [ ] Enviar
- [ ] Verificar que funciona sin login

### PRUEBA 7: Dashboard Admin
- [ ] Login como admin
- [ ] Ir a `/customers/manage`
- [ ] Click en botón de preferencias (🔔)
- [ ] Verificar que abre modal
- [ ] No hay errores en consola

---

## MONITOREO (Primeras 2 Horas)

### Logs
- [ ] Ver logs en tiempo real
- [ ] No hay errores críticos
- [ ] Logs de preferencias funcionan
- [ ] Logs de bloqueo funcionan

### Base de Datos
- [ ] Verificar tabla `customer_preferences`
- [ ] Verificar notificaciones bloqueadas
- [ ] No hay errores de BD

### Usuarios
- [ ] No hay quejas de clientes
- [ ] No hay reportes de errores
- [ ] Sistema funciona normalmente

---

## SI ALGO FALLA

### Rollback Inmediato
- [ ] `git reset --hard <commit-anterior>`
- [ ] `docker-compose restart backend`
- [ ] Verificar que funciona
- [ ] Notificar al equipo

### Investigación
- [ ] Revisar logs de error
- [ ] Revisar consola del navegador
- [ ] Revisar base de datos
- [ ] Documentar el problema

---

## POST-DESPLIEGUE (24 Horas)

### Monitoreo Continuo
- [ ] Revisar logs cada 4 horas
- [ ] Verificar notificaciones bloqueadas
- [ ] Verificar quejas de usuarios
- [ ] Verificar métricas de uso

### Documentación
- [ ] Actualizar documentación si es necesario
- [ ] Documentar problemas encontrados
- [ ] Documentar soluciones aplicadas

---

## FIRMA DE APROBACIÓN

**Despliegue realizado por:** _______________

**Fecha:** _______________

**Hora:** _______________

**Todas las pruebas pasadas:** [ ] SÍ  [ ] NO

**Observaciones:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Aprobado para producción:** [ ] SÍ  [ ] NO

---

## CONTACTOS DE EMERGENCIA

**Desarrollador:** _______________ (Tel: _______________)

**DevOps:** _______________ (Tel: _______________)

**Soporte:** _______________ (Tel: _______________)

---

## NOTAS IMPORTANTES

⚠️ **NO desplegar en:**
- Viernes después de las 3 PM
- Fines de semana
- Días festivos
- Horarios de alto tráfico

✅ **Mejor momento para desplegar:**
- Martes o Miércoles
- Entre 10 AM - 2 PM
- Con todo el equipo disponible
- Con tiempo para monitorear

🔄 **Rollback disponible en:** < 5 minutos

📞 **Soporte disponible:** 24/7

---

**IMPORTANTE:** Este checklist debe completarse COMPLETAMENTE antes de considerar el despliegue exitoso.
