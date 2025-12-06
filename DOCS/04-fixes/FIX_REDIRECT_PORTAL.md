# 🔧 Fix: Redirección a Login en Portal de Clientes

**Problema:** Al acceder a `https://staging.jemavi.co/customer-portal` redirige a `/auth/login`  
**Causa:** El servidor no se reinició después del deploy o hay caché

---

## ✅ Solución Rápida

### En el servidor staging:

```bash
# 1. Verificar configuración de rutas
docker-compose exec web python debug_routes.py

# 2. Reiniciar el servidor
docker-compose restart web

# 3. Verificar que esté corriendo
docker-compose ps

# 4. Probar el portal
curl -I https://staging.jemavi.co/customer-portal
```

O usar el script automatizado:

```bash
bash scripts/restart_staging.sh
```

---

## 🔍 Diagnóstico Detallado

### Verificar que las rutas estén configuradas:

```bash
docker-compose exec web python debug_routes.py
```

Debería mostrar:
```
✅ PÚBLICA - /customer-portal
✅ PÚBLICA - /customer-portal/verify
✅ PÚBLICA - /customer-portal/dashboard
✅ PÚBLICA - /api/customer-portal/request-otp
✅ PÚBLICA - /api/customer-portal/verify-otp
```

### Verificar logs del middleware:

```bash
docker-compose logs -f web | grep -i "customer-portal\|auth_middleware"
```

Buscar líneas como:
- `Redirigiendo a login desde: /customer-portal` ❌ (problema)
- Sin logs de redirección ✅ (correcto)

---

## 🐛 Posibles Causas

### 1. Servidor no reiniciado después del deploy
**Solución:**
```bash
docker-compose restart web
```

### 2. Código antiguo en caché de Python
**Solución:**
```bash
docker-compose down
docker-compose up -d --build
```

### 3. Caché del navegador
**Solución:**
- Abrir en ventana privada/incógnito
- O limpiar caché del navegador (Ctrl+Shift+Del)

### 4. Nginx caché (si aplica)
**Solución:**
```bash
docker-compose exec nginx nginx -s reload
```

---

## 🧪 Pruebas

### 1. Probar con curl (sin caché del navegador):

```bash
# Debe retornar 200 y HTML
curl -I https://staging.jemavi.co/customer-portal

# Debe retornar 200 y JSON
curl https://staging.jemavi.co/api/customer-portal/request-otp \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"phone": "+573334004007"}'
```

### 2. Probar en navegador:

```
https://staging.jemavi.co/customer-portal
```

Debería mostrar el formulario del portal, NO redirigir a login.

### 3. Verificar rutas en Swagger:

```
https://staging.jemavi.co/docs
```

Buscar la sección "Portal de Clientes" y probar los endpoints.

---

## 📋 Checklist

- [ ] Código actualizado en staging (git pull)
- [ ] Script de diagnóstico ejecutado
- [ ] Servidor reiniciado
- [ ] Rutas verificadas como públicas
- [ ] Prueba con curl exitosa
- [ ] Prueba en navegador exitosa
- [ ] Caché del navegador limpiado

---

## 🔧 Si el Problema Persiste

### Verificar que el archivo config_routes.py esté actualizado:

```bash
docker-compose exec web cat src/app/config_routes.py | grep -A 5 "customer-portal"
```

Debe mostrar:
```python
# Portal de Clientes (público con OTP)
"/customer-portal",
"/customer-portal/verify",
"/customer-portal/dashboard",
```

### Verificar que el middleware esté usando la configuración correcta:

```bash
docker-compose exec web python -c "
from app.config_routes import is_public_route
print('¿/customer-portal es pública?', is_public_route('/customer-portal'))
"
```

Debe mostrar: `True`

### Rebuild completo (último recurso):

```bash
docker-compose down -v
docker-compose up -d --build
docker-compose exec web alembic upgrade head
```

---

## 📝 Archivos Involucrados

- `CODE/src/app/config_routes.py` - Configuración de rutas públicas
- `CODE/src/app/middleware/auth_middleware.py` - Middleware de autenticación
- `CODE/debug_routes.py` - Script de diagnóstico
- `scripts/restart_staging.sh` - Script de reinicio

---

**Siguiente paso:** Ejecutar en staging:
```bash
bash scripts/restart_staging.sh
```

Luego probar: `https://staging.jemavi.co/customer-portal`
