# 🔧 Scripts del Proyecto

Esta carpeta contiene scripts de utilidad organizados por categoría.

---

## 📁 Estructura de Carpetas

### `/testing/`
Scripts para pruebas y diagnósticos:
- `test_role_validation.sh` - Pruebas automatizadas de validación de roles
- `diagnostico_imagenes.sh` - Diagnóstico del problema de imágenes
- `verificar_fix_imagenes.sh` - Verificación del fix de imágenes

### `/deploy/`
Scripts relacionados con deploy:
- `cleanup_staging.sh` - Limpieza del entorno de staging

### Raíz de scripts
- `README.md` - Este archivo

---

## 🧪 Scripts de Testing

### `test_role_validation.sh`
**Propósito:** Pruebas automatizadas de validación de roles

**Uso:**
```bash
cd /home/ubuntu/paqueteria-staging
./scripts/testing/test_role_validation.sh
```

**Pruebas que realiza:**
1. Health Check
2. Endpoint público /api/images
3. Endpoint protegido sin auth
4. Verificar estructura de código
5. Verificar logs de aplicación
6. Verificar archivos modificados

**Salida:** Reporte con ✅/❌ para cada prueba

---

### `diagnostico_imagenes.sh`
**Propósito:** Diagnóstico del problema de visualización de imágenes

**Uso:**
```bash
./scripts/testing/diagnostico_imagenes.sh
```

**Verifica:**
- Configuración de S3
- Rutas de imágenes
- Permisos de acceso
- Endpoints públicos

---

### `verificar_fix_imagenes.sh`
**Propósito:** Verificar que el fix de imágenes funciona correctamente

**Uso:**
```bash
./scripts/testing/verificar_fix_imagenes.sh
```

**Verifica:**
- Acceso público a /api/images
- Respuestas HTTP correctas
- Configuración de rutas públicas

---

## 🚀 Scripts de Deploy

### `cleanup_staging.sh`
**Propósito:** Limpiar el entorno de staging

**Uso:**
```bash
./scripts/deploy/cleanup_staging.sh
```

**Acciones:**
- Limpia contenedores antiguos
- Elimina imágenes no utilizadas
- Libera espacio en disco

---

## 📝 Convenciones

### Nombres de Scripts
- `test_*.sh` - Scripts de pruebas
- `diagnostico_*.sh` - Scripts de diagnóstico
- `verificar_*.sh` - Scripts de verificación
- `cleanup_*.sh` - Scripts de limpieza

### Permisos
Todos los scripts deben tener permisos de ejecución:
```bash
chmod +x script.sh
```

### Ubicación
- Scripts de testing: `scripts/testing/`
- Scripts de deploy: `scripts/deploy/`
- Scripts generales: `scripts/`

---

## 🔒 Seguridad

### Buenas Prácticas
1. No incluir credenciales en los scripts
2. Usar variables de entorno para configuración
3. Validar inputs antes de ejecutar comandos
4. Incluir manejo de errores

### Variables de Entorno
Los scripts pueden usar estas variables:
- `BASE_URL` - URL base del servidor
- `ENVIRONMENT` - Entorno (staging/production)

---

## 🧪 Testing de Scripts

Antes de usar un script en producción:
1. Probarlo en staging
2. Verificar que no tiene errores
3. Documentar su uso
4. Agregar manejo de errores

---

## 📊 Estado de Scripts

| Script | Estado | Última Prueba | Resultado |
|--------|--------|---------------|-----------|
| test_role_validation.sh | ✅ Activo | 2025-12-07 | ✅ PASS |
| diagnostico_imagenes.sh | ✅ Activo | 2025-12-07 | ✅ PASS |
| verificar_fix_imagenes.sh | ✅ Activo | 2025-12-07 | ✅ PASS |
| cleanup_staging.sh | ✅ Activo | 2025-12-07 | ✅ PASS |

---

## 🔄 Actualización

Esta documentación se actualiza continuamente. Última actualización: **7 de diciembre de 2025**

---

## 📞 Contacto

Para preguntas sobre los scripts, consultar con el equipo de desarrollo.
