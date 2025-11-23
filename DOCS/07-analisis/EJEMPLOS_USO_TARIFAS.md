# 📋 Ejemplos de Uso de Tarifas Base

## 🔍 Dónde están definidas las variables

Las variables de tarifas están definidas en:
- **Archivo de configuración**: `CODE/src/app/config.py` (líneas 58-70)
- **Archivo de ejemplo**: `CODE/env.example` (líneas 77-84)
- **Archivo real**: `CODE/.env` (debes crearlo si no existe)

## 📝 Cómo usar las tarifas en tu código

### Ejemplo 1: En una ruta/endpoint

```python
from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/tarifas")
async def obtener_tarifas():
    """Obtener tarifas desde .env"""
    return {
        "normal": settings.base_delivery_rate_normal,
        "extra_dimensioned": settings.base_delivery_rate_extra_dimensioned,
        "storage_per_day": settings.base_storage_rate,
        "currency": settings.currency
    }
```

### Ejemplo 2: En un servicio

```python
from app.config import settings
from decimal import Decimal

class MiServicio:
    def calcular_costo(self, tipo_paquete: str, dias_almacenamiento: int):
        # Obtener tarifa base según tipo
        if tipo_paquete == "NORMAL":
            tarifa_base = settings.base_delivery_rate_normal
        else:
            tarifa_base = settings.base_delivery_rate_extra_dimensioned
        
        # Calcular almacenamiento
        tarifa_almacenamiento = settings.base_storage_rate * dias_almacenamiento
        
        # Total
        total = tarifa_base + tarifa_almacenamiento
        
        return {
            "base": tarifa_base,
            "almacenamiento": tarifa_almacenamiento,
            "total": total
        }
```

### Ejemplo 3: En una función de cálculo

```python
from app.config import settings
from decimal import Decimal

def calcular_tarifa_paquete(tipo: str, dias: int = 0):
    """
    Calcular tarifa total de un paquete
    
    Args:
        tipo: "NORMAL" o "EXTRA_DIMENSIONADO"
        dias: Días de almacenamiento
    
    Returns:
        Dict con desglose de tarifas
    """
    # Tarifa base
    if tipo == "NORMAL":
        base = Decimal(str(settings.base_delivery_rate_normal))
    elif tipo == "EXTRA_DIMENSIONADO":
        base = Decimal(str(settings.base_delivery_rate_extra_dimensioned))
    else:
        base = Decimal(str(settings.base_delivery_rate_normal))  # Fallback
    
    # Almacenamiento
    storage_per_day = Decimal(str(settings.base_storage_rate))
    storage = storage_per_day * Decimal(str(dias))
    
    # Total
    total = base + storage
    
    return {
        "base_fee": float(base),
        "storage_fee": float(storage),
        "storage_days": dias,
        "total_amount": float(total),
        "currency": settings.currency
    }
```

### Ejemplo 4: En un template (pasando desde la vista)

```python
# En tu ruta/endpoint
from app.config import settings
from fastapi.templating import Jinja2Templates

@router.get("/mi-vista")
async def mi_vista(request: Request):
    context = {
        "tarifas": {
            "normal": settings.base_delivery_rate_normal,
            "extra": settings.base_delivery_rate_extra_dimensioned,
            "almacenamiento": settings.base_storage_rate
        }
    }
    return templates.TemplateResponse("mi_template.html", context)
```

```html
<!-- En tu template HTML -->
<div>
    <p>Tarifa Normal: ${{ tarifas.normal }} COP</p>
    <p>Tarifa Extra: ${{ tarifas.extra }} COP</p>
    <p>Almacenamiento por día: ${{ tarifas.almacenamiento }} COP</p>
</div>
```

## 🔧 Variables disponibles

| Variable en Python | Variable en .env | Valor por defecto | Descripción |
|-------------------|------------------|-------------------|-------------|
| `settings.base_storage_rate` | `BASE_STORAGE_RATE` | 1000 | Tarifa diaria de almacenamiento (COP) |
| `settings.base_delivery_rate_normal` | `BASE_DELIVERY_RATE_NORMAL` | 1500 | Tarifa base para paquetes normales (COP) |
| `settings.base_delivery_rate_extra_dimensioned` | `BASE_DELIVERY_RATE_EXTRA_DIMENSIONED` | 2000 | Tarifa base para paquetes extra dimensionados (COP) |
| `settings.overtime_rate_per_24h` | `OVERTIME_RATE_PER_24H` | 1000 | Tarifa adicional por cada 24 horas extra (COP) |
| `settings.currency` | `CURRENCY` | COP | Moneda |

## 📍 Ubicación del archivo .env

El archivo `.env` debe estar en:
```
CODE/.env
```

Si no existe, créalo copiando el ejemplo:
```bash
cp CODE/env.example CODE/.env
```

## ✅ Ejemplo real del código

Aquí está cómo se usa en el código real del proyecto:

```python
# En CODE/src/app/routes/packages.py (línea 1200)
@router.get("/rates/dynamic")
async def get_dynamic_rates():
    """Obtener tarifas dinámicas desde .env"""
    from app.config import settings
    
    rates = {
        "normal": int(settings.base_delivery_rate_normal),
        "extra_dimensioned": int(settings.base_delivery_rate_extra_dimensioned),
        "storage_per_day": int(settings.base_storage_rate),
        "currency": settings.currency
    }
    
    return {
        "success": True,
        "rates": rates,
        "message": "Tarifas obtenidas dinámicamente desde .env"
    }
```

```python
# En CODE/src/app/services/package_state_service.py (línea 533)
from app.config import settings

if package_type_value == "NORMAL":
    base_fee = Decimal(str(settings.base_delivery_rate_normal))
elif package_type_value == "EXTRA_DIMENSIONADO":
    base_fee = Decimal(str(settings.base_delivery_rate_extra_dimensioned))

storage_fee_per_day = Decimal(str(settings.base_storage_rate))
storage_fee = storage_fee_per_day * storage_days
```

## 🚀 Cómo cambiar las tarifas

1. Edita el archivo `CODE/.env`
2. Modifica los valores:
   ```env
   BASE_STORAGE_RATE=1500
   BASE_DELIVERY_RATE_NORMAL=2000
   BASE_DELIVERY_RATE_EXTRA_DIMENSIONED=3000
   ```
3. Reinicia el servidor para que los cambios surtan efecto

## ⚠️ Importante

- Las variables se leen **una vez al iniciar el servidor**
- Si cambias el `.env`, **debes reiniciar el servidor**
- Los valores por defecto se usan si la variable no existe en `.env`
- Las variables en el sistema operativo tienen prioridad sobre el archivo `.env`

