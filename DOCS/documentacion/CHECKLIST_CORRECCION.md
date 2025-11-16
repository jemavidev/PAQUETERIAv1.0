# ✅ Checklist de Corrección de Imágenes

## 📋 Antes de Empezar

- [ ] He leído `INICIO_RAPIDO_CORRECCION.md`
- [ ] Tengo acceso SSH al servidor
- [ ] Conozco la IP del servidor
- [ ] Tengo las credenciales correctas
- [ ] He creado un backup (opcional pero recomendado)

## 🔍 Diagnóstico Inicial

- [ ] Ejecuté `./diagnose-static-files.sh`
- [ ] Confirmé que las imágenes no son accesibles (404)
- [ ] Verifiqué que los archivos existen en `CODE/src/static/images/`
- [ ] Revisé los logs del contenedor

## 🚀 Aplicación de la Corrección

### Opción A: Usando el Menú Interactivo

- [ ] Ejecuté `./menu-correccion-imagenes.sh`
- [ ] Seleccioné opción 4 (Desplegar al servidor)
- [ ] Ingresé la IP del servidor
- [ ] Ingresé el usuario SSH
- [ ] Confirmé la configuración
- [ ] El script se ejecutó sin errores

### Opción B: Usando el Script Directo

- [ ] Ejecuté `./deploy-static-fix-to-server.sh`
- [ ] Ingresé la IP del servidor
- [ ] Ingresé el usuario SSH
- [ ] Confirmé la configuración
- [ ] El script creó el backup
- [ ] Los archivos se subieron correctamente
- [ ] Los contenedores se reconstruyeron
- [ ] Los contenedores iniciaron correctamente

### Opción C: Manual

- [ ] Me conecté al servidor vía SSH
- [ ] Navegué al directorio del proyecto
- [ ] Creé backup de `docker-compose.lightsail.yml`
- [ ] Actualicé los archivos de configuración
- [ ] Ejecuté `docker compose down`
- [ ] Ejecuté `docker compose build --no-cache app`
- [ ] Ejecuté `docker compose up -d`
- [ ] Verifiqué que los contenedores estén corriendo

## ✅ Verificación Post-Despliegue

### Verificación desde Línea de Comandos

- [ ] Health check responde 200:
  ```bash
  curl http://SERVIDOR:8000/health
  ```

- [ ] Favicon es accesible (200):
  ```bash
  curl -I http://SERVIDOR:8000/static/images/favicon.png
  ```

- [ ] Logo es accesible (200):
  ```bash
  curl -I http://SERVIDOR:8000/static/images/logo.png
  ```

- [ ] CSS es accesible (200):
  ```bash
  curl -I http://SERVIDOR:8000/static/css/main.css
  ```

### Verificación desde el Navegador

- [ ] Abrí la aplicación en el navegador
- [ ] Presioné F12 (herramientas de desarrollo)
- [ ] Fui a la pestaña "Network" o "Red"
- [ ] Recargué la página (Ctrl+R)
- [ ] No hay errores 404 en archivos estáticos
- [ ] Las imágenes se visualizan correctamente
- [ ] El favicon aparece en la pestaña
- [ ] El logo se muestra en la página

### Verificación de Contenedores

- [ ] Los contenedores están corriendo:
  ```bash
  docker ps
  ```

- [ ] No hay errores en los logs:
  ```bash
  docker logs paqueteria_app --tail 50
  ```

- [ ] La estructura de directorios es correcta:
  ```bash
  docker exec paqueteria_app ls -lh /app/src/static/images/
  ```

## 🎉 Confirmación Final

- [ ] ✅ Las imágenes se visualizan en el servidor
- [ ] ✅ No hay errores 404 en la consola
- [ ] ✅ Los contenedores están estables
- [ ] ✅ Los logs no muestran errores
- [ ] ✅ La aplicación funciona correctamente

## 🐛 Si Algo Salió Mal

### Las imágenes aún no se ven

- [ ] Limpié el caché del navegador (Ctrl+Shift+R)
- [ ] Verifiqué los logs: `docker logs paqueteria_app`
- [ ] Verifiqué la estructura: `docker exec paqueteria_app ls -lh /app/src/static/`
- [ ] Revisé los permisos de archivos
- [ ] Ejecuté el diagnóstico nuevamente

### Error de conexión SSH

- [ ] Verifiqué la IP del servidor
- [ ] Verifiqué las credenciales
- [ ] Verifiqué que el puerto SSH esté abierto
- [ ] Probé la conexión: `ssh usuario@servidor`

### Contenedores no inician

- [ ] Revisé los logs: `docker compose logs`
- [ ] Verifiqué la sintaxis: `docker compose config`
- [ ] Reconstruí sin caché: `docker compose build --no-cache`
- [ ] Verifiqué el espacio en disco: `df -h`

### Otros problemas

- [ ] Consulté `DOCS/SOLUCION_IMAGENES_ESTATICAS.md`
- [ ] Ejecuté el menú y seleccioné "Ayuda" (opción 6)
- [ ] Revisé los logs completos
- [ ] Restauré el backup si es necesario

## 📝 Notas

Fecha de aplicación: _______________

Hora de inicio: _______________

Hora de finalización: _______________

Problemas encontrados:
_____________________________________________
_____________________________________________
_____________________________________________

Soluciones aplicadas:
_____________________________________________
_____________________________________________
_____________________________________________

## 🎯 Resultado Final

- [ ] ✅ ÉXITO - Todo funciona correctamente
- [ ] ⚠️  PARCIAL - Funciona pero con advertencias
- [ ] ❌ FALLO - Necesita más investigación

---

**Firma:** _______________  
**Fecha:** _______________
