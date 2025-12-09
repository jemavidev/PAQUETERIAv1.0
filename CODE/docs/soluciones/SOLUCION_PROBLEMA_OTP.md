# ✅ Solución al Problema de OTP en Staging

## 🔍 Diagnóstico Realizado

He ejecutado las pruebas y **el sistema OTP funciona correctamente**:

- ✅ Tabla `customer_otps` existe
- ✅ Modelo `CustomerOTP` funciona
- ✅ Verificación de códigos funciona
- ✅ Generación de tokens JWT funciona
- ✅ Timezone configurado correctamente

## 🎯 Problema Identificado

El OTP encontrado en la base de datos estaba **expirado por tiempo** (creado hace 33 minutos, expira en 5 minutos).

## 🔧 Causas Posibles del Problema en Staging

### 1. ⚠️ OTPs Expirando Antes de Ser Usados

**Síntoma:** El usuario recibe el SMS pero cuando intenta verificar, ya expiró.

**Causas:**
- El SMS tarda en llegar
- El usuario tarda en ingresar el código
- Los códigos expiran en 5 minutos

**Solución:**
```python
# En CODE/src/app/models/customer_otp.py
# Cambiar de 5 a 10 minutos
if not self.expires_at:
    self.expires_at = get_colombia_now() + timedelta(minutes=10)  # Era 5
```

### 2. ⚠️ Código con Espacios o Formato Incorrecto

**Síntoma:** El código se ve correcto pero no verifica.

**Causa:** El usuario copia el código con espacios del SMS: `"123 456"` en vez de `"123456"`

**Solución en Frontend:**
```javascript
// Limpiar el código antes de enviar
const cleanCode = code.trim().replace(/\s+/g, '').replace(/-/g, '');
```

### 3. ⚠️ Usuario Intenta Múltiples Veces

**Síntoma:** "Ha excedido el número de intentos"

**Causa:** El usuario intenta 3 veces con código incorrecto (por espacios, etc.)

**Solución:**
- Mejorar el mensaje de error
- Mostrar el código sin espacios en el input
- Permitar más intentos (cambiar `max_attempts` de 3 a 5)

### 4. ⚠️ SMS No Llega o Llega Tarde

**Síntoma:** El usuario no recibe el SMS

**Verificar:**
```bash
# Ver logs de envío de SMS
cd CODE
grep -i "sms.*573002596319" logs/app.log | tail -20
```

**Solución:**
- Verificar configuración de SMS
- Verificar créditos del proveedor SMS
- Agregar reenvío de código

### 5. ⚠️ Problema de Sincronización de Código

**Síntoma:** El código en el SMS no coincide con el de la BD

**Verificar:**
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

PHONE = '+573002596319'  # Cambiar por el teléfono real

db = SessionLocal()
result = db.execute(text('''
    SELECT otp_code, created_at 
    FROM customer_otps 
    WHERE customer_phone = :phone 
    ORDER BY created_at DESC 
    LIMIT 1
'''), {'phone': PHONE})

row = result.fetchone()
if row:
    print(f'Último código generado: {row[0]}')
    print(f'Creado: {row[1]}')
else:
    print('No hay OTPs para este teléfono')

db.close()
"
```

## 🚀 Soluciones Inmediatas

### Solución 1: Aumentar Tiempo de Expiración

```bash
cd CODE/src/app/models
```

Editar `customer_otp.py` línea ~48:
```python
# ANTES
self.expires_at = get_colombia_now() + timedelta(minutes=5)

# DESPUÉS
self.expires_at = get_colombia_now() + timedelta(minutes=10)
```

### Solución 2: Aumentar Intentos Permitidos

Editar `customer_otp.py` línea ~30:
```python
# ANTES
max_attempts = Column(Integer, default=3, nullable=False)

# DESPUÉS
max_attempts = Column(Integer, default=5, nullable=False)
```

### Solución 3: Limpiar Código en Frontend

En el archivo del formulario de verificación:
```javascript
// Antes de enviar el request
const verifyOTP = async (code) => {
    // Limpiar el código
    const cleanCode = code.trim().replace(/\s+/g, '').replace(/-/g, '');
    
    const response = await fetch('/api/customer-portal/verify-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            phone: phone,
            code: cleanCode  // Usar código limpio
        })
    });
    
    // ...
};
```

### Solución 4: Agregar Botón de Reenvío

```javascript
const resendOTP = async () => {
    const response = await fetch('/api/customer-portal/request-otp', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone: phone })
    });
    
    if (response.ok) {
        alert('Nuevo código enviado');
    }
};
```

## 🧪 Cómo Probar en Staging

### 1. Crear OTP Nuevo
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.customer_otp import CustomerOTP

PHONE = '+573002596319'  # Cambiar por teléfono real

db = SessionLocal()

# Limpiar anteriores
from sqlalchemy import text
db.execute(text('UPDATE customer_otps SET is_expired = TRUE WHERE customer_phone = :phone'), {'phone': PHONE})
db.commit()

# Crear nuevo
otp = CustomerOTP(customer_phone=PHONE)
db.add(otp)
db.commit()
db.refresh(otp)

print(f'Código: {otp.otp_code}')
print(f'Válido por 5 minutos')

db.close()
"
```

### 2. Probar Verificación
```bash
cd CODE
python3 test_otp_verification_live.py
# Ingresa el teléfono y código cuando te lo pida
```

### 3. Ver Logs en Tiempo Real
```bash
tail -f logs/app.log | grep -i otp
```

## 📊 Métricas para Monitorear

Después de aplicar las soluciones, monitorea:

1. **Tasa de éxito de verificación:**
```sql
SELECT 
    COUNT(*) FILTER (WHERE is_verified = TRUE) * 100.0 / COUNT(*) as tasa_exito
FROM customer_otps
WHERE created_at > NOW() - INTERVAL '24 hours';
```

2. **Tiempo promedio de verificación:**
```sql
SELECT 
    AVG(EXTRACT(EPOCH FROM (verified_at - created_at))) / 60 as minutos_promedio
FROM customer_otps
WHERE is_verified = TRUE
  AND created_at > NOW() - INTERVAL '24 hours';
```

3. **OTPs expirados sin verificar:**
```sql
SELECT COUNT(*)
FROM customer_otps
WHERE is_verified = FALSE
  AND is_expired = FALSE
  AND expires_at < NOW()
  AND created_at > NOW() - INTERVAL '24 hours';
```

## ✅ Checklist de Verificación

Antes de dar por resuelto:

- [ ] Aumentar tiempo de expiración a 10 minutos
- [ ] Aumentar intentos permitidos a 5
- [ ] Limpiar código en frontend (quitar espacios)
- [ ] Agregar botón de reenvío de código
- [ ] Mejorar mensajes de error
- [ ] Verificar que SMS llega correctamente
- [ ] Probar con usuario real en staging
- [ ] Monitorear logs por 24 horas

## 🆘 Si el Problema Persiste

1. **Ejecuta diagnóstico completo:**
```bash
cd CODE
python3 debug_otp_staging.py
```

2. **Comparte:**
   - Output del diagnóstico
   - Últimas 50 líneas de logs: `tail -50 logs/app.log`
   - Teléfono del cliente afectado
   - Hora exacta del intento

3. **Verifica configuración SMS:**
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.config import settings

print(f'SMS Provider: {settings.sms_provider}')
print(f'SMS Configured: {bool(settings.sms_api_key)}')
"
```

---

**Última actualización:** 2025-11-30  
**Estado:** ✅ Sistema funcional, optimizaciones recomendadas
