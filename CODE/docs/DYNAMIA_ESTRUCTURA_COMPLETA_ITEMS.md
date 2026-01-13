# Estructura Completa de Items - DynamiaERP

## 📋 Información Disponible de Cada Item

### ✅ Campos Principales (Siempre Disponibles)

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | Integer | ID único del item | 698605 |
| `codigo` | String | Código del producto | "211129" |
| `nombre` | String | Nombre completo del producto | "1/4 DE LAMINA ICOPOR 10MM 50x50" |
| `accountId` | Integer | ID de la cuenta | 128 |

### 💰 Información de Precios y Costos

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `precioVenta` | Float | Precio de venta al público | 1400.0 |
| `costoAproximado` | Float | Costo aproximado del producto | 900.0 |
| `costoEfectivo` | Float | Costo efectivo | 900.0 |
| `precioFijo` | Boolean | Si el precio es fijo | false |
| `precioVentaCalculado` | Boolean | Si el precio se calcula automáticamente | false |
| `impuestoIncluido` | Boolean | Si el precio incluye impuestos | false |
| `porcentajeImpuesto` | Float | Porcentaje de impuesto | 0.0 |
| `exentoImpuestos` | Boolean | Si está exento de impuestos | false |
| `tienePrecioTemp` | Boolean | Si tiene precio temporal | true |
| `usarPrecioSucursales` | Boolean | Si usa precios por sucursal | false |

### 📦 Información de Inventario

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `existenciasTotales` | Float | Existencias totales | 0.0 |
| `existenciasMinimas` | Float | Existencias mínimas | 0.0 |
| `existenciasMaximas` | Float | Existencias máximas | 0.0 |
| `existenciasExternas` | Float | Existencias externas | 0.0 |

### 🏷️ Clasificación y Categorización

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `tipo` | Object | Tipo de item (PRODUCTO, SERVICIO, etc.) | {"id": 502, "name": "PRODUCTO"} |
| `tipo.id` | Integer | ID del tipo | 502 |
| `tipo.name` | String | Nombre del tipo | "PRODUCTO" |
| `lineaPrincipal` | Object | Línea principal del producto | {"id": 26097, "name": "211 - PAPELERIA / ESCOLAR"} |
| `lineaPrincipal.id` | Integer | ID de la línea | 26097 |
| `lineaPrincipal.name` | String | Nombre de la línea | "211 - PAPELERIA / ESCOLAR" |
| `nombreLinea` | String | Nombre de la línea (directo) | "211 - PAPELERIA / ESCOLAR" |
| `marca` | Object | Marca del producto | {"id": 4710, "name": "G"} |
| `marca.id` | Integer | ID de la marca | 4710 |
| `marca.name` | String | Nombre de la marca | "G" |

### 📝 Información Descriptiva

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `referencia` | String | Referencia del producto | "" |
| `descripcion` | String | Descripción detallada | "" |
| `codigoBarra` | String | Código de barras | "PYGA" |
| `codigoReferencia` | String | Código de referencia | "211129" |
| `codigoLector` | String | Código para lector | "PYGA" |
| `externalRef` | String | Referencia externa | "15640" |

### ✅ Estados y Configuraciones

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `activo` | Boolean | Si el producto está activo | true |
| `vendible` | Boolean | Si se puede vender | true |
| `comprable` | Boolean | Si se puede comprar | true |
| `trasladable` | Boolean | Si se puede trasladar | true |
| `visualizableWeb` | Boolean | Si es visible en web | true |
| `destacado` | Boolean | Si es producto destacado | false |
| `permitePedidos` | Boolean | Si permite pedidos | false |

### 🛒 Configuración de Ventas

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `cantidadEnVentas` | Float | Cantidad por defecto en ventas | 1.0 |
| `cantidadManual` | Boolean | Si la cantidad es manual | false |
| `ordenEnVentas` | Integer | Orden en ventas | 0 |
| `permiteDescuentos` | Boolean | Si permite descuentos | false |
| `bloquearDescuentos` | Boolean | Si bloquea descuentos | false |
| `porcentajeDescuento` | Float | Porcentaje de descuento | 0.0 |
| `modoPrecio` | String | Modo de precio | "POR_DEFECTO" |

### 🍽️ Configuración de Restaurante/Domicilios

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `domicilios` | Boolean | Si aplica para domicilios | true |
| `paraLlevar` | Boolean | Si es para llevar | true |
| `bebidaAlcoholica` | Boolean | Si es bebida alcohólica | false |

### 💼 Comisiones

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `comisionable` | Boolean | Si genera comisión | false |
| `descontarEnComisiones` | Boolean | Si se descuenta en comisiones | false |
| `porcentajeComision` | Float | Porcentaje de comisión | 0.0 |

### 🔧 Configuraciones Avanzadas

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `compuesto` | Boolean | Si es producto compuesto | false |
| `compuestoDinamico` | Boolean | Si es compuesto dinámico | false |
| `subitems` | Array | Lista de subitems | [] |
| `multiPresentaciones` | Boolean | Si tiene múltiples presentaciones | false |
| `presentacionesObligatorias` | Boolean | Si las presentaciones son obligatorias | false |
| `usaSeriales` | Boolean | Si usa números de serie | false |
| `usarBalanza` | Boolean | Si usa balanza | false |
| `autolotes` | Boolean | Si usa lotes automáticos | false |
| `usarEnTransformaciones` | Boolean | Si se usa en transformaciones | false |
| `preguntasObligatorias` | Array | Preguntas obligatorias | [] |
| `usarPreguntasObligatorias` | Boolean | Si usa preguntas obligatorias | false |

### 📊 Información de Gestión

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `porcentajePMG` | Float | Porcentaje PMG | 0.0 |
| `nombreGenerado` | Boolean | Si el nombre es generado | false |
| `autocreadoProveedor` | Boolean | Si fue autocreado por proveedor | false |

### 📅 Auditoría y Fechas

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `creationDate` | String | Fecha de creación | "11-08-2025" |
| `creationTime` | String | Hora de creación | "07:50:38" |
| `creationTimestamp` | String | Timestamp de creación | "2025-08-11 07:50:38" |
| `creationInstant` | String | Instant de creación (ISO) | "2025-08-11T12:50:38Z" |
| `creationDateZoned` | String | Fecha con zona horaria | "2025-08-11T07:50:38-05:00" |
| `creator` | String | Usuario creador | "anonimo" |
| `lastUpdate` | String | Última actualización | "2025-08-11 07:49:41" |
| `lastUpdateInstant` | String | Instant de actualización | "2025-08-11T12:49:41Z" |
| `lastUpdateZoned` | String | Actualización con zona horaria | "2025-08-11T07:49:41-05:00" |

---

## 📊 Resumen de Campos por Categoría

### Campos Esenciales para PAQUETEX (Mínimo Requerido)
```python
{
    "id": 698605,                    # ID único
    "codigo": "211129",              # Código del producto
    "nombre": "Producto X",          # Nombre
    "precioVenta": 1400.0,          # Precio
    "activo": true,                  # Estado
    "vendible": true                 # Si se puede vender
}
```

### Campos Recomendados para PAQUETEX
```python
{
    # Esenciales
    "id": 698605,
    "codigo": "211129",
    "nombre": "Producto X",
    
    # Precios
    "precioVenta": 1400.0,
    "costoAproximado": 900.0,
    "impuestoIncluido": false,
    "porcentajeImpuesto": 0.0,
    
    # Clasificación
    "tipo": {"id": 502, "name": "PRODUCTO"},
    "marca": {"id": 4710, "name": "G"},
    "lineaPrincipal": {"id": 26097, "name": "PAPELERIA"},
    
    # Inventario
    "existenciasTotales": 0.0,
    
    # Estados
    "activo": true,
    "vendible": true,
    "visualizableWeb": true,
    
    # Descripción
    "descripcion": "Descripción del producto",
    "codigoBarra": "PYGA"
}
```

### Campos Completos (Todo Disponible)
Ver estructura JSON completa arriba con **60+ campos**.

---

## 🎯 Campos Útiles para Diferentes Funcionalidades

### Para Catálogo de Productos
- `id`, `codigo`, `nombre`
- `precioVenta`, `costoAproximado`
- `descripcion`, `referencia`
- `marca.name`, `lineaPrincipal.name`
- `activo`, `vendible`, `visualizableWeb`
- `destacado`

### Para Control de Inventario
- `existenciasTotales`, `existenciasMinimas`, `existenciasMaximas`
- `existenciasExternas`
- `trasladable`, `comprable`
- `usaSeriales`, `autolotes`

### Para Ventas
- `precioVenta`, `impuestoIncluido`, `porcentajeImpuesto`
- `vendible`, `activo`
- `cantidadEnVentas`, `cantidadManual`
- `permiteDescuentos`, `porcentajeDescuento`
- `modoPrecio`

### Para Facturación
- `precioVenta`, `costoAproximado`
- `impuestoIncluido`, `porcentajeImpuesto`, `exentoImpuestos`
- `codigo`, `codigoBarra`, `codigoReferencia`

### Para Domicilios/Delivery
- `domicilios`, `paraLlevar`
- `bebidaAlcoholica`

### Para Comisiones
- `comisionable`, `porcentajeComision`
- `descontarEnComisiones`

---

## 💡 Ejemplo de Uso en PAQUETEX

### Modelo de Datos Sugerido para PAQUETEX

```python
# models/product.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from database import Base

class Product(Base):
    __tablename__ = "products"
    
    # IDs
    id = Column(Integer, primary_key=True)
    dynamia_id = Column(Integer, unique=True, index=True)  # ID de DynamiaERP
    
    # Información básica
    codigo = Column(String(50), unique=True, index=True)
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text)
    referencia = Column(String(100))
    
    # Precios
    precio_venta = Column(Float, nullable=False)
    costo_aproximado = Column(Float)
    impuesto_incluido = Column(Boolean, default=False)
    porcentaje_impuesto = Column(Float, default=0.0)
    
    # Clasificación
    tipo_id = Column(Integer)
    tipo_nombre = Column(String(100))
    marca_id = Column(Integer)
    marca_nombre = Column(String(100))
    linea_id = Column(Integer)
    linea_nombre = Column(String(255))
    
    # Inventario
    existencias_totales = Column(Float, default=0.0)
    existencias_minimas = Column(Float, default=0.0)
    existencias_maximas = Column(Float, default=0.0)
    
    # Estados
    activo = Column(Boolean, default=True)
    vendible = Column(Boolean, default=True)
    visible_web = Column(Boolean, default=True)
    destacado = Column(Boolean, default=False)
    
    # Códigos
    codigo_barra = Column(String(100))
    codigo_referencia = Column(String(100))
    external_ref = Column(String(100))
    
    # Configuración de ventas
    permite_descuentos = Column(Boolean, default=True)
    porcentaje_descuento = Column(Float, default=0.0)
    
    # Domicilios
    aplica_domicilios = Column(Boolean, default=True)
    para_llevar = Column(Boolean, default=True)
    
    # Auditoría
    fecha_sincronizacion = Column(DateTime)
    ultima_actualizacion_dynamia = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### Servicio de Sincronización

```python
# services/product_sync_service.py
from typing import List, Dict, Any
import requests
from datetime import datetime
from models.product import Product
from database import SessionLocal

class ProductSyncService:
    """Servicio para sincronizar productos de DynamiaERP"""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.dynamiaerp.co"
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def fetch_all_products(self) -> List[Dict[str, Any]]:
        """Obtener todos los productos de DynamiaERP"""
        response = requests.get(
            f"{self.base_url}/api/inventario/items",
            headers=self.get_headers()
        )
        response.raise_for_status()
        data = response.json()
        return data.get('data', [])
    
    def map_dynamia_to_local(self, dynamia_item: Dict[str, Any]) -> Dict[str, Any]:
        """Mapear item de DynamiaERP a modelo local"""
        return {
            "dynamia_id": dynamia_item.get('id'),
            "codigo": dynamia_item.get('codigo'),
            "nombre": dynamia_item.get('nombre'),
            "descripcion": dynamia_item.get('descripcion', ''),
            "referencia": dynamia_item.get('referencia', ''),
            
            # Precios
            "precio_venta": dynamia_item.get('precioVenta', 0.0),
            "costo_aproximado": dynamia_item.get('costoAproximado', 0.0),
            "impuesto_incluido": dynamia_item.get('impuestoIncluido', False),
            "porcentaje_impuesto": dynamia_item.get('porcentajeImpuesto', 0.0),
            
            # Clasificación
            "tipo_id": dynamia_item.get('tipo', {}).get('id'),
            "tipo_nombre": dynamia_item.get('tipo', {}).get('name'),
            "marca_id": dynamia_item.get('marca', {}).get('id'),
            "marca_nombre": dynamia_item.get('marca', {}).get('name'),
            "linea_id": dynamia_item.get('lineaPrincipal', {}).get('id'),
            "linea_nombre": dynamia_item.get('lineaPrincipal', {}).get('name'),
            
            # Inventario
            "existencias_totales": dynamia_item.get('existenciasTotales', 0.0),
            "existencias_minimas": dynamia_item.get('existenciasMinimas', 0.0),
            "existencias_maximas": dynamia_item.get('existenciasMaximas', 0.0),
            
            # Estados
            "activo": dynamia_item.get('activo', True),
            "vendible": dynamia_item.get('vendible', True),
            "visible_web": dynamia_item.get('visualizableWeb', True),
            "destacado": dynamia_item.get('destacado', False),
            
            # Códigos
            "codigo_barra": dynamia_item.get('codigoBarra', ''),
            "codigo_referencia": dynamia_item.get('codigoReferencia', ''),
            "external_ref": dynamia_item.get('externalRef', ''),
            
            # Configuración
            "permite_descuentos": dynamia_item.get('permiteDescuentos', True),
            "porcentaje_descuento": dynamia_item.get('porcentajeDescuento', 0.0),
            
            # Domicilios
            "aplica_domicilios": dynamia_item.get('domicilios', True),
            "para_llevar": dynamia_item.get('paraLlevar', True),
            
            # Auditoría
            "fecha_sincronizacion": datetime.now(),
            "ultima_actualizacion_dynamia": dynamia_item.get('lastUpdate')
        }
    
    def sync_products(self, filters: Dict[str, Any] = None):
        """Sincronizar productos de DynamiaERP a base de datos local"""
        db = SessionLocal()
        
        try:
            # Obtener productos de DynamiaERP
            dynamia_products = self.fetch_all_products()
            
            # Aplicar filtros si existen
            if filters:
                if filters.get('activo'):
                    dynamia_products = [p for p in dynamia_products if p.get('activo')]
                if filters.get('vendible'):
                    dynamia_products = [p for p in dynamia_products if p.get('vendible')]
            
            synced_count = 0
            updated_count = 0
            
            for dynamia_item in dynamia_products:
                # Mapear datos
                product_data = self.map_dynamia_to_local(dynamia_item)
                
                # Buscar si ya existe
                existing = db.query(Product).filter(
                    Product.dynamia_id == product_data['dynamia_id']
                ).first()
                
                if existing:
                    # Actualizar
                    for key, value in product_data.items():
                        setattr(existing, key, value)
                    updated_count += 1
                else:
                    # Crear nuevo
                    new_product = Product(**product_data)
                    db.add(new_product)
                    synced_count += 1
            
            db.commit()
            
            return {
                "success": True,
                "synced": synced_count,
                "updated": updated_count,
                "total": len(dynamia_products)
            }
            
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            db.close()
```

---

## 🎨 Vista de Productos en PAQUETEX

### Endpoint para Listar Productos

```python
# routes/products.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product

router = APIRouter()

@router.get("/products")
async def list_products(
    skip: int = 0,
    limit: int = 50,
    search: str = None,
    activo: bool = None,
    vendible: bool = None,
    categoria: str = None,
    db: Session = Depends(get_db)
):
    """Listar productos con filtros"""
    query = db.query(Product)
    
    # Filtros
    if activo is not None:
        query = query.filter(Product.activo == activo)
    if vendible is not None:
        query = query.filter(Product.vendible == vendible)
    if search:
        query = query.filter(
            Product.nombre.ilike(f"%{search}%") |
            Product.codigo.ilike(f"%{search}%")
        )
    if categoria:
        query = query.filter(Product.linea_nombre.ilike(f"%{categoria}%"))
    
    # Paginación
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "products": products
    }

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.post("/products/sync")
async def sync_products(db: Session = Depends(get_db)):
    """Sincronizar productos desde DynamiaERP"""
    from services.product_sync_service import ProductSyncService
    import os
    
    service = ProductSyncService(token=os.getenv('DYNAMIA_TOKEN'))
    result = service.sync_products(filters={"activo": True, "vendible": True})
    
    return result
```

---

## 📱 Template HTML para Visualizar Productos

```html
<!-- templates/products/list.html -->
<div class="products-container">
    <div class="products-header">
        <h2>Catálogo de Productos</h2>
        <button onclick="syncProducts()">Sincronizar con DynamiaERP</button>
    </div>
    
    <div class="products-filters">
        <input type="text" id="search" placeholder="Buscar por nombre o código...">
        <select id="categoria">
            <option value="">Todas las categorías</option>
            <!-- Categorías dinámicas -->
        </select>
        <button onclick="filterProducts()">Filtrar</button>
    </div>
    
    <div class="products-grid">
        {% for product in products %}
        <div class="product-card">
            <div class="product-header">
                <h3>{{ product.nombre }}</h3>
                <span class="product-code">{{ product.codigo }}</span>
            </div>
            
            <div class="product-info">
                <p class="product-price">${{ product.precio_venta | number_format }}</p>
                <p class="product-category">{{ product.linea_nombre }}</p>
                <p class="product-brand">{{ product.marca_nombre }}</p>
            </div>
            
            <div class="product-stock">
                <span>Existencias: {{ product.existencias_totales }}</span>
            </div>
            
            <div class="product-actions">
                <button onclick="addToSale({{ product.id }})">Agregar a Venta</button>
                <button onclick="viewDetails({{ product.id }})">Ver Detalles</button>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
```

---

**Última actualización:** 2026-01-13  
**Total de campos disponibles:** 60+  
**Estado:** ✅ Documentación completa
