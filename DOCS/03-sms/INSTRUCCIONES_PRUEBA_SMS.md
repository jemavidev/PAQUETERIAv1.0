# 📱 Instrucciones para Enviar SMS de Prueba al 3002596319

## ✅ Respuesta Rápida

**SÍ, es posible enviar un SMS de prueba al número 3002596319.**

El sistema está completamente configurado con LIWA.co y listo para usar.

---

## 🚀 Opción 1: Método Más Rápido (Recomendado)

### Paso 1: Abrir Terminal

```bash
cd CODE
```

### Paso 2: Ejecutar Script

```bash
python scripts/enviar_sms_prueba.py
```

### Paso 3: Confirmar Envío

Cuando el script pregunte:
```
¿Desea continuar con el envío? (s/n):
```

Responde: `s`

### Paso 4: Verificar Resultado

El script mostrará:
```
✅ SMS ENVIADO EXITOSAMENTE

📋 Detalles:
   • ID Notificación: 12345
   • Estado: sent
   • Mensaje: SMS enviado exitosamente
   • Costo: $0.50 COP
```

**¡Listo!** El SMS llegará al número 3002596319 en segundos.

---

## 🔧 Opción 2: Usando el Menú Interactivo

### Paso 1: Ejecutar Script con Menú

```bash
cd CODE
python scripts/test_sms.py
```

### Paso 2: Seleccionar Opción

```
Opciones:
1. Enviar SMS de prueba (consume créditos)
2. Probar configuración (modo simulación)
3. Ver estadísticas de SMS
4. Salir

Seleccione una opción (1-4): 1
```

### Paso 3: Confirmar y Enviar

Sigue las instrucciones en pantalla.

---

## 🌐 Opción 3: Usando la API REST

Si el servidor está corriendo:

```bash
curl -X POST "http://localhost/api/v1/notifications/send/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "recipient": "3002596319",
    "message": "Mensaje de prueba desde PAQUETEX EL CLUB",
    "priority": "ALTA",
    "is_test": false
  }'
```

---

## 📋 Requisitos Previos

### 1. Verificar Configuración

```bash
cd CODE
cat .env | grep LIWA
```

Deberías ver:
```
LIWA_API_KEY=c52d8399ac63a24563ee8a967bafffc6cb8d8dfa
LIWA_ACCOUNT=00486396309
LIWA_PASSWORD=6fEuRnd*$#NfFAS
```

✅ **Configuración correcta**

### 2. Instalar Dependencias (si es necesario)

```bash
cd CODE
pip install -r requirements.txt
```

### 3. Base de Datos

Asegúrate de que la base de datos esté corriendo y accesible.

---

## 💰 Información de Costos

| Tipo de Envío | Costo | Descripción |
|---------------|-------|-------------|
| **Modo Prueba** | $0.00 | Simulación, no envía SMS real |
| **Modo Real** | $0.50 COP | Envía SMS real al número |

---

## 🔍 Verificar Envío

### Opción A: En la Salida del Script

El script mostrará el resultado inmediatamente.

### Opción B: En la Base de Datos

```sql
SELECT 
    id,
    recipient,
    message,
    status,
    sent_at,
    cost_cents
FROM notifications
WHERE recipient = '3002596319'
ORDER BY created_at DESC
LIMIT 1;
```

### Opción C: Usando la API

```bash
curl -X GET "http://localhost/api/v1/notifications/stats/?days=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📱 Detalles del Envío

- **Número destino:** 3002596319
- **Mensaje:** "Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB. Sistema funcionando correctamente."
- **Remitente:** PAQUETEX EL CLUB
- **Proveedor:** LIWA.co
- **Tiempo estimado de entrega:** 5-30 segundos

---

## ⚠️ Consideraciones Importantes

### Modo de Prueba vs Modo Real

El sistema puede estar configurado en dos modos:

1. **Modo Prueba** (`enable_test_mode=True`)
   - ✅ No consume créditos
   - ✅ Simula el envío
   - ✅ Guarda registro en BD
   - ❌ No envía SMS real

2. **Modo Real** (`enable_test_mode=False`)
   - ✅ Envía SMS real
   - ✅ Llega al número
   - ❌ Consume créditos ($0.50 COP)

### Verificar Modo Actual

El script mostrará automáticamente el modo configurado:
```
✓ Modo prueba: NO (consumirá créditos)
```
o
```
✓ Modo prueba: SÍ (sin costo)
```

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
cd CODE
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python scripts/enviar_sms_prueba.py
```

### Error: "Autenticación Liwa fallida"

Verificar credenciales:
```bash
cat CODE/.env | grep LIWA
```

### Error: "Número de teléfono inválido"

Usar formato de 10 dígitos: `3002596319` (sin +57)

### Error: "Database connection failed"

Verificar que la base de datos esté corriendo:
```bash
docker-compose ps
```

---

## 📊 Ejemplo de Salida Exitosa

```
======================================================================
ENVÍO DE SMS DE PRUEBA - PAQUETEX EL CLUB
======================================================================

📱 Número destino: 3002596319
💬 Mensaje: Hola! Este es un mensaje de prueba desde PAQUETEX EL CLUB...
📏 Longitud: 75 caracteres

🔧 Verificando configuración...
   ✓ Proveedor: liwa
   ✓ Cuenta: 00486396309
   ✓ Modo prueba: NO (consumirá créditos)

======================================================================
⚠️  ATENCIÓN: Este envío consumirá créditos reales de SMS
⚠️  Costo estimado: $0.50 COP

¿Desea continuar con el envío? (s/n): s

📤 Enviando SMS...

======================================================================
RESULTADO DEL ENVÍO
======================================================================

✅ SMS ENVIADO EXITOSAMENTE

📋 Detalles:
   • ID Notificación: 550e8400-e29b-41d4-a716-446655440000
   • Estado: sent
   • Mensaje: SMS enviado exitosamente
   • Costo: $0.50 COP

💡 El SMS debería llegar en los próximos segundos

======================================================================
```

---

## 📞 Información del Proveedor

- **Proveedor:** LIWA.co
- **Cuenta:** 00486396309
- **API:** https://api.liwa.co/v2/
- **Documentación:** https://api.liwa.co/docs

---

## 📖 Documentación Adicional

Para más información:

1. **Análisis Completo:** `ANALISIS_SISTEMA_SMS.md`
2. **README Scripts:** `CODE/scripts/README_SMS.md`
3. **Código Fuente:** `CODE/src/app/services/sms_service.py`
4. **API Endpoints:** `CODE/src/app/routes/notifications.py`

---

## ✅ Resumen

**Para enviar el SMS de prueba:**

```bash
cd CODE
python scripts/enviar_sms_prueba.py
```

Responde `s` cuando se solicite confirmación.

**Costo:** $0.50 COP

**Tiempo de entrega:** 5-30 segundos

**Estado:** ✅ Sistema operacional y listo

---

**Fecha:** 2025-01-24  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para usar
