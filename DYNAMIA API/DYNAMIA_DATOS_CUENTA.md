# Datos de la Cuenta DynamiaERP - Papyrus

## Información de la Empresa

- **Nombre:** DISTRIBUIDORA PAPYRUS S.A.S.
- **NIT:** 901.210.008-8
- **Email:** info@papyrus.com.co
- **Dirección:** CRA 43A #64 SUR 65 INT1611T2, BULEVAR DE ALCAZAR
- **Ciudad:** SABANETA

## Sucursales

### Sucursal Principal
- **ID:** 242
- **Nombre:** CARTAGENA
- **Dirección:** CRA 91 #54-120 LOCAL 12, EL CLUB APARTAMENTOS

**NOTA:** Este ID de sucursal (242) debe usarse en todas las ventas y facturas.

## Estado de la Conexión

✅ **Token Válido:** El token proporcionado funciona correctamente
✅ **Acceso a API:** Conexión exitosa con todos los endpoints principales
✅ **Datos Disponibles:** 
- Información de empresa: OK
- Sucursales: OK (1 sucursal)
- Clientes: OK (4 clientes registrados)
- Inventario: OK (múltiples items)
- Tipos de venta: OK

## Endpoints Verificados

| Endpoint | Estado | Notas |
|----------|--------|-------|
| `/api/empresa` | ✅ OK | Información completa de empresa |
| `/api/empresa/sucursales` | ✅ OK | 1 sucursal disponible |
| `/api/ventas/clientes` | ✅ OK | 4 clientes registrados |
| `/api/inventario/items` | ✅ OK | Items disponibles |
| `/api/connect/ventas/tipos/documentos` | ✅ OK | Tipos de venta disponibles |
| `/api/connect/ventas/tipos/pagos` | ✅ OK | Formas de pago disponibles |
| `/api/v2/public/accounts/context` | ❌ 404 | Endpoint no disponible |
| `/api/ventas/facturaElectronica/status` | ⚠️ Error | Requiere configuración adicional |

## Clientes Registrados

La cuenta tiene **4 clientes** registrados actualmente. Estos pueden ser consultados y actualizados mediante la API.

## Inventario

La cuenta tiene múltiples items de inventario registrados que pueden ser utilizados en las ventas.

## Configuración para Integración

### Variables de Entorno Necesarias

```env
# DynamiaERP API
DYNAMIA_API_URL=https://api.dynamiaerp.co
DYNAMIA_TOKEN=tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e
DYNAMIA_ACCOUNT=papyrus
DYNAMIA_USERNAME=jesus
DYNAMIA_PASSWORD=il1111

# IDs importantes
DYNAMIA_SUCURSAL_ID=242
```

### Datos Importantes para Código

```python
# Usar en todas las ventas
SUCURSAL_ID = 242

# Headers para todas las peticiones
headers = {
    "Authorization": "Bearer tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e",
    "Content-Type": "application/json"
}
```

## Próximos Pasos

1. ✅ Verificar conexión con API
2. ✅ Obtener datos de la cuenta
3. ⬜ Consultar tipos de venta disponibles (IDs específicos)
4. ⬜ Consultar formas de pago disponibles (IDs específicos)
5. ⬜ Probar creación de cliente de prueba
6. ⬜ Probar creación de venta de prueba
7. ⬜ Configurar facturación electrónica (si aplica)
8. ⬜ Implementar servicio de integración
9. ⬜ Integrar con sistema de paquetería

## Notas Importantes

### Facturación Electrónica
El endpoint de facturación electrónica retorna un error que indica que se requiere configuración adicional:
```
"No se recibio token de tipo de venta"
```

Esto sugiere que:
1. La facturación electrónica puede requerir configuración previa en DynamiaERP
2. Puede ser necesario contactar con soporte para habilitar esta funcionalidad
3. Alternativamente, se pueden crear ventas normales primero y luego generar facturas

### Recomendación
Comenzar la integración con:
1. Sincronización de clientes
2. Creación de ventas básicas
3. Luego agregar facturación electrónica cuando esté configurada

## Contacto Soporte

Si se necesita habilitar facturación electrónica o configurar aspectos adicionales:
- **Email:** devteam@dynamiasoluciones.com
- **Cuenta:** papyrus
- **Usuario:** jesus

## Fecha de Verificación

**2026-01-13** - Conexión verificada y funcionando correctamente
