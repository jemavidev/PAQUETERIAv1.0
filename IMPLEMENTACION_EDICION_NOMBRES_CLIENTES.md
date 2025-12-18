# Implementación de Edición de Nombres Personalizados para Paquetes

## 📋 Resumen

Se ha implementado la funcionalidad para **editar el nombre del destinatario de un paquete específico** sin modificar el nombre del cliente en la base de datos. Esto permite usar nombres personalizados o alias para entregas específicas mientras se mantiene la información original del cliente.

## 🔗 URL

**URL:** https://staging.jemavi.co/announce-papyrus

## ✨ Características Principales

### Comportamiento del Sistema:

1. **Cliente Existente:**
   - Cuando se encuentra un cliente por teléfono, aparece un **ícono de lápiz** al lado del nombre
   - El campo muestra el nombre del cliente en modo **solo lectura** (fondo gris)
   - Al hacer clic en el ícono de lápiz, se puede editar el nombre

2. **Edición de Nombre:**
   - El campo se vuelve editable
   - El ícono cambia a un check verde
   - Aparece el mensaje: "✏️ Editando - Este nombre se usará SOLO para este paquete (el cliente mantiene su nombre original)"
   - El borde del campo se vuelve amarillo

3. **Guardado:**
   - El nombre editado se usa **SOLO para el anuncio/paquete actual**
   - El cliente en la base de datos **mantiene su nombre original**
   - El próximo paquete para el mismo teléfono mostrará el nombre original del cliente

## 🎯 Casos de Uso

Esta funcionalidad es útil para:

- **Entregas a diferentes personas:** Cliente "JUAN PÉREZ" pero el paquete es para "MARÍA PÉREZ"
- **Ubicaciones específicas:** "JUAN PÉREZ - OFICINA" o "JUAN PÉREZ - CASA"
- **Departamentos:** "EMPRESA XYZ - CONTABILIDAD"
- **Alias temporales:** "JUAN PÉREZ - EDIFICIO 3 APT 201"

## 🎯 Flujo de Uso

1. **Ingresar teléfono** del cliente (ej: 3001234567)
2. El sistema busca automáticamente al cliente
3. Si el cliente existe:
   - Se muestra su nombre registrado en modo solo lectura
   - Aparece el ícono de lápiz para editar
4. **Opcional:** Hacer clic en el ícono de lápiz para editar
5. Modificar el nombre según sea necesario (ej: agregar ubicación, cambiar destinatario)
6. Hacer clic en "Anunciar Paquete"
7. El sistema:
   - Crea el anuncio con el nombre personalizado
   - **NO modifica** el nombre del cliente en la BD
   - El cliente mantiene su nombre original para futuros paquetes

## 📝 Archivos Modificados

### Backend:
- `CODE/src/app/routes/public.py` - Endpoint `/api/announcements/quick`
  - Modificado para detectar si el nombre fue editado
  - Si se edita, usa el nombre personalizado SOLO para el anuncio
  - NO actualiza el nombre del cliente en la BD

### Frontend:
- `CODE/src/templates/announce/announce_quick.html`
  - Agregado botón de edición (ícono de lápiz)
  - Función `enableNameEditing()` para habilitar edición
  - Mensajes claros sobre el comportamiento

## 🔍 Lógica Implementada

### Backend (Python):
```python
if existing_customer:
    customer_id = existing_customer.id
    
    # Si el usuario editó el nombre, usar el nombre editado SOLO para este anuncio
    if customer_name_input and customer_name_input.upper() != existing_customer.full_name.upper():
        customer_name = customer_name_input.upper()  # Nombre personalizado para el anuncio
        # El cliente mantiene su nombre original en la BD
    else:
        customer_name = existing_customer.full_name  # Nombre original
```

### Frontend (JavaScript):
- Detecta cuando el cliente existe
- Muestra botón de edición
- Al editar, muestra mensaje claro sobre el comportamiento
- Envía el nombre editado al backend

## 🧪 Cómo Probar

### 1. Reiniciar el Backend
```bash
cd CODE
docker-compose -f ../docker-compose.staging.yml restart backend
```

### 2. Probar con Cliente Existente

**Paso 1:** Ir a https://staging.jemavi.co/announce-papyrus

**Paso 2:** Ingresar un teléfono de cliente existente (ej: 3001234567)

**Paso 3:** Observar que:
- Aparece el nombre del cliente
- Hay un ícono de lápiz al lado

**Paso 4:** Hacer clic en el ícono de lápiz

**Paso 5:** Editar el nombre (ej: agregar " - OFICINA")

**Paso 6:** Anunciar el paquete

**Paso 7:** Verificar:
- El anuncio se creó con el nombre editado
- Buscar el mismo teléfono nuevamente
- Debe mostrar el nombre ORIGINAL del cliente (sin la edición)

### 3. Verificar en Dashboard

**Opción A - Ver el Anuncio:**
- Ir al dashboard de anuncios
- Buscar el anuncio recién creado
- Verificar que tiene el nombre personalizado

**Opción B - Ver el Cliente:**
- Ir a gestión de clientes
- Buscar el cliente por teléfono
- Verificar que su nombre NO cambió

### 4. Ejemplo Completo

```
Cliente en BD: "JUAN PÉREZ" (Tel: 3001234567)

Anuncio 1:
- Editar a: "JUAN PÉREZ - OFICINA"
- Resultado: Anuncio con "JUAN PÉREZ - OFICINA"
- Cliente sigue siendo: "JUAN PÉREZ"

Anuncio 2 (mismo teléfono):
- Aparece: "JUAN PÉREZ" (nombre original)
- Editar a: "JUAN PÉREZ - CASA"
- Resultado: Anuncio con "JUAN PÉREZ - CASA"
- Cliente sigue siendo: "JUAN PÉREZ"
```

## 📌 Notas Técnicas

- El nombre del cliente en la BD **NUNCA** se modifica
- Cada anuncio puede tener un nombre personalizado diferente
- La funcionalidad es compatible con clientes nuevos y existentes
- Si no se edita el nombre, se usa el nombre original del cliente
- Los SMS y emails usan el nombre del anuncio (personalizado si fue editado)
