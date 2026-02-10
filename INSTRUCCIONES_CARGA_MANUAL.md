# INSTRUCCIONES: Carga Manual de PDFs

## ✅ ARCHIVOS PREPARADOS

He copiado los 183 archivos PDF a una ubicación accesible:

**Ubicación**: `CODE/uploads/facturas_para_cargar/`

---

## 🚀 OPCIÓN 1: Interfaz de Carga Masiva (RECOMENDADO)

### Paso 1: Abrir la interfaz
Abre en tu navegador:
```
http://localhost:8000/static/carga_masiva_facturas.html
```

O abre directamente el archivo:
```
file:///home/stk/Documents/GIT/PAQUETEX v1.0/CODE/carga_masiva_facturas.html
```

### Paso 2: Seleccionar archivos
1. Click en "📁 Seleccionar PDFs"
2. Navega a: `CODE/uploads/facturas_para_cargar/`
3. Selecciona TODOS los archivos (Ctrl+A)
4. Click en "Abrir"

### Paso 3: Cargar
1. Verifica que aparecen los 183 archivos
2. Click en "⬆️ Cargar 183 archivos"
3. Espera a que termine (10-15 minutos)
4. Revisa el resumen final

### Ventajas:
- ✅ Carga múltiples archivos a la vez
- ✅ Muestra progreso en tiempo real
- ✅ Lista de éxitos y errores
- ✅ No requiere línea de comandos

---

## 🚀 OPCIÓN 2: Interfaz Web del Sistema

### Paso 1: Ir al tab de Facturas
```
http://localhost:8000/invoices/facturas
```

### Paso 2: Cargar archivos
1. Click en el botón "+" (Cargar factura)
2. Selecciona múltiples PDFs de `CODE/uploads/facturas_para_cargar/`
3. Carga en lotes de 10-20 archivos
4. Repite hasta cargar todos

### Nota:
- Puede ser más lento
- Requiere cargar en lotes
- Pero es la interfaz oficial del sistema

---

## 🚀 OPCIÓN 3: Drag & Drop (Si está disponible)

Si el sistema tiene drag & drop:

1. Abre el navegador de archivos
2. Navega a `CODE/uploads/facturas_para_cargar/`
3. Selecciona todos los PDFs (Ctrl+A)
4. Arrastra y suelta en la zona de carga del navegador

---

## 📁 UBICACIÓN DE LOS ARCHIVOS

```
/home/stk/Documents/GIT/PAQUETEX v1.0/CODE/uploads/facturas_para_cargar/

Contiene:
- 183 archivos PDF
- Copiados desde CUFE/CUFE-XML/
- Listos para cargar
```

### Verificar archivos:
```bash
ls CODE/uploads/facturas_para_cargar/ | wc -l
# Debe mostrar: 183
```

---

## ⏱️ TIEMPO ESTIMADO

- **Por archivo**: 2-3 segundos
- **Total (183 archivos)**: 10-15 minutos
- **En lotes de 20**: ~1 minuto por lote (9 lotes)

---

## 📊 QUÉ ESPERAR

### Durante la carga:
- Barra de progreso
- Contador de archivos procesados
- Lista de éxitos (verde) y errores (rojo)

### Después de la carga:
- Facturas aparecen en el tab FACTURAS
- Estado inicial: "pendiente_dian"
- CUFE extraído o temporal generado
- Archivos subidos a S3

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Error: "No autenticado"
- Asegúrate de estar logueado en el sistema
- Refresca la página e intenta de nuevo

### Error: "CUFE duplicado"
- Normal si ya cargaste algunos archivos
- El sistema no permite duplicados
- Continúa con los demás archivos

### Error: "Timeout"
- Algunos PDFs pueden tardar más
- Intenta cargarlos individualmente después

### Carga muy lenta
- Carga en lotes más pequeños (10 archivos)
- Verifica conexión a internet (para S3)
- Verifica que el servidor no esté sobrecargado

---

## ✅ VERIFICACIÓN POST-CARGA

### En el navegador:
1. Ir a http://localhost:8000/invoices/facturas
2. Verificar que aparecen las facturas
3. Revisar que los datos se extrajeron

### Estadísticas:
```
http://localhost:8000/api/v2/invoices/statistics
```

Debe mostrar:
```json
{
  "total_facturas": 183,
  "facturas_completas": 0,
  "facturas_pendientes": 183,
  "total_productos": 0
}
```

---

## 🎯 PRÓXIMOS PASOS

Después de cargar los PDFs:

1. **Cargar archivos DIAN (XML)**
   - Ir al tab CUFE
   - Cargar los archivos XML correspondientes
   - Ubicación: `CUFE/CUFE-XML/*.xml`

2. **Validar datos**
   - Revisar facturas con advertencias
   - Corregir campos problemáticos

3. **Verificar productos**
   - Ir al tab PRODUCTOS
   - Verificar extracción correcta

---

## 📝 ARCHIVOS CREADOS

1. **CODE/uploads/facturas_para_cargar/** - Carpeta con 183 PDFs
2. **CODE/carga_masiva_facturas.html** - Interfaz de carga masiva
3. **INSTRUCCIONES_CARGA_MANUAL.md** - Este documento

---

## 💡 RECOMENDACIÓN

**Usa la OPCIÓN 1** (Interfaz de carga masiva):
- Más rápida
- Mejor feedback visual
- Manejo automático de errores
- Resumen detallado

---

**Fecha**: 10 de Febrero de 2026  
**Archivos preparados**: 183 PDFs  
**Ubicación**: `CODE/uploads/facturas_para_cargar/`  
**Listo para cargar**: ✅
