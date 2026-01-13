# ✅ Checklist de Despliegue - Sistema de Productos

**Fecha:** 2026-01-13  
**Versión:** 1.0.0  
**Ambiente:** Staging → Production

---

## 📋 Pre-Despliegue

### Verificaciones Locales ✅

- [x] Migración ejecutada localmente
- [x] Código compila sin errores
- [x] Importaciones funcionan
- [x] Base de datos tiene las tablas
- [x] Templates existen
- [x] Endpoints registrados
- [x] Rutas web configuradas

### Archivos a Desplegar ✅

**Backend:**
- [x] `alembic/versions/add_products_table.py`
- [x] `alembic/env.py` (modificado)
- [x] `src/app/models/product.py`
- [x] `src/app/services/product_sync_service.py`
- [x] `src/app/routes/products.py`
- [x] `src/app/routes/protected.py` (modificado)
- [x] `src/main.py` (modificado)

**Frontend:**
- [x] `src/templates/products/list.html`

**Documentación:**
- [x] `docs/PRODUCTOS_PLAN_IMPLEMENTACION.md`
- [x] `docs/PRODUCTOS_RESUMEN_RAPIDO.md`
- [x] `docs/PRODUCTOS_GUIA_USO.md`
- [x] `docs/PRODUCTOS_IMPLEMENTACION_COMPLETADA.md`
- [x] `docs/PRODUCTOS_REPORTE_PRUEBAS.md`
- [x] `docs/PRODUCTOS_CHECKLIST_DESPLIEGUE.md`

**Testing:**
- [x] `test_product_sync.py`

---

## 🚀 Despliegue a Staging

### 1. Preparación

```bash
# Hacer commit de cambios
git add .
git commit -m "feat: Sistema de productos completo con sincronización DynamiaERP"

# Push a staging
git push origin staging
```

### 2. En el Servidor Staging

```bash
# Pull de cambios
git pull origin staging

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias (si hay nuevas)
pip install -r requirements.txt

# Ejecutar migración
alembic upgrade heads

# Reiniciar servidor
sudo systemctl restart paquetex
# O si usas PM2:
pm2 restart paquetex
```

### 3. Verificaciones Post-Despliegue

- [ ] Servidor inicia sin errores
- [ ] Logs no muestran errores
- [ ] Página `/products` carga
- [ ] API `/api/products` responde
- [ ] Documentación API `/docs` muestra nuevos endpoints

---

## 🧪 Pruebas en Staging

### Pruebas Funcionales

- [ ] **Acceso a la interfaz**
  - Navegar a `https://staging.tudominio.com/products`
  - Verificar que carga sin errores
  - Verificar que muestra mensaje "No se encontraron productos"

- [ ] **Sincronización**
  - Click en botón "Sincronizar"
  - Confirmar acción
  - Esperar a que complete
  - Verificar mensaje de éxito
  - Verificar que aparecen productos

- [ ] **Búsqueda**
  - Escribir término de búsqueda
  - Verificar que filtra en tiempo real
  - Probar con diferentes términos

- [ ] **Filtros**
  - Probar filtro "Estado" (Activo/Inactivo)
  - Probar filtro "Vendible" (Sí/No)
  - Probar filtro "Destacado" (Sí/No)
  - Probar combinación de filtros

- [ ] **Paginación**
  - Verificar que muestra 50 productos por página
  - Click en "Siguiente"
  - Click en "Anterior"
  - Click en número de página específico
  - Verificar contador de productos

- [ ] **Configuración de Columnas**
  - Click en "Configurar Columnas"
  - Desmarcar algunas columnas
  - Reordenar con flechas
  - Guardar configuración
  - Verificar que se aplica
  - Recargar página y verificar que persiste

### Pruebas de API

```bash
# Listar productos
curl https://staging.tudominio.com/api/products

# Buscar productos
curl https://staging.tudominio.com/api/products?search=termo

# Ver detalle (reemplazar {id} con ID real)
curl https://staging.tudominio.com/api/products/1

# Sincronizar (requiere autenticación admin)
curl -X POST https://staging.tudominio.com/api/products/sync \
  -H "Authorization: Bearer TOKEN"

# Ver historial (requiere autenticación admin)
curl https://staging.tudominio.com/api/products/sync/history \
  -H "Authorization: Bearer TOKEN"
```

### Pruebas de Rendimiento

- [ ] Sincronizar catálogo completo
  - Medir tiempo de sincronización
  - Verificar que no hay timeouts
  - Verificar que no hay errores de memoria

- [ ] Cargar página con muchos productos
  - Verificar tiempo de carga < 3 segundos
  - Verificar que paginación funciona bien

- [ ] Búsqueda con muchos resultados
  - Verificar que responde rápido
  - Verificar que no hay lag

### Pruebas de Seguridad

- [ ] Acceso sin autenticación
  - Intentar acceder a `/products` sin login
  - Debe redirigir a login

- [ ] Sincronización sin permisos
  - Intentar sincronizar como usuario normal
  - Debe retornar error 403

- [ ] SQL Injection
  - Probar búsqueda con caracteres especiales
  - Verificar que no hay errores

---

## 📊 Métricas a Monitorear

### Durante Sincronización

- Tiempo de ejecución
- Cantidad de productos procesados
- Cantidad de errores
- Uso de CPU
- Uso de memoria
- Uso de base de datos

### Durante Uso Normal

- Tiempo de respuesta de API
- Tiempo de carga de página
- Cantidad de consultas a BD
- Errores en logs
- Uso de recursos

---

## 🐛 Problemas Comunes y Soluciones

### Error: "DATABASE_URL not found"

**Solución:**
```bash
# Verificar .env en servidor
cat .env | grep DATABASE_URL

# Si no existe, agregar
echo 'DATABASE_URL="postgresql://..."' >> .env
```

### Error: "DYNAMIA_TOKEN not found"

**Solución:**
```bash
# Agregar token de DynamiaERP
echo 'DYNAMIA_TOKEN="tu_token"' >> .env
echo 'DYNAMIA_API_URL="https://api.dynamiaerp.co"' >> .env
echo 'DYNAMIA_ACCOUNT_ID="128"' >> .env
```

### Error: "Table products does not exist"

**Solución:**
```bash
# Ejecutar migración
alembic upgrade heads
```

### Error: "Multiple head revisions"

**Solución:**
```bash
# Ejecutar todas las migraciones
alembic upgrade heads
```

### Sincronización muy lenta

**Causas:**
- Muchos productos (>1000)
- Conexión lenta a DynamiaERP
- Base de datos sin índices

**Solución:**
- Es normal con catálogos grandes
- Considerar sincronización nocturna
- Verificar índices en BD

### Página no carga

**Verificar:**
```bash
# Ver logs del servidor
tail -f /var/log/paquetex/error.log

# Verificar que el servidor está corriendo
systemctl status paquetex
# O
pm2 status

# Verificar que el template existe
ls -la src/templates/products/list.html
```

---

## ✅ Criterios de Aceptación

### Funcionalidad Mínima

- [x] Página `/products` carga correctamente
- [ ] Sincronización funciona sin errores
- [ ] Se muestran productos en la tabla
- [ ] Búsqueda funciona
- [ ] Filtros funcionan
- [ ] Paginación funciona
- [ ] Configuración de columnas se guarda

### Rendimiento

- [ ] Sincronización completa en < 5 minutos (para ~500 productos)
- [ ] Página carga en < 3 segundos
- [ ] API responde en < 1 segundo
- [ ] Búsqueda responde en < 500ms

### Estabilidad

- [ ] Sin errores en logs
- [ ] Sin memory leaks
- [ ] Sin timeouts
- [ ] Sin errores de base de datos

---

## 🎯 Despliegue a Producción

### Cuando Staging esté OK

1. **Crear tag de versión**
```bash
git tag -a v1.0.0-productos -m "Sistema de productos v1.0.0"
git push origin v1.0.0-productos
```

2. **Merge a main/master**
```bash
git checkout main
git merge staging
git push origin main
```

3. **Desplegar a producción**
```bash
# En servidor de producción
git pull origin main
alembic upgrade heads
sudo systemctl restart paquetex
```

4. **Verificar en producción**
- [ ] Página carga
- [ ] Sincronización funciona
- [ ] Todo funciona como en staging

5. **Monitorear por 24 horas**
- [ ] Revisar logs
- [ ] Revisar métricas
- [ ] Revisar reportes de usuarios

---

## 📝 Notas Finales

### Backup Antes de Desplegar

```bash
# Backup de base de datos
pg_dump -h host -U user -d dbname > backup_pre_productos_$(date +%Y%m%d).sql

# Backup de código
tar -czf backup_code_$(date +%Y%m%d).tar.gz /path/to/app
```

### Rollback Plan

Si algo sale mal:

```bash
# Revertir migración
alembic downgrade -1

# Revertir código
git revert HEAD
git push

# Restaurar backup
psql -h host -U user -d dbname < backup_pre_productos_YYYYMMDD.sql
```

### Comunicación

- [ ] Notificar al equipo antes de desplegar
- [ ] Notificar cuando esté en staging
- [ ] Notificar cuando esté en producción
- [ ] Documentar cualquier issue encontrado

---

## 📚 Recursos

- **Documentación completa:** `docs/PRODUCTOS_GUIA_USO.md`
- **Reporte de pruebas:** `docs/PRODUCTOS_REPORTE_PRUEBAS.md`
- **Plan de implementación:** `docs/PRODUCTOS_PLAN_IMPLEMENTACION.md`

---

**Preparado por:** Kiro AI  
**Fecha:** 2026-01-13  
**Estado:** ✅ Listo para desplegar
