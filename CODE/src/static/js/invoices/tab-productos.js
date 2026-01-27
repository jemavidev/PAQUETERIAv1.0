// ========================================
// PAQUETES EL CLUB - Tab Productos
// ========================================

/**
 * Lógica para el tab de productos y matching
 */
const TabProductos = {
    /**
     * Estado del tab
     */
    state: {
        products: [],
        loading: false,
        page: 1,
        perPage: 50,
        total: 0,
        filters: {
            matched_only: false,
            unmatched_only: false,
            invoice_id: null
        },
        stats: null
    },
    
    /**
     * Inicializa el tab
     */
    async init() {
        await this.loadStats();
        await this.loadProducts();
        this.setupEventListeners();
    },
    
    /**
     * Carga estadísticas
     */
    async loadStats() {
        try {
            const response = await fetch('/api/products/stats', {
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            const data = await response.json();
            
            if (data.success) {
                this.state.stats = data.data;
                this.renderStats();
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    },
    
    /**
     * Carga productos
     */
    async loadProducts() {
        this.state.loading = true;
        
        try {
            const params = new URLSearchParams({
                page: this.state.page,
                per_page: this.state.perPage
            });
            
            if (this.state.filters.matched_only) {
                params.append('matched_only', 'true');
            }
            
            if (this.state.filters.unmatched_only) {
                params.append('unmatched_only', 'true');
            }
            
            if (this.state.filters.invoice_id) {
                params.append('invoice_id', this.state.filters.invoice_id);
            }
            
            const response = await fetch(`/api/products?${params}`, {
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            const data = await response.json();
            
            if (data.success) {
                this.state.products = data.data;
                this.state.total = data.pagination.total;
                this.renderProducts();
                this.renderPagination(data.pagination);
            }
        } catch (error) {
            console.error('Error cargando productos:', error);
            this.showError('Error cargando productos');
        } finally {
            this.state.loading = false;
        }
    },
    
    /**
     * Ejecuta auto-matching
     */
    async autoMatch(invoiceId = null, threshold = 0.85) {
        if (!confirm(`¿Ejecutar auto-matching con umbral de ${(threshold * 100).toFixed(0)}%?`)) {
            return;
        }
        
        this.showLoading('Ejecutando auto-matching...');
        
        try {
            const formData = new FormData();
            if (invoiceId) {
                formData.append('invoice_id', invoiceId);
            }
            formData.append('confidence_threshold', threshold);
            
            const response = await fetch('/api/products/auto-match', {
                method: 'POST',
                body: formData,
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess(`Matched: ${data.matched}/${data.total} productos`);
                await this.loadStats();
                await this.loadProducts();
                this.showMatchResults(data.results);
            } else {
                this.showError('Error en auto-matching');
            }
        } catch (error) {
            console.error('Error en auto-matching:', error);
            this.showError('Error en auto-matching');
        }
    },
    
    /**
     * Match manual de un producto
     */
    async manualMatch(productId, catalogProductId) {
        try {
            const formData = new FormData();
            formData.append('catalog_product_id', catalogProductId);
            
            const response = await fetch(`/api/products/${productId}/match`, {
                method: 'POST',
                body: formData,
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Match realizado correctamente');
                await this.loadStats();
                await this.loadProducts();
            } else {
                this.showError(data.detail || 'Error en match');
            }
        } catch (error) {
            console.error('Error en match manual:', error);
            this.showError('Error en match manual');
        }
    },
    
    /**
     * Exporta productos
     */
    async exportProducts(format = 'csv') {
        try {
            const formData = new FormData();
            formData.append('format', format);
            
            if (this.state.filters.invoice_id) {
                formData.append('invoice_id', this.state.filters.invoice_id);
            }
            
            const response = await fetch('/api/products/export', {
                method: 'POST',
                body: formData,
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            
            if (format === 'csv') {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'productos_facturas.csv';
                a.click();
                window.URL.revokeObjectURL(url);
                this.showSuccess('Archivo descargado');
            } else {
                const data = await response.json();
                console.log('Datos exportados:', data);
            }
        } catch (error) {
            console.error('Error exportando:', error);
            this.showError('Error exportando productos');
        }
    },
    
    /**
     * Renderiza estadísticas
     */
    renderStats() {
        const container = document.getElementById('products-stats');
        if (!container || !this.state.stats) return;
        
        const html = `
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Total Items</div>
                    <div class="text-2xl font-bold">${this.state.stats.total_items}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Con Match</div>
                    <div class="text-2xl font-bold text-green-600">${this.state.stats.matched}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Sin Match</div>
                    <div class="text-2xl font-bold text-yellow-600">${this.state.stats.unmatched}</div>
                </div>
                <div class="bg-white rounded-lg shadow p-4">
                    <div class="text-sm text-gray-500">Tasa de Match</div>
                    <div class="text-2xl font-bold text-blue-600">${this.state.stats.match_rate}%</div>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    },
    
    /**
     * Renderiza productos
     */
    renderProducts() {
        const container = document.getElementById('products-list');
        if (!container) return;
        
        if (this.state.products.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 text-gray-500">
                    <p>No hay productos para mostrar</p>
                </div>
            `;
            return;
        }
        
        const html = `
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Código</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descripción</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cantidad</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Precio</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Match</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Margen</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Acciones</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                        ${this.state.products.map(p => this.renderProductRow(p)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = html;
    },
    
    /**
     * Renderiza fila de producto
     */
    renderProductRow(product) {
        const matchBadge = this.getMatchBadge(product);
        const marginBadge = product.margin ? this.getMarginBadge(product.margin) : '-';
        
        return `
            <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                    <code class="text-xs bg-gray-100 px-2 py-1 rounded">${product.codigo || '-'}</code>
                </td>
                <td class="px-6 py-4">
                    <div class="text-sm text-gray-900 max-w-xs truncate">${product.descripcion}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${product.cantidad}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${Formatters.currency(product.precio_unitario)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    ${Formatters.currency(product.valor_total)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${matchBadge}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    ${marginBadge}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    ${this.renderProductActions(product)}
                </td>
            </tr>
        `;
    },
    
    /**
     * Obtiene badge de match
     */
    getMatchBadge(product) {
        if (!product.matched) {
            return '<span class="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-800">Sin match</span>';
        }
        
        const confidence = product.match_confidence * 100;
        let color = 'green';
        if (confidence < 85) color = 'yellow';
        if (confidence < 70) color = 'red';
        
        return `<span class="px-2 py-1 text-xs rounded-full bg-${color}-100 text-${color}-800">${confidence.toFixed(0)}%</span>`;
    },
    
    /**
     * Obtiene badge de margen
     */
    getMarginBadge(margin) {
        const value = margin.margin_percentage;
        let color = 'green';
        if (value < 0) color = 'red';
        else if (value < 20) color = 'yellow';
        
        const icon = value < 0 ? '↓' : '↑';
        
        return `<span class="px-2 py-1 text-xs rounded-full bg-${color}-100 text-${color}-800">${icon} ${value.toFixed(2)}%</span>`;
    },
    
    /**
     * Renderiza acciones de producto
     */
    renderProductActions(product) {
        const actions = [];
        
        if (!product.matched) {
            actions.push(`<button onclick="TabProductos.showMatchModal(${product.id})" class="text-green-600 hover:text-green-900 mr-2">Match</button>`);
        }
        
        actions.push(`<button onclick="TabProductos.viewProduct(${product.id})" class="text-blue-600 hover:text-blue-900">Ver</button>`);
        
        return actions.join('');
    },
    
    /**
     * Renderiza paginación
     */
    renderPagination(pagination) {
        const container = document.getElementById('products-pagination');
        if (!container) return;
        
        const html = `
            <div class="flex items-center justify-between px-4 py-3 bg-white border-t border-gray-200">
                <div class="text-sm text-gray-700">
                    Mostrando ${((pagination.page - 1) * pagination.per_page) + 1} a ${Math.min(pagination.page * pagination.per_page, pagination.total)} de ${pagination.total}
                </div>
                <div class="flex gap-2">
                    <button onclick="TabProductos.previousPage()" 
                            ${pagination.page === 1 ? 'disabled' : ''}
                            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50">
                        Anterior
                    </button>
                    <button onclick="TabProductos.nextPage()" 
                            ${pagination.page >= pagination.pages ? 'disabled' : ''}
                            class="px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-50">
                        Siguiente
                    </button>
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    },
    
    /**
     * Muestra modal de match
     */
    showMatchModal(productId) {
        const catalogProductId = prompt('Ingresa el ID del producto del catálogo:');
        if (catalogProductId) {
            this.manualMatch(productId, parseInt(catalogProductId));
        }
    },
    
    /**
     * Ver detalles de producto
     */
    async viewProduct(productId) {
        try {
            const response = await fetch(`/api/products/${productId}`, {
                credentials: 'include'  // ✨ Incluir cookies de autenticación
            });
            const data = await response.json();
            
            if (data.success) {
                console.log('Producto:', data.data);
                alert(JSON.stringify(data.data, null, 2));
            }
        } catch (error) {
            console.error('Error obteniendo producto:', error);
        }
    },
    
    /**
     * Muestra resultados de matching
     */
    showMatchResults(results) {
        console.log('Resultados de matching:', results);
        
        const matched = results.filter(r => r.matched).length;
        const failed = results.filter(r => !r.matched).length;
        
        let message = `✅ Matched: ${matched}\n`;
        if (failed > 0) {
            message += `❌ Sin match: ${failed}`;
        }
        
        alert(message);
    },
    
    /**
     * Página anterior
     */
    async previousPage() {
        if (this.state.page > 1) {
            this.state.page--;
            await this.loadProducts();
        }
    },
    
    /**
     * Página siguiente
     */
    async nextPage() {
        this.state.page++;
        await this.loadProducts();
    },
    
    /**
     * Aplica filtros
     */
    async applyFilters(filters) {
        this.state.filters = { ...this.state.filters, ...filters };
        this.state.page = 1;
        await this.loadProducts();
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Botón auto-match
        const btnAutoMatch = document.getElementById('btn-auto-match');
        if (btnAutoMatch) {
            btnAutoMatch.addEventListener('click', () => this.autoMatch());
        }
        
        // Botón exportar
        const btnExport = document.getElementById('btn-export');
        if (btnExport) {
            btnExport.addEventListener('click', () => this.exportProducts('csv'));
        }
        
        // Filtros
        const filterMatched = document.getElementById('filter-matched');
        if (filterMatched) {
            filterMatched.addEventListener('change', (e) => {
                this.applyFilters({ matched_only: e.target.checked, unmatched_only: false });
            });
        }
        
        const filterUnmatched = document.getElementById('filter-unmatched');
        if (filterUnmatched) {
            filterUnmatched.addEventListener('change', (e) => {
                this.applyFilters({ unmatched_only: e.target.checked, matched_only: false });
            });
        }
    },
    
    /**
     * Utilidades de UI
     */
    showLoading(message) {
        console.log('Loading:', message);
    },
    
    showSuccess(message) {
        alert(message);
    },
    
    showError(message) {
        alert('Error: ' + message);
    }
};

// Inicializar cuando el DOM esté listo
if (typeof window !== 'undefined') {
    window.TabProductos = TabProductos;
}
