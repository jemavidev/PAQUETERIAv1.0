# ✅ CHECKLIST DE VERIFICACIÓN RÁPIDA

**Proyecto:** Refactorización Sistema de Facturas de Proveedores  
**Fecha:** 19 de Enero, 2026  

---

## 🚀 ANTES DE DESPLEGAR

### Archivos Creados
- [ ] `CODE/src/app/services/enhanced_pdf_extractor.py` existe
- [ ] `CODE/alembic/versions/20260119_170057_add_extraction_quality.py` existe
- [ ] Archivos tienen sintaxis correcta (sin errores de Python)

### Archivos Modificados
- [ ] `CODE/src/app/services/supplier_invoice_service.py` actualizado
- [ ] `CODE/src/app/routes/invoices.py` con nuevos endpoints
- [ ] `CODE/src/templates/invoices/_tab_facturas.html` con columna de calidad
- [ ] `CODE/src/templates/invoices/dashboard.html` actualizado

### Git
- [ ] Todos los cambios commiteados
- [ ] Push a repositorio remoto
- [ ] Branch correcto (main/master)

---

## 🔧 DURANTE EL DESPLIEGUE

### Servidor
- [ ] SSH al servidor exitoso
- [ ] Pull de cambios completado
- [ ] Sin conflictos de merge

### Base de Datos
- [ ] Migración ejecutada: `alembic upgrade head`
- [ ] Sin errores en migración
- [ ] Campo `extraction_quality` existe en tabla

### Servicios
- [ ] Servicios reiniciados: `docker-compose restart web`
- [ ] Contenedores corriendo: `docker-compose ps`
- [ ] Sin errores en logs iniciales

---

## ✅ DESPUÉS DEL DESPLIEGUE

### Verificación Visual (5 min)

#### 1. Tabla Principal
- [ ] Abrir https://staging.jemavi.co/invoices
- [ ] Tab "Facturas" visible
- [ ] Columna "Calidad" presente
- [ ] Badges de calidad con colores (🟢🟡🔴)
- [ ] Botones de acción visibles (👁️ 📄 🗑️)

#### 2. Subir Factura Nueva
- [ ] Clic en "Subir PDFs"
- [ ] Modal se abre correctamente
- [ ] Seleccionar PDF de prueba
- [ ] Subir archivo
- [ ] Factura aparece en tabla
- [ ] Score de calidad visible

#### 3. Modal de Detalle
- [ ] Clic en botón "Ver" (👁️)
- [ ] Modal se abre
- [ ] Todos los campos visibles
- [ ] Score de calidad mostrado
- [ ] Botón "Re-extraer" presente

#### 4. Editar Factura
- [ ] Modificar campo "Proveedor"
- [ ] Clic en "Guardar Cambios"
- [ ] Modal se cierra
- [ ] Cambio reflejado en tabla

#### 5. Re-extraer Datos
- [ ] Abrir factura con baja calidad
- [ ] Clic en "🔄 Re-extraer"
- [ ] Confirmar acción
- [ ] Mensaje de éxito
- [ ] Calidad mejorada

#### 6. Ver PDF
- [ ] Clic en botón "PDF" (📄)
- [ ] PDF se abre en nueva pestaña
- [ ] PDF se visualiza correctamente

#### 7. Eliminar Factura
- [ ] Clic en botón "Eliminar" (🗑️)
- [ ] Confirmación aparece
- [ ] Confirmar eliminación
- [ ] Factura desaparece de tabla

### Verificación Técnica (10 min)

#### Base de Datos
```bash
# Conectar a BD
docker-compose exec db psql -U postgres -d paquetex

# Verificar campo
\d supplier_invoices
# Debe mostrar: extraction_quality | double precision

# Verificar datos
SELECT id, supplier_name, extraction_quality 
FROM supplier_invoices 
ORDER BY uploaded_at DESC 
LIMIT 5;
# Debe mostrar valores entre 0.0 y 1.0

\q
```
- [ ] Campo `extraction_quality` existe
- [ ] Valores entre 0.0 y 1.0
- [ ] Sin errores en queries

#### Logs del Servidor
```bash
# Ver logs recientes
docker-compose logs --tail=100 web

# Buscar errores
docker-compose logs web | grep -i "error\|exception" | tail -20
```
- [ ] Sin errores críticos
- [ ] Sin excepciones no manejadas
- [ ] Extractor mejorado funcionando

#### Endpoints API
```bash
# Probar endpoint de detalle
curl -s https://staging.jemavi.co/invoices/api/supplier-invoices/1/detail | jq

# Probar endpoint de lista
curl -s https://staging.jemavi.co/invoices/api/supplier-invoices/list | jq '.invoices[0]'
```
- [ ] Endpoint `/detail` responde
- [ ] Endpoint `/list` incluye `extraction_quality`
- [ ] JSON válido retornado

### Verificación de Performance (5 min)

#### Tiempos de Carga
- [ ] Tabla carga en <2 segundos
- [ ] Modal se abre en <500ms
- [ ] Re-extracción completa en <5 segundos
- [ ] PDF se abre en <2 segundos

#### Uso de Recursos
```bash
# Ver uso de CPU/Memoria
docker stats --no-stream
```
- [ ] CPU <80%
- [ ] Memoria <80%
- [ ] Sin memory leaks

---

## 📊 VERIFICACIÓN DE CALIDAD (15 min)

### Probar con Facturas Reales

#### Factura de EXITO
- [ ] Subir factura de EXITO
- [ ] Proveedor detectado correctamente
- [ ] NIT correcto (890900608)
- [ ] Calidad >80%

#### Factura de MAKRO
- [ ] Subir factura de MAKRO
- [ ] Proveedor detectado correctamente
- [ ] NIT correcto (890903407)
- [ ] Calidad >80%

#### Factura Desconocida
- [ ] Subir factura de proveedor no conocido
- [ ] Datos extraídos (aunque sea parcialmente)
- [ ] Calidad calculada
- [ ] Re-extracción funciona

### Casos Edge

#### Factura Sin CUFE
- [ ] Subir factura sin CUFE
- [ ] Estado "Sin CUFE"
- [ ] Otros datos extraídos
- [ ] Se puede agregar CUFE manualmente

#### Factura Corrupta
- [ ] Intentar subir PDF corrupto
- [ ] Error manejado correctamente
- [ ] Mensaje de error claro
- [ ] No rompe el sistema

#### Factura Duplicada
- [ ] Subir misma factura dos veces
- [ ] Detecta duplicado
- [ ] Mensaje de advertencia
- [ ] No crea registro duplicado

---

## 🐛 PROBLEMAS COMUNES

### Problema: Campo extraction_quality no existe
**Verificar:**
```bash
docker-compose exec web alembic current
docker-compose exec web alembic upgrade head
```
- [ ] Migración ejecutada
- [ ] Campo creado

### Problema: Modal no se abre
**Verificar:**
- [ ] Console del navegador sin errores
- [ ] Función `viewInvoiceDetail` definida
- [ ] Cache del navegador limpio (Ctrl+Shift+R)

### Problema: Botones no funcionan
**Verificar:**
- [ ] JavaScript cargado correctamente
- [ ] Funciones definidas en `_tab_facturas.html`
- [ ] Sin errores en console

### Problema: Calidad siempre 0.0
**Verificar:**
```bash
docker-compose logs web | grep "enhanced_extractor"
```
- [ ] Extractor mejorado se está usando
- [ ] Sin errores en extracción
- [ ] Fallback a extractor básico si falla

---

## 📈 MÉTRICAS A MONITOREAR

### Primeras 24 Horas
- [ ] Tasa de extracción exitosa >80%
- [ ] Calidad promedio >0.70
- [ ] Sin errores críticos en logs
- [ ] Usuarios pueden usar el sistema

### Primera Semana
- [ ] Feedback de usuarios positivo
- [ ] Tiempo de corrección reducido
- [ ] Re-extracción usada cuando necesario
- [ ] Sin quejas de performance

---

## ✅ CONFIRMACIÓN FINAL

### Funcionalidad
- [ ] Todas las verificaciones visuales pasadas
- [ ] Todas las verificaciones técnicas pasadas
- [ ] Todas las verificaciones de calidad pasadas
- [ ] Sin problemas críticos

### Documentación
- [ ] Usuarios notificados de cambios
- [ ] Documentación actualizada
- [ ] Equipo informado

### Rollback Plan
- [ ] Comando de rollback preparado
- [ ] Backup de BD reciente
- [ ] Equipo disponible para soporte

---

## 🎉 SISTEMA VERIFICADO

Si todas las casillas están marcadas:

✅ **El sistema está funcionando correctamente**  
✅ **Listo para uso en producción**  
✅ **Monitorear durante 48 horas**  

---

**Verificado por:** _______________  
**Fecha:** _______________  
**Hora:** _______________  
**Ambiente:** [ ] Staging [ ] Producción  
**Estado:** [ ] ✅ Aprobado [ ] ⚠️ Con observaciones [ ] ❌ Rechazado  

**Observaciones:**
```
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

**Preparado por:** Kiro AI  
**Fecha:** 19 de Enero, 2026
