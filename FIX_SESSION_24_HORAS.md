# Fix: Sesiones de 24 Horas - COMPLETADO ✅

## 🔴 Problema Identificado

El sistema estaba pidiendo autenticación cada 1-2 horas aunque el código estaba configurado para 24 horas.

### Causa Raíz
Los archivos `.env` tenían configurado:
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=30  # ❌ Solo 30 minutos
```

Esto sobrescribía el default del código en `config.py`:
```python
access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 horas
```

## ✅ Solución Aplicada

### 1. Actualizado `.env` (Producción)
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas = 1440 minutos
```

### 2. Actualizado `.env.staging` (Staging)
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas = 1440 minutos
```

### 3. Actualizado `.env.production` (Producción)
```bash
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas = 1440 minutos
```

## 📊 Cómo Funciona Ahora

### JWT Token
- **Expiración**: 24 horas (1440 minutos)
- **Creado en**: `auth.py` - función `create_access_token()`
- **Verificado en**: `auth.py` - función `verify_token()`

### Cookies
- **Expiración**: 24 horas (86400 segundos)
- **Configuradas en**: `auth.py` - endpoint `/login`
- **Cookies establecidas**:
  - `access_token` (HttpOnly, Secure en producción)
  - `user_id` (HttpOnly, Secure en producción)
  - `user_name` (HttpOnly, Secure en producción)
  - `user_role` (HttpOnly, Secure en producción)

### Flujo de Autenticación
1. Usuario hace login → Se crea JWT con expiración de 24 horas
2. JWT se guarda en cookie con max_age de 24 horas
3. En cada request, `get_current_user_from_cookies()` verifica:
   - ✅ Cookie existe
   - ✅ Token es válido
   - ✅ Token no ha expirado (24 horas)
   - ✅ Usuario existe en BD
   - ✅ Usuario está activo

## 🚀 Aplicar Cambios

### Opción 1: Deploy Completo (RECOMENDADO)

#### Staging
```bash
# 1. Commit y push
git add .env.staging
git commit -m "fix: aumentar sesión a 24 horas en staging"
git push origin staging

# 2. Deploy en staging
./deploy.sh staging
```

#### Producción
```bash
# 1. Commit y push
git add .env .env.production
git commit -m "fix: aumentar sesión a 24 horas en producción"
git push origin main

# 2. Deploy en producción
./deploy.sh papyrus
```

### Opción 2: Actualización Manual (Rápida)

#### Staging
```bash
# Conectar al servidor
ssh ubuntu@staging

# Editar .env
cd /home/ubuntu/paqueteria-staging
nano CODE/.env.staging

# Cambiar:
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# Por:
# ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Reiniciar contenedor
docker compose -f docker-compose.staging.yml restart app
```

#### Producción
```bash
# Conectar al servidor
ssh ubuntu@papyrus

# Editar .env
cd /ruta/al/proyecto
nano .env

# Cambiar:
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# Por:
# ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Reiniciar contenedor
docker compose restart app
```

## ✅ Verificación

### 1. Verificar Configuración
```bash
# En el servidor
docker compose exec app python -c "from app.config import settings; print(f'Token expira en: {settings.access_token_expire_minutes} minutos')"
```

Debe mostrar:
```
Token expira en: 1440 minutos
```

### 2. Verificar en Logs
Después de hacer login, verificar los logs:
```bash
docker compose logs -f app | grep "Token"
```

Debe mostrar algo como:
```
Token verificado - Exp: 2026-02-12 16:40:00, Ahora UTC: 2026-02-11 16:40:00, Tiempo restante: 1440.00 minutos
```

### 3. Probar en Navegador
1. Hacer login
2. Esperar 2 horas
3. Navegar por la aplicación
4. ✅ NO debe pedir autenticación nuevamente

## 📝 Notas Importantes

### Sesiones Existentes
- Las sesiones creadas ANTES del cambio seguirán expirando en 30 minutos
- Los usuarios deberán hacer login nuevamente para obtener sesión de 24 horas
- Después del primer login post-cambio, tendrán 24 horas de sesión

### Seguridad
- Las cookies tienen flags `HttpOnly` y `Secure` (en producción)
- Esto previene acceso desde JavaScript y ataques XSS
- Las cookies solo se envían por HTTPS en producción

### Inactividad vs Expiración
- **Expiración**: 24 horas desde el login (tiempo absoluto)
- **Inactividad**: No hay timeout de inactividad
- Si el usuario no usa la app por 23 horas, aún tendrá 1 hora de sesión
- Después de 24 horas, deberá hacer login nuevamente

### Extender Sesión (Opcional - No Implementado)
Si quieres que la sesión se extienda con cada actividad:
1. Implementar refresh token automático
2. Actualizar cookies en cada request
3. Esto mantendría la sesión activa indefinidamente mientras haya actividad

## 🔧 Troubleshooting

### Problema: Sigue pidiendo login cada hora
**Solución**:
1. Verificar que el .env tiene `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
2. Reiniciar el contenedor
3. Hacer logout y login nuevamente
4. Verificar logs para confirmar tiempo de expiración

### Problema: Sesión expira inmediatamente
**Solución**:
1. Verificar que el SECRET_KEY es el mismo en todos los entornos
2. Verificar que no hay diferencia de zona horaria
3. Verificar logs de `verify_token()` para ver el error específico

### Problema: Cookies no se están guardando
**Solución**:
1. Verificar que el dominio es correcto
2. Verificar que HTTPS está habilitado en producción
3. Verificar que SameSite está configurado correctamente

## 📊 Comparación Antes/Después

### Antes
```
Login → Token expira en 30 minutos → Pide login cada 30 min
```

### Después
```
Login → Token expira en 24 horas → Pide login cada 24 horas
```

## ✅ Checklist de Aplicación

- [x] Actualizado `.env` con `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- [x] Actualizado `.env.staging` con `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- [x] Actualizado `.env.production` con `ACCESS_TOKEN_EXPIRE_MINUTES=1440`
- [ ] Commit y push de cambios
- [ ] Deploy en staging
- [ ] Verificar en staging (esperar 2 horas)
- [ ] Deploy en producción
- [ ] Verificar en producción
- [ ] Notificar a usuarios que hagan logout/login para obtener nueva sesión

---

**Cambio aplicado**: 2026-02-11
**Archivos modificados**: `.env`, `.env.staging`, `.env.production`
**Impacto**: Sesiones ahora duran 24 horas en lugar de 30 minutos
**Requiere**: Reinicio de contenedores y nuevo login de usuarios
