# 🔍 Diagnóstico y Solución - Imágenes no se visualizan

## 📋 Paso 1: Ejecutar Diagnóstico Profundo

Primero, necesitamos identificar exactamente dónde está el problema:

```bash
./diagnose-server-deep.sh
```

Este script te pedirá:
- IP del servidor (o 'local' para localhost)
- Usuario SSH (si es remoto)

Y verificará:
1. ✅ Estado de contenedores
2. ✅ Estructura de directorios
3. ✅ Montajes de volúmenes
4. ✅ Permisos de archivos
5. ✅ Acceso HTTP
6. ✅ Logs de la aplicación
7. ✅ Configuración de FastAPI
8. ✅ Configuración de Nginx
9. ✅ Pruebas desde dentro del contenedor
10. ✅ Resumen y recomendaciones

## 📋 Paso 2: Test de Acceso Específico

Para identificar si el problema es con Nginx o FastAPI:

```bash
./test-static-access.sh
```

Este script prueba:
- Acceso directo a FastAPI (puerto 8000)
- Acceso a través de Nginx (puerto 80)
- Verificación desde dentro del contenedor
- Análisis de logs

## 🔍 Interpretación de Resultados

### Escenario A: Los archivos NO existen en el contenedor

**Síntomas:**
```
❌ /app/src/static/images/favicon.png... No existe
```

**Causa:** El volumen no está montado correctamente

**Solución:**
1. Verifica que los archivos existan en el host:
   ```bash
   ls -lh CODE/src/static/images/
   ```

2. Si no existen, créalos o cópialos

3. Reconstruye el contenedor:
   ```bash
   docker compose -f docker-compose.lightsail.yml down
   docker compose -f docker-compose.lightsail.yml up -d
   ```

### Escenario B: Los archivos existen pero FastAPI retorna 404

**Síntomas:**
```
✅ /app/src/static/images/favicon.png... Existe
❌ http://localhost:8000/static/images/favicon.png... FALLO (HTTP 404)
```

**Causa:** FastAPI no está configurado correctamente para servir archivos estáticos

**Solución:** Aplica una de las soluciones alternativas:
```bash
./fix-static-alternative.sh
```

### Escenario C: FastAPI funciona pero Nginx no

**Síntomas:**
```
✅ http://servidor:8000/static/images/favicon.png... OK (HTTP 200)
❌ http://servidor/static/images/favicon.png... FALLO (HTTP 404)
```

**Causa:** Nginx no está configurado correctamente

**Solución:**
1. Verifica la configuración de Nginx:
   ```bash
   sudo nginx -t
   ```

2. Revisa los logs de Nginx:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Asegúrate de que Nginx esté haciendo proxy correctamente

### Escenario D: Problemas de permisos

**Síntomas:**
```
✅ /app/src/static/images/favicon.png... Existe
❌ Es legible... No es legible
```

**Causa:** El usuario del contenedor no tiene permisos para leer los archivos

**Solución:**
1. Desde el host, ajusta los permisos:
   ```bash
   chmod -R 755 CODE/src/static/
   ```

2. Reinicia el contenedor:
   ```bash
   docker compose -f docker-compose.lightsail.yml restart app
   ```

## 🛠️ Soluciones Alternativas

Si las soluciones anteriores no funcionan, prueba estas alternativas:

### Solución 1: Copiar archivos en la imagen Docker

Modifica el `Dockerfile` para copiar los archivos estáticos durante el build:

```dockerfile
# Después de COPY src/ /app/src/
COPY src/static/ /app/src/static/
```

Luego reconstruye:
```bash
docker compose -f docker-compose.lightsail.yml build --no-cache app
docker compose -f docker-compose.lightsail.yml up -d
```

### Solución 2: Servir con Nginx directamente

Configura Nginx para servir los archivos directamente desde el host:

```nginx
location /static/ {
    alias /ruta/completa/al/proyecto/CODE/src/static/;
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### Solución 3: Usar un volumen nombrado

Crea un volumen específico para archivos estáticos:

```yaml
volumes:
  - static_data:/app/src/static:ro

volumes:
  static_data:
    driver: local
```

## 📊 Checklist de Verificación

Después de aplicar cualquier solución:

- [ ] Los archivos existen en el host: `ls -lh CODE/src/static/images/`
- [ ] Los archivos existen en el contenedor: `docker exec CONTAINER ls -lh /app/src/static/images/`
- [ ] Los archivos son legibles: `docker exec CONTAINER test -r /app/src/static/images/favicon.png`
- [ ] FastAPI responde 200: `curl -I http://servidor:8000/static/images/favicon.png`
- [ ] Nginx responde 200 (si aplica): `curl -I http://servidor/static/images/favicon.png`
- [ ] Las imágenes se ven en el navegador
- [ ] No hay errores 404 en la consola del navegador

## 🔧 Comandos Útiles

```bash
# Ver logs en tiempo real
docker logs -f paqueteria_app

# Entrar al contenedor
docker exec -it paqueteria_app bash

# Verificar archivos desde dentro
ls -lh /app/src/static/images/

# Probar curl desde dentro
curl -I http://localhost:8000/static/images/favicon.png

# Ver montajes de volúmenes
docker inspect paqueteria_app | grep -A 10 Mounts

# Reiniciar solo la app
docker compose -f docker-compose.lightsail.yml restart app

# Ver logs de Nginx
sudo tail -f /var/log/nginx/error.log
```

## 📞 Siguiente Paso

1. **Ejecuta el diagnóstico:**
   ```bash
   ./diagnose-server-deep.sh
   ```

2. **Guarda la salida completa** y compártela si necesitas ayuda

3. **Identifica el escenario** que coincide con tu problema

4. **Aplica la solución** correspondiente

5. **Verifica** usando el checklist

---

**Nota:** Si después de probar todas las soluciones el problema persiste, es posible que haya un problema más profundo con la configuración del servidor o el firewall.
