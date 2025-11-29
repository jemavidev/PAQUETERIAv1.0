# 🚨 Solución Error 502 en Staging

**Fecha:** 2025-11-28  
**Error:** 502 Bad Gateway  
**Causa:** El servidor backend no está respondiendo

---

## 🔍 Diagnóstico Rápido

### Paso 1: Ejecutar Script de Diagnóstico

```bash
cd /ruta/al/proyecto
./diagnostico-staging.sh
```

Este script te mostrará:
- Estado de contenedores Docker
- Logs recientes
- Puertos en uso
- Espacio en disco
- Memoria disponible

---

## 🛠️ Soluciones Comunes

### Solución 1: Contenedores Caídos (Más Común)

**Síntoma:** `docker-compose ps` muestra contenedores "Exit" o no muestra nada

**Solución:**
```bash
cd /ruta/al/proyecto

# Ver estado
docker-compose -f docker-compose.staging.yml ps

# Reiniciar contenedores
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.staging.yml logs -f
```

---

### Solución 2: Error en el Código (Sintaxis Python)

**Síntoma:** Logs muestran errores de Python (SyntaxError, ImportError, etc.)

**Solución:**
```bash
# Ver logs específicos del contenedor web
docker-compose -f docker-compose.staging.yml logs web

# Si hay error de sintaxis, hacer rollback
git log --oneline -5
git reset --hard <commit-anterior-que-funcionaba>
docker-compose -f docker-compose.staging.yml restart
```

---

### Solución 3: Puerto Ocupado

**Síntoma:** Error "port already in use" o "address already in use"

**Solución:**
```bash
# Ver qué está usando el puerto
sudo netstat -tulpn | grep :80
# o
sudo ss -tulpn | grep :80

# Matar proceso que ocupa el puerto
sudo kill -9 <PID>

# Reiniciar contenedores
docker-compose -f docker-compose.staging.yml restart
```

---

### Solución 4: Sin Espacio en Disco

**Síntoma:** `df -h` muestra 100% de uso

**Solución:**
```bash
# Ver espacio
df -h

# Limpiar logs de Docker
docker system prune -a --volumes -f

# Limpiar logs del sistema
sudo journalctl --vacuum-time=3d

# Limpiar archivos temporales
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Reiniciar contenedores
docker-compose -f docker-compose.staging.yml restart
```

---

### Solución 5: Sin Memoria RAM

**Síntoma:** `free -h` muestra 0 disponible, servidor muy lento

**Solución:**
```bash
# Ver memoria
free -h

# Reiniciar contenedores (libera memoria)
docker-compose -f docker-compose.staging.yml restart

# Si no es suficiente, reiniciar servidor
sudo reboot
```

---

### Solución 6: Base de Datos No Responde

**Síntoma:** Logs muestran "connection refused" o "database error"

**Solución:**
```bash
# Ver estado de contenedor de DB
docker-compose -f docker-compose.staging.yml ps db

# Reiniciar solo la DB
docker-compose -f docker-compose.staging.yml restart db

# Ver logs de DB
docker-compose -f docker-compose.staging.yml logs db

# Si no funciona, reiniciar todo
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d
```

---

### Solución 7: Nginx Mal Configurado

**Síntoma:** Nginx está corriendo pero devuelve 502

**Solución:**
```bash
# Verificar configuración de Nginx
sudo nginx -t

# Si hay error, revisar archivo de configuración
sudo nano /etc/nginx/sites-available/staging

# Reiniciar Nginx
sudo systemctl restart nginx

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

---

## 🚀 Solución Rápida (Reinicio Completo)

Si no tienes tiempo para diagnosticar, haz un reinicio completo:

```bash
cd /ruta/al/proyecto

# 1. Detener todo
docker-compose -f docker-compose.staging.yml down

# 2. Limpiar (opcional, si hay problemas persistentes)
docker system prune -f

# 3. Reconstruir (opcional, si cambiaste código)
docker-compose -f docker-compose.staging.yml build --no-cache

# 4. Iniciar
docker-compose -f docker-compose.staging.yml up -d

# 5. Ver logs
docker-compose -f docker-compose.staging.yml logs -f
```

**Tiempo estimado:** 2-3 minutos

---

## 🔍 Verificar que Funciona

Después de aplicar la solución:

```bash
# 1. Ver estado de contenedores
docker-compose -f docker-compose.staging.yml ps
# Todos deben estar "Up"

# 2. Ver logs (no debe haber errores)
docker-compose -f docker-compose.staging.yml logs --tail=50

# 3. Probar endpoint
curl http://localhost:8000/
# o
curl http://tu-dominio-staging.com/

# 4. Verificar en navegador
# Abrir: http://tu-dominio-staging.com/
```

---

## 📋 Checklist de Verificación

Después de solucionar el 502:

- [ ] Contenedores corriendo (`docker-compose ps`)
- [ ] Sin errores en logs (`docker-compose logs`)
- [ ] Puertos correctos (`netstat` o `ss`)
- [ ] Espacio en disco >10% libre (`df -h`)
- [ ] Memoria disponible >500MB (`free -h`)
- [ ] Nginx funcionando (si aplica)
- [ ] Base de datos respondiendo
- [ ] Página carga en navegador
- [ ] No hay error 502

---

## 🆘 Si Nada Funciona

### Opción 1: Rollback a Versión Anterior

```bash
cd /ruta/al/proyecto

# Ver commits recientes
git log --oneline -10

# Volver a commit que funcionaba
git reset --hard <commit-hash>

# Reiniciar contenedores
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d --build
```

### Opción 2: Reiniciar Servidor Completo

```bash
sudo reboot
```

Después del reinicio:
```bash
cd /ruta/al/proyecto
docker-compose -f docker-compose.staging.yml up -d
```

### Opción 3: Revisar Logs Detallados

```bash
# Logs de Docker
docker-compose -f docker-compose.staging.yml logs --tail=200

# Logs del sistema
sudo journalctl -xe

# Logs de Nginx (si aplica)
sudo tail -100 /var/log/nginx/error.log

# Logs de aplicación
tail -100 /ruta/al/proyecto/logs/*.log
```

---

## 📞 Comandos de Emergencia

```bash
# Ver todo el estado del sistema
./diagnostico-staging.sh

# Reinicio rápido
docker-compose -f docker-compose.staging.yml restart

# Reinicio completo
docker-compose -f docker-compose.staging.yml down && \
docker-compose -f docker-compose.staging.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.staging.yml logs -f

# Entrar al contenedor para debugging
docker-compose -f docker-compose.staging.yml exec web bash
```

---

## 🎯 Causa Más Probable del 502

En orden de probabilidad:

1. **Contenedores caídos** (70%) → Reiniciar contenedores
2. **Error en código nuevo** (15%) → Rollback o fix
3. **Puerto ocupado** (5%) → Liberar puerto
4. **Sin recursos** (5%) → Limpiar o reiniciar
5. **Nginx mal configurado** (3%) → Revisar config
6. **Base de datos caída** (2%) → Reiniciar DB

---

## 💡 Prevención Futura

Para evitar 502 en el futuro:

1. **Siempre probar en local** antes de push
2. **Usar el script de reset** para deployment limpio
3. **Monitorear recursos** (espacio, memoria)
4. **Revisar logs** después de cada deployment
5. **Tener backup** de última versión funcional

---

## 🚀 Acción Inmediata

**AHORA MISMO, ejecuta:**

```bash
cd /ruta/al/proyecto
./diagnostico-staging.sh
```

Esto te dirá exactamente qué está mal. Luego aplica la solución correspondiente de arriba.

**Si ves contenedores caídos, ejecuta:**
```bash
docker-compose -f docker-compose.staging.yml up -d
```

**Eso debería solucionar el 502 en el 90% de los casos.** 🎯
