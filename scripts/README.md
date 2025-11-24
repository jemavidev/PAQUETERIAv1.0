# 🛠️ Scripts del Proyecto PAQUETEX

Esta carpeta contiene todos los scripts de utilidad organizados por categoría.

## 📂 Estructura de Carpetas

### `/database`
Scripts relacionados con la base de datos:

**Creación de Tablas:**
- `crear_tabla_customer_preferences.py` - Crea tabla de preferencias de clientes
- `crear_tabla_customer_preferences.sql` - SQL para tabla de preferencias
- `crear_tabla_preferencias.sh` - Script bash para crear preferencias
- `crear_tabla_preferencias_simple.sh` - Versión simplificada

**Gestión de Usuarios:**
- `crear_usuario_jveyes.py` - Crea usuario de prueba
- `cambiar_password_jveyes.py` - Cambia contraseña de usuario

**Uso:**
```bash
# Crear tabla de preferencias
python3 scripts/database/crear_tabla_customer_preferences.py

# Crear usuario de prueba
python3 scripts/database/crear_usuario_jveyes.py

# Cambiar contraseña
python3 scripts/database/cambiar_password_jveyes.py
```

---

### `/email`
Scripts para testing y diagnóstico de emails:

**Testing:**
- `test_email_direct.py` - Prueba directa de envío SMTP
- `test_email_reset.py` - Prueba email de reset de contraseña
- `enviar_email_test.py` - Envío de email de prueba

**Diagnóstico:**
- `diagnosticar_smtp.sh` - Diagnóstico completo de SMTP

**Uso:**
```bash
# Probar envío directo
python3 scripts/email/test_email_direct.py

# Diagnosticar SMTP
bash scripts/email/diagnosticar_smtp.sh

# Enviar email de prueba
python3 scripts/email/enviar_email_test.py
```

---

### `/testing`
Scripts de verificación y testing del sistema:

**Verificación de Componentes:**
- `check_email_notifications.py` - Verifica notificaciones en BD
- `verificar_preferencias.sh` - Verifica sistema de preferencias
- `verificar_settings.sh` - Verifica configuración
- `verificar_cambios.sh` - Verifica cambios aplicados

**Testing Completo:**
- `test_settings.sh` - Test del sistema de settings
- `verificar_sistema_completo.sh` - Verificación completa del sistema

**Uso:**
```bash
# Verificar notificaciones
python3 scripts/testing/check_email_notifications.py

# Verificar sistema completo
bash scripts/testing/verificar_sistema_completo.sh

# Test de settings
bash scripts/testing/test_settings.sh
```

---

## 🔧 Requisitos

### Python Scripts
Requieren las dependencias del proyecto:
```bash
cd CODE
pip install -r requirements.txt
```

### Bash Scripts
Requieren:
- `bash` (incluido en Linux/Mac)
- `curl` (para requests HTTP)
- `jq` (para parsing JSON)

Instalar en Ubuntu/Debian:
```bash
sudo apt-get install curl jq
```

---

## 📝 Convenciones

### Permisos
Todos los scripts tienen permisos de ejecución:
```bash
chmod +x scripts/**/*.sh
chmod +x scripts/**/*.py
```

### Variables de Entorno
Los scripts Python cargan variables desde `CODE/.env`:
```python
from dotenv import load_dotenv
load_dotenv('CODE/.env')
```

### Logging
Los scripts incluyen logging detallado:
- ✅ Operaciones exitosas
- ❌ Errores
- ℹ️ Información
- ⚠️ Advertencias

---

## 🚀 Scripts Más Usados

### 1. Verificación Rápida del Sistema
```bash
bash scripts/testing/verificar_sistema_completo.sh
```

### 2. Test de Email
```bash
python3 scripts/email/test_email_direct.py
```

### 3. Verificar Notificaciones
```bash
python3 scripts/testing/check_email_notifications.py
```

### 4. Crear Tabla de Preferencias
```bash
python3 scripts/database/crear_tabla_customer_preferences.py
```

---

## 🔍 Troubleshooting

### Error: "No module named 'dotenv'"
```bash
cd CODE
pip install python-dotenv
```

### Error: "Permission denied"
```bash
chmod +x scripts/path/to/script.sh
```

### Error: "DATABASE_URL not found"
Verifica que existe `CODE/.env` con la variable `DATABASE_URL`

---

## 📚 Documentación Relacionada

- [Documentación Principal](../DOCS/README.md)
- [Guías de Uso](../DOCS/guias/)
- [Soluciones](../DOCS/soluciones/)

---

**Última actualización:** 24 de Noviembre, 2025
