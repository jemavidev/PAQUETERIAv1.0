# Sistema de Paginación Implementado

## ✅ Cambios Realizados

### 1. Backend (API)
- **Nuevo modelo de respuesta**: `InvoiceListResponse` con metadata de paginación
  - `items`: Lista de facturas
  - `total`: Total de items en la base de datos
  - `page`: Página actual
  - `page_size`: Items por página
  - `total_pages`: Total de páginas

- **Endpoint mejorado**: `GET /api/v2/invoices/facturas`
  - Ahora devuelve metadata completa de paginación
  - Cuenta el total de items aplicando los mismos filtros
  - Calcula automáticamente el número total de páginas
  - Límite por defecto: 25 items por página

### 2. Frontend (Template)

#### Controles de Paginación
- **Botones de navegación**:
  - Primera página (<<)
  - Página anterior (<)
  - Números de página (con "..." para páginas intermedias)
  - Página siguiente (>)
  - Última página (>>)

- **Selector de items por página**: 10, 25, 50, 100

- **Información de página**: "Mostrando X a Y de Z facturas"

#### Características
- Navegación inteligente: muestra 5 páginas alrededor de la actual
- Scroll automático al inicio al cambiar de página
- Botones deshabilitados cuando no hay más páginas
- Página actual resaltada en azul
- Responsive: se adapta a móviles y tablets

### 3. JavaScript
- Variables globales para estado de paginación:
  - `currentPage`: Página actual
  - `itemsPerPage`: Items por página (default: 25)
  - `totalPages`: Total de páginas
  - `totalItems`: Total de items

- Funciones de navegación:
  - `goToPage(page)`: Ir a página específica
  - `nextPage()`: Página siguiente
  - `previousPage()`: Página anterior
  - `changeItemsPerPage()`: Cambiar items por página

## 🎯 Cómo Usar

### Para el Usuario
1. La paginación aparece automáticamente cuando hay más de 25 facturas
2. Usa los botones de navegación para moverte entre páginas
3. Cambia el selector "por página" para ver más o menos items
4. Los filtros de búsqueda se mantienen al cambiar de página

### Para el Desarrollador
```javascript
// Cambiar página
goToPage(3);

// Siguiente/Anterior
nextPage();
previousPage();

// Cambiar items por página
document.getElementById('items-per-page').value = 50;
changeItemsPerPage();
```

## 📊 Ejemplo de Respuesta API

```json
{
  "items": [
    {
      "cufe": "7569152b6d0396f9e5079cbac6bc56df...",
      "proveedor_nombre": "DISTRIBUIDORA PAPYRUS S.A.S",
      "estado": "pendiente_dian",
      ...
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 25,
  "total_pages": 6
}
```

## 🔧 Parámetros de Query

- `skip`: Número de items a saltar (default: 0)
- `limit`: Items por página (default: 25, max: 500)
- `search`: Búsqueda en proveedor, número, CUFE
- `estado`: Filtrar por estado
- `fecha_desde`: Filtrar desde fecha
- `fecha_hasta`: Filtrar hasta fecha

## ✨ Mejoras Futuras (Opcional)

1. Agregar "Ir a página" con input numérico
2. Mostrar total de páginas en el selector
3. Guardar preferencia de items por página en localStorage
4. Agregar animaciones de transición entre páginas
5. Precargar página siguiente en background
