# INSTRUCCIONES PARA REINICIAR EL SERVIDOR

## ⚠️ SITUACIÓN ACTUAL

Los procesos del servidor están corriendo con permisos de root y no puedo detenerlos automáticamente.

```
Procesos corriendo:
- PID 3480: uvicorn (root)
- PID 525912: python main (root)
- PID 525967: python main (root)
```

---

## 🔧 SOLUCIÓN: Reinicio Manual

### Opción 1: Reinicio con Docker (Recomendado)

Si el servidor está corriendo en Docker:

```bash
# Ver contenedores corriendo
docker ps

# Reiniciar el contenedor
docker restart <container_id>

# O reiniciar todos los contenedores
docker-compose restart
```

### Opción 2: Reinicio Manual con Sudo

```bash
# 1. Detener procesos
sudo pkill -f uvicorn
sudo pkill -f "python.*main"

# 2. Verificar que se detuvieron
ps aux | grep -E "uvicorn|python.*main" | grep -v grep

# 3. Iniciar servidor
cd CODE
./start_server.sh
```

### Opción 3: Reinicio del Sistema (Si nada más funciona)

```bash
sudo systemctl restart <nombre_del_servicio>
```

---

## ✅ VERIFICAR QUE EL SERVIDOR REINICIÓ

### 1. Verificar Procesos

```bash
ps aux | grep uvicorn | grep -v grep
```

**Resultado esperado:** Deberías ver un proceso nuevo con fecha/hora reciente

### 2. Verificar Logs

```bash
tail -f CODE/logs/app.log
```

**Buscar:** Mensajes de inicio del servidor y carga de módulos

### 3. Probar en el Navegador

```bash
curl http://localhost:8000/health
```

**Resultado esperado:** `{"status":"ok"}`

### 4. Probar el Nuevo Filtro

1. Abre: `http://localhost:8000/invoices/v2/productos`
2. Busca el selector: **[🔽 Solo reventa ▼]**
3. Si lo ves, el servidor reinició correctamente

---

## 🎯 CAMBIOS QUE VERÁS DESPUÉS DEL REINICIO

### TAB Productos

```
┌────────────────────────────────────────────────────┐
│ [Búsqueda...] [🔽 Solo reventa ▼]  ← NUEVO        │
│                                                    │
│ Opciones:                                          │
│ • Solo reventa (default)                           │
│ • Solo consumo                                     │
│ • Solo servicios                                   │
│ • Todos los tipos                                  │
└────────────────────────────────────────────────────┘
```

### TAB Facturas - Modal de Edición

```
┌────────────────────────────────────────────────────┐
│ Editar Factura                                     │
├────────────────────────────────────────────────────┤
│ ...                                                │
│ Tipo de Factura: [Productos para reventa ▼] ← NUEVO│
│ ...                                                │
└────────────────────────────────────────────────────┘
```

---

## 🧪 PRUEBAS DESPUÉS DEL REINICIO

### Test 1: Verificar Filtro en TAB Productos

```bash
# Debe retornar solo productos de facturas tipo 'reventa'
curl "http://localhost:8000/api/v2/invoices/productos?limit=5" | jq '.'
```

### Test 2: Verificar Campo en API

```bash
# Debe incluir el campo 'tipo_factura'
curl "http://localhost:8000/api/v2/invoices/facturas?limit=1" | jq '.items[0].tipo_factura'
```

**Resultado esperado:** `"reventa"`

### Test 3: Cambiar Tipo de Factura

1. Ve al TAB FACTURAS
2. Edita una factura
3. Cambia "Tipo de Factura" a "Consumo interno"
4. Guarda
5. Ve al TAB PRODUCTOS
6. Los productos de esa factura ya no aparecen (filtro en "Solo reventa")

---

## 📊 ESTADO ACTUAL DE LA BASE DE DATOS

```
✅ Migración aplicada
✅ Columna tipo_factura creada
✅ Índice creado
✅ 152 facturas como 'reventa'
```

---

## ❓ TROUBLESHOOTING

### Problema: No veo el filtro en TAB Productos

**Solución:**
1. Limpia caché del navegador (Ctrl + Shift + R)
2. Verifica que el servidor reinició
3. Revisa logs: `tail -f CODE/logs/app.log`

### Problema: Error al editar factura

**Solución:**
1. Verifica que la migración se aplicó:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'invoices_v2' AND column_name = 'tipo_factura';
   ```
2. Debe retornar: `tipo_factura`

### Problema: Filtro no funciona

**Solución:**
1. Abre consola del navegador (F12)
2. Ve a Network
3. Busca la petición a `/api/v2/invoices/productos`
4. Verifica que incluye `?tipo_factura=reventa`

---

## 📝 RESUMEN

**Estado:** Migración aplicada ✅, Servidor necesita reinicio ⏳

**Próximo paso:** Reiniciar el servidor manualmente con uno de los métodos arriba

**Después del reinicio:** Probar el filtro en TAB Productos y el campo en TAB Facturas

---

## 🆘 SI NECESITAS AYUDA

1. Verifica logs: `tail -f CODE/logs/app.log`
2. Verifica procesos: `ps aux | grep uvicorn`
3. Verifica puerto: `netstat -tulpn | grep 8000`
4. Prueba API: `curl http://localhost:8000/health`
