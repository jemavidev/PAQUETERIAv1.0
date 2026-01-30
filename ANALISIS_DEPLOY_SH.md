# ⚠️ Análisis: ¿Puedo ejecutar deploy.sh sin problemas?

**Fecha**: 30 de Enero, 2026  
**Pregunta**: ¿Puedo ejecutar `./deploy.sh` sin problemas después de los cambios realizados?

---

## 🎯 Respuesta Corta

**SÍ, PERO CON PRECAUCIONES** ⚠️

El script `deploy.sh` funcionará, pero hay **configuraciones que necesitan ajuste** para que sea 100% compatible con el sistema actual.

---

## ✅ Lo Que Funciona Bien

### 1. Estructura General
- ✅ El script está bien diseñado y es robusto
- ✅ Maneja múltiples entornos (localhost, staging, papyrus)
- ✅ Tiene sistema de rollback y selección de commits
- ✅ Compatible con `docker compose` (sin guión)

### 2. Operaciones Básicas
- ✅ Git pull/push funcionan correctamente
- ✅ Docker operations (up, down, restart) funcionan
- ✅ Health check está configurado
- ✅ Logs y status funcionan

---

## ⚠️ Problemas Identificados

### 1. **CRÍTICO: Migraciones Deshabilitadas en Staging**

**Problema**:
```bash
MIGRATIONS_ENABLED=false            # ❌ Deshabilitado
MIGRATIONS_AUTO=false
```

**Por qué es un problema**:
- Acabamos de crear nuevas tablas (`invoices_v2`, `invoice_products_v2`)
- Las migraciones YA están aplicadas en tu staging local
- Si ejecutas deploy.sh, NO aplicará las migraciones en el servidor remoto
- El servidor remoto NO tendrá las tablas nuevas

**Impacto**:
- ❌ La aplicación fallará al intentar acceder a las tablas de facturas V2
- ❌ Error: "Table 'invoices_v2' doesn't exist"

**Solución**:
```bash
# Editar .deploy/config/staging.conf
MIGRATIONS_ENABLED=true             # ✅ Habilitar
MIGRATIONS_AUTO=true                # ✅ Aplicar automáticamente
```

### 2. **ADVERTENCIA: Comando de Migraciones Incorrecto**

**Problema**:
```bash
MIGRATIONS_COMMAND="docker compose -f docker-compose.staging.yml exec -T app alembic upgrade heads"
#                                                                                              ^^^^^ 
#                                                                                              Debería ser "head" (singular)
```

**Solución**:
```bash
MIGRATIONS_COMMAND="docker compose -f docker-compose.staging.yml exec -T app alembic upgrade head"
```

### 3. **ADVERTENCIA: Backup Deshabilitado**

**Problema**:
```bash
BACKUP_ENABLED=false                # ❌ Deshabilitado
BACKUP_AUTO_BEFORE_DEPLOY=false
```

**Comentario en config**:
> "Migraciones deshabilitadas porque staging comparte BD con producción"

**Riesgo**:
- Si staging comparte BD con producción, las migraciones afectarán producción
- NO hay backup antes de aplicar migraciones
- Si algo sale mal, NO hay forma de revertir

**Recomendación**:
- ✅ Habilitar backup antes de deploy
- ✅ O confirmar que staging tiene BD separada

### 4. **INFO: Rebuild Habilitado**

**Configuración actual**:
```bash
DOCKER_REBUILD_ON_DEPLOY=true       # ✅ Correcto
```

**Esto está bien** porque:
- Los cambios en modelos requieren rebuild
- Los archivos de migración necesitan estar en la imagen

---

## 🔧 Cambios Necesarios

### Opción 1: Habilitar Migraciones (RECOMENDADO)

Edita `.deploy/config/staging.conf`:

```bash
# ┌────────────────────────────────────────────────────────────────────────────┐
# │ MIGRACIONES                                                                │
# └────────────────────────────────────────────────────────────────────────────┘

MIGRATIONS_ENABLED=true             # ✅ CAMBIAR a true
MIGRATIONS_AUTO=true                # ✅ CAMBIAR a true
MIGRATIONS_COMMAND="docker compose -f docker-compose.staging.yml exec -T app alembic upgrade head"  # ✅ CORREGIR "heads" → "head"
MIGRATIONS_ROLLBACK_COMMAND="docker compose -f docker-compose.staging.yml exec app alembic downgrade -1"
```

### Opción 2: Habilitar Backup (RECOMENDADO)

Si staging comparte BD con producción:

```bash
# ┌────────────────────────────────────────────────────────────────────────────┐
# │ BACKUP                                                                     │
# └────────────────────────────────────────────────────────────────────────────┘

BACKUP_ENABLED=true                 # ✅ CAMBIAR a true
BACKUP_AUTO_BEFORE_DEPLOY=true      # ✅ CAMBIAR a true
BACKUP_DB_COMMAND="docker compose -f docker-compose.staging.yml exec -T app pg_dump \$DATABASE_URL"
BACKUP_RETENTION_DAYS=7
```

---

## 📋 Pasos Recomendados ANTES de Ejecutar deploy.sh

### 1. Verificar Estado Actual

```bash
# Ver qué entorno está configurado
cat .deploy-current

# Ver configuración de staging
cat .deploy/config/staging.conf | grep -E "MIGRATIONS|BACKUP"
```

### 2. Aplicar Cambios a la Configuración

```bash
# Editar configuración
nano .deploy/config/staging.conf

# O usar sed para cambios rápidos
sed -i 's/MIGRATIONS_ENABLED=false/MIGRATIONS_ENABLED=true/' .deploy/config/staging.conf
sed -i 's/MIGRATIONS_AUTO=false/MIGRATIONS_AUTO=true/' .deploy/config/staging.conf
sed -i 's/upgrade heads/upgrade head/' .deploy/config/staging.conf
```

### 3. Verificar Que Staging Tiene BD Separada

```bash
# Conectarse a staging
ssh ubuntu@staging

# Ver configuración de BD
cat /home/ubuntu/paqueteria-staging/.env.staging | grep DATABASE_URL

# Comparar con producción
# Si son diferentes → OK para migraciones
# Si son iguales → ⚠️ CUIDADO, afectará producción
```

### 4. Ejecutar Deploy con Precaución

```bash
# Opción A: Modo interactivo (recomendado para primera vez)
./deploy.sh

# Seleccionar:
# [E] Cambiar Entorno → staging
# [1] Deploy Completo

# Opción B: Modo CLI directo
./deploy.sh --env staging --deploy
```

---

## 🚨 Escenarios de Riesgo

### Escenario 1: Staging Comparte BD con Producción

**Si esto es cierto**:
- ❌ NO ejecutar deploy.sh sin backup
- ❌ Las migraciones afectarán producción
- ⚠️ Riesgo ALTO de romper producción

**Solución**:
1. Crear BD separada para staging
2. O aplicar migraciones manualmente en producción primero
3. Luego ejecutar deploy.sh

### Escenario 2: Staging Tiene BD Separada

**Si esto es cierto**:
- ✅ Seguro ejecutar deploy.sh
- ✅ Las migraciones solo afectan staging
- ✅ Riesgo BAJO

**Acción**:
1. Habilitar migraciones en config
2. Ejecutar deploy.sh normalmente

---

## 📝 Checklist Pre-Deploy

Antes de ejecutar `./deploy.sh`, verifica:

- [ ] ✅ Migraciones habilitadas en `.deploy/config/staging.conf`
- [ ] ✅ Comando de migraciones corregido (`head` no `heads`)
- [ ] ✅ Backup habilitado (si BD compartida)
- [ ] ✅ Verificado que staging tiene BD separada
- [ ] ✅ Commit actual tiene todos los cambios
- [ ] ✅ Archivo `.env.staging` existe y está actualizado
- [ ] ✅ Servidor staging tiene espacio en disco
- [ ] ✅ Servidor staging tiene acceso a GitHub

---

## 🎯 Recomendación Final

### Para Deploy Seguro:

**Opción A: Deploy Manual (MÁS SEGURO)**
```bash
# 1. Conectarse a staging
ssh ubuntu@staging

# 2. Ir al directorio
cd /home/ubuntu/paqueteria-staging

# 3. Pull manual
git fetch origin staging
git reset --hard origin/staging

# 4. Rebuild
docker compose -f docker-compose.staging.yml build app

# 5. Up
docker compose -f docker-compose.staging.yml up -d

# 6. Aplicar migraciones
docker compose -f docker-compose.staging.yml exec -T app alembic upgrade head

# 7. Restart
docker compose -f docker-compose.staging.yml restart app

# 8. Verificar
curl http://localhost:8001/health
```

**Opción B: Usar deploy.sh (DESPUÉS DE AJUSTES)**
```bash
# 1. Aplicar cambios a .deploy/config/staging.conf
# 2. Ejecutar
./deploy.sh --env staging --deploy
```

---

## 📊 Resumen

| Aspecto | Estado | Acción Requerida |
|---------|--------|------------------|
| Script deploy.sh | ✅ Funcional | Ninguna |
| Migraciones | ⚠️ Deshabilitadas | Habilitar en config |
| Comando migraciones | ⚠️ Incorrecto | Corregir "heads" → "head" |
| Backup | ⚠️ Deshabilitado | Habilitar si BD compartida |
| Docker rebuild | ✅ Habilitado | Ninguna |
| Git operations | ✅ Funcional | Ninguna |
| Health check | ✅ Configurado | Ninguna |

---

## 🆘 Si Algo Sale Mal

### Rollback Rápido

```bash
# Opción 1: Usar deploy.sh
./deploy.sh --env staging
# Seleccionar: [3] Pull a Commit Específico
# Elegir commit anterior

# Opción 2: Manual
ssh ubuntu@staging
cd /home/ubuntu/paqueteria-staging
git log --oneline -10
git reset --hard <commit-anterior>
docker compose -f docker-compose.staging.yml restart app
```

### Revertir Migraciones

```bash
ssh ubuntu@staging
cd /home/ubuntu/paqueteria-staging
docker compose -f docker-compose.staging.yml exec app alembic downgrade -1
docker compose -f docker-compose.staging.yml restart app
```

---

## ✅ Conclusión

**Puedes ejecutar `./deploy.sh`**, pero:

1. **PRIMERO** habilita migraciones en `.deploy/config/staging.conf`
2. **PRIMERO** corrige el comando de migraciones (`head` no `heads`)
3. **VERIFICA** que staging tiene BD separada de producción
4. **CONSIDERA** habilitar backup automático

**Si no haces estos cambios**, el deploy se ejecutará pero las tablas de facturas V2 NO se crearán en el servidor remoto y la aplicación fallará.

---

**Documentación generada**: 30 de Enero, 2026
