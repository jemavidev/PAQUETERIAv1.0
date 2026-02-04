# ✅ FIX: Extracción de CUFE y Descarga de PDF

## Problemas Solucionados

### 1. ❌ Descarga de PDF no funcionaba
**Causa**: El botón de descarga estaba pasando el CUFE en lugar de la URL del archivo.

**Solución**:
- ✅ Nuevo endpoint: `GET /api/v2/invoices/facturas/{cufe}/download-url`
- ✅ Genera URL pre-firmada de S3 bajo demanda (válida por 1 hora)
- ✅ Función `downloadInvoice()` actualizada para obtener URL del servidor
- ✅ Manejo de errores mejorado con mensajes claros

**Cómo funciona ahora**:
1. Usuario hace clic en botón de descarga
2. Frontend solicita URL al servidor: `/api/v2/invoices/facturas/{cufe}/download-url`
3. Backend genera URL pre-firmada de S3
4. Frontend descarga el archivo usando la URL temporal

### 2. ❌ No se capturaba el CUFE (todas las facturas aparecían como TEMPORAL)
**Causa**: Posibles problemas:
- pdfplumber no instalado en producción
- PDFs con CUFE en formato de imagen (no texto)
- Errores silenciosos durante la extracción

**Solución**:
- ✅ Logging detallado agregado en `extract_text_from_pdf()`
- ✅ Logging detallado agregado en `extract_cufe()`
- ✅ Logging detallado agregado en `create_invoice_from_provider_pdf()`
- ✅ Script de diagnóstico: `verificar_extraccion_cufe.py`
- ✅ Mensajes de error más descriptivos

**Logs que verás ahora**:
```
📄 Procesando 2 páginas del PDF
   Página 1: 6780 caracteres extraídos
📊 Total extraído: 6780 caracteres
🔍 Buscando CUFE en texto de 6780 caracteres
✅ Encontrados 1 patrones de 96 caracteres hex
✅ CUFE válido extraído: 7569152b6d0396f9e507...ed3e2318402d2eb418d2
📊 Datos extraídos del PDF:
   - CUFE: 7569152b6d0396f9e507...
   - Proveedor: DISTRIBUIDORA PAPYRUS S.A.S
   - NIT: 900376841-
   - Número: 18764089385495
   - Fecha: 2025-02-24 00:00:00
   - Total: 787138
✅ Factura creada: 7569152b6d0396f9... - DISTRIBUIDORA PAPYRUS S.A.S (estado: pendiente_dian)
```

## 🔧 Verificación en Producción

### Paso 1: Verificar que pdfplumber esté instalado
```bash
cd CODE
source .venv/bin/activate
python3 verificar_extraccion_cufe.py
```

**Salida esperada**:
```
✅ pdfplumber está instalado
   Versión: 0.10.3
✅ PDFParserService importado correctamente
✅ Sistema de extracción de CUFE está configurado correctamente
```

### Paso 2: Revisar logs del servidor
Cuando cargues una factura, busca en los logs:
```bash
# Ver logs en tiempo real
docker-compose logs -f app

# O si usas systemd
journalctl -u paquetex -f
```

Busca estos mensajes:
- `📄 Procesando X páginas del PDF` - Confirma que se está extrayendo texto
- `🔍 Buscando CUFE` - Confirma que se está buscando el CUFE
- `✅ CUFE válido extraído` - Confirma que se encontró el CUFE
- `❌ No se encontró patrón` - Indica que el PDF no tiene CUFE extraíble

### Paso 3: Probar descarga de PDF
1. Carga una factura que tenga archivo PDF (verifica que `archivo_proveedor_s3_key` no sea null)
2. Haz clic en el botón de descarga (icono verde de descarga)
3. Deberías ver el mensaje "Descargando factura..." y el archivo se descargará

## 🐛 Si el CUFE sigue sin extraerse

### Causa 1: pdfplumber no instalado
```bash
cd CODE
source .venv/bin/activate
pip install pdfplumber==0.10.3
```

### Causa 2: PDFs con CUFE en imagen (no texto)
Los PDFs escaneados o con CUFE en formato de imagen no se pueden extraer con pdfplumber.

**Solución**: Usar el botón "🔗 Asociar CUFE" para agregar el CUFE manualmente:
1. Haz clic en el botón 🔗 junto a "TEMPORAL"
2. Pega el CUFE completo (96 caracteres)
3. El sistema auto-limpia espacios y valida
4. Haz clic en "Asociar CUFE"

### Causa 3: Error en el servidor
Revisa los logs del servidor para ver el error específico:
```bash
docker-compose logs app | grep -A 10 "Error"
```

## 📊 Prueba con PDFs de Ejemplo

Los siguientes PDFs se probaron y **SÍ extraen el CUFE correctamente**:
- `CUFE/FACTURAS/FE15778.pdf` ✅
- `CUFE/FACTURAS/FV09006851640112400000125.pdf` ✅
- `CUFE/FACTURAS/ad00454539650892500016306.pdf` ✅

Si estos PDFs funcionan en local pero no en producción, el problema es de configuración del servidor.

## 🎯 Resumen de Archivos Modificados

1. **Backend**:
   - `CODE/src/app/routes/invoices_v2_routes.py` - Nuevo endpoint de descarga
   - `CODE/src/app/services/pdf_parser_service.py` - Logging mejorado
   - `CODE/src/app/services/invoice_v2_service.py` - Logging mejorado

2. **Frontend**:
   - `CODE/src/templates/invoices_v2/facturas.html` - Función downloadInvoice actualizada

3. **Scripts de diagnóstico**:
   - `CODE/verificar_extraccion_cufe.py` - Verificar configuración
   - `CODE/test_cufe_simple.py` - Probar extracción con PDFs
   - `CODE/diagnostico_carga_facturas.py` - Diagnosticar flujo completo

## 🚀 Próximos Pasos

1. Ejecutar `verificar_extraccion_cufe.py` en producción
2. Reiniciar el servidor para aplicar cambios
3. Cargar una factura de prueba
4. Revisar logs para confirmar extracción de CUFE
5. Probar descarga de PDF
6. Si el CUFE no se extrae, usar el botón "🔗 Asociar CUFE" manualmente
