# 🔧 Solución: Productos no visibles en Staging

**Fecha:** 2026-02-09  
**Problema:** No se visualizan productos en staging  
**Causa:** Endpoint requiere autenticación  
**Estado BD:** ✅ 88 productos disponibles (no 90)

---

## 🔍 Diagnóstico Completo

### ✅ Verificaciones Realizadas

1. **Servidor Staging:** ✅ Funcionando
   ```json
   {
     "status": "healthy",
     "version": "4.0.0-staging",
     "environment": "staging"
   }
   ```

2. **Base de Datos:** ✅ 88 productos
   ```
   Total productos en BD: 88
   Ejemplos:
   - 7706616340433: BANDERITAS ADH 5X20H /12X45MM MARFIL
   - 781312: VELITA NUMERO METALIZ ADO PEQ UNID
   - 771924: VELA VOLCAN 15-12CM GRANDE UNID
   ```

3. **Servicio Backend:** ✅ Funciona correctamente
   ```python
   service.list_products(skip=0, limit=10)
   # Retorna 10 productos correctamente
   ```

4. **Endpoint API:** ❌ Requiere autenticación
   ```
   GET /api/v2/invoices/productos
   Status: 401 Unauthorized
   Response: {"detail":"No autenticado","requires_auth":true}
   ```

5. **Archivos Desplegados:** ✅ Todos presentes
   - invoices_v2_routes.py
   - productos.html
   - productos-loader.js

---

## ❌ Problema Identificado

### El endpoint está protegido por autenticación

**Middleware de autenticación** (`auth_middleware.py`) bloquea TODAS las rutas `/api/` que no estén en la lista de rutas públicas.

**Código del middleware:**
```python
# Si la ruta empieza con /api/ y NO está en API_PUBLIC_ROUTES
if path.startswith("/api/"):
    return self._return_401_json(request, path)
```

**Ruta de productos:**
```
/api/v2/invoices/productos
```

**Estado:** NO está en `API_PUBLIC_ROUTES` → Requiere autenticación

---

## 🎯 Soluciones

### Opción 1: Autenticarse en el Navegador (RECOMENDADO)

Este es el comportamiento correcto y esperado. Los productos deben estar protegidos.

**Pasos:**

1. **Accede a staging:**
   ```
   https://staging.jemavi.co/auth/login
   ```

2. **Inicia sesión** con tus credenciales

3. **Navega a productos:**
   ```
   https://staging.jemavi.co/invoices/v2/productos
   ```

4. **Verifica en DevTools (F12):**
   - Tab **Console:** Busca logs de carga
   - Tab **Network:** Busca petición a `/api/v2/invoices/productos`
   - Debe retornar `200 OK` con array de productos

---

### Opción 2: Hacer el Endpoint Público (NO RECOMENDADO)

Solo para testing temporal. NO usar en producción.

**Archivo:** `CODE/src/app/config_routes.py`

**Agregar:**
```python
API_PUBLIC_ROUTES: Set[str] = {
    # ... rutas existentes ...
    
    # Facturas V2 - Productos (TEMPORAL PARA TESTING)
    "/api/v2/invoices/productos",
}
```

**Desplegar:**
```bash
# Copiar archivo modificado
scp CODE/src/app/config_routes.py ubuntu@staging:/home/ubuntu/paqueteria-staging/CODE/src/app/

# Reiniciar contenedor
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml restart app"
```

⚠️ **IMPORTANTE:** Esto expone los productos sin autenticación. Revertir después de testing.

---

## 🧪 Pruebas de Verificación

### Test 1: Verificar Autenticación

```bash
# Sin autenticación (debe fallar)
curl -s https://staging.jemavi.co/api/v2/invoices/productos | jq .

# Respuesta esperada:
# {
#   "detail": "No autenticado",
#   "requires_auth": true
# }
```

### Test 2: Verificar con Sesión

1. Abre el navegador
2. Accede a https://staging.jemavi.co/auth/login
3. Inicia sesión
4. Abre DevTools (F12) → Console
5. Ejecuta:
   ```javascript
   fetch('/api/v2/invoices/productos?skip=0&limit=5', {
       credentials: 'include'
   })
   .then(r => r.json())
   .then(data => console.log('Productos:', data))
   ```

**Resultado esperado:** Array con 5 productos

### Test 3: Verificar Template

```bash
# Verificar que el template llama a la URL correcta
ssh ubuntu@staging "grep -n '/api/v2/invoices/productos' /home/ubuntu/paqueteria-staging/CODE/src/templates/invoices_v2/productos.html"
```

**Resultado esperado:** Línea con `const url = \`/api/v2/invoices/productos?${params}\`;`

---

## 📊 Datos Actuales

### Productos en Base de Datos

```
Total: 88 productos (no 90 como esperabas)
```

**Posibles razones de la diferencia:**
- 2 productos fueron eliminados
- 2 productos no se importaron correctamente
- Conteo inicial era incorrecto

**Verificar:**
```bash
ssh ubuntu@staging "docker compose -f /home/ubuntu/paqueteria-staging/docker-compose.staging.yml exec -T app python -c \"
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceProductV2

db = SessionLocal()
count = db.query(InvoiceProductV2).count()
print(f'Total productos: {count}')
db.close()
\""
```

---

## 🐛 Debugging en el Navegador

### 1. Verificar Autenticación

**Console:**
```javascript
// Verificar cookies
document.cookie

// Debe contener: access_token=...
```

### 2. Verificar Petición

**Network Tab:**
1. Filtra por `productos`
2. Busca petición a `/api/v2/invoices/productos`
3. Verifica:
   - **Status:** Debe ser `200 OK` (no `401`)
   - **Response:** Debe ser array de objetos
   - **Headers → Request → Cookie:** Debe incluir `access_token`

### 3. Verificar Respuesta

**Console:**
```javascript
// Ver datos cargados
console.log('Productos cargados:', window.productosData);
```

---

## 📝 Checklist de Verificación

- [x] Servidor staging funcionando
- [x] Health check pasando
- [x] Base de datos con 88 productos
- [x] Servicio backend funciona
- [x] Endpoint API configurado correctamente
- [x] Template con URL correcta
- [x] Archivos desplegados
- [ ] **Usuario autenticado en navegador**
- [ ] **Cookies de sesión presentes**
- [ ] **Petición retorna 200 OK**
- [ ] **Productos visibles en interfaz**

---

## 🎯 Acción Requerida

### PASO A PASO:

1. **Abre navegador en modo incógnito** (para limpiar cookies)

2. **Accede a:**
   ```
   https://staging.jemavi.co/auth/login
   ```

3. **Inicia sesión** con tus credenciales

4. **Abre DevTools** (F12)

5. **Navega a:**
   ```
   https://staging.jemavi.co/invoices/v2/productos
   ```

6. **En Console, busca:**
   ```
   🌐 Haciendo petición a: /api/v2/invoices/productos?...
   📡 Respuesta recibida: 200 OK
   ✅ Datos recibidos: [...]
   ```

7. **Si ves 401 Unauthorized:**
   - Verifica que iniciaste sesión correctamente
   - Verifica que las cookies están presentes
   - Intenta cerrar sesión y volver a iniciar

8. **Si ves 200 OK pero no se muestran productos:**
   - Revisa errores en Console
   - Verifica que el array de productos no esté vacío
   - Verifica que el template esté renderizando correctamente

---

## 📞 Información Adicional

**Servidor:** https://staging.jemavi.co  
**Endpoint:** /api/v2/invoices/productos  
**Método:** GET  
**Autenticación:** Requerida (Cookie: access_token)  
**Productos en BD:** 88  
**Estado:** 🟢 HEALTHY

---

## 🔄 Si el Problema Persiste

Si después de autenticarte correctamente sigues sin ver productos:

1. **Captura de pantalla de:**
   - DevTools → Console (todos los logs)
   - DevTools → Network → Petición a `/api/v2/invoices/productos`
   - La interfaz mostrando el problema

2. **Ejecuta en Console:**
   ```javascript
   // Verificar autenticación
   console.log('Cookies:', document.cookie);
   
   // Hacer petición manual
   fetch('/api/v2/invoices/productos?skip=0&limit=5', {
       credentials: 'include'
   })
   .then(r => {
       console.log('Status:', r.status);
       return r.json();
   })
   .then(data => console.log('Data:', data))
   .catch(err => console.error('Error:', err));
   ```

3. **Comparte los resultados** para análisis adicional

---

## ✅ Resumen

**Problema:** Endpoint requiere autenticación  
**Solución:** Iniciar sesión en el navegador  
**Productos disponibles:** 88 (no 90)  
**Estado del servidor:** ✅ Funcionando correctamente  

El sistema está funcionando como debe. Solo necesitas autenticarte para ver los productos.
