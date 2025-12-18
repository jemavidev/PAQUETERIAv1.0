# 🧪 Guía de Pruebas de Cache con Autenticación

**Fecha:** 2024-12-18  
**Propósito:** Probar el cache en endpoints que requieren autenticación

---

## 🎯 OPCIONES DISPONIBLES

Tienes 3 formas de probar el cache con autenticación:

### **Opción 1: Script Bash con Cookies (Recomendado)** ⭐

El más simple y directo.

```bash
./test_cache_with_cookies.sh https://staging.jemavi.co admin TU_PASSWORD
```

**Ventajas:**
- ✅ Simple y rápido
- ✅ No requiere Python
- ✅ Usa el mismo sistema de auth que el navegador (cookies)
- ✅ Muestra mejoras de rendimiento automáticamente

---

### **Opción 2: Script Python con Token**

Más flexible y detallado.

```bash
# Opción A: Editar el archivo y cambiar credenciales
nano test_cache_with_auth.py
# Cambiar USERNAME y PASSWORD
python3 test_cache_with_auth.py

# Opción B: Variables de entorno
export TEST_USERNAME='admin'
export TEST_PASSWORD='tu_password'
python3 test_cache_with_auth.py

# Opción C: Argumentos
python3 test_cache_with_auth.py admin tu_password
```

**Ventajas:**
- ✅ Más detallado
- ✅ Fácil de extender
- ✅ Mejor manejo de errores

---

### **Opción 3: Manual con curl**

Para pruebas específicas.

```bash
# 1. Login y guardar cookies
curl -c /tmp/cookies.txt -X POST https://staging.jemavi.co/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu_password"}'

# 2. Probar endpoint (primera vez - cache miss)
time curl -b /tmp/cookies.txt https://staging.jemavi.co/api/packages?limit=10

# 3. Probar endpoint (segunda vez - cache hit)
time curl -b /tmp/cookies.txt https://staging.jemavi.co/api/packages?limit=10

# 4. Limpiar
rm /tmp/cookies.txt
```

---

## 📊 ENDPOINTS A PROBAR

### 1. **Búsqueda de Paquetes**
```
GET /api/packages?limit=10
```
- Cache: 60 segundos
- Mejora esperada: >80%

### 2. **Estadísticas de Dashboard**
```
GET /api/admin/dashboard
```
- Cache: 5 minutos
- Mejora esperada: >90%

### 3. **Lista de Clientes**
```
GET /api/admin/customers?limit=10
```
- Cache: 2 minutos
- Mejora esperada: >80%

### 4. **Lista de Usuarios**
```
GET /api/admin/users?limit=10
```
- Cache: 2 minutos
- Mejora esperada: >80%

---

## 🔐 OBTENER CREDENCIALES

### Para Staging

**Opción 1: Crear usuario de prueba**
```bash
ssh staging "docker exec paqueteria_staging_app python -c '
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash

db = SessionLocal()

# Crear usuario de prueba
test_user = User(
    username=\"test_cache\",
    email=\"test@cache.com\",
    full_name=\"Test Cache User\",
    password_hash=get_password_hash(\"TestCache123!\"),
    role=UserRole.ADMIN,
    is_active=True
)

db.add(test_user)
db.commit()
print(\"✅ Usuario creado: test_cache / TestCache123!\")
'"
```

**Opción 2: Usar usuario existente**
- Pregunta al administrador del sistema
- O usa tus credenciales de admin

---

## 📈 INTERPRETAR RESULTADOS

### Resultado Esperado

```
Primera llamada (CACHE MISS): 0.250s (Status: 200)
Segunda llamada (CACHE HIT):  0.015s (Status: 200)
🚀 Mejora: 94.0%
   ✅ EXCELENTE: Cache funcionando óptimamente
```

### Evaluación

| Mejora | Estado | Acción |
|--------|--------|--------|
| **>80%** | ✅ Excelente | Cache funcionando óptimamente |
| **50-80%** | ✅ Bueno | Cache funcionando bien |
| **20-50%** | ⚠️ Aceptable | Revisar configuración |
| **<20%** | ❌ Problema | Verificar Redis y logs |

---

## 🐛 TROUBLESHOOTING

### Problema: "Login fallido (401)"

**Causa:** Credenciales incorrectas

**Solución:**
```bash
# Verificar usuario existe
ssh staging "docker exec paqueteria_staging_app python -c '
from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()
user = db.query(User).filter(User.username == \"admin\").first()
if user:
    print(f\"✅ Usuario existe: {user.username} ({user.role.value})\")
else:
    print(\"❌ Usuario no encontrado\")
'"
```

### Problema: "No hay mejora de rendimiento"

**Causa:** Cache no está funcionando

**Solución:**
```bash
# 1. Verificar Redis
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
print(\"Redis:\", cache_manager.redis_client.ping())
'"

# 2. Ver logs de cache
ssh staging "docker logs --tail 50 paqueteria_staging_app | grep -i cache"

# 3. Verificar estadísticas
ssh staging "docker exec paqueteria_staging_app python -c '
from app.cache_manager import cache_manager
import json
print(json.dumps(cache_manager.get_cache_stats(), indent=2))
'"
```

### Problema: "Status 401 en segunda llamada"

**Causa:** Token/cookie expiró

**Solución:**
- Reducir tiempo entre llamadas
- Verificar TTL del token
- Hacer login nuevamente

---

## 📝 EJEMPLOS COMPLETOS

### Ejemplo 1: Test rápido en staging

```bash
# Crear usuario de prueba
ssh staging "docker exec paqueteria_staging_app python -c '
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == \"test_cache\").first()
if not user:
    user = User(
        username=\"test_cache\",
        email=\"test@cache.com\",
        full_name=\"Test Cache\",
        password_hash=get_password_hash(\"TestCache123!\"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    print(\"✅ Usuario creado\")
else:
    print(\"✅ Usuario ya existe\")
'"

# Ejecutar test
./test_cache_with_cookies.sh https://staging.jemavi.co test_cache TestCache123!
```

### Ejemplo 2: Test con usuario existente

```bash
# Usar tu usuario admin
./test_cache_with_cookies.sh https://staging.jemavi.co admin tu_password_real
```

### Ejemplo 3: Test manual detallado

```bash
# 1. Login
curl -c /tmp/cookies.txt -X POST https://staging.jemavi.co/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu_password"}' | python3 -m json.tool

# 2. Test de paquetes
echo "=== Primera llamada ==="
time curl -b /tmp/cookies.txt https://staging.jemavi.co/api/packages?limit=10 | python3 -m json.tool

sleep 1

echo "=== Segunda llamada ==="
time curl -b /tmp/cookies.txt https://staging.jemavi.co/api/packages?limit=10 | python3 -m json.tool

# 3. Limpiar
rm /tmp/cookies.txt
```

---

## ✅ CHECKLIST DE PRUEBAS

Antes de considerar el cache como exitoso:

- [ ] Login funciona correctamente
- [ ] Primera llamada retorna datos (200)
- [ ] Segunda llamada retorna datos (200)
- [ ] Segunda llamada es >80% más rápida
- [ ] Cache hit rate en Redis aumenta
- [ ] No hay errores en logs
- [ ] Funciona en todos los endpoints probados

---

## 📞 SOPORTE

Si tienes problemas:

1. Verificar que Redis está corriendo
2. Verificar logs de la aplicación
3. Verificar credenciales
4. Consultar `REPORTE_ANALISIS_STAGING.md`

---

**Última actualización:** 2024-12-18  
**Versión:** 1.0.0
