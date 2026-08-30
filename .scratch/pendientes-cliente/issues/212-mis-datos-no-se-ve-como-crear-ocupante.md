# 212 — `/mis-datos`: no se ve cómo crear un residente/ocupante

**Pedido original (cliente):** "Crear ocupante: No sé cómo crear un
residente en esta vista." — la ruta (`POST /mis-datos/ocupantes`) existe,
falta confirmar si el disparador en la UI está ausente, escondido, o poco
claro.

**Status:** pendiente

## Investigación

El formulario "Agregar un nuevo Residente" SÍ existe y funciona (`verify.html`,
dentro del tab "Residentes"). Confirmado en el ambiente local que el
teléfono de prueba (+573002596319) es Ocupante Principal de un apartamento
-- `mostrar_tab_ocupantes` debería ser `True` y el tab "Residentes" debería
estar visible con el formulario al final. Probable causa: no se vio el tab
(reorganizado en pestañas hace tiempo, issue 39) o no se hizo scroll hasta
el final del panel. Falta que el cliente confirme si el tab "Residentes"
aparece y si el formulario "Agregar un nuevo Residente" es visible ahí --
si no aparece con una cuenta real, es un bug distinto a re-investigar.

