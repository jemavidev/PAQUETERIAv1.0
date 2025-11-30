# ✅ Checklist de Pruebas - Fix Loop de Redirección

## Estado del Fix

**Verificación Automática**: ✅ PASÓ

```bash
cd CODE
./verify_fix.sh
```

---

## Pruebas Manuales

### 🔧 Preparación

- [ ] Servidor está corriendo (`docker-compose ps` o verificar http://localhost:8000/health)
- [ ] Navegador abierto (preferiblemente Chrome o Firefox)
- [ ] DevTools abierto (F12) para ver cookies y consola

---

### 📋 Escenario 1: Login Normal (Primera Vez)

**Objetivo**: Verificar que el login funciona sin problemas

1. [ ] Abrir navegador en **modo incógnito** (Ctrl+Shift+N)
2. [ ] Ir a: `http://localhost:8000/admin`
3. [ ] Verificar que redirige a: `http://localhost:8000/auth/login?redirect=/admin`
4. [ ] Ingresar credenciales:
   - Usuario: `jesus`
   - Contraseña: `jesusSeaboard12`
5. [ ] Click en "Iniciar Sesión"
6. [ ] **VERIFICAR**: Deberías llegar a `/admin` (dashboard)
7. [ ] **VERIFICAR**: NO deberías ver el formulario de login nuevamente
8. [ ] **VERIFICAR**: Deberías ver tu nombre en el header

**Resultado esperado**: ✅ Login exitoso, acceso a /admin sin loop

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

### 📋 Escenario 2: Auto-Redirect (Ya Autenticado)

**Objetivo**: Verificar que no muestra login si ya estás autenticado

1. [ ] Con la sesión del Escenario 1 **activa**
2. [ ] Ir directamente a: `http://localhost:8000/auth/login`
3. [ ] **VERIFICAR**: Deberías ser redirigido automáticamente
4. [ ] **VERIFICAR**: NO deberías ver el formulario de login
5. [ ] **VERIFICAR**: Deberías estar en `/packages` o `/admin`

**Resultado esperado**: ✅ Redirigido automáticamente, no muestra formulario

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

### 📋 Escenario 3: Token Expirado

**Objetivo**: Verificar mensaje de sesión expirada y limpieza de cookies

1. [ ] Con la sesión del Escenario 1 **activa**
2. [ ] Abrir DevTools (F12) > Application > Cookies
3. [ ] Buscar cookie `access_token`
4. [ ] Cambiar su valor a: `invalid_token_xyz123`
5. [ ] Ir a: `http://localhost:8000/auth/login`
6. [ ] **VERIFICAR**: Deberías ver un mensaje amarillo: "Tu sesión ha expirado"
7. [ ] **VERIFICAR**: Las cookies deberían ser eliminadas automáticamente
8. [ ] Revisar DevTools > Application > Cookies
9. [ ] **VERIFICAR**: Las cookies `access_token`, `user_id`, etc. deberían estar vacías o eliminadas

**Resultado esperado**: ✅ Mensaje mostrado, cookies limpiadas

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

### 📋 Escenario 4: Verificar NO Loop (Crítico)

**Objetivo**: Confirmar que NO hay loop de redirección infinito

1. [ ] Cerrar **todas** las pestañas del navegador
2. [ ] Abrir una **nueva pestaña** (puede ser normal, no incógnito)
3. [ ] Ir a: `http://localhost:8000/admin`
4. [ ] Ingresar credenciales y hacer login
5. [ ] **VERIFICAR**: Deberías llegar a `/admin` en **un solo intento**
6. [ ] **VERIFICAR**: La URL debería ser: `http://localhost:8000/admin`
7. [ ] **VERIFICAR**: NO deberías ver el formulario de login nuevamente
8. [ ] **VERIFICAR**: NO deberías ser redirigido de vuelta a `/auth/login`

**Resultado esperado**: ✅ Acceso directo a /admin, sin loop

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

### 📋 Escenario 5: Logout y Re-Login

**Objetivo**: Verificar que el ciclo completo funciona

1. [ ] Con sesión activa, ir a: `http://localhost:8000/logout`
2. [ ] **VERIFICAR**: Deberías ser redirigido a `/auth/login`
3. [ ] **VERIFICAR**: Las cookies deberían estar eliminadas
4. [ ] Intentar acceder a: `http://localhost:8000/admin`
5. [ ] **VERIFICAR**: Deberías ser redirigido a login
6. [ ] Hacer login nuevamente
7. [ ] **VERIFICAR**: Deberías acceder a `/admin` sin problemas

**Resultado esperado**: ✅ Logout funciona, re-login funciona

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

### 📋 Escenario 6: Múltiples Pestañas

**Objetivo**: Verificar comportamiento con múltiples pestañas

1. [ ] Hacer login en una pestaña
2. [ ] Abrir una **nueva pestaña** (misma ventana)
3. [ ] Ir a: `http://localhost:8000/admin`
4. [ ] **VERIFICAR**: Deberías acceder directamente (sin pedir login)
5. [ ] En la **primera pestaña**, ir a: `http://localhost:8000/auth/login`
6. [ ] **VERIFICAR**: Deberías ser redirigido automáticamente

**Resultado esperado**: ✅ Sesión compartida entre pestañas

**Si falla**: ❌ Anota qué pasó: ___________________________________

---

## 🔍 Verificaciones Adicionales

### Cookies (DevTools > Application > Cookies)

Después de un login exitoso, deberías ver:

- [ ] `access_token` - Valor largo (JWT token)
- [ ] `user_id` - ID del usuario
- [ ] `user_name` - Nombre de usuario
- [ ] `user_role` - Rol del usuario (admin, operador, usuario)

### Consola del Navegador (DevTools > Console)

No deberías ver:

- [ ] Errores en rojo
- [ ] Warnings sobre cookies
- [ ] Errores de JavaScript

### Network (DevTools > Network)

Al hacer login, deberías ver:

- [ ] POST a `/api/auth/login` - Status 200
- [ ] GET a `/admin` - Status 200 (no 302)

---

## 📊 Resumen de Resultados

### Escenarios Completados

- [ ] Escenario 1: Login Normal
- [ ] Escenario 2: Auto-Redirect
- [ ] Escenario 3: Token Expirado
- [ ] Escenario 4: NO Loop (CRÍTICO)
- [ ] Escenario 5: Logout y Re-Login
- [ ] Escenario 6: Múltiples Pestañas

### Resultado Final

**Total de escenarios**: 6
**Escenarios exitosos**: _____ / 6
**Escenarios fallidos**: _____ / 6

---

## ✅ Conclusión

Si **todos** los escenarios pasaron:
- ✅ El fix está funcionando correctamente
- ✅ El problema del loop de redirección está resuelto
- ✅ El sistema está listo para producción

Si **algún** escenario falló:
- ❌ Revisa los logs del servidor: `docker-compose logs -f app`
- ❌ Revisa la consola del navegador (F12 > Console)
- ❌ Consulta: `DOCS/fixes/INSTRUCCIONES_TEST_FIX.md`

---

## 📝 Notas Adicionales

Anota cualquier comportamiento inesperado:

```
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
```

---

**Fecha de prueba**: ___________________
**Probado por**: ___________________
**Navegador**: ___________________
**Resultado general**: ⬜ ÉXITO  ⬜ FALLO
