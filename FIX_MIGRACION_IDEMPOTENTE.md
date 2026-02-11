# Fix: Migración Idempotente - COMPLETADO ✅

## 🔴 Problema
Al ejecutar `alembic upgrade head` se obtenía el error:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateColumn) 
column "tipo_factura" of relation "invoices_v2" already exists
```

## 🔍 Causa
La columna `tipo_factura` ya fue creada anteriormente cuando ejecutaste el script `aplicar_migracion_tipo_factura.py`, pero Alembic no tenía registro de que la migración ya se aplicó.

## ✅ Solución Implementada

### Migración Idempotente
Modificada la migración `20260211_092552_add_tipo_factura.py` para que sea idempotente:

**Antes:**
```python
def upgrade():
    op.add_column('invoices_v2', 
        sa.Column('tipo_factura', sa.String(20), nullable=False, server_default='reventa')
    )
    op.create_index('idx_invoices_tipo_factura', 'invoices_v2', ['tipo_factura'])
```

**Después:**
```python
def upgrade():
    # Verificar si la columna ya existe antes de agregarla
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('invoices_v2')]
    
    if 'tipo_factura' not in columns:
        op.add_column('invoices_v2', 
            sa.Column('tipo_factura', sa.String(20), nullable=False, server_default='reventa')
        )
        print("✅ Columna 'tipo_factura' agregada")
    else:
        print("ℹ️  Columna 'tipo_factura' ya existe, saltando...")
    
    # Verificar si el índice ya existe antes de crearlo
    indexes = [idx['name'] for idx in inspector.get_indexes('invoices_v2')]
    
    if 'idx_invoices_tipo_factura' not in indexes:
        op.create_index('idx_invoices_tipo_factura', 'invoices_v2', ['tipo_factura'])
        print("✅ Índice 'idx_invoices_tipo_factura' creado")
    else:
        print("ℹ️  Índice 'idx_invoices_tipo_factura' ya existe, saltando...")
```

### Beneficios
1. ✅ La migración puede ejecutarse múltiples veces sin errores
2. ✅ Verifica si la columna existe antes de crearla
3. ✅ Verifica si el índice existe antes de crearlo
4. ✅ Muestra mensajes informativos sobre qué se hizo

## 🚀 Próximos Pasos

### 1. Commit y push de los cambios
```bash
git add CODE/alembic/versions/20260211_092552_add_tipo_factura.py
git commit -m "fix: hacer migración tipo_factura idempotente

- Verificar si columna existe antes de crearla
- Verificar si índice existe antes de crearlo
- Evitar error DuplicateColumn en re-ejecuciones

Fixes: sqlalchemy.exc.ProgrammingError DuplicateColumn"
git push origin staging
```

### 2. Ejecutar deploy
```bash
./deploy.sh staging
```

Ahora la migración se ejecutará sin errores:
- Si la columna ya existe: Saltará la creación y mostrará mensaje informativo
- Si la columna no existe: La creará normalmente

## 📊 Resultado Esperado

Al ejecutar `alembic upgrade head`:
```
INFO  [alembic.runtime.migration] Running upgrade ... -> 20260211_092552, add tipo_factura to invoices_v2
ℹ️  Columna 'tipo_factura' ya existe, saltando...
ℹ️  Índice 'idx_invoices_tipo_factura' ya existe, saltando...
```

## ✅ Estado
- ✅ Migración modificada para ser idempotente
- ✅ Verifica existencia de columna e índice
- ✅ Listo para commit y deploy

## 📝 Notas Técnicas

### ¿Qué es una migración idempotente?
Una migración idempotente es aquella que puede ejecutarse múltiples veces sin causar errores ni efectos secundarios. Siempre produce el mismo resultado final, independientemente de cuántas veces se ejecute.

### ¿Por qué es importante?
- Evita errores en re-despliegues
- Facilita rollbacks y re-aplicaciones
- Hace el sistema más robusto
- Permite recuperación de estados inconsistentes

### Alternativa: Stamp
Si prefieres no modificar la migración, puedes marcarla como aplicada:
```bash
docker-compose -f docker-compose.staging.yml exec app alembic stamp 20260211_092552
```

Esto le dice a Alembic que la migración ya está aplicada sin ejecutarla.

---

**Recomendación**: Usar la migración idempotente (solución implementada) es más robusto y seguro.
