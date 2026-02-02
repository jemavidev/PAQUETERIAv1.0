# Instrucciones para Resolver Conflicto de Migraciones

## Problema
La migración está fallando porque intenta crear columnas que ya existen en la base de datos de staging.

## Solución: Marcar Migraciones como Aplicadas

### Opción 1: Usando el Script Python (RECOMENDADO)

Si tienes el entorno de desarrollo configurado:

```bash
cd CODE
python fix_migration_conflict.py
```

### Opción 2: Usando Docker

Si tienes los contenedores corriendo:

```bash
# Desde el directorio raíz del proyecto
docker compose -f docker-compose.staging.yml exec web python CODE/fix_migration_conflict.py
```

### Opción 3: Manualmente con psql

Si tienes `psql` instalado:

```bash
cd CODE
psql "postgresql://jveyes:a?HC!2.*1#?[==:|289qAI=)#V4kDzl\$@ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com:5432/paqueteria_staging" -f fix_migration_conflict.sql
```

### Opción 4: SQL Directo (Copiar y Pegar)

Conéctate a la base de datos de staging y ejecuta:

```sql
-- Verificar migraciones actuales
SELECT version_num, applied_at 
FROM alembic_version 
ORDER BY applied_at DESC;

-- Verificar si las columnas existen
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'invoices' 
AND column_name IN ('cufe_status', 'dian_status');

-- Si cufe_status existe, marcar la migración como aplicada
INSERT INTO alembic_version (version_num)
SELECT 'add_cufe_dian_status_fields'
WHERE NOT EXISTS (
    SELECT 1 FROM alembic_version 
    WHERE version_num = 'add_cufe_dian_status_fields'
)
AND EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'invoices' AND column_name = 'cufe_status'
);

-- Verificar si cufe_records existe
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'cufe_records';

-- Si cufe_records existe, marcar la migración como aplicada
INSERT INTO alembic_version (version_num)
SELECT 'create_cufe_records_table'
WHERE NOT EXISTS (
    SELECT 1 FROM alembic_version 
    WHERE version_num = 'create_cufe_records_table'
)
AND EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name = 'cufe_records'
);

-- Verificar resultado
SELECT version_num, applied_at 
FROM alembic_version 
ORDER BY applied_at DESC
LIMIT 10;
```

## Después de Aplicar la Corrección

Una vez que hayas marcado las migraciones como aplicadas, ejecuta:

```bash
cd CODE
alembic upgrade head
```

## Verificar que Todo Funciona

```bash
cd CODE
alembic current
alembic history --verbose
```

## Notas Importantes

- ⚠️ **Estás trabajando con la base de datos de STAGING en AWS RDS**
- 📍 Host: `ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com`
- 🗄️ Database: `paqueteria_staging`
- 👤 Usuario: `jveyes`

## Si Necesitas Ayuda

Si ninguna de estas opciones funciona, puedes:
1. Conectarte a la base de datos usando un cliente GUI (DBeaver, pgAdmin, etc.)
2. Ejecutar manualmente las consultas SQL de la Opción 4
3. Luego ejecutar `alembic upgrade head`
