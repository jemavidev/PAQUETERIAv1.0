# 238 — `/mis-paquetes`: bug real, no-Principal veía lo que ÉL anunció para otro residente

**Pedido original (cliente):** "Sigo viendo paquetes de otras personas
(Anunciados y Cancelados no están funcionando así) y no soy en residente
principal."

**Status:** implementado

## Diagnóstico (`/diagnosing-bugs`)

Confirmado con datos reales del ambiente local (Postgres dev): la Persona
de prueba +573002596319 (no-Principal) tenía 2 Paquetes donde ELLA es
`announced_by_phone` pero el `recipient_phone`/`recipient_name` es OTRO
residente de su misma unidad -- uno en ANUNCIADO, uno en CANCELADO, calzando
exacto con lo reportado.

Causa raíz: el filtro de issue 235 para no-Principal seguía siendo
`announced_by_phone.in_([mi_telefono]) OR recipient_phone.in_([mi_telefono])`
-- igual que el Principal, solo que con un único teléfono en la lista. Un
no-Principal que anuncia un paquete PARA un housemate (`destinatario` !=
"yo mismo") seguía viendo ese paquete por el lado `announced_by_phone`,
mostrando el nombre del OTRO residente -- justo lo que el pedido original
de 235 pedía excluir ("solo paquetes que estén A NOMBRE DE quien entró en
la cuenta").

## Fix

`customer_paquetes.py::mis_paquetes` -- para no-Principal, la condición
pasa a ser estrictamente `Paquete.recipient_phone == persona.telefono`
(sin `announced_by_phone`). El Principal no cambia (sigue viendo TODO,
anunciado o recibido, de cualquier Teléfono de la unidad).

Regresión: `test_no_principal_no_ve_lo_que_anuncio_para_otro_residente`
en `test_mis_paquetes.py` -- Beto (no-Principal) anuncia un paquete para
Ana (Principal de su unidad), Beto no debe verlo en su propio
`/mis-paquetes`.
