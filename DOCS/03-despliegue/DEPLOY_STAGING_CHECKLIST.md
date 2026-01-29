# ✅ CHECKLIST: Deploy a Servidor Staging

## 🎯 Objetivo

Asegurar que cuando se despliegue el código al **servidor staging**, automáticamente se conecte a la base de datos `paqueteria_staging` en AWS RDS.

---

## 📋 CAMBIOS REALIZADOS EN CÓDIGO LOCAL

### ✅ Archivos Creados/Modificados:

1. **`CODE/.env.staging`** ⭐ NUEVO
   - Configuración completa para staging
   - `DATABASE_URL=postgresql://...paqueteria_staging`
   - Puerto: 8001
   - Redis: 6380
   - S3 Prefix: `staging/`

2. **`docker-compose.staging.yml`** ✏️ MODIFICADO
   - Cambiado: `env_file: ./CODE/.env` 
   - A: `env_file: ./CODE/.env.staging`

3. **Scripts de gestión** 📝 NUEVOS
   - `scripts/staging/01_verify_and_init_staging_db.py`
   - `scripts/staging/verify_staging_db.sh`
   - `scripts/staging/list_databases.py`
   - `scripts/staging/SETUP_STAGING_GUIDE.md`

4. **Documentación** 📖 NUEVA
   - `ANALISIS_CONEXIONES_DB_COMPLETO.md`
   - `STAGING_SETUP_RESUMEN.md`
   - `DEPLOY_STAGING_CHECKLIST.md` (este archivo)

---

## 🚀 PROCESO DE DEPLOY AL SERVIDOR STAGING

### **Paso 1: Subir Código al Servidor**

```bash
# Desde tu máquina local
git add .
git commit -m "feat: Configurar staging para usar paqueteria_staging"
git push origin main

# O si usas rsync/scp
rsync -avz --exclude 'node_modules' --exclude '__pycache__' \
    ./ usuario@servidor-staging:/ruta/proyecto/
```

### **Paso 2: En el Servidor Staging**

```bash
# SSH al servidor staging
ssh usuario@servidor-staging

# Ir al directorio del proyecto
cd /ruta/proyecto

# Verificar que CODE/.env.staging existe
ls -la CODE/.env.staging

# Verificar contenido (debe tener DATABASE_URL con paqueteria_staging)
grep DATABASE_URL CODE/.env.staging
```

**Debe mostrar:**
```
DATABASE_URL=postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_staging
```

### **Paso 3: Verificar Base de Datos (Opcional)**

```bash
# Verificar que paqueteria_staging existe
python3 scripts/staging/01_verify_and_init_staging_db.py

# O usar el script bash
bash scripts/staging/verify_staging_db.sh
```

### **Paso 4: Levantar Contenedor Staging**

```bash
# Detener contenedor anterior (si existe)
docker-compose -f docker-compose.staging.yml down

# Reconstruir imagen (si hay cambios en código)
docker-compose -f docker-compose.staging.yml build --no-cache

# Levantar contenedor
docker-compose -f docker-compose.staging.yml up -d
```

### **Paso 5: Verificar Conexión**

```bash
# Ver logs
docker-compose -f docker-compose.staging.yml logs -f app

# Verificar DATABASE_URL dentro del contenedor
docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
```

**Debe mostrar:**
```
DATABASE_URL=postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_staging
```

### **Paso 6: Probar Endpoints**

```bash
# Probar salud del servidor
curl http://localhost:8001/health

# Probar endpoint de facturas
curl http://localhost:8001/invoices/api/supplier-invoices/stats

# Probar vista de facturas (desde navegador)
# http://servidor-staging:8001/invoices
```

---

## 🔍 VERIFICACIÓN POST-DEPLOY

### **Checklist de Verificación:**

- [ ] Contenedor staging está corriendo en puerto 8001
- [ ] `DATABASE_URL` apunta a `paqueteria_staging`
- [ ] Endpoint `/health` responde OK
- [ ] Logs no muestran errores de conexión a BD
- [ ] Al crear datos en staging, se guardan en `paqueteria_staging`
- [ ] Producción (puerto 80) sigue funcionando normal

### **Comandos de Verificación:**

```bash
# 1. Estado del contenedor
docker-compose -f docker-compose.staging.yml ps

# 2. DATABASE_URL
docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL

# 3. Logs
docker-compose -f docker-compose.staging.yml logs --tail=50 app

# 4. Health check
curl http://localhost:8001/health

# 5. Verificar BD desde DBeaver
# Conectar a paqueteria_staging y ver si hay datos nuevos
```

---

## 📊 ARQUITECTURA FINAL

```
┌─────────────────────────────────────────────────────────────┐
│                    SERVIDOR STAGING                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Contenedor Staging (Puerto 8001)                    │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  FastAPI App                                    │  │  │
│  │  │  - Lee: CODE/.env.staging                       │  │  │
│  │  │  - DATABASE_URL=...paqueteria_staging           │  │  │
│  │  │  - ENVIRONMENT=staging                          │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│                    (Conecta a)                               │
│                           ↓                                  │
└───────────────────────────┼──────────────────────────────────┘
                            ↓
                            ↓
┌───────────────────────────┼──────────────────────────────────┐
│                    AWS RDS (us-east-1)                       │
├───────────────────────────┼──────────────────────────────────┤
│                           ↓                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  paqueteria_staging                                    │ │
│  │  - Datos de pruebas                                    │ │
│  │  - Independiente de producción                         │ │
│  │  - Puerto: 5432                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  paqueteria_v4 (Producción)                           │ │
│  │  - Datos reales                                        │ │
│  │  - No afectada por staging                            │ │
│  │  - Puerto: 5432                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔒 SEGURIDAD Y SEPARACIÓN

### **Garantías:**

✅ **Staging y Producción están completamente separados:**
- Diferentes puertos (8001 vs 80)
- Diferentes bases de datos (paqueteria_staging vs paqueteria_v4)
- Diferentes volúmenes Docker
- Diferentes prefijos S3 (staging/ vs raíz)
- Diferentes SECRET_KEY

✅ **Producción NO se ve afectada:**
- Staging no puede modificar datos de producción
- Staging solo puede LEER de producción (para sincronización)
- Producción sigue en puerto 80 sin cambios

✅ **Staging es seguro para pruebas:**
- Puedes crear/modificar/eliminar datos sin miedo
- Puedes probar features nuevas
- Puedes hacer pruebas de carga

---

## 🛠️ TROUBLESHOOTING

### **Problema: Staging se conecta a producción**

**Solución:**
```bash
# Verificar que docker-compose.staging.yml usa el archivo correcto
grep env_file docker-compose.staging.yml
# Debe mostrar: - ./CODE/.env.staging

# Verificar DATABASE_URL dentro del contenedor
docker-compose -f docker-compose.staging.yml exec app env | grep DATABASE_URL
# Debe mostrar: ...paqueteria_staging
```

### **Problema: Tablas no existen en paqueteria_staging**

**Solución:**
```bash
# Opción 1: Ejecutar migraciones
cd CODE
export DATABASE_URL="postgresql://jveyes:...@...amazonaws.com:5432/paqueteria_staging"
alembic upgrade head

# Opción 2: Copiar esquema desde producción
python3 scripts/staging/02_copy_schema_from_prod.py
```

### **Problema: No se puede conectar a AWS RDS**

**Solución:**
```bash
# Verificar conectividad
telnet ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com 5432

# Verificar security groups en AWS
# Debe permitir conexiones desde la IP del servidor staging
```

---

## 📝 NOTAS IMPORTANTES

### **Para el Equipo:**

1. **Código Local:**
   - Los cambios están en Git
   - `CODE/.env.staging` tiene la configuración correcta
   - `docker-compose.staging.yml` está actualizado

2. **Deploy:**
   - Solo necesitas hacer `git pull` en el servidor staging
   - Y ejecutar `docker-compose -f docker-compose.staging.yml up -d`
   - Todo lo demás es automático

3. **Verificación:**
   - Siempre verificar `DATABASE_URL` después del deploy
   - Siempre revisar logs después del deploy
   - Siempre probar un endpoint después del deploy

4. **Rollback:**
   - Si algo falla, puedes volver a la versión anterior:
   ```bash
   git checkout HEAD~1
   docker-compose -f docker-compose.staging.yml up -d --build
   ```

---

## ✅ RESUMEN FINAL

### **Lo que se hizo:**

1. ✅ Creado `CODE/.env.staging` con configuración correcta
2. ✅ Modificado `docker-compose.staging.yml` para usar `.env.staging`
3. ✅ Creados scripts de verificación y gestión
4. ✅ Documentado todo el proceso

### **Lo que NO se necesita hacer:**

- ❌ NO modificar archivos de rutas (routes/*.py)
- ❌ NO modificar servicios
- ❌ NO modificar modelos
- ❌ NO modificar vistas HTML

### **Por qué funciona:**

Todos los endpoints usan `Depends(get_db)` que automáticamente usa la `DATABASE_URL` del archivo `.env` que cargue el contenedor.

### **Próximo paso:**

Hacer deploy al servidor staging y verificar que todo funciona.

---

**Fecha:** 2026-01-29  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para deploy
