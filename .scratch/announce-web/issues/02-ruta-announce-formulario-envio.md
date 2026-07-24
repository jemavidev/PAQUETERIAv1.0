# 02 — Ruta `/announce` (formulario + envío)

**Spec:** `.scratch/announce-web/spec.md` · **Glosario:** Anuncio, Anunciante, Destinatario, Nombre sin teléfono

**What to build:** Un residente **anuncia un paquete desde `/announce`**: abre un formulario (nombre, teléfono, T&C, a nombre de quién), envía, y el sistema registra/reutiliza su Persona, crea el Paquete en `ANUNCIADO` con su snapshot congelado, y muestra una **confirmación** con el número de seguimiento / código de acceso. Mobile-first, **sin** número de guía.

**Blocked by:** 01 — Capa web clean-room + arnés HTTP.

**Status:** ready-for-agent

- [ ] `GET /announce` → 200: formulario con **nombre**, **teléfono**, checkbox **T&C**, y selector **"a nombre de quién"** (yo mismo / otra persona registrada [pide teléfono] / solo un nombre [pide nombre]). **Sin** campo de número de guía.
- [ ] `POST /announce` válido → mapea la selección a un `Destinatario`, llama a `announce(session, …)`, hace commit, crea el Paquete `ANUNCIADO`; la respuesta de **confirmación** muestra `tracking_number` / `access_code`.
- [ ] Los **3 casos** de "a nombre de": **yo mismo**; **persona registrada** (por su teléfono); **solo un nombre** (queda bajo el tel del anunciante, sin crear Persona sin llave).
- [ ] **Validación**: sin nombre / sin teléfono / sin T&C → re-render con mensaje, **cero** Paquetes creados. `persona_registrada` de un teléfono no registrado → mensaje claro ("usa 'solo un nombre'"), sin Paquete.
- [ ] El "a nombre de" **casual no agrupa**: no toca el `apartamento_actual` de nadie (ya garantizado por el dominio; el test lo verifica).
- [ ] El JS del submit **re-habilita el botón con `finally`** pase lo que pase (bug a no heredar, `PACKAGES_DIAGNOSIS.md`).
- [ ] Tests HTTP (`TestClient`): `GET` renderiza el form (con los campos, **sin** guía); `POST` de cada uno de los 3 casos crea el Paquete correcto (verificado en BD); las validaciones no crean nada.
