# Credenciales DynamiaERP API

## Información de Acceso

- **Account:** papyrus
- **Usuario:** jesus
- **Contraseña:** il1111
- **Token:** tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e

## URLs de la API

- **Producción:** https://api.dynamiaerp.co
- **Swagger UI:** http://api.pos.dynamiaerp.co/swagger-ui/index.html
- **OpenAPI Docs:** http://api.pos.dynamiaerp.co/v3/api-docs

## Autenticación

### Método 1: Usando Token Directo
```bash
curl -H "Authorization: Bearer tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e" \
     https://api.dynamiaerp.co/api/empresa
```

### Método 2: Obtener Token con Usuario/Contraseña
```bash
curl -X POST https://api.dynamiaerp.co/api/seguridad/gettoken \
     -H "Content-Type: application/json" \
     -d '{"username":"jesus","password":"il1111"}'
```

## Notas Importantes

- El token proporcionado puede ser de larga duración o permanente
- Verificar si el token expira y necesita renovación
- Guardar estas credenciales de forma segura en variables de entorno
- No compartir estas credenciales en repositorios públicos

## Variables de Entorno Recomendadas

```env
DYNAMIA_API_URL=https://api.dynamiaerp.co
DYNAMIA_ACCOUNT=papyrus
DYNAMIA_USERNAME=jesus
DYNAMIA_PASSWORD=il1111
DYNAMIA_TOKEN=tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e
```

## Fecha de Creación
2026-01-13

---

**IMPORTANTE:** Este archivo contiene información sensible. 
Asegúrate de que esté en .gitignore y no se suba al repositorio.
