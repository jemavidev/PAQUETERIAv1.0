# 🎯 Solución Simple Final - Sincronización Staging

**Fecha:** 27 de enero de 2026  
**Problema:** Demasiada complejidad con archivos señal y monitor externo  
**Solución:** Instalar PostgreSQL client en el contenedor y ejecutar directamente

---

## 💡 Análisis del Problema

### ❌ Solución Anterior (Compleja)
```
Navegador → App → Archivo señal → Monitor en host → Docker → Sincronización
```
**Problemas:**
- Requiere montar volúmenes
- Requiere servicio systemd en el host
- Requiere permisos Docker en el host
- Muchos puntos de falla

### ✅ Solución Nueva (Simple)
```
Navegador → App → Ejecuta pg_dump/pg_restore directamente → Sincronización
```
**Ventajas:**
- Todo dentro del contenedor
- No requiere archivos señal
- No requiere monitor externo
- No requiere montar /tmp
- Mucho más simple

---

## 🚀 Implementación Simple

### Paso 1: Actualizar Dockerfile

Agregar PostgreSQL client al Dockerfile:

```dockerfile
# Instalar dependencias del sistema (incluyendo PostgreSQL client)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    nodejs \
    npm \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

### Paso 2: Actualizar el código Python

Modificar `sync_staging.py` para ejecutar pg_dump/pg_restore directamente:

```python
import subprocess
import os

async def run_sync():
    """
    Ejecuta la sincronización directamente usando pg_dump y pg_restore
    """
    global sync_status
    
    try:
        sync_status["is_running"] = True
        sync_status["progress"] = 10
        sync_status["message"] = "Iniciando sincronización..."
        
        # Credenciales
        host = os.getenv("POSTGRES_HOST")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        
        # Configurar PGPASSWORD
        env = os.environ.copy()
        env["PGPASSWORD"] = password
        
        # Exportar producción
        sync_status["progress"] = 30
        sync_status["message"] = "Exportando producción..."
        
        dump_cmd = [
            "pg_dump",
            "-h", host,
            "-U", user,
            "-d", "paqueteria_v4",
            "-F", "c",
            "-f", "/tmp/backup.dump",
            "--no-owner",
            "--no-acl"
        ]
        
        subprocess.run(dump_cmd, env=env, check=True)
        
        # Restaurar en staging
        sync_status["progress"] = 70
        sync_status["message"] = "Restaurando en staging..."
        
        restore_cmd = [
            "pg_restore",
            "-h", host,
            "-U", user,
            "-d", "paqueteria_staging",
            "/tmp/backup.dump",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-acl"
        ]
        
        subprocess.run(restore_cmd, env=env, check=True, stderr=subprocess.DEVNULL)
        
        # Limpiar
        os.remove("/tmp/backup.dump")
        
        sync_status["progress"] = 100
        sync_status["last_result"] = "success"
        sync_status["message"] = "Sincronización completada"
        
    except Exception as e:
        sync_status["last_result"] = f"error: {str(e)}"
        sync_status["message"] = str(e)
    finally:
        sync_status["is_running"] = False
```

---

## 📝 Archivos a Modificar

### 1. `CODE/Dockerfile`
```dockerfile
# Línea 8-12, cambiar:
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    nodejs \
    npm \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*
```

### 2. `CODE/src/app/routes/sync_staging.py`
Reemplazar la función `run_sync()` con la versión que usa subprocess.

---

## 🚀 Aplicar la Solución

### Opción A: Reconstruir la imagen (Recomendado)

```bash
# 1. Actualizar archivos localmente
# - Modificar CODE/Dockerfile
# - Modificar CODE/src/app/routes/sync_staging.py

# 2. Subir al servidor
scp CODE/Dockerfile staging:~/paqueteria-staging/CODE/
scp CODE/src/app/routes/sync_staging.py staging:~/paqueteria-staging/CODE/src/app/routes/

# 3. Reconstruir en el servidor
ssh staging
cd ~/paqueteria-staging
docker-compose -f docker-compose.staging.yml build app
docker-compose -f docker-compose.staging.yml up -d app
```

### Opción B: Instalar PostgreSQL client sin reconstruir

```bash
# 1. Conectar al contenedor
ssh staging
docker exec -it paqueteria_staging_app bash

# 2. Instalar PostgreSQL client
apt-get update
apt-get install -y postgresql-client

# 3. Probar
pg_dump --version

# 4. Salir
exit

# 5. Actualizar solo el código Python
scp CODE/src/app/routes/sync_staging.py staging:~/paqueteria-staging/CODE/src/app/routes/

# 6. Reiniciar app
ssh staging
cd ~/paqueteria-staging
docker-compose -f docker-compose.staging.yml restart app
```

---

## ✅ Ventajas de Esta Solución

1. **Simple**: Todo en un solo lugar (el contenedor)
2. **Sin dependencias externas**: No requiere monitor en el host
3. **Sin archivos señal**: Comunicación directa
4. **Sin volúmenes especiales**: No necesita montar /tmp
5. **Fácil de debuggear**: Logs en un solo lugar
6. **Más rápido**: Sin intermediarios

---

## 🐛 Troubleshooting

### Error: "pg_dump: command not found"
```bash
# Instalar en el contenedor
docker exec -it paqueteria_staging_app bash
apt-get update && apt-get install -y postgresql-client
```

### Error: "connection refused"
```bash
# Verificar credenciales en .env.staging
cat ~/paqueteria-staging/.env.staging | grep POSTGRES
```

### Ver logs
```bash
# Logs del contenedor
docker logs -f paqueteria_staging_app

# Logs de la app
docker exec paqueteria_staging_app cat /app/logs/app.log
```

---

## 📊 Comparación

| Aspecto | Solución Anterior | Solución Nueva |
|---------|-------------------|----------------|
| Complejidad | Alta (5 componentes) | Baja (1 componente) |
| Puntos de falla | 5+ | 1 |
| Archivos a modificar | 10+ | 2 |
| Requiere systemd | Sí | No |
| Requiere Docker en host | Sí | No |
| Requiere montar volúmenes | Sí | No |
| Tiempo de setup | 30 min | 5 min |
| Facilidad de debug | Difícil | Fácil |

---

## 🎉 Resultado

Con esta solución:
- ✅ Click en botón → Sincronización directa
- ✅ Sin archivos señal
- ✅ Sin monitor externo
- ✅ Sin problemas de permisos
- ✅ Mucho más simple y confiable

---

**Recomendación:** Usar esta solución simple en lugar de la compleja anterior.
