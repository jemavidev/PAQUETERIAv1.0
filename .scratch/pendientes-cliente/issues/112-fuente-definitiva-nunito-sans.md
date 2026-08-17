# 112 — Fuente definitiva en /paquetes: Nunito Sans (reemplaza Roboto)

**Pedido original (cliente):**
"creo que vamos con Nunito Sans." -- tras comparar Roboto (issue 110) más
6 alternativas en una galería aparte.

**Status:** implementado

## Contexto

[[110]] había dejado Roboto instalada como primera fuente real de
`/paquetes` a pedido explícito. El mismo día, tras ver el resultado en
vivo, el cliente pidió alternativas -- se generó una galería comparando 7
tipografías sobre capturas reales de la vista (no mockups de texto
suelto). El cliente eligió Nunito Sans.

## Implementación

- `packages/list.html`, `{% block head %}`: el `<link>` de Google Fonts y
  el `font-family` de `#vista-paquetes` cambian de `Roboto` a `Nunito
  Sans` -- mismo mecanismo exacto de [[110]] (mismo alcance: solo esta
  vista, header/footer compartidos sin tocar), pesos 400/500/600/700/800
  (Nunito Sans SÍ tiene 600/800 nativos, a diferencia de Roboto -- no hace
  falta aproximar ningún peso esta vez).

## Verificación

- Playwright contra el servidor local real: `getComputedStyle` confirma
  `font-family` empieza con "Nunito Sans" en el título y en la tabla; el
  header compartido sigue en `system-ui` sin cambios.
- Suite completa: cambio puramente de presentación, sin lógica nueva --
  no se esperan tests nuevos; se corre igual para confirmar cero
  regresiones.
- Pendiente: deploy a test.papyrus.com.co.
