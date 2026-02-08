# 🚀 INSTRUCCIONES: Reprocesar Facturas AHORA

**Fecha**: 2026-02-08  
**Objetivo**: Extraer los ~72 productos faltantes de las 3 facturas  
**Tiempo estimado**: 5-10 minutos

---

## ✅ PASO 1: Reiniciar el Servidor

### Opción A - Si usas Docker:
```bash
cd /home/stk/Documents/GIT/PAQUETEX\ v1.0
docker-compose restart
```

### Opción B - Si usas uvicorn directamente:
```bash
# Detener servidor (como root o con sudo)
sudo pkill -f uvicorn

# Esperar 2 segundos
sleep 2

# Iniciar de nuevo
cd /home/stk/Documents/GIT/PAQUETEX\ v1.0/CODE
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Opción C - Si usas systemd:
```bash
sudo systemctl restart paquetex
```

---

## ✅ PASO 2: Verificar que el servidor está corriendo

Abre en tu navegador:
```
http://localhost:8000/invoices/productos
```

Deberías ver la interfaz del TAB PRODUCTOS (aunque solo con 18 productos por ahora).

---

## ✅ PASO 3: Reprocesar las 3 Facturas

### 3.1 Ir al TAB CUFE:
```
http://localhost:8000/invoices/cufe
```

### 3.2 Reprocesar Factura 1: PAPYRUS SOLUCIONES INTEGRALES (2FE-438)

1. **Buscar** la factura en la lista (buscar por "PAPYRUS" o "2FE-438")
2. **Click** en el botón "📄 Cargar DIAN" (icono de documento)
3. **Seleccionar** el archivo PDF DIAN correspondiente
4. **Subir** el archivo
5. **Esperar** a que procese (verás un mensaje de éxito)
6. **Verificar** en los logs que dice algo como: "✅ Extraídos X productos del PDF"

### 3.3 Reprocesar Factura 2: DISTRIBUIDORA PAPYRUS (FE-15778)

1. **Buscar** la factura (buscar por "DISTRIBUIDORA" o "FE-15778")
2. **Click** en "📄 Cargar DIAN"
3. **Seleccionar** el archivo PDF DIAN
4. **Subir** y esperar
5. **Verificar** mensaje de éxito

### 3.4 Reprocesar Factura 3: PAPYRUS SOLUCIONES INTEGRALES (FELN-1141)

1. **Buscar** la factura (buscar por "FELN-1141")
2. **Click** en "📄 Cargar DIAN"
3. **Seleccionar** el archivo PDF DIAN
4. **Subir** y esperar
5. **Verificar** mensaje de éxito

---

## ✅ PASO 4: Verificar Resultados

### 4.1 Ir al TAB PRODUCTOS:
```
http://localhost:8000/invoices/productos
```

### 4.2 Verificar el total:

Deberías ver en la parte superior algo como:
```
Mostrando 1-25 de ~90 productos
```

### 4.3 Buscar productos específicos:

Prueba buscar estos códigos para verificar que se extrajeron:
- `631668` (BOLSA DE PAPEL SELVA)
- `631669` (BOLSA PAPEL CARROS)
- `631655` (BOLSA PAPEL TROPICAL)

Si aparecen, ¡funcionó! 🎉

---

## 📊 Verificación Rápida desde Terminal

Si quieres verificar desde la terminal sin abrir el navegador:

```bash
cd /home/stk/Documents/GIT/PAQUETEX\ v1.0/CODE
python3 -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM invoice_products_v2'))
    total = result.scalar()
    print(f'✅ Total productos en BD: {total}')
    
    result = conn.execute(text('''
        SELECT i.proveedor_nombre, COUNT(p.id) as total
        FROM invoices_v2 i 
        LEFT JOIN invoice_products_v2 p ON i.cufe = p.cufe 
        WHERE i.estado = \"completo\" 
        GROUP BY i.proveedor_nombre
        ORDER BY total DESC
    '''))
    
    print()
    print('📦 Productos por proveedor:')
    for row in result:
        proveedor = row[0] or 'Sin nombre'
        total = row[1]
        print(f'   - {proveedor[:40]:40s}: {total:3d} productos')
"
```

**Resultado esperado**:
```
✅ Total productos en BD: ~90

📦 Productos por proveedor:
   - PAPYRUS SOLUCIONES INTEGRALES SAS      :  24 productos
   - DISTRIBUIDORA PAPYRUS S.A.S            :  24 productos
   - PAPYRUS SOLUCIONES INTEGRALES S.A.S.   :  24 productos
   - SOLUCIONES MAF S.A.S.                  :  18 productos
```

---

## ⚠️ Solución de Problemas

### Si el servidor no inicia:

1. **Verificar puerto ocupado**:
   ```bash
   sudo lsof -i :8000
   ```

2. **Matar proceso si es necesario**:
   ```bash
   sudo kill -9 <PID>
   ```

3. **Verificar logs**:
   ```bash
   cd /home/stk/Documents/GIT/PAQUETEX\ v1.0/CODE
   tail -f logs/app.log
   ```

### Si no se extraen productos:

1. **Verificar que el parser se actualizó**:
   ```bash
   cd /home/stk/Documents/GIT/PAQUETEX\ v1.0/CODE
   grep -A 3 "FORMATO 0: Nuevo formato" src/app/services/pdf_parser_service.py
   ```
   
   Debería mostrar el nuevo patrón.

2. **Verificar logs del servidor** al subir el archivo DIAN:
   - Buscar mensajes como: "Producto extraido (FORMATO NUEVO)"
   - Si dice "No se encontro seccion de productos", el PDF no tiene el formato esperado

### Si solo se extraen algunos productos:

Es normal si las facturas tienen diferentes cantidades de productos. Verifica el total sumando todos.

---

## 🎯 Resultado Final Esperado

**Antes de reprocesar**:
```
Total: 18 productos
```

**Después de reprocesar**:
```
Total: ~90 productos
  - SOLUCIONES MAF: 18 productos
  - PAPYRUS SOLUCIONES (2FE): ~24 productos
  - DISTRIBUIDORA PAPYRUS: ~24 productos
  - PAPYRUS SOLUCIONES (FELN): ~24 productos
```

---

## ✅ Checklist

- [ ] Paso 1: Servidor reiniciado
- [ ] Paso 2: Servidor accesible en http://localhost:8000
- [ ] Paso 3.2: Factura 1 reprocesada (PAPYRUS 2FE-438)
- [ ] Paso 3.3: Factura 2 reprocesada (DISTRIBUIDORA FE-15778)
- [ ] Paso 3.4: Factura 3 reprocesada (PAPYRUS FELN-1141)
- [ ] Paso 4: Verificado ~90 productos en TAB PRODUCTOS
- [ ] Verificación: Búsqueda de códigos funciona (631668, 631669, etc.)

---

## 📞 Cuando Termines

Avísame:
1. ✅ Cuántos productos tienes en total
2. ✅ Si aparecen los códigos 631668, 631669, 631655
3. ✅ Si hay algún error o problema

Y continuamos con:
- Mejorar la visualización del TAB PRODUCTOS
- Agregar campos de trazabilidad (opcional)
- Dashboard de análisis (opcional)

---

**Creado**: 2026-02-08  
**Tiempo estimado**: 5-10 minutos  
**Dificultad**: Fácil ⭐
