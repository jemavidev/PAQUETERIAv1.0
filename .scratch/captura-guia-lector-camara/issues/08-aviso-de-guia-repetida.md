# 08 — Aviso de guía repetida al recibir

**What to build:** hoy Recibir acepta una guía que ya tiene otro paquete sin decir nada, y el Operador no puede distinguir una lectura repetida por error de un envío legítimo de varias cajas con la misma guía. Con este ticket, al leer o escribir en el campo una guía que ya existe en otros paquetes, el modal muestra un aviso que **no bloquea**: "Ya hay N paquete(s) con esta guía", con los estados de esos otros paquetes. Lo alimenta un servicio de consulta solo para Staff que devuelve cantidad y estados, nunca datos de nadie. La política no cambia: la Guía sigue siendo una referencia, sin unicidad; dos paquetes con la misma guía se pueden recibir.

**Spec:** `.scratch/captura-guia-lector-camara/spec.md` (historias 42 a 49).

**Blocked by:** 02 — Prueba en navegador real para el modal Recibir.

**Status:** done

- [x] Servicio de consulta: dada una guía, devuelve cuántos paquetes la tienen y en qué estado está cada uno, considerando todos los estados (incluido `Cancelado`). No devuelve nombres, teléfonos, códigos de acceso ni ningún dato que permita ver esos paquetes.
- [x] Solo Staff: una petición sin sesión de Staff se rechaza igual que las demás rutas de Staff.
- [x] La comparación normaliza la guía como al guardarla (mayúsculas, espacios colapsados, recortada): "abc  123" y "ABC 123" cuentan como la misma.
- [x] Puede recibir el paquete actual para no contarlo: recibir un paquete no se advierte a sí mismo.
- [x] Una guía vacía no consulta ni avisa; cantidad cero no muestra ningún aviso.
- [x] En el modal Recibir, al terminar de leer o escribir (con una pausa breve, sin consultar en cada tecla), aparece junto al campo "Ya hay N paquete(s) con esta guía" con los estados; el aviso desaparece si la guía cambia a una que no existe.
- [x] El aviso nunca deshabilita ni retrasa el botón "Recibir": con una guía repetida, recibir funciona y el Paquete queda `Recibido` con esa guía (verificado por HTTP con dos paquetes de la misma guía, ambos `Recibido`).
- [x] Vale en /paquetes, /announce y el Recibir de /consultar por el mismo componente; prueba en navegador real en /paquetes con una guía sembrada en la BD y con el escaneo de la cámara simulada como segundo camino.

## Verificación

- Vistas fallar primero: 6 de las 7 pruebas nuevas de HTTP (el servicio no existía) y 4 de las 5 de navegador
  real. La que ya pasaba en cada grupo fija lo que no debe cambiar: dos paquetes con la misma guía se pueden
  recibir, y una guía que no existe no muestra aviso. Ahora pasan las 15 de `tests/web/test_captura_guia.py`
  y las 5 de `tests/browser/test_guia_repetida.py` (44 en el seam completo).
- Servicio (`GET /paquetes/guia-repetida`, solo Staff): devuelve `{"cantidad": N, "por_estado": {...}}` contando
  TODOS los estados (la prueba usa Recibido, Entregado y Cancelado). Sin sesión responde 303 a `/ingresar`, como
  el resto de rutas de Staff. La respuesta no trae nombres, teléfonos ni códigos de acceso (la prueba lo
  comprueba contra los tres paquetes sembrados).
- Normalización como al guardar: "  abc 123  " encuentra la guía guardada como "ABC 123" (mayúsculas, espacios
  colapsados, recortada). `excluir` deja fuera al paquete indicado; un id inválido se ignora. Guía vacía, en
  blanco o de más de 50 caracteres devuelve cantidad 0 sin error.
- En el modal Recibir (navegador real): al escribir una guía que ya existe aparece "Ya hay 1 paquete con esta guía
  (1 recibido)." con una pausa de 300 ms; desaparece si la guía cambia a una que no existe o se deja vacía; una
  lectura de la cámara simulada también lo dispara al instante; y NUNCA bloquea: el botón sigue habilitado y
  "Recibir" deja el paquete `Recibido` con la misma guía que el otro.
- Política sin cambios: la Guía sigue sin unicidad (glosario: es una referencia, no una llave). Dos paquetes con la
  misma guía se reciben (HTTP: ambos `Recibido` con `MISMA-1`).
- Vale en /paquetes, /announce y el Recibir de /consultar por reusar el mismo componente (la prueba de navegador
  corre en /paquetes; el bloque de captura es idéntico en las cuatro páginas, ver ticket 03).
- Regresión: `tests/data_model` completo (830), los 44 de navegador, y las dos tandas web (`test_captura_guia`,
  `test_packages`, `test_search`, `test_announce_new`, `test_customers_manage`, `test_layout`,
  `test_cache_headers`), todo en verde.
- Decisión menor: la ruta es un GET de un solo segmento (`/paquetes/guia-repetida`), como el precedente de
  `/paquetes/promover-candidatos`, para no chocar con las rutas `/paquetes/{id}/...`. `paquete_service` importa
  `normalizar_guia` de `paquete_lifecycle` (sin ciclo: el ciclo de vida no importa al servicio).
