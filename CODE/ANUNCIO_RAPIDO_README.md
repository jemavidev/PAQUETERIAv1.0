# 🚀 Sistema de Anuncio Rápido - Guía de Implementación

## 📋 Resumen

Se ha implementado un nuevo sistema de **Anuncio Rápido** que permite a los clientes registrados anunciar paquetes ingresando únicamente su número de teléfono. El sistema automáticamente:

- ✅ Busca al cliente en la base de datos
- ✅ Autocompleta el nombre del cliente
- ✅ Genera un número de guía temporal único (formato: `TEMP-XXXXXX`)
- ✅ Crea el anuncio y envía notificaciones (SMS + Email)

## 🎯 Archivos Creados/Modificados

### Nuevos Archivos

1. **Template Frontend**
   - `CODE/src/templates/announce/announce_quick.html`
   - Vista simplificada con búsqueda automática de cliente

2. **Documentación**
   - `CODE/docs/ANUNCIO_RAPIDO.md`
   - Documentación completa del sistema

3. **Script de Pruebas**
   - `CODE/scripts/testing/test_anuncio_rapido.py`
   - Suite de pruebas automatizadas

### Archivos Modificados

1. **Rutas Públicas**
   - `CODE/src/app/routes/public.py`
   - Agregados 3 nuevos endpoints:
     - `GET /announce-quick` - Vista de anuncio rápido
     - `GET /api/customers/search-by-phone` - Búsqueda de cliente
     - `POST /api/announcements/quick` - Creación de anuncio rápido

## 🌐 URLs Disponibles

### Producción/Staging
```
https://staging.jemavi.co/announce-quick
```

### Desarrollo Local
```
http://localhost:8000/announce-quick
```

## 🔧 Cómo Usar

### Para Usuarios Finales

1. **Acceder a la página**
   - Ir a `/announce-quick`

2. **Ingresar teléfono**
   - Escribir el número de teléfono (formato: +573001234567 o 3001234567)
   - El sistema buscará automáticamente después de 500ms

3. **Verificar datos**
   - Si el cliente existe, se mostrará su nombre
   - Si no existe, se mostrará una advertencia

4. **Aceptar términos y enviar**
   - Marcar la casilla de términos y condiciones
   - Hacer clic en "Anunciar Paquete"

5. **Recibir confirmación**
   - Se mostrará un modal con:
     - Número de guía temporal (ej: `TEMP-A3B7C9`)
     - Código de consulta (ej: `X7Y2`)
   - Se enviará SMS y email con los códigos

### Para Desarrolladores

#### Probar Localmente

1. **Iniciar el servidor**
   ```bash
   cd CODE
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Acceder a la vista**
   ```
   http://localhost:8000/announce-quick
   ```

3. **Ejecutar pruebas**
   ```bash
   cd CODE
   python scripts/testing/test_anuncio_rapido.py
   ```

#### Endpoints API

**1. Buscar Cliente por Teléfono**
```bash
curl -X GET "http://localhost:8000/api/customers/search-by-phone?phone=+573001234567"
```

**Respuesta exitosa:**
```json
{
  "id": "uuid",
  "full_name": "JUAN PEREZ",
  "display_name": "Juan Perez",
  "phone": "+573001234567",
  "email": "juan@example.com",
  "is_vip": false,
  "total_packages_received": 5
}
```

**2. Crear Anuncio Rápido**
```bash
curl -X POST "http://localhost:8000/api/announcements/quick" \
  -H "Content-Type: application/json" \
  -d '{"customer_phone": "+573001234567"}'
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "Anuncio creado exitosamente",
  "announcement": {
    "id": "uuid",
    "customer_name": "JUAN PEREZ",
    "customer_phone": "+573001234567",
    "guide_number": "TEMP-A3B7C9",
    "tracking_code": "X7Y2",
    "announced_at": "2025-12-11T10:30:00",
    "status": "pendiente"
  }
}
```

## 🧪 Pruebas

### Ejecutar Suite de Pruebas

```bash
cd CODE
python scripts/testing/test_anuncio_rapido.py
```

### Pruebas Incluidas

1. ✅ Búsqueda de cliente por teléfono
2. ✅ Creación de anuncio rápido
3. ✅ Validación de teléfonos inválidos
4. ✅ Rechazo de anuncios sin cliente existente

### Requisitos para Pruebas

- Servidor corriendo en `http://localhost:8000`
- Cliente existente con teléfono `+573001234567` (o modificar en el script)
- Base de datos accesible

## 📱 Flujo de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│  1. Usuario ingresa teléfono                                │
│     Input: +573001234567                                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Sistema busca cliente (debounce 500ms)                  │
│     GET /api/customers/search-by-phone?phone=+573001234567  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Sistema muestra resultado                                │
│     ✓ Cliente encontrado: "JUAN PEREZ"                      │
│     ⚠ Cliente no encontrado: Usar formulario completo       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Usuario acepta términos y envía                          │
│     POST /api/announcements/quick                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. Sistema procesa                                          │
│     - Genera guía: TEMP-A3B7C9                              │
│     - Genera tracking: X7Y2                                  │
│     - Crea anuncio en BD                                     │
│     - Envía SMS al cliente                                   │
│     - Envía email al cliente                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. Usuario recibe confirmación                              │
│     Modal con códigos + SMS + Email                          │
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Seguridad

- ✅ Validación de formato de teléfono
- ✅ Normalización automática de números
- ✅ Generación de códigos únicos con reintentos (máx 10)
- ✅ Protección contra duplicados
- ✅ Logs de auditoría
- ✅ Manejo robusto de errores

## 🎨 Características del Frontend

### Búsqueda en Tiempo Real
- Debounce de 500ms para evitar múltiples peticiones
- Loader animado durante la búsqueda
- Feedback visual inmediato

### Validaciones
- Formato de teléfono (mínimo 10 dígitos)
- Cliente existente
- Términos y condiciones

### Responsive Design
- Optimizado para móviles y desktop
- Autofocus inteligente (solo en desktop)
- Modal de éxito con códigos destacados

## 📊 Comparación con Anuncio Normal

| Característica | Anuncio Normal (`/announce`) | Anuncio Rápido (`/announce-quick`) |
|----------------|------------------------------|-------------------------------------|
| Campos requeridos | Nombre, Teléfono, Guía | Solo Teléfono |
| Número de guía | Manual | Automático (TEMP-XXXXXX) |
| Cliente nuevo | ✅ Sí | ❌ No (solo existentes) |
| Búsqueda automática | ❌ No | ✅ Sí |
| Tiempo estimado | 30-45 segundos | 15-20 segundos |
| Uso recomendado | Nuevos clientes | Clientes frecuentes |

## 🚀 Despliegue

### Staging
```bash
# Ya está desplegado en:
https://staging.jemavi.co/announce-quick
```

### Producción
```bash
# Cuando esté listo para producción:
git push origin main
# El sistema de CI/CD lo desplegará automáticamente
```

## 📝 Notas Importantes

### Para Clientes Nuevos
- Los clientes nuevos deben usar el formulario completo (`/announce`)
- El sistema creará automáticamente el cliente en la primera vez
- Después podrán usar el anuncio rápido

### Números de Guía Temporales
- Formato: `TEMP-XXXXXX` (6 caracteres alfanuméricos)
- Los operadores pueden actualizar a la guía real después
- El sistema mantiene el historial completo

### Notificaciones
- **SMS**: Siempre se envía (si el servicio está configurado)
- **Email**: Solo si el cliente tiene email registrado
- Ambos incluyen los códigos de guía y tracking

## 🐛 Troubleshooting

### Cliente no encontrado
**Problema**: El sistema no encuentra al cliente por teléfono

**Solución**:
1. Verificar que el teléfono esté en formato correcto
2. Verificar que el cliente exista en la BD
3. Usar el formulario completo para crear el cliente

### Error al generar códigos
**Problema**: "No se pudo generar un código único"

**Solución**:
1. Verificar que la BD no esté llena de códigos
2. Reintentar la operación
3. Revisar logs del servidor

### SMS/Email no se envía
**Problema**: El anuncio se crea pero no llegan notificaciones

**Solución**:
1. Verificar configuración de servicios de SMS/Email
2. Revisar logs del servidor
3. Verificar que el teléfono/email sean válidos

## 📞 Soporte

Para problemas o preguntas:
- **Email**: soporte@jemavi.co
- **Teléfono**: +57 300 123 4567
- **Documentación**: Ver `CODE/docs/ANUNCIO_RAPIDO.md`

## ✅ Checklist de Implementación

- [x] Template HTML creado
- [x] Endpoints API implementados
- [x] Búsqueda de cliente por teléfono
- [x] Generación de guía temporal
- [x] Generación de código de tracking
- [x] Integración con notificaciones (SMS + Email)
- [x] Validaciones de frontend
- [x] Validaciones de backend
- [x] Manejo de errores
- [x] Documentación completa
- [x] Script de pruebas
- [ ] Pruebas en staging
- [ ] Aprobación de usuario
- [ ] Despliegue a producción

## 🎉 ¡Listo para Usar!

El sistema de Anuncio Rápido está completamente implementado y listo para ser probado. Sigue las instrucciones de este README para comenzar a usarlo.
