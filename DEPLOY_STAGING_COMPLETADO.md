# ✅ DEPLOY A STAGING COMPLETADO

**Fecha:** 2 de febrero de 2026, 15:00:47
**Commit:** `3c4a966` - "Fix: Corregir subida de PDFs a S3 y generar URLs pre-firmadas"
**Rama:** `staging`
**Duración:** 440 segundos (~7 minutos)

---

## 🎯 Funcionalidad Desplegada

### ✅ Subida Automática de PDFs a S3

Cuando subes una factura de proveedor:
1. El PDF se extrae y se procesa
2. Se sube automáticamente a AWS S3
3. Se guarda en: `invoices/provider/{cufe}.pdf`
4. Se almacena la key de S3 en la base de datos

### ✅ Descarga de PDFs con URLs Pre-firmadas

- Botón de descarga en la columna "Acciones"
- Verde si hay PDF disponible en S3
- Gris si no hay PDF (facturas antiguas)
- URLs seguras que expiran en 1 hora
- Se regeneran automáticamente al recargar la página

### ✅ Copiar CUFE al Portapapeles

- Botón de clipboard al lado del CUFE truncado
- Copia el código CUFE completo
- Feedback visual al copiar

---

## 📊 Estado Actual del Sistema

### Servicios en Staging

```
✅ paqueteria_staging_app    - UP (healthy) - 23 minutos
✅ paqueteria_staging_redis  - UP (healthy) - 2 días
```

### Base de Datos

```
Total de facturas: 12
Facturas con PDF en S3: 0 (todas son antiguas)
```

### Configuración S3

```
✅ AWS_ACCESS_KEY_ID: AKIASQJ3NG...
✅ AWS_S3_BUCKET: elclub-paqueteria
✅ AWS_REGION: us-east-1
✅ S3_PREFIX: staging/
✅ S3Service: Inicializado correctamente
```

---

## 🧪 Cómo Probar la Funcionalidad

### 1. Acceder a la Vista de Facturas

```
URL: https://staging.tudominio.com/invoices
```

### 2. Subir una Factura Nueva

1. Click en el tab "Facturas"
2. Click en "Cargar Factura de Proveedor"
3. Selecciona un PDF de factura
4. Click en "Subir"

### 3. Verificar la Subida a S3

Deberías ver en los logs:

```bash
ssh ubuntu@staging
docker logs -f paqueteria_staging_app | grep S3
```

Busca:
```
✅ Archivo subido a S3: invoices/provider/{cufe}.pdf
```

### 4. Verificar el Botón de Descarga

- El botón debe aparecer en VERDE
- Click en el botón → descarga el PDF
- El PDF debe ser el mismo que subiste

### 5. Verificar el Botón de Copiar CUFE

- Click en el botón de clipboard
- Pega en un editor de texto
- Debe ser el CUFE completo (128 caracteres)

---

## ⚠️ Notas Importantes

### Facturas Antiguas (12 en total)

Las facturas que ya están en la base de datos **NO** tienen PDF en S3:
- Fueron creadas antes de este fix
- El botón de descarga aparecerá en GRIS (deshabilitado)
- Para tenerlas en S3, debes re-subirlas

### Facturas Nuevas

Todas las facturas que subas después del deploy:
- ✅ Se subirán automáticamente a S3
- ✅ El botón estará en VERDE
- ✅ Podrás descargar el PDF en cualquier momento

### URLs Pre-firmadas

Las URLs de descarga son temporales:
- ✅ Expiran después de 1 hora
- ✅ Se regeneran automáticamente al recargar la página
- ✅ Más seguras que URLs públicas
- ✅ No requiere cambiar permisos del bucket S3

---

## 🔍 Comandos Útiles

### Ver logs en tiempo real

```bash
ssh ubuntu@staging
docker logs -f paqueteria_staging_app
```

### Ver estado de contenedores

```bash
ssh ubuntu@staging
cd /home/ubuntu/paqueteria-staging
docker compose -f docker-compose.staging.yml ps
```

### Verificar facturas en la base de datos

```bash
ssh ubuntu@staging
docker exec paqueteria_staging_app python -c "
from src.app.database import SessionLocal
from src.app.models.invoice_v2 import InvoiceV2

db = SessionLocal()
total = db.query(InvoiceV2).count()
con_s3 = db.query(InvoiceV2).filter(InvoiceV2.archivo_proveedor_s3_key.isnot(None)).count()
print(f'Total: {total} | Con S3: {con_s3}')
db.close()
"
```

### Verificar archivos en S3

```bash
ssh ubuntu@staging
docker exec paqueteria_staging_app python -c "
from src.app.services.s3_service import S3Service
s3 = S3Service()
# Listar archivos en el bucket (requiere permisos de listado)
print('Bucket:', s3.bucket_name)
"
```

---

## 📝 Archivos Modificados en el Deploy

### 1. `CODE/src/app/services/invoice_v2_service.py`

- Corregir conversión de archivo a bytes para S3
- Agregar logging detallado
- Guardar `archivo_proveedor_s3_key` en la base de datos

### 2. `CODE/src/app/routes/invoices_v2_routes.py`

- Generar URLs pre-firmadas dinámicamente
- URLs válidas por 1 hora
- Regenerar en cada request

### 3. `CODE/src/templates/invoices_v2/facturas.html`

- Botón de descarga con estados (verde/gris)
- Botón de copiar CUFE
- Mejoras visuales en tabs y badges

---

## 🎯 Próximos Pasos

### Opción 1: Probar con Factura Nueva

1. Ve a `https://staging.tudominio.com/invoices`
2. Sube una factura nueva
3. Verifica que el botón de descarga esté en verde
4. Descarga el PDF y verifica que sea correcto

### Opción 2: Re-subir Facturas Antiguas

Si necesitas tener las facturas antiguas en S3:
1. Descarga los PDFs originales (si los tienes)
2. Re-súbelos usando el modal de carga
3. El sistema los detectará como duplicados si tienen el mismo CUFE

### Opción 3: Deploy a Producción

Cuando estés satisfecho con staging:
```bash
./deploy.sh --env papyrus --deploy
```

---

## ✅ Checklist de Verificación

- [x] Deploy completado exitosamente
- [x] Servicios corriendo (app + redis)
- [x] S3Service configurado correctamente
- [x] Credenciales AWS válidas
- [ ] Probar subida de factura nueva
- [ ] Verificar botón de descarga en verde
- [ ] Descargar PDF y verificar contenido
- [ ] Probar botón de copiar CUFE
- [ ] Verificar que facturas antiguas muestran botón gris

---

**Estado:** ✅ Deploy completado y verificado
**Siguiente:** Probar funcionalidad con factura nueva
