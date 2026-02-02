# Cómo Abrir el Proyecto en Localhost

## Opción 1: Usando Docker (Recomendado)

### Requisitos Previos
- Docker y Docker Compose instalados
- Puerto 8000 disponible

### Pasos

1. **Verificar que tienes el archivo .env configurado**
```bash
# El archivo CODE/.env ya está configurado
# Usa la base de datos de staging en AWS RDS
ls -la CODE/.env
```

2. **Levantar el proyecto**
```bash
# Desde la raíz del proyecto
docker compose -f docker-compose.dev.yml up -d
```

3. **Ver los logs (opcional)**
```bash
docker compose -f docker-compose.dev.yml logs -f app
```

4. **Abrir en el navegador**
```
http://localhost:8000
```

5. **Detener el proyecto**
```bash
docker compose -f docker-compose.dev.yml down
```

### Características del Modo Desarrollo

✅ **Hot Reload**: Los cambios en el código se reflejan automáticamente
✅ **Base de datos**: Usa AWS RDS (paqueteria_staging) - mismos datos que staging
✅ **Redis**: Contenedor local
✅ **S3**: Usa el bucket real de AWS
✅ **Debug**: Activado con logs detallados

### Estructura de Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| App (FastAPI) | 8000 | http://localhost:8000 |
| Redis | 6379 | redis://localhost:6379 |

---

## Opción 2: Sin Docker (Desarrollo Nativo)

### Requisitos Previos
- Python 3.11+
- PostgreSQL (o usar AWS RDS remoto)
- Redis (o usar Redis remoto)

### Pasos

1. **Crear entorno virtual**
```bash
cd CODE
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
# Copiar el archivo .env si no existe
cp .env.example .env

# Editar .env con tus credenciales
nano .env
```

4. **Ejecutar migraciones (si es necesario)**
```bash
alembic upgrade head
```

5. **Iniciar el servidor**
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Abrir en el navegador**
```
http://localhost:8000
```

---

## Opción 3: Modo Desarrollo Rápido (Solo Frontend)

Si solo quieres ver cambios en templates/static sin levantar todo:

1. **Usar el servidor de staging como backend**
```bash
# Editar los archivos en CODE/src/templates/ o CODE/src/static/
# Los cambios se verán en staging después de reiniciar
```

2. **Reiniciar staging para ver cambios**
```bash
docker compose -f docker-compose.staging.yml restart app
```

---

## Rutas Principales

Una vez que el servidor esté corriendo:

| Ruta | Descripción |
|------|-------------|
| http://localhost:8000 | Página principal |
| http://localhost:8000/auth/login | Login |
| http://localhost:8000/dashboard | Dashboard (requiere login) |
| http://localhost:8000/packages | Gestión de paquetes |
| http://localhost:8000/invoices | Sistema de facturas V2 |
| http://localhost:8000/products | Gestión de productos |
| http://localhost:8000/docs | Documentación API (Swagger) |
| http://localhost:8000/health | Health check |

---

## Usuarios de Prueba

Para acceder al sistema en desarrollo/staging:

### Admin
- **Usuario**: `jveyes` o `admin`
- **Contraseña**: (consultar en la base de datos o crear uno nuevo)

### Crear un usuario nuevo
```bash
# Conectarse al contenedor
docker compose -f docker-compose.dev.yml exec app bash

# Ejecutar script de creación de usuario (si existe)
python scripts/create_user.py
```

O desde la interfaz web:
1. Ir a http://localhost:8000/auth/register
2. Registrarse con un email
3. Verificar en la base de datos y cambiar el rol a admin si es necesario

---

## Troubleshooting

### Puerto 8000 ya está en uso
```bash
# Ver qué proceso está usando el puerto
lsof -i :8000

# Matar el proceso
kill -9 <PID>

# O usar otro puerto
docker compose -f docker-compose.dev.yml up -d
# Editar docker-compose.dev.yml y cambiar "8000:8000" a "8001:8000"
```

### Error de conexión a la base de datos
```bash
# Verificar que las credenciales en CODE/.env son correctas
cat CODE/.env | grep DATABASE_URL

# Verificar conectividad a AWS RDS
ping ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com
```

### Redis no conecta
```bash
# Verificar que Redis está corriendo
docker compose -f docker-compose.dev.yml ps

# Reiniciar Redis
docker compose -f docker-compose.dev.yml restart redis
```

### Cambios no se reflejan
```bash
# Verificar que los volúmenes están montados correctamente
docker compose -f docker-compose.dev.yml config

# Reiniciar el contenedor
docker compose -f docker-compose.dev.yml restart app

# Ver logs para errores
docker compose -f docker-compose.dev.yml logs -f app
```

### Error de permisos en uploads
```bash
# Crear directorio de uploads si no existe
mkdir -p CODE/src/uploads

# Dar permisos
chmod -R 777 CODE/src/uploads
```

---

## Comandos Útiles

### Ver logs en tiempo real
```bash
docker compose -f docker-compose.dev.yml logs -f app
```

### Entrar al contenedor
```bash
docker compose -f docker-compose.dev.yml exec app bash
```

### Ejecutar migraciones
```bash
docker compose -f docker-compose.dev.yml exec app alembic upgrade head
```

### Reiniciar servicios
```bash
# Reiniciar todo
docker compose -f docker-compose.dev.yml restart

# Reiniciar solo app
docker compose -f docker-compose.dev.yml restart app
```

### Limpiar y reconstruir
```bash
# Detener y eliminar contenedores
docker compose -f docker-compose.dev.yml down

# Reconstruir imágenes
docker compose -f docker-compose.dev.yml build --no-cache

# Levantar de nuevo
docker compose -f docker-compose.dev.yml up -d
```

---

## Desarrollo con Hot Reload

El proyecto está configurado con hot reload, lo que significa que:

✅ **Cambios en Python** (`CODE/src/**/*.py`) se reflejan automáticamente
✅ **Cambios en templates** (`CODE/src/templates/**/*.html`) se reflejan automáticamente
✅ **Cambios en static** (`CODE/src/static/**/*`) se reflejan automáticamente

**No necesitas reiniciar** el servidor para ver cambios en estos archivos.

### Archivos que SÍ requieren reinicio:
- `CODE/requirements.txt` (nuevas dependencias)
- `CODE/alembic/**/*.py` (migraciones)
- Variables de entorno en `CODE/.env`
- Configuración de Docker

---

## Notas Importantes

⚠️ **Base de datos compartida**: El modo desarrollo usa la misma base de datos que staging (AWS RDS). Ten cuidado con los cambios que hagas.

⚠️ **S3 compartido**: Los archivos se suben al mismo bucket de AWS S3 con prefijo `staging/`.

⚠️ **Credenciales**: Las credenciales de AWS están en el archivo `.env`. No las compartas ni las subas a Git.

💡 **Tip**: Si quieres una base de datos completamente local, puedes:
1. Instalar PostgreSQL localmente
2. Crear una base de datos `paqueteria_dev`
3. Cambiar `DATABASE_URL` en `CODE/.env`
4. Ejecutar migraciones: `alembic upgrade head`

---

## Siguiente Paso

Una vez que tengas el proyecto corriendo en localhost:

1. **Probar la carga de facturas**: http://localhost:8000/invoices/facturas
2. **Verificar que los cambios del fix funcionan**
3. **Hacer tus modificaciones**
4. **Probar localmente antes de desplegar a staging**
