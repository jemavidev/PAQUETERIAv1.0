/**
 * Cargador de productos para el TAB PRODUCTOS
 * Versión standalone para evitar conflictos
 */

let currentPage = 1;
let itemsPerPage = 50;
let currentProducts = [];
let totalItems = 0;

// Función principal para cargar productos
async function loadProducts() {
    console.log('🔄 Cargando productos...');
    
    const loading = document.getElementById('loading');
    const tbody = document.getElementById('products-tbody');
    const emptyState = document.getElementById('products-empty');
    const totalCount = document.getElementById('totalProductsCount');
    const paginationContainer = document.getElementById('pagination-container');
    
    if (!tbody) {
        console.error('❌ No se encontró el elemento products-tbody');
        return;
    }
    
    loading?.classList.remove('hidden');
    tbody.innerHTML = '';
    emptyState?.classList.add('hidden');
    paginationContainer?.classList.add('hidden');
    
    const skip = (currentPage - 1) * itemsPerPage;
    const searchValue = document.getElementById('search')?.value || '';
    
    const params = new URLSearchParams({
        skip: skip,
        limit: itemsPerPage,
        search: searchValue
    });
    
    try {
        const response = await fetch(`/api/v2/invoices/productos?${params}`, {
            credentials: 'same-origin'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            
            if (response.status === 401 || response.status === 403) {
                console.error('❌ No autenticado - redirigiendo al login');
                window.location.href = errorData.redirect_url || '/auth/login';
                return;
            }
            
            throw new Error(errorData.detail || 'Error cargando productos');
        }
        
        const products = await response.json();
        console.log(`✅ ${products.length} productos cargados`);
        
        currentProducts = products;
        totalItems = products.length;
        
        if (products.length === 0 && currentPage === 1) {
            emptyState?.classList.remove('hidden');
            if (totalCount) totalCount.textContent = '';
        } else {
            const htmlContent = products.map(product => renderProductRow(product)).join('');
            tbody.innerHTML = htmlContent;
            
            const pageStart = skip + 1;
            const pageEnd = skip + products.length;
            if (totalCount) {
                totalCount.textContent = `${products.length} productos`;
            }
            
            if (products.length > 0 && paginationContainer) {
                updatePaginationControls(pageStart, pageEnd, products.length);
                paginationContainer.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('❌ Error cargando productos:', error);
        emptyState?.classList.remove('hidden');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="11" class="px-6 py-12 text-center">
                        <div class="text-red-600 font-medium">Error cargando productos</div>
                        <div class="text-sm text-gray-500 mt-2">${error.message}</div>
                    </td>
                </tr>
            `;
        }
    } finally {
        loading?.classList.add('hidden');
    }
}

function renderProductRow(product) {
    const formatCurrency = (value) => {
        if (!value) return '$0';
        return `$${parseFloat(value).toLocaleString('es-CO', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`;
    };
    
    const formatDate = (date) => {
        if (!date) return '-';
        try {
            return new Date(date).toLocaleDateString('es-CO');
        } catch {
            return '-';
        }
    };
    
    const proveedor = product.proveedor_nombre || '-';
    const numeroFactura = product.numero_factura || '-';
    
    return `
        <tr class="hover:bg-gray-50 transition-colors">
            <td class="px-6 py-4 text-sm font-mono text-gray-900">
                <span class="whitespace-nowrap">${product.codigo_producto || '-'}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                <div class="max-w-xs overflow-hidden text-ellipsis" title="${product.descripcion || '-'}">
                    ${product.descripcion || '-'}
                </div>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900">
                <span class="uppercase whitespace-nowrap overflow-hidden text-ellipsis block max-w-xs" title="${proveedor}">
                    ${proveedor}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900 hidden md:table-cell">
                <span class="whitespace-nowrap">${numeroFactura}</span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-900 hidden lg:table-cell">${formatDate(product.fecha_compra)}</td>
            <td class="px-6 py-4 text-sm text-right text-gray-900 hidden md:table-cell">${product.cantidad || '-'}</td>
            <td class="px-6 py-4 text-sm text-right text-gray-900">
                <div class="font-medium">${formatCurrency(product.precio_unitario)}</div>
            </td>
            <td class="px-6 py-4 text-sm text-right hidden lg:table-cell">-</td>
            <td class="px-6 py-4 text-sm text-right hidden xl:table-cell">-</td>
            <td class="px-6 py-4 text-sm text-right font-medium text-gray-900">${formatCurrency(product.total_item)}</td>
            <td class="px-6 py-4 text-sm text-center">
                <button class="text-papyrus-blue hover:text-papyrus-blue-dark" title="Ver detalles">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                </button>
            </td>
        </tr>
    `;
}

function updatePaginationControls(pageStart, pageEnd, total) {
    const pageStartEl = document.getElementById('page-start');
    const pageEndEl = document.getElementById('page-end');
    const totalItemsEl = document.getElementById('total-items');
    
    if (pageStartEl) pageStartEl.textContent = pageStart;
    if (pageEndEl) pageEndEl.textContent = pageEnd;
    if (totalItemsEl) totalItemsEl.textContent = total;
}

function clearSearch() {
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.value = '';
        currentPage = 1;
        loadProducts();
    }
}

function goToPage(page) {
    if (page < 1) return;
    currentPage = page;
    loadProducts();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('✅ DOM cargado - inicializando productos');
        loadProducts();
        
        // Búsqueda automática
        const searchInput = document.getElementById('search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    currentPage = 1;
                    loadProducts();
                }, 500);
            });
        }
    });
} else {
    console.log('✅ DOM ya cargado - inicializando productos inmediatamente');
    loadProducts();
}

console.log('✅ productos-loader.js cargado correctamente');
