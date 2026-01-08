/**
 * ════════════════════════════════════════════════════════════════════════════
 * SCRIPT DE PRUEBAS PARA CONSOLA DEL NAVEGADOR
 * ════════════════════════════════════════════════════════════════════════════
 * 
 * INSTRUCCIONES:
 * 1. Ir a https://staging.jemavi.co/admin
 * 2. Hacer login
 * 3. Abrir la consola del navegador (F12)
 * 4. Copiar y pegar todo este código
 * 5. Presionar Enter
 * 
 * El script ejecutará pruebas automáticas y mostrará los resultados
 * ════════════════════════════════════════════════════════════════════════════
 */

(function() {
    'use strict';
    
    console.clear();
    console.log('%c════════════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold');
    console.log('%cPRUEBAS DEL DASHBOARD UNIFICADO', 'color: cyan; font-weight: bold; font-size: 16px');
    console.log('%c════════════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold');
    console.log('');
    
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    
    // Funciones auxiliares
    function testPass(message) {
        console.log('%c✓ PASS:', 'color: green; font-weight: bold', message);
        passedTests++;
    }
    
    function testFail(message) {
        console.log('%c✗ FAIL:', 'color: red; font-weight: bold', message);
        failedTests++;
    }
    
    function testInfo(message) {
        console.log('%cℹ INFO:', 'color: blue; font-weight: bold', message);
    }
    
    function testHeader(message) {
        console.log('');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: yellow');
        console.log('%c' + message, 'color: yellow; font-weight: bold');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: yellow');
        console.log('');
    }
    
    function runTest(description, testFn) {
        totalTests++;
        console.log(`%c[TEST ${totalTests}]`, 'color: blue; font-weight: bold', description);
        try {
            const result = testFn();
            if (result) {
                testPass(description);
            } else {
                testFail(description);
            }
        } catch (error) {
            testFail(description + ' - Error: ' + error.message);
        }
    }
    
    // ════════════════════════════════════════════════════════════════════════
    // 1. PRUEBAS DE ELEMENTOS DEL DOM
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('1. PRUEBAS DE ELEMENTOS DEL DOM');
    
    runTest('Verificar que existen los 6 tabs', () => {
        const tabs = [
            'tab-dashboard',
            'tab-users',
            'tab-packages',
            'tab-customers',
            'tab-messages',
            'tab-settings'
        ];
        return tabs.every(id => document.getElementById(id) !== null);
    });
    
    runTest('Verificar que existen los 6 contenidos de tabs', () => {
        const contents = [
            'dashboard-content',
            'users-content',
            'packages-content',
            'customers-content',
            'messages-content',
            'settings-content'
        ];
        return contents.every(id => document.getElementById(id) !== null);
    });
    
    runTest('Verificar que el tab Dashboard está activo por defecto', () => {
        const dashboardTab = document.getElementById('tab-dashboard');
        return dashboardTab && dashboardTab.classList.contains('border-papyrus-blue');
    });
    
    runTest('Verificar que el contenido Dashboard está visible por defecto', () => {
        const dashboardContent = document.getElementById('dashboard-content');
        return dashboardContent && !dashboardContent.classList.contains('hidden');
    });
    
    runTest('Verificar que otros contenidos están ocultos', () => {
        const contents = [
            'users-content',
            'packages-content',
            'customers-content',
            'messages-content',
            'settings-content'
        ];
        return contents.every(id => {
            const el = document.getElementById(id);
            return el && el.classList.contains('hidden');
        });
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 2. PRUEBAS DE FUNCIONES JAVASCRIPT
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('2. PRUEBAS DE FUNCIONES JAVASCRIPT');
    
    runTest('Verificar que existe la función switchTab()', () => {
        return typeof switchTab === 'function';
    });
    
    runTest('Verificar que existe la función loadDashboardStats()', () => {
        return typeof loadDashboardStats === 'function';
    });
    
    runTest('Verificar que existe la función loadUsersTab()', () => {
        return typeof loadUsersTab === 'function';
    });
    
    runTest('Verificar que existe la función loadPackagesTab()', () => {
        return typeof loadPackagesTab === 'function';
    });
    
    runTest('Verificar que existe la función loadCustomersTab()', () => {
        return typeof loadCustomersTab === 'function';
    });
    
    runTest('Verificar que existe la función loadMessagesTab()', () => {
        return typeof loadMessagesTab === 'function';
    });
    
    runTest('Verificar que existe la función formatCurrency()', () => {
        return typeof formatCurrency === 'function';
    });
    
    runTest('Verificar que existe la función formatNumber()', () => {
        return typeof formatNumber === 'function';
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 3. PRUEBAS DE SECCIONES DEL TAB DASHBOARD
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('3. PRUEBAS DE SECCIONES DEL TAB DASHBOARD');
    
    runTest('Verificar sección Financiero', () => {
        return document.body.innerHTML.includes('💰 Financiero') || 
               document.body.innerHTML.includes('Financiero');
    });
    
    runTest('Verificar sección Paquetes', () => {
        return document.body.innerHTML.includes('📦 Paquetes') || 
               document.body.innerHTML.includes('Paquetes');
    });
    
    runTest('Verificar sección Clientes', () => {
        return document.body.innerHTML.includes('👥 Clientes') || 
               document.body.innerHTML.includes('Clientes');
    });
    
    runTest('Verificar sección SMS', () => {
        return document.body.innerHTML.includes('📱 SMS') || 
               document.body.innerHTML.includes('SMS y Notificaciones');
    });
    
    runTest('Verificar sección Performance', () => {
        return document.body.innerHTML.includes('⚡ Performance') || 
               document.body.innerHTML.includes('Performance');
    });
    
    runTest('Verificar sección Salud del Sistema', () => {
        return document.body.innerHTML.includes('🏥 Salud') || 
               document.body.innerHTML.includes('Salud del Sistema');
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 4. PRUEBAS DE NAVEGACIÓN ENTRE TABS
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('4. PRUEBAS DE NAVEGACIÓN ENTRE TABS');
    
    runTest('Cambiar al tab Usuarios', () => {
        if (typeof switchTab === 'function') {
            switchTab('users');
            const usersContent = document.getElementById('users-content');
            const dashboardContent = document.getElementById('dashboard-content');
            return usersContent && !usersContent.classList.contains('hidden') &&
                   dashboardContent && dashboardContent.classList.contains('hidden');
        }
        return false;
    });
    
    runTest('Cambiar al tab Paquetes', () => {
        if (typeof switchTab === 'function') {
            switchTab('packages');
            const packagesContent = document.getElementById('packages-content');
            const usersContent = document.getElementById('users-content');
            return packagesContent && !packagesContent.classList.contains('hidden') &&
                   usersContent && usersContent.classList.contains('hidden');
        }
        return false;
    });
    
    runTest('Cambiar al tab Clientes', () => {
        if (typeof switchTab === 'function') {
            switchTab('customers');
            const customersContent = document.getElementById('customers-content');
            const packagesContent = document.getElementById('packages-content');
            return customersContent && !customersContent.classList.contains('hidden') &&
                   packagesContent && packagesContent.classList.contains('hidden');
        }
        return false;
    });
    
    runTest('Cambiar al tab Mensajes', () => {
        if (typeof switchTab === 'function') {
            switchTab('messages');
            const messagesContent = document.getElementById('messages-content');
            const customersContent = document.getElementById('customers-content');
            return messagesContent && !messagesContent.classList.contains('hidden') &&
                   customersContent && customersContent.classList.contains('hidden');
        }
        return false;
    });
    
    runTest('Cambiar al tab Settings', () => {
        if (typeof switchTab === 'function') {
            switchTab('settings');
            const settingsContent = document.getElementById('settings-content');
            const messagesContent = document.getElementById('messages-content');
            return settingsContent && !settingsContent.classList.contains('hidden') &&
                   messagesContent && messagesContent.classList.contains('hidden');
        }
        return false;
    });
    
    runTest('Volver al tab Dashboard', () => {
        if (typeof switchTab === 'function') {
            switchTab('dashboard');
            const dashboardContent = document.getElementById('dashboard-content');
            const settingsContent = document.getElementById('settings-content');
            return dashboardContent && !dashboardContent.classList.contains('hidden') &&
                   settingsContent && settingsContent.classList.contains('hidden');
        }
        return false;
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 5. PRUEBAS DE BOTONES
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('5. PRUEBAS DE BOTONES');
    
    runTest('Verificar botón Actualizar en header', () => {
        const buttons = document.querySelectorAll('button');
        return Array.from(buttons).some(btn => 
            btn.textContent.includes('Actualizar') || 
            btn.onclick && btn.onclick.toString().includes('reload')
        );
    });
    
    runTest('Verificar botones de navegación en tabs', () => {
        const links = document.querySelectorAll('button, a');
        const navigationButtons = [
            'Ir a Gestión',
            'Ver Todos los Paquetes',
            'Ver Todos los Clientes',
            'Ver Todos los Mensajes'
        ];
        return navigationButtons.some(text => 
            Array.from(links).some(link => link.textContent.includes(text))
        );
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 6. PRUEBAS DE RESPONSIVE
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('6. PRUEBAS DE RESPONSIVE');
    
    runTest('Verificar clases responsive Tailwind', () => {
        const html = document.body.innerHTML;
        return html.includes('sm:') && html.includes('md:') && html.includes('lg:');
    });
    
    runTest('Verificar que los tabs tienen overflow-x-auto', () => {
        const nav = document.querySelector('nav[aria-label="Tabs"]');
        return nav && (nav.classList.contains('overflow-x-auto') || 
                      getComputedStyle(nav).overflowX === 'auto');
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // 7. PRUEBAS DE ICONOS SVG
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('7. PRUEBAS DE ICONOS SVG');
    
    runTest('Verificar que hay iconos SVG en los tabs', () => {
        const svgs = document.querySelectorAll('button svg, a svg');
        return svgs.length >= 6; // Al menos 6 iconos (uno por tab)
    });
    
    runTest('Verificar que hay iconos SVG en las secciones', () => {
        const svgs = document.querySelectorAll('svg');
        return svgs.length >= 20; // Muchos iconos en todo el dashboard
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // RESUMEN DE RESULTADOS
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('RESUMEN DE RESULTADOS');
    
    console.log('');
    console.log('%cTotal de pruebas:', 'font-weight: bold', totalTests);
    console.log('%c✓ Pruebas exitosas:', 'color: green; font-weight: bold', passedTests);
    console.log('%c✗ Pruebas fallidas:', 'color: red; font-weight: bold', failedTests);
    console.log('');
    
    const percentage = ((passedTests / totalTests) * 100).toFixed(1);
    console.log('%cPorcentaje de éxito:', 'font-weight: bold', percentage + '%');
    console.log('');
    
    if (failedTests === 0) {
        console.log('%c════════════════════════════════════════════════════════════════', 'color: green; font-weight: bold');
        console.log('%c✓ TODAS LAS PRUEBAS PASARON EXITOSAMENTE', 'color: green; font-weight: bold; font-size: 16px');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: green; font-weight: bold');
    } else {
        console.log('%c════════════════════════════════════════════════════════════════', 'color: orange; font-weight: bold');
        console.log('%c⚠ ALGUNAS PRUEBAS FALLARON', 'color: orange; font-weight: bold; font-size: 16px');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: orange; font-weight: bold');
    }
    
    console.log('');
    console.log('%cPRUEBAS ADICIONALES RECOMENDADAS:', 'color: cyan; font-weight: bold');
    console.log('1. Verificar que los datos se cargan correctamente en cada tab');
    console.log('2. Probar en diferentes tamaños de pantalla (responsive)');
    console.log('3. Verificar que no hay errores en la consola');
    console.log('4. Probar la navegación entre tabs múltiples veces');
    console.log('5. Verificar que los botones de navegación funcionan');
    console.log('');
    
    // Retornar objeto con resultados
    return {
        total: totalTests,
        passed: passedTests,
        failed: failedTests,
        percentage: percentage,
        success: failedTests === 0
    };
})();
