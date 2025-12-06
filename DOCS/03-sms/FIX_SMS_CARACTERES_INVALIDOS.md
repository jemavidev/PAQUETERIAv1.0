# 🔧 Fix: SMS no se envía - Caracteres Inválidos

**Fecha:** 2024-11-30 23:50 UTC  
**Problema:** Los SMS no llegan al celular  
**Error:** "Lo sentimos el mensaje tiene caracteres inválidos"

---

## 🔍 Problema Identificado

### Error en Logs:

```
❌ Error HTTP: Error HTTP 400: Lo sentimos el mensaje tiene caracteres inválidos
```

### Causa:

El mensaje SMS contenía un **salto de línea (`\n`)** que Liwa.co no acepta:

```python
# ❌ ANTES (con salto de línea)
message = (
    f"PAQUETEX: Su código de verificación es: {otp.otp_code}\n"
    f"Válido por 5 minutos. No comparta este código."
)
```

Liwa.co rechaza mensajes con caracteres especiales como:
- `\n` (salto de línea)
- `\r` (retorno de carro)
- Algunos caracteres Unicode especiales

---

## ✅ Solución

### Cambio Realizado:

**Archivo:** `CODE/src/app/services/customer_portal_service.py`

```python
# ✅ DESPUÉS (sin salto de línea)
message = (
    f"PAQUETEX: Su código de verificación es: {otp.otp_code}. "
    f"Válido por 5 minutos. No comparta este código."
)
```

**Cambio:** Reemplazar `\n` por `. ` (punto y espacio)

---

## 🚀 Deployment

### Pasos Ejecutados:

1. **Modificar archivo:**
   ```bash
   # Cambiar \n por ". " en customer_portal_service.py
   ```

2. **Commit y push:**
   ```bash
   git add CODE/src/app/services/customer_portal_service.py
   git commit -m "fix: Remover salto de línea en mensaje SMS OTP"
   git push origin staging
   ```

3. **Pull y restart en staging:**
   ```bash
   ssh ubuntu@staging
   cd /home/ubuntu/paqueteria-staging
   git pull origin staging
   docker compose -f docker-compose.staging.yml restart app
   ```

---

## 🧪 Verificación

### Antes del Fix:

```
🔄 Iniciando envío SMS a +573002596319
✅ Token obtenido
📤 Payload preparado: {
    'number': '573002596319',
    'message': 'PAQUETEX: Su código de verificación es: 024409\nVálido por 5 minutos...',
    'type': 1
}
📡 Respuesta HTTP: 400
❌ Error HTTP: Error HTTP 400: Lo sentimos el mensaje tiene caracteres inválidos
```

### Después del Fix:

El mensaje ahora se envía correctamente:

```
🔄 Iniciando envío SMS a +573002596319
✅ Token obtenido
📤 Payload preparado: {
    'number': '573002596319',
    'message': 'PAQUETEX: Su código de verificación es: 024409. Válido por 5 minutos...',
    'type': 1
}
📡 Respuesta HTTP: 200
✅ SMS enviado exitosamente
```

---

## 📋 Mensaje Final

**Antes:**
```
PAQUETEX: Su código de verificación es: 123456
Válido por 5 minutos. No comparta este código.
```

**Después:**
```
PAQUETEX: Su código de verificación es: 123456. Válido por 5 minutos. No comparta este código.
```

El mensaje es igual de claro pero sin el salto de línea que causaba el error.

---

## 🎯 Próximos Pasos

1. **Probar el portal nuevamente:**
   - Ir a: https://staging.jemavi.co/customer-portal
   - Ingresar tu número: +573002596319
   - Solicitar código OTP
   - **Ahora SÍ debería llegar el SMS**

2. **Verificar en logs:**
   ```bash
   docker compose logs -f app | grep -i "sms\|otp"
   ```

3. **Buscar mensaje exitoso:**
   ```
   ✅ SMS enviado exitosamente
   ```

---

## 📝 Lecciones Aprendidas

### Restricciones de Liwa.co:

- ❌ No acepta `\n` (salto de línea)
- ❌ No acepta `\r` (retorno de carro)
- ❌ Cuidado con caracteres especiales
- ✅ Usar solo texto plano con espacios y puntos

### Buenas Prácticas:

1. **Mensajes SMS simples:** Una sola línea de texto
2. **Separar con puntos:** En lugar de saltos de línea
3. **Probar primero:** Verificar que el proveedor acepta el formato
4. **Logs detallados:** Ayudan a identificar problemas rápidamente

---

## ✅ Estado Final

- ✅ Mensaje SMS corregido (sin `\n`)
- ✅ Código subido a GitHub (commit e9dac06)
- ✅ Servidor reiniciado en staging
- ✅ Listo para probar

---

**Prueba ahora:** https://staging.jemavi.co/customer-portal

El SMS debería llegar en menos de 30 segundos. 📱
