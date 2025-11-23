# 📊 Guía de Usuario - Dashboard Mejorado

## Introducción

El nuevo dashboard de PAQUETEX te permite gestionar y visualizar todos tus paquetes de forma rápida y eficiente. Esta guía te mostrará cómo aprovechar al máximo todas sus funcionalidades.

---

## 🚀 Acceso Rápido

**URL**: `https://tu-dominio.com/dashboard`

Al ingresar verás:
- 4 tarjetas con estadísticas principales
- Gráficos visuales de estado
- Lista de paquetes recientes
- Herramientas de búsqueda y filtrado

---

## 📈 Entendiendo las Estadísticas

### Tarjetas Principales

#### 1️⃣ Total Paquetes (Azul)
- Muestra todos los paquetes en el sistema
- Incluye procesados y pendientes
- Se actualiza en tiempo real

#### 2️⃣ Procesados (Verde)
- Paquetes que ya fueron recibidos
- Indica paquetes completados
- Porcentaje del total

#### 3️⃣ Pendientes (Amarillo)
- Paquetes anunciados pero no recibidos
- Requieren atención
- Prioridad de procesamiento

#### 4️⃣ Hoy (Morado)
- Paquetes anunciados hoy
- Actividad del día actual
- Indicador de volumen diario

---

## 🔍 Búsqueda y Filtros

### Búsqueda por Texto

**Campo de búsqueda**: Barra grande en la parte superior

Puedes buscar por:
- ✅ Nombre del cliente
- ✅ Número de teléfono
- ✅ Número de guía
- ✅ Código de tracking

**Ejemplo**: Escribe "Juan" para ver todos los paquetes de clientes llamados Juan.

### Filtro por Estado

**Dropdown de estado**: Al lado del campo de búsqueda

Opciones:
- **Todos los estados**: Muestra todos los paquetes
- **Pendientes**: Solo paquetes no procesados
- **Procesados**: Solo paquetes completados

### Limpiar Filtros

**Botón X**: Elimina todos los filtros aplicados y muestra todos los paquetes.

---

## 📦 Lista de Paquetes

### Información Mostrada

Cada tarjeta de paquete muestra:

1. **Nombre del Cliente** (Grande, en negrita)
2. **Estado** (Badge de color)
   - 🟢 Verde = Procesado
   - 🟡 Amarillo = Pendiente
3. **Teléfono** (Con icono 📞)
4. **Número de Guía** (Con icono 🏷️)
5. **Código de Tracking** (Con icono 📋)
6. **Fecha de Anuncio** (Con icono 📅)

### Ver Detalles

**Click en cualquier paquete** para ver información completa:
- Historial del paquete
- Eventos registrados
- Información del cliente
- Opciones de gestión

---

## 💾 Exportar Datos

### ¿Para qué exportar?

- Crear reportes personalizados
- Análisis en Excel
- Respaldo de información
- Compartir con otros sistemas

### Cómo Exportar

1. **Click en "Exportar"** (botón con icono de descarga)
2. **Selecciona el formato**:
   - **CSV**: Para Excel, Google Sheets
   - **JSON**: Para desarrolladores, APIs

3. **El archivo se descarga automáticamente**

### Datos Incluidos en la Exportación

- ID del paquete
- Nombre del cliente
- Teléfono
- Número de guía
- Código de tracking
- Estado (Procesado/Pendiente)
- Fecha de anuncio

**Nota**: La exportación respeta los filtros aplicados. Si buscaste "Juan", solo se exportarán los paquetes de Juan.

---

## 🔄 Actualizar Datos

### Botón Actualizar

**Icono de flechas circulares** en la parte superior derecha.

**Cuándo usar**:
- Después de procesar paquetes
- Para ver cambios recientes
- Si los datos parecen desactualizados

**Qué actualiza**:
- Estadísticas de las tarjetas
- Lista de paquetes
- Gráficos visuales

---

## 📊 Gráficos Visuales

### Barras de Progreso

**Sección "Resumen Visual"**

#### Estado de Paquetes
- **Barra Verde**: % de paquetes procesados
- **Barra Amarilla**: % de paquetes pendientes

**Interpretación**:
- Barra llena = 100% de ese tipo
- Barra vacía = 0% de ese tipo
- Ideal: Barra verde llena, amarilla vacía

### Indicadores de Actividad

#### Tarjeta "Hoy"
- Paquetes anunciados en el día actual
- Útil para medir actividad diaria

#### Tarjeta "Esta Semana"
- Paquetes de los últimos 7 días
- Útil para tendencias semanales

---

## 📄 Paginación

### Navegación entre Páginas

**Controles en la parte inferior de la lista**

- **Anterior**: Ver página previa
- **Siguiente**: Ver página siguiente
- **Indicador**: "Página X de Y"

**Límite**: 8 paquetes por página

**Tip**: Usa filtros para reducir resultados y encontrar más rápido.

---

## 💡 Consejos y Trucos

### 1. Búsqueda Rápida
- Escribe solo parte del nombre o número
- No necesitas escribir completo
- La búsqueda es instantánea (después de 0.5 segundos)

### 2. Filtros Combinados
- Puedes usar búsqueda + filtro de estado
- Ejemplo: Buscar "Juan" + Filtrar "Pendientes"
- Resultado: Solo paquetes pendientes de Juan

### 3. Exportación Selectiva
- Aplica filtros antes de exportar
- Solo se exportarán los resultados filtrados
- Útil para reportes específicos

### 4. Monitoreo Diario
- Revisa la tarjeta "Hoy" cada mañana
- Identifica paquetes pendientes rápidamente
- Usa el filtro "Pendientes" para priorizar

### 5. Análisis Semanal
- Revisa "Esta Semana" los lunes
- Compara con semanas anteriores
- Identifica tendencias de volumen

---

## ❓ Preguntas Frecuentes

### ¿Con qué frecuencia se actualizan los datos?
Los datos se actualizan cada vez que:
- Cargas la página
- Haces click en "Actualizar"
- Cambias de página en la paginación

### ¿Puedo ver paquetes antiguos?
Sí, todos los paquetes están disponibles. Usa la paginación para navegar o busca por fecha/nombre.

### ¿Los filtros afectan las estadísticas?
No, las tarjetas de estadísticas siempre muestran el total. Los filtros solo afectan la lista de paquetes.

### ¿Puedo exportar todos los paquetes?
Sí, asegúrate de no tener filtros aplicados (click en X para limpiar) y luego exporta.

### ¿Qué formato de exportación debo usar?
- **CSV**: Si vas a abrir en Excel o Google Sheets
- **JSON**: Si necesitas los datos para programación o APIs

### ¿Puedo personalizar el dashboard?
Actualmente no, pero está en desarrollo. Próximamente podrás:
- Elegir qué widgets ver
- Cambiar el orden de las tarjetas
- Configurar alertas personalizadas

---

## 🎯 Casos de Uso Comunes

### Caso 1: Revisar Paquetes Pendientes
1. Click en filtro "Pendientes"
2. Revisa la lista
3. Click en cada paquete para procesarlo

### Caso 2: Buscar Paquete de un Cliente
1. Escribe el nombre en búsqueda
2. Encuentra el paquete en la lista
3. Click para ver detalles

### Caso 3: Generar Reporte Mensual
1. Exporta en formato CSV
2. Abre en Excel
3. Crea tablas dinámicas y gráficos

### Caso 4: Monitorear Actividad Diaria
1. Revisa tarjeta "Hoy" cada mañana
2. Compara con días anteriores
3. Identifica picos de actividad

### Caso 5: Análisis de Eficiencia
1. Revisa % de procesados en gráfico
2. Identifica cuellos de botella
3. Prioriza paquetes pendientes

---

## 🆘 Solución de Problemas

### No veo ningún paquete
✅ **Solución**: 
- Limpia los filtros (botón X)
- Actualiza la página (F5)
- Verifica que haya paquetes en el sistema

### La búsqueda no funciona
✅ **Solución**:
- Espera 0.5 segundos después de escribir
- Verifica que escribiste correctamente
- Intenta con menos caracteres

### No puedo exportar
✅ **Solución**:
- Verifica que haya paquetes para exportar
- Intenta con otro formato
- Revisa que tu navegador permita descargas

### Los números no coinciden
✅ **Solución**:
- Click en "Actualizar"
- Recarga la página completa
- Verifica que no haya filtros aplicados

---

## 📱 Uso en Móvil

El dashboard está optimizado para móviles:

- ✅ Tarjetas apiladas verticalmente
- ✅ Botones grandes y táctiles
- ✅ Texto legible sin zoom
- ✅ Navegación fluida

**Tip**: Usa en modo horizontal para mejor visualización de gráficos.

---

## 🎓 Mejores Prácticas

1. **Revisa el dashboard diariamente** para estar al día
2. **Usa filtros** para trabajar más eficientemente
3. **Exporta regularmente** para respaldos
4. **Actualiza después de cambios** para ver resultados
5. **Combina búsqueda y filtros** para precisión

---

## 📞 Soporte

¿Necesitas ayuda?

- 📧 Email: soporte@paquetex.com
- 📱 WhatsApp: +57 XXX XXX XXXX
- 🌐 Web: www.paquetex.com/soporte

---

**¡Disfruta tu nuevo dashboard mejorado!** 🎉
