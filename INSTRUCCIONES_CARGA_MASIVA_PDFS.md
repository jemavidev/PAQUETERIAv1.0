# INSTRUCCIONES: Carga Masiva de PDFs

## 📋 OBJETIVO

Cargar los 183 archivos PDF de `/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML` en el tab de Facturas.

---

## 🚀 OPCIÓN 1: Script Python (RECOMENDADO)

### Requisitos previos:
1. Servidor corriendo en `http://localhost:8000`
2. Credenciales de usuario

### Ejecutar:

```bash
python3 cargar_pdfs_facturas_v2.py
```

### Proceso:
1. Verifica conexión al servidor
2. Solicita usuario y contraseña
3. Autentica en el sistema
4. Carga los 183 PDFs uno por uno
5. Muestra progreso en tiempo real
6. Genera resumen final

### Ventajas:
- ✅ Manejo robusto de errores
- ✅ Autenticación automática
- ✅ Progreso detallado
- ✅ Resumen con estadísticas

---

## 🚀 OPCIÓN 2: Script Bash (ALTERNATIVA)

### Ejecutar:

```bash
./cargar_pdfs_facturas_simple.sh
```

### Nota:
- Requiere tener una sesión activa en el navegador
- Usa curl directamente
- Más simple pero menos robusto

---

## 📊 QUÉ ESPERAR

### Durante la carga:
```
[1/183] Procesando: archivo1.pdf
   ✅ Cargado exitosamente
   📋 CUFE: a1b2c3d4e5f6...
   🏢 Proveedor: ALMACEN VENEPLAST SAS
   📊 Estado: pendiente_dian

[2/183] Procesando: archivo2.pdf
   ✅ Cargado exitosamente
   ...
```

### Resumen final:
```
📊 RESUMEN DE CARGA
   Total archivos: 183
   ✅ Exitosos: 180
   ❌ Fallidos: 3
   📈 Tasa de éxito: 98.4%
```

---

## ⏱️ TIEMPO ESTIMADO

- **Por archivo**: ~2-3 segundos
- **Total (183 archivos)**: ~10-15 minutos

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Error: "No se puede conectar al servidor"
```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000/

# Si no responde, iniciar el servidor
cd CODE
./start_server.sh
```

### Error: "Credenciales incorrectas"
- Verifica usuario y contraseña
- Asegúrate de tener permisos de administrador

### Error: "Timeout"
- Algunos PDFs pueden tardar más
- El script continúa con el siguiente archivo
- Se reportan en el resumen final

### Error: "CUFE duplicado"
- El sistema no permite CUFEs duplicados
- Si un PDF ya fue cargado, se reporta como error
- Esto es normal y esperado

---

## 📁 ARCHIVOS CREADOS

1. **cargar_pdfs_facturas_v2.py** - Script Python robusto (RECOMENDADO)
2. **cargar_pdfs_facturas_simple.sh** - Script Bash simple
3. **cargar_pdfs_facturas.py** - Script Python original

---

## ✅ VERIFICACIÓN POST-CARGA

### Opción 1: Navegador
1. Ir a http://localhost:8000/invoices/facturas
2. Verificar que aparecen las facturas cargadas
3. Revisar que los datos se extrajeron correctamente

### Opción 2: API
```bash
# Ver estadísticas
curl http://localhost:8000/api/v2/invoices/statistics

# Ver facturas (primeras 10)
curl http://localhost:8000/api/v2/invoices/facturas?limit=10
```

### Opción 3: Base de datos
```bash
cd CODE
python3 -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2

db = SessionLocal()
count = db.query(InvoiceV2).count()
print(f'Total facturas en BD: {count}')
db.close()
"
```

---

## 🎯 PRÓXIMOS PASOS

Después de cargar los PDFs en el tab de Facturas:

1. **Asociar archivos DIAN (XML)**
   - Ir al tab CUFE
   - Cargar los archivos XML correspondientes
   - El sistema detectará automáticamente el tipo

2. **Validar datos**
   - Revisar facturas con advertencias (icono ⚠️)
   - Corregir campos problemáticos si es necesario

3. **Verificar productos**
   - Ir al tab PRODUCTOS
   - Verificar que los productos se extrajeron correctamente

---

## 📝 NOTAS IMPORTANTES

- ✅ Los PDFs se suben a S3 automáticamente
- ✅ Se extrae el CUFE de cada PDF
- ✅ Si no tiene CUFE, se genera uno temporal
- ✅ El estado inicial es "pendiente_dian"
- ✅ Para completar, cargar el archivo XML/PDF DIAN en el tab CUFE

---

**Fecha**: 10 de Febrero de 2026  
**Archivos a cargar**: 183 PDFs  
**Ubicación**: `/home/stk/Documents/GIT/PAQUETEX v1.0/CUFE/CUFE-XML`
