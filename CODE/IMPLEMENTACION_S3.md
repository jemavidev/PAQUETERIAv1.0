# 📦 Implementación de AWS S3 para PDFs de Facturas

**Fecha:** 2026-01-13  
**Estado:** ✅ Implementado  
**Versión:** 1.0

---

## 🎯 Objetivo

Migrar el almacenamiento de PDFs de facturas desde el servidor local a AWS S3 para:
- Escalabilidad ilimitada
- Reducir carga en el servidor
- Backup automático y durabilidad
- Acceso más rápido con URLs firmadas
- Reducir costos de almacenamiento

---

## 📋 Archivos Modificados/Creados

### Nuevos Archivos
- `src/app/services/s3_storage_service.py` - Servicio de S3
- `migrar_pdfs_a_s3.py` - Script de migración
- `verificar_s3.py` - Script de verificación
- `IMPLEMENTACION_S3.md` - Esta documentación

### Archivos Modificados
- `src/app/services/invoice_service.py` - Integración con S3
- `src/app/routes/invoices.py` - Endpoints actualizados
- `.env` - Variables de configuración S3

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=tu_access_key_id_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_access_key_aqui
AWS_S3_BUCKET_NAME=elclub-paqueteria
AWS_REGION=us-east-1
AWS_S3_PREFIX=invoices/
AWS_S3_ENABLED=true
```

### Configuración del Bucket S3

1. **Nombre del bucket:** `elclub-paqueteria`
2. **Región:** `us-east-1`
3. **Estructura de carpetas:**
   ```
   elclub-paqueteria/
   └── invoices/
       ├── {file_hash1}.pdf
       ├── {file_hash2}.pdf
       └── ...
   ```

4. **Permisos necesarios:**
   - `s3:PutObject` - Subir archivos
   - `s3:GetObject` - Descargar archivos
   - `s3:DeleteObject` - Eliminar archivos
   - `s3:ListBucket` - Listar archivos
   - `s3:HeadObject` - Verificar existencia

5. **Seguridad:**
   - Encriptación en reposo: AES256
   - Acceso privado (no público)
   - URLs firmadas para acceso temporal

---

## 🚀 Funcionalidades Implementadas

### 1. Servicio S3 (`S3StorageService`)

**Métodos principales:**
- `upload_pdf()` - Sube un PDF a S3
- `download_pdf()` - Descarga un PDF desde S3
- `exists()` - Verifica si un PDF existe
- `delete_pdf()` - Elimina un PDF
- `generate_presigned_url()` - Genera URL firmada temporal
- `list_pdfs()` - Lista PDFs en S3
- `get_storage_stats()` - Estadísticas de almacenamiento
- `migrate_from_local()` - Migra PDFs locales a S3

### 2. Integración en InvoiceService

**Nuevos métodos:**
- `save_pdf()` - Guarda PDF (S3 o local como fallback)
- `get_pdf()` - Obtiene PDF (S3 o local como fallback)
- `delete_pdf()` - Elimina PDF (S3 y local)

**Lógica de fallback:**
1. Intenta usar S3 si está habilitado
2. Si falla, usa almacenamiento local
3. Al leer, busca primero en S3, luego local

### 3. Nuevos Endpoints API

**Descarga de PDFs:**
```
GET /invoices/api/{invoice_id}/download-pdf
```
- Descarga el PDF original
- Funciona con S3 o almacenamiento local

**Visualización de PDFs:**
```
GET /invoices/api/{invoice_id}/view-pdf
```
- Retorna URL firmada si S3 está habilitado
- O sirve el PDF directamente

### 4. Modificaciones en Endpoints Existentes

**Upload de facturas (`/invoices/api/extract`):**
- Ahora guarda PDFs en S3 automáticamente
- Incluye metadata (CUFE, proveedor, fecha)
- Fallback a almacenamiento local si S3 falla

**Re-procesamiento (`/invoices/api/{id}/reprocess`):**
- Obtiene PDFs desde S3 o local
- Usa archivo temporal para procesamiento

---

## 📊 Scripts de Utilidad

### 1. Verificar Configuración S3

```bash
cd CODE
python3 verificar_s3.py
```

**Muestra:**
- Estado de variables de entorno
- Conexión a S3
- Estadísticas de almacenamiento
- Lista de archivos

### 2. Migrar PDFs Existentes

```bash
cd CODE
python3 migrar_pdfs_a_s3.py
```

**Proceso:**
1. Verifica configuración S3
2. Lista PDFs locales
3. Obtiene metadata de la base de datos
4. Sube cada PDF a S3 con metadata
5. Omite archivos que ya existen en S3
6. Muestra resumen de migración

**⚠️ Importante:**
- Los archivos locales NO se eliminan automáticamente
- Puedes eliminarlos manualmente después de verificar
- O mantenerlos como backup local

---

## 🔄 Flujo de Trabajo

### Subida de Nueva Factura

```
1. Usuario sube PDF
2. Sistema extrae datos
3. Calcula hash del archivo
4. Guarda PDF en S3 (con metadata)
5. Si falla S3, guarda localmente
6. Guarda registro en base de datos
```

### Descarga de Factura

```
1. Usuario solicita PDF
2. Sistema busca en S3
3. Si está en S3:
   - Genera URL firmada (1 hora)
   - O descarga y sirve
4. Si no está en S3:
   - Busca localmente
   - Sirve archivo local
```

### Re-procesamiento

```
1. Usuario solicita re-procesar
2. Sistema obtiene PDF (S3 o local)
3. Guarda en archivo temporal
4. Re-procesa con PDFExtractor
5. Actualiza datos en BD
6. Elimina archivo temporal
```

---

## 💰 Costos Estimados AWS S3

### Almacenamiento
- **Precio:** $0.023 por GB/mes (us-east-1)
- **Estimado:** 1000 facturas × 500 KB = 500 MB
- **Costo mensual:** ~$0.01 USD

### Transferencia
- **Subida:** Gratis
- **Descarga:** $0.09 por GB (primeros 10 TB)
- **Estimado:** 100 descargas/mes × 500 KB = 50 MB
- **Costo mensual:** ~$0.005 USD

### Solicitudes
- **PUT:** $0.005 por 1000 solicitudes
- **GET:** $0.0004 por 1000 solicitudes
- **Estimado:** 100 uploads + 200 downloads/mes
- **Costo mensual:** ~$0.001 USD

**Total estimado:** < $0.02 USD/mes

---

## 🔒 Seguridad

### Encriptación
- **En reposo:** AES256 (server-side)
- **En tránsito:** HTTPS/TLS

### Acceso
- **Bucket:** Privado (no público)
- **URLs firmadas:** Expiran en 1 hora
- **IAM:** Credenciales con permisos mínimos

### Metadata
- Incluye información de factura
- No incluye datos sensibles
- Útil para auditoría

---

## 🧪 Testing

### Verificar que S3 funciona

```bash
# 1. Verificar configuración
python3 verificar_s3.py

# 2. Subir una factura de prueba
# (usar la interfaz web)

# 3. Verificar que se subió a S3
python3 verificar_s3.py

# 4. Descargar la factura
# (usar el botón de descarga en la interfaz)
```

### Verificar Fallback Local

```bash
# 1. Deshabilitar S3 temporalmente
# En .env: AWS_S3_ENABLED=false

# 2. Subir una factura
# Debe guardarse localmente

# 3. Verificar archivo local
ls -lh src/uploads/invoices/

# 4. Re-habilitar S3
# En .env: AWS_S3_ENABLED=true
```

---

## 🐛 Troubleshooting

### Error: "Credenciales de AWS no configuradas"

**Solución:**
```bash
# Verificar variables en .env
grep AWS_ .env

# Asegurarse de que están configuradas:
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

### Error: "Bucket no encontrado"

**Solución:**
1. Verificar nombre del bucket en .env
2. Verificar que el bucket existe en AWS
3. Verificar región correcta

### Error: "Access Denied"

**Solución:**
1. Verificar permisos IAM del usuario
2. Asegurarse de tener permisos:
   - s3:PutObject
   - s3:GetObject
   - s3:DeleteObject
   - s3:ListBucket

### PDFs no se suben a S3

**Solución:**
```bash
# 1. Verificar que S3 está habilitado
python3 verificar_s3.py

# 2. Ver logs del servidor
docker-compose logs web | grep S3

# 3. Verificar conectividad
# Desde el contenedor:
docker-compose exec web python3 -c "import boto3; print(boto3.__version__)"
```

---

## 📈 Próximas Mejoras

### Corto Plazo
- [ ] Dashboard de estadísticas S3
- [ ] Limpieza automática de archivos locales después de migración
- [ ] Notificaciones de errores de S3

### Mediano Plazo
- [ ] Versionado de PDFs en S3
- [ ] Lifecycle policies (mover a Glacier después de 1 año)
- [ ] CloudFront CDN para descargas más rápidas

### Largo Plazo
- [ ] Análisis de costos y optimización
- [ ] Replicación multi-región
- [ ] Backup automático a otro bucket

---

## 📚 Referencias

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [S3 Pricing](https://aws.amazon.com/s3/pricing/)

---

**Última actualización:** 2026-01-13  
**Autor:** Sistema PAQUETEX  
**Versión:** 1.0
