# 🔍 Diagnóstico: Productos no visibles en Staging

**Fecha:** 2026-02-09  
**Servidor:** https://staging.jemavi.co  
**Estado:** ✅ Servidor funcionando, ⚠️ Productos requieren autenticación

---

## 📊 Estado Actual

### ✅ Servidor
```json
{
  "status": "healthy",
  "timestamp": "2026-02-09T20:57:19.648371",
  "version": "4.0.0-staging",
  "environment": "staging"
}
```

### ✅ Base de Datos
```
Total productos en BD: 88
Ejemplo: BANDERITAS ADH 5X20H /12X45MM MARFIL - 7706616340433
```

### ✅ Archivos Desplegados
- ✅ `invoices_v2_routes.py` - Rutas API
- ✅ `productos.html` - Template
- ✅ `productos-loader.js` - JavaScript (copiado)

---

## ❌ Problema Identificado

### 1. Autenticación Requerida

Cuando intentas acceder a `/api/v2/invoices/productos` sin estar autenticado:

```json
{
  "detail": "No autenticado",
  "redirect_url": "/auth/login",
  "original_url": "/api/v2/invoices/productos",
  "requires_auth": true
}
```

**Logs del servidor:**
```
2026-02-09 15:53:15,093 - src.app.middleware.auth_middleware - INFO - API no autenticada: /api/invoices/1/productos
INFO: 172.18.0.1:40814 - "GET /api/invoices/1/productos HTTP/1.1" 401 Unauthorized
```

---

## 🔧 Soluciones

### Opción 1: Acceder Autenticado (Recomendado)

1. **Accede a staging:**
   ```
   https://staging.jemavi.co/auth/login
   ```

2. **Inicia sesión con tus credenciales**

3. **Navega a Facturas V2:**
   ```
   https://staging.jemavi.co/invoices/v2/productos
   ```

4. **Verifica que los productos se carguen correctamente**

### Opción 2: Verificar Endpoint Directamente (Para Testing)

Si quieres probar el endpoint sin autenticación, necesitas modificar temporalmente la ruta para que no requiera auth.

**Archivo:** `CODE/src/app/routes/invoices_v2_routes.py`

Busca la línea:
```python
@router.get("/productos")
def list_products(
```

Y verifica que NO tenga el decorador de autenticación. Si lo tiene, coméntalo temporalmente:

```python
# @require_auth  # ← Comentar esta línea para testing
@router.get("/productos")
def list_products(
```

---

## 🧪 Pruebas de Verificación

### 1. Verificar que el endpoint existe

```bash
# Desde el servidor staging
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml exec -T app python -c \"
from src.app.routes.invoices_v2_routes import router
print('Rutas disponibles:')
for route in router.routes:
    print(f'  {route.methods} {route.path}')
\" | grep productos"
```

### 2. Verificar productos en BD

```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml exec -T app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2

db = SessionLocal()
count = db.query(InvoiceProductV2).count()
print(f'Total productos: {count}')

# Mostrar primeros 5
productos = db.query(InvoiceProductV2).limit(5).all()
for p in productos:
    print(f'  - {p.codigo_producto}: {p.descripcion}')
db.close()
\""
```

### 3. Verificar template

```bash
# Verificar que el template existe
ssh ubuntu@staging "ls -lh /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/productos.html"

# Verificar que llama a la URL correcta
ssh ubuntu@staging "grep -n '/api/v2/invoices/productos' /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/productos.html"
```

---

## 📝 Configuración Actual

### Router Prefix
```python
router = APIRouter(prefix="/api/v2/invoices", tags=["Invoices V2"])
```

### Endpoint de Productos
```
GET /api/v2/invoices/productos
```

### Template URL
```javascript
const url = `/api/v2/invoices/productos?${params}`;
```

✅ **Las URLs coinciden correctamente**

---

## 🎯 Pasos para Verificar Funcionamiento

### 1. Acceder a Staging
```
https://staging.jemavi.co
```

### 2. Iniciar Sesión
- Usuario: [tu usuario]
- Contraseña: [tu contraseña]

### 3. Navegar a Productos
```
https://staging.jemavi.co/invoices/v2/productos
```

### 4. Verificar en Consola del Navegador

Abre las DevTools (F12) y verifica:

**Console:**
```
🌐 Haciendo petición a: /api/v2/invoices/productos?search=&skip=0&limit=25
📡 Respuesta recibida: 200 OK
📄 Content-Type: application/json
✅ Datos recibidos: [...]
```

**Network:**
- Busca la petición a `/api/v2/invoices/productos`
- Verifica que el status sea `200 OK`
- Verifica que la respuesta contenga un array de productos

---

## 🐛 Debugging Adicional

### Ver logs en tiempo real

```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml logs -f app" | grep -i "productos\|error"
```

### Verificar rutas registradas

```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml exec -T app python -c \"
from src.main import app
print('Rutas registradas:')
for route in app.routes:
    if hasattr(route, 'path') and 'productos' in route.path:
        print(f'  {route.methods if hasattr(route, \\\"methods\\\") else \\\"N/A\\\"} {route.path}')
\""
```

### Test directo del servicio

```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml exec -T app python -c \"
from src.app.database import SessionLocal
from src.app.services.invoice_v2_service import InvoiceV2Service

db = SessionLocal()
service = InvoiceV2Service(db)

# Listar productos
productos = service.list_products(skip=0, limit=5)
print(f'Productos encontrados: {len(productos)}')
for p in productos:
    print(f'  - {p.codigo_producto}: {p.descripcion[:50]}')

db.close()
\""
```

---

## ✅ Checklist de Verificación

- [x] Servidor staging funcionando
- [x] Health check pasando
- [x] Base de datos con 88 productos
- [x] Archivos desplegados correctamente
- [x] Router configurado con prefix correcto
- [x] Template con URL correcta
- [ ] **Usuario autenticado en staging**
- [ ] **Productos visibles en la interfaz**

---

## 🎯 Próximo Paso

**ACCIÓN REQUERIDA:**

1. Accede a https://staging.jemavi.co/auth/login
2. Inicia sesión
3. Navega a https://staging.jemavi.co/invoices/v2/productos
4. Verifica que los 88 productos se muestren correctamente

Si después de autenticarte sigues sin ver productos, revisa la consola del navegador (F12) para ver los errores específicos.

---

## 📞 Información de Contacto

**Servidor:** staging.jemavi.co  
**Puerto:** 8001 (interno), 443 (HTTPS externo)  
**Base de Datos:** paqueteria_staging (AWS RDS)  
**Productos en BD:** 88  
**Estado:** 🟢 HEALTHY
