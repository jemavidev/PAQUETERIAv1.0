/**
 * PAQUETES EL CLUB v4.0 - Test Scroll Mobile
 * Script de prueba rápida para verificar scroll en móviles
 * 
 * Uso: Copiar y pegar en la consola del navegador
 */

(function() {
    'use strict';
    
    console.log('🧪 Iniciando prueba de scroll móvil...\n');
    
    // Test 1: Información del dispositivo
    console.log('📱 INFORMACIÓN DEL DISPOSITIVO');
    console.log('─────────────────────────────');
    console.log('User Agent:', navigator.userAgent);
    console.log('Ancho de pantalla:', window.innerWidth + 'px');
    console.log('Alto de pantalla:', window.innerHeight + 'px');
    console.log('Ratio de píxeles:', window.devicePixelRatio);
    console.log('Orientación:', window.innerWidth > window.innerHeight ? 'Landscape' : 'Portrait');
    console.log('');
    
    // Test 2: Dimensiones del documento
    console.log('📏 DIMENSIONES DEL DOCUMENTO');
    console.log('─────────────────────────────');
    console.log('HTML height:', document.documentElement.scrollHeight + 'px');
    console.log('Body height:', document.body.scrollHeight + 'px');
    console.log('Viewport height:', document.documentElement.clientHeight + 'px');
    console.log('Contenido excede viewport:', document.body.scrollHeight > window.innerHeight ? '✅ Sí' : '❌ No');
    console.log('');
    
    // Test 3: Posición de scroll
    console.log('📍 POSICIÓN DE SCROLL');
    console.log('─────────────────────────────');
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollHeight = document.documentElement.scrollHeight;
    const clientHeight = document.documentElement.clientHeight;
    const maxScroll = scrollHeight - clientHeight;
    const scrollPercent = maxScroll > 0 ? (scrollTop / maxScroll * 100).toFixed(1) : 0;
    
    console.log('Scroll actual:', scrollTop + 'px');
    console.log('Scroll máximo:', maxScroll + 'px');
    console.log('Porcentaje:', scrollPercent + '%');
    console.log('Puede hacer scroll:', maxScroll > 0 ? '✅ Sí' : '❌ No');
    console.log('');
    
    // Test 4: Estilos de elementos críticos
    console.log('🎨 ESTILOS DE ELEMENTOS CRÍTICOS');
    console.log('─────────────────────────────');
    
    const checkElement = (selector, name) => {
        const element = document.querySelector(selector);
        if (!element) {
            console.log(`${name}: ❌ No encontrado`);
            return;
        }
        
        const styles = window.getComputedStyle(element);
        console.log(`${name}:`);
        console.log(`  - overflow-y: ${styles.overflowY}`);
        console.log(`  - height: ${styles.height}`);
        console.log(`  - min-height: ${styles.minHeight}`);
        console.log(`  - max-height: ${styles.maxHeight}`);
        console.log(`  - position: ${styles.position}`);
        
        // Verificar problemas
        const issues = [];
        if (styles.overflowY === 'hidden') issues.push('overflow-y: hidden');
        if (styles.height !== 'auto' && styles.height.includes('vh')) issues.push('altura en vh');
        if (element.scrollHeight > element.clientHeight && styles.overflowY === 'visible') {
            issues.push('contenido excede pero overflow es visible');
        }
        
        if (issues.length > 0) {
            console.log(`  ⚠️ Problemas: ${issues.join(', ')}`);
        } else {
            console.log(`  ✅ Sin problemas detectados`);
        }
        console.log('');
    };
    
    checkElement('html', 'HTML');
    checkElement('body', 'BODY');
    checkElement('main', 'MAIN');
    checkElement('.container', 'CONTAINER');
    
    // Test 5: Verificar scroll funcional
    console.log('🔄 PRUEBA DE SCROLL FUNCIONAL');
    console.log('─────────────────────────────');
    
    const originalScroll = window.pageYOffset;
    
    // Intentar hacer scroll
    window.scrollTo(0, 100);
    
    setTimeout(() => {
        const newScroll = window.pageYOffset;
        
        if (newScroll !== originalScroll) {
            console.log('✅ Scroll funciona correctamente');
            console.log(`   Scroll cambió de ${originalScroll}px a ${newScroll}px`);
        } else {
            console.log('❌ Scroll no funciona');
            console.log('   El scroll no cambió después de intentar scrollear');
        }
        
        // Restaurar posición original
        window.scrollTo(0, originalScroll);
        
        // Test 6: Prueba de scroll al final
        console.log('');
        console.log('🎯 PRUEBA DE SCROLL AL FINAL');
        console.log('─────────────────────────────');
        
        // Scroll al final
        window.scrollTo(0, document.body.scrollHeight);
        
        setTimeout(() => {
            const finalScroll = window.pageYOffset;
            const reachedBottom = Math.abs(finalScroll - maxScroll) < 10;
            
            if (reachedBottom) {
                console.log('✅ Se puede llegar al final del documento');
                console.log(`   Scroll final: ${finalScroll}px de ${maxScroll}px`);
            } else {
                console.log('❌ NO se puede llegar al final del documento');
                console.log(`   Scroll final: ${finalScroll}px de ${maxScroll}px`);
                console.log(`   Diferencia: ${maxScroll - finalScroll}px`);
            }
            
            // Restaurar posición original
            window.scrollTo(0, originalScroll);
            
            // Resumen final
            console.log('');
            console.log('📊 RESUMEN DE LA PRUEBA');
            console.log('═════════════════════════════');
            
            const tests = [
                { name: 'Dispositivo móvil', pass: window.innerWidth <= 768 },
                { name: 'Contenido excede viewport', pass: document.body.scrollHeight > window.innerHeight },
                { name: 'Scroll funcional', pass: newScroll !== originalScroll },
                { name: 'Puede llegar al final', pass: reachedBottom },
                { name: 'Body permite scroll', pass: window.getComputedStyle(document.body).overflowY !== 'hidden' },
                { name: 'HTML permite scroll', pass: window.getComputedStyle(document.documentElement).overflowY !== 'hidden' }
            ];
            
            const passed = tests.filter(t => t.pass).length;
            const total = tests.length;
            
            tests.forEach(test => {
                console.log(`${test.pass ? '✅' : '❌'} ${test.name}`);
            });
            
            console.log('');
            console.log(`Resultado: ${passed}/${total} pruebas pasadas`);
            
            if (passed === total) {
                console.log('🎉 ¡Todas las pruebas pasaron! El scroll funciona correctamente.');
            } else {
                console.log('⚠️ Algunas pruebas fallaron. Revisar los problemas detectados arriba.');
                console.log('');
                console.log('💡 SUGERENCIAS:');
                console.log('1. Verificar que no hay elementos con overflow: hidden');
                console.log('2. Asegurar que body y html tienen height: auto');
                console.log('3. Verificar que main tiene flex: 1 1 auto');
                console.log('4. Activar el modo debug en mobile-scroll-debug.js');
                console.log('5. Ejecutar scrollDebug.fix() para aplicar correcciones');
            }
            
            console.log('');
            console.log('🔧 COMANDOS ÚTILES:');
            console.log('─────────────────────────────');
            console.log('scrollDebug.analyze() - Analizar problemas');
            console.log('scrollDebug.fix() - Aplicar correcciones');
            console.log('scrollDebug.report() - Reportar problemas');
            console.log('');
            
        }, 500);
    }, 500);
})();
