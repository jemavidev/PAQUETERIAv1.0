# 🚀 INSTRUCCIONES DE DESPLIEGUE - Refactorización Facturas

**Fecha:** 19 de Enero, 2026  
**Proyecto:** PAQUETEX - Sistema de Gestión de Facturas  

---

## ✅ ARCHIVOS LISTOS PARA DESPLEGAR

### Nuevos Archivos
```
CODE/src/app/services/enhanced_pdf_extractor.py
CODE/alembic/versions/20260119_170057_add_extraction_quality.py
CODE/test_refactorizacion.py
ANALISIS_REFACTORIZACION_FACTURAS_PROVEEDORES.md
REFACTORIZACION_COMPLETADA.md
INSTRUCCIONES_DESPLIEGUE_REFACTORIZACION.md (este archivo)
```

### Archivos Modificados
```
CODE/src/app/services/supplier_invoice_service.py
CODE/src/app/routes/invoices.py
CODE/src/templates/invoices/_tab_facturas.html
CODE/src/templates/invoices/dashboard.html
```

---

## 📋 PASOS DE DESPLIEGUE

### 1. Verificar Archivos (Local)

```bash
# Verificar que los archivos existen
ls -la CODE/src/app/services/enhanced_pdf_extractor.py
ls -la CODE/alembic/versions/20260119_170057_add_extraction_quality.py

# Verificar sintaxis Python
cd CODE
python3 -m py_compile src/app/services/enhanced_pdf_extractor.py
python3 -m py_compile src/app/services/supplier_invoice_service.py
```

### 2. Commit y Push a Git

```bash
# Agregar archivos
git add CODE/src/app/services/enhanced_pdf_extractor.py
git add CODE/alembic/versions/20260119_170057_add_extraction_quality.py
git add CODE/src/app/services/supplier_invoice_service.py
git add CODE/src/app/routes/invoices.py
git add CODE/src/templates/invoices/_tab_facturas.html
git add CODE/src/templates/invoices/dashboard.html
git add ANALISIS_REFACTORIZACION_FACTURAS_PROVEEDORES.md
git add REFACTORIZACION_COMPLETADA.md
git add INSTRUCCIONES_DESPLIEGUE_REFACTORIZACION.md

# Commit
git commit -m "feat: Refactorización completa sistema facturas proveedores

- Extractor mejorado con scores de confianza
- Columna de calidad en tabla
- Modal de detalle con edición
- Acciones funcionales (ver, editar, re-extraer, eliminar)
- API mejorada con nuevos endpoints
- Migración para campo extraction_quality"

# Push
git push origin main
```

### 3. Desplegar en Staging

```bash
# SSH a servidor staging
ssh usuario@staging.jemavi.co

# Ir al directorio del proyecto
cd /ruta/al/proyecto

# Pull cambios
git pull origin main

# Ejecutar migración de BD
cd CODE
docker-compose exec web alembic upgrade head

# Reiniciar servicios
docker-compose restart web

# Verificar logs
docker-compose logs -f web | grep "enhanced"
```

### 4. Verificar en Staging

1. **Abrir navegador:**
   ```
   https://staging.jemavi.co/invoices
   ```

2. **Verificar tabla:**
   - ✅ Columna "Calidad" visible
   - ✅ Badges de calidad con colores (🟢🟡🔴)
   - ✅ Botones de acción funcionando

3. **Probar subida de factura:**
   - Clic en "Subir PDFs"
   - Seleccionar un PDF de prueba
   - Subir
   - Verificar que aparece con score de calidad

4. **Probar modal de detalle:**
   - Clic en botón "Ver" (👁️) de una factura
   - Verificar que se abre modal
   - Verificar que muestra todos los campos
   - Verificar que muestra score de calidad
   - Probar editar un campo
   - Guardar cambios
   - Verificar que se actualiza en tabla

5. **Probar re-extracción:**
   - Abrir factura con baja calidad
   - Clic en "🔄 Re-extraer"
   - Verificar que mejora la calidad

6. **Probar PDF:**
   - Clic en botón "PDF" (📄)
   - Verificar que se abre en nueva pestaña

7. **Probar eliminar:**
   - Clic en botón "Eliminar" (🗑️)
   - Confirmar
   - Verificar que desaparece de tabla

### 5. Verificar Base de Datos

```bash
# Conectar a BD
docker-compose exec db psql -U postgres -d paquetex

# Verificar que el campo existe
\d supplier_invoices

# Debería mostrar:
# extraction_quality | double precision | | |

# Verificar datos
SELECT id, supplier_name, extraction_quality 
FROM supplier_invoices 
ORDER BY uploaded_at DESC 
LIMIT 5;

# Salir
\q
```

### 6. Monitorear Logs

```bash
# Ver logs en tiempo real
docker-compose logs -f web

# Buscar errores relacionados con extractor
docker-compose logs web | grep -i "enhanced\|extraction"

# Buscar errores en general
docker-compose logs web | grep -i "error\|exception"
```

---

## 🐛 TROUBLESHOOTING

### Problema 1: Campo extraction_quality no existe

**Síntoma:**
```
sqlalchemy.exc.ProgrammingError: column "extraction_quality" does not exist
```

**Solución:**
```bash
cd CODE
docker-compose exec web alembic upgrade head
docker-compose restart web
```

### Problema 2: Extractor mejorado no funciona

**Síntoma:**
- Facturas se suben pero calidad siempre es 0.0
- Logs muestran: "Error en extractor mejorado, usando básico"

**Solución:**
```bash
# Verificar que el archivo existe
docker-compose exec web ls -la /app/src/app/services/enhanced_pdf_extractor.py

# Verificar sintaxis
docker-compose exec web python -m py_compile /app/src/app/services/enhanced_pdf_extractor.py

# Reiniciar
docker-compose restart web
```

### Problema 3: Modal no se abre

**Síntoma:**
- Clic en botón "Ver" no hace nada
- Console del navegador muestra error

**Solución:**
```bash
# Verificar que el JavaScript está en el archivo correcto
grep -n "viewInvoiceDetail" CODE/src/templates/invoices/_tab_facturas.html

# Limpiar cache del navegador
# Ctrl + Shift + R (Chrome/Firefox)

# Verificar que el template se actualizó
docker-compose exec web cat /app/src/templates/invoices/_tab_facturas.html | grep "viewInvoiceDetail"
```

### Problema 4: Botones de acción no funcionan

**Síntoma:**
- Clic en botones no hace nada
- Console muestra: "function not defined"

**Solución:**
```bash
# Verificar que las funciones están definidas
grep -n "function viewPdf" CODE/src/templates/invoices/_tab_facturas.html
grep -n "function deleteInvoice" CODE/src/templates/invoices/_tab_facturas.html
grep -n "function copyCufe" CODE/src/templates/invoices/_tab_facturas.html

# Limpiar cache y recargar
```

### Problema 5: API endpoints no responden

**Síntoma:**
```
404 Not Found: /invoices/api/supplier-invoices/123/detail
```

**Solución:**
```bash
# Verificar que los endpoints están en el archivo
grep -n "@router.get.*supplier-invoices.*detail" CODE/src/app/routes/invoices.py

# Reiniciar servidor
docker-compose restart web

# Verificar rutas registradas
docker-compose exec web python -c "
from app.main import app
for route in app.routes:
    if hasattr(route, 'path'):
        print(route.path)
" | grep supplier-invoices
```

---

## ✅ CHECKLIST DE VERIFICACIÓN POST-DESPLIEGUE

### Backend
- [ ] Migración ejecutada correctamente
- [ ] Campo extraction_quality existe en BD
- [ ] Extractor mejorado funciona
- [ ] Nuevos endpoints responden
- [ ] Logs sin errores críticos

### Frontend
- [ ] Columna de calidad visible
- [ ] Badges de calidad con colores correctos
- [ ] Modal de detalle se abre
- [ ] Campos editables funcionan
- [ ] Botón "Re-extraer" funciona
- [ ] Botón "Ver PDF" funciona
- [ ] Botón "Eliminar" funciona
- [ ] Botón "Copiar CUFE" funciona

### Funcionalidad
- [ ] Subir nueva factura funciona
- [ ] Calidad se calcula correctamente
- [ ] Editar factura guarda cambios
- [ ] Re-extraer mejora calidad
- [ ] Eliminar factura funciona
- [ ] Ver PDF funciona

### Performance
- [ ] Carga de tabla rápida (<2s)
- [ ] Modal se abre rápido (<500ms)
- [ ] Re-extracción completa en <5s
- [ ] Sin memory leaks

---

## 📊 MÉTRICAS A MONITOREAR

### Primeras 24 horas

1. **Tasa de extracción exitosa:**
   ```sql
   SELECT 
     COUNT(*) as total,
     COUNT(CASE WHEN extraction_quality >= 0.8 THEN 1 END) as alta_calidad,
     COUNT(CASE WHEN extraction_quality >= 0.5 AND extraction_quality < 0.8 THEN 1 END) as media_calidad,
     COUNT(CASE WHEN extraction_quality < 0.5 THEN 1 END) as baja_calidad
   FROM supplier_invoices
   WHERE uploaded_at >= NOW() - INTERVAL '24 hours';
   ```

2. **Campos más problemáticos:**
   ```sql
   SELECT 
     COUNT(CASE WHEN supplier_name IS NULL THEN 1 END) as sin_proveedor,
     COUNT(CASE WHEN invoice_date IS NULL THEN 1 END) as sin_fecha,
     COUNT(CASE WHEN invoice_number IS NULL THEN 1 END) as sin_numero,
     COUNT(CASE WHEN cufe IS NULL THEN 1 END) as sin_cufe
   FROM supplier_invoices
   WHERE uploaded_at >= NOW() - INTERVAL '24 hours';
   ```

3. **Uso de re-extracción:**
   - Monitorear logs para ver cuántas veces se usa
   - Verificar si mejora la calidad

### Primera semana

1. **Comparar con sistema anterior:**
   - Tasa de extracción exitosa: antes ~60%, objetivo >85%
   - Datos completos: antes ~40%, objetivo >70%
   - Tiempo de corrección: antes ~5min, objetivo <2min

2. **Feedback de usuarios:**
   - ¿Encuentran útil el indicador de calidad?
   - ¿Usan la función de re-extracción?
   - ¿Hay proveedores que necesitan patrones específicos?

---

## 🎯 PRÓXIMOS PASOS

### Inmediato (Esta semana)

1. **Monitorear en staging** durante 2-3 días
2. **Recopilar feedback** de usuarios
3. **Ajustar patrones** si es necesario
4. **Agregar más proveedores** a la biblioteca

### Corto plazo (Próximas 2 semanas)

1. **Desplegar a producción** si staging funciona bien
2. **Analizar facturas existentes** en carpeta de Google Drive
3. **Optimizar patrones** basados en datos reales
4. **Crear tests automatizados**

### Mediano plazo (Próximo mes)

1. **Dashboard de métricas** de calidad
2. **Aprendizaje automático** de patrones
3. **Integración con DIAN** para descarga automática
4. **Procesamiento en background** para lotes grandes

---

## 📞 SOPORTE

Si encuentras problemas durante el despliegue:

1. **Revisar logs:**
   ```bash
   docker-compose logs -f web | grep -i "error\|exception"
   ```

2. **Verificar estado de servicios:**
   ```bash
   docker-compose ps
   ```

3. **Rollback si es necesario:**
   ```bash
   git revert HEAD
   git push origin main
   docker-compose restart web
   ```

4. **Contactar al equipo de desarrollo**

---

## ✅ CONFIRMACIÓN DE DESPLIEGUE

Una vez completado el despliegue, confirmar:

- [ ] Todos los pasos ejecutados
- [ ] Todas las verificaciones pasadas
- [ ] Métricas monitoreadas
- [ ] Usuarios notificados de nuevas funcionalidades
- [ ] Documentación actualizada

**Fecha de despliegue:** _______________  
**Desplegado por:** _______________  
**Ambiente:** [ ] Staging [ ] Producción  
**Estado:** [ ] Exitoso [ ] Con problemas [ ] Rollback  

---

**Preparado por:** Kiro AI  
**Fecha:** 19 de Enero, 2026  
**Versión:** 1.0
