# Instrucciones para Probar el Fix de Loop de Redirección

## Problema Encontrado

Había **DOS definiciones duplicadas** de la ruta `/auth/login` en `public.py`:
- Una en la línea 242 (vieja, sin el fix)
- Otra en la línea 342 (nueva, con el fix)

FastAPI estaba usando la primera definición, por eso el fix no funcionaba.

## Solución Aplicada

✅ Eliminé la definición duplicada (línea 242)
✅ Dejé solo la definición con el fix (línea 342)

## Pasos para Probar

### 1. Reiniciar el Servidor

```bash
# Opción A: Si usas docker-compose
cd CODE
docker-compose restart app

# Opción B: Si usas docker compose (sin guión)
cd CODE
docker compose restart app

# Opción C: Si el servidor corre directamente
# Detén el proceso (Ctrl+C) y vuelve a iniciarlo
```

### 2. Ejecutar Tests Automatizados

```bash
cd CODE
./test_current_behavior.sh
```

**Resultado esperado:**
- ✓ Servidor funcionando
- ✓ /admin redirige a login
- ✓ Página de login carga
- ✓ Mensaje de sesión expirada (ahora debería funcionar)
- ✓ Limpieza de cookies (ahora debería funcionar)

### 3. Prueba Manual (Recomendado)

#### Escenario 1: Login Normal

1. Abre tu navegador en modo incógnito
2. Ve a: `http://localhost:8000/admin`
3. Deberías ser redirigido a: `http://localhost:8000/auth/login?redirect=/admin`
4. Ingresa tus credenciales:
   - Usuario: `jesus`
   - Contraseña: `jesusSeaboard12`
5. Haz clic en "Iniciar Sesión"
6. **Resultado esperado**: Deberías ser redirigido a `/admin` SIN entrar en loop

#### Escenario 2: Ya Autenticado

1. Con la sesión del Escenario 1 activa
2. Intenta ir directamente a: `http://localhost:8000/auth/login`
3. **Resultado esperado**: Deberías ser redirigido automáticamente a `/packages` (o a la URL en el parámetro `redirect`)

#### Escenario 3: Token Expirado

1. Abre DevTools (F12) > Application > Cookies
2. Edita la cookie `access_token` y cambia su valor a: `invalid_token_123`
3. Ve a: `http://localhost:8000/auth/login`
4. **Resultado esperado**: 
   - Deberías ver un mensaje amarillo: "Tu sesión ha expirado. Por favor, inicia sesión nuevamente."
   - Las cookies inválidas deberían ser eliminadas automáticamente

#### Escenario 4: Verificar que NO hay Loop

1. Cierra todas las pestañas del navegador
2. Abre una nueva pestaña
3. Ve a: `http://localhost:8000/admin`
4. Inicia sesión
5. **Resultado esperado**: Deberías llegar a `/admin` sin problemas
6. **NO debería pasar**: Que te redirija de vuelta a login infinitamente

### 4. Verificar Logs del Servidor

Mientras pruebas, revisa los logs del servidor:

```bash
# Si usas docker-compose
docker-compose logs -f app | grep -i "login\|redirect\|token"

# Busca mensajes como:
# "Usuario ya autenticado, redirigiendo a: /admin"
# "Token expirado o inválido detectado, limpiando cookies"
```

## Tests con cURL

Si prefieres probar con cURL:

### Test 1: Token Expirado

```bash
# Crear cookies inválidas
cat > /tmp/test_cookies.txt << EOF
# Netscape HTTP Cookie File
localhost	FALSE	/	FALSE	0	access_token	invalid_token_xyz
localhost	FALSE	/	FALSE	0	user_id	1
localhost	FALSE	/	FALSE	0	user_name	testuser
localhost	FALSE	/	FALSE	0	user_role	admin
EOF

# Acceder a /auth/login con cookies inválidas
curl -s -b /tmp/test_cookies.txt http://localhost:8000/auth/login | grep -i "sesión ha expirado"

# Resultado esperado: Debería encontrar el texto "Tu sesión ha expirado"
```

### Test 2: Limpieza de Cookies

```bash
# Verificar headers Set-Cookie
curl -s -i -b /tmp/test_cookies.txt http://localhost:8000/auth/login | grep -i "set-cookie"

# Resultado esperado: Deberías ver headers como:
# Set-Cookie: access_token=; Path=/; Max-Age=0
# Set-Cookie: user_id=; Path=/; Max-Age=0
```

### Test 3: Login y Acceso a /admin

```bash
# Login
curl -s -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jesus&password=jesusSeaboard12" \
  -c /tmp/login_cookies.txt \
  http://localhost:8000/api/auth/login | jq .

# Acceder a /admin con las cookies
curl -s -b /tmp/login_cookies.txt http://localhost:8000/admin | grep -i "dashboard\|administración"

# Resultado esperado: Debería encontrar contenido del dashboard
```

## Checklist de Verificación

- [ ] Servidor reiniciado después de los cambios
- [ ] Test automatizado ejecutado (`./test_current_behavior.sh`)
- [ ] Prueba manual: Login normal funciona
- [ ] Prueba manual: Auto-redirect desde /auth/login funciona
- [ ] Prueba manual: Mensaje de sesión expirada se muestra
- [ ] Prueba manual: NO hay loop de redirección
- [ ] Logs del servidor muestran mensajes correctos

## Problemas Comunes

### Problema: "Credenciales incorrectas"

**Solución**: Verifica que el usuario existe en la base de datos:
```bash
# Consultar usuarios
docker-compose exec db psql -U paqueteria_user -d paqueteria_db -c "SELECT username, email, is_active FROM users;"
```

### Problema: "El fix no funciona"

**Solución**: Asegúrate de haber reiniciado el servidor después de los cambios.

### Problema: "Sigo viendo el loop"

**Solución**: 
1. Limpia las cookies del navegador (DevTools > Application > Clear storage)
2. Cierra todas las pestañas
3. Abre una nueva pestaña en modo incógnito
4. Intenta de nuevo

## Resultado Esperado Final

Después de aplicar el fix:

✅ **Login funciona correctamente**
✅ **Acceso a /admin con sesión válida funciona**
✅ **Auto-redirect desde /auth/login cuando ya estás autenticado**
✅ **Mensaje claro cuando la sesión expira**
✅ **Limpieza automática de cookies inválidas**
✅ **NO hay loop de redirección infinito**

## Contacto

Si encuentras algún problema, revisa:
1. Los logs del servidor
2. Las cookies en DevTools
3. La consola del navegador (F12 > Console)

Y documenta:
- Qué estabas haciendo
- Qué esperabas que pasara
- Qué pasó realmente
- Capturas de pantalla si es posible
