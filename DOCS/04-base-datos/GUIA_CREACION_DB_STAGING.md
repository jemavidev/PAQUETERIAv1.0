# 🆕 Guía: Creación de Base de Datos Staging

## 📋 RESUMEN

Se ha preparado todo para crear una base de datos staging SEPARADA de producción.

---

## ✅ ARCHIVOS CREADOS

### 1. Configuración de Ambientes

```
.env.production          ✅ Copia del .env actual (producción)
.env.staging             ✅ Nueva configuración para staging
```

### 2. Scripts

```
scripts/database/create_staging_database.sh           ✅ Crear DB staging
scripts/database/sync_prod_to_staging_initial.sh      ✅ Sincronización inicial
scripts/database/sync_prod_to_staging_daily.sh        ✅ Sincronización diaria
```

### 3. Docker Compose Actualizado

```
docker-compose.staging.yml    ✅ Ahora usa .env.staging
```

---

## 🔒 GARANTÍAS DE SEGURIDAD

### ✅ Producción NO se toca:

1. **`.env` original NO modificado**
   - Sigue apuntando a `paqueteria_v4`
   - Producción sigue funcionando igual

2. **`.env.production` es backup**
   - Copia exacta del `.env` original
   - Por si necesitas restaurar

3. **`.env.staging` es NUEVO**
   - Apunta a `paqueteria_staging` (nueva DB)
   - No afecta producción

4. **Script con confirmaciones**
   - Pide confirmación antes de crear
   - Muestra qué va a hacer
   - Permite cancelar en cualquier momento

---

## 📊 CONFIGURACIÓN DE BASES DE DATOS

### Producción (NO CAMBIA)
```yaml
Base de datos: paqueteria_v4
Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...
Usuario: jveyes
Archivo: .env (sin cambios)
Docker: docker-compose.prod.yml
```

### Staging (NUEVA)
```yaml
Base de datos: paqueteria_staging  ← NUEVA
Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535... (mismo servidor)
Usuario: jveyes (mismo usuario)
Archivo: .env.staging  ← NUEVO
Docker: docker-compose.staging.yml (actualizado)
```

---

## 🚀 PASOS PARA CREAR STAGING

### Paso 1: Crear Base de Datos

```bash
# Ejecutar script (pedirá confirmación)
./scripts/database/create_staging_database.sh
```

**El script hará:**
1. ✅ Pedir confirmación (escribe 'SI')
2. ✅ Verificar si ya existe
3. ✅ Crear `paqueteria_staging`
4. ✅ Verificar creación
5. ✅ Mostrar resumen

**Salida esperada:**
```
╔══════════════════════════════════════════════════════════════════╗
║          🆕 CREAR BASE DE DATOS STAGING                          ║
╚══════════════════════════════════════════════════════════════════╝

🔒 Validaciones de seguridad...

⚠️  IMPORTANTE: Este script creará una NUEVA base de datos.

   Base de datos a crear: paqueteria_staging
   Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...
   Usuario: jveyes

   ✅ NO se modificará la base de datos de producción (paqueteria_v4)
   ✅ Solo se creará una nueva base de datos vacía

¿Deseas continuar? (escribe 'SI' para confirmar): SI

✅ Confirmación recibida

🔍 Verificando si la base de datos ya existe...

🆕 Creando base de datos 'paqueteria_staging'...
✅ Base de datos creada exitosamente

🔍 Verificando creación...
✅ Base de datos verificada
   Nombre: paqueteria_staging
   Tamaño: 8192 kB
   Host: ls-abe25e9bea57818f0ee32555c0e7b4a10e361535...

📊 Bases de datos en el servidor:

     datname      |  size   
------------------+---------
 paqueteria_v4    | 150 MB
 paqueteria_staging | 8192 kB

╔══════════════════════════════════════════════════════════════════╗
║                  ✅ BASE DE DATOS CREADA                         ║
╚══════════════════════════════════════════════════════════════════╝
```

### Paso 2: Sincronizar Datos de Producción

```bash
# Copiar estructura y datos de producción a staging
./scripts/database/sync_prod_to_staging_initial.sh
```

**Esto copiará:**
- ✅ Todas las tablas de producción
- ✅ Todos los datos actuales
- ✅ Estructura completa

**Tiempo estimado:** 5-10 minutos (depende del tamaño)

### Paso 3: Aplicar Migraciones de Staging

```bash
# Aplicar migraciones adicionales de staging
cd CODE
DATABASE_URL="postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl$@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging" \
  alembic upgrade head
```

**Esto aplicará:**
- ✅ Migraciones de invoice_items
- ✅ Migraciones de cufe_records
- ✅ Migraciones de supplier_invoices
- ✅ Otras tablas de staging

### Paso 4: Iniciar Staging

```bash
# Iniciar contenedores de staging
docker-compose -f docker-compose.staging.yml up -d
```

**Verificar:**
```bash
# Ver logs
docker-compose -f docker-compose.staging.yml logs -f app

# Verificar salud
docker-compose -f docker-compose.staging.yml ps

# Probar endpoint
curl http://localhost:8001/health
```

---

## 🔍 VERIFICACIÓN

### Verificar que Producción NO se afectó:

```bash
# 1. Verificar que producción sigue usando paqueteria_v4
docker-compose -f docker-compose.prod.yml config | grep DATABASE_URL

# 2. Verificar que producción sigue funcionando
curl http://localhost:8000/health

# 3. Ver logs de producción (no debe haber errores)
docker-compose -f docker-compose.prod.yml logs --tail 50 app
```

### Verificar que Staging usa paqueteria_staging:

```bash
# 1. Verificar configuración
docker-compose -f docker-compose.staging.yml config | grep DATABASE_URL

# 2. Verificar conexión a DB
docker-compose -f docker-compose.staging.yml exec app python -c "
from src.app.database import engine
print(f'Connected to: {engine.url}')
"

# 3. Contar tablas en staging
docker-compose -f docker-compose.staging.yml exec app python -c "
from src.app.database import engine
result = engine.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=\\'public\\'')
print(f'Tables in staging: {result.scalar()}')
"
```

---

## 📊 COMPARACIÓN: ANTES vs DESPUÉS

### ANTES (Riesgoso)
```
Producción  →  paqueteria_v4  ←─┐
                                 ├─ MISMA DB ⚠️
Staging     →  paqueteria_v4  ←─┘
```

### DESPUÉS (Seguro)
```
Producción  →  paqueteria_v4
                    ↓
                Sync Diaria
                    ↓
Staging     →  paqueteria_staging  ← SEPARADA ✅
```

---

## 🔄 FLUJO DE TRABAJO DIARIO

### Desarrollo en Staging:

```bash
# 1. Trabajar en rama staging
git checkout staging

# 2. Hacer cambios en código

# 3. Crear migración (si es necesario)
cd CODE
alembic revision -m "add_new_feature"

# 4. Aplicar en staging
DATABASE_URL="postgresql://...paqueteria_staging" alembic upgrade head

# 5. Probar en staging
# http://localhost:8001

# 6. Si todo funciona, merge a main
git checkout main
git merge staging

# 7. Aplicar migraciones en producción
DATABASE_URL="postgresql://...paqueteria_v4" alembic upgrade head

# 8. Deploy a producción
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 🚨 ROLLBACK (Si algo sale mal)

### Si necesitas volver atrás:

```bash
# 1. Detener staging
docker-compose -f docker-compose.staging.yml down

# 2. Eliminar base de datos staging
PGPASSWORD='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$' psql \
  -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535... \
  -U jveyes \
  -d postgres \
  -c "DROP DATABASE paqueteria_staging;"

# 3. Restaurar configuración original (si es necesario)
# Producción NO se afecta, sigue funcionando normal
```

---

## 📝 CHECKLIST

### Antes de Crear Staging:
- [x] Backup de .env creado (.env.production)
- [x] .env.staging creado
- [x] Scripts de sincronización creados
- [x] docker-compose.staging.yml actualizado
- [ ] Confirmar que producción funciona
- [ ] Tener acceso a AWS RDS

### Durante la Creación:
- [ ] Ejecutar create_staging_database.sh
- [ ] Confirmar creación (escribir 'SI')
- [ ] Verificar que se creó correctamente
- [ ] Ejecutar sync_prod_to_staging_initial.sh
- [ ] Aplicar migraciones de staging
- [ ] Iniciar contenedores de staging

### Después de Crear:
- [ ] Verificar que producción NO se afectó
- [ ] Verificar que staging funciona
- [ ] Probar endpoints de staging
- [ ] Configurar sincronización diaria (cron)
- [ ] Documentar proceso

---

## 💡 TIPS

### 1. Monitorear Tamaño de DB

```bash
# Ver tamaño de ambas bases de datos
PGPASSWORD='...' psql -h ... -U jveyes -d postgres -c "
SELECT 
  datname, 
  pg_size_pretty(pg_database_size(datname)) as size 
FROM pg_database 
WHERE datname IN ('paqueteria_v4', 'paqueteria_staging')
ORDER BY datname;
"
```

### 2. Sincronización Manual

```bash
# Si necesitas sincronizar manualmente
./scripts/database/sync_prod_to_staging_daily.sh
```

### 3. Ver Diferencias entre Ambientes

```bash
# Comparar tablas
PGPASSWORD='...' psql -h ... -U jveyes -d paqueteria_v4 -c "\dt" > /tmp/prod_tables.txt
PGPASSWORD='...' psql -h ... -U jveyes -d paqueteria_staging -c "\dt" > /tmp/staging_tables.txt
diff /tmp/prod_tables.txt /tmp/staging_tables.txt
```

---

## 🎯 RESULTADO ESPERADO

Después de completar todos los pasos:

✅ **Producción:**
- Base de datos: `paqueteria_v4`
- Funcionando normal
- Sin cambios
- Sin riesgos

✅ **Staging:**
- Base de datos: `paqueteria_staging` (nueva)
- Datos copiados de producción
- Tablas adicionales de staging
- Listo para pruebas

✅ **Sincronización:**
- Automática diaria
- Producción → Staging
- Solo lectura desde staging

---

## 📞 SOPORTE

Si algo sale mal:
1. NO entrar en pánico
2. Producción NO se afecta
3. Revisar logs: `docker-compose -f docker-compose.staging.yml logs`
4. Verificar conexión a DB
5. Consultar esta guía

---

**Creado:** 27 de enero de 2026  
**Rama:** mainv2.1  
**Estado:** Listo para ejecutar
