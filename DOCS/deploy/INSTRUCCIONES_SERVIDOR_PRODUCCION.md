# 🚀 Instrucciones para Actualizar Servidor de Producción

## ✅ Cambios Subidos a GitHub

Los siguientes archivos ya están en GitHub:

- ✅ `CODE/src/templates/general/terms.html` (Template de Términos y Condiciones)
- ✅ `CODE/src/templates/general/privacy.html` (Template de Políticas de Privacidad)
- ✅ Rutas configuradas en `CODE/src/app/routes/public.py`
- ✅ Scripts de verificación y sincronización

## 🎯 Pasos en el Servidor de Producción

### Opción 1: Script Automático (Recomendado)

Conéctate al servidor y ejecuta:

```bash
# 1. Ir al directorio del proyecto
cd /ruta/al/proyecto

# 2. Hacer pull de los cambios
git pull origin main

# 3. Ejecutar el script de actualización
chmod +x actualizar-produccion.sh
./actualizar-produccion.sh
```

El script hará automáticamente:
- ✅ Pull de GitHub
- ✅ Verificación de templates
- ✅ Configuración de permisos
- ✅ Reinicio del contenedor
- ✅ Verificación de endpoints
- ✅ Mostrar logs

### Opción 2: Manual (Paso a Paso)

```bash
# 1. Conectarse al servidor
ssh usuario@servidor-produccion

# 2. Ir al directorio del proyecto
cd /ruta/al/proyecto

# 3. Hacer pull de GitHub
git pull origin main

# 4. Verificar que los archivos existen
ls -lh CODE/src/templates/general/terms.html
ls -lh CODE/src/templates/general/privacy.html

# 5. Configurar permisos
chmod 644 CODE/src/templates/general/terms.html
chmod 644 CODE/src/templates/general/privacy.html

# 6. Reiniciar el contenedor
docker compose -f docker-compose.prod.yml restart app

# 7. Esperar 10 segundos
sleep 10

# 8. Verificar que funciona
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
```

## 🔍 Verificación

Después de ejecutar los pasos, verifica que los endpoints respondan:

```bash
# Debe responder "HTTP/1.1 200 OK"
curl -I http://localhost:8000/terms
curl -I http://localhost:8000/privacy
curl -I http://localhost:8000/help
```

## 🌐 URLs Finales

Una vez actualizado, las siguientes URLs estarán disponibles:

- `https://tu-dominio.com/terms` - Términos y Condiciones
- `https://tu-dominio.com/privacy` - Políticas de Privacidad
- `https://tu-dominio.com/help` - Centro de Ayuda (con enlaces a las anteriores)

## 🆘 Solución de Problemas

### Si los endpoints no responden (404)

```bash
# Ver logs del contenedor
docker logs paqueteria_v1_prod_app

# Verificar que los archivos están en el contenedor
docker exec paqueteria_v1_prod_app ls -lh /app/src/templates/general/

# Reiniciar todo el stack
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

### Si los archivos no están sincronizados

```bash
# Verificar volúmenes montados
docker inspect paqueteria_v1_prod_app | grep -A 20 "Mounts"

# Reconstruir el contenedor (última opción)
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml build --no-cache app
docker compose -f docker-compose.prod.yml up -d
```

## 📞 Soporte

Si después de seguir estos pasos los templates no funcionan:

1. Ejecuta el script de verificación:
   ```bash
   ./verificar-templates.sh
   ```

2. Revisa la documentación completa:
   - `DOCS/SOLUCION_SINCRONIZACION_TEMPLATES.md`
   - `ARREGLAR_TEMPLATES_PRODUCCION.md`

3. Contacta al equipo de desarrollo con:
   - Salida del script de verificación
   - Logs del contenedor
   - Código de respuesta HTTP de los endpoints

---

**Tiempo estimado:** 5 minutos  
**Requiere:** Acceso SSH al servidor  
**Última actualización:** 2025-11-21
