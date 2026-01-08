/**
 * ════════════════════════════════════════════════════════════════════════════
 * SCRIPT DE PRUEBA DE BOTONES Y ENLACES
 * ════════════════════════════════════════════════════════════════════════════
 * 
 * INSTRUCCIONES:
 * 1. Ir a https://staging.jemavi.co/admin
 * 2. Hacer login
 * 3. Abrir la consola del navegador (F12)
 * 4. Copiar y pegar este código
 * 5. Presionar Enter
 * 
 * El script verificará todos los botones y enlaces del dashboard
 * ════════════════════════════════════════════════════════════════════════════
 */

(function() {
    'use strict';
    
    console.clear();
    console.log('%c════════════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold');
    console.log('%cPRUEBA DE BOTONES Y ENLACES - DASHBOARD UNIFICADO', 'color: cyan; font-weight: bold; font-size: 16px');
    console.log('%c════════════════════════════════════════════════════════════════', 'color: cyan; font-weight: bold');
    console.log('');
    
    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    
    function testPass(message) {
        console.log('%c✓ PASS:', 'color: green; font-weight: bold', message);
        passedTests++;
    }
    
    function testFail(message) {
        console.log('%c✗ FAIL:', 'color: red; font-weight: bold', message);
        failedTests++;
    }
    
    function testHeader(message) {
        console.log('');
        console.log('%c' + message, 'color: yellow; font-weight: bold');
        console.log('');
    }
    
    // ════════════════════════════════════════════════════════════════════════
    // 1. VERIFICAR BOTONES EN TABS
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('1. VERIFICANDO BOTONES EN TABS');
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar botón "Ir a Gestión de Usuarios"');
    const userButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent.includes('Ir a Gestión') || btn.onclick && btn.onclick.toString().includes('/admin/users')
    );
    if (userButtons.length > 0) {
        testPass('Botón encontrado: ' + userButtons.length + ' instancia(s)');
        console.log('   Destino:', '/admin/users');
    } else {
        testFail('Botón no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar botón "Ver Todos los Paquetes"');
    const packageButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent.includes('Ver Todos los Paquetes') || btn.onclick && btn.onclick.toString().includes('/packages')
    );
    if (packageButtons.length > 0) {
        testPass('Botón encontrado: ' + packageButtons.length + ' instancia(s)');
        console.log('   Destino:', '/packages');
    } else {
        testFail('Botón no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar botón "Ver Todos los Clientes"');
    const customerButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent.includes('Ver Todos los Clientes') || btn.onclick && btn.onclick.toString().includes('/customers')
    );
    if (customerButtons.length > 0) {
        testPass('Botón encontrado: ' + customerButtons.length + ' instancia(s)');
        console.log('   Destino:', '/customers');
    } else {
        testFail('Botón no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar botón "Ver Todos los Mensajes"');
    const messageButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
        btn.textContent.includes('Ver Todos los Mensajes') || btn.onclick && btn.onclick.toString().includes('/messages')
    );
    if (messageButtons.length > 0) {
        testPass('Botón encontrado: ' + messageButtons.length + ' instancia(s)');
        console.log('   Destino:', '/messages');
    } else {
        testFail('Botón no encontrado');
    }
    
    // ════════════════════════════════════════════════════════════════════════
    // 2. VERIFICAR ENLACES EN TAB SETTINGS
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('2. VERIFICANDO ENLACES EN TAB SETTINGS');
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar enlace a /admin/users');
    const userLinks = Array.from(document.querySelectorAll('a[href="/admin/users"]'));
    if (userLinks.length > 0) {
        testPass('Enlace encontrado: ' + userLinks.length + ' instancia(s)');
    } else {
        testFail('Enlace no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar enlace a /packages');
    const packageLinks = Array.from(document.querySelectorAll('a[href="/packages"]'));
    if (packageLinks.length > 0) {
        testPass('Enlace encontrado: ' + packageLinks.length + ' instancia(s)');
    } else {
        testFail('Enlace no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar enlace a /customers');
    const customerLinks = Array.from(document.querySelectorAll('a[href="/customers"]'));
    if (customerLinks.length > 0) {
        testPass('Enlace encontrado: ' + customerLinks.length + ' instancia(s)');
    } else {
        testFail('Enlace no encontrado');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar enlace a /messages');
    const messageLinks = Array.from(document.querySelectorAll('a[href="/messages"]'));
    if (messageLinks.length > 0) {
        testPass('Enlace encontrado: ' + messageLinks.length + ' instancia(s)');
    } else {
        testFail('Enlace no encontrado');
    }
    
    // ════════════════════════════════════════════════════════════════════════
    // 3. VERIFICAR FUNCIONALIDAD DE BOTONES
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('3. VERIFICANDO FUNCIONALIDAD DE BOTONES');
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar que botones tienen onclick');
    const buttonsWithOnclick = Array.from(document.querySelectorAll('button[onclick]')).filter(btn =>
        btn.onclick && btn.onclick.toString().includes('window.location.href')
    );
    if (buttonsWithOnclick.length >= 4) {
        testPass('Encontrados ' + buttonsWithOnclick.length + ' botones con onclick');
    } else {
        testFail('Solo se encontraron ' + buttonsWithOnclick.length + ' botones con onclick (esperado >= 4)');
    }
    
    totalTests++;
    console.log('[TEST ' + totalTests + '] Verificar que enlaces tienen href válido');
    const validLinks = Array.from(document.querySelectorAll('a[href]')).filter(link => {
        const href = link.getAttribute('href');
        return href && (href.startsWith('/') || href.startsWith('http'));
    });
    if (validLinks.length > 0) {
        testPass('Encontrados ' + validLinks.length + ' enlaces con href válido');
    } else {
        testFail('No se encontraron enlaces válidos');
    }
    
    // ════════════════════════════════════════════════════════════════════════
    // 4. PRUEBA INTERACTIVA (OPCIONAL)
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('4. PRUEBA INTERACTIVA DE NAVEGACIÓN');
    
    console.log('%cℹ INFO:', 'color: blue; font-weight: bold', 'Para probar la navegación manualmente:');
    console.log('');
    console.log('1. Cambiar al tab Usuarios:');
    console.log('   switchTab("users")');
    console.log('');
    console.log('2. Hacer clic en botón de Usuarios (simulado):');
    console.log('   // El botón redirigirá a /admin/users');
    console.log('');
    console.log('3. Cambiar al tab Settings:');
    console.log('   switchTab("settings")');
    console.log('');
    console.log('4. Probar enlaces en Settings:');
    console.log('   // Los enlaces están listos para hacer clic');
    console.log('');
    
    // ════════════════════════════════════════════════════════════════════════
    // 5. LISTA DE TODOS LOS BOTONES Y ENLACES
    // ════════════════════════════════════════════════════════════════════════
    
    testHeader('5. INVENTARIO DE BOTONES Y ENLACES');
    
    console.log('%cBotones de navegación encontrados:', 'font-weight: bold');
    const allNavButtons = Array.from(document.querySelectorAll('button')).filter(btn =>
        btn.onclick && btn.onclick.toString().includes('window.location.href')
    );
    allNavButtons.forEach((btn, index) => {
        const onclick = btn.onclick.toString();
        const match = onclick.match(/window\.location\.href\s*=\s*['"]([^'"]+)['"]/);
        if (match) {
            console.log(`   ${index + 1}. "${btn.textContent.trim().substring(0, 50)}" → ${match[1]}`);
        }
    });
    
    console.log('');
    console.log('%cEnlaces encontrados:', 'font-weight: bold');
    const allNavLinks = Array.from(document.querySelectorAll('a[href^="/"]')).filter(link => {
        const href = link.getAttribute('href');
        return href && ['/admin/users', '/packages', '/customers', '/messages'].includes(href);
    });
    allNavLinks.forEach((link, index) => {
        console.log(`   ${index + 1}. "${link.textContent.trim().substring(0, 50)}" → ${link.getAttribute('href')}`);
    });
    
    // ════════════════════════════════════════════════════════════════════════
    // RESUMEN
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
        console.log('%c✓ TODOS LOS BOTONES Y ENLACES ESTÁN CORRECTOS', 'color: green; font-weight: bold; font-size: 16px');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: green; font-weight: bold');
    } else {
        console.log('%c════════════════════════════════════════════════════════════════', 'color: orange; font-weight: bold');
        console.log('%c⚠ ALGUNOS BOTONES O ENLACES TIENEN PROBLEMAS', 'color: orange; font-weight: bold; font-size: 16px');
        console.log('%c════════════════════════════════════════════════════════════════', 'color: orange; font-weight: bold');
    }
    
    console.log('');
    console.log('%cPRUEBA MANUAL RECOMENDADA:', 'color: cyan; font-weight: bold');
    console.log('1. Cambiar a cada tab y hacer clic en los botones');
    console.log('2. Verificar que redirigen correctamente');
    console.log('3. Verificar que no hay errores en la consola');
    console.log('');
    
    return {
        total: totalTests,
        passed: passedTests,
        failed: failedTests,
        percentage: percentage,
        buttons: allNavButtons.length,
        links: allNavLinks.length
    };
})();
