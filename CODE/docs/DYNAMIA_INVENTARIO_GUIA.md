# Guía de Consulta de Inventario - DynamiaERP

## 📦 Endpoints de Inventario

### 1. Listar Todos los Items
```
GET /api/inventario/items
```

**Respuesta:** Lista completa de items del inventario

**Ejemplo:**
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

items = response.json()
print(f"Total de items: {len(items)}")

for item in items:
    print(f"- {item['nombre']} (ID: {item['id']}, Código: {item['codigo']})")
```

### 2. Últimos Items Creados
```
GET /api/inventario/items/ultimos
```

**Respuesta:** Lista de los últimos items agregados al inventario

### 3. Tipos de Items
```
GET /api/inventario/items/tipos
```

**Respuesta:** Lista de tipos de items disponibles (producto, servicio, etc.)

### 4. Consultar Existencias
```
GET /api/inventario/items/existencias
```

**Parámetros opcionales:**
- `bodegaId`: ID de la bodega
- `itemId`: ID del item

**Ejemplo:**
```python
# Consultar existencias de un item específico en una bodega
params = {
    "bodegaId": 242,
    "itemId": 698539
}

response = requests.get(
    "https://api.dynamiaerp.co/api/inventario/items/existencias",
    headers=headers,
    params=params
)

existencias = response.json()
```

### 5. Marcas
```
GET /api/inventario/marcas
```

**Respuesta:** Lista de marcas de productos

### 6. Líneas de Productos
```
GET /api/inventario/lineas
```

**Respuesta:** Lista de líneas o categorías de productos

### 7. Fabricantes
```
GET /api/inventario/fabricantes
```

**Respuesta:** Lista de fabricantes

### 8. Bodegas
```
GET /api/inventario/bodegas
```

**Respuesta:** Lista de bodegas disponibles

### 9. Presentaciones
```
GET /api/inventario/presentaciones
```

**Respuesta:** Lista de presentaciones de productos

### 10. Grupos de Presentaciones
```
GET /api/inventario/presentaciones/grupos
```

**Respuesta:** Lista de grupos de presentaciones

## 📊 Estructura de un Item

```json
{
  "id": 698539,
  "codigo": "ET514R",
  "nombre": "PAPEL CONTAC ROJO 45CM x 3MTS",
  "descripcion": "Papel contact rojo para forrar",
  "precio": 15000.00,
  "estado": "ACTIVO",
  "tipo": {
    "id": 1,
    "nombre": "PRODUCTO"
  },
  "marca": {
    "id": 123,
    "nombre": "ETERNA"
  },
  "linea": {
    "id": 456,
    "nombre": "PAPELERIA"
  },
  "bodega": {
    "id": 242,
    "nombre": "CARTAGENA"
  }
}
```

## 🔍 Casos de Uso

### Caso 1: Listar Todos los Productos

```python
from CODE.scripts.consultar_inventario_dynamia import DynamiaInventarioClient

# Crear cliente
client = DynamiaInventarioClient(
    token="tk80fddb468262bcf5734f1c25f0724c6c6edcbee12cbff8fbde9948879e03650e"
)

# Obtener todos los items
items = client.get_all_items()

# Mostrar información
for item in items:
    print(f"{item['nombre']} - ${item.get('precio', 0):,.2f}")
```

### Caso 2: Buscar Producto por Nombre

```python
# Buscar productos que contengan "papel"
resultados = client.buscar_item_por_nombre("papel")

for item in resultados:
    print(f"- {item['nombre']} (Código: {item['codigo']})")
```

### Caso 3: Buscar Producto por Código

```python
# Buscar producto específico por código
item = client.buscar_item_por_codigo("ET514R")

if item:
    print(f"Producto encontrado: {item['nombre']}")
    print(f"Precio: ${item['precio']:,.2f}")
```

### Caso 4: Consultar Existencias de un Producto

```python
# Consultar existencias en bodega específica
existencias = client.get_existencias(
    bodega_id=242,  # ID de bodega CARTAGENA
    item_id=698539   # ID del producto
)

for existencia in existencias:
    print(f"Cantidad disponible: {existencia.get('cantidad', 0)}")
```

### Caso 5: Listar Productos por Categoría

```python
# Obtener todas las líneas de productos
lineas = client.get_lineas()

# Obtener todos los items
items = client.get_all_items()

# Filtrar por línea específica
linea_id = 456  # ID de la línea "PAPELERIA"
productos_papeleria = [
    item for item in items 
    if item.get('linea', {}).get('id') == linea_id
]

print(f"Productos de papelería: {len(productos_papeleria)}")
```

### Caso 6: Exportar Inventario a JSON

```python
import json

# Obtener todos los items
items = client.get_all_items()

# Guardar en archivo JSON
with open('inventario_completo.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, indent=2, ensure_ascii=False)

print(f"✓ Inventario exportado: {len(items)} items")
```

### Caso 7: Obtener Items con Precio Mayor a X

```python
# Obtener todos los items
items = client.get_all_items()

# Filtrar por precio
precio_minimo = 10000
items_caros = [
    item for item in items 
    if item.get('precio', 0) >= precio_minimo
]

print(f"Items con precio >= ${precio_minimo:,.0f}: {len(items_caros)}")
```

## 🚀 Script Interactivo

Hemos creado un script interactivo para consultar el inventario:

```bash
cd CODE
python scripts/consultar_inventario_dynamia.py
```

**Opciones disponibles:**
1. Listar todos los items
2. Últimos items creados
3. Tipos de items
4. Marcas
5. Líneas de productos
6. Bodegas
7. Consultar existencias
8. Buscar item por nombre
9. Buscar item por código
10. Guardar inventario completo en JSON
0. Salir

## 📝 Integración con Sistema de Paquetería

### Sincronizar Paquetes como Productos

Si quieres sincronizar los paquetes del sistema de paquetería con DynamiaERP:

```python
# 1. Obtener paquetes del sistema local
paquetes_locales = [
    {"nombre": "Paquete Premium", "precio": 100000},
    {"nombre": "Paquete Básico", "precio": 50000},
    {"nombre": "Paquete Express", "precio": 150000}
]

# 2. Obtener items de DynamiaERP
items_dynamia = client.get_all_items()

# 3. Verificar si ya existen
for paquete in paquetes_locales:
    existe = any(
        item['nombre'] == paquete['nombre'] 
        for item in items_dynamia
    )
    
    if not existe:
        print(f"Paquete '{paquete['nombre']}' no existe en DynamiaERP")
        # Aquí podrías crear el item usando POST /api/inventario/items
```

### Usar Items de DynamiaERP en Ventas

Cuando crees una venta, puedes referenciar los items del inventario:

```python
# Buscar el item en DynamiaERP
item = client.buscar_item_por_nombre("Paquete Premium")[0]

# Crear venta con el item
venta = {
    "sucursalId": 242,
    "cliente": {"id": 123},
    "detalles": [
        {
            "itemId": item['id'],  # ID del item en DynamiaERP
            "descripcion": item['nombre'],
            "cantidad": 1,
            "precio": item['precio']
        }
    ]
}
```

## 🔧 Funciones Útiles

### Función para Buscar Múltiples Items

```python
def buscar_items_por_codigos(codigos: list) -> list:
    """Buscar múltiples items por sus códigos"""
    client = DynamiaInventarioClient(token=os.getenv('DYNAMIA_TOKEN'))
    items = client.get_all_items()
    
    resultados = []
    for codigo in codigos:
        item = next((i for i in items if i.get('codigo') == codigo), None)
        if item:
            resultados.append(item)
    
    return resultados

# Uso
codigos = ["ET514R", "ET514B", "ET514V"]
items = buscar_items_por_codigos(codigos)
```

### Función para Obtener Items por Rango de Precio

```python
def items_por_rango_precio(precio_min: float, precio_max: float) -> list:
    """Obtener items en un rango de precio"""
    client = DynamiaInventarioClient(token=os.getenv('DYNAMIA_TOKEN'))
    items = client.get_all_items()
    
    return [
        item for item in items 
        if precio_min <= item.get('precio', 0) <= precio_max
    ]

# Uso
items = items_por_rango_precio(10000, 50000)
```

### Función para Agrupar Items por Marca

```python
from collections import defaultdict

def agrupar_por_marca() -> dict:
    """Agrupar items por marca"""
    client = DynamiaInventarioClient(token=os.getenv('DYNAMIA_TOKEN'))
    items = client.get_all_items()
    
    agrupados = defaultdict(list)
    for item in items:
        marca = item.get('marca', {}).get('nombre', 'Sin marca')
        agrupados[marca].append(item)
    
    return dict(agrupados)

# Uso
items_por_marca = agrupar_por_marca()
for marca, items in items_por_marca.items():
    print(f"{marca}: {len(items)} items")
```

## 📊 Estadísticas del Inventario

```python
def estadisticas_inventario():
    """Obtener estadísticas del inventario"""
    client = DynamiaInventarioClient(token=os.getenv('DYNAMIA_TOKEN'))
    items = client.get_all_items()
    
    total_items = len(items)
    items_con_precio = [i for i in items if i.get('precio', 0) > 0]
    precio_promedio = sum(i['precio'] for i in items_con_precio) / len(items_con_precio)
    precio_max = max(i['precio'] for i in items_con_precio)
    precio_min = min(i['precio'] for i in items_con_precio)
    
    print(f"Total de items: {total_items}")
    print(f"Items con precio: {len(items_con_precio)}")
    print(f"Precio promedio: ${precio_promedio:,.2f}")
    print(f"Precio máximo: ${precio_max:,.2f}")
    print(f"Precio mínimo: ${precio_min:,.2f}")
```

## ⚠️ Notas Importantes

1. **Autenticación:** Todos los endpoints requieren el token de autenticación
2. **Rate Limiting:** Ten en cuenta posibles límites de peticiones
3. **Caché:** Considera cachear los resultados para mejorar performance
4. **Paginación:** Algunos endpoints pueden soportar paginación (verificar documentación)

## 📞 Soporte

Si necesitas ayuda con el inventario:
- **Email:** devteam@dynamiasoluciones.com
- **Documentación:** http://api.pos.dynamiaerp.co/swagger-ui/index.html

---

**Última actualización:** 2026-01-13
