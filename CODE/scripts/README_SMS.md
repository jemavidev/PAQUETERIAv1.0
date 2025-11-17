# Scripts de Prueba SMS

Este directorio contiene scripts para probar el sistema de envío de SMS.

## 📋 Scripts Disponibles

### 1. `enviar_sms_prueba.py` - Envío Simple y Directo

Script simple para enviar un SMS de prueba al número 3002596319.

**Uso:**
```bash
cd CODE
python scripts/enviar_sms_prueba.py
```

**Características:**
- ✅ Envío directo sin menús
- ✅ Verificación de configuración
- ✅ Confirmación antes de enviar
- ✅ Respeta el modo de prueba configurado

---

### 2. `test_sms.py` - Menú Interactivo Completo

Script con menú interactivo para múltiples opciones de prueba.

**Uso:**
```bash
cd CODE
python scripts/test_sms.py
```

**Opciones del menú:**
1. **Enviar SMS de prueba** - Envía un SMS real (consume créditos)
2. **Probar configuración** - Modo simulación (sin consumir créditos)
3. **Ver estadísticas** - Muestra estadísticas de SMS enviados
4. **Salir**

---

## 🔧 Requisitos Previos

### 1. Instalar Dependencias

```bash
cd CODE
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Asegúrate de que el archivo `CODE/.env` contenga:

```bash
# Configuración SMS (LIWA.co)
LIWA_API_KEY=c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$#NfFAS
LIWA_AUTH_URL=https://api.liwa.co/v2/auth/login
LIWA_FROM_NAME="PAQUETEX EL CLUB"
```

### 3. Base de Datos

Los scripts requieren acceso a la base de datos PostgreSQL configurada en `DATABASE_URL`.

---

## 📱 Número de Prueba

Los scripts están configurados para enviar al número: **3002596319**

Para cambiar el número, edita la variable `NUMERO_DESTINO` en el script.

---

## 💰 Costos

- **Modo Prueba** (`enable_test_mode=True`): Sin costo, solo simulación
- **Modo Real** (`enable_test_mode=False`): $0.50 COP por SMS

---

## 🔍 Verificar Configuración

Para verificar que la configuración está correcta:

```bash
cd CODE
cat .env | grep LIWA
```

Deberías ver las variables de configuración de LIWA.

---

## 📊 Ver Resultados

Los SMS enviados se registran en la tabla `notifications` de la base de datos.

Para ver los últimos SMS enviados:

```sql
SELECT 
    id,
    recipient,
    message,
    status,
    sent_at,
    cost_cents,
    is_test
FROM notifications
WHERE notification_type = 'SMS'
ORDER BY created_at DESC
LIMIT 10;
```

---

## 🐛 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"

**Solución:**
```bash
cd CODE
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python scripts/enviar_sms_prueba.py
```

### Error: "Autenticación Liwa fallida"

**Solución:** Verificar credenciales en `.env`
```bash
cat CODE/.env | grep LIWA
```

### Error: "Número de teléfono inválido"

**Solución:** Usar formato de 10 dígitos sin prefijos: `3002596319`

### Error: "Connection refused" o "Database error"

**Solución:** Verificar que la base de datos esté corriendo
```bash
# Si usas Docker
docker-compose ps

# Verificar conexión
psql $DATABASE_URL -c "SELECT 1"
```

---

## 📖 Documentación Adicional

Para más información sobre el sistema de SMS, consulta:
- `ANALISIS_SISTEMA_SMS.md` - Análisis completo del sistema
- `CODE/src/app/services/sms_service.py` - Código del servicio
- `CODE/src/app/routes/notifications.py` - Endpoints de API

---

## 🚀 Ejemplo de Uso Completo

```bash
# 1. Ir al directorio CODE
cd CODE

# 2. Verificar configuración
cat .env | grep LIWA

# 3. Instalar dependencias (si es necesario)
pip install -r requirements.txt

# 4. Ejecutar script simple
python scripts/enviar_sms_prueba.py

# 5. Confirmar envío cuando se solicite
# Responder 's' para enviar

# 6. Verificar resultado en la salida del script
```

---

## ⚙️ Configuración Avanzada

### Cambiar Modo de Prueba

Para activar/desactivar el modo de prueba, actualiza la configuración en la base de datos:

```sql
UPDATE sms_configuration 
SET enable_test_mode = true  -- false para modo real
WHERE is_active = true;
```

O usa la API:

```bash
curl -X PUT "http://localhost/api/v1/notifications/config/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{"enable_test_mode": true}'
```

---

**Última actualización:** 2025-01-24
**Versión:** 1.0.0
