# ❓ FAQ: Nombres Personalizados para Paquetes

## Preguntas Frecuentes

### 1. ¿Qué hace esta funcionalidad?

Permite editar el nombre del destinatario al anunciar un paquete, sin modificar el nombre del cliente en la base de datos. Es como poner un "alias" o "nombre temporal" solo para ese paquete específico.

---

### 2. ¿El nombre del cliente se modifica en la base de datos?

**NO.** El cliente mantiene su nombre original. Solo el paquete/anuncio específico usa el nombre editado.

**Ejemplo:**
- Cliente en BD: "JUAN PÉREZ"
- Editas a: "JUAN PÉREZ - OFICINA"
- Resultado: Cliente sigue siendo "JUAN PÉREZ", pero el paquete se registra como "JUAN PÉREZ - OFICINA"

---

### 3. ¿Qué pasa si anuncio otro paquete para el mismo cliente?

El sistema mostrará el **nombre original** del cliente nuevamente. Cada paquete puede tener un nombre diferente.

**Ejemplo:**
```
Paquete 1: JUAN PÉREZ - OFICINA
Paquete 2: JUAN PÉREZ - CASA
Paquete 3: JUAN PÉREZ (sin editar)
```

---

### 4. ¿Cuándo debo usar esta funcionalidad?

Úsala cuando:
- El paquete va a una ubicación específica (oficina, casa, bodega)
- El paquete es para otra persona (familiar, empleado)
- Necesitas agregar información adicional (departamento, piso, etc.)
- Quieres especificar un destinatario diferente sin crear un nuevo cliente

---

### 5. ¿Cómo edito el nombre?

1. Ingresa el teléfono del cliente
2. Espera a que aparezca el nombre
3. Haz clic en el **ícono de lápiz** (✏️) al lado del nombre
4. Edita el nombre como necesites
5. Haz clic en "Anunciar Paquete"

---

### 6. ¿Puedo editar el nombre de un cliente nuevo?

No es necesario. Para clientes nuevos, el campo ya está editable desde el inicio. Esta funcionalidad es solo para clientes existentes.

---

### 7. ¿Los SMS y emails usan el nombre editado?

**SÍ.** Las notificaciones (SMS, emails) usarán el nombre que aparece en el paquete, que puede ser el editado.

---

### 8. ¿Puedo deshacer la edición?

Sí, simplemente recarga la página o ingresa el teléfono nuevamente. El sistema mostrará el nombre original del cliente.

---

### 9. ¿Qué pasa si no edito el nombre?

El sistema usa el nombre original del cliente. La edición es **opcional**.

---

### 10. ¿Afecta las estadísticas del cliente?

**NO.** Todos los paquetes siguen asociados al mismo cliente, independientemente del nombre usado en cada paquete. Las estadísticas (total de paquetes, historial, etc.) se mantienen intactas.

---

### 11. ¿Puedo ver el historial de nombres usados?

Sí, en el historial de paquetes del cliente verás el nombre específico usado en cada entrega.

---

### 12. ¿Hay un límite de caracteres para el nombre editado?

Sí, el límite es de **100 caracteres** (igual que el nombre del cliente).

---

### 13. ¿Qué pasa si dos paquetes tienen nombres diferentes pero el mismo teléfono?

Es completamente normal y esperado. El sistema los asocia al mismo cliente por el teléfono, pero cada paquete puede tener su propio nombre de destinatario.

---

### 14. ¿Puedo buscar paquetes por el nombre editado?

Sí, puedes buscar paquetes por cualquier nombre (original o editado) en el sistema de búsqueda.

---

### 15. ¿Esta funcionalidad está disponible en todas las vistas?

Actualmente está disponible en:
- ✅ `/announce-papyrus` (Anuncio rápido PAPYRUS)

Próximamente podría agregarse a otras vistas de anuncio.

---

## Casos de Uso Comunes

### Caso 1: Empresa con múltiples ubicaciones
```
Cliente: DISTRIBUIDORA XYZ
Teléfono: 3001111111

Paquetes:
- DISTRIBUIDORA XYZ - BODEGA NORTE
- DISTRIBUIDORA XYZ - BODEGA SUR
- DISTRIBUIDORA XYZ - OFICINA PRINCIPAL
```

### Caso 2: Familia con un solo teléfono
```
Cliente: JUAN PÉREZ
Teléfono: 3002222222

Paquetes:
- JUAN PÉREZ (para él)
- MARÍA PÉREZ (esposa)
- PEDRO PÉREZ (hijo)
- JUAN PÉREZ - OFICINA
```

### Caso 3: Edificio o conjunto residencial
```
Cliente: EDIFICIO CENTRAL
Teléfono: 3003333333

Paquetes:
- EDIFICIO CENTRAL - APT 301
- EDIFICIO CENTRAL - APT 502
- EDIFICIO CENTRAL - ADMINISTRACIÓN
```

---

## Solución de Problemas

### Problema: No veo el ícono de lápiz

**Posibles causas:**
1. El cliente no existe (es nuevo)
2. El navegador tiene caché antiguo
3. El campo aún está cargando

**Solución:**
1. Verifica que el teléfono sea de un cliente existente
2. Recarga la página (Ctrl + Shift + R)
3. Espera a que aparezca el mensaje "Cliente encontrado"

---

### Problema: El nombre del cliente cambió en la base de datos

**Esto NO debería pasar.** Si ocurre:
1. Reporta el bug inmediatamente
2. Proporciona el teléfono del cliente afectado
3. Proporciona el número de guía del paquete

---

### Problema: No puedo editar el nombre

**Posibles causas:**
1. No hiciste clic en el ícono de lápiz
2. El campo está deshabilitado por algún error

**Solución:**
1. Haz clic en el ícono de lápiz (✏️)
2. Recarga la página e intenta nuevamente
3. Verifica la consola del navegador (F12) por errores

---

## Mejores Prácticas

### ✅ Recomendado:
- Usar nombres descriptivos: "JUAN PÉREZ - OFICINA"
- Mantener formato consistente
- Agregar ubicación cuando sea relevante
- Usar mayúsculas para consistencia

### ❌ No recomendado:
- Cambiar completamente el nombre sin relación al cliente
- Usar abreviaturas confusas
- Agregar información innecesaria
- Usar caracteres especiales excesivos

---

## Glosario

**Cliente:** Persona o empresa registrada en la base de datos con un teléfono único.

**Nombre Original:** El nombre del cliente tal como está registrado en la base de datos.

**Nombre Personalizado:** El nombre editado que se usa solo para un paquete específico.

**Anuncio:** Registro de un paquete que está en camino o esperando ser recibido.

**Destinatario:** La persona que recibirá el paquete (puede ser diferente al cliente registrado).

---

## Contacto y Soporte

Si tienes más preguntas o encuentras algún problema:

1. **Reporta bugs:** Describe el problema con capturas de pantalla
2. **Sugerencias:** Comparte ideas para mejorar la funcionalidad
3. **Dudas:** Consulta con el equipo de desarrollo

---

**Última actualización:** 2024-12-17
**Versión:** 1.0
