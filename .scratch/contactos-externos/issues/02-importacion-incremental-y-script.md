# 02 — Importación incremental + script

**What to build:** `importar_contactos_externos(session, filas_nuevas)` que aplica la fusión sobre un
lote nuevo y lo cruza contra los `ContactoExterno` ya existentes (crea, enriquece sin sobreescribir
nombre, o reporta el caso ambiguo de conectar dos contactos ya persistidos), más el script que lee
`docs/contacts.csv` y un export de la tabla `customers` de producción y llama a esa función.

**Blocked by:** 01 — Núcleo: esquema + fusión pura.

**Status:** ready-for-agent

- [ ] Primera importación crea los `ContactoExterno` esperados con sus teléfonos y fuente(s)
- [ ] Reimportar exactamente el mismo lote no duplica ningún contacto
- [ ] Un lote nuevo con un teléfono que ya existe enriquece ese contacto (nuevo teléfono/fuente) sin
      sobreescribir su `nombre` ya guardado
- [ ] Un lote que conecta (por teléfono compartido) dos `ContactoExterno` ya existentes y distintos
      NO los fusiona automáticamente, y queda reportado en el resumen devuelto
- [ ] El script lee `docs/contacts.csv` + un export local de `customers` de producción y produce el
      mismo resultado que llamar a la función directamente
