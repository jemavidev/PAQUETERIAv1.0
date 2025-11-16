# 🚀 Guía de Desarrollo y Despliegue

## 📋 Configuración Sincronizada

Ambos entornos (localhost y servidor) ahora usan la **misma configuración** para evitar problemas al desplegar.

### ✅ Configuración Correcta de Volúmenes

```yaml
volumes:
  - ./CODE/src:/app/src          # ✅ Un solo montaje del código fuente
  - uploads_data:/app/uploads    # ✅ Archivos subidos
  - logs_data:/app/logs          # ✅ Logs
```

### ❌ Configuración Incorrecta (NO USAR)

```yaml
volumes:
  - ./CODE/src:/app/src
  - ./CODE/src/static:/app/static  # ❌ MONTAJE REDUNDANTE - CAUSA PROBLEMAS
  - uploads_data:/app/uploads
```

## 🔄 Flujo de Trabajo

### 1. Desarrollo en Localhost

```bash
# Iniciar contenedores de desarrollo
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker logs -f paqueteria_v1_prod_app

# Detener contenedores
docker compose -f docker-compose.prod.yml down
```

### 2. Verificar Configuración Antes de Desplegar

```bash
# Ejecutar script de verificación
./sync-configs.sh
```

Este script verifica que:
- ✅ No haya montajes redundantes
- ✅ Ambos archivos docker-compose estén sincronizados
- ✅ La configuración sea correcta

### 3. Desplegar al Servidor

```bash
# Opción A: Despliegue automático
./deploy-to-papyrus.sh

# Opción B: Despliegue manual
scp docker-compose.prod.yml papyrus:/home/ubuntu/paqueteria/
ssh papyrus "cd /home/ubuntu/paqueteria && docker compose -f docker-compose.prod.yml up -d"
```

## 📁 Archivos de Configuración

### Localhost (Desarrollo)
- **Archivo:** `docker-compose.prod.yml`
- **Uso:** Desarrollo local con hot reload
- **Puerto:** `127.0.0.1:8000`
- **Características:**
  - Hot reload habilitado (`--reload`)
  - Volúmenes sin `:ro` para permitir cambios
  - Incluye Prometheus y Grafana para monitoreo

### Servidor (Producción)
- **Archivo:** `docker-compose.prod.yml` (mismo archivo)
- **Uso:** Producción en AWS Lightsail
- **Puerto:** `127.0.0.1:8000` (accesible vía Nginx)
- **Características:**
  - Configuración optimizada
  - Volúmenes en modo read-only donde sea posible
  - Nginx como reverse proxy

## 🔍 Verificación de Archivos Estáticos

### En Localhost

```bash
# Verificar que las imágenes sean accesibles
curl -I http://localhost:8000/static/images/favicon.png
curl -I http://localhost:8000/static/images/logo.png

# Debe retornar: HTTP/1.1 200 OK
```

### En el Servidor

```bash
# Verificar que las imágenes sean accesibles
curl -I https://paquetex.papyrus.com.co/static/images/favicon.png
curl -I https://paquetex.papyrus.com.co/static/images/logo.png

# Debe retornar: HTTP/1.1 200 OK
```

## 🛠️ Solución de Problemas

### Problema: Imágenes no se visualizan después de desplegar

**Solución:**
1. Verificar configuración:
   ```bash
   ./sync-configs.sh
   ```

2. Si hay montajes redundantes, eliminarlos:
   ```bash
   # Editar docker-compose.prod.yml
   # Eliminar la línea: - ./CODE/src/static:/app/static
   ```

3. Recrear contenedores:
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml up -d
   ```

### Problema: Cambios en localhost no se reflejan en el servidor

**Causa:** Los archivos docker-compose están desincronizados

**Solución:**
1. Verificar sincronización:
   ```bash
   ./sync-configs.sh
   ```

2. Asegurarse de usar el mismo archivo en ambos entornos

### Problema: Error 502 Bad Gateway en el servidor

**Causa:** Problema con el proxy de Docker o Nginx

**Solución:**
1. Verificar que el contenedor esté corriendo:
   ```bash
   ssh papyrus "docker ps | grep paqueteria"
   ```

2. Verificar logs:
   ```bash
   ssh papyrus "docker logs paqueteria_v1_prod_app --tail 50"
   ```

3. Reiniciar contenedores:
   ```bash
   ssh papyrus "cd /home/ubuntu/paqueteria && docker compose -f docker-compose.prod.yml restart app"
   ```

## 📊 Estructura de Directorios

```
/app/                           # Dentro del contenedor
├── src/                        # Código fuente (montado desde host)
│   ├── static/                 # Archivos estáticos
│   │   ├── css/
│   │   ├── images/            # ← Imágenes servidas por FastAPI
│   │   └── js/
│   ├── templates/
│   └── main.py
├── uploads/                    # Archivos subidos (volumen Docker)
└── logs/                       # Logs (volumen Docker)
```

## 🎯 Puntos Clave

1. **Un solo montaje:** Solo monta `./CODE/src:/app/src`, no montes `/app/static` por separado
2. **Misma configuración:** Usa `docker-compose.prod.yml` en ambos entornos
3. **Verificar antes de desplegar:** Ejecuta `./sync-configs.sh` antes de cada despliegue
4. **FastAPI sirve los estáticos:** Los archivos en `/app/src/static/` son servidos por FastAPI
5. **Nginx hace proxy:** En el servidor, Nginx hace proxy a FastAPI para servir todo

## 📝 Checklist de Despliegue

Antes de cada despliegue, verifica:

- [ ] Ejecuté `./sync-configs.sh` y todo está correcto
- [ ] Los cambios funcionan correctamente en localhost
- [ ] Las imágenes se visualizan en localhost
- [ ] No hay errores en los logs locales
- [ ] He hecho commit de los cambios en git (opcional pero recomendado)
- [ ] Tengo backup de la configuración del servidor (opcional)

Durante el despliegue:

- [ ] Subí los archivos al servidor
- [ ] Recreé los contenedores
- [ ] Verifiqué que los contenedores estén corriendo
- [ ] Probé el acceso a la aplicación
- [ ] Verifiqué que las imágenes se visualicen

Después del despliegue:

- [ ] La aplicación responde correctamente
- [ ] Las imágenes se visualizan
- [ ] No hay errores 502 o 404
- [ ] Los logs no muestran errores

## 🔗 Scripts Útiles

- `sync-configs.sh` - Verificar sincronización de configuraciones
- `deploy-to-papyrus.sh` - Desplegar al servidor automáticamente
- `diagnose-server-deep.sh` - Diagnóstico profundo del servidor
- `test-static-access.sh` - Probar acceso a archivos estáticos

## 💡 Mejores Prácticas

1. **Siempre verifica localmente primero:** Prueba todos los cambios en localhost antes de desplegar
2. **Usa el script de sincronización:** Ejecuta `./sync-configs.sh` antes de cada despliegue
3. **Mantén las configuraciones idénticas:** No hagas cambios manuales sin actualizar ambos archivos
4. **Documenta los cambios:** Si modificas la configuración, actualiza esta guía
5. **Haz backups:** Antes de cambios importantes, crea backups de la configuración

---

**Última actualización:** 2025-11-16  
**Versión:** 1.0  
**Estado:** ✅ Configuración sincronizada y funcionando
