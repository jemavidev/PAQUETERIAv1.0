# 🎯 Solución Definitiva - Sin Complicaciones

**Fecha:** 27 de enero de 2026  
**Enfoque:** Primero que funcione manualmente, luego automatizar

---

## 📋 Plan Simple en 3 Fases

### Fase 1: Script Manual que Funcione ✅
Crear un script que el usuario ejecute manualmente en el servidor.

### Fase 2: Botón que Llame al Script ⏳
Una vez que el script funcione, conectarlo al botón.

### Fase 3: Automatización Opcional ⏳
Si se desea, agregar cron job o similar.

---

## 🚀 FASE 1: Script Manual (EMPEZAR AQUÍ)

### Paso 1: Verificar que tienes PostgreSQL client

```bash
ssh staging
which pg_dump
```

**Si NO existe:**
```bash
# Rocky Linux / RHEL
sudo dnf install postgresql -y

# O Ubuntu/Debian
sudo apt-get install postgresql-client -y
```

### Paso 2: Crear el script de sincronización

```bash
ssh staging
cat > ~/sync_manual.sh << 'EOF'
#!/bin/bash
# Script manual de sincronización

HOST="ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com"
USER="jveyes"
PASS='a?HC!2.*1#?[==:|289qAI=)#V4kDzl$'

export PGPASSWORD="$PASS"

echo "🔄 Sincronizando producción → staging..."
echo ""

# Exportar
echo "📦 Exportando producción..."
pg_dump -h "$HOST" -U "$USER" -d paqueteria_v4 -F c -f /tmp/backup.dump --no-owner --no-acl

if [ $? -eq 0 ]; then
    echo "✅ Exportado"
else
    echo "❌ Error en exportación"
    exit 1
fi

echo ""

# Restaurar
echo "📥 Restaurando en staging..."
pg_restore -h "$HOST" -U "$USER" -d paqueteria_staging /tmp/backup.dump --clean --if-exists --no-owner --no-acl 2>&1 | grep -v "^WARNING" || true

if [ $? -le 1 ]; then
    echo "✅ Restaurado"
else
    echo "❌ Error en restauración"
    exit 1
fi

echo ""
echo "✅ Sincronización completada"
EOF

chmod +x ~/sync_manual.sh
```

### Paso 3: Probar el script

```bash
~/sync_manual.sh
```

**Resultado esperado:**
```
🔄 Sincronizando producción → staging...

📦 Exportando producción...
✅ Exportado

📥 Restaurando en staging...
✅ Restaurado

✅ Sincronización completada
```

---

## ✅ Si el Script Manual Funciona

**¡PERFECTO!** Ahora podemos pasar a la Fase 2.

---

## ❌ Si el Script Manual NO Funciona

### Error: "pg_dump: command not found"

```bash
# Instalar PostgreSQL client
sudo dnf install postgresql -y

# Verificar
which pg_dump
pg_dump --version
```

### Error: "connection refused" o "could not connect"

```bash
# Verificar conectividad
ping ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com

# Probar conexión
psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
     -U jveyes -d paqueteria_v4 -c "SELECT 1;"
```

### Error: "authentication failed"

Verificar credenciales en `.env.staging`:
```bash
cat ~/paqueteria-staging/.env.staging | grep POSTGRES
```

---

## 🎯 FASE 2: Conectar al Botón (Solo después de que Fase 1 funcione)

Una vez que `~/sync_manual.sh` funcione perfectamente, podemos hacer que el botón lo ejecute.

### Opción A: Endpoint que ejecuta el script

Modificar `sync_staging.py` para ejecutar el script:

```python
import subprocess

async def run_sync():
    result = subprocess.run(
        ["/home/rocky/sync_manual.sh"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        sync_status["last_result"] = "success"
    else:
        sync_status["last_result"] = f"error: {result.stderr}"
```

### Opción B: Webhook simple

Crear un endpoint HTTP simple que ejecute el script.

---

## 📝 Resumen

1. **PRIMERO:** Hacer que `~/sync_manual.sh` funcione
2. **SEGUNDO:** Conectarlo al botón
3. **TERCERO:** Automatizar si se desea

**No pasar al paso 2 hasta que el paso 1 funcione perfectamente.**

---

## 🆘 Necesito Ayuda

Si el script manual no funciona, comparte:

```bash
# 1. Verificar PostgreSQL client
which pg_dump
pg_dump --version

# 2. Probar conexión
psql -h ls-abe25e9bea57818f0ee32555c0e7b4a10e361535.ctobuhtlkwoj.us-east-1.rds.amazonaws.com \
     -U jveyes -d paqueteria_v4 -c "SELECT version();"

# 3. Ejecutar script y compartir salida
~/sync_manual.sh
```

---

**Enfoque:** Paso a paso, sin complicaciones. Primero que funcione manualmente.
