# 🎬 Ejemplo Visual del Funcionamiento

## Escenario 1: Cliente con Paquetes Anunciados

### Paso 1: Usuario ingresa teléfono
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: [3001234567_________]         │
│                                             │
│ 👤 Nombre: [___________________]           │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

### Paso 2: Sistema busca cliente (automático al salir del campo)
```
🔍 Buscando cliente...
✅ Cliente encontrado: JUAN PEREZ
✅ Tiene 2 paquetes anunciados
```

### Paso 3: Vista actualizada con información
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: 3001234567                    │
│                                             │
│ 👤 Nombre: JUAN PEREZ                      │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ ℹ️ Este cliente tiene 2 paquete(s)      │ │
│ │    anunciado(s)                         │ │
│ │                                          │ │
│ │ Códigos de consulta (clic para ver):    │ │
│ │                                          │ │
│ │ • 5SX8 🔗 ← Clic aquí                   │ │
│ │ • A1B2 🔗 ← Clic aquí                   │ │
│ │                                     [X] │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

### Paso 4: Usuario hace clic en un código
```
Clic en "5SX8" →
Abre nueva pestaña:
https://staging.jemavi.co/search?auto_search=5SX8

┌─────────────────────────────────────────────┐
│ 🔍 Búsqueda de Paquetes                    │
│                                             │
│ Código: 5SX8                               │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │ 📦 PAPYRUS-123456                       │ │
│ │ Estado: ANUNCIADO                       │ │
│ │ Cliente: JUAN PEREZ                     │ │
│ │ Fecha: 17/12/2024                       │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## Escenario 2: Cliente sin Paquetes Anunciados

### Paso 1: Usuario ingresa teléfono
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: [3009876543_________]         │
│                                             │
│ 👤 Nombre: [___________________]           │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

### Paso 2: Sistema busca cliente
```
🔍 Buscando cliente...
✅ Cliente encontrado: MARIA LOPEZ
✅ No tiene paquetes anunciados
```

### Paso 3: Vista actualizada (sin alerta)
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: 3009876543                    │
│                                             │
│ 👤 Nombre: MARIA LOPEZ                     │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

**Nota:** No aparece ninguna alerta porque no hay paquetes pendientes.

---

## Escenario 3: Cliente Nuevo (No Existe)

### Paso 1: Usuario ingresa teléfono
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: [3005555555_________]         │
│                                             │
│ 👤 Nombre: [___________________]           │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

### Paso 2: Sistema busca cliente
```
🔍 Buscando cliente...
❌ Cliente no encontrado
→ Continuar con proceso normal
```

### Paso 3: Vista sin cambios (usuario debe ingresar nombre)
```
┌─────────────────────────────────────────────┐
│ 📱 Teléfono: 3005555555                    │
│                                             │
│ 👤 Nombre: [___________________] ← Vacío   │
│           ↑                                 │
│           Usuario debe escribir aquí       │
│                                             │
│ [Anunciar Paquete]                         │
└─────────────────────────────────────────────┘
```

---

## 🔄 Flujo Completo del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│  Usuario ingresa teléfono                               │
│           ↓                                              │
│  Pierde foco del campo (blur) o presiona Enter         │
│           ↓                                              │
│  JavaScript: buscarClientePorTelefono()                 │
│           ↓                                              │
│  Fetch: /api/customers/search-by-phone?phone=XXX       │
│           ↓                                              │
│  ┌───────┴────────┐                                     │
│  │                │                                      │
│  ▼                ▼                                      │
│ 404            200 OK                                   │
│ Cliente        Cliente                                  │
│ NO existe      existe                                   │
│  │              │                                        │
│  │              ├─→ Mostrar nombre                      │
│  │              │                                        │
│  │              ├─→ ¿Tiene paquetes anunciados?        │
│  │              │    │                                   │
│  │              │    ├─→ SÍ: Mostrar códigos           │
│  │              │    │    como enlaces                  │
│  │              │    │                                   │
│  │              │    └─→ NO: No mostrar nada           │
│  │              │                                        │
│  └─→ Campo      └─→ Usuario puede                      │
│      nombre          anunciar paquete                   │
│      vacío                                              │
│      (usuario                                           │
│      escribe)                                           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🎨 Colores y Estilos

### Alerta de Paquetes Anunciados:
- **Fondo:** Azul claro (`bg-blue-50`)
- **Borde:** Azul (`border-blue-400`)
- **Texto:** Azul oscuro (`text-blue-800`)
- **Enlaces:** Azul interactivo (`text-blue-600 hover:text-blue-800`)

### Iconos:
- **Info:** ℹ️ (círculo con i)
- **Enlace externo:** 🔗 (flecha saliendo de cuadrado)
- **Cerrar:** ✕ (X)

---

## 📱 Responsive

### Desktop:
```
┌────────────────────────────────────────────────────┐
│ ℹ️ Este cliente tiene 2 paquete(s) anunciado(s)   │
│                                                     │
│ Códigos de consulta (clic para ver detalles):     │
│ • 5SX8 🔗                                          │
│ • A1B2 🔗                                     [X]  │
└────────────────────────────────────────────────────┘
```

### Mobile:
```
┌──────────────────────────────┐
│ ℹ️ Este cliente tiene 2      │
│    paquete(s) anunciado(s)   │
│                              │
│ Códigos de consulta:         │
│ • 5SX8 🔗                    │
│ • A1B2 🔗              [X]   │
└──────────────────────────────┘
```

---

## 🧪 Casos de Prueba

### Prueba 1: Cliente con 1 paquete
```
Input: 3001111111
Output: "Este cliente tiene 1 paquete(s) anunciado(s)"
        • ABC1 🔗
```

### Prueba 2: Cliente con múltiples paquetes
```
Input: 3002222222
Output: "Este cliente tiene 3 paquete(s) anunciado(s)"
        • XYZ9 🔗
        • DEF4 🔗
        • GHI7 🔗
```

### Prueba 3: Cliente sin paquetes
```
Input: 3003333333
Output: Solo muestra nombre, sin alerta
```

### Prueba 4: Cliente nuevo
```
Input: 3009999999
Output: Campo nombre vacío, sin alerta
```

---

## ✅ Validaciones

1. **Teléfono mínimo 10 dígitos** antes de buscar
2. **Solo paquetes con `is_processed = FALSE`**
3. **Solo paquetes con `is_active = TRUE`**
4. **Enlaces abren en nueva pestaña** (`target="_blank"`)
5. **Alerta se puede cerrar** (botón X)
6. **Alerta se limpia** al buscar otro teléfono

---

## 🔗 URLs Generadas

### Staging:
```
/search?auto_search=5SX8
→ https://staging.jemavi.co/search?auto_search=5SX8
```

### Producción:
```
/search?auto_search=5SX8
→ https://jemavi.co/search?auto_search=5SX8
```

**Nota:** La URL es relativa (`/search`) para que funcione en ambos ambientes.
