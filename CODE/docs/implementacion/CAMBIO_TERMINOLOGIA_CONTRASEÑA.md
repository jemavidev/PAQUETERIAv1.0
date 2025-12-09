# Cambio de Terminología: "Código OTP" → "Contraseña Temporal"

**Fecha**: 2025-02-07  
**Objetivo**: Mejorar la experiencia del usuario haciendo que el proceso sea más intuitivo

## Resumen

Se cambió toda la terminología del sistema de verificación OTP de "código" a "contraseña temporal" para que el cliente perciba el proceso como un acceso con contraseña temporal en lugar de un código de verificación técnico.

## Cambios Realizados

### 1. Frontend (`CODE/src/templates/customer/verify.html`)

#### Títulos y Labels
- ❌ "Código de Verificación" → ✅ "Contraseña Temporal (6 dígitos)"
- ❌ "Enviar Código" → ✅ "Solicitar Contraseña Temporal"
- ❌ "Verificar Código" → ✅ "Acceder a mi Portal"
- ❌ "Reenviar código" → ✅ "Reenviar contraseña"

#### Mensajes
- ❌ "Código enviado" → ✅ "Contraseña temporal enviada"
- ❌ "Código incorrecto" → ✅ "Contraseña incorrecta"
- ❌ "Código expirado" → ✅ "Contraseña expirada"

#### Info Box
- Cambió de icono de información (ℹ️) a candado (🔐)
- Texto actualizado: "Recibirás una contraseña temporal de 6 dígitos por SMS"

### 2. Backend (`CODE/src/app/routes/customer_preferences_otp.py`)

#### Mensajes SMS
```python
# ANTES
f"PAQUETEX: Su código para gestionar preferencias es: {otp.otp_code}. "
f"Válido por 5 minutos. No comparta este código."

# DESPUÉS
f"PAQUETEX: Su contraseña temporal es: {otp.otp_code}. "
f"Válida por 5 minutos. No comparta esta contraseña."
```

#### Mensajes de Error API
- ❌ "Código no encontrado o expirado" → ✅ "Contraseña no encontrada o expirada"
- ❌ "Código incorrecto" → ✅ "Contraseña incorrecta"
- ❌ "Solicite un nuevo código" → ✅ "Solicite una nueva contraseña"
- ❌ "Error al enviar código" → ✅ "Error al enviar contraseña temporal"

#### Mensajes de Éxito
- ❌ "Código de verificación enviado por SMS" → ✅ "Contraseña temporal enviada por SMS"

#### Logs Internos
- ❌ "Verificando código para portal" → ✅ "Verificando contraseña temporal para portal"
- ❌ "Código correcto" → ✅ "Contraseña correcta"
- ❌ "Limpiando OTPs antiguos" → ✅ "Limpiando contraseñas temporales antiguas"

## Impacto en la Experiencia del Usuario

### Antes
El cliente veía:
1. "Ingrese su código de verificación"
2. "Código enviado por SMS"
3. "Verificar código"

**Percepción**: Proceso técnico de verificación, similar a 2FA

### Después
El cliente ve:
1. "Ingrese su contraseña temporal"
2. "Contraseña temporal enviada por SMS"
3. "Acceder a mi Portal"

**Percepción**: Proceso de login con contraseña temporal, más familiar y menos intimidante

## Consistencia

✅ **Frontend**: Todos los textos visibles usan "contraseña temporal"  
✅ **Backend API**: Todos los mensajes de error/éxito usan "contraseña"  
✅ **SMS**: Mensaje actualizado con "contraseña temporal"  
✅ **Logs**: Actualizados para reflejar nueva terminología (facilita debugging)

## Archivos Modificados

1. `CODE/src/templates/customer/verify.html` - Template HTML completo
2. `CODE/src/app/routes/customer_preferences_otp.py` - Endpoints y mensajes

## Notas Técnicas

- El código interno sigue usando la variable `otp_code` (no se cambió para mantener compatibilidad con la base de datos)
- Los logs internos usan "contraseña temporal" para facilitar el debugging
- La funcionalidad técnica permanece idéntica, solo cambió la presentación al usuario

## Testing Recomendado

1. ✅ Verificar que el SMS llegue con el texto correcto
2. ✅ Probar flujo completo de solicitud → verificación
3. ✅ Verificar mensajes de error (contraseña incorrecta, expirada, etc.)
4. ✅ Confirmar que el botón "Reenviar contraseña" funcione correctamente
5. ✅ Validar que todos los textos en pantalla sean consistentes

## Beneficios

1. **Más intuitivo**: Los usuarios están familiarizados con "contraseñas temporales"
2. **Menos técnico**: Evita jerga técnica como "OTP" o "código de verificación"
3. **Mejor UX**: El proceso se siente como un login normal con contraseña temporal
4. **Consistente**: Toda la interfaz usa la misma terminología
