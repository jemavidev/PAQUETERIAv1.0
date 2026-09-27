# Spec — Posición de almacenamiento al Recibir

Status: done -- tickets 01-03 desplegados en test (`f17c396`) y verificados por Jesús 2026-09-27

Origen: sesión de `grilling` del 2026-09-26 (pedido del cliente sobre el modal Recibir de /paquetes).

## Problem Statement

Cuando el personal de Papyrus va a entregar un paquete, no sabe en qué parte del estante lo dejó quien lo
recibió. Tiene que buscarlo a ojo entre todos los paquetes almacenados, lo que hace la entrega lenta y
propensa a errores, sobre todo cuando un residente tiene varios paquetes o cuando quien entrega no es quien
recibió.

## Solution

Al **Recibir** un Paquete, el Operador elige obligatoriamente la **Posición** del estante donde lo guarda,
tocando uno de 14 botones que reproducen el estante físico (7 filas × 2 lados, etiquetados 11…72). La
Posición queda registrada en el Paquete y el staff la ve al buscarlo en /paquetes y al entregarlo, así que
va directo al compartimento correcto. El residente nunca la ve.

## User Stories

1. As an Operador, I want to pick the storage Posición of a package when I receive it, so that whoever delivers it later knows where to find it.
2. As an Operador, I want the Posición picker to look like the physical shelf (fila 7 arriba, fila 1 abajo; lado izquierdo = x2, lado derecho = x1), so that I can pick the right compartment without translating labels.
3. As an Operador, I want the Posición buttons labeled exactly like the stickers on the shelf (11, 12, 21, 22 … 71, 72), so that screen and shelf match one-to-one.
4. As an Operador, I want to select a Posición with a single tap, so that choosing it adds as little friction as possible to each reception.
5. As an Operador, I want tapping a different Posición to replace my previous selection, so that I can fix a slip before confirming.
6. As an Operador, I want the selected Posición to be clearly highlighted, so that I can confirm at a glance what I chose.
7. As an Operador, I want tapping a Posición to NOT receive the package by itself, so that reception is always confirmed deliberately with the Recibir button.
8. As an Operador, I want the Posición picker placed at the end of the Recibir modal, right before the Recibir button, so that it is the last thing I decide after physically shelving the package.
9. As an Operador, I want the modal to stop me with a message next to the picker if I press Recibir without a Posición, so that no package is received without a location.
10. As an Operador, I want the server to reject a reception without a valid Posición even if the browser check is bypassed, so that no package ends up received without location.
11. As an Operador, I want a rejected reception (missing or invalid Posición) to have no side effects — no unit declared, no Ocupante created, no messenger payment recorded — and to reopen the same Recibir modal with the message inside, so that I can just pick a Posición and retry.
12. As an Operador, I want the Posición to be required whether I receive from /paquetes, from /announce (anunciar y recibir) or from /consultar, so that there is no back door to receive without location.
13. As an Operador using "Lector" mode, I want the scanner flow to keep working as today (focus on the guía; the scan only fills the guía), so that adding the Posición does not break scanning.
14. As an Operador, I want to see a "📍 41" label on each Recibido package in the /paquetes list, on both the mobile card and the desktop row, so that I can find where every package of a resident is without opening anything.
15. As an Operador, I want the Posición shown prominently in the Entregar modal, so that I can confirm I am holding the right package before handing it over.
16. As an Operador, I want packages without a Posición (received before this feature, or imported from v1) to show "Sin ubicación" in the Entregar modal and no label in the list, so that the absence is explicit and not confused with an error.
17. As an Operador, I want Entregado and Cancelado packages to not show the Posición label in the list, so that the list only points me to packages that are physically on the shelf.
18. As an Admin, I want the Posición to stay stored on the Paquete after it is delivered, so that there is a record of where it was kept.
19. As a residente, I never see the Posición (not in /mis-paquetes, not in public /consultar, not in any SMS/email/WhatsApp notification), because it is internal operational data of the papelería Papyrus.
20. As the system, I want the database to accept only the 14 valid Posición codes (or NULL), so that no invalid location can be stored by any path.
21. As the v1 mirror importer, I keep importing Recibido packages without Posición, so that the mirror keeps working unchanged.

## Implementation Decisions

- **Domain term "Posición"** (added to `CONTEXT.md`): a compartment of the single physical shelf of the papelería Papyrus, holding many packages. Code of two digits **fila + lado**: fila 1 (abajo) … 7 (arriba); lado **1 = derecha**, **2 = izquierda**. Valid set: 11, 12, 21, 22, 31, 32, 41, 42, 51, 52, 61, 62, 71, 72. Avoided term: "ubicación" as a domain noun (it is only UI copy for the "Sin ubicación" state), and the v1 `posicion`/"baroti" (an auto-generated number, unrelated).
- **Fixed in code**: one domain module owns the constant set of valid Posiciones, the validation, and the display layout (rows top-to-bottom 7→1, each row `[x2, x1]`). No admin configuration. Adding a row or a shelf later is a code change.
- **No occupancy control**, no per-Posición counts, no free/occupied state.
- **Schema**: new nullable column on Paquete for the Posición (small integer or short string), with a DB `CHECK` restricting it to the 14 codes or NULL. NULL means "Sin ubicación" (every pre-existing package and every v1-imported package). Alembic migration on the single-root tree (ADR-0002); no backfill.
- **Domain `receive()`** gains a `posicion` argument. It validates the value against the fixed set before mutating anything (same pattern as the guía: invalid → a dedicated domain exception, package untouched) and persists it. Kept optional at the domain signature so the many existing callers/tests and the importer are not forced to pass it; **the obligation is enforced at the web boundary** (below). A domain `receive()` without Posición leaves it NULL.
- **Endpoint `POST /paquetes/{id}/recibir`** accepts a `posicion` form field and rejects missing or invalid values **early, before any side effect** (declaring the unit, resolving/creating an Ocupante, messenger payment), exactly like the existing too-long-guía check. On rejection it re-renders the originating view with the Recibir modal of that package reopened and the message next to the picker — for /paquetes and for /consultar (`origen="consultar"`), mirroring the guía error path. /announce's "anunciar y recibir" uses this same endpoint, so it inherits the rule.
- **Recibir modal UI** (shared macro, so it applies to /paquetes, /announce and /consultar at once): a group of 14 buttons at the end of the modal, immediately before the submit button, laid out as a 2-column × 7-row grid mirroring the shelf (72|71 on top … 12|11 at the bottom). Implemented as a required radio group (real radios, visually as tappable buttons — same idea as the existing chip groups), so a tap only selects, the browser blocks a submit without selection, and the selection is visually highlighted. Thumb-sized targets (mobile-first). Only the code is shown on each button; no counts.
- **Lector mode unchanged**: focus still goes to the guía; the scanner never selects a Posición or submits.
- **Staff display**: /paquetes list shows a "📍 NN" badge only for packages in `Recibido` that have a Posición (mobile card and desktop row). The Entregar modal shows the Posición prominently at the top, or "Sin ubicación" when NULL. No filter by Posición.
- **Not shown to residents**: the Posición is not exposed in /mis-paquetes, public /consultar (obfuscated view), or any notification template/variable.
- **Not shown in the timeline**: the package timeline is shared with the resident's /mis-paquetes; per the client's decision the Posición does not appear in the timeline at all (staff or resident).
- **Retention**: the Posición is kept after Entregado/Cancelado; it is simply not displayed anywhere once the package leaves Recibido.
- **No editing**: there is no "cambiar ubicación" action, and the existing Corregir flows do not touch the Posición. A mis-tap at reception cannot be corrected from the app (accepted consequence).

## Testing Decisions

- Good tests assert externally observable behavior — the resulting Paquete state, the HTTP response and rendered HTML — never template internals or helper functions.
- **Seam 1 — domain `receive()`** (data_model, integration against Postgres; prior art: `tests/data_model/test_recibir_paquete.py`, "Seam A"): receiving with a valid Posición persists it; an invalid code raises and leaves the package intact (still Anunciado, no Posición); receiving without Posición leaves it NULL; the Posición survives a later `deliver()`; the DB `CHECK` rejects an out-of-set value written directly.
- **Seam 2 — web endpoint + rendered pages** (tests/web with the app's test client; prior art: `tests/web/test_packages.py`, `tests/web/test_captura_guia.py` for the reject-early-and-reopen-modal pattern, `tests/web/test_search.py` for `origen=consultar`, `tests/web/test_announce_new.py`): POST without/with invalid Posición → 400, modal reopened with the message, and **no side effects** (no unit declared, no Ocupante created, no payment recorded); POST with a valid Posición → Recibido with that Posición; the Recibir modal renders the 14 options in the shelf order (72,71 … 12,11) as a required group before the submit button in all three views; /paquetes shows "📍 NN" for Recibido only (not for Entregado/Anunciado, not when NULL); the Entregar modal shows the Posición or "Sin ubicación"; /mis-paquetes, public /consultar and the timeline fragment never contain the Posición (prior art: `tests/web/test_mis_paquetes.py`, `tests/web/test_consultar_ofuscado.py`).
- Existing tests that post to the recibir endpoint must be updated to send a valid Posición; domain-level callers of `receive()` do not need changes.
- Browser tests (`tests/browser/test_recibir_guia.py` as prior art) only if the tap-to-select / required behavior needs a real browser check; the required radio group is covered by rendered-HTML assertions otherwise.

## Out of Scope

- Changing a package's Posición after reception ("cambiar ubicación"), or correcting it via Corregir.
- Occupancy control, per-Posición counts, free/occupied indicators.
- Filtering or searching /paquetes by Posición.
- Admin configuration of shelves/rows/sides; more than one shelf.
- Backfilling Posición for already-Recibido or v1-imported packages; changes to the v1 mirror importer.
- Showing the Posición to residents, in notifications, or in the timeline.
- Reports/statistics by Posición.

## Further Notes

- The shelf orientation was confirmed explicitly twice during grilling: **11 derecha, 12 izquierda**, fila 1 abajo.
- `.scratch/` and the repo are public on GitHub — the spec contains no PII.
- Tailwind: new classes in templates require rebuilding `tailwind.css` and committing it (the deploy repo's Dockerfile does not build CSS).
