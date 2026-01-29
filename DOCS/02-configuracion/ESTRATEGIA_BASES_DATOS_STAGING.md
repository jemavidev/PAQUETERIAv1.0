# 🗄️ Estrategia de Bases de Datos: Producción vs Staging

## 🎯 OBJETIVO

Mantener dos bases de datos separadas:
- **Producción:** Datos reales, estable
- **Staging:** Copia de producción + nuevas funcionalidades

---

## 📊 ARQUITECTURA RECOMENDADA

### Opción 1: REPLICACIÓN SELECTIVA + MIGRACIONES (⭐ RECOMENDADA)

```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS RDS                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐         ┌──────────────────────┐     │
│  │   PRODUCCIÓN         │         │     STAGING          │     │
│  │  paqueteria_v4       │────────▶│  paqueteria_staging  │     │
│  │                      │  Sync   │                      │     │
│  │  Tablas:             │  Daily  │  Tablas:             │     │
│  │  • users             │         │  • users (copiada)   │     │
│  │  • packages          │         │  • packages (copiada)│     │
│  │  • customers         │         │  • customers (copiada)│    │
│  │  • rates             │         │  • rates (copiada)   │     │
│  │  • messages          │         │  • messages (copiada)│     │
│  │  • announcements     │         │  • announcements     │     │
│  │  • ...               │         │  • ...               │     │
│  │                      │         │  + invoice_items ✨  │     │
│  │  Datos: REALES       │         │  + cufe_records ✨   │     │
│  │  Acceso: Solo MAIN   │         │  + products ✨       │     │
│  └──────────────────────┘         │                      │     │
│                                    │  Datos: Copia + Test │     │
│                                    │  Acceso: STAGING     │     │
│                                    └──────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### Ventajas:
✅ Datos reales en staging para pruebas realistas
✅ Nuevas tablas solo en staging (no afecta producción)
✅ Sincronización controlada (no en tiempo real)
✅ Fácil rollback si algo falla
✅ No afecta performance de producción

### Desventajas:
⚠️ Datos no están en tiempo real (desfase de horas/días)
⚠️ Requiere script de sincronización
⚠️ Duplicación de datos (más almacenamiento)

---

## 🔧 IMPLEMENTACIÓN

### 1️⃣ Crear Base de Datos Staging en AWS RDS

```bash
# Opción A: Desde AWS Console
# 1. Ir a RDS → Create database
# 2. Nombre: paqueteria-staging
# 3. Mismo tipo que producción (PostgreSQL)
# 4. Instancia más pequeña (db.t3.micro para ahorrar)

# Opción B: Desde AWS CLI
aws rds create-db-instance \
  --db-instance-identifier paqueteria-staging \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username jveyes \
  --master-user-password "TU_PASSWORD_STAGING" \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --port 5432
```

### 2️⃣ Configurar Variables de Entorno

**Producción (.env):**
```bash
# Base de datos de producción (NO CAMBIAR)
DATABASE_URL=postgresql://jveyes:password@prod-host.rds.amazonaws.com:5432/paqueteria_v4
ENVIRONMENT=production
```

**Staging (.env.staging):**
```bash
# Base de datos de staging
DATABASE_URL=postgresql://jveyes:password@staging-host.rds.amazonaws.com:5432/paqueteria_staging
ENVIRONMENT=staging

# Conexión a producción (solo lectura para sincronización)
PROD_DATABASE_URL=postgresql://jveyes:password@prod-host.rds.amazonaws.com:5432/paqueteria_v4
```

### 3️⃣ Script de Sincronización Inicial

```bash
#!/bin/bash
# scripts/sync_prod_to_staging_initial.sh

echo "🔄 Sincronización inicial: Producción → Staging"
echo "================================================"

# Variables
PROD_HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
PROD_DB="paqueteria_v4"
PROD_USER="jveyes"
PROD_PASS="a?HC!2.*1#?[==:|289qAI=)#V4kDzl$"

STAGING_HOST="staging-host.rds.amazonaws.com"
STAGING_DB="paqueteria_staging"
STAGING_USER="jveyes"
STAGING_PASS="staging_password"

# 1. Dump de producción (estructura + datos)
echo "📦 Exportando datos de producción..."
PGPASSWORD=$PROD_PASS pg_dump \
  -h $PROD_HOST \
  -U $PROD_USER \
  -d $PROD_DB \
  --no-owner \
  --no-acl \
  -F c \
  -f /tmp/prod_backup.dump

# 2. Restaurar en staging
echo "📥 Importando a staging..."
PGPASSWORD=$STAGING_PASS pg_restore \
  -h $STAGING_HOST \
  -U $STAGING_USER \
  -d $STAGING_DB \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  /tmp/prod_backup.dump

# 3. Aplicar migraciones de staging
echo "🔧 Aplicando migraciones de staging..."
cd CODE
DATABASE_URL=postgresql://$STAGING_USER:$STAGING_PASS@$STAGING_HOST:5432/$STAGING_DB \
  alembic upgrade head

echo "✅ Sincronización inicial completada"
```

### 4️⃣ Script de Sincronización Incremental (Diaria)

```bash
#!/bin/bash
# scripts/sync_prod_to_staging_daily.sh

echo "🔄 Sincronización diaria: Producción → Staging"
echo "=============================================="

# Variables
PROD_HOST="..."
STAGING_HOST="..."

# Tablas a sincronizar (solo las de producción)
TABLES=(
  "users"
  "packages"
  "customers"
  "rates"
  "messages"
  "announcements"
  "package_events"
  "customer_preferences"
)

for table in "${TABLES[@]}"; do
  echo "📊 Sincronizando tabla: $table"
  
  # 1. Exportar tabla de producción
  PGPASSWORD=$PROD_PASS pg_dump \
    -h $PROD_HOST \
    -U $PROD_USER \
    -d $PROD_DB \
    -t $table \
    --data-only \
    --no-owner \
    -f /tmp/${table}.sql
  
  # 2. Truncar tabla en staging
  PGPASSWORD=$STAGING_PASS psql \
    -h $STAGING_HOST \
    -U $STAGING_USER \
    -d $STAGING_DB \
    -c "TRUNCATE TABLE $table CASCADE;"
  
  # 3. Importar datos
  PGPASSWORD=$STAGING_PASS psql \
    -h $STAGING_HOST \
    -U $STAGING_USER \
    -d $STAGING_DB \
    -f /tmp/${table}.sql
  
  echo "✅ $table sincronizada"
done

echo "✅ Sincronización diaria completada"
```

### 5️⃣ Configurar Cron Job (Sincronización Automática)

```bash
# Editar crontab
crontab -e

# Agregar sincronización diaria a las 2 AM
0 2 * * * /path/to/scripts/sync_prod_to_staging_daily.sh >> /var/log/db_sync.log 2>&1
```

---

## 🔄 FLUJO DE TRABAJO DIARIO

### Desarrollo de Nueva Feature:

```bash
# 1. Trabajar en rama staging
git checkout staging

# 2. Crear migración para nueva tabla
cd CODE
alembic revision -m "add_invoice_items_table"

# 3. Editar migración
# CODE/alembic/versions/xxxxx_add_invoice_items_table.py

# 4. Aplicar en staging
DATABASE_URL=postgresql://staging-url alembic upgrade head

# 5. Desarrollar y probar feature
# La base de datos staging tiene:
#   - Datos reales de producción (sincronizados)
#   - Nueva tabla invoice_items (solo en staging)

# 6. Commit y push
git add .
git commit -m "feat: Add invoice items functionality"
git push origin staging
```

### Merge a Producción:

```bash
# 1. Merge código
git checkout main
git merge staging

# 2. Aplicar migraciones en producción
cd CODE
DATABASE_URL=postgresql://prod-url alembic upgrade head

# 3. Deploy
./deploy.sh

# 4. Verificar
# La base de datos producción ahora tiene:
#   - Todos los datos existentes (intactos)
#   - Nueva tabla invoice_items (creada por migración)
```

---

## 📋 GESTIÓN DE MIGRACIONES

### Estructura de Migraciones:

```
CODE/alembic/versions/
├── 001_initial_schema.py          # Producción
├── 002_add_packages.py             # Producción
├── 003_add_customers.py            # Producción
├── 004_add_invoice_items.py        # Staging → Producción
├── 005_add_cufe_records.py         # Staging → Producción
└── 006_add_products.py             # Staging → Producción
```

### Comandos Útiles:

```bash
# Ver historial de migraciones
alembic history

# Ver estado actual
alembic current

# Aplicar todas las migraciones pendientes
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Generar migración automática (detecta cambios en modelos)
alembic revision --autogenerate -m "descripcion"
```

---

## 🔐 SEGURIDAD

### Permisos de Base de Datos:

```sql
-- Usuario de producción (solo lectura para sincronización)
CREATE USER sync_user WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE paqueteria_v4 TO sync_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO sync_user;

-- Usuario de staging (lectura/escritura)
CREATE USER staging_user WITH PASSWORD 'staging_password';
GRANT ALL PRIVILEGES ON DATABASE paqueteria_staging TO staging_user;
```

### Backup Antes de Sincronización:

```bash
# Backup de staging antes de sincronizar
PGPASSWORD=$STAGING_PASS pg_dump \
  -h $STAGING_HOST \
  -U $STAGING_USER \
  -d $STAGING_DB \
  -F c \
  -f /backups/staging_backup_$(date +%Y%m%d_%H%M%S).dump
```

---

## 🚨 CASOS ESPECIALES

### Caso 1: Datos Sensibles

```bash
# Anonimizar datos sensibles en staging
psql -h $STAGING_HOST -U $STAGING_USER -d $STAGING_DB << EOF
-- Anonimizar emails
UPDATE users SET email = CONCAT('user_', id, '@test.com');

-- Anonimizar teléfonos
UPDATE customers SET phone = CONCAT('300000', id);

-- Anonimizar contraseñas (ya deberían estar hasheadas)
-- No es necesario si usas bcrypt/argon2
EOF
```

### Caso 2: Tablas Grandes

```bash
# Sincronizar solo últimos N registros
PGPASSWORD=$PROD_PASS pg_dump \
  -h $PROD_HOST \
  -U $PROD_USER \
  -d $PROD_DB \
  -t packages \
  --data-only \
  --no-owner \
  | head -n 10000 \
  | PGPASSWORD=$STAGING_PASS psql \
    -h $STAGING_HOST \
    -U $STAGING_USER \
    -d $STAGING_DB
```

### Caso 3: Rollback de Migración

```bash
# Si una migración falla en producción
alembic downgrade -1

# Revisar y corregir migración
# Volver a aplicar
alembic upgrade head
```

---

## 📊 MONITOREO

### Script de Verificación:

```python
# scripts/verify_db_sync.py
import psycopg2
from datetime import datetime

def check_sync_status():
    # Conectar a ambas bases de datos
    prod_conn = psycopg2.connect("postgresql://prod-url")
    staging_conn = psycopg2.connect("postgresql://staging-url")
    
    prod_cursor = prod_conn.cursor()
    staging_cursor = staging_conn.cursor()
    
    # Comparar conteos de tablas
    tables = ['users', 'packages', 'customers']
    
    for table in tables:
        prod_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        prod_count = prod_cursor.fetchone()[0]
        
        staging_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        staging_count = staging_cursor.fetchone()[0]
        
        diff = abs(prod_count - staging_count)
        status = "✅" if diff < 10 else "⚠️"
        
        print(f"{status} {table}: Prod={prod_count}, Staging={staging_count}, Diff={diff}")
    
    prod_conn.close()
    staging_conn.close()

if __name__ == "__main__":
    check_sync_status()
```

---

## 💰 COSTOS AWS RDS

### Estimación:

```
Producción (db.t3.small):
- Instancia: ~$30/mes
- Almacenamiento (20GB): ~$2.30/mes
- Backup: ~$1/mes
Total: ~$33/mes

Staging (db.t3.micro):
- Instancia: ~$15/mes
- Almacenamiento (20GB): ~$2.30/mes
- Backup: ~$1/mes
Total: ~$18/mes

TOTAL: ~$51/mes
```

### Optimización:
- Usar instancias más pequeñas en staging
- Apagar staging fuera de horario laboral (ahorro 50%)
- Usar Aurora Serverless para staging (pago por uso)

---

## 🎯 RECOMENDACIÓN FINAL

Para tu caso específico, recomiendo:

### ✅ Estrategia Híbrida:

1. **Base de datos separadas** (Producción + Staging)
2. **Sincronización diaria** de tablas existentes
3. **Migraciones independientes** en staging
4. **Merge controlado** a producción después de pruebas

### 📅 Timeline:

```
Día 1: Crear base de datos staging
Día 2: Sincronización inicial
Día 3: Configurar cron job
Día 4: Probar flujo completo
Día 5: Documentar proceso
```

### 🔄 Flujo Simplificado:

```
1. Desarrollar en staging (con datos reales copiados)
2. Probar features nuevas
3. Merge a main
4. Aplicar migraciones en producción
5. Deploy
```

---

## 📚 RECURSOS

- [PostgreSQL Replication](https://www.postgresql.org/docs/current/logical-replication.html)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

---

**Generado:** 27 de enero de 2026  
**Autor:** Kiro AI  
**Estado:** Estrategia recomendada para PAQUETEX
