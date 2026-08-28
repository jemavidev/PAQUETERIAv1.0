# 200 — `/administracion/notificaciones`: layout de acordeón

**Pedido original (cliente):**
Pedido repetido 3+ veces ("mejora... tabs y sub tabs", "dame alternativas")
hasta que el cliente señaló explícitamente que quería VER las opciones, no
más descripciones en texto: "pero sigio sin ver los podibles cambios de
como se vera la vista de las notificaciones, te lo he pedido ya con esta
mas de 3 veces". Se prototiparon 3 layouts en vivo (evento como tab, canal
como tab, acordeón) directo sobre `/administracion/notificaciones` vía
`?variant=a/b/d`, contra datos reales. Respuesta del cliente: "VAMOS CON LA
OPCION d Y ESTARE REALIZANDO MODIFICACIONES MAS ADELANTE".

**Status:** implementado

## Cómo se prototipó (nota de proceso, `/prototype` skill)

3 templates throwaway (`admin/_proto_variant_{a,b,d}.html` + un switcher
flotante), servidos por la MISMA ruta real vía un query param `?variant=`
que no tocaba la ruta por defecto. El cliente los abrió en su propio
navegador contra el servidor de dev local, con datos reales y los botones
"Guardar" funcionando de verdad. Nada de esto se comiteó nunca (se
descartó directo al elegir D, no hizo falta una rama aparte para
preservarlo).

## Implementación (D elegida, ya integrada a la plantilla real)

- `admin/notificaciones.html`: cada una de las 8 tarjetas evento/motivo
  pasa de `<div>` siempre expandido a `<details>` nativo (cero JS) --
  mismo contenido interno de siempre (pestañas de canal, errores, preview
  de Email), solo cambia el contenedor exterior.
- La primera fila abre por defecto (para que la página no arranque 100%
  colapsada); cualquier fila con un error de validación propio o que se
  acabe de guardar también se abre automáticamente -- mismo criterio que
  ya usaba `canal_activo` para reabrir la pestaña de canal correcta,
  extendido un nivel más arriba.
- Chevron que gira al abrir/cerrar vía `details[open] > summary svg`, sin
  JS.
- `admin.py`: se quitó el `variant` query param y el diccionario
  `_PROTO_TEMPLATES` de la ruta real -- ya no hace falta, la decisión está
  tomada. Los 5 archivos `_proto_*` se borraron.

## Verificación

- 3 tests nuevos: la primera fila abre por defecto y otra no; un error en
  una fila que NO es la primera abre su propio acordeón; un guardado
  exitoso en una fila que no es la primera también lo abre.
- `test_admin_notificaciones.py` completo: 21 tests, todos pasan (los 18
  ya existentes, sin tocarlos, siguen viendo exactamente el mismo
  contenido interno).
- Verificado en vivo contra el servidor de dev local: 8 acordeones reales
  en la página (el conteo de `<details>` da 10 porque el menú de cuenta
  del header también usa `<details>`, 2 instancias mobile/desktop -- nada
  nuevo, ya estaba ahí), solo 1 abierto por defecto.

## Pendiente (el cliente avisó que seguirá pidiendo ajustes)

- Deploy a test.papyrus.com.co.
- Cualquier ajuste adicional que el cliente pida sobre este layout.
