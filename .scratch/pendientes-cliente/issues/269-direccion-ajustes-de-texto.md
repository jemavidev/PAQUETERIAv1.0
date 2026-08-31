# 269 — `/residentes` tab Dirección: 5 ajustes de texto

**Pedido original (cliente):**
1. Remueve "Solo el personal de Papyrus puede asignar o cambiar esto -- el residente lo ve de solo lectura en 'Mis datos'."
2. Remueve "⚠️ Este residente está registrado como Residente de su apartamento actual -- para reasignarlo desde acá, primero dalo de baja como Residente en la tab 'Residentes'."
3. Remueve "⚠️ Este residente es el Residente principal de su apartamento actual, que tiene otros Residentes activos -- para reasignarlo desde acá, primero convierte a otro en principal o dales de baja a todos en la tab 'Residentes'."
4. Cambia "Si ya es Ocupante (no principal) de otra unidad, moverlo acá" por "Mudar residente de apartamento" -- y si existe algún modal de esto, actualizarlo con el mismo enfoque.
5. Cambia "Libre -- sin residentes registrados" por "Apartamento vacío."

**Status:** implementado

## Alcance

1. `customers_manage/detail.html` -- se borra el `<p>` descriptivo bajo
   el título "Dirección".
2/3. Los 2 mensajes de `_aviso_reasignacion_bloqueada` (issue 69,
   `customers_manage.py`) son las ÚNICAS 2 ramas que esa función puede
   devolver -- al removerse ambas, se borra la función entera (y su
   único call site en `_contexto_detalle`, y el bloque `{% if
   aviso_reasignacion_bloqueada %}` del template) en vez de dejarla
   viva devolviendo siempre texto vacío. Efecto real: el staff ya no ve
   el aviso preventivo explicando por qué el picker va a rechazar el
   guardado -- se entera recién al intentarlo (el guard real sigue
   intacto en `reasignar_apartamento`, esto solo quita el aviso
   anticipado).
4. `customers_manage/detail.html` -- cambia el `<label>` del checkbox
   `mover_de_otra_unidad` (el `name` del campo NO cambia, solo el texto
   visible -- ningún test ni la ruta dependen del texto). Revisado: no
   existe ningún modal asociado a ESTE checkbox puntual (el picker
   compartido no trae modal propio) -- los textos "Mudar residente a X"
   que sí existen en otros lados (`_recibir_paquete.html`,
   `packages/_resultados.html`, la sección "Agregar Residente" de esta
   misma ficha) pertenecen a un flujo DISTINTO (resolver conflicto al
   agregar un contacto que ya es Ocupante de otra unidad) -- no se
   tocan, fuera de alcance de este pedido puntual sobre Dirección.
5. `components/_recibir_paquete.html` -- 2 ocurrencias del mismo texto
   (una con punto final, una sin) en el MISMO componente compartido,
   usado también por `/announce` y "Recibir" en `/paquetes` (modo
   `con_resumen=True` vs modo liviano) -- mismo criterio que issue 266
   (componente compartido, se cambian las 2 para consistencia en toda
   la app, no solo Dirección).

## Verificación

- Se encontraron y eliminaron 2 tests obsoletos que cubrían el
  feature de issue 69 recién removido (`test_tab_direccion_avisa_si_
  es_ocupante_activo`, `test_tab_direccion_sin_aviso_si_no_es_
  ocupante`) -- no tenía sentido dejarlos, aserteaban texto que ya no
  existe para nadie.
- Suite (`test_customers_manage.py` + `test_packages.py` +
  `test_announce_new.py`, las 3 vistas que tocan el componente
  compartido): 414 passed.
- Verificado en vivo (`/residentes/c75f7cdd-...?tab=direccion`): los 3
  textos removidos ya no aparecen, "Mudar residente de apartamento" y
  "Apartamento vacío." sí.
