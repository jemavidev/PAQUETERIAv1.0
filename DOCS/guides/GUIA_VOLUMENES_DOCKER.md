# 📦 Guía de Volúmenes Docker - Paquetería v1.0

## ✅ Cambios Implementados

Se han actualizado los 3 archivos docker-compose para manejar correctamente los datos mediante volúmenes externos:

### 🎯 Objetivo Logrado
**Ahora puedes modificar archivos estáticos (CSS, JS, imágenes, PDFs) y templates HTML sin necesidad de reconstruir la imagen Docker o reiniciar contenedores.**

---

## 📁 Estructura de Volúmenes

### **Desarrollo** (`docker-compose.dev.yml`)
```yaml
Volúmenes Montados:
├── ./CODE/src:/app/src                    # Código Python (hot reload)
├── ./CODE/src/static:/app/src/static      # CSS, JS, imágenes, PDFs (editable)
├── ./CODE/src/templates:/app/src/templates # Templates HTML (editable)
├── uploads_data_dev:/app/uploads          # Archivos subidos
├── logs_data_dev:/app/logs                # Logs de aplicación
└── backups_data_dev:/app/backups          # Backups de BD
```

### **Producción** (`docker-compose.prod.yml`)
```yaml
Volúmenes Montados (App):
├── ./CODE/src/app:/app/src/app:ro         # Código Python (read-only)
├── ./CODE/src/static:/app/src/static      # CSS, JS, imágenes, PDFs (editable)
├── ./CODE/src/templates:/app/src/templates # Templates HTML (editable)
├── uploads_data:/app/uploads              # Archivos subidos
├── logs_data:/app/logs                    # Logs de aplicación
└── backups_data:/app/backups              # Backups de BD

Volúmenes Montados (Celery Worker/Beat):
├── ./CODE/src/app:/app/src/app:ro         # Código Python (read-only)
├── uploads_data:/app/uploads              # Archivos subidos
├── logs_data:/app/logs                    # Logs
└── backups_data:/app/backups              # Backups de BD
```

### **Lightsail** (`docker-compose.lightsail.yml`)
```yaml
Volúmenes Montados (App):
├── ./CODE/src/app:/app/src/app:ro         # Código Python (read-only)
├── ./CODE/src/static:/app/src/static      # CSS, JS, imágenes, PDFs (editable)
├── ./CODE/src/templates:/app/src/templates # Templates HTML (editable)
├── uploads_data:/app/uploads              # Archivos subidos
├── logs_data:/app/logs                    # Logs de aplicación
└── backups_data:/app/backups              # Backups de BD

Volúmenes Montados (Celery Worker):
├── ./CODE/src/app:/app/src/app:ro         # Código Python (read-only)
├── uploads_data:/app/uploads              # Archivos subidos
├── logs_data:/app/logs                    # Logs
└── backups_data:/app/backups              # Backups de BD
```

---

## 🔄 Qué Puedes Modificar Sin Rebuild

### ✅ **Cambios Instantáneos** (sin reiniciar contenedor)
- **CSS**: `CODE/src/static/css/*.css`
- **JavaScript**: `CODE/src/static/js/*.js`
- **Imágenes**: `CODE/src/static/images/*`
- **PDFs**: `CODE/src/static/pdf/*`
- **Templates HTML**: `CODE/src/templates/**/*.html`

### 🔄 **Cambios con Restart** (sin rebuild)
- **Código Python**: `CODE/src/app/**/*.py`
  - Desarrollo: Hot reload automático
  - Producción/Lightsail: `docker compose restart app`

### 🏗️ **Cambios que Requieren Rebuild**
- `requirements.txt` (nuevas dependencias)
- `Dockerfile` (cambios en la imagen base)
- Archivos copiados en el Dockerfile

---

## 🚀 Comandos Útiles

### Aplicar Cambios en Archivos Estáticos
```bash
# No requiere ningún comando - los cambios son instantáneos
# Solo refresca el navegador (Ctrl+F5)
```

### Aplicar Cambios en Código Python (Producción)
```bash
# Reiniciar solo el contenedor de la app
docker compose -f docker-compose.prod.yml restart app

# O reiniciar todos los servicios
docker compose -f docker-compose.prod.yml restart
```

### Ver Logs en Tiempo Real
```bash
# Desarrollo
docker compose -f docker-compose.dev.yml logs -f app

# Producción
docker compose -f docker-compose.prod.yml logs -f app

# Lightsail
docker compose -f docker-compose.lightsail.yml logs -f app
```

### Acceder a Volúmenes Persistentes
```bash
# Ver ubicación de volúmenes
docker volume ls

# Inspeccionar un volumen
docker volume inspect paqueteria_v1_prod_uploads_data

# Backup de un volumen
docker run --rm -v paqueteria_v1_prod_uploads_data:/data -v $(pwd):/backup alpine tar czf /backup/uploads-backup.tar.gz /data
```

---

## ⚠️ Importante: Carpeta `/CODE/static` Redundante

### Problema Detectado
Existen **DOS carpetas static**:
1. `/CODE/static/` (raíz) - **NO se usa en Docker**
2. `/CODE/src/static/` (dentro de src) - **Montada en Docker**

### Diferencias Encontradas
- Algunos archivos JS tienen diferencias menores
- `/CODE/src/static` tiene archivos más recientes

### ✅ Recomendación
**Eliminar `/CODE/static`** después de verificar que `/CODE/src/static` tiene todo el contenido actualizado.

```bash
# 1. Verificar diferencias
diff -r CODE/static CODE/src/static

# 2. Si todo está bien en src/static, eliminar la carpeta redundante
rm -rf CODE/static
```

---

## 🔒 Seguridad

### Código Python en Producción
- Montado como **read-only** (`:ro`)
- Previene modificaciones accidentales o maliciosas
- Requiere restart para aplicar cambios (intencional)

### Archivos Estáticos
- Montados como **read-write**
- Permite actualizaciones rápidas de diseño
- No afecta la lógica de negocio

---

## 📊 Beneficios de Esta Configuración

✅ **Desarrollo más rápido**: Cambios en CSS/JS/HTML sin rebuild  
✅ **Menor downtime**: No necesitas reconstruir imágenes  
✅ **Persistencia de datos**: Uploads, logs y backups sobreviven a recreaciones de contenedores  
✅ **Seguridad**: Código Python protegido en producción  
✅ **Flexibilidad**: Puedes editar templates y estilos en caliente  
✅ **Backups seguros**: Base de datos en volumen persistente  

---

## 🧪 Prueba de Funcionamiento

### Test 1: Modificar CSS
```bash
# 1. Editar un archivo CSS
echo "body { background: red; }" >> CODE/src/static/css/custom.css

# 2. Refrescar navegador (Ctrl+F5)
# ✅ Debería verse el cambio inmediatamente
```

### Test 2: Modificar Template
```bash
# 1. Editar un template HTML
echo "<h1>TEST</h1>" >> CODE/src/templates/dashboard/index.html

# 2. Refrescar navegador
# ✅ Debería verse el cambio inmediatamente
```

### Test 3: Modificar Código Python (Producción)
```bash
# 1. Editar un archivo Python
nano CODE/src/app/routes/dashboard.py

# 2. Reiniciar contenedor
docker compose -f docker-compose.prod.yml restart app

# 3. Verificar cambios
# ✅ Cambios aplicados sin rebuild
```

---

## 📝 Notas Adicionales

- Los volúmenes Docker persisten incluso si eliminas los contenedores
- Para limpiar volúmenes: `docker compose down -v` (⚠️ elimina datos)
- Los archivos en volúmenes se sincronizan en tiempo real con el host
- En desarrollo, el hot reload de Python funciona automáticamente

---

**Fecha de actualización**: 22 de noviembre de 2025  
**Versión**: 1.0
