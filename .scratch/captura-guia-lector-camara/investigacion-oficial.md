# Investigación oficial: captura de la guía en "Recibir paquete" con el lector integrado del Farset F7 y con la cámara de celulares

**Contexto:** el modal "Recibir paquete" de `/paquetes` tiene un input de texto `guide_number`
(varchar(50), opcional) y un botón "Escanear con cámara" que usa ZXing-JS
(`CODE/src/app/web/static/vendor/zxing.min.js`, 292 KB, `BrowserMultiFormatReader` sin hints,
`decodeFromVideoDevice(null, video, cb)`). El cliente captura la guía con dos tipos de dispositivo:
(A) celulares normales (Android y posiblemente iPhone, Chrome/Safari móvil) y (B) equipos "Farsat F7"
con lector de códigos integrado. Hechos ya verificados en el navegador contra el servidor dev (dados
por el encargo, no re-investigados aquí): un lector tipo teclado que agrega Enter dispara el submit y
RECIBE el paquete al instante; al abrir el modal el foco queda en el botón de la fila, no en el input
Guía; no hay WebSerial/WebHID/BarcodeDetector en el código; el cliente pidió quitar `autofocus` en
vistas de staff (issue 284). Esta investigación contrasta tres frentes contra fuentes primarias:
el equipo F7 (P1), la cámara en navegador móvil (P2) y las simbologías de las guías colombianas (P3).

**Nota de metodología:**

- **Fecha de acceso de todo lo citado: 2026-09-21.** Donde se cita código fuente de Chromium o WebKit
  es la rama `main` de ese día -- no está atada a una versión publicada de Chrome/Safari (el mapeo
  `main` -> versión estable no se verificó).
- **farset.net** (tienda Shopify del fabricante) no bloquea fetchers, pero `WebFetch` devolvió 404 en
  la URL vieja del F7 (`/product/f7-handheld-pda-with-keypad-android-11-14/`, que un buscador aún
  lista; sin copia en Wayback). Se obtuvo la ficha vigente con `curl` + User-Agent de navegador desde
  `/collections/mobile-computers` -> `/products/farset-f7-rugged-android-14-barcode-scanner-pda-with-keyboard`.
  Los botones "User Manual & Software" de esa ficha (English/Español/... y "Time Sync Tool v1.1")
  tienen `href="#"` -- están sin enlace hoy.
- **Amazon** (los dos enlaces del usuario: `a.co/d/0bL42Ycb` y `amazon.com/dp/B0FQBBHRNR`): `WebFetch`
  devolvió solo el esqueleto de la página; `curl` con User-Agent de navegador + `Accept-Language` sí
  devolvió el HTML completo (2.4 MB, sin captcha). El enlace corto `a.co` responde 404 a un `HEAD` pero
  con `GET` redirige al mismo ASIN B0FQBBHRNR. Del listado salieron dos PDFs bajo "Product guides and
  documents" (ver P1.4); uno tiene capa de texto (`pdftotext`) y el otro es solo imagen (se renderizó
  a PNG con `pdftoppm` y se leyó visualmente). **Todo lo que viene solo de Amazon se etiqueta
  [CONFIRMADO: anuncio del minorista]**, no como fuente del fabricante.
- **MDN y `developer.chrome.com`** se leyeron con `WebFetch` (que pasa la página por un modelo
  resumidor): las citas literales son las que devolvió la herramienta. Para los datos que cargan
  peso se contrastó con fuente cruda: JSON de compatibilidad de MDN (`browser-compat-data`) y código
  de Chromium/WebKit vía `raw.githubusercontent.com`, registro de npm y API pública de GitHub.
- **Bugzilla de WebKit** se leyó por su endpoint XML. No se usó `issues.chromium.org` (exige login).
- Ningún fetcher fue bloqueado por WAF salvo lo dicho de Amazon/`WebFetch`. Máximo 3 `curl` en paralelo.
- Todo archivo temporal (PDFs, bundles descargados) quedó en `/tmp`; no se tocó código del repo.

---

## Resumen ejecutivo

1. **El equipo es "Farset F7" (marca FARSET, no "Farsat"), de Shenzhen Farset Technology Co., Ltd.,
   marca hermana de YGF (Shenzhen Yige Technology Co., Ltd.), un fabricante ODM/OEM.** Es un handheld
   Android con teclado físico de 22 teclas, dos teclas de escaneo laterales, 4G, cámara trasera de
   13 MP con autofoco y motor de lectura Honeywell N6603 (variante "F7") o SE6100 "Zebra-licensed"
   (variante "F7-WiFi"). [CONFIRMADO: sitio del fabricante farset.net / ygf-tech.com].
2. **Hallazgo central de P1:** el listado de la tienda Farset en Amazon publica (como "User Guide (PDF)")
   la definición de la interfaz del servicio de escaneo (el PDF no lleva marca ni nombra el modelo).
   Según ese documento, **el modo de envío
   por defecto es `BROADCAST` (no teclado), el terminador por defecto es `NONE` y prefijo/sufijo por
   defecto están vacíos.** Los modos disponibles son `FOCUS`, `FOCUS_OVERWRITE`, `BROADCAST` y
   `CLIPBOARD`; el terminador puede ser `ENTER`, `TAB`, `SPACE` o `NONE`. El FAQ del fabricante dice
   que si "el escaneo no funciona" hay que poner el "send mode" en "Focus+Broadcast".
   [CONFIRMADO: documentos del fabricante]. Lectura razonable: de fábrica, una lectura no llega al
   campo Guía de una página web hasta que alguien cambie ese ajuste. [INFERENCIA]
3. **Lo que ningún documento dice y solo el equipo físico responde:** si el modo `FOCUS` escribe de
   verdad en un `<input>` dentro de Chrome, cómo lo inyecta (¿eventos de teclado?, ¿accesibilidad?),
   si el gatillo físico funciona con un formulario web, y si el equipo trae Chrome/Google Play.
   [NO VERIFICABLE SIN EL EQUIPO FÍSICO]
4. **`BarcodeDetector`:** en Chrome Android existe desde la versión 83 pero, según el código de
   Chromium, solo si hay Google Play Services >= 19.7.42 (si no, queda deshabilitado). En Safari/iOS
   está apagado por defecto en WebKit (preferencia `ShapeDetection`: `testable`, `defaultValue: false`);
   Firefox no lo tiene. [CONFIRMADO: MDN/BCD, código Chromium y WebKit]
5. **Cámara con ZXing tal como está:** sin restricciones, Chrome entrega vídeo a 640x480 a 30 fps
   (comentario del propio código de Chromium) -- una entrada pobre para códigos 1D. El bundle
   vendorizado es **byte a byte `@zxing/library@0.19.1`** (enero de 2022), que **no** puede leer
   Codabar ni Code 93, y cuyo bucle de reintento tras un fallo espera 0 ms (los 500 ms solo aplican
   después de una lectura exitosa). [CONFIRMADO: hash SHA-256 y código fuente v0.19.1]
6. **`@zxing/library` está oficialmente "en modo mantenimiento"** (README), pero publicó 0.22.0 y 0.23.0
   en abril de 2026 tras casi dos años sin releases, con mejoras de lectura 1D. Alternativas activas:
   `zxing-wasm` / `barcode-detector` (Sec-ant, sobre ZXing-C++, ~1 MiB de wasm). [CONFIRMADO]
7. **P3: ninguna transportadora ni Mercado Libre publica la simbología del código de barras de la
   guía.** Lo único que hay de fuente primaria son longitudes/formatos del número: Coordinadora, 11
   dígitos; 4-72 (correo certificado), 13 caracteres con letras (`ET123456789CO`). Una muestra de rótulo
   publicada por Coordinadora contiene un QR de 32 dígitos y ningún código 1D detectable. Todo lo demás
   es de confianza baja. [CONFIRMADO parcial / NO ENCONTRADO]

---

## 0. Precisiones sobre lo que ya hace el código actual (verificadas contra la fuente)

**Versión vendorizada.** `sha256(zxing.min.js) = c5837e4858a3775173bab09ee36e6052545c7880c9d7452e2f464770c6e642ce`,
idéntico al de `https://cdn.jsdelivr.net/npm/@zxing/library@0.19.1/umd/index.min.js` (292,379 bytes);
el commit `be5bcd6` también dice "Bundle @zxing/library 0.19.1". Las versiones vecinas tienen otro hash
(0.19.2: 292,343 B; 0.20.0: 336,049 B; 0.21.3: 336,008 B; 0.22.0: 352,462 B; 0.23.0: 362,150 B).
0.19.1 se publicó el 2022-01-10 (registro npm). [CONFIRMADO: comparación de hash; registro npm,
https://registry.npmjs.org/@zxing/library]

**Lectores 1D por defecto en 0.19.1.** Fuente: `src/core/oned/MultiFormatOneDReader.ts` en el tag
`v0.19.1` (https://raw.githubusercontent.com/zxing-js/library/v0.19.1/src/core/oned/MultiFormatOneDReader.ts).
Sin hints la lista es UPC/EAN (dos veces), Code 39, Code 128, ITF y RSS-14. **Codabar y Code 93 están
comentados** (`// this.readers.push(new CodaBarReader())`, `// ... Code93Reader`), tanto en la lista por
defecto como en la rama de `POSSIBLE_FORMATS`: en 0.19.1 esos dos formatos no se pueden leer ni pidiéndolos.
En `v0.23.0` la rama `POSSIBLE_FORMATS` ya conecta Code 93 y Codabar y la lista por defecto incluye
Code 93 (Codabar sigue comentado en la lista por defecto). [CONFIRMADO: código fuente]

**Cadencia del bucle.** Fuente: `src/browser/BrowserCodeReader.ts` v0.19.1, `decodeContinuously`.
Tras una lectura exitosa espera `timeBetweenScansMillis` (por defecto 500 ms) y sigue; tras un fallo
(`NotFoundException`, checksum o formato) reprograma con `_timeBetweenDecodingAttempts`, cuyo valor por
defecto es **0 ms**. Es decir, mientras no hay código a la vista el bucle intenta decodificar tan rápido
como el navegador lo permita; existe el setter `timeBetweenDecodingAttempts` para espaciarlo.
[CONFIRMADO: código fuente]. El efecto real en batería/CPU del equipo no se midió.

**Restricciones que ya pide.** `decodeFromVideoDevice(null, ...)` arma `{ video: { facingMode: 'environment' } }`
sin ancho/alto/enfoque; existe `decodeFromConstraints(constraints, video, cb)` en la misma versión si
se quiere pasar otras restricciones. El elemento `<video>` recibe `autoplay`, `muted` y `playsinline`.
[CONFIRMADO: código fuente v0.19.1]

---

## 1. P1 -- Farset F7

### 1.1 Qué es exactamente

- **Marca y fabricante.** La marca es **FARSET** ("Farsat" es la grafía del cliente; se buscaron ambas y
  solo "Farset" existe). Pie del sitio: "(c) 2026, Shenzhen Farset Technology Co., Ltd."; "About us":
  "founded in 2014, is a professional manufacturer specializing in rugged Android handheld PDAs, RFID
  terminals, barcode scanning devices, and industrial tablets ... flexible ODM and OEM services".
  https://www.farset.net/pages/about-us [CONFIRMADO: sitio del fabricante]
- **Relación con YGF.** `https://www.ygf-tech.com/about-ygf/`: "Shenzhen Yige Technology Co., Ltd., founded
  in 2014 ... Operating under the YGF brand ... the company also offers selected product lines under the
  FARSET brand". Ambos sitios comparten el correo de contacto `marketing@ygf-tech.com`, y YGF tiene su
  propia ficha del F7 (`https://www.ygf-tech.com/product/f7-handheld-pda-with-keypad-android-11-14/`,
  "F7 Handheld Computer"). [CONFIRMADO: sitio del fabricante] Es decir, el F7 lo fabrica la propia empresa
  detrás de FARSET/YGF; no es un rebrand de Chainway/Urovo/Newland/etc. según lo publicado. YGF además
  ofrece a terceros "Barcode scanning engine selection & integration", "Android OS customization",
  "Firmware flashing & application pre-installation" (https://www.ygf-tech.com/support/), o sea que el
  software del escáner es personalización del propio fabricante. [CONFIRMADO]
- **Rastro de un OEM de software.** El documento del servicio de escaneo (1.4) usa nombres de paquete
  `com.eastaeon.*` (p. ej. `com.eastaeon.scan_service_control_action`). No se encontró ninguna página
  que identifique a "Eastaeon" ni que use esos nombres fuera de ese documento (búsquedas de
  `"com.eastaeon"`, `"com.android.scanner.service_settings"`, `"Focus+Broadcast"`: sin resultados
  relevantes). Sospecha razonable de que el servicio de escaneo viene de un tercero, pero **no hay
  evidencia de quién ni de que sea el fabricante del hardware.** [INFERENCIA]
- **FCC ID:** se buscó "Shenzhen Yige Technology"/"Farset" + FCC ID; no apareció ninguno. [NO ENCONTRADO]

### 1.2 Variantes y especificaciones publicadas

| Dato | F7 (farset.net) | F7-WiFi (farset.net) | YGF F7 (ygf-tech.com) |
|---|---|---|---|
| SO | Android 14.0 | Android 14.0 | "Android 9.0 with GMS" en la tabla; el encabezado dice "Android 9 / Android 14" |
| Motor | "Honey-Well N6603" | "SE6100-2D, Zebra License" | SE6100-2D estándar; opcionales Honeywell 6603/6703, Zebra 4710/4770 (y HS7/4100 en el encabezado) |
| NFC / WAN | NFC; 2G/3G/4G | sin NFC ("Not supported"); solo WiFi | NFC; 4G |
| Memoria | 3 GB + 32 GB | 3 GB + 64 GB | 4 GB + 64 GB (Android 9) |
| Cámara | trasera 13 MP autofoco + LED | ídem | ídem ("13MP, AF, with flash LED") |
| Teclas | -- | -- | "22 physical keyboard keys on the front, 1 power key, 2 scan keys on the side" |

Fuentes: https://www.farset.net/products/farset-f7-rugged-android-14-barcode-scanner-pda-with-keyboard ,
https://www.farset.net/products/farset-f7-wifi-rugged-android-14-barcode-scanner-pda-with-keyboard ,
https://www.ygf-tech.com/product/f7-handheld-pda-with-keypad-android-11-14/ .
[CONFIRMADO: sitio del fabricante]. Además: "Development Tool: Android SDK; Supported language: Java" (YGF).

**Listado de Amazon del usuario (ASIN B0FQBBHRNR).** Título actual: "Farset F7-Pro 1D 2D Android Barcode
Scanner Handheld Mobile Computer PDA ... HoneyWell-N6603 1D/2D/QR Scan Engine NFC, 5000mAh Removable
Battery, IP67 Rugged, 2026". Bullets: "The FARSET F7-Pro runs Android 14 with GMS certification, powered by
an octa-core processor, 3GB of RAM, and 32GB of storage"; "professional HoneyWell-N6603 scan engine ...
reads 1D/2D/QR barcodes, including damaged, faded, and screen-based codes, with a scanning distance up
to 50 cm"; "22 physical keys"; "4G LTE, dual-band Wi-Fi, Bluetooth 5.0, NFC". Tabla A+: CPU "MediaTek
MT8768 Octa-Core 2.0GHz"; comparativa donde "F7 Android 14 PDA Scanner" = Honeywell N6603 con NFC y
4G/WiFi y "F7-WiFi" = SE6100 sin NFC. Tienda: "Visit the Farset Store". [CONFIRMADO: anuncio del minorista]

**Ojo con el nombre exacto.** El mismo producto aparece como "F7" (farset.net, primer título del
ASIN en el buscador), "F7-Pro" (título actual en Amazon) y el manual en PDF tiene como título interno
"F7T 英文说明书 1022". No se pudo establecer si son el mismo equipo con nombres distintos o revisiones;
el usuario debe confirmar la etiqueta trasera del equipo. [NO VERIFICABLE SIN EL EQUIPO FÍSICO]

### 1.3 Motor de escaneo (ficha del fabricante del motor)

Honeywell N660X Series (N6603 = versión con puntero láser rojo): "proprietary CMOS sensor with global
shutter and 844 x 640 pixel resolution; 60 frames per second max"; iluminación LED blanca; "AIMING:
visible green LED (N6600) or red laser aimer (N6603)"; "Enhanced reading ... barcodes ... displayed on
mobile phone screens"; simbologías lineales incluidas: UPC/EAN/JAN, GS1 DataBar, **Code 39, Code 128**,
Code 32, **Code 93, Codabar/NW7, Interleaved 2 of 5**, Code 2 of 5, Matrix 2 of 5, MSI, Telepen, Trioptic,
China Post; 2D: PDF417, MicroPDF417, GS1 Composite, Aztec, Data Matrix, **QR**, Micro QR, MaxiCode, Han
Xin; alcances típicos p. ej. "C39 5mil 64-163 mm; UPC-A 13mil 46-419 mm" (rango estándar).
Fuente: datasheet Honeywell 007610-3-EN (04/21),
https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/siot/en-us/products/barcode-scan-engines-modules-and-decoding-software/2d-barcode-scan-engines/n660x-series-2d-scan-engines/documents/sps-siot-oem-2d-imagers-n660x-series-datasheet-007610-ciid-178662.pdf
[CONFIRMADO: fabricante del motor]. Es un **imager de área** (no un láser de barrido); "láser" es solo el
puntero. Que el F7 exponga todas esas simbologías depende de la configuración del servicio de escaneo
(1.4). La tabla de YGF dice "Optical resolution 1280*800" y "Scan precision >=3mil", cifras que no
coinciden con el N6603 (844x640): el bloque de YGF parece genérico de la familia, no por motor.
[INFERENCIA]. La variante F7-WiFi usa un SE6100 "independently developed under Zebra's authorization"
según la guía de compra de farset.net (https://www.farset.net/pages/barcode-scanner-buying-guide);
no se consultó ninguna ficha de ese motor. [CONFIRMADO solo como afirmación del fabricante del equipo]

### 1.4 Cómo entrega la lectura a una aplicación (lo que más importa)

**Fuente A -- FAQ del fabricante** (https://www.farset.net/pages/faq, sección "Products and Technology"):

> The scanning function is not working. -- Simply open the scan tool app, click scan settings, locate
> the send mode setting - Focus+Broadcast, and the device is ready to scan.

[CONFIRMADO: sitio del fabricante]. Confirma que existe una app "scan tool" con "scan settings" y un
ajuste "send mode" con al menos una opción llamada "Focus+Broadcast".

**Fuente B -- "User Guide (PDF)" del listado de Amazon**
(https://m.media-amazon.com/images/I/71ordJb-iUL.pdf, 6 páginas; título interno "扫描服务接口定义" =
"Scan service interface definition"; metadatos: creado el 2026-08-19). Está publicado en el listado de la
tienda Farset (el listado muestra "YGF Official Flagship Store" junto a los vídeos) bajo "Product guides and
documents"; **el PDF no lleva logo ni nombre de marca y no nombra el modelo F7**: se trata como documento del
fabricante por estar en su listado, y describe "the scanning service" en general (puede ser común a una familia
de equipos). El FAQ de la Fuente A confirma que existe un ajuste "send mode" en la app de escaneo del F7.
Contenido relevante, literal:

- Lista de ajustes del servicio: sonido, vibración, escaneo continuo, intervalo, autoarranque,
  **"Barcode terminator setting"**, **"Barcode sending method"**, "Broadcast settings for barcodes",
  "Barcode parameter settings", **"Barcode prefix setting"**, **"Barcode suffix setting"**, filtro de
  espacios al inicio/fin, habilitar/deshabilitar cabezal, filtro de caracteres invisibles, modo de luz
  continua y "Trigger scanning".
- **Método de envío** (extra `barcode_send_mode`, acción `com.android.scanner.service_settings`):
  `"FOCUS": Focus input`; `"FOCUS_OVERWRITE": Focus input, covering existing content`;
  `"BROADCAST": broadcast //Default value`; `"CLIPBOARD": clipboard`.
- **Terminador** (extra `endchar`): `"ENTER": carriage return`, `"TAB": TAB`, `"SPACE": space`,
  `"NONE": No ending symbol //Default value`.
- **Prefijo y sufijo** (extras `prefix`, `suffix`): "String type, default is null character".
- **Broadcast:** acción por defecto `com.android.server.scannerservice.broadcast`, clave `scannerdata`.
- Otros valores por defecto: `sound_play` true, `viberate` true, `scan_continue` false, `interval` 0,
  `boot_start` true, `filter_prefix_suffix_blank` false, `filter_invisible_chars` false, cabezal
  habilitado true.
- **Parámetros del motor:** acción `com.eastaeon.scan_service_control_action`, `command` =
  `"setScanningParameter"`, `param` (int), `value` (int); el único ejemplo es `param 8610, value 1`.
  **El documento no incluye la tabla que relaciona `param` con simbologías.**
- **Disparo por software:** acción `com.eastaeon.floatingbutton.KEY_DOWN`, `command` = `startScan` /
  `stopScan` / `startScanOneTimes` ("not supported in some older versions").
- Todo se controla enviando *broadcasts* de Android; nota: "Supports multiple settings in one broadcast".

[CONFIRMADO: documento publicado en el listado del fabricante, sin marca ni modelo en el PDF]. Consecuencias
directas:

- El servicio tiene el modo teclado que uno esperaría (`FOCUS`/`FOCUS_OVERWRITE` = "Focus input") y un
  terminador configurable con Enter/Tab, **pero el valor por defecto documentado es `BROADCAST` +
  `NONE`**. Una lectura por defecto va a un *broadcast* de Android que una página web en Chrome no
  puede recibir. [INFERENCIA: una página web no registra receptores de broadcast de Android; no hay
  fuente que lo diga para este equipo]
- Con terminador `NONE` (el defecto) no se agrega Enter, así que la lectura sola **no** enviaría el
  formulario; con `ENTER` sí, y entonces vale el hecho ya verificado (submit inmediato). [INFERENCIA]
- El FAQ llama "Focus+Broadcast" a lo que en el documento de la API no aparece como valor (la API lista
  `FOCUS`, `FOCUS_OVERWRITE`, `BROADCAST`, `CLIPBOARD`). Puede ser un nombre de interfaz para una
  combinación, o firmware distinto al del documento. [NO VERIFICABLE SIN EL EQUIPO FÍSICO]
- Un sitio web no puede enviar esos *broadcasts*; el ajuste se hace en la app del escáner del equipo
  (Ajustes -> "Scanning Tools" -> "Scanning Settings", ver Fuente C) o por otra vía de administración.
  Un `adb shell am broadcast -a com.android.scanner.service_settings --es barcode_send_mode FOCUS
  --es endchar NONE` sería la traducción directa del ejemplo Java del documento, pero **no se probó**
  y el documento no lo menciona. [INFERENCIA]

**Fuente C -- IFU (Instructions for Use) del listado de Amazon**
(https://m.media-amazon.com/images/I/D1tdDrGXVrL.pdf, 2 páginas de imagen con 13 páginas de manual; título
interno "F7T 英文说明书 1022", creado el 2025-10-22, marcado "Farset", con correo de contacto de YGF).
Página 7, "Bar code scanning": "You can scan the barcode through the terminal's built-in scanning program
or the scanning program developed by the customer. -- Common problem: The scanning head positioning
light/fill light is not on. Please confirm whether the scanning function is turned off. If it is turned
off, please enter Settings-Scanning Tools-Scanning Settings-Enable/Disable Code Scanning switch to turn it
off and on again." La página 4 menciona una tecla "SCAN scan key" en el teclado y el diagrama de la
página 3 rotula "Scan Button" y "Scanner". El manual **no** describe el modo de envío, terminadores ni
simbologías. [CONFIRMADO: documento del fabricante]

### 1.5 Respuestas a lo que pedía el encargo

| Pregunta | Respuesta | Etiqueta |
|---|---|---|
| SO | Android 14 (F7/F7-WiFi de farset.net); YGF además lista Android 9 (MT6762V) | CONFIRMADO: fabricante |
| Navegador (¿Chrome?) | Ningún documento del fabricante lo dice. Amazon dice "Android 14 with GMS certification"; el FAQ del fabricante dice que algunas unidades no acceden a Google Play y hay que flashear una "TeeKey" con "SN Writer" ("Unable to access or use the Google Play Store") | CONFIRMADO: minorista/fabricante para lo citado; presencia de Chrome NO VERIFICABLE |
| Motor | Honeywell N6603 (imager 2D 1D+2D) o SE6100 "Zebra-licensed" (F7-WiFi) | CONFIRMADO |
| Modo de salida | Servicio de escaneo con `FOCUS`, `FOCUS_OVERWRITE`, `BROADCAST` (defecto), `CLIPBOARD` | CONFIRMADO: doc. del fabricante |
| Sufijo/prefijo | Terminador `ENTER`/`TAB`/`SPACE`/`NONE` (defecto `NONE`); `prefix` y `suffix` texto libre (defecto vacío) | CONFIRMADO |
| Activar/desactivar simbologías | Existe el mecanismo (`setScanningParameter` con `param`/`value`) pero sin tabla de parámetros; el motor soporta las simbologías de 1.3 | CONFIRMADO parcial |
| Gatillo físico + formulario web en Chrome | No documentado | NO VERIFICABLE SIN EL EQUIPO FÍSICO |
| Que `FOCUS` escriba en un `<input>` de una página en Chrome | No documentado | NO VERIFICABLE SIN EL EQUIPO FÍSICO |
| Portapapeles / serie / HID | Portapapeles: sí (`CLIPBOARD`). Serie/HID: no aparecen en la documentación consultada | CONFIRMADO / NO ENCONTRADO |

### 1.6 Qué se buscó y no se encontró

- Manual de usuario descargable (los botones de farset.net no tienen enlace), manual de la app "scan tool"
  y tabla de `param` de `setScanningParameter`.
- Ficha en la FCC (`fccid.io`) de "Shenzhen Yige Technology"/"Farset".
- Documentación de terceros que describa `com.android.scanner.service_settings` o `com.eastaeon`.
- Qué pedirle al cliente: fotos de la etiqueta trasera (modelo exacto), capturas de "Settings -> Scanning
  Tools -> Scanning Settings" completas, versión de Android/parche, y si Chrome está instalado y su versión
  (`chrome://version`). Contacto de soporte del fabricante público: `marketing@ygf-tech.com`.

---

## 2. P2 -- Cámara en navegador móvil

### 2.a `BarcodeDetector` (Shape Detection API): estado real

**Datos de compatibilidad de MDN** (crudo,
https://raw.githubusercontent.com/mdn/browser-compat-data/main/api/BarcodeDetector.json ; estado:
`experimental: true, standard_track: true`; spec https://wicg.github.io/shape-detection-api/):

| Navegador | Dato BCD |
|---|---|
| Chrome Android | `version_added: 83`, sin `partial_implementation` |
| Chrome escritorio | 88 con `partial_implementation`: "Supported on ChromeOS and macOS only" (nota de macOS Ventura anterior a Chrome 113) |
| Edge / Opera escritorio | como Chrome escritorio (parcial, solo macOS) |
| Firefox | `version_added: false` (bug https://bugzil.la/1553738); Firefox Android = "mirror" (no) |
| Safari | 17 **solo con preferencia** ("Shape Detection API", `value_to_set: true`) |
| Safari iOS | "mirror" de Safari (o sea, tras la misma preferencia) |
| Samsung Internet / WebView / Opera Android | "mirror" de Chrome Android |

MDN (https://developer.mozilla.org/en-US/docs/Web/API/Barcode_Detection_API): "experimental technology",
"Limited availability ... not Baseline", disponible solo en contextos seguros (HTTPS), utilizable en Web
Workers. Formatos: `aztec, code_128, code_39, code_93, codabar, data_matrix, ean_13, ean_8, itf, pdf417,
qr_code, upc_a, upc_e, unknown`; "You can check for formats supported by the user agent via the
`getSupportedFormats()` method." [CONFIRMADO: MDN/BCD]

**Chrome Android (código de Chromium):**
`services/shape_detection/android/java/src/org/chromium/shape_detection/BarcodeDetectionProviderImpl.java`
-- `create()` devuelve `null` (detección deshabilitada) si `ChromiumPlayServicesAvailability` no ve Google
Play Services ("Google Play Services not available") o si la versión es menor a 19742000
("Detection disabled (%d < 19.7.42)", referencia https://crbug.com/1020746). `enumerateSupportedFormats`
devuelve 13 formatos fijos: AZTEC, CODE_128, CODE_39, CODE_93, CODABAR, DATA_MATRIX, EAN_13, EAN_8, ITF,
PDF417, QR_CODE, UPC_A, UPC_E. La implementación (`BarcodeDetectionImpl.java`) usa
`com.google.android.gms.vision.barcode.BarcodeDetector`. [CONFIRMADO: código fuente, rama main]
Coincide con la documentación de Chrome (https://developer.chrome.com/docs/capabilities/shape-detection,
página con pie "Last updated 2019-01-07" aunque su texto menciona Chrome 83): "Barcode detection is
available on macOS, ChromeOS, and Android." / "Google Play Services are required on Android." /
"The presence of an interface doesn't tell you whether the underlying platform supports the feature." [CONFIRMADO]

**Safari/iOS (código de WebKit):** `Source/WTF/Scripts/Preferences/UnifiedWebPreferences.yaml` define
`ShapeDetection: status: testable, humanReadableName: "Shape Detection API", defaultValue: false`, con la
nota "When enabling this, don't enable on watchOS or the macOS base system (which don't have
Vision.framework)". Es decir, apagado por defecto en WebKit `main`. Todos los navegadores de iOS usan
WebKit [INFERENCIA: es política de plataforma de Apple, no verificada aquí con fuente], así que en iOS no
hay `BarcodeDetector` por defecto. [CONFIRMADO: código WebKit para Safari; INFERENCIA para otros navegadores iOS]

**Implicación para el F7** [INFERENCIA]: si una unidad no tuviera Google Play Services, el `BarcodeDetector`
de Chrome quedaría deshabilitado aun existiendo la interfaz; se vería como `getSupportedFormats()` vacío o
error. Solo comprobable en el equipo.

### 2.b Alternativas a ZXing-JS y mantenimiento de `@zxing/library`

**`@zxing/library` (oficial, https://github.com/zxing-js/library):** el README dice, literal:

> Looking for an actively maintained barcode scanning library with commercial support? Check out STRICH ...
> ## Project in Maintenance Mode Only. The project is in maintenance mode, meaning, changes are driven by
> contributed patches. Only bug fixes and minor enhancements will be considered. There is otherwise no
> active development or roadmap for this project. It is "DIY". ... While we do not have the time to actively
> maintain zxing-js anymore, we are open to new maintainers taking the lead.

(el banner promociona una librería comercial ajena; se cita solo como texto del README). Estado a
2026-09-21: **no archivado**; 179 issues abiertos; último push 2026-09-13. Releases (registro npm):
0.19.1 2022-01-10; 0.19.2 2023-01-25; 0.19.3 y 0.20.0 2023-04-19; 0.21.0 2024-04-29; 0.21.3 2024-08-21;
**0.22.0 2026-04-27; 0.23.0 2026-04-29** (`latest`). Notas de 0.23.0
(https://github.com/zxing-js/library/releases/tag/v0.23.0): "OneDReader: Increased default row sampling
from 15 to 25 lines, covering ~78% of image height (up from ~47%) ... without requiring TRY_HARDER";
"BrowserCodeReader: Added GlobalHistogramBinarizer fallback when HybridBinarizer fails ... on very small
barcodes or uniform-background images"; buffer de escala de grises reutilizable por frame; error del bucle
continuo ahora se registra; soporte MaxiCode y (0.22.0) Micro QR; README: MaxiCode "needs testing!",
RSS-Expanded "not production ready!". `@zxing/browser` (paquete aparte): 0.1.5 2024-05-22, 0.2.0 2026-04-27,
0.2.1 2026-07-06; repo no archivado, 55 issues. [CONFIRMADO: README, releases, registro npm, API de GitHub]
El bundle del proyecto (0.19.1) no tiene ninguna de esas mejoras. El impacto de actualizar en tasa de
lectura o compatibilidad de API con el código actual **no se probó**. [NO VERIFICADO]

**`zxing-wasm` y `barcode-detector` (Sec-ant):**

| Paquete | Estado (2026-09-21) | Datos |
|---|---|---|
| `zxing-wasm` (https://github.com/Sec-ant/zxing-wasm) | v3.1.4 publicada 2026-09-10; repo activo (push 2026-09-20); MIT | "ZXing-C++ WebAssembly as an ES/CJS module"; `zxing-wasm/reader`: binario wasm "~1.04 MiB"; `full`: "~1.46 MiB". `.wasm` se descarga en runtime desde jsDelivr por defecto; se puede servir propio con `prepareZXingModule({ overrides: { locateFile } })` |
| `barcode-detector` (https://github.com/Sec-ant/barcode-detector) | v3.2.2 publicada 2026-08-16; activo (push 2026-09-19); MIT | "A Barcode Detection API ponyfill/polyfill that uses ZXing-C++ WebAssembly under the hood". Subruta `polyfill`: "will automatically register the BarcodeDetector class ... if it's not already present"; subruta `ponyfill`: clase sin tocar el global. Soporta `codabar, code_39, code_93, code_128, itf, ean_*, upc_*, databar*, pdf417, qr_code, data_matrix, aztec, ...` (lista completa en su README) |
| ZXing-C++ (upstream, https://github.com/zxing-cpp/zxing-cpp) | v3.1.1 publicada 2026-07-29; push 2026-09-20; Apache-2.0 | README: "originally ported from the Java ZXing library but has been developed further and now includes many improvements in terms of runtime and detection performance" |

[CONFIRMADO: READMEs, npm y API de GitHub]. La afirmación de "mejoras de rendimiento y detección" de ZXing-C++
es de sus propios mantenedores; **no se encontró ningún benchmark independiente** y no se midió aquí.
[NO VERIFICADO]. Opciones de `ReaderOptions` (fuente:
`zxing-wasm/src/bindings/readerOptions.ts`, `zxing-cpp/core/src/ReaderOptions.h`): `formats` (por defecto
todos), `tryHarder`, `tryRotate`, `tryInvert`, `tryDownscale` (todos `true` por defecto), `binarizer`,
`downscaleThreshold` 500 / `downscaleFactor` 3, `minLineCount` "The number of scan lines in a linear barcode
that have to be equal to accept the result (default: 2)", `maxNumberOfSymbols` 255. [CONFIRMADO: código]

### 2.c Restricciones de `getUserMedia` útiles para códigos 1D

- **Resolución.** Sin restricciones de tamaño, Chrome usa 640x480 a 30 fps: `MediaStreamVideoSource`
  (`third_party/blink/public/web/modules/mediastream/media_stream_video_source.h`): "Default resolution. If no
  constraints are specified and the delegate support it, this is the resolution that will be used.
  `kDefaultWidth = 640, kDefaultHeight = 480, kDefaultFrameRate = 30`". [CONFIRMADO: código Chromium]
  Para Safari no se encontró el equivalente. [NO VERIFICADO]. MDN
  (https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia): "An `ideal` value ... has
  gravity -- the browser will try to find the setting ... with the smallest fitness distance from the ideal
  values"; "Plain values are inherently ideal"; `min`/`max`/`exact` obligan y pueden producir
  `OverconstrainedError`; su ejemplo usa `{ width: 1280, height: 720 }`. [CONFIRMADO: MDN] Que 1280x720 o
  1920x1080 mejoren la lectura de 1D es lo esperable por más píxeles por módulo, pero **no hay fuente
  oficial que lo cuantifique**. [INFERENCIA]
- **`focusMode: continuous`.** MDN lista `focusMode` ("none", "manual", "single-shot", "continuous") entre las
  propiedades de pistas de imagen de `MediaTrackConstraints`, sin tabla de compatibilidad
  (https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints). En Chrome Android el modo por
  defecto **ya es continuo**: `media/capture/video/android/java/src/org/chromium/media/VideoCaptureCamera2.java`
  inicializa `mFocusMode = AndroidMeteringMode.CONTINUOUS` y lo traduce a `CONTROL_AF_MODE_CONTINUOUS_PICTURE`.
  En WebKit, `MediaTrackConstraints.idl` tiene `// FIXME: add focusMode;` (no implementado), y
  `MediaTrackCapabilities.idl` igual. [CONFIRMADO: código Chromium y WebKit]. Conclusión [INFERENCIA]: pedir
  `focusMode` no aporta en Chrome Android (ya es continuo) y no existe en Safari.
- **`torch`.** Chrome (https://developer.chrome.com/blog/imagecapture, "Last updated 2016-12-05"): "Torch mode
  (flash constantly on) can be found in the `MediaTrackCapabilities`"; es un ajuste "live" que se aplica con
  `applyConstraints({ advanced: [{ torch: true }] })`. Chromium Android reporta `SUPPORTS_TORCH` si la cámara
  tiene unidad de flash (`FLASH_INFO_AVAILABLE`; el código comenta que Camera2 no permite consultar el modo
  torch y "since there's a Flash unit, we assume so"). WebKit: `torch` está en las restricciones/capacidades
  (`ConstrainBoolean torch`) y `AVVideoCaptureSource.mm` lo expone si `[device hasTorch]` (iPhone con flash).
  El blog de WebKit de Safari 18.4
  (https://webkit.org/blog/16574/webkit-features-in-safari-18-4/) corrige un `getSettings()` desactualizado
  para `torch` y `whiteBalanceMode`, lo que confirma que existe en Safari. [CONFIRMADO: docs y código]. La
  disponibilidad real depende de cada dispositivo: hay que consultar `track.getCapabilities()` en ejecución.
- **`zoom`.** Chrome: mismo blog, `applyConstraints({ advanced: [{ zoom }] })` tras `getCapabilities()`; en
  `VideoCaptureCamera2.java` `MIN_ZOOM = 1.0`, `MAX_ZOOM = mMaxZoom` (de la cámara). WebKit: Safari 17.0
  "exposing `zoom` in `MediaTrackCapabilities`" (https://webkit.org/blog/14445/webkit-features-in-safari-17-0/);
  en `AVVideoCaptureSource.mm`: "We restrict zoom for now as it might require elevated permissions" y tope 10x.
  [CONFIRMADO: docs y código]
- **Nada de lo anterior está garantizado por dispositivo.** Todo es "si el equipo lo reporta". El cambio de
  restricciones sobre ZXing-JS 0.19.1 se haría con `decodeFromConstraints` (ver sección 0). [INFERENCIA]

### 2.d Hints de ZXing (`POSSIBLE_FORMATS`, `TRY_HARDER`) según el código v0.19.1

Fuentes: `src/core/DecodeHintType.ts`, `src/core/MultiFormatReader.ts`, `src/core/oned/OneDReader.ts`,
`src/core/oned/MultiFormatOneDReader.ts`, `src/core/oned/ITFReader.ts` (tag `v0.19.1` del repo
zxing-js/library).

- **`POSSIBLE_FORMATS`** (documentación del enum: "Image is known to be of one of a few possible formats").
  `MultiFormatReader.setHints` solo instancia los lectores de los formatos pedidos; sin hints prueba, para cada
  frame, 1D (UPC/EAN, Code 39, Code 128, ITF, RSS-14) y luego QR, DataMatrix, Aztec y PDF417. Restringir a
  1D evita construir/probar los cuatro lectores 2D en cada frame fallido. [CONFIRMADO: código]. Menos falsos
  positivos por tener menos decodificadores compitiendo es plausible pero **no cuantificado** en ninguna
  documentación. [INFERENCIA]. Trampa: si la lista pedida solo contiene formatos sin lector cableado
  (Codabar, Code 93 en 0.19.1), `MultiFormatOneDReader` cae a la lista por defecto completa.
- **Robustez propia de cada simbología.** Code 128 lleva checksum módulo 103 obligatorio que ZXing verifica
  (`checksumTotal % 103 !== lastCode` -> error): lecturas erróneas poco probables. Code 39 solo verifica
  checksum si se activa `ASSUME_CODE_39_CHECK_DIGIT`. ITF no tiene checksum obligatorio y por defecto solo
  acepta longitudes `[6, 8, 10, 12, 14]` (o mayores a 14) salvo que se pase el hint `ALLOWED_LENGTHS`
  ("Allowed lengths of encoded data -- reject anything else"). [CONFIRMADO: código]
- **`TRY_HARDER`** ("Spend more time to try to find a barcode; optimize for accuracy, not speed"). En
  `OneDReader.doDecode`: sin él, `rowStep = max(1, height >> 5)` y `maxLines = 15` ("roughly the middle half
  of the image"); con él, `rowStep = max(1, height >> 8)` y `maxLines = height` ("Look at the whole image"), y si
  falla reintenta con la imagen rotada 90 grados. En `MultiFormatReader`, con `TRY_HARDER` los lectores 1D pasan
  **al final** de la lista (después de QR/DM/Aztec/PDF417). Aritmética [INFERENCIA de código, sin medición]: a
  640x480 son 15 filas frente a hasta 480; a 1280x720, 15 frente a hasta 720 (más el pase rotado) por cada
  frame sin código. Dos rarezas de 0.19.1: `MultiFormatReader` detecta `TRY_HARDER` con `!== undefined` (basta
  con haber puesto la clave, aunque sea `false`) mientras `OneDReader` exige `=== true`; y sin `POSSIBLE_FORMATS`,
  `TRY_HARDER` retrasa la lectura 1D detrás de los cuatro lectores 2D.
- **Costo/beneficio.** `POSSIBLE_FORMATS` recorta trabajo por frame y sirve si se conoce la simbología (P3: no
  se conoce con fuente primaria); `TRY_HARDER` amplía la búsqueda por toda la imagen a costa de más CPU por
  frame, útil cuando el código no está centrado o es pequeño. En 0.23.0 el muestreo sin `TRY_HARDER` ya sube de
  15 a 25 líneas. [CONFIRMADO: notas de 0.23.0; el resto INFERENCIA]

### 2.e Contexto seguro y permisos

- MDN, `getUserMedia` (https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia): "This feature
  is available only in secure contexts (HTTPS)"; "in insecure contexts, `navigator.mediaDevices` is `undefined`";
  "must always get user permission ... Browsers may offer a once-per-domain permission feature, but they must ask at
  least the first time"; las directivas de Permissions-Policy que aplican son `camera` y `microphone` (por ejemplo
  `Permissions-Policy: camera=(self)`, relevante si la página se embebe en un iframe). [CONFIRMADO: MDN]
- MDN, contextos seguros (https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts): son
  seguros los documentos servidos por HTTPS o desde `localhost`/`127.0.0.0/8`/`*.localhost`. [CONFIRMADO: MDN]
  El servidor dev en `localhost:8010` califica; una IP de red local por HTTP (p. ej. `http://192.168.x.x:8010` desde
  un celular) **no**. [INFERENCIA a partir de la regla]
- **iOS / PWA instalada:** WebKit Bugzilla 185448 ("getUserMedia not working in apps added to home screen that run in
  standalone mode"), estado RESOLVED FIXED; comentario de un ingeniero de Apple del 2020-02-05: "With today's iOS and
  iPadOS 13.4 Beta, WebRTC (getUserMedia) should work as expected in home screen web apps."
  (https://bugs.webkit.org/show_bug.cgi?id=185448). Bug 215884 ("recurring permissions prompts in standalone when
  hash changes"): RESOLVED CONFIGURATION CHANGED (última modificación 2026-02-03); los comentarios de usuarios (no oficiales) siguen
  reportando que una PWA instalada vuelve a pedir el permiso de cámara aunque Safari ya lo tuviera
  (https://bugs.webkit.org/show_bug.cgi?id=215884). [CONFIRMADO para el arreglo; los reportes de reprompt son de
  usuarios]
- **Otros navegadores de iOS (Chrome, Firefox):** WebKit Bugzilla 208667 ("getUserMedia does not work in
  WKWebView-based browsers like Chrome, Firefox"), cerrado el 2021-01-05: "WKWebView applications can now have
  access to getUserMedia" (confirmaciones en iOS 14.3). (https://bugs.webkit.org/show_bug.cgi?id=208667). [CONFIRMADO]

---

## 3. P3 -- Simbologías/longitudes de las guías colombianas

**Regla aplicada:** solo cuenta como confirmado un documento de la transportadora o de la plataforma. Blogs,
foros y publicaciones de otros países no se usaron como confirmación. **Resultado: en ningún caso se encontró
un documento oficial que diga qué simbología (Code 128, ITF, Code 39, QR, etc.) usa el código de barras de la
guía.** Lo hallado es sobre formato/longitud del número de guía y una muestra de rótulo.

| Operador | Qué dice una fuente propia | Fuente | Simbología publicada |
|---|---|---|---|
| **Coordinadora** | El número de guía tiene 11 dígitos: en el rastreo, "Verifica que cada número de guía contenga los 11 dígitos correspondientes para que el sistema lo reconozca adecuadamente". En la documentación de su servicio web el ejemplo de `codigo_remision` es `00011234567` (11 dígitos con ceros a la izquierda) | https://coordinadora.com/blog/numero-de-seguimiento-que-es/ ; https://sandbox.coordinadora.com/agw/ws/guias/1.4/server.php?doc= | No |
| **4-72 (Servicios Postales Nacionales)** | "si tu envío es de correo certificado, el número de guía debe estar compuesto por 13 dígitos, ejemplo: ET123456789CO"; y en otra respuesta: "Guía Nº (Debe ser de 13 caracteres, 2 letras iniciando, seguidas de 9 números y dos letras finalizando)" (la propia página mezcla "13 dígitos" y "13 caracteres") | https://www.4-72.com.co/preguntas-frecuentes/1/preguntas-frecuentes-4-72/ | No |
| **Servientrega** | WSDL oficial del servicio `GeneracionGuias`: la etiqueta se genera en "Bond, Sticker, Tirilla, Estandar 10x14, Estandar 10x10 o Zpl"; `Num_Guia` es de tipo `s:decimal`; hay "rangos de guías provisionados" por cliente. No dice cuántos dígitos ni qué simbología | http://web.servientrega.com:8081/GeneracionGuias.asmx (y `?WSDL`) | No |
| **Interrapidísimo** | No se encontró documento con longitud ni simbología. Un buscador devolvió URLs del propio sitio de seguimiento con números de 12 dígitos (p. ej. `.../SiguetuEnvio/shipment/700106501330`), que **no se verificaron** | (sin fuente citable) | No |
| **Envía** | Según resultados de búsqueda (las páginas no se abrieron): etiquetas en formato PDF y ZPL (ZPLII STOCK_4X6); nada sobre simbología ni longitud | help.envia.com / docs.envia.com (solo snippets) | No |
| **TCC, Deprisa** | Se buscó en sus dominios (`tcc.com.co`, `deprisa.com`): solo páginas de rastreo/generación de guía (TCC: rastreo múltiple separado por comas; Deprisa: hasta 10 guías separadas por comas); sin longitud ni simbología | https://tcc.com.co/rastreo/ ; https://www.deprisa.com/es/rastrea | No |
| **Mercado Libre Envíos** | Docs de desarrolladores de "Mercado Envíos 2": etiquetas por el recurso `shipment_labels`, formatos `pdf` o `zpl2`. En el texto de la página (25 KB) no aparece "código de barras", "barcode", "QR" ni "Code 128" | https://developers.mercadolibre.com.ar/es_ar/mercadoenvios-modo-2 ; https://developers.mercadolibre.com.co/es_ar/envios | No |

[CONFIRMADO: documento de la transportadora/plataforma] para las cifras y frases citadas de Coordinadora, 4-72,
Servientrega y Mercado Libre; [NO ENCONTRADO] para simbologías en todos los casos; Interrapidísimo, TCC,
Deprisa y Envía quedan sin dato propio.

**Muestra de rótulo de Coordinadora (observación propia sobre un documento de la transportadora).**
`http://ws.coordinadora.com/rotulo15x6Nuevo.pdf` (PDF de 922 páginas de etiquetas 15x6 cm generado con FPDF,
fecha interna 2019-07-16). Se renderizó la página 1 y 2 a 300 dpi y se decodificó con el mismo bundle ZXing 0.19.1
del proyecto: restringiendo a cada formato 1D (Code 128, Code 39, ITF, EAN-13, UPC-A, EAN-8, RSS-14; con y sin
`TRY_HARDER`) **no hubo lectura**; restringiendo a QR **sí**: un QR cuyo texto son **32 caracteres, todos
dígitos**. Un análisis de transiciones por fila tampoco halló ninguna banda alta compatible con un código 1D
(solo líneas de texto). Por privacidad no se registró ningún dato de los envíos, solo formato y longitud.
Limitaciones: es una sola muestra de 2019 y no se sabe si el QR de 32 dígitos contiene el número de guía de 11
dígitos ni si las etiquetas actuales son iguales. [CONFIRMADO: existencia de un QR de 32 dígitos en esa
muestra; INFERENCIA: ausencia de 1D en el rótulo, por mi análisis; NO VERIFICABLE: relación del QR con la guía]

**Consecuencias, todas de confianza baja** [INFERENCIA]:

- Una guía puede ser numérica de 11-12 dígitos, o alfanumérica de 13 caracteres (4-72). Un lector configurado
  solo para ITF/numérico no leería la de 4-72.
- Lo que "el código de barras" devuelve puede no ser lo que el portero teclearía a mano (p. ej. un QR de 32
  dígitos frente a una guía de 11), por lo que un campo de guía alimentado por escáner podría necesitar
  normalización o una regla por transportadora.
- Con 0.19.1, si alguna transportadora usara Codabar o Code 93, ZXing no la leería (sección 0).

---

## Qué implica para PaqueteX (inferencias, no decisiones)

Todo lo que sigue es **[INFERENCIA]** derivada de los hechos de arriba; no se recomienda una opción como
definitiva -- eso se resuelve en la entrevista con el dueño del proyecto.

**Frente F7 (lector integrado)**

1. *Dejar de fábrica (`BROADCAST`).* Según el documento del fabricante es el defecto y una página web no recibe
   broadcasts de Android; el campo Guía quedaría sin texto. Solo sirve si hay una app nativa/envoltorio que
   escuche el broadcast, lo cual está fuera del stack actual (FastAPI + JS vanilla).
2. *Configurar `FOCUS` o `FOCUS_OVERWRITE` con terminador `NONE`.* La lectura se escribiría en el campo enfocado
   sin enviar el formulario; el operador confirma con el botón. Depende de que `FOCUS` funcione dentro de un
   `<input>` de Chrome (no documentado) y de que el campo tenga el foco (hecho ya verificado: el modal deja el foco
   en el botón de la fila; el pedido de quitar `autofocus` es de vistas de staff, issue 284 -- si aplica o no a un
   input dentro del modal es decisión del dueño).
3. *Configurar `FOCUS` con terminador `ENTER`.* El formulario se envía solo (hecho ya verificado): flujo más rápido,
   pero una lectura errónea o de otra simbología recibe un paquete sin confirmación. Un `TAB` como terminador
   movería el foco al siguiente campo sin enviar.
4. *Usar `CLIPBOARD`.* Existe en la API pero exige pegar manualmente; parece poco práctico frente a `FOCUS`.
5. *La configuración vive en cada equipo,* no en la web (los ajustes se cambian por la app del escáner o por
   broadcasts); con varios F7 habría que replicarla o administrarla aparte (p. ej. la vía ADB de 1.4, sin probar).
6. *Que el campo pueda recibir texto por el teclado* (además de la cámara) ya es la ruta natural: el F7 también
   tiene teclado físico numérico y una cámara de 13 MP con autofoco, por lo que el botón "Escanear con cámara"
   podría usarse en el F7 si Chrome y `getUserMedia` funcionan allí (no verificado).

**Frente cámara (celulares Android/iPhone)**

7. *Dejar ZXing 0.19.1 como está.* Sin restricciones, 640x480; sin Codabar/Code 93; bucle sin pausa tras fallos.
8. *Pasar restricciones (`decodeFromConstraints`)* con resolución ideal 1280x720 o 1920x1080 y un botón de linterna
   si `getCapabilities().torch` existe; `focusMode` no aporta en Chrome Android (ya es continuo) y no existe en
   Safari.
9. *Añadir hints* (`POSSIBLE_FORMATS` con los 1D que se confirmen en campo; `ALLOWED_LENGTHS`/`TRY_HARDER` según
   el caso) a costa de perder formatos no listados; hoy no hay fuente para elegir la lista.
10. *Actualizar `@zxing/library` a 0.23.0* (mejor muestreo 1D, Code 93/Codabar cableados en `POSSIBLE_FORMATS`),
    sin probar compatibilidad con el código actual.
11. *Usar `BarcodeDetector` nativo donde exista* (Chrome Android con Play Services) y ZXing (o el polyfill
    `barcode-detector`) como respaldo en iOS/Firefox/equipos sin Play Services.
12. *Migrar a `zxing-wasm`/`barcode-detector`* (ZXing-C++, mantenido, ~1 MiB de wasm autoalojado para no depender
    del CDN); implica un peso mayor y una prueba de rendimiento propia.
13. *Normalizar lo leído antes de guardarlo* (recortar espacios/caracteres invisibles, decidir qué hacer con QR
    largos o alfanuméricos): el valor debería tratarse igual venga del lector, la cámara o el teclado.

---

## Preguntas que solo el equipo físico o el cliente pueden responder

1. Modelo exacto en la etiqueta trasera del equipo (¿"F7", "F7-Pro", "F7T"?) y variante (¿N6603 con NFC/4G o
   F7-WiFi con SE6100?).
2. Versión de Android y del parche; ¿está instalado Chrome? ¿versión (`chrome://version`)? ¿hay Google Play
   Services/Play Store en esa unidad?
3. En "Settings -> Scanning Tools -> Scanning Settings": captura de todas las pantallas, sobre todo el "send
   mode" actual, el terminador/sufijo y qué simbologías aparecen activadas.
4. ¿El gatillo lateral y el botón flotante de escaneo funcionan con Chrome abierto sobre un formulario web?
5. Con `FOCUS`/`FOCUS_OVERWRITE`: ¿el texto entra en un `<input>` de Chrome? ¿con qué latencia? ¿duplica o
   trunca caracteres?
6. ¿Qué transportadoras llegan realmente y en qué proporción? Para cada una, una guía física real: qué código
   trae (¿1D, QR, ambos?), qué texto devuelve el lector y cómo se compara con el número impreso.
7. ¿También se usarán iPhones? ¿Qué versión de iOS y desde Safari o desde una PWA instalada?
8. ¿El flujo deseado tras una lectura es confirmar a mano o recibir al instante (Enter automático)?

## Protocolo de prueba de campo para el F7 (sin construir herramientas)

Objetivo: saber qué entrega el equipo a una página web y qué simbologías/formatos ve. Usar el servidor dev o
`test.papyrus.com.co` con el modal "Recibir paquete", y como control un campo de texto ordinario (p. ej. el cuadro de
búsqueda de Google en Chrome).

1. **Identificar el equipo:** foto de la etiqueta trasera; en Ajustes -> Acerca del teléfono, versión de Android;
   en Chrome, `chrome://version`; anotar si existe Google Play.
2. **Fotografiar los ajustes del escáner:** Ajustes -> Scanning Tools -> Scanning Settings, todas las pantallas
   (modo de envío, terminador, prefijo/sufijo, filtros, simbologías).
3. **Prueba de campo enfocado sin la app de PaqueteX:** en Chrome, tocar un campo de texto ordinario, apretar el
   gatillo lateral y escanear un código 1D de una guía real. Observar: ¿aparece texto?, ¿agrega Enter/Tab/espacio?,
   ¿cambia con el modo `FOCUS`, `FOCUS_OVERWRITE` ("Focus+Broadcast" en el FAQ), `BROADCAST`, `CLIPBOARD`?
4. **Repetir en el modal de PaqueteX:** con y sin tocar antes el campo Guía; con terminador `NONE` y con `ENTER`
   (¿se recibe el paquete?); anotar cuántos toques hicieron falta.
5. **Una guía real por cada transportadora** (Servientrega, Interrapidísimo, Coordinadora, Envía, TCC, 4-72,
   Deprisa, Mercado Libre): anotar el texto devuelto frente al número impreso (longitud, letras, ceros a la
   izquierda, prefijos), y si la etiqueta trae un 1D, un QR o ambos y cuál lee el F7.
6. **Robustez y comparación de cámara:** distancia y ángulo, etiqueta arrugada o brillante, código en pantalla,
   dos lecturas seguidas del mismo código (¿duplica?), lectura rápida en ráfaga. Repetir las guías del paso 5 con
   "Escanear con cámara" en el F7, en un Android normal (Chrome) y en un iPhone (Safari): éxito sí/no y tiempo
   aproximado; en la consola remota (`chrome://inspect`) `track.getSettings()`/`getCapabilities()` para ver la
   resolución real y si hay `torch`/`zoom`.

---

## Qué queda sin verificar

- **Todo lo que solo el equipo físico responde:** comportamiento de `FOCUS`/`FOCUS_OVERWRITE` en Chrome, valor por
  defecto real del "send mode" en el firmware del cliente (el documento dice `BROADCAST`; el FAQ dice que hay que
  poner "Focus+Broadcast"), significado exacto de ese nombre, funcionamiento del gatillo con un formulario web,
  presencia/versión de Chrome y de Google Play Services.
- Manual completo de la app "scan tool" del F7 (los botones de descarga de farset.net están vacíos), tabla de
  parámetros de `setScanningParameter`, FCC ID, y quién es "Eastaeon" (nombre de paquete en el servicio de escaneo).
- Si "F7", "F7-Pro" y "F7T" son el mismo equipo.
- Cualquier medición de rendimiento: ZXing-JS 0.19.1 frente a 0.23.0, frente a `zxing-wasm`; efecto de 1280x720 o
  1920x1080 en la tasa de lectura de 1D; costo real de `TRY_HARDER`; efecto del bucle sin pausa en batería.
  No se encontró benchmark independiente de ZXing-C++ frente a ZXing-JS.
- Compatibilidad de API entre `@zxing/library` 0.19.1 y 0.23.0 para el código actual.
- Resolución por defecto de `getUserMedia` en Safari/iOS, y comportamiento del autoenfoque allí (WebKit no
  implementa `focusMode`); en qué versión exacta de iOS/Safari salieron `torch` y `zoom` como restricciones.
- Simbología del código de barras de cada transportadora (Servientrega, Interrapidísimo, Coordinadora, Envía, TCC,
  4-72, Deprisa, Mercado Libre): sin fuente primaria. Longitud de guía de Servientrega, Interrapidísimo, TCC, Envía y
  Deprisa: sin fuente primaria. Contenido del QR de 32 dígitos de la muestra de Coordinadora y si las etiquetas
  actuales lo mantienen.
- Si Samsung Internet (fork de Chromium) hereda la exigencia de Google Play Services para `BarcodeDetector`, y el
  comportamiento en WebViews embebidos.
- Fuentes intentadas sin éxito: `issues.chromium.org` (login), página de `enviosonline.4-72.com.co` (no resuelve
  DNS desde este entorno), un PDF público de Interrapidísimo listado por el buscador (404 al pedirlo).
