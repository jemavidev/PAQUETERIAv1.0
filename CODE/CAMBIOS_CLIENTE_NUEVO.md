# 🆕 Cambios - Soporte para Clientes Nuevos

## ✅ Nueva Funcionalidad Implementada

### Descripción
Ahora el sistema permite crear clientes nuevos directamente desde el anuncio PAPYRUS cuando el número de teléfono no está registrado.

---

## 🔄 Flujo Actualizado

### Caso 1: Cliente Existente ✅
```
1. Usuario ingresa teléfono
2. Sistema busca y encuentra cliente
3. Muestra nombre (solo lectura, fondo gris)
4. Mensaje: "✓ Cliente encontrado en el sistema"
5. Usuario hace clic en "Anunciar Paquete"
6. Sistema crea anuncio con guía PAPYRUS-XXXXXX
```

### Caso 2: Cliente Nuevo 🆕
```
1. Usuario ingresa teléfono
2. Sistema busca y NO encuentra cliente
3. Muestra campo de nombre (editable, fondo blanco)
4. Mensaje: "✏️ Ingresa el nombre del cliente para crear uno nuevo"
5. Usuario ingresa nombre del cliente
6. Usuario hace clic en "Anunciar Paquete"
7. Sistema crea cliente nuevo
8. Sistema crea anuncio con guía PAPYRUS-XXXXXX
```

---

## 🎨 Cambios en la UI

### Campo de Nombre Dinámico

**Cliente Existente:**
- Campo: Solo lectura (readonly)
- Fondo: Gris (`bg-gray-50`)
- Cursor: No permitido (`cursor-not-allowed`)
- Mensaje: Verde con ✓

**Cliente Nuevo:**
- Campo: Editable
- Fondo: Blanco/Transparente
- Cursor: Normal
- Mensaje: Azul con ✏️
- Auto-focus en el campo de nombre

---

## 🔧 Cambios Técnicos

### Frontend (`announce_quick.html`)

**1. Campo de Nombre Actualizado:**
```html
<input type="text" 
       id="customer_name" 
       name="customer_name" 
       class="w-full px-0 py-3 border-0 border-b-2 border-gray-200 
              focus:border-papyrus-blue focus:ring-0 bg-transparent 
              transition-colors text-sm sm:text-base"
       placeholder="Nombre del cliente"
       oninput="this.value = this.value.toUpperCase()">
```

**2. Búsqueda de Cliente Mejorada:**
```javascript
if (response.ok) {
    // Cliente existente - solo lectura
    customerNameInput.readOnly = true;
    customerNameInput.classList.add('bg-gray-50', 'cursor-not-allowed');
} else if (response.status === 404) {
    // Cliente nuevo - editable
    customerNameInput.readOnly = false;
    customerNameInput.classList.add('bg-transparent');
    customerNameInput.focus();
}
```

**3. Validación Actualizada:**
```javascript
// Validar nombre solo si el campo es editable
if (!customerNameInput.readOnly && !customerName) {
    showError('📝 Campo Requerido', 'El nombre del cliente es requerido');
    return;
}
```

**4. Envío con Nombre:**
```javascript
const requestData = {
    customer_phone: normalizedPhone
};

// Incluir nombre si existe (para clientes nuevos)
if (customerName && customerName.trim()) {
    requestData.customer_name = customerName.trim().toUpperCase();
}
```

### Backend (`public.py`)

**1. Endpoint Actualizado:**
```python
@router.post("/api/announcements/quick")
async def create_quick_announcement(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    customer_phone = body.get("customer_phone", "").strip()
    customer_name_input = body.get("customer_name", "").strip()  # ← NUEVO
```

**2. Lógica de Cliente:**
```python
existing_customer = customer_service.get_customer_by_phone(db, customer_phone)

if existing_customer:
    # Usar cliente existente
    customer_id = existing_customer.id
    customer_name = existing_customer.full_name
else:
    # Crear cliente nuevo
    if not customer_name_input:
        return error("Nombre requerido")
    
    # Separar nombre y apellido
    name_parts = customer_name_input.split()
    first_name = name_parts[0]
    last_name = " ".join(name_parts[1:]) or "PENDIENTE"
    
    # Crear cliente
    new_customer = customer_service.create_customer(db, CustomerCreate(...))
    customer_id = new_customer.id
    customer_name = new_customer.full_name
```

---

## 📊 Comparación

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Cliente no encontrado** | Error: "Cliente no encontrado" | Permite crear cliente nuevo |
| **Campo de nombre** | Solo lectura siempre | Dinámico (readonly o editable) |
| **Validación de nombre** | No aplica | Solo si es cliente nuevo |
| **Creación de cliente** | No soportado | ✅ Soportado |
| **Datos requeridos** | Solo teléfono | Teléfono + Nombre (si es nuevo) |

---

## 🧪 Casos de Prueba

### Test 1: Cliente Existente
```bash
# 1. Ingresar teléfono existente: +573001234567
# 2. Verificar que aparece nombre en gris (readonly)
# 3. Verificar mensaje verde: "✓ Cliente encontrado"
# 4. Hacer clic en "Anunciar Paquete"
# 5. Verificar que se crea anuncio con PAPYRUS-XXXXXX
```

### Test 2: Cliente Nuevo
```bash
# 1. Ingresar teléfono nuevo: +573009999999
# 2. Verificar que aparece campo editable
# 3. Verificar mensaje azul: "✏️ Ingresa el nombre..."
# 4. Ingresar nombre: "JUAN PEREZ"
# 5. Hacer clic en "Anunciar Paquete"
# 6. Verificar que se crea cliente y anuncio
```

### Test 3: Validación de Nombre
```bash
# 1. Ingresar teléfono nuevo: +573009999998
# 2. Campo de nombre aparece editable
# 3. NO ingresar nombre
# 4. Hacer clic en "Anunciar Paquete"
# 5. Verificar error: "El nombre del cliente es requerido"
```

### Test API
```bash
# Cliente existente
curl -X POST "https://staging.jemavi.co/api/announcements/quick" \
  -H "Content-Type: application/json" \
  -d '{"customer_phone": "+573001234567"}'

# Cliente nuevo
curl -X POST "https://staging.jemavi.co/api/announcements/quick" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_phone": "+573009999999",
    "customer_name": "JUAN PEREZ"
  }'
```

---

## 📝 Notas Importantes

### Separación de Nombre y Apellido
El sistema automáticamente separa el nombre completo:
- **Primera palabra** → `first_name`
- **Resto de palabras** → `last_name`
- **Si solo hay una palabra** → `last_name = "PENDIENTE"`

**Ejemplos:**
- "JUAN PEREZ" → first_name: "JUAN", last_name: "PEREZ"
- "MARIA JOSE GARCIA" → first_name: "MARIA", last_name: "JOSE GARCIA"
- "CARLOS" → first_name: "CARLOS", last_name: "PENDIENTE"

### Conversión a Mayúsculas
El nombre se convierte automáticamente a mayúsculas:
- En el frontend: `oninput="this.value = this.value.toUpperCase()"`
- En el backend: Se almacena tal como viene (ya en mayúsculas)

### Longitud Máxima
- `first_name`: Máximo 50 caracteres
- `last_name`: Máximo 50 caracteres

---

## ✅ Checklist de Verificación

- [x] Campo de nombre dinámico (readonly/editable)
- [x] Búsqueda de cliente actualizada
- [x] Validación de nombre para clientes nuevos
- [x] Creación de cliente en backend
- [x] Separación automática de nombre/apellido
- [x] Conversión a mayúsculas
- [x] Mensajes de estado claros
- [x] Auto-focus en campo de nombre
- [x] Sin errores de sintaxis
- [ ] Probado en staging
- [ ] Verificado con cliente existente
- [ ] Verificado con cliente nuevo

---

## 🚀 Despliegue

Los cambios están listos para ser desplegados:

```bash
git add .
git commit -m "feat: Soporte para crear clientes nuevos desde anuncio PAPYRUS"
git push origin main
```

---

## 📸 Capturas de Pantalla Esperadas

### Cliente Existente
```
┌─────────────────────────────────────────┐
│ 📱 Teléfono: +573001234567             │
│ ✓ Cliente encontrado en el sistema     │
│                                         │
│ 👤 Nombre: JUAN PEREZ [gris, readonly] │
│                                         │
│ [Anunciar Paquete]                      │
└─────────────────────────────────────────┘
```

### Cliente Nuevo
```
┌─────────────────────────────────────────┐
│ 📱 Teléfono: +573009999999             │
│ ✏️ Ingresa el nombre del cliente...    │
│                                         │
│ 👤 Nombre: _____________ [editable]    │
│                                         │
│ [Anunciar Paquete]                      │
└─────────────────────────────────────────┘
```

---

**Fecha**: 11 de Diciembre, 2025
**Versión**: 2.1.0
**Estado**: ✅ Listo para desplegar
