# 🛠️ Ejemplos de Desarrollo - Dashboard

## Guía para Desarrolladores

Esta guía contiene ejemplos prácticos para extender y personalizar el dashboard.

---

## 📋 Tabla de Contenidos

1. [Agregar Nuevos Widgets](#agregar-nuevos-widgets)
2. [Crear Nuevos Filtros](#crear-nuevos-filtros)
3. [Agregar Formatos de Exportación](#agregar-formatos-de-exportación)
4. [Integrar Gráficos Avanzados](#integrar-gráficos-avanzados)
5. [Crear Endpoints Personalizados](#crear-endpoints-personalizados)

---

## 1. Agregar Nuevos Widgets

### Ejemplo: Widget de "Clientes Activos"

**Frontend** (`dashboard_improved.html`):

```html
<!-- Agregar después de los widgets existentes -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
        <div>
            <p class="text-sm font-medium text-gray-500">Clientes Activos</p>
            <p class="text-3xl font-bold text-indigo-600 mt-2" x-text="stats.customers?.active || 0"></p>
            <p class="text-xs text-gray-500 mt-1">Con paquetes activos</p>
        </div>
        <div class="bg-indigo-100 rounded-lg p-3">
            <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
        </div>
    </div>
</div>
```

**Backend** (`api.py`):

```python
# En el endpoint /api/dashboard/stats, agregar:

# Clientes con paquetes activos
active_customers = db.query(Customer).join(PackageAnnouncementNew).filter(
    PackageAnnouncementNew.is_processed == False
).distinct().count()

# En el return, agregar:
"customers": {
    "total": total_customers,
    "active": active_customers  # Nueva métrica
}
```

---

## 2. Crear Nuevos Filtros

### Ejemplo: Filtro por Rango de Fechas

**Frontend** (`dashboard_improved.html`):

```html
<!-- Agregar en la sección de filtros -->
<div class="flex gap-2">
    <input x-model="dateFrom" 
           @change="loadPackages(1)"
           type="date"
           class="px-4 py-2.5 border border-gray-300 rounded-lg focus:border-papyrus-blue">
    <span class="flex items-center text-gray-500">hasta</span>
    <input x-model="dateTo" 
           @change="loadPackages(1)"
           type="date"
           class="px-4 py-2.5 border border-gray-300 rounded-lg focus:border-papyrus-blue">
</div>
```

**JavaScript** (en el componente Alpine.js):

```javascript
// Agregar en data:
dateFrom: '',
dateTo: '',

// Modificar loadPackages:
async loadPackages(page = 1) {
    // ... código existente ...
    
    if (this.dateFrom) {
        params.append('date_from', this.dateFrom);
    }
    
    if (this.dateTo) {
        params.append('date_to', this.dateTo);
    }
    
    // ... resto del código ...
}
```

**Backend** (`api.py`):

```python
from datetime import datetime

@router.get("/dashboard/packages")
async def get_dashboard_packages(
    page: int = 1,
    limit: int = 8,
    search: str = None,
    status: str = None,
    date_from: str = None,  # Nuevo parámetro
    date_to: str = None,    # Nuevo parámetro
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    # ... código existente ...
    
    # Filtro por rango de fechas
    if date_from:
        date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        query = query.filter(PackageAnnouncementNew.announced_at >= date_from_obj)
    
    if date_to:
        date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        # Agregar 1 día para incluir todo el día
        date_to_obj = date_to_obj.replace(hour=23, minute=59, second=59)
        query = query.filter(PackageAnnouncementNew.announced_at <= date_to_obj)
    
    # ... resto del código ...
```

---

## 3. Agregar Formatos de Exportación

### Ejemplo: Exportación a Excel (.xlsx)

**Instalar dependencia**:
```bash
pip install openpyxl
```

**Backend** (`api.py`):

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
import io

@router.get("/dashboard/export")
async def export_dashboard_data(
    format: str = "csv",
    # ... parámetros existentes ...
):
    # ... código existente ...
    
    elif format.lower() == "excel":
        # Crear workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "Paquetes"
        
        # Estilo de encabezados
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        # Escribir encabezados
        headers = ['ID', 'Cliente', 'Teléfono', 'Número de Guía', 
                   'Código de Tracking', 'Estado', 'Fecha de Anuncio']
        
        for col, header in enumerate(headers, start=1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center')
        
        # Escribir datos
        for row, pkg in enumerate(packages, start=2):
            ws.cell(row=row, column=1, value=str(pkg.id))
            ws.cell(row=row, column=2, value=pkg.customer_name)
            ws.cell(row=row, column=3, value=pkg.customer_phone)
            ws.cell(row=row, column=4, value=pkg.guide_number)
            ws.cell(row=row, column=5, value=pkg.tracking_code)
            ws.cell(row=row, column=6, value='PROCESADO' if pkg.is_processed else 'PENDIENTE')
            ws.cell(row=row, column=7, value=pkg.announced_at.strftime('%Y-%m-%d %H:%M:%S') if pkg.announced_at else '')
        
        # Ajustar ancho de columnas
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width
        
        # Guardar en memoria
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        filename = f"paquetes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
```

**Frontend** (agregar opción en menú):

```html
<a @click="exportData('excel'); open = false" 
   class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 cursor-pointer">
    Exportar como Excel
</a>
```

---

## 4. Integrar Gráficos Avanzados

### Ejemplo: Gráfico de Líneas con Chart.js

**Agregar Chart.js** (en `base.html` o en el template):

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

**Frontend** (`dashboard_improved.html`):

```html
<!-- Agregar después de los widgets -->
<div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Tendencia de Paquetes (Últimos 7 Días)</h3>
    <canvas id="trendChart" height="80"></canvas>
</div>
```

**JavaScript**:

```javascript
// En el componente Alpine.js, agregar:
chartInstance: null,

async loadTrendData() {
    try {
        const response = await fetch('/api/dashboard/trend?days=7', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            this.renderTrendChart(data.trend);
        }
    } catch (error) {
        console.error('Error loading trend data:', error);
    }
},

renderTrendChart(trendData) {
    const ctx = document.getElementById('trendChart');
    
    // Destruir gráfico anterior si existe
    if (this.chartInstance) {
        this.chartInstance.destroy();
    }
    
    this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.map(d => d.date),
            datasets: [{
                label: 'Paquetes Anunciados',
                data: trendData.map(d => d.count),
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
},

// Llamar en init():
init() {
    this.loadStats();
    this.loadPackages(1);
    this.loadTrendData();  // Nueva llamada
}
```

**Backend** (nuevo endpoint):

```python
@router.get("/dashboard/trend")
async def get_dashboard_trend(
    days: int = 7,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener tendencia de paquetes por día"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, cast, Date
        
        # Calcular rango de fechas
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query agrupado por fecha
        trend_data = db.query(
            cast(PackageAnnouncementNew.announced_at, Date).label('date'),
            func.count(PackageAnnouncementNew.id).label('count')
        ).filter(
            PackageAnnouncementNew.announced_at >= start_date
        ).group_by(
            cast(PackageAnnouncementNew.announced_at, Date)
        ).order_by('date').all()
        
        # Formatear respuesta
        trend = [
            {
                "date": row.date.strftime('%Y-%m-%d'),
                "count": row.count
            }
            for row in trend_data
        ]
        
        return {
            "success": True,
            "trend": trend
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo tendencia: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tendencia: {str(e)}"
        )
```

---

## 5. Crear Endpoints Personalizados

### Ejemplo: Endpoint de Estadísticas por Cliente

**Backend** (`api.py`):

```python
@router.get("/dashboard/customer-stats")
async def get_customer_stats(
    customer_id: str = None,
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    """Obtener estadísticas de un cliente específico"""
    try:
        from app.models.customer import Customer
        
        if not customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="customer_id es requerido"
            )
        
        # Buscar cliente
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )
        
        # Estadísticas del cliente
        total_packages = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.customer_phone == customer.phone
        ).count()
        
        processed_packages = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.customer_phone == customer.phone,
            PackageAnnouncementNew.is_processed == True
        ).count()
        
        pending_packages = total_packages - processed_packages
        
        # Último paquete
        last_package = db.query(PackageAnnouncementNew).filter(
            PackageAnnouncementNew.customer_phone == customer.phone
        ).order_by(PackageAnnouncementNew.announced_at.desc()).first()
        
        return {
            "success": True,
            "customer": {
                "id": str(customer.id),
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email
            },
            "stats": {
                "total_packages": total_packages,
                "processed_packages": processed_packages,
                "pending_packages": pending_packages,
                "last_package_date": last_package.announced_at.isoformat() if last_package else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas del cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )
```

**Uso desde Frontend**:

```javascript
async loadCustomerStats(customerId) {
    try {
        const response = await fetch(`/api/dashboard/customer-stats?customer_id=${customerId}`, {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            console.log('Customer stats:', data);
            // Mostrar en modal o sección dedicada
        }
    } catch (error) {
        console.error('Error loading customer stats:', error);
    }
}
```

---

## 🔧 Utilidades Comunes

### Formatear Fechas

```javascript
function formatDate(dateString, format = 'short') {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    
    const formats = {
        short: {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        },
        long: {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        },
        time: {
            hour: '2-digit',
            minute: '2-digit'
        }
    };
    
    return date.toLocaleDateString('es-CO', formats[format]);
}
```

### Debounce Helper

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Uso:
const debouncedSearch = debounce((term) => {
    console.log('Searching for:', term);
}, 500);
```

### Validar Permisos

```python
from functools import wraps
from fastapi import HTTPException, status

def require_role(*allowed_roles):
    """Decorador para validar roles de usuario"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User, **kwargs):
            if current_user.role.value not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Acceso denegado. Roles permitidos: {', '.join(allowed_roles)}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Uso:
@router.get("/dashboard/admin-only")
@require_role("ADMIN")
async def admin_only_endpoint(
    current_user: User = Depends(get_current_active_user_from_cookies),
    db: Session = Depends(get_db)
):
    # Solo accesible para ADMIN
    pass
```

---

## 📚 Recursos Adicionales

### Librerías Recomendadas

**Frontend**:
- [Chart.js](https://www.chartjs.org/) - Gráficos interactivos
- [ApexCharts](https://apexcharts.com/) - Gráficos avanzados
- [Alpine.js](https://alpinejs.dev/) - Framework reactivo ligero
- [Tailwind CSS](https://tailwindcss.com/) - Estilos utility-first

**Backend**:
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderno
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM para Python
- [Pandas](https://pandas.pydata.org/) - Análisis de datos
- [openpyxl](https://openpyxl.readthedocs.io/) - Manipulación de Excel

### Documentación Oficial

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Alpine.js Docs](https://alpinejs.dev/start-here)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Chart.js Docs](https://www.chartjs.org/docs/latest/)

---

## 🐛 Debugging

### Habilitar Logs Detallados

**Backend**:
```python
import logging

# En el inicio de tu archivo
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# En tus funciones
logger.debug(f"Query params: {params}")
logger.info(f"Processing {len(packages)} packages")
logger.error(f"Error occurred: {str(e)}", exc_info=True)
```

**Frontend**:
```javascript
// En el componente Alpine.js
init() {
    // Habilitar modo debug
    window.dashboardDebug = true;
    
    if (window.dashboardDebug) {
        console.log('Dashboard initialized');
        console.log('Initial state:', this.$data);
    }
}

// En funciones
async loadPackages(page = 1) {
    if (window.dashboardDebug) {
        console.log('Loading packages:', { page, searchTerm: this.searchTerm });
    }
    // ... resto del código
}
```

---

## ✅ Testing

### Test de Endpoint

```python
# tests/test_dashboard_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_dashboard_packages():
    response = client.get("/api/dashboard/packages?page=1&limit=8")
    assert response.status_code == 200
    data = response.json()
    assert "packages" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1

def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "packages" in data["stats"]
```

---

**¡Feliz desarrollo!** 🚀
