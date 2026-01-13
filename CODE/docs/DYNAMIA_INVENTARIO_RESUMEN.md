# Resumen - Consulta de Inventario DynamiaERP

## ✅ Confirmado

**Sí, es posible leer los items/productos del inventario de DynamiaERP**

- ✅ **Total de items disponibles:** 1,827 productos
- ✅ **Endpoint funcionando:** `GET /api/inventario/items`
- ✅ **Formato de respuesta:** JSON con estructura `{statusCode, size, valid, data: []}`
- ✅ **Script creado:** `CODE/scripts/consultar_inventario_dynamia.py`

## 📦 Información del Inventario

### Datos Verificados
- **Total de productos:** 1,827 items
- **Items con "PAPEL":** 93 productos
- **Estructura completa:** ID, código, nombre, precio, tipo, marca, línea, etc.

### Ejemplos de Productos
1. Láminas de icopor (varios grosores)
2. Papel (93 variedades diferentes)
3. Cargadores USB
4. Papelería en general
5. Artículos de oficina

## 🚀 Cómo Usar

### Opción 1: Script Interactivo
```bash
cd CODE
python scripts/consultar_inventario_dynamia.py
```

**Menú disponible:**
- Listar todos los items
- Buscar por nombre
- Buscar por código
- Consultar existencias
- Ver marcas, líneas, bodegas
- Exportar a JSON

### Opción 2: Código Python
```python
from CODE.scripts.consultar_inventario_dynamia import DynamiaInventarioClient

# Crear cliente
client = DynamiaInventarioClient(
    token="tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e"
)

# Obtener todos los items
items = client.get_all_items()
print(f"Total: {len(items)} items")

# Buscar por nombre
resultados = client.buscar_item_por_nombre("PAPEL")
print(f"Encontrados: {len(resultados)} items con 'PAPEL'")

# Buscar por código
item = client.buscar_item_por_codigo("211129")
if item:
    print(f"Producto: {item['nombre']}")
```

### Opción 3: Request Directo
```python
import requests

headers = {
    "Authorization": "Bearer tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e",
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.dynamiaerp.co/api/inventario/items",
    headers=headers
)

data = response.json()
items = data['data']  # Lista de items

print(f"Total de items: {len(items)}")
```

## 📊 Estructura de un Item

```json
{
  "id": 698605,
  "codigo": "211129",
  "nombre": "1/4 DE LAMINA ICOPOR 10MM 50x50 ( G - G - 050601 )",
  "descripcion": "...",
  "precio": 5000.00,
  "estado": "ACTIVO",
  "tipo": {
    "id": 1,
    "nombre": "PRODUCTO"
  },
  "marca": {
    "id": 123,
    "nombre": "MARCA"
  },
  "linea": {
    "id": 456,
    "nombre": "LINEA"
  }
}
```

## 🔍 Endpoints Disponibles

| Endpoint | Descripción | Verificado |
|----------|-------------|------------|
| `GET /api/inventario/items` | Listar todos los items | ✅ |
| `GET /api/inventario/items/ultimos` | Últimos items creados | ✅ |
| `GET /api/inventario/items/tipos` | Tipos de items | ✅ |
| `GET /api/inventario/items/existencias` | Consultar existencias | ⬜ |
| `GET /api/inventario/marcas` | Listar marcas | ✅ |
| `GET /api/inventario/lineas` | Listar líneas | ✅ |
| `GET /api/inventario/bodegas` | Listar bodegas | ✅ |
| `GET /api/inventario/fabricantes` | Listar fabricantes | ⬜ |
| `GET /api/inventario/presentaciones` | Listar presentaciones | ⬜ |

## 💡 Casos de Uso para Paquetería

### 1. Sincronizar Paquetes con Inventario
```python
# Verificar si los paquetes existen en DynamiaERP
paquetes = ["Paquete Premium", "Paquete Básico", "Paquete Express"]

items = client.get_all_items()
for paquete in paquetes:
    existe = any(paquete in item['nombre'] for item in items)
    print(f"{paquete}: {'✓ Existe' if existe else '✗ No existe'}")
```

### 2. Usar Items en Ventas
```python
# Buscar item para usar en venta
item = client.buscar_item_por_nombre("Paquete Premium")[0]

# Crear venta con el item
venta = {
    "detalles": [
        {
            "itemId": item['id'],
            "descripcion": item['nombre'],
            "cantidad": 1,
            "precio": item['precio']
        }
    ]
}
```

### 3. Consultar Precios
```python
# Obtener precio de un producto
item = client.buscar_item_por_codigo("211129")
precio = item['precio']
print(f"Precio: ${precio:,.2f}")
```

### 4. Exportar Catálogo
```python
# Exportar todo el inventario a JSON
items = client.get_all_items()

import json
with open('catalogo_productos.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2, ensure_ascii=False)
```

## 📝 Documentación Creada

1. **`DYNAMIA_INVENTARIO_GUIA.md`** - Guía completa de uso
2. **`consultar_inventario_dynamia.py`** - Script interactivo
3. **`DYNAMIA_INVENTARIO_RESUMEN.md`** - Este documento

## ⚡ Respuesta a tu Pregunta

**Pregunta:** ¿Es posible leer en la sección de inventario los items o productos?

**Respuesta:** **SÍ, totalmente posible**

- ✅ Endpoint funcionando: `GET /api/inventario/items`
- ✅ Total de items: 1,827 productos disponibles
- ✅ Información completa: ID, código, nombre, precio, tipo, marca, línea
- ✅ Script listo para usar
- ✅ Búsqueda por nombre o código
- ✅ Exportación a JSON

## 🎯 Próximos Pasos Sugeridos

1. ⬜ Probar el script interactivo
2. ⬜ Exportar inventario completo a JSON
3. ⬜ Identificar qué items usar para paquetes
4. ⬜ Integrar consulta de inventario en sistema de paquetería
5. ⬜ Crear paquetes como items en DynamiaERP (si no existen)

---

**Fecha:** 2026-01-13  
**Estado:** ✅ Verificado y funcionando
