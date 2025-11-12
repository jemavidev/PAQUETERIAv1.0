/**
 * PAQUETES EL CLUB v4.0 - JavaScript Principal
 * Versión: 1.0.0
 * Fecha: 2025-01-24
 * Autor: Equipo de Desarrollo
 */

// Configuración global
const CONFIG = {
    API_BASE: window.location.origin,
    CSRF_TOKEN: null,
    USER_AUTH: false
};

// Utilidades generales
const Utils = {
    /**
     * Mostrar mensaje de éxito
     */
    showSuccess: function(message, duration = 5000) {
        this.showToast(message, 'success', duration);
    },

    /**
     * Mostrar mensaje de error
     */
    showError: function(message, duration = 7000) {
        this.showToast(message, 'error', duration);
    },

    /**
     * Mostrar mensaje de información
     */
    showInfo: function(message, duration = 5000) {
        this.showToast(message, 'info', duration);
    },

    /**
     * Mostrar toast notification
     */
    showToast: function(message, type = 'info', duration = 5000) {
        // Crear elemento toast
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        // Agregar al contenedor de toasts
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        container.appendChild(toast);

        // Auto-remover después de la duración
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, duration);
    },

    /**
     * Validar formato de teléfono colombiano
     */
    validatePhone: function(phone) {
        const phoneRegex = /^\+57\s?\d{3}\s?\d{3}\s?\d{4}$/;
        return phoneRegex.test(phone);
    },

    /**
     * Formatear teléfono colombiano
     */
    formatPhone: function(phone) {
        // Remover todos los caracteres no numéricos excepto +
        const cleaned = phone.replace(/[^\d+]/g, '');

        // Si ya tiene formato correcto, devolver como está
        if (this.validatePhone(cleaned)) {
            return cleaned;
        }

        // Formatear número colombiano
        if (cleaned.startsWith('+57')) {
            const number = cleaned.substring(3);
            if (number.length === 10) {
                return `+57 ${number.substring(0, 3)} ${number.substring(3, 6)} ${number.substring(6)}`;
            }
        } else if (cleaned.startsWith('57')) {
            const number = cleaned.substring(2);
            if (number.length === 10) {
                return `+57 ${number.substring(0, 3)} ${number.substring(3, 6)} ${number.substring(6)}`;
            }
        } else if (cleaned.length === 10) {
            return `+57 ${cleaned.substring(0, 3)} ${cleaned.substring(3, 6)} ${cleaned.substring(6)}`;
        }

        return cleaned;
    },

    /**
     * Copiar texto al portapapeles
     */
    copyToClipboard: function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(() => {
                this.showSuccess('Copiado al portapapeles');
            });
        } else {
            // Fallback para navegadores antiguos
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showSuccess('Copiado al portapapeles');
        }
    },

    /**
     * Formatear fecha para display
     */
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-CO', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    /**
     * Obtener parámetros de URL
     */
    getUrlParams: function() {
        const params = {};
        const queryString = window.location.search.substring(1);
        const pairs = queryString.split('&');

        for (let i = 0; i < pairs.length; i++) {
            const pair = pairs[i].split('=');
            if (pair[0]) {
                params[decodeURIComponent(pair[0])] = decodeURIComponent(pair[1] || '');
            }
        }

        return params;
    }
};

// API Client
const API = {
    /**
     * Realizar petición GET
     */
    get: async function(endpoint, params = {}) {
        const url = new URL(endpoint, CONFIG.API_BASE);
        Object.keys(params).forEach(key => {
            if (params[key] !== null && params[key] !== undefined) {
                url.searchParams.append(key, params[key]);
            }
        });

        const response = await fetch(url, {
            method: 'GET',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    },

    /**
     * Realizar petición POST
     */
    post: async function(endpoint, data = {}) {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    },

    /**
     * Realizar petición PUT
     */
    put: async function(endpoint, data = {}) {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });

        return this.handleResponse(response);
    },

    /**
     * Realizar petición DELETE
     */
    delete: async function(endpoint) {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });

        return this.handleResponse(response);
    },

    /**
     * Obtener headers para las peticiones
     */
    getHeaders: function() {
        const headers = {
            'Content-Type': 'application/json'
        };

        // Agregar token de autenticación si existe
        const token = this.getAuthToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    },

    /**
     * Obtener token de autenticación
     */
    getAuthToken: function() {
        // Intentar obtener de localStorage primero
        let token = localStorage.getItem('access_token');

        // Si no está en localStorage, intentar de cookies
        if (!token) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'access_token') {
                    token = value;
                    break;
                }
            }
        }

        return token;
    },

    /**
     * Manejar respuesta de la API
     */
    handleResponse: async function(response) {
        const data = await response.json();

        if (!response.ok) {
            // Manejar errores específicos
            if (response.status === 401) {
                // Token expirado o inválido
                this.handleAuthError();
            } else if (response.status === 429) {
                // Rate limiting
                Utils.showError('Demasiadas solicitudes. Intente nuevamente en unos momentos.');
            } else {
                // Otros errores
                const errorMessage = data.detail || data.message || 'Error en la solicitud';
                Utils.showError(errorMessage);
            }
            throw new Error(data.detail || data.message || 'Error en la solicitud');
        }

        return data;
    },

    /**
     * Manejar error de autenticación
     */
    handleAuthError: function() {
        // Limpiar tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');

        // Redireccionar a login si no estamos en página pública
        if (!window.location.pathname.includes('/announce') &&
            !window.location.pathname.includes('/consult')) {
            window.location.href = '/announce';
        }

        Utils.showError('Sesión expirada. Por favor, inicie sesión nuevamente.');
    }
};

// Funcionalidades específicas de la aplicación
const PackageApp = {
        /**
         * Inicializar la aplicación
         */
        init: function() {
            this.bindEvents();
            this.checkAuthStatus();
            this.loadPageData();
        },

        /**
         * Vincular eventos
         */
        bindEvents: function() {
            // Formulario de anuncio de paquete
            const announceForm = document.getElementById('announce-form');
            if (announceForm) {
                announceForm.addEventListener('submit', this.handleAnnounceSubmit.bind(this));
            }

            // Formulario de consulta de paquete
            const consultForm = document.getElementById('consult-form');
            if (consultForm) {
                consultForm.addEventListener('submit', this.handleConsultSubmit.bind(this));
            }

            // Formulario de login
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.addEventListener('submit', this.handleLoginSubmit.bind(this));
            }

            // Auto-formateo de teléfono
            const phoneInputs = document.querySelectorAll('input[type="tel"]');
            phoneInputs.forEach(input => {
                input.addEventListener('input', this.handlePhoneInput.bind(this));
            });
        },

        /**
         * Verificar estado de autenticación
         */
        checkAuthStatus: function() {
            const token = API.getAuthToken();
            CONFIG.USUARIO_AUTH = !!token;

            // Actualizar UI según estado de autenticación
            this.updateAuthUI();
        },

        /**
         * Actualizar UI según autenticación
         */
        updateAuthUI: function() {
            const authElements = document.querySelectorAll('.auth-required');
            const publicElements = document.querySelectorAll('.public-only');

            if (CONFIG.USUARIO_AUTH) {
                authElements.forEach(el => el.style.display = 'block');
                publicElements.forEach(el => el.style.display = 'none');
            } else {
                authElements.forEach(el => el.style.display = 'none');
                publicElements.forEach(el => el.style.display = 'block');
            }
        },

        /**
         * Cargar datos específicos de la página
         */
        loadPageData: function() {
            const path = window.location.pathname;

            if (path.includes('/dashboard')) {
                this.loadDashboardData();
            } else if (path.includes('/packages')) {
                this.loadPackagesData();
            }
        },

        /**
         * Manejar envío del formulario de anuncio
         */
        handleAnnounceSubmit: async function(event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            const data = {
                customer_name: formData.get('name'),
                customer_phone: formData.get('phone'),
                guide_number: formData.get('tracking_number')
            };

            try {
                const result = await API.post('/api/packages/announce', data);

                Utils.showSuccess('Paquete anunciado exitosamente');

                // Mostrar información del paquete
                this.showPackageInfo(result);

            } catch (error) {
                console.error('Error al anunciar paquete:', error);
            }
        },

        /**
         * Manejar envío del formulario de consulta
         */
        handleConsultSubmit: async function(event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            const trackingNumber = formData.get('tracking_number');

            try {
                const result = await API.get(`/tracking/${trackingNumber}`);

                this.showPackageStatus(result);

            } catch (error) {
                console.error('Error al consultar paquete:', error);
                Utils.showError('Paquete no encontrado');
            }
        },

        /**
         * Manejar envío del formulario de login
         */
        handleLoginSubmit: async function(event) {
            event.preventDefault();

            const formData = new FormData(event.target);
            const data = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            try {
                const result = await API.post('/api/auth/login', data);

                // Guardar tokens
                localStorage.setItem('access_token', result.access_token);
                localStorage.setItem('refresh_token', result.refresh_token);

                CONFIG.USUARIO_AUTH = true;
                this.updateAuthUI();

                Utils.showSuccess('Inicio de sesión exitoso');

                // Redireccionar al dashboard
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);

            } catch (error) {
                console.error('Error en login:', error);
            }
        },

        /**
         * Manejar input de teléfono
         */
        handlePhoneInput: function(event) {
            const input = event.target;
            const formatted = Utils.formatPhone(input.value);
            if (formatted !== input.value) {
                input.value = formatted;
            }
        },

        /**
         * Mostrar información del paquete anunciado
         */
        showPackageInfo: function(data) {
            const infoDiv = document.getElementById('package-info');
            if (infoDiv) {
                infoDiv.innerHTML = `
                <div class="package-info-card">
                    <h3>Paquete Anunciado Exitosamente</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <label>Número de Tracking:</label>
                            <span class="tracking-number">${data.tracking_number}</span>
                            <button onclick="Utils.copyToClipboard('${data.tracking_number}')">Copiar</button>
                        </div>
                        <div class="info-item">
                            <label>Código de Acceso:</label>
                            <span class="access-code">${data.access_code}</span>
                            <button onclick="Utils.copyToClipboard('${data.access_code}')">Copiar</button>
                        </div>
                        <div class="info-item">
                            <label>Estado:</label>
                            <span class="status">${data.package.status}</span>
                        </div>
                    </div>
                </div>
            `;
                infoDiv.style.display = 'block';
            }
        },

        /**
         * Mostrar estado del paquete consultado
         */
        showPackageStatus: function(data) {
                const statusDiv = document.getElementById('package-status');
                if (statusDiv) {
                    statusDiv.innerHTML = `
                <div class="package-status-card">
                    <h3>Estado del Paquete</h3>
                    <div class="status-info">
                        <div class="status-item">
                            <label>Número de Tracking:</label>
                            <span>${data.tracking_number}</span>
                        </div>
                        <div class="status-item">
                            <label>Estado:</label>
                            <span class="status-${data.status}">${data.status}</span>
                        </div>
                        <div class="status-item">
                            <label>Cliente:</label>
                            <span>${data.customer_name || 'No disponible'}</span>
                        </div>
                        ${data.announced_at ? `
                        <div class="status-item">
                            <label>Anunciado:</label>
                            <span>${Utils.formatDate(data.announced_at)}</span>
                        </div>
                        ` : ''}
                        ${data.received_at ? `
                        <div class="status-item">
                            <label>Recibido:</label>
                            <span>${Utils.formatDate(data.received_at)}</span>
                        </div>
                        ` : ''}
                        ${data.delivered_at ? `
                        <div class="status-item">
                            <label>Entregado:</label>
                            <span>${Utils.formatDate(data.delivered_at)}</span>
                        </div>
                        ` : ''}
                        ${data.observations ? `
                        <div class="status-item">
                            <label>Observaciones:</label>
                            <span>${data.observations}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
            statusDiv.style.display = 'block';
        }
    },

    /**
     * Cargar datos del dashboard
     */
    loadDashboardData: async function() {
        try {
            const stats = await API.get('/api/packages/stats/summary');
            this.updateDashboardStats(stats);
        } catch (error) {
            console.error('Error cargando datos del dashboard:', error);
        }
    },

    /**
     * Actualizar estadísticas del dashboard
     */
    updateDashboardStats: function(stats) {
        // Actualizar contadores
        const totalPackagesEl = document.getElementById('total-packages');
        if (totalPackagesEl) {
            totalPackagesEl.textContent = stats.total_packages || 0;
        }

        // Actualizar gráficos y otras métricas según sea necesario
    },

    /**
     * Cargar datos de paquetes
     */
    loadPackagesData: async function() {
        try {
            const packages = await API.get('/api/packages/');
            this.updatePackagesList(packages);
        } catch (error) {
            console.error('Error cargando paquetes:', error);
        }
    },

    /**
     * Actualizar lista de paquetes
     */
    updatePackagesList: function(packages) {
        const container = document.getElementById('packages-list');
        if (container && packages) {
            container.innerHTML = packages.map(pkg => `
                <div class="package-card">
                    <div class="package-header">
                        <span class="tracking-number">${pkg.tracking_number}</span>
                        <span class="status status-${pkg.status}">${pkg.status}</span>
                    </div>
                    <div class="package-info">
                        <p><strong>Cliente:</strong> ${pkg.customer_name}</p>
                        <p><strong>Teléfono:</strong> ${pkg.customer_phone}</p>
                        <p><strong>Anunciado:</strong> ${Utils.formatDate(pkg.announced_at)}</p>
                    </div>
                </div>
            `).join('');
        }
    }
};

// Global fetch interceptor for authentication errors
const originalFetch = window.fetch;
window.fetch = async function(...args) {
    try {
        const response = await originalFetch(...args);
        if (!response.ok && response.status === 401) {
            // Clone to read body without consuming
            const clonedResponse = response.clone();
            try {
                const data = await clonedResponse.json();
                console.log('Fetch interceptor: 401 error with data:', data);
                if (data.detail === "No autenticado") {
                    console.log('Fetch interceptor: Redirecting to login due to "No autenticado"');
                    window.location.href = '/auth/login';
                    // Return a pending promise to prevent further processing
                    return new Promise(() => {});
                }
            } catch (e) {
                console.log('Fetch interceptor: Could not parse response as JSON');
                // Not json, ignore
            }
        }
        return response;
    } catch (error) {
        console.log('Fetch interceptor: Network error:', error);
        throw error;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    PackageApp.init();
});

// Exportar para uso global
window.PackageApp = PackageApp;
window.Utils = Utils;
window.API = API;