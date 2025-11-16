# 🔧 Corrección: Imágenes no se visualizan en el servidor

## 📋 Resumen Ejecutivo

**Problema:** Las imágenes y archivos estáticos no se visualizan en el servidor de producción, aunque funcionan correctamente en localhost.

**Causa:** Configuración incorrecta de volúmenes en Docker que montaba los archivos estáticos en una ubicación diferente a la esperada por FastAPI.

**Solución:** Eliminación del montaje redundante de archivos estáticos en los archivos docker-compose.

**Estado:** ✅ Solucionado y listo para desplegar

---

## 🚀 Aplicar la Solución (3 opciones)

### Opción 1: Despliegue Automático al Servidor (Recomendado)

```bash
./deploy-static-fix-to-server.sh
```

Este script:
- Se conecta al servidor vía SSH
- Crea un backup de la configuración actual
- Sube los archivos corregidos
- Aplica la corrección automáticamente
- Verifica que todo funcione correctamente

### Opción 2: Despliegue Local (para pruebas)

```bash
./redeploy-with-static-fix.sh
```

Úsalo para probar la corrección en tu máquina local antes de desplegar al servidor.

### Opción 3: Manual

Si prefieres hacerlo paso a paso:

```bash
# 1. Conectarse al servidor
ssh usuario@servidor

# 2. Ir al directorio del proyecto
cd /ruta/al/proyecto

# 3. Crear backup
cp docker-compose.lightsail.yml docker-compose.lightsail.yml.backup

# 4. Actualizar archivos (git pull o copiar manualmente)

# 5. Redesplegar
docker compose -f docker-compose.lightsail.yml down
docker compose -f docker-compose.lightsail.yml build --no-cache app
docker compose -f docker-compose.lightsail.yml up -d

# 6. Verificar
curl -I http://localhost:8000/static/images/favicon.png
```

---

## 🔍 Diagnóstico (antes de aplicar)

Para verificar el problema actual sin hacer cambios:

```bash
./diagnose-static-files.sh
```

Este script muestra:
- Estado de los contenedores
- Estructura de directorios
- Montajes de volúmenes
- Accesibilidad de archivos estáticos
- Logs recientes

---

## ✅ Verificación Post-Despliegue

Después de aplicar la solución, verifica:

### 1. Desde la línea de comandos:

```bash
# Health check
curl http://TU_SERVIDOR:8000/health

# Favicon
curl -I http://TU_SERVIDOR:8000/static/images/favicon.png

# Logo
curl -I http://TU_SERVIDOR:8000/static/images/logo.png

# CSS
curl -I http://TU_SERVIDOR:8000/static/css/main.css
```

Todos deben retornar `HTTP/1.1 200 OK`

### 2. Desde el navegador:

1. Abre la aplicación: `http://TU_SERVIDOR:8000`
2. Presiona F12 (herramientas de desarrollo)
3. Ve a la pestaña "Network" o "Red"
4. Recarga la página (Ctrl+R)
5. Verifica que no haya errores 404 en archivos estáticos

---

## 📝 Cambios Realizados

### Archivos Modificados:

1. **docker-compose.prod.yml**
   - ❌ Eliminado: `- ./CODE/src/static:/app/static`
   - ✅ Mantiene: `- ./CODE/src:/app/src`

2. **docker-compose.lightsail.yml**
   - ❌ Eliminado: `- ./CODE/src/static:/app/static:ro`
   - ✅ Mantiene: `- ./CODE/src:/app/src:ro`

3. **CODE/nginx/nginx.lightsail.conf**
   - ✅ Agregado: Logs de debug para archivos estáticos

### Archivos Creados:

- `diagnose-static-files.sh` - Script de diagnóstico
- `fix-static-files.sh` - Script de corrección rápida
- `redeploy-with-static-fix.sh` - Script de redespliegue completo
- `deploy-static-fix-to-server.sh` - Script para desplegar al servidor
- `DOCS/SOLUCION_IMAGENES_ESTATICAS.md` - Documentación detallada

---

## 🐛 Troubleshooting

### Problema: Archivos aún no se ven después de aplicar la corrección

**Solución 1:** Limpiar caché del navegador
```
Ctrl+Shift+R (Windows/Linux)
Cmd+Shift+R (Mac)
```

**Solución 2:** Verificar logs del contenedor
```bash
docker logs paqueteria_app --tail 100
```

**Solución 3:** Verificar estructura en el contenedor
```bash
docker exec paqueteria_app ls -lh /app/src/static/images/
```

### Problema: Error de conexión SSH al servidor

**Solución:** Verifica:
- La IP del servidor es correcta
- Tienes acceso SSH configurado
- El puerto SSH está abierto (default: 22)
- Las credenciales son correctas

### Problema: Contenedores no inician después del cambio

**Solución:** Revisa los logs
```bash
docker compose -f docker-compose.lightsail.yml logs
```

---

## 📚 Documentación Adicional

Para más detalles técnicos, consulta:
- `DOCS/SOLUCION_IMAGENES_ESTATICAS.md` - Documentación completa
- `CODE/src/main.py` - Configuración de FastAPI
- `CODE/nginx/nginx.lightsail.conf` - Configuración de Nginx

---

## 🎯 Checklist de Despliegue

Antes de desplegar:
- [ ] He leído este documento
- [ ] He ejecutado el diagnóstico (`./diagnose-static-files.sh`)
- [ ] He probado la solución localmente (opcional)
- [ ] Tengo acceso SSH al servidor
- [ ] He creado un backup de la configuración actual

Durante el despliegue:
- [ ] Los archivos se subieron correctamente
- [ ] Los contenedores se reconstruyeron sin errores
- [ ] Los contenedores están corriendo (`docker ps`)

Después del despliegue:
- [ ] El health check responde 200
- [ ] Los archivos estáticos son accesibles (curl)
- [ ] Las imágenes se ven en el navegador
- [ ] No hay errores 404 en la consola del navegador
- [ ] Los logs no muestran errores

---

## 💡 Comandos Útiles

```bash
# Ver estado de contenedores
docker compose -f docker-compose.lightsail.yml ps

# Ver logs en tiempo real
docker logs -f paqueteria_app

# Reiniciar solo la aplicación
docker compose -f docker-compose.lightsail.yml restart app

# Detener todo
docker compose -f docker-compose.lightsail.yml down

# Ver uso de recursos
docker stats

# Ejecutar comando en el contenedor
docker exec paqueteria_app ls -lh /app/src/static/
```

---

## 📞 Soporte

Si después de aplicar la solución sigues teniendo problemas:

1. Ejecuta el diagnóstico y guarda la salida:
   ```bash
   ./diagnose-static-files.sh > diagnostico.txt
   ```

2. Revisa los logs completos:
   ```bash
   docker logs paqueteria_app > logs.txt
   ```

3. Verifica la configuración de Nginx (si aplica):
   ```bash
   sudo nginx -t
   sudo tail -f /var/log/nginx/error.log
   ```

---

**Fecha:** 2025-01-24  
**Versión:** 1.0  
**Estado:** ✅ Listo para desplegar
