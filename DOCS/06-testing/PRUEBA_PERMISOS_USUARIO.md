# 🔐 Guía de Prueba: Permisos del Rol USUARIO

## 📋 Resumen de Permisos para USUARIO

Según la matriz de permisos del sistema, el rol **USUARIO** tiene los siguientes permisos:

### ✅ Permisos Permitidos

| Funcionalidad | Acceso | Descripción |
|---------------|--------|-------------|
| **Ver perfil propio** | ✅ | Puede ver su propia información de perfil |
| **Editar perfil propio** | ✅ | Puede modificar sus datos personales |
| **Cambiar contraseña propia** | ✅ | Puede actualizar su contraseña |
| **Ver paquetes** | ✅ | Puede consultar la lista de paquetes |
| **Ver clientes** | ✅ | Puede consultar la lista de clientes |
| **Ver estadísticas** | ✅ | Puede ver estadísticas del sistema |

### ❌ Permisos Denegados

| Funcionalidad | Acceso | Descripción |
|---------------|--------|-------------|
| **Crear paquetes** | ❌ | No puede crear nuevos paquetes |
| **Editar paquetes** | ❌ | No puede modificar paquetes existentes |
| **Crear clientes** | ❌ | No puede agregar nuevos clientes |
| **Editar clientes** | ❌ | No puede modificar datos de clientes |
| **Ver usuarios** | ❌ | No puede ver la lista de usuarios del sistema |
| **Crear usuarios** | ❌ | No puede crear nuevos usuarios |
| **Editar usuarios** | ❌ | No puede modificar otros usuarios |
| **Eliminar usuarios** | ❌ | No puede eliminar usuarios |
| **Restablecer contraseñas** | ❌ | No puede restablecer contraseñas de otros |
| **Acceder a admin** | ❌ | No puede acceder al panel de administración |

---

## 🔍 Ver Clientes - ¿Qué puede ver un USUARIO?

### Acceso Permitido

Un usuario con rol **USUARIO** puede:

1. **Ver la lista de clientes** - Acceso a `/customers` o la vista de clientes
2. **Buscar clientes** - Usar filtros y búsqueda
3. **Ver detalles de un cliente** - Información completa del cliente
4. **Ver paquetes asociados a un cliente** - Historial de paquetes del cliente

### Restricciones

Un usuario con rol **USUARIO** NO puede:

1. ❌ Crear nuevos clientes
2. ❌ Editar información de clientes existentes
3. ❌ Eliminar clientes
4. ❌ Importar clientes desde CSV
5. ❌ Exportar clientes (posiblemente restringido)
6. ❌ Ver clientes inválidos o realizar limpieza de datos

### Implementación en el Código

Según el análisis del código:

**Archivo:** `CODE/src/app/routes/customers.py`

- **Línea ~513:** Solo ADMIN puede ver clientes inválidos
  ```python
  if current_user.role.value != "ADMIN":
      raise HTTPException(status_code=403, detail="Solo administradores pueden ver clientes inválidos")
  ```

- **Línea ~95:** Solo ADMIN puede eliminar clientes
  ```python
  if current_user.role.value != "ADMIN":
      raise HTTPException(status_code=403, detail="Solo administradores pueden eliminar clientes")
  ```

---

## 📊 Ver Estadísticas - ¿Qué puede ver un USUARIO?

### Restricción Importante ⚠️

**CONTRADICCIÓN ENCONTRADA:** Aunque la matriz de permisos indica que USUARIO puede "Ver estadísticas" (✅), el código implementa una restricción:

**Archivo:** `CODE/src/app/routes/package_events.py` (Línea ~278-283)

```python
# Verificar permisos (solo admin y operadores)
if current_user.role.value not in ["ADMIN", "OPERADOR"]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para ver estadísticas"
    )
```

### Estadísticas Restringidas

Las siguientes estadísticas están **BLOQUEADAS** para el rol USUARIO:

1. ❌ **Estadísticas de eventos de paquetes** - `/api/package-events/statistics`
2. ❌ **Estadísticas de mensajes** - Según `CODE/src/app/routes/messages.py` (Línea ~62-68)
3. ❌ **Estadísticas de anuncios** - Según `CODE/src/app/routes/announcements.py` (Línea ~288-294)

```python
# messages.py
if current_user.role.value not in ["ADMIN", "OPERATOR", "OPERADOR"]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para ver estadísticas de mensajes"
    )

# announcements.py
if current_user.role.value not in ["ADMIN", "OPERADOR"]:
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos para ver estadísticas de anuncios"
    )
```

### Posibles Estadísticas Permitidas

El USUARIO podría ver estadísticas básicas en:

- Dashboard personal (si existe)
- Estadísticas de sus propios paquetes
- Contadores generales en la interfaz

---

## 🧪 Cómo Comprobar los Permisos

### Método 1: Prueba Manual en la Interfaz Web

1. **Crear un usuario de prueba con rol USUARIO:**
   ```bash
   # Acceder al contenedor o ejecutar script
   python CODE/scripts/create_test_user.py --role USUARIO
   ```

2. **Iniciar sesión con el usuario USUARIO**

3. **Probar acceso a clientes:**
   - Navegar a la sección de clientes
   - Verificar que NO aparezcan botones de:
     - "Nuevo Cliente"
     - "Editar" en cada cliente
     - "Eliminar"
     - "Importar CSV"
   - Verificar que SÍ pueda:
     - Ver la lista de clientes
     - Buscar clientes
     - Ver detalles de un cliente

4. **Probar acceso a estadísticas:**
   - Intentar acceder a `/admin` (debería ser denegado)
   - Intentar acceder a endpoints de estadísticas vía API
   - Verificar qué estadísticas se muestran en el dashboard

### Método 2: Prueba con API (cURL o Postman)

#### Paso 1: Obtener Token de Autenticación

```bash
# Login como USUARIO
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario_prueba",
    "password": "password123"
  }'
```

Guardar el `access_token` de la respuesta.

#### Paso 2: Probar Ver Clientes (Debería funcionar ✅)

```bash
# Listar clientes
curl -X GET "http://localhost:8000/api/customers?skip=0&limit=10" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Resultado esperado:** Código 200 con lista de clientes

#### Paso 3: Probar Crear Cliente (Debería fallar ❌)

```bash
# Intentar crear cliente
curl -X POST "http://localhost:8000/api/customers" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "Usuario",
    "phone": "+573001234567"
  }'
```

**Resultado esperado:** Código 403 (Forbidden) o error de permisos

#### Paso 4: Probar Ver Estadísticas (Debería fallar ❌)

```bash
# Intentar ver estadísticas de eventos
curl -X GET "http://localhost:8000/api/package-events/statistics" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Resultado esperado:** Código 403 con mensaje "No tienes permisos para ver estadísticas"

```bash
# Intentar ver estadísticas de mensajes
curl -X GET "http://localhost:8000/api/messages/statistics" \
  -H "Authorization: Bearer TU_TOKEN_AQUI"
```

**Resultado esperado:** Código 403 con mensaje "No tienes permisos para ver estadísticas de mensajes"

### Método 3: Prueba con Script Python

Crear un script de prueba:

```python
# test_usuario_permissions.py
import requests

BASE_URL = "http://localhost:8000"
USERNAME = "usuario_prueba"
PASSWORD = "password123"

def test_usuario_permissions():
    # 1. Login
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    
    if response.status_code != 200:
        print("❌ Error en login")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login exitoso\n")
    
    # 2. Probar ver clientes (debería funcionar)
    print("🔍 Probando: Ver clientes...")
    response = requests.get(f"{BASE_URL}/api/customers", headers=headers)
    if response.status_code == 200:
        print("✅ PERMITIDO: Ver clientes")
    else:
        print(f"❌ DENEGADO: Ver clientes (código {response.status_code})")
    
    # 3. Probar crear cliente (debería fallar)
    print("\n🔍 Probando: Crear cliente...")
    response = requests.post(f"{BASE_URL}/api/customers", headers=headers, json={
        "first_name": "Test",
        "last_name": "Usuario",
        "phone": "+573001234567"
    })
    if response.status_code == 403:
        print("✅ CORRECTAMENTE DENEGADO: Crear cliente")
    elif response.status_code == 200:
        print("❌ ERROR: Usuario puede crear clientes (no debería)")
    else:
        print(f"⚠️ Respuesta inesperada: {response.status_code}")
    
    # 4. Probar ver estadísticas (debería fallar según código)
    print("\n🔍 Probando: Ver estadísticas de eventos...")
    response = requests.get(f"{BASE_URL}/api/package-events/statistics", headers=headers)
    if response.status_code == 403:
        print("✅ DENEGADO: Ver estadísticas (según implementación actual)")
    elif response.status_code == 200:
        print("⚠️ PERMITIDO: Ver estadísticas (contradice implementación)")
    else:
        print(f"⚠️ Respuesta inesperada: {response.status_code}")
    
    # 5. Probar acceso a admin (debería fallar)
    print("\n🔍 Probando: Acceso a panel admin...")
    response = requests.get(f"{BASE_URL}/admin", headers=headers)
    if response.status_code in [403, 401]:
        print("✅ CORRECTAMENTE DENEGADO: Acceso a admin")
    elif response.status_code == 200:
        print("❌ ERROR: Usuario puede acceder a admin (no debería)")
    else:
        print(f"⚠️ Respuesta inesperada: {response.status_code}")

if __name__ == "__main__":
    test_usuario_permissions()
```

Ejecutar:

```bash
python test_usuario_permissions.py
```

---

## 📝 Resumen de Hallazgos

### ✅ Confirmado: USUARIO puede ver clientes

- Acceso de solo lectura a la lista de clientes
- Puede buscar y ver detalles
- No puede crear, editar o eliminar

### ⚠️ Contradicción: Estadísticas

**Documentación dice:** USUARIO puede ver estadísticas (✅)

**Código implementa:** Solo ADMIN y OPERADOR pueden ver estadísticas (❌)

**Archivos afectados:**
- `CODE/src/app/routes/package_events.py` - Estadísticas de eventos
- `CODE/src/app/routes/messages.py` - Estadísticas de mensajes
- `CODE/src/app/routes/announcements.py` - Estadísticas de anuncios

### 🔧 Recomendación

Decidir cuál es el comportamiento correcto:

**Opción A:** Actualizar la documentación para reflejar que USUARIO NO puede ver estadísticas

**Opción B:** Modificar el código para permitir que USUARIO vea estadísticas básicas (sin datos sensibles)

---

## 📞 Contacto

Si encuentras discrepancias o necesitas aclaración sobre permisos, contacta al equipo de desarrollo.
