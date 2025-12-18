# 🎨 Guía Visual: Nombres Personalizados para Paquetes

## 📱 Interfaz de Usuario

### Estado 1: Cliente Existente (Sin Editar)
```
┌─────────────────────────────────────────┐
│  📱 Teléfono                            │
│  [3001234567]                           │
│                                         │
│  👤 Nombre del Cliente                  │
│  [JUAN PÉREZ                      ✏️]  │
│  ✓ Cliente encontrado en el sistema    │
│                                         │
│  💬 [Contactar por WhatsApp]           │
│                                         │
│  [📦 Anunciar Paquete]                 │
└─────────────────────────────────────────┘

Características:
- Campo de nombre con fondo GRIS (solo lectura)
- Ícono de LÁPIZ visible a la derecha
- Mensaje verde: "Cliente encontrado"
```

### Estado 2: Modo Edición Activado
```
┌─────────────────────────────────────────┐
│  📱 Teléfono                            │
│  [3001234567]                           │
│                                         │
│  👤 Nombre del Cliente                  │
│  [JUAN PÉREZ - OFICINA            ✓]  │
│  ✏️ Editando - Este nombre se usará    │
│     SOLO para este paquete              │
│                                         │
│  💬 [Contactar por WhatsApp]           │
│                                         │
│  [📦 Anunciar Paquete]                 │
└─────────────────────────────────────────┘

Características:
- Campo de nombre con fondo BLANCO (editable)
- Borde AMARILLO indicando edición
- Ícono cambia a CHECK VERDE
- Mensaje amarillo explicativo
- Texto seleccionado automáticamente
```

### Estado 3: Cliente Nuevo
```
┌─────────────────────────────────────────┐
│  📱 Teléfono                            │
│  [3009876543]                           │
│                                         │
│  👤 Nombre del Cliente                  │
│  [MARÍA LÓPEZ                        ]  │
│  (Sin ícono de lápiz)                   │
│                                         │
│  💬 [Contactar por WhatsApp]           │
│                                         │
│  [📦 Anunciar Paquete]                 │
└─────────────────────────────────────────┘

Características:
- Campo editable desde el inicio
- Sin ícono de lápiz (no es necesario)
- Fondo blanco (editable)
- Campo requerido
```

## 🔄 Flujo de Interacción

```
┌─────────────────┐
│ Usuario ingresa │
│   teléfono      │
└────────┬────────┘
         │
         ▼
    ┌────────┐
    │¿Existe?│
    └───┬────┘
        │
    ┌───┴───┐
    │       │
   SÍ      NO
    │       │
    ▼       ▼
┌───────┐ ┌──────────┐
│Mostrar│ │Campo     │
│nombre │ │editable  │
│+ lápiz│ │desde     │
└───┬───┘ │inicio    │
    │     └──────────┘
    ▼
┌───────────┐
│¿Editar?   │
└─────┬─────┘
      │
  ┌───┴───┐
  │       │
 SÍ      NO
  │       │
  ▼       ▼
┌─────┐ ┌─────┐
│Clic │ │Usar │
│lápiz│ │orig.│
└──┬──┘ └──┬──┘
   │       │
   ▼       │
┌─────┐    │
│Editar│   │
│nombre│   │
└──┬──┘    │
   │       │
   └───┬───┘
       ▼
  ┌─────────┐
  │Anunciar │
  │ paquete │
  └────┬────┘
       │
       ▼
  ┌──────────────────┐
  │Anuncio creado con│
  │nombre editado    │
  │                  │
  │Cliente mantiene  │
  │nombre original   │
  └──────────────────┘
```

## 📊 Comparación: Antes vs Después

### ANTES (Sin esta funcionalidad):
```
Cliente: JUAN PÉREZ (Tel: 3001234567)

Paquete 1: JUAN PÉREZ
Paquete 2: JUAN PÉREZ
Paquete 3: JUAN PÉREZ

Problema: No se puede especificar ubicación o destinatario diferente
```

### DESPUÉS (Con esta funcionalidad):
```
Cliente: JUAN PÉREZ (Tel: 3001234567)
         ↑ Nombre NUNCA cambia

Paquete 1: JUAN PÉREZ - OFICINA
Paquete 2: JUAN PÉREZ - CASA
Paquete 3: MARÍA PÉREZ (esposa)

Ventaja: Flexibilidad sin duplicar clientes
```

## 🎯 Casos de Uso Visualizados

### Caso 1: Múltiples Ubicaciones
```
┌─────────────────────────────────────┐
│ Cliente en BD                       │
│ ┌─────────────────────────────────┐ │
│ │ EMPRESA ABC                     │ │
│ │ Tel: 3001111111                 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              │
              ├─────────────────┬─────────────────┐
              ▼                 ▼                 ▼
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │Paquete 1 │      │Paquete 2 │      │Paquete 3 │
        │EMPRESA   │      │EMPRESA   │      │EMPRESA   │
        │ABC -     │      │ABC -     │      │ABC -     │
        │BODEGA 1  │      │BODEGA 2  │      │OFICINA   │
        └──────────┘      └──────────┘      └──────────┘
```

### Caso 2: Diferentes Destinatarios
```
┌─────────────────────────────────────┐
│ Cliente en BD                       │
│ ┌─────────────────────────────────┐ │
│ │ JUAN PÉREZ                      │ │
│ │ Tel: 3002222222                 │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
              │
              ├─────────────────┬─────────────────┐
              ▼                 ▼                 ▼
        ┌──────────┐      ┌──────────┐      ┌──────────┐
        │Paquete 1 │      │Paquete 2 │      │Paquete 3 │
        │JUAN      │      │MARÍA     │      │PEDRO     │
        │PÉREZ     │      │PÉREZ     │      │PÉREZ     │
        │          │      │(esposa)  │      │(hijo)    │
        └──────────┘      └──────────┘      └──────────┘
```

## 🎨 Elementos Visuales Clave

### Ícono de Lápiz (Estado Normal)
```
┌─────┐
│  ✏️ │  ← Color: Gris (#9CA3AF)
└─────┘    Hover: Azul (#3B82F6)
           Tooltip: "Editar nombre del cliente"
```

### Ícono de Check (Estado Editando)
```
┌─────┐
│  ✓  │  ← Color: Verde (#10B981)
└─────┘    Tooltip: "Editando - Nombre personalizado"
```

### Campo de Nombre (Estados)
```
Solo Lectura:
┌────────────────────────────────┐
│ JUAN PÉREZ                  ✏️ │  ← Fondo: Gris claro
└────────────────────────────────┘    Cursor: not-allowed

Editando:
┌────────────────────────────────┐
│ JUAN PÉREZ - OFICINA        ✓ │  ← Fondo: Blanco
└────────────────────────────────┘    Borde: Amarillo
                                      Cursor: text
```

### Mensajes de Estado
```
Cliente Encontrado:
✓ Cliente encontrado en el sistema
  ↑ Color: Verde (#10B981)

Editando:
✏️ Editando - Este nombre se usará SOLO para este paquete
   (el cliente mantiene su nombre original)
   ↑ Color: Amarillo (#F59E0B)
```

## 📱 Responsive Design

### Desktop (> 768px)
```
┌─────────────────────────────────────────────┐
│  Anuncio PAPYRUS                            │
│  Solo necesitas tu número de teléfono       │
├─────────────────────────────────────────────┤
│                                             │
│  📱 Teléfono                                │
│  [3001234567                            ]   │
│                                             │
│  👤 Nombre del Cliente                      │
│  [JUAN PÉREZ                          ✏️]  │
│  ✓ Cliente encontrado en el sistema        │
│                                             │
│  💬 [Contactar por WhatsApp]               │
│                                             │
│  [📦 Anunciar Paquete]                     │
│                                             │
└─────────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────────┐
│ Anuncio PAPYRUS      │
│ Solo necesitas tu    │
│ número de teléfono   │
├──────────────────────┤
│                      │
│ 📱 Teléfono          │
│ [3001234567      ]   │
│                      │
│ 👤 Nombre            │
│ [JUAN PÉREZ    ✏️]  │
│ ✓ Cliente encontrado │
│                      │
│ 💬 [WhatsApp]       │
│                      │
│ [📦 Anunciar]       │
│                      │
└──────────────────────┘
```

## 🎬 Animaciones

### Al hacer clic en el lápiz:
```
1. Ícono lápiz → Ícono check (0.2s)
2. Fondo gris → Fondo blanco (0.3s)
3. Borde normal → Borde amarillo (0.3s)
4. Mensaje verde → Mensaje amarillo (0.2s)
5. Focus en campo + selección de texto
```

### Transiciones CSS:
```css
transition: all 0.3s ease-in-out;
```

## ✅ Checklist Visual

Al probar, verificar:

- [ ] Ícono de lápiz visible y centrado
- [ ] Ícono cambia a check al editar
- [ ] Colores correctos (gris → azul en hover)
- [ ] Campo cambia de gris a blanco
- [ ] Borde amarillo visible al editar
- [ ] Mensajes claros y legibles
- [ ] Responsive en móvil
- [ ] Animaciones suaves
- [ ] Tooltip visible en hover
- [ ] Focus automático al editar
- [ ] Texto seleccionado al editar

---

**Diseño:** Minimalista y funcional
**Colores:** Papyrus Blue (#3B82F6), Verde (#10B981), Amarillo (#F59E0B)
**Tipografía:** Sistema por defecto (sans-serif)
