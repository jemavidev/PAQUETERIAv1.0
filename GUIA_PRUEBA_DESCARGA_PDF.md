# 📥 Guía de Prueba: Botón de Descarga de Facturas

## ✅ Estado Actual

El sistema de descarga está **completamente implementado y funcional**:

### Backend ✅
- **Endpoint**: `GET /api/v2/invoices/facturas/{cufe}/download-url`
- **Función**: Genera URL pre-firmada de S3 (válida por 1 hora)
- **Respuesta**: `{"url": "https://...", "filename": "factura_XXX.pdf"}`
- **Test**: ✅ Probado y funcionando (ver `test_download_endpoint.py`)

### Frontend ✅
- **Botón**: Icono verde de descarga en columna "Acciones"
- **Función**: `downloadInvoice(cufe)` - Async, con manejo de errores
- **Estados**:
  - Verde: Archivo disponible (clickeable)
  - Gris: Sin archivo (deshabilitado)

---

## 🧪 Cómo Probar

### Paso 1: Verificar que hay facturas con archivos
```bash
cd CODE
source .venv/bin/activate
python3 test_download_endpoint.py
```

**Salida esperada**:
```
✅ Encontradas X facturas
📋 Facturas disponibles:
   1. ✅ TEMP_7b9bff369db2578...
      S3 Key: invoices/provider/TEMP_...pdf
✅ ENDPOINT DE DESCARGA FUNCIONANDO CORRECTAMENTE
```

### Paso 2: Probar en el navegador

1. **Abrir la aplicación**: http://localhost:8000/invoices/facturas (o tu URL de producción)

2. **Identificar facturas con archivo**:
   - Botón de descarga **VERDE** = Tiene archivo ✅
   - Botón de descarga **GRIS** = Sin archivo ❌

3. **Hacer clic en el botón verde de descarga**:
   - Deberías ver el mensaje: "Descargando factura..." (verde)
   - El archivo PDF se descargará automáticamente

### Paso 3: Verificar en la consola del navegador (F12)

Si hay algún error, abre la consola del navegador (F12) y busca:
- ✅ `200 OK` en la pestaña Network para la petición a `/download-url`
- ❌ Errores en rojo en la consola

---

## 🐛 Solución de Problemas

### Problema 1: Botón gris (deshabilitado)
**Causa**: La factura no tiene archivo en S3 (`archivo_proveedor_s3_key` es null)

**Solución**:
1. Verifica que el archivo se subió correctamente al cargar la factura
2. Revisa los logs del servidor durante la carga
3. Verifica la configuración de AWS S3 en `.env`

### Problema 2: Error "No hay archivo PDF disponible"
**Causa**: El archivo no existe en S3 o la key es incorrecta

**Solución**:
```bash
# Verificar que el archivo existe en S3
aws s3 ls s3://elclub-paqueteria/invoices/provider/

# O usar el script de diagnóstico
python3 CODE/test_download_endpoint.py
```

### Problema 3: Error "Error generando URL de descarga"
**Causa**: Problema con las credenciales de AWS o permisos de S3

**Solución**:
1. Verifica las credenciales en `.env`:
   ```
   AWS_ACCESS_KEY_ID=tu-access-key
   AWS_SECRET_ACCESS_KEY=tu-secret-key
   AWS_S3_BUCKET=elclub-paqueteria
   AWS_REGION=us-east-1
   ```

2. Verifica permisos del bucket S3:
   - El usuario debe tener permisos `s3:GetObject`
   - El bucket debe permitir URLs pre-firmadas

### Problema 4: Descarga no inicia
**Causa**: Bloqueador de pop-ups o error de CORS

**Solución**:
1. Permite pop-ups para el sitio
2. Verifica la consola del navegador (F12) para errores
3. Verifica que la URL generada sea válida (debe empezar con `https://`)

---

## 🔍 Debugging Avanzado

### Ver la petición completa en el navegador:
1. Abre DevTools (F12)
2. Ve a la pestaña "Network"
3. Haz clic en el botón de descarga
4. Busca la petición a `/download-url`
5. Verifica:
   - Status: 200 OK
   - Response: `{"url": "https://...", "filename": "..."}`

### Probar el endpoint directamente:
```bash
# Obtener un CUFE de prueba
CUFE="TEMP_7b9bff369db2578418a81fd0870c4cac4af83540b326e2f2647543bc12e3ff56"

# Probar el endpoint
curl -X GET "http://localhost:8000/api/v2/invoices/facturas/${CUFE}/download-url"
```

**Respuesta esperada**:
```json
{
  "url": "https://elclub-paqueteria.s3.amazonaws.com/invoices/provider/TEMP_...?X-Amz-Algorithm=...",
  "filename": "factura_XXX.pdf"
}
```

### Ver logs del servidor:
```bash
# Docker
docker-compose logs -f app | grep -E "(download|URL|S3)"

# Systemd
journalctl -u paquetex -f | grep -E "(download|URL|S3)"
```

---

## 📊 Flujo Completo

```
Usuario hace clic en botón de descarga
    ↓
JavaScript: downloadInvoice(cufe)
    ↓
Fetch: GET /api/v2/invoices/facturas/{cufe}/download-url
    ↓
Backend: Busca factura en BD
    ↓
Backend: Verifica que tenga archivo_proveedor_s3_key
    ↓
Backend: Genera URL pre-firmada de S3 (válida 1 hora)
    ↓
Backend: Retorna {"url": "...", "filename": "..."}
    ↓
JavaScript: Crea elemento <a> con la URL
    ↓
JavaScript: Simula click para descargar
    ↓
Navegador: Descarga el archivo PDF
```

---

## ✨ Características

- ✅ **URLs temporales**: Válidas por 1 hora (seguridad)
- ✅ **Descarga directa**: No requiere autenticación adicional
- ✅ **Nombre automático**: `factura_{numero}.pdf`
- ✅ **Manejo de errores**: Mensajes claros al usuario
- ✅ **Estados visuales**: Verde (disponible) / Gris (no disponible)
- ✅ **Async/Await**: No bloquea la interfaz

---

## 🎯 Checklist de Verificación

- [ ] Backend: Endpoint `/download-url` responde correctamente
- [ ] S3: Archivos existen en el bucket
- [ ] Frontend: Botón verde visible para facturas con archivo
- [ ] Frontend: Click en botón inicia descarga
- [ ] Navegador: Archivo PDF se descarga correctamente
- [ ] Logs: No hay errores en consola del navegador
- [ ] Logs: No hay errores en logs del servidor

---

Si todos los checks están ✅, el sistema de descarga está funcionando perfectamente! 🎉
