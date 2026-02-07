# 🚀 INSTRUCCIONES RÁPIDAS - Fix Emisor/Adquiriente

## ⚡ Ejecución Rápida

```bash
# 1. Ejecutar el script de corrección
./fix_emisor_adquiriente.sh

# 2. Confirmar cuando se solicite
# El script mostrará cuántas facturas se van a reprocesar

# 3. Esperar a que termine
# Verás el progreso en tiempo real

# 4. Verificar en la interfaz web
# Tab CUFE → Verificar que los proveedores sean correctos
```

## ✅ Lo que hace el script

1. **Descarga** archivos DIAN desde S3
2. **Re-extrae** datos con la lógica corregida
3. **Actualiza** la base de datos
4. **Reporta** cambios realizados

## 🎯 Resultado Esperado

**Antes:**
- Proveedor: PAPYRUS SOLUCIONES INTEGRALES S.A.S. ❌

**Después:**
- Proveedor: VENEPLAST LTDA ✅
- Cliente: PAPYRUS SOLUCIONES INTEGRALES S.A.S. ✅

## 📊 Cambios Realizados

### 1. Modal de Carga DIAN (Tab CUFE)
- ✅ Diseño drag & drop moderno
- ✅ Menos texto, más visual
- ✅ Animaciones al arrastrar archivos
- ✅ Lista de archivos con opción de eliminar

### 2. Botón Limpiar Búsqueda (Ambos tabs)
- ✅ Botón X dentro del campo de búsqueda
- ✅ Aparece solo cuando hay texto
- ✅ Un clic limpia y recarga

### 3. Fix Emisor/Adquiriente
- ✅ Código corregido en `pdf_parser_service.py`
- ✅ Script de corrección masiva creado
- ✅ Test ejecutado exitosamente

## 🔍 Verificación

```bash
# Ejecutar test (opcional)
python3 test_regex_emisor_adquiriente.py

# Debe mostrar:
# ✅ EMISOR: VENEPLAST LTDA
# ✅ ADQUIRIENTE: PAPYRUS SOLUCIONES INTEGRALES S.A.S.
```

## ⚠️ Importante

- El script necesita acceso a S3
- Hace backup automático por factura (rollback si falla)
- Tiempo estimado: 2-5 segundos por factura

## 📝 Archivos Modificados

1. `CODE/src/app/services/pdf_parser_service.py` - Lógica corregida
2. `CODE/src/templates/invoices_v2/cufe.html` - Modal drag & drop + botón X
3. `CODE/src/templates/invoices_v2/facturas.html` - Botón X

## 🎉 ¡Listo!

Después de ejecutar el script, todos los datos estarán correctos y las nuevas cargas funcionarán perfectamente.
