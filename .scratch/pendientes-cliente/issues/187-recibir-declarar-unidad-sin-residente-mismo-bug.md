# 187 — "Recibir" (declarar unidad inline) tenía el mismo bug que [[186]]

**Pedido original:** "acabo de probar con este nuevo caso 'ESTE ES UN CLIENTE FANTASMA 5AWR' y
pasa lo mismo y no se corrigio, analiza lo que se hizo en todos los flujos y dime que pasa y como
se corrije."

**Status:** implementado

## Diagnóstico

Reconstruido con datos reales de la base local: el paquete se anunció por WhatsApp
("clientefantasma"), sin unidad. Luego se usó el modal "**Recibir**" (no "Asignar apartamento") --
ese modal trae su PROPIO picker Torre/Apartamento inline cuando el destinatario no tiene unidad
(`modal_recibir`, `sin_apartamento=True`). Ese sub-paso y el de "elegir/crear residente" son
**independientes y ambos opcionales por diseño** (`receive_action`, `packages.py`): eligiendo
Torre 2/Apto 302 pero sin tocar el radio "Nuevo residente" (ninguno viene marcado por defecto), el
paquete quedó **RECIBIDO** mostrando esa unidad en Dirección, sin ningún Ocupante real vinculado --
exactamente el mismo síntoma que [[186]], confirmado con la base: `recipient_name` seguía
literal el nombre del anunciante ("ESTE ES UN CLIENTE FANTASMA"), sin ningún Ocupante nuevo
creado en TORRE 2/302.

[[186]] solo cubrió el modal "Asignar apartamento" (`assign_apartment_action`) -- el mismo patrón
de bug vive DUPLICADO en `receive_action` (la ruta `/paquetes/{id}/recibir`), que también puede
asignar unidad sin resolver residente, y NO estaba cubierto por ese fix.

## Cambio

- `packages.py` (`receive_action`): mismo criterio que [[186]] -- si se asignó Torre+Apartamento
  EN ESE MISMO envío (`asigno_apartamento_ahora`, capturado antes de que `corregir_apartamento`
  mute `paquete.snapshot_apartamento`) y no se resolvió ningún residente
  (`hay_resolucion_residente`, ni `candidato_idx` ni `nuevo_ocupante_nombre`), el redirect final
  cambia de `destino` (que puede ser `/paquetes` o `/consultar?q=...` si vino de ahí) a
  `/paquetes?corregir=<id>` -- gana incluso sobre el origen `/consultar`, porque esa vista no tiene
  el modal Corregir y completar la asociación real importa más que volver ahí en este caso puntual.

## Verificación

- 2 tests nuevos: `test_recibir_declara_apartamento_sin_residente_redirige_a_corregir` (confirma
  el nuevo `Location`, sigue el redirect, confirma candidato real ofrecido y modal abierto) y
  `test_recibir_declara_apartamento_con_nuevo_residente_no_redirige_a_corregir` (guard: con
  `candidato_idx=nuevo` + nombre lleno, sigue yendo a `/paquetes` sin cambios).
- Suite completa.
- Verificado en local (`localhost:8010`) con un paquete real: anunciado sin unidad, recibido con
  Torre 2/Apto 302 sin residente -- confirmado el redirect a `?corregir=`. Datos de prueba
  limpiados.
- Pendiente: verificar en test.papyrus.com.co tras deploy. El paquete "ESTE ES UN CLIENTE
  FANTASMA" que quedó en la base local (dato de prueba del cliente, no tocado) ya se puede
  terminar de asociar entrando a su "Corregir destinatario" -- ahora sí ofrece candidatos reales.
