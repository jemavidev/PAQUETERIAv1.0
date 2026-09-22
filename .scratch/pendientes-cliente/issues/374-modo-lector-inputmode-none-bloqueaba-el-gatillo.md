# 374 — Modo lector: `inputmode="none"` impedía que el gatillo del F7 llenara el campo

**Reporte original (Jesús), probando en el F7 real:** "cuando esta activado el lector de codigos se dispara
pero no esta capturando el codigo que lee, si lo hago por medio de la captura del input si funciona, pero
cuando se tiene el lector activo no captura el dato".

**Status:** implementado, pendiente que Jesús lo confirme en el F7 real (localhost por red local, ver abajo)

## Diagnóstico

El modo lector (ticket 10, `.scratch/captura-guia-lector-camara`) ponía `inputmode="none"` en el campo al
enfocarlo por código, para que no apareciera el teclado en pantalla. Ese atributo le dice al navegador que el
campo no necesita una conexión de entrada normal. Hipótesis (no confirmada con el fabricante, pero consistente
con el síntoma exacto reportado): el mecanismo con el que el F7 inyecta el texto leído depende de esa
conexión, así que con `inputmode="none"` el gatillo "dispara" (el motor de escaneo decodifica) pero no tiene
dónde escribir. Al tocar el campo a mano, el propio código revertía `inputmode` a `"text"` (para mostrar el
teclado) — y ahí sí funcionaba, coincidiendo exactamente con lo reportado.

No se pudo reproducir en un navegador de escritorio/simulado (es un comportamiento del propio mecanismo de
inyección del F7, no visible sin el equipo) — se corrigió por hipótesis y quedó pendiente que Jesús la
confirme en el equipo real.

## Decisión

Se quita `inputmode="none"` por completo. El campo se queda con el `inputmode="text"` que ya trae de fábrica,
tanto con el modo lector activado como desactivado. Se pierde la ventaja cosmética original (que el teclado en
pantalla no apareciera al enfocar por código) — se prefiere eso a que el lector físico no funcione, que es la
razón de ser de todo el modo lector.

Como consecuencia, el listener que revertía `inputmode` al tocar el campo a mano ya no hace falta (nunca se
aleja de "text") y se retiró.

## Verificación

- `tests/browser/test_modo_lector.py` y `test_modo_lector_entregar.py`: las aserciones que esperaban
  `inputmode == "none"` al enfocar por el modo lector pasan a esperar `"text"`; el test que verificaba la
  reversión al tocar el campo se reemplazó por uno que solo confirma que teclear a mano sigue funcionando.
- CONTEXT.md (glosario, "Modo lector") y el manual del Operador actualizados para no prometer "sin teclado en
  pantalla".
- Pendiente: confirmación de Jesús en el F7 real -- ver [[375]] para cómo probar contra `localhost` por red
  local en vez de desplegar a test.papyrus.com.co en cada intento.
