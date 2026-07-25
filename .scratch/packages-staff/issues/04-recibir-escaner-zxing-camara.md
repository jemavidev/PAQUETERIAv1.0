# 04 — Recibir con escáner ZXing (cámara)

**Spec:** `.scratch/packages-staff/spec.md` · **Glosario:** Guía, Recibir · **Brief:** §3 (ZXing multi-formato), §7

**What to build:** El operador **escanea el código de barras** del paquete con la **cámara del celular** al recibir; ZXing decodifica el mayor abanico de símbolos y **rellena la Guía** automáticamente. Si no hay cámara o niega el permiso, el modal **cae a entrada manual** sin bloquearse.

**Blocked by:** 01 — Lista de paquetes + Recibir (enhancement sobre el modal Recibir).

**Status:** ready-for-agent

- [ ] **ZXing** (`@zxing/browser` + `@zxing/library`) **vendorizado como asset estático** servido por la propia app (**sin CDN, sin proceso Node en runtime**; brief §3, ADR "liviano").
- [ ] En el modal **Recibir**, un botón **"Escanear"** abre la **cámara** (`getUserMedia`) y decodifica **multi-formato** (Code128/39, EAN-8/13, UPC-A/E, ITF, Codabar, QR, DataMatrix, PDF417, Aztec); el valor decodificado **rellena el campo `guide_number`**.
- [ ] **Degrada con gracia:** sin cámara / permiso denegado → el campo sigue **editable manualmente** (nunca bloquea); la cámara se **libera** al cerrar el modal.
- [ ] La **Guía sigue siendo opcional** y de referencia; el emparejamiento **no cambia** (por nombre/teléfono, no se promueve la guía a llave).
- [ ] Cobertura automatizable: el **asset ZXing se sirve** (`GET /static/...` → 200) y el modal Recibir **incluye el disparador de escaneo**. La **ruta de cámara** se verifica **manual/e2e** (no hay cámara en CI).
