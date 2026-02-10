# Instrucciones de Despliegue - Conteo de Productos

## Resumen de Cambios

Se ha implementado la funcionalidad para mostrar la cantidad de productos en la columna "Estado" de los tabs FACTURAS y CUFE, específicamente para facturas con estado **"Completo"** y **"Validado"**.

## Archivos Modificados

### Backend
- `CODE/src/app/routes/invoices_v2_routes.py`
  - Schema `InvoiceResponse` actualizado con campo `productos_count`
  - Endpoint `/api/v2/invoices/facturas` modificado para incluir conteo

### Frontend
- `CODE/src/templates/invoices_v2/facturas.html`
  - Función `renderInvoiceRow()` actualizada
- `CODE/src/templates/invoices_v2/cufe.html`
  - Función `renderCufeRow()` actualizada

## Pasos para Despliegue

### 1. Verificar Cambios Localmente

```bash
# Ejecutar script de verificación
./VERIFICAR_CAMBIOS_PRODUCTOS_COUNT.sh
```

**Resultado esperado**: Todos los checks deben mostrar ✓

### 2. Probar en Desarrollo

```bash
# Ir al directorio del código
cd CODE

# Activar entorno virtual (si aplica)
source .venv/bin/activate

# Reiniciar servidor
./start_server.sh
```

### 3. Verificar en Navegador

1. Abrir: `http://localhost:8000/invoices/facturas`
2. Verificar que facturas con estado "Completo" muestren: `🟢 X prod.`
3. Abrir: `http://localhost:8000/invoices/cufe`
4. Verificar que facturas validadas muestren: `🟢 X prod.`
5. Verificar que otros estados solo muestren el círculo de color

### 4. Pruebas Funcionales

#### Test 1: Facturas con Productos
```
✓ Facturas con estado "completo" muestran conteo
✓ Facturas con estado "validado" muestran conteo
✓ El número de productos es correcto
✓ El tooltip muestra información completa
```

#### Test 2: Facturas sin Productos
```
✓ Facturas con estado "pendiente_dian" NO muestran conteo
✓ Facturas con estado "error" NO muestran conteo
✓ Facturas con estado "sin_dian" NO muestran conteo
```

#### Test 3: Rendimiento
```
✓ La página carga en menos de 2 segundos
✓ La paginación funciona correctamente
✓ La búsqueda no se ve afectada
```

### 5. Despliegue a Staging

```bash
# Commit de cambios
git add CODE/src/app/routes/invoices_v2_routes.py
git add CODE/src/templates/invoices_v2/facturas.html
git add CODE/src/templates/invoices_v2/cufe.html
git add CONTEO_PRODUCTOS_IMPLEMENTADO.md
git add EJEMPLO_VISUAL_CONTEO_PRODUCTOS.md
git add INSTRUCCIONES_DESPLIEGUE_CONTEO_PRODUCTOS.md

git commit -m "feat: Agregar conteo de productos en columna Estado para facturas completas/validadas

- Backend: Agregar campo productos_count a InvoiceResponse
- Backend: Implementar lógica de conteo optimizada en endpoint /facturas
- Frontend: Actualizar renderInvoiceRow() en facturas.html
- Frontend: Actualizar renderCufeRow() en cufe.html
- Docs: Agregar documentación completa de la funcionalidad

El conteo solo se muestra para facturas con estado 'completo' o 'validado',
basándose en los productos extraídos del archivo DIAN/CUFE."

# Push a staging
git push origin staging
```

### 6. Despliegue a Producción

```bash
# Merge a main/master
git checkout main
git merge staging

# Push a producción
git push origin main

# Desplegar (según tu proceso)
./deploy.sh production
# O
docker-compose up -d --build
```

## Rollback (si es necesario)

### Opción 1: Revertir Commit
```bash
git revert HEAD
git push origin main
```

### Opción 2: Desactivar Funcionalidad

Modificar `CODE/src/app/routes/invoices_v2_routes.py`:

```python
# Comentar la lógica de conteo
# cufes_to_count = [inv.cufe for inv in invoices if inv.estado in ['completo', 'validado']]
# ... resto del código de conteo ...

# Siempre devolver None
invoice_dict['productos_count'] = None
```

## Monitoreo Post-Despliegue

### Métricas a Vigilar

1. **Tiempo de respuesta del endpoint `/api/v2/invoices/facturas`**
   - Antes: ~200-300ms
   - Después: ~250-350ms (aumento esperado: +50ms)
   - Alerta si: >500ms

2. **Uso de CPU**
   - Aumento esperado: <5%
   - Alerta si: >10%

3. **Uso de memoria**
   - Aumento esperado: <10MB
   - Alerta si: >50MB

4. **Errores en logs**
   - Buscar: "productos_count", "InvoiceProductV2"
   - Alerta si: >5 errores/hora

### Queries de Monitoreo

```sql
-- Verificar conteo de productos por factura
SELECT 
    i.cufe,
    i.estado,
    i.proveedor_nombre,
    COUNT(p.id) as productos_count
FROM invoices_v2 i
LEFT JOIN invoice_products_v2 p ON i.cufe = p.cufe
WHERE i.estado IN ('completo', 'validado')
GROUP BY i.cufe, i.estado, i.proveedor_nombre
ORDER BY i.created_at DESC
LIMIT 20;

-- Verificar facturas sin productos (posibles errores)
SELECT 
    i.cufe,
    i.estado,
    i.proveedor_nombre,
    i.fecha_emision,
    COUNT(p.id) as productos_count
FROM invoices_v2 i
LEFT JOIN invoice_products_v2 p ON i.cufe = p.cufe
WHERE i.estado IN ('completo', 'validado')
GROUP BY i.cufe, i.estado, i.proveedor_nombre, i.fecha_emision
HAVING COUNT(p.id) = 0
ORDER BY i.created_at DESC;
```

## Troubleshooting

### Problema 1: No se muestra el conteo

**Síntomas**: La columna Estado solo muestra el círculo de color

**Solución**:
1. Verificar que el estado sea 'completo' o 'validado'
2. Verificar en la consola del navegador si `productos_count` está en la respuesta
3. Verificar logs del servidor para errores en la query de conteo

```bash
# Ver logs
tail -f CODE/logs/app.log | grep productos_count
```

### Problema 2: Conteo incorrecto

**Síntomas**: El número de productos no coincide con la realidad

**Solución**:
1. Verificar en la base de datos:
```sql
SELECT COUNT(*) FROM invoice_products_v2 WHERE cufe = 'CUFE_AQUI';
```
2. Verificar que no haya productos duplicados
3. Reprocesar la factura si es necesario

### Problema 3: Rendimiento lento

**Síntomas**: La página tarda más de 2 segundos en cargar

**Solución**:
1. Verificar índices en la base de datos:
```sql
-- Debe existir índice en cufe
SHOW INDEX FROM invoice_products_v2 WHERE Key_name LIKE '%cufe%';
```
2. Optimizar query si es necesario
3. Considerar caché de conteos

### Problema 4: Error 500 en el endpoint

**Síntomas**: Error al cargar la lista de facturas

**Solución**:
1. Verificar logs del servidor
2. Verificar que la tabla `invoice_products_v2` existe
3. Verificar permisos de la base de datos

```bash
# Ver error completo
tail -n 100 CODE/logs/app.log | grep ERROR
```

## Checklist de Despliegue

### Pre-Despliegue
- [ ] Código revisado y probado localmente
- [ ] Tests pasando (si aplica)
- [ ] Documentación actualizada
- [ ] Backup de base de datos realizado
- [ ] Plan de rollback definido

### Durante Despliegue
- [ ] Servidor en modo mantenimiento (opcional)
- [ ] Código desplegado
- [ ] Servidor reiniciado
- [ ] Verificación básica funcionando

### Post-Despliegue
- [ ] Verificar tabs FACTURAS y CUFE
- [ ] Verificar conteo de productos
- [ ] Verificar rendimiento
- [ ] Verificar logs sin errores
- [ ] Notificar a usuarios (si aplica)

## Contacto y Soporte

Si encuentras algún problema durante el despliegue:

1. Revisar esta documentación
2. Revisar logs del servidor
3. Consultar `CONTEO_PRODUCTOS_IMPLEMENTADO.md` para detalles técnicos
4. Ejecutar `./VERIFICAR_CAMBIOS_PRODUCTOS_COUNT.sh` para diagnóstico

---

**Fecha**: 2026-02-10
**Versión**: 1.0
**Estado**: ✅ Listo para Despliegue
