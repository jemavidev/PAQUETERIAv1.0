# 371 — `/administracion/estadisticas-cobro`: cada sección como una tarjeta (bloque) independiente, con orden definido por Jesús

**Pedido original (Jesús):** "de que forma puedes dividir las tarjetas por bloques, la idea
es que por ejemplo 'Estadísticas de cobro', 'Panorama' y 'Ahora', estos 3 por ejemplo sean o
se vean como tarjetas independientes, separadas de forma que se distingan, realiza esto para
las diferentes secciones de esta vista, ya que te estare diciendo cual va de primera, segunda
y el orden de como debe quedar todo. Por ahora esto sera lo ultimo que haga con relacion a
esta vista para continuar con otro enfoque despues."

**Status:** pendiente (bloques prototipados sobre la propuesta del issue 370; falta que
Jesús diga el orden final)

## Contexto

Es el último ajuste de esta vista por ahora (el siguiente enfoque será aparte). Se apoya en
la propuesta del [[370]], que Jesús aprobó a la vista ("se ve mucho mejor"): la propuesta
sigue en su rama/worktree/puerto (`prototipo/estadisticas-cobro-filtros-y-tablas`, `:8011`)
y lo actual (`:8010`) no se toca hasta que Jesús confirme el orden. Después, todo (la
propuesta + los bloques) se reescribe en el código real con pruebas.

## Qué se hace

- Cada sección de la vista es una tarjeta con su propia forma: encabezado con ícono, título,
  aclaración y color propio (Estadísticas de cobro: pizarra · Panorama: azul · Ahora: ámbar ·
  Periodo seleccionado: verde), sombra y anillo, y separación entre bloques. Los paneles de
  antes quedan como tarjetas blancas DENTRO de su bloque.
- El orden de los bloques es una lista de una línea (`_estadisticas_bloques.html`), no
  depende del orden del marcado; para probar órdenes sin tocar código, `?orden=ahora,panorama,
  filtros,periodo` en la URL (solo prototipo).
- Los paneles de adentro (Ingresos, Entregados, Recaudo, Paquetes, tablas...) se reordenan
  moviéndolos: Jesús dirá también ese orden.

## Prototipo (2026-09-21)

Rama `prototipo/estadisticas-cobro-filtros-y-tablas`, commit sobre el del 370 (sin push, NO se
mergea), `:8011`. Lo actual (`:8010`) no se tocó.

- Cuatro bloques: **Estadísticas de cobro** (filtros, pizarra), **Panorama** (azul), **Ahora**
  (ámbar) y **Periodo seleccionado** (verde). Cada uno es una tarjeta con encabezado propio
  (ícono, título, aclaración, y las fechas exactas del periodo en una pastilla), sombra y anillo,
  sobre un lienzo gris claro; los paneles de antes quedan como tarjetas blancas dentro.
- Orden: `ORDEN` en `_estadisticas_bloques.html` (una línea). `?orden=` en la URL lo prueba sin
  editar nada (solo prototipo). Verificado: mover cualquier bloque, incluido el de filtros;
  ids inválidos o repetidos se ignoran; el orden sobrevive al refresco en vivo.
- Verificado en navegador en escritorio y móvil (sin scroll horizontal ni errores de consola) y
  la prueba de comportamiento del 370 sigue completa.

**Orden actual de los paneles de adentro** (para que Jesús diga el nuevo):
1. Estadísticas de cobro: Periodo · Tipo · Cobro · Torre.
2. Panorama: Ingresos · Entregados y Cancelados · SMS enviados por AWS · Tiempos promedio.
3. Ahora: En bodega ahora · Por cobrar en bodega y Deuda contra entrega · Paquete más antiguo /
   Anuncios que nunca llegaron / Clientes registrados · Requieren atención (tabla).
4. Periodo seleccionado: Comparado con el periodo anterior · Evolución del periodo · Recaudo ·
   Paquetes · Clientes · Operación y calidad · SMS del periodo · Detrás de las cifras (tabla).

**Pendiente:** el orden final (de bloques y de paneles) y, con él, pasar TODO (la propuesta del
370 + estos bloques) al código real con pruebas y quitar el andamio del prototipo (`?orden=`).
Antes, confirmar las decisiones abiertas del 370 o dejarlas como están prototipadas.
