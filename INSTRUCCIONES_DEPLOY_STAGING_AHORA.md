# Instrucciones para Deploy en Staging - AHORA

## ✅ Problema Resuelto
El error de "Multiple head revisions" en Alembic ha sido corregido.

## 📋 Cambios Aplicados
1. ✅ Eliminada migración de merge incorrecta
2. ✅ Unificadas todas las ramas en un solo head
3. ✅ Commit y push a staging completados
4. ✅ Verificación de heads exitosa (solo 1 head)

## 🚀 Próximos Pasos

### Opción 1: Usar el script de deploy (RECOMENDADO)
```bash
./deploy.sh staging
```

Este script automáticamente:
- Hace pull de los últimos cambios
- Reconstruye los contenedores
- Ejecuta health check
- Aplica las migraciones de Alembic (ahora sin errores)
- Reinicia el servidor

### Opción 2: Reinicio manual
Si el script de deploy falla, ejecuta manualmente:

```bash
# En el servidor staging
cd /ruta/al/proyecto

# Pull de cambios
git pull origin staging

# Reiniciar contenedores
sudo docker-compose -f docker-compose.staging.yml down
sudo docker-compose -f docker-compose.staging.yml up -d --build

# Aplicar migraciones
sudo docker-compose -f docker-compose.staging.yml exec app alembic upgrade head

# Verificar que el servidor está corriendo
sudo docker-compose -f docker-compose.staging.yml ps
```

## ✅ Verificación Post-Deploy

### 1. Verificar que las migraciones se aplicaron
```bash
sudo docker-compose -f docker-compose.staging.yml exec app alembic current
```

Debería mostrar: `20260211_092552 (head)`

### 2. Verificar TAB Productos
- Abrir: https://staging.tudominio.com/invoices/productos
- Verificar que aparece el selector "Tipo de Factura"
- Opciones: Solo reventa (default), Solo consumo, Solo servicios, Todos

### 3. Verificar TAB Facturas
- Abrir: https://staging.tudominio.com/invoices/facturas
- Hacer clic en "Editar" en cualquier factura
- Verificar que aparece el campo "Tipo de Factura"
- Opciones: Reventa, Consumo, Servicio, Otro

### 4. Verificar filtrado por defecto
- TAB Productos debe mostrar solo productos de facturas tipo "reventa"
- Cambiar el filtro a "Todos" para ver todos los productos

## 📊 Estado Actual

### Migraciones
- ✅ Solo 1 head: `20260211_092552`
- ✅ Campo `tipo_factura` agregado a tabla `invoices_v2`
- ✅ Índice creado para búsquedas rápidas
- ✅ 152 facturas existentes marcadas como 'reventa' por defecto

### Backend
- ✅ Modelo `InvoiceV2` actualizado
- ✅ API `/productos` con filtro `tipo_factura`
- ✅ Schema `InvoiceResponse` incluye `tipo_factura`

### Frontend
- ✅ TAB Productos: Selector de filtro
- ✅ TAB Facturas: Campo editable en modal

## 🔧 Troubleshooting

### Si el deploy falla con error de permisos
```bash
sudo ./deploy.sh staging
```

### Si Alembic sigue mostrando error de múltiples heads
```bash
# Verificar heads localmente
python3 verificar_alembic_heads.py

# Si muestra más de 1 head, contactar al desarrollador
```

### Si el servidor no responde después del deploy
```bash
# Ver logs
sudo docker-compose -f docker-compose.staging.yml logs -f app

# Reiniciar contenedores
sudo docker-compose -f docker-compose.staging.yml restart
```

## 📝 Notas Importantes

1. **Por defecto**: TAB Productos muestra solo productos de reventa
2. **Clasificación manual**: Cada factura debe clasificarse manualmente en TAB Facturas
3. **Filtros**: Usa el selector en TAB Productos para cambiar el tipo de factura mostrado
4. **Performance**: El índice en `tipo_factura` asegura búsquedas rápidas

## ✅ Checklist Final

- [ ] Deploy ejecutado sin errores
- [ ] Migraciones aplicadas correctamente
- [ ] Selector de "Tipo de Factura" visible en TAB Productos
- [ ] Campo "Tipo de Factura" editable en TAB Facturas
- [ ] Filtrado por defecto funciona (solo reventa)
- [ ] Cambio de filtro funciona correctamente

---

**Commit**: `4c6946e` - fix: resolver múltiples heads en Alembic
**Branch**: `staging`
**Estado**: ✅ Listo para deploy
