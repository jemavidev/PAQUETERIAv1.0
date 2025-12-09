# 🧪 INSTRUCCIONES PARA EJECUTAR PRUEBAS

**Sistema:** Portal de Clientes - OTP y Preferencias  
**Versión:** 1.0.0  
**Fecha:** 2025-12-08

---

## 📋 REQUISITOS PREVIOS

### Software necesario:
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Acceso a internet
- Teléfono móvil para recibir SMS

### Instalación de dependencias:

```bash
# Instalar httpx (cliente HTTP asíncrono)
pip install httpx

# O si usas pip3
pip3 install httpx
```

---

## 🚀 EJECUCIÓN DE PRUEBAS AUTOMATIZADAS

### Paso 1: Navegar al directorio del proyecto

```bash
cd CODE
```

### Paso 2: Ejecutar el script de pruebas

```bash
python3 test_sistema_completo_final.py
```

### Paso 3: Seguir las instrucciones en pantalla

El script te guiará a través del proceso:

1. **Solicitud de OTP:**
   - El script enviará automáticamente un código OTP a tu teléfono
   - Verás un mensaje de confirmación

2. **Ingreso de código:**
   - Recibirás un SMS con un código de 6 dígitos
   - El script te pedirá que ingreses el código
   - Ejemplo: `123456`

3. **Pruebas automáticas:**
   - El script ejecutará todas las pruebas automáticamente
   - Verás el progreso en tiempo real
   - Al final, verás un resumen completo

### Paso 4: Revisar resultados

Al finalizar, el script generará:
- Resumen en pantalla con estadísticas
- Archivo JSON con resultados detallados: `test_results_[TIMESTAMP].json`

---

## 📊 INTERPRETACIÓN DE RESULTADOS

### Salida exitosa:

```
================================================================================
                            RESUMEN DE PRUEBAS                                
================================================================================

Total de pruebas: 8
✅ Exitosas: 8
❌ Fallidas: 0
Tasa de éxito: 100.0%

🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
El sistema está listo para producción.
```

**Significado:** Todas las funcionalidades están operativas. Puedes proceder con el despliegue.

### Salida con errores:

```
Total de pruebas: 8
✅ Exitosas: 6
❌ Fallidas: 2
Tasa de éxito: 75.0%

⚠️  Algunas pruebas fallaron. Revisar antes de desplegar.
```

**Significado:** Hay problemas que deben resolverse antes del despliegue.

**Acciones:**
1. Revisar el archivo `test_results_[TIMESTAMP].json`
2. Identificar qué pruebas fallaron
3. Revisar los logs del servidor
4. Corregir los problemas
5. Volver a ejecutar las pruebas

---

## 🔍 PRUEBAS MANUALES COMPLEMENTARIAS

Además de las pruebas automatizadas, se recomienda realizar estas verificaciones manuales:

### 1. Flujo completo de autenticación

**URL:** `https://staging.jemavi.co/announce`

**Pasos:**
1. Abrir la URL en un navegador
2. Ingresar tu número de teléfono (formato: 3334004007)
3. Click en "Solicitar código"
4. Verificar que recibes el SMS
5. Ingresar el código de 6 dígitos
6. Verificar que accedes al dashboard

**Resultado esperado:**
- ✅ SMS recibido en menos de 30 segundos
- ✅ Código válido por 5 minutos
- ✅ Acceso al dashboard después de verificación
- ✅ Sin errores en consola del navegador

### 2. Gestión de preferencias desde el portal

**URL:** `https://staging.jemavi.co/customer-portal/dashboard`

**Pasos:**
1. Acceder al dashboard (después de autenticación OTP)
2. Scroll hasta "Preferencias de Notificaciones"
3. Desactivar "Notificaciones por SMS"
4. Verificar feedback visual (switch cambia a OFF)
5. Recargar la página
6. Verificar que el cambio se mantuvo

**Resultado esperado:**
- ✅ Switch cambia de estado inmediatamente
- ✅ Mensaje de confirmación aparece
- ✅ Cambios persisten después de recargar
- ✅ Sin errores en consola

### 3. Gestión de preferencias desde panel de administración

**URL:** `https://staging.jemavi.co/customers/manage`

**Pasos:**
1. Acceder al panel (requiere autenticación de administrador)
2. Buscar un cliente por teléfono
3. Click en "Gestionar preferencias de notificación"
4. Modificar preferencias en el modal
5. Guardar cambios
6. Verificar mensaje de confirmación

**Resultado esperado:**
- ✅ Modal se abre correctamente
- ✅ Preferencias actuales se cargan
- ✅ Cambios se guardan exitosamente
- ✅ Mensaje de confirmación aparece

### 4. Verificación de bloqueo de notificaciones

**Requisitos:** Acceso a logs del servidor

**Pasos:**
1. Desactivar todas las notificaciones para un cliente
2. Simular un evento de paquete (anunciado, recibido, etc.)
3. Revisar logs del servidor
4. Buscar mensajes de bloqueo

**Comando para revisar logs:**
```bash
docker-compose logs -f | grep -E "(bloqueado|BLOCKED)"
```

**Resultado esperado:**
```
📵 SMS bloqueado por preferencias del cliente [CUSTOMER_ID] (evento: package_received)
📧❌ Email bloqueado por preferencias del cliente [CUSTOMER_ID] (evento: package_received)
```

### 5. Verificación de OTPs de autenticación

**Importante:** Los OTPs de autenticación NUNCA deben bloquearse

**Pasos:**
1. Desactivar TODAS las notificaciones para un cliente
2. Solicitar un nuevo código OTP desde `/announce`
3. Verificar que el SMS SÍ llega
4. Revisar logs del servidor

**Resultado esperado:**
- ✅ SMS con OTP llega normalmente
- ✅ En logs: "No verificar preferencias para OTP de autenticación"
- ✅ Cliente puede acceder al portal

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "No se pudo conectar al servidor"

**Causa:** El servidor staging no está disponible o hay problemas de red

**Solución:**
```bash
# Verificar que el servidor está activo
curl https://staging.jemavi.co/health

# Si no responde, contactar al equipo de infraestructura
```

### Problema: "Código OTP no llega"

**Causa:** Problemas con el servicio de SMS (Liwa.co)

**Solución:**
```bash
# Revisar logs del servidor
docker-compose logs | grep -i "liwa\|sms"

# Verificar configuración de Liwa
# Revisar variables de entorno: LIWA_API_KEY, LIWA_ACCOUNT, LIWA_PASSWORD
```

### Problema: "Token JWT inválido"

**Causa:** El token expiró o hay problemas con la clave secreta

**Solución:**
```bash
# Verificar que SECRET_KEY está configurada
echo $SECRET_KEY

# Solicitar un nuevo código OTP
# Los tokens expiran después de 1 hora
```

### Problema: "Preferencias no se guardan"

**Causa:** Problemas con la base de datos o permisos

**Solución:**
```bash
# Verificar conexión a base de datos
docker-compose logs db

# Verificar que la tabla existe
docker-compose exec db psql -U postgres -d paquetex -c "\dt customer_preferences"

# Verificar permisos del usuario
```

### Problema: "Error de JavaScript en consola"

**Causa:** Recursos no cargados o variables no definidas

**Solución:**
1. Abrir DevTools (F12)
2. Ir a la pestaña Console
3. Identificar el error específico
4. Verificar que todos los scripts se cargan correctamente
5. Limpiar caché del navegador (Ctrl+Shift+R)

---

## 📞 SOPORTE

Si encuentras problemas que no puedes resolver:

1. **Revisar documentación:**
   - `CODE/VERIFICACION_CODIGO_COMPLETA.md`
   - `CODE/RESUMEN_PRUEBAS_SISTEMA.md`

2. **Revisar logs del servidor:**
   ```bash
   docker-compose logs -f --tail=100
   ```

3. **Consultar base de datos:**
   ```bash
   docker-compose exec db psql -U postgres -d paquetex
   ```

4. **Contactar al equipo de desarrollo:**
   - Proporcionar el archivo `test_results_[TIMESTAMP].json`
   - Incluir logs relevantes del servidor
   - Describir los pasos para reproducir el problema

---

## ✅ CHECKLIST DE VERIFICACIÓN

Antes de considerar las pruebas como exitosas, verifica:

- [ ] Script de pruebas automatizado ejecutado sin errores
- [ ] Todas las pruebas (8/8) pasaron exitosamente
- [ ] Flujo de autenticación OTP funciona manualmente
- [ ] Preferencias se pueden modificar desde el portal
- [ ] Preferencias se pueden modificar desde panel de administración
- [ ] Notificaciones se bloquean según preferencias
- [ ] OTPs de autenticación NO se bloquean
- [ ] Sin errores en consola del navegador
- [ ] Logs del servidor no muestran errores críticos
- [ ] Archivo de resultados generado correctamente

---

## 🎯 PRÓXIMOS PASOS

Una vez que todas las pruebas pasen exitosamente:

1. **Documentar resultados:**
   - Guardar archivo `test_results_[TIMESTAMP].json`
   - Tomar capturas de pantalla de pruebas exitosas
   - Documentar cualquier observación

2. **Preparar para producción:**
   - Hacer backup de base de datos de producción
   - Revisar checklist de despliegue
   - Coordinar ventana de mantenimiento

3. **Desplegar a producción:**
   - Seguir procedimiento de despliegue estándar
   - Monitorear logs durante las primeras horas
   - Estar disponible para soporte

4. **Verificación post-despliegue:**
   - Ejecutar pruebas en producción
   - Verificar métricas de uso
   - Recopilar feedback de usuarios

---

**Última actualización:** 2025-12-08  
**Versión del documento:** 1.0.0
