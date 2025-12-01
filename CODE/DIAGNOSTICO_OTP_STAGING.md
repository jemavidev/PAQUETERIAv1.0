# 🔍 Diagnóstico de Problemas OTP en Staging

## 🚨 Problema Reportado
No es posible ingresar con el código OTP en el ambiente de staging.

---

## 📋 Scripts de Diagnóstico Disponibles

### 1. Verificación Rápida
```bash
cd CODE
python3 check_otp_issue.py
```

**Qué hace:**
- Verifica que la tabla `customer_otps` existe
- Muestra los últimos 10 OTPs creados
- Lista OTPs pendientes de verificar
- Verifica timezone del servidor
- Prueba el modelo CustomerOTP

### 2. Diagnóstico Completo
```bash
cd CODE
python3 debug_otp_staging.py
```

**Qué hace:**
- Diagnóstico interactivo paso a paso
- Verifica conexión a BD
- Analiza OTPs de un teléfono específico
- Permite probar verificación en vivo
- Revisa logs del sistema

### 3. Prueba de Verificación en Vivo
```bash
cd CODE
python3 test_otp_verification_live.py
```

**Qué hace:**
- Simula exactamente el proceso de verificación
- Muestra cada paso del proceso
- Detecta problemas comunes (espacios, caracteres extra)
- Compara códigos byte por byte

---

## 🔍 Causas Comunes del Problema

### 1. ⚠️ Tabla `customer_otps` No Existe

**Síntoma:** Error al buscar OTPs en la base de datos

**Solución:**
```bash
cd CODE
python3 create_customer_otps_table.py
```

### 2. ⚠️ Código con Espacios o Caracteres Extra

**Síntoma:** El código se ve correcto pero no verifica

**Causa:** El usuario copia el código con espacios: `"123 456"` en lugar de `"123456"`

**Solución:** El frontend debe limpiar el código:
```javascript
// En el frontend
const cleanCode = code.trim().replace(/\s+/g, '');
```

### 3. ⚠️ OTP Expirado

**Síntoma:** "Código no encontrado o expirado"

**Causa:** Los códigos expiran en 5 minutos

**Verificar:**
```bash
python3 check_otp_issue.py
# Revisa la sección "OTPs pendientes de verificar"
# Verifica el "Tiempo restante"
```

### 4. ⚠️ Intentos Agotados

**Síntoma:** "Ha excedido el número de intentos"

**Causa:** Se intentó verificar 3 veces con código incorrecto

**Solución:** Solicitar un nuevo código OTP

### 5. ⚠️ Problema de Timezone

**Síntoma:** OTPs se marcan como expirados inmediatamente

**Causa:** El servidor no está en timezone de Colombia

**Verificar:**
```bash
# En el servidor
date
timedatectl

# Debería mostrar: America/Bogota o UTC-5
```

**Solución:**
```bash
# Configurar timezone
sudo timedatectl set-timezone America/Bogota
```

### 6. ⚠️ Teléfono No Normalizado

**Síntoma:** "Cliente no encontrado"

**Causa:** El teléfono en la BD está en formato diferente

**Ejemplo:**
- BD: `+573001234567`
- Request: `3001234567`

**Verificar:**
```sql
SELECT phone FROM customers WHERE phone LIKE '%3001234567%';
```

### 7. ⚠️ Cliente Inactivo

**Síntoma:** "No encontramos un cliente registrado"

**Causa:** El cliente existe pero `is_active = FALSE`

**Verificar:**
```sql
SELECT id, full_name, phone, is_active 
FROM customers 
WHERE phone = '+573001234567';
```

---

## 🛠️ Pasos de Diagnóstico Manual

### Paso 1: Verificar Tabla
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('SELECT COUNT(*) FROM customer_otps'))
print(f'Total OTPs: {result.scalar()}')
db.close()
"
```

### Paso 2: Ver Últimos OTPs
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    SELECT customer_phone, otp_code, is_verified, is_expired, created_at
    FROM customer_otps
    ORDER BY created_at DESC
    LIMIT 5
'''))

for row in result:
    print(f'{row[0]} | {row[1]} | Verificado: {row[2]} | Expirado: {row[3]} | {row[4]}')

db.close()
"
```

### Paso 3: Verificar OTP Específico
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.customer_otp import CustomerOTP
from sqlalchemy import desc

PHONE = '+573001234567'  # Cambiar por el teléfono real

db = SessionLocal()
otp = db.query(CustomerOTP).filter(
    CustomerOTP.customer_phone == PHONE
).order_by(desc(CustomerOTP.created_at)).first()

if otp:
    print(f'Código: {otp.otp_code}')
    print(f'Intentos: {otp.attempts}/{otp.max_attempts}')
    print(f'Verificado: {otp.is_verified}')
    print(f'Expirado: {otp.is_expired}')
    print(f'is_valid(): {otp.is_valid()}')
else:
    print('No se encontró OTP')

db.close()
"
```

### Paso 4: Ver Logs del Servidor
```bash
# Ver logs en tiempo real
tail -f logs/app.log | grep -i otp

# O buscar en logs existentes
grep -i "verificando código" logs/app.log | tail -20
```

---

## 🔧 Soluciones Rápidas

### Limpiar OTPs Expirados
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
result = db.execute(text('''
    DELETE FROM customer_otps 
    WHERE created_at < NOW() - INTERVAL '1 hour'
'''))
db.commit()
print(f'OTPs eliminados: {result.rowcount}')
db.close()
"
```

### Resetear OTPs de un Cliente
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

PHONE = '+573001234567'  # Cambiar por el teléfono real

db = SessionLocal()
result = db.execute(text('''
    UPDATE customer_otps 
    SET is_expired = TRUE
    WHERE customer_phone = :phone
      AND is_verified = FALSE
'''), {'phone': PHONE})
db.commit()
print(f'OTPs expirados: {result.rowcount}')
db.close()
"
```

### Crear OTP Manual para Pruebas
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from app.models.customer_otp import CustomerOTP

PHONE = '+573001234567'  # Cambiar por el teléfono real

db = SessionLocal()
otp = CustomerOTP(customer_phone=PHONE)
db.add(otp)
db.commit()
db.refresh(otp)

print(f'✅ OTP creado: {otp.otp_code}')
print(f'   Expira en: 5 minutos')
print(f'   Usa este código para probar')

db.close()
"
```

---

## 📊 Checklist de Verificación

Antes de reportar un bug, verifica:

- [ ] La tabla `customer_otps` existe
- [ ] El cliente existe y está activo
- [ ] Se solicitó un OTP recientemente (< 5 minutos)
- [ ] El código no tiene espacios ni caracteres extra
- [ ] No se agotaron los 3 intentos
- [ ] El timezone del servidor es correcto
- [ ] Los logs no muestran errores

---

## 🆘 Si Nada Funciona

1. **Reiniciar el servidor:**
```bash
sudo systemctl restart paquetex
# o
cd CODE/src && pkill -f uvicorn && uvicorn main:app --reload
```

2. **Verificar que el código está actualizado:**
```bash
cd CODE
git status
git log -1 --oneline
```

3. **Recrear la tabla:**
```bash
cd CODE
python3 -c "
import sys
sys.path.insert(0, 'src')
from app.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
db.execute(text('DROP TABLE IF EXISTS customer_otps CASCADE'))
db.commit()
db.close()
"

python3 create_customer_otps_table.py
```

4. **Contactar soporte con:**
   - Output de `python3 check_otp_issue.py`
   - Últimas 50 líneas de logs: `tail -50 logs/app.log`
   - Teléfono del cliente afectado

---

## 📝 Notas Importantes

- Los códigos OTP expiran en **5 minutos**
- Máximo **3 intentos** por código
- Máximo **5 códigos** por hora por teléfono
- Los códigos son de **6 dígitos numéricos**
- El teléfono debe estar en formato internacional: `+573001234567`

---

**Última actualización:** 2025-11-30  
**Versión:** 1.0.0
