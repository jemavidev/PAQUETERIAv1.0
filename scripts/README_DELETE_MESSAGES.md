# 🗑️ Eliminación de Mensajes - Guía de Uso

## ⚠️ ADVERTENCIA IMPORTANTE

**Estos scripts eliminarán TODOS los mensajes de la base de datos de forma PERMANENTE.**
Esta operación NO se puede deshacer. Úsalos con precaución.

---

## 📋 Archivos Disponibles

1. **delete_all_messages.sh** - Script bash interactivo (RECOMENDADO)
2. **delete_all_messages.py** - Script Python con confirmación
3. **delete_all_messages.sql** - Script SQL directo

---

## 🚀 Método 1: Script Bash Interactivo (RECOMENDADO)

Este es el método más fácil y seguro. El script te guiará paso a paso.

```bash
# Desde el directorio raíz del proyecto
./scripts/delete_all_messages.sh
```

El script te mostrará:
- Estadísticas actuales de mensajes
- Opciones para ejecutar (Python o SQL)
- Confirmación antes de eliminar

---

## 🐍 Método 2: Script Python Directo

Ejecutar el script Python dentro del contenedor backend:

```bash
# Opción A: Ejecutar directamente en el contenedor
docker compose -f docker-compose.prod.yml exec backend python /app/scripts/delete_all_messages.py

# Opción B: Entrar al contenedor y ejecutar
docker compose -f docker-compose.prod.yml exec backend bash
cd /app/scripts
python delete_all_messages.py
```

**Características:**
- ✅ Muestra estadísticas detalladas antes de eliminar
- ✅ Requiere confirmación explícita (escribir "SI")
- ✅ Muestra cada mensaje que será eliminado
- ✅ Verifica que la eliminación fue exitosa

---

## 🗄️ Método 3: Script SQL Directo

**⚠️ CUIDADO: Este método NO pide confirmación**

```bash
# Ejecutar SQL en el contenedor de base de datos
docker compose -f docker-compose.prod.yml exec db psql -U paquetex_user -d paquetex_db -f /scripts/delete_all_messages.sql
```

---

## 📊 Verificar Mensajes Actuales

Antes de eliminar, puedes verificar cuántos mensajes existen:

```bash
# Opción 1: Usando psql
docker compose -f docker-compose.prod.yml exec db psql -U paquetex_user -d paquetex_db -c "SELECT COUNT(*) as total, status, COUNT(*) FROM messages GROUP BY status;"

# Opción 2: Usando Python
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.database import SessionLocal
from app.models.message import Message
db = SessionLocal()
messages = db.query(Message).all()
print(f'Total mensajes: {len(messages)}')
for m in messages:
    print(f'  - ID: {m.id}, Estado: {m.status.value}, Tracking: {m.tracking_code}')
db.close()
"
```

---

## 🔄 Después de Eliminar

Después de eliminar los mensajes, puedes verificar que se eliminaron correctamente:

```bash
# Verificar que no quedan mensajes
docker compose -f docker-compose.prod.yml exec db psql -U paquetex_user -d paquetex_db -c "SELECT COUNT(*) FROM messages;"
```

Deberías ver: `count = 0`

---

## 🎯 Ejemplo de Uso Completo

```bash
# 1. Ver mensajes actuales
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.database import SessionLocal
from app.models.message import Message
db = SessionLocal()
print(f'Total mensajes: {db.query(Message).count()}')
db.close()
"

# 2. Ejecutar script de eliminación (RECOMENDADO)
./scripts/delete_all_messages.sh

# 3. Verificar que se eliminaron
docker compose -f docker-compose.prod.yml exec db psql -U paquetex_user -d paquetex_db -c "SELECT COUNT(*) FROM messages;"
```

---

## 🛡️ Seguridad

- ✅ El script Python pide confirmación explícita
- ✅ Muestra todos los mensajes antes de eliminar
- ✅ Verifica la eliminación después de ejecutar
- ⚠️ El script SQL NO pide confirmación (úsalo con cuidado)

---

## 📝 Notas

- Los mensajes eliminados NO se pueden recuperar
- Se recomienda hacer un backup antes de eliminar si es necesario
- El contador de IDs NO se reinicia automáticamente (los nuevos mensajes continuarán desde el último ID)
- Si quieres reiniciar el contador de IDs, descomenta la línea en el script SQL

---

## 🆘 Soporte

Si tienes problemas:
1. Verifica que los contenedores estén corriendo: `docker compose -f docker-compose.prod.yml ps`
2. Verifica los logs: `docker compose -f docker-compose.prod.yml logs backend`
3. Verifica la conexión a la base de datos

---

**Última actualización:** 2024-12-17
