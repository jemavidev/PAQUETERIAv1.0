# 🔧 Solución: Error al crear preferencias

## ❌ Problema

El botón de preferencias funciona, pero muestra error:
```
Error al cargar preferencias: Error al crear preferencias
```

**Causa:** La tabla `customer_preferences` no existe en la base de datos.

---

## ✅ Solución Rápida

### **Opción 1: Script Automático**

```bash
./crear_tabla_preferencias.sh
```

### **Opción 2: Manual (Recomendado)**

```bash
# 1. Conectar a la base de datos
docker-compose exec db psql -U postgres -d paquetex_db

# 2. Copiar y pegar este SQL:
CREATE TABLE IF NOT EXISTS customer_preferences (
    id SERIAL PRIMARY KEY,
    customer_id UUID NOT NULL UNIQUE,
    token VARCHAR(64) NOT NULL UNIQUE,
    sms_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    email_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    notify_package_received BOOLEAN NOT NULL DEFAULT TRUE,
    notify_package_delivered BOOLEAN NOT NULL DEFAULT TRUE,
    notify_package_announced BOOLEAN NOT NULL DEFAULT TRUE,
    notify_payment_due BOOLEAN NOT NULL DEFAULT TRUE,
    marketing_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_customer_preferences_customer_id ON customer_preferences(customer_id);
CREATE INDEX IF NOT EXISTS idx_customer_preferences_token ON customer_preferences(token);

# 3. Verificar que se creó
SELECT COUNT(*) FROM customer_preferences;

# 4. Salir
\q
```

### **Opción 3: Desde pgAdmin o DBeaver**

Si usas una herramienta gráfica:
1. Conecta a la base de datos `paquetex_db`
2. Abre el archivo `crear_tabla_customer_preferences.sql`
3. Ejecuta el SQL

---

## 🧪 Verificar que Funciona

Después de crear la tabla:

1. **Recarga la página** (Ctrl+F5)
2. **Haz clic en el botón morado** de preferencias
3. **Debería abrir el modal** sin errores
4. **Verás:**
   - Link de preferencias del cliente
   - Toggles de notificaciones
   - Botón "Guardar Cambios"

---

## 🔍 Verificar en Base de Datos

```sql
-- Ver si la tabla existe
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'customer_preferences';

-- Ver estructura de la tabla
\d customer_preferences

-- Ver registros (debería estar vacía al inicio)
SELECT * FROM customer_preferences;
```

---

## ❓ Si Sigue sin Funcionar

### **Verificar logs del servidor:**

```bash
docker-compose logs -f app | grep -i "preferences"
```

### **Verificar que la API está registrada:**

```bash
curl http://localhost:8000/api/customer/preferences/create \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "test"}'
```

Debería retornar un error de validación (UUID inválido), no un 404.

---

## 📝 Resumen

1. ✅ El botón funciona correctamente
2. ❌ La tabla no existe en la BD
3. 🔧 Ejecuta el SQL para crear la tabla
4. ✅ Recarga y prueba de nuevo

---

**Ejecuta el SQL y luego prueba de nuevo el botón!** 🚀
