# 346 — Investigación: "Asignar apartamento" aparece desactivado donde antes estaba activo

**Pedido original (cliente):**
"Adicional verifica porque no aparece activado donde en algunos casos si
deberia aparecer activado" (seguido de la confusión previa: "no se porque
ahora los iconos de asignar apartamento aparecen desactivados en todas las
vistas, pero menos en el modal de la vista Residentes, no se porque").

**Status:** implementado, pendiente confirmar visualmente

## Hallazgo (verificado en vivo en localhost:8010)

No es un bug de un caso puntual -- es consecuencia directa de issue 343
("remueve el icono Asignar apartamento... de la vista /paquetes", sin
acotar a mobile en ese momento):

- **Modal "Ver" de `/paquetes`** (issue 342): funciona correctamente --
  probado en vivo con un paquete Anunciado sin unidad ("TEST"), el ícono
  🏠 abre "Asignar apartamento" con normalidad.
- **Columna "Torre y Apartamento" de DESKTOP** (`packages/_resultados.html`,
  `<td class="hidden sm:table-cell ...">`): issue 343 retiró el botón
  activo de ahí también (no solo de mobile) -- ahora SIEMPRE muestra el
  indicador apagado, incluso para paquetes Anunciado/Recibido sin unidad,
  donde antes de issue 343 sí era clicable. Confirmado en vivo con "TEST" y
  "PEDRO EL ESCAMOSO" (ambos Anunciados, sin unidad, ícono gris en
  desktop).
- **`/residentes`** (fila + su propio modal "Asignar apartamento"): función
  aparte, no tocada por ningún issue de esta sesión -- sigue funcionando
  igual que siempre (de ahí que el cliente la viera como la única
  excepción "normal").

## Resolución

El cliente confirmó con un caso real ("Paquete X5NW" debería verse con
color, "Paquete D8GZ" debería quedar gris) y pidió restaurar el botón
activo -- **solo en desktop**; en mobile el ícono sigue sin mostrarse en
ningún estado (reconfirmado explícitamente: "al cambiar a la version
mobil, este icono no se debe mostrar").

`packages/_resultados.html`: la columna de desktop (`<td class="hidden
sm:table-cell ...">`) recupera las 3 ramas originales -- dirección /
botón activo `data-open="modal-asignar-apto-<id>"` en ANUNCIADO-RECIBIDO
sin unidad / indicador apagado en ENTREGADO-CANCELADO sin unidad. La
píldora de mobile (issue 345) no se tocó -- sigue condicionada solo a
`p.direccion_corta`, sin ninguna rama de estado.

`test_icono_asignar_apartamento_en_anunciado_y_recibido_sin_unidad`
actualizado: el conteo de "🏠</button>" sube de 2 a 4 (2 paquetes x 2
ubicaciones activas ahora: columna desktop + modal Ver). Suite completa:
229 passed.
