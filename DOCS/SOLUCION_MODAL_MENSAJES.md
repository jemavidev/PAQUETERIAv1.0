# 🔧 Solución: Modal de Mensajes No Funciona

## 🔍 Problema Identificado

Cuando haces clic en el botón del modal, eres redirigido a `/packages` en lugar de abrir el modal.

### Causa Raíz

El problema es de **autenticación**:

1. El endpoint `/api/messages/{message_id}` requiere autenticación
2. Tu sesión no tiene un token válido o ha expirado
3. El `AuthMiddleware` intercepta la petición y retorna 401
4. El navegador te redirige a otra página

## ✅ Soluciones

### Solución 1: Iniciar Sesión Correctamente (RECOMENDADO)

1. **Cierra sesión completamente:**
   - Ve a https://staging.jemavi.co/auth/logout
   - O borra las cookies del sitio

2. **Inicia sesión nuevamente:**
   - Ve a https://staging.jemavi.co/auth/login
   - Ingresa tus credenciales de admin/operador
   - Asegúrate de que el login sea exitoso

3. **Verifica que estés autenticado:**
   - Abre la consola del navegador (F12)
   - Ve a la pestaña "Application" > "Cookies"
   - Verifica que exista la cookie `access_token` con un valor válido

4. **Prueba el modal nuevamente:**
   - Ve a https://staging.jemavi.co/messages
   - Haz clic en el botón verde del mensaje
   - El modal debería abrirse correctamente

### Solución 2: Hacer el Endpoint Público (TEMPORAL - Solo para Testing)

Si necesitas probar sin autenticación, puedes agregar el endpoint a las rutas públicas:

**Archivo:** `CODE/src/app/config_routes.py`

```python
API_PUBLIC_ROUTES: Set[str] = {
    # ... otras rutas ...
    
    # Mensajes (temporal para testing)
    "/api/messages",  # Agregar esta línea
    
    # ... resto de rutas ...
}
```

**⚠️ ADVERTENCIA:** Esto hará que TODOS los mensajes sean públicos. NO uses esto en producción.

### Solución 3: Verificar Cookies en el Navegador

Si ya iniciaste sesión pero sigue sin funcionar:

1. **Abre la consola del navegador (F12)**

2. **Ejecuta este código:**
   ```javascript
   // Verificar cookies
   console.log('Cookies:', document.cookie);
   
   // Verificar token
   const token = document.cookie.split('; ').find(row => row.startsWith('access_token='));
   console.log('Token:', token);
   
   // Probar endpoint manualmente
   fetch('/api/messages/52', {
       credentials: 'same-origin'
   })
   .then(r => r.json())
   .then(d => console.log('Respuesta:', d))
   .catch(e => console.error('Error:', e));
   ```

3. **Analiza la respuesta:**
   - Si ves `"detail": "No autenticado"` → Tu sesión expiró, inicia sesión nuevamente
   - Si ves los datos del mensaje → El problema está en otro lado
   - Si ves un error de red → Problema de conectividad

## 🧪 Cómo Probar que Funciona

### Paso 1: Verificar Autenticación

```bash
# Desde tu terminal local
curl -s "https://staging.jemavi.co/api/messages/52" \
  -H "Cookie: access_token=TU_TOKEN_AQUI" \
  | python3 -m json.tool
```

Si ves los datos del mensaje, tu token es válido.

### Paso 2: Probar en el Navegador

1. Ve a https://staging.jemavi.co/messages
2. Abre la consola (F12)
3. Ejecuta: `openMessageDetail(52)`
4. El modal debería abrirse

### Paso 3: Verificar el Modal

Una vez abierto el modal, deberías ver:

- ✅ Información del cliente (nombre, teléfono, email)
- ✅ Información del paquete (tracking)
- ✅ Contenido de la pregunta
- ✅ Formulario de respuesta (si el mensaje está ABIERTO)
- ✅ Botones "Cancelar" y "Responder"

## 🔐 Credenciales de Prueba

Si no tienes credenciales, contacta al administrador del sistema para que te cree una cuenta con rol de ADMIN u OPERADOR.

## 📝 Notas Importantes

### Por qué se requiere autenticación

Los mensajes contienen información sensible de clientes:
- Nombres completos
- Teléfonos
- Emails
- Información de paquetes

Por seguridad, solo usuarios autenticados (admin/operador) pueden acceder a esta información.

### Roles que pueden acceder

- ✅ **ADMIN** - Acceso completo a todos los mensajes
- ✅ **OPERADOR** - Acceso completo a todos los mensajes
- ❌ **USUARIO** - Solo puede ver sus propios mensajes

### Tiempo de expiración del token

Los tokens de autenticación expiran después de:
- **30 minutos** de inactividad (por defecto)

Si tu sesión expira, simplemente inicia sesión nuevamente.

## 🆘 Si Sigue Sin Funcionar

### Opción 1: Revisar Logs del Backend

```bash
# Ver logs del backend en tiempo real
docker compose -f docker-compose.prod.yml logs -f backend
```

Busca mensajes de error relacionados con autenticación o mensajes.

### Opción 2: Verificar que el Mensaje Existe

```bash
# Verificar que el mensaje ID 52 existe
python3 -c "
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT', 5432),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor()
cursor.execute('SELECT id, subject, status FROM messages WHERE id = 52')
result = cursor.fetchone()

if result:
    print(f'✅ Mensaje encontrado: ID={result[0]}, Asunto={result[1]}, Estado={result[2]}')
else:
    print('❌ Mensaje no encontrado')

cursor.close()
conn.close()
"
```

### Opción 3: Crear un Nuevo Mensaje

Si el mensaje 52 no existe o tiene problemas, crea uno nuevo:

```bash
python3 scripts/create_simple_message.py
```

---

## 📊 Resumen

**Problema:** Modal no abre, redirige a `/packages`  
**Causa:** Falta de autenticación válida  
**Solución:** Iniciar sesión correctamente en https://staging.jemavi.co/auth/login

**Estado del Modal:** ✅ Funcionando correctamente (cuando estás autenticado)  
**Estado del Endpoint:** ✅ Funcionando correctamente (requiere autenticación)  
**Estado del Mensaje de Prueba:** ✅ Creado (ID: 52)

---

**Última actualización:** 2024-12-17
