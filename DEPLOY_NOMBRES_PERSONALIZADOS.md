# 🚀 Deploy: Nombres Personalizados para Paquetes

## 📋 Checklist Pre-Deploy

- [x] Código implementado y probado localmente
- [x] Sin errores de sintaxis o linting
- [ ] Probado en staging
- [ ] Validado por usuario final
- [ ] Listo para producción

## 🔧 Archivos Modificados

### Backend:
```
CODE/src/app/routes/public.py
```
- Endpoint: `POST /api/announcements/quick`
- Cambio: Detecta nombre editado y lo usa solo para el anuncio

### Frontend:
```
CODE/src/templates/announce/announce_quick.html
```
- Agregado: Botón de edición con ícono de lápiz
- Agregado: Función `enableNameEditing()`
- Agregado: Mensajes explicativos

## 🚀 Comandos de Deploy

### Opción 1: Deploy Completo (Recomendado)
```bash
# Desde el directorio raíz del proyecto
./deploy.sh
```

### Opción 2: Deploy Manual

#### Staging:
```bash
cd CODE
docker-compose -f ../docker-compose.staging.yml down
docker-compose -f ../docker-compose.staging.yml up -d --build
docker-compose -f ../docker-compose.staging.yml logs -f backend
```

#### Producción:
```bash
cd CODE
docker-compose -f ../docker-compose.prod.yml down
docker-compose -f ../docker-compose.prod.yml up -d --build
docker-compose -f ../docker-compose.prod.yml logs -f backend
```

### Opción 3: Solo Reiniciar Backend (Cambios menores)
```bash
# Staging
docker-compose -f docker-compose.staging.yml restart backend

# Producción
docker-compose -f docker-compose.prod.yml restart backend
```

## ✅ Verificación Post-Deploy

### 1. Verificar que el servicio está corriendo
```bash
# Staging
curl -I https://staging.jemavi.co/announce-papyrus

# Producción
curl -I https://jemavi.co/announce-papyrus
```

**Respuesta esperada:** `200 OK`

### 2. Probar la funcionalidad

#### Paso 1: Abrir la página
- Staging: https://staging.jemavi.co/announce-papyrus
- Producción: https://jemavi.co/announce-papyrus

#### Paso 2: Ingresar teléfono existente
- Ejemplo: 3001234567

#### Paso 3: Verificar elementos visuales
- ✅ Aparece el nombre del cliente
- ✅ Aparece el ícono de lápiz al lado del nombre
- ✅ El campo está en modo solo lectura (fondo gris)

#### Paso 4: Probar edición
- Hacer clic en el ícono de lápiz
- ✅ El campo se vuelve editable
- ✅ El ícono cambia a check verde
- ✅ Aparece mensaje: "Editando - Este nombre se usará SOLO para este paquete..."
- ✅ El borde se vuelve amarillo

#### Paso 5: Crear anuncio
- Editar el nombre (ej: agregar " - OFICINA")
- Hacer clic en "Anunciar Paquete"
- ✅ Se crea el anuncio exitosamente
- ✅ Aparece modal de confirmación

#### Paso 6: Verificar persistencia
- Ingresar el mismo teléfono nuevamente
- ✅ Debe mostrar el nombre ORIGINAL del cliente (sin la edición anterior)

### 3. Verificar logs
```bash
# Ver logs del backend
docker-compose -f docker-compose.staging.yml logs -f backend | grep "Nombre personalizado"
```

**Logs esperados:**
```
✅ Cliente existente: <uuid> - JUAN PÉREZ
📝 Nombre personalizado para este anuncio: JUAN PÉREZ - OFICINA
```

### 4. Verificar en base de datos (Opcional)

```sql
-- Verificar que el cliente mantiene su nombre original
SELECT id, full_name, phone FROM customers WHERE phone = '+573001234567';

-- Verificar que el anuncio tiene el nombre personalizado
SELECT id, customer_name, guide_number, customer_id 
FROM package_announcements_new 
WHERE customer_phone = '+573001234567' 
ORDER BY created_at DESC 
LIMIT 5;
```

**Resultado esperado:**
- Cliente: Nombre original sin cambios
- Anuncios: Pueden tener nombres diferentes (personalizados)

## 🐛 Troubleshooting

### Problema: El ícono de lápiz no aparece
**Solución:**
1. Limpiar caché del navegador (Ctrl + Shift + R)
2. Verificar que el archivo HTML se actualizó correctamente
3. Revisar logs del backend

### Problema: El nombre del cliente se modifica
**Solución:**
1. Verificar que el código del backend está actualizado
2. Revisar logs para ver si hay errores
3. Verificar la lógica en `public.py` línea ~1780

### Problema: Error al crear anuncio
**Solución:**
1. Revisar logs del backend: `docker-compose logs backend`
2. Verificar conexión a base de datos
3. Verificar que el endpoint `/api/announcements/quick` responde

## 📊 Métricas a Monitorear

Después del deploy, monitorear:

1. **Tasa de uso de edición:**
   - ¿Cuántos anuncios usan nombres personalizados?
   - Query: `SELECT COUNT(*) FROM package_announcements_new WHERE customer_name != (SELECT full_name FROM customers WHERE id = customer_id)`

2. **Errores en el endpoint:**
   - Revisar logs de errores en `/api/announcements/quick`

3. **Feedback de usuarios:**
   - ¿Los usuarios entienden la funcionalidad?
   - ¿Hay confusión sobre el comportamiento?

## 🔄 Rollback (Si es necesario)

Si hay problemas críticos, hacer rollback:

```bash
# 1. Ir al commit anterior
git log --oneline  # Ver commits
git checkout <commit-anterior>

# 2. Rebuild y deploy
docker-compose -f docker-compose.staging.yml down
docker-compose -f docker-compose.staging.yml up -d --build

# 3. Volver a la rama actual cuando esté listo
git checkout staging
```

## 📝 Notas Finales

- Esta funcionalidad es **backward compatible** (no rompe nada existente)
- Es **opcional** (si no se edita, funciona como antes)
- **No requiere migración de base de datos**
- **No afecta datos existentes**

## ✅ Checklist Post-Deploy

- [ ] Servicio corriendo sin errores
- [ ] Página carga correctamente
- [ ] Ícono de lápiz visible
- [ ] Edición funciona correctamente
- [ ] Anuncios se crean exitosamente
- [ ] Cliente mantiene nombre original
- [ ] SMS/Emails se envían correctamente
- [ ] Logs sin errores críticos
- [ ] Usuarios notificados del cambio (si aplica)

---

**Fecha de implementación:** 2024-12-17
**Versión:** 1.0
**Estado:** ✅ Listo para deploy
