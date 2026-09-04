# Investigación oficial: por qué un enlace `wa.me` no abrió la app nativa de WhatsApp en Android

**Contexto:** PaqueteX genera enlaces `https://wa.me/<telefono>?text=<mensaje>` en `/paquetes`,
`/residentes` y el footer público. El cliente probó uno de estos enlaces desde su Android real,
con WhatsApp nativo instalado, y el enlace abrió el navegador con una página web en vez de lanzar
la app. Esta investigación contrasta el problema contra documentación y comportamiento oficial de
Meta/WhatsApp, más las plataformas Android/iOS de las que depende el mecanismo.

**Nota de metodología:** `faq.whatsapp.com` bloquea `curl`/fetchers automatizados directos (HTTP
400 por WAF) para varias rutas. El contenido citado de `faq.whatsapp.com/5913398998672934` se
recuperó de una copia archivada íntegra en Wayback Machine (`web.archive.org`, captura del
2026-01-21) que contiene el JSON fuente exacto que ese artículo sirve en producción -- no es un
resumen de terceros, es el contenido oficial en crudo. Además, donde la documentación de texto de
Meta no alcanza, se usó **observación directa del comportamiento en vivo de los servidores de
producción de `wa.me`/`api.whatsapp.com`** (peticiones HTTP reales hechas para esta investigación,
2026-09-03) como evidencia de primera mano -- se marca explícitamente dónde una afirmación viene de
ahí en vez de un documento de ayuda.

**Contexto interno relevante (ya en este repo):** este mismo problema tiene una historia previa
documentada en `.scratch/pendientes-cliente/issues/301-whatsapp-web-send-sin-target-blank.md` y
`.scratch/pendientes-cliente/issues/304-whatsapp-revierte-web-whatsapp-com.md`. Resumen: el
cliente pidió originalmente migrar a `web.whatsapp.com/send?phone=` (301); verificado en vivo,
`web.whatsapp.com` **nunca** abrió la app en ningún dispositivo (ni Android nativo, ni Chrome de
escritorio sin configuración manual de 3 pasos) -- se revirtió a `wa.me` (304), desplegado a
`test.papyrus.com.co` el mismo día de esta investigación (2026-09-03). El cierre de 304 queda
explícito: *"Pendiente: que el cliente confirme en su propio Android que ya abre la app de verdad
(esa parte no se puede probar por curl)."* El reporte que motiva esta investigación es,
aparentemente, esa confirmación pendiente -- y resultó negativa incluso con `wa.me`.

---

## Resumen ejecutivo

El formato del enlace actual de PaqueteX (`wa.me/<solo dígitos, sin +>?text=<urlencoded>`) es
**exactamente** el que exige la documentación oficial de WhatsApp -- eso queda descartado como
causa. `wa.me` y `api.whatsapp.com/send` son, en efecto, el mismo mecanismo (`wa.me` es un
redirector HTTP 302 hacia `api.whatsapp.com/send`, verificado en esta investigación). El
mecanismo real por el que la app se abre **no está documentado por Meta en ningún nivel técnico**:
Meta nunca publica que dependa de Android App Links / iOS Universal Links -- pero la evidencia de
primera mano (código fuente real de la página de `api.whatsapp.com/send`, ver Pregunta 1) confirma
que así es. La página web que el usuario vio ("Share on WhatsApp") **es precisamente el fallback
documentado** que Android/Apple describen para cuando esa intercepción a nivel de sistema
operativo no ocurre -- no es una señal de que el link esté mal construido. Dado que en este caso
`wa.me` (el dominio correcto, con formato correcto) tampoco abrió la app en el Android real del
cliente, la causa más probable **no es el link ni el dominio** -- es alguna condición del lado del
sistema operativo/navegador de ese dispositivo específico que impide que Android reconozca a
WhatsApp como manejador verificado de ese enlace en el momento del clic (ver Pregunta 2 y la
sección final).

---

## 1. Mecanismo exacto por el que `wa.me`/`api.whatsapp.com/send` abren la app nativa

**Meta no documenta el mecanismo técnico en ningún texto de ayuda encontrado.** Se buscó
exhaustivamente en `faq.whatsapp.com`, `business.whatsapp.com`, `business.whatsapp.com/developers`
y `developers.facebook.com` (incluida la página de Marketing API específica para "Click to
WhatsApp" ads,
[developers.facebook.com/docs/marketing-api/ad-creative/messaging-ads/click-to-whatsapp/](https://developers.facebook.com/docs/marketing-api/ad-creative/messaging-ads/click-to-whatsapp/))
y ninguna explica *cómo* el clic termina abriendo la app. Este es un hallazgo en sí mismo: Meta
documenta el **formato** del link (ver Pregunta 5) pero no el mecanismo de apertura.

Lo que sí se pudo establecer por **evidencia directa** (código fuente real servido por
`api.whatsapp.com` para esta investigación, 2026-09-03):

- `https://wa.me/<numero>?text=<msg>` responde con un **HTTP 302** cuyo `Location` es
  `https://api.whatsapp.com/send/?phone=<numero>&text=<msg>&type=phone_number&app_absent=0`.
  `wa.me` es, literalmente, un acortador/redirector -- no contiene lógica de apertura de app.
- La página que sirve `api.whatsapp.com/send/...` (título interno `"Share on WhatsApp"`) **no
  contiene ningún `intent://` ni redirección automática por JavaScript a un esquema de app** en el
  HTML/JS que recibe un navegador Chrome Android normal. Sí contiene un componente
  (`WAUIOpenAppIntegration`) que arma un botón visible **"Open WhatsApp"** cuyo `href`/acción es el
  esquema personalizado `whatsapp://send/?phone=<numero>&text=<msg>`, más un enlace de
  respaldo `https://www.whatsapp.com/download`.

Esto implica dos capas, ninguna documentada por Meta pero consistentes con el comportamiento
observado:

1. **Capa automática (silenciosa):** antes de que este HTML llegue a renderizarse, el sistema
   operativo intercepta la navegación HTTPS a `wa.me`/`api.whatsapp.com` si tiene esos dominios
   registrados como manejador verificado de la app -- esto es exactamente **Android App Links**
   (`android:autoVerify="true"` + archivo `assetlinks.json` en el dominio) documentado
   oficialmente por Google en
   [developer.android.com/training/app-links](https://developer.android.com/training/app-links) y
   [developer.android.com/training/app-links/verify-applinks](https://developer.android.com/training/app-links/verify-applinks),
   e **iOS Universal Links** (`apple-app-site-association` + entitlement de dominios asociados)
   documentado oficialmente por Apple en
   [developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app](https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app).
   Cuando esta capa funciona, el usuario nunca ve una página web -- pasa directo a la app.
2. **Capa manual (visible, de respaldo):** si la capa 1 no interceptó la navegación, el navegador
   sí carga la página `api.whatsapp.com/send`, que ofrece un botón "Open WhatsApp" (esquema
   `whatsapp://`, requiere que el usuario lo toque) y, si no hay app, un enlace de descarga.

El síntoma reportado por el cliente ("se abrió el navegador con una página web") es exactamente lo
que se ve cuando la Capa 1 no ocurre y el usuario no notó/tocó el botón de la Capa 2.

## 2. Condiciones bajo las cuales el mecanismo NO se activa

Ningún documento de Meta enumera estas condiciones explícitamente (tampoco es su plataforma la que
las controla). Lo que la documentación oficial **de la plataforma** (Google para Android) sí dice:

- **Verificación fallida o ausente:** según
  [Verify Android App Links](https://developer.android.com/training/app-links/verify-applinks),
  la app solo se establece como manejador automático de un dominio si el sistema verificó
  exitosamente el archivo Digital Asset Links de ese host. En Android 11 y anteriores, si falla la
  verificación de **cualquiera** de los hosts declarados por la app, el sistema no establece la
  app como manejador por defecto para ninguno.
- **Enlace no verificado → diálogo de desambiguación, no la app directamente:** según
  [App Links (overview)](https://developer.android.com/training/app-links), *"deep links are
  subject to the system disambiguation dialog"* mientras que los enlaces verificados *"can
  immediately open corresponding content in your app, without requiring the user to select your
  app from a disambiguation dialog"*. Es decir: sin verificación, Android puede mostrar un
  selector de apps en vez de abrir directo -- y si el usuario (o una elección previa "siempre
  abrir con...") resolvió ese selector hacia el navegador en el pasado, el link se abre en
  navegador sin más aviso.
- **El ajuste "Open by default" / "enlaces admitidos" del usuario:** el mismo documento describe
  la pantalla de sistema *Open by default* → toggle **"Open supported links"**, con una lista de
  dominios asociados a cada app. Si ese toggle está apagado para WhatsApp, o si otra app ya está
  asociada a ese dominio en ese dispositivo (*"On a given device, only one app at a time can be
  associated with a particular domain"*), WhatsApp no intercepta el link aunque esté instalada.
- **Cambios de comportamiento por versión de Android:** el mismo documento señala que Android 12+
  permite verificación manual (`adb shell am compat enable 175408749 PACKAGE_NAME` o el flujo
  normal si el APK apunta a Android 12+), y que Android 15+ re-verifica los dominios en segundo
  plano periódicamente (hasta 7 días de latencia para propagar cambios), mientras que Android 14 y
  anteriores **no** re-verifican automáticamente -- solo al instalar/actualizar la app. Esto
  importa si WhatsApp fue instalado hace mucho y el estado de verificación quedó desactualizado.

**Lo que la documentación de Android consultada NO cubre explícitamente** (búsqueda dedicada, sin
resultado en `developer.android.com/training/app-links*`): el comportamiento específico cuando el
link se abre dentro de un WebView/in-app-browser de otra app (Instagram, Gmail, un SMS) en vez de
un navegador completo. Es sabido en la práctica que muchos WebViews embebidos no evalúan App Links
de la misma forma que un navegador de primera clase, pero no se encontró una página oficial de
Google o Meta que lo confirme por escrito -- se anota como pregunta abierta, no como hecho
verificado.

Un dato relacionado, encontrado indirectamente (no se localizó la URL oficial exacta en
`developers.facebook.com`/`business.whatsapp.com`, así que se cita con esa salvedad): Meta describe
en material de producto sobre "Click to WhatsApp ads" un **"In-App Browser (IAB) experience for
WhatsApp"** que reconoce como caso deliberado que un clic dentro del navegador embebido de
Facebook/Instagram puede necesitar redirigir explícitamente a la app si está instalada -- lo cual
confirma indirectamente que Meta sabe que sus propios navegadores embebidos no interceptan el link
hacia la app "gratis" por el mismo mecanismo que un navegador estándar.

## 3. ¿`wa.me` y `api.whatsapp.com/send` tienen el mismo comportamiento?

**Sí, confirmado por observación directa, no solo por documentación de terceros.** Ver Pregunta 1:
`wa.me/<numero>?text=<msg>` responde HTTP 302 con `Location: https://api.whatsapp.com/send/?phone=<numero>&text=<msg>&type=phone_number&app_absent=0`.
`wa.me` es el alias corto oficial que siempre reenvía a `api.whatsapp.com/send` -- son el mismo
mecanismo de intercepción en la capa de sistema operativo, no dos implementaciones distintas. Esto
coincide con lo que ya había quedado registrado en
`.scratch/pendientes-cliente/issues/304-whatsapp-revierte-web-whatsapp-com.md`: *"`api.whatsapp.com/send?phone=...&text=...`
-- funcionalmente idéntico a `wa.me` (mismo mecanismo, wa.me es su alias corto oficial)"*.

El artículo oficial de ayuda
([faq.whatsapp.com/5913398998672934](https://faq.whatsapp.com/5913398998672934)) solo documenta
`wa.me` -- no menciona `api.whatsapp.com/send` en ningún punto del texto (confirmado sobre el
contenido íntegro del artículo, no un resumen). Esto no es evidencia de que sean distintos, solo de
que Meta consolidó su documentación pública alrededor del dominio corto.

**Lo que sí es distinto y relevante para PaqueteX:** el dominio `web.whatsapp.com` (el cliente
web/escritorio, pensado para vincular sesión por QR) **no** es equivalente -- issue 304 ya lo
verificó en vivo en 2 dispositivos reales: nunca abre la app nativa por default en Android, y en
Chrome de escritorio solo bajo una configuración manual de 3 pasos por dispositivo. No es
"Click to Chat", es un producto distinto que casualmente acepta un parámetro `phone=` parecido.

## 4. Comportamiento de fallback documentado

**Meta no documenta explícitamente el fallback en el texto de ayuda de `faq.whatsapp.com`** más
allá de una frase genérica: *"By clicking the link, a chat with the person automatically opens.
Click to chat works on both your phone and WhatsApp Web."* -- no dice qué pasa si la app no está
instalada o si la intercepción del sistema operativo no ocurre.

Por observación directa (Pregunta 1), el fallback real es una página HTML servida por
`api.whatsapp.com/send` (título `"Share on WhatsApp"`) con:
- Un botón **"Open WhatsApp"** que intenta el esquema `whatsapp://send/?phone=...&text=...`
  (requiere clic del usuario -- no se auto-ejecuta al cargar la página).
- Un enlace **"Download WhatsApp"** hacia `https://www.whatsapp.com/download`.
- Contenido descriptivo genérico de WhatsApp Messenger.

Esta página es **exactamente** lo que Android documenta como comportamiento natural de un enlace
HTTPS normal cuando ningún manejador verificado lo intercepta: el sistema simplemente lo trata
como una URL web y el navegador la carga como cualquier otra. El síntoma "se abrió el navegador
con una página web" descrito por el cliente calza con esta página de fallback -- **no** con un
error de link roto (un link mal formado devolvería un error HTTP o un mensaje de WhatsApp
distinto, no esta página con branding "Share on WhatsApp"/"Open WhatsApp"/"Download WhatsApp").
Esto mueve la causa raíz hacia "algo impidió la intercepción a nivel de sistema operativo", tal
como planteaba la hipótesis (a)/(c) del problema original.

## 5. Requisitos de formato exigidos por la documentación oficial

Confirmado contra el contenido íntegro del artículo oficial
[faq.whatsapp.com/5913398998672934](https://faq.whatsapp.com/5913398998672934) ("How to use click
to chat"):

> Use **`https://wa.me/<number>`** where the `<number>` is a full phone number in international
> format. Omit any zeroes, brackets, or dashes when adding the phone number in international
> format.
>
> **Use**: `https://wa.me/1XXXXXXXXXX`
> **Don't use**: `https://wa.me/+001-(XXX)XXXXXXX`
>
> Use **`https://wa.me/whatsappphonenumber?text=urlencodedtext`** where `whatsappphonenumber` is a
> full phone number in international format and `urlencodedtext` is the URL-encoded pre-filled
> message.

En criollo: número completo con código de país, **sin** `+`, sin espacios, sin guiones, sin
paréntesis; el texto va en `?text=` URL-encoded. No se documenta ningún límite de longitud
explícito para `text=` en este artículo (no se encontró tampoco en ningún otro documento oficial
consultado).

**Esto coincide exactamente con la implementación actual de PaqueteX.** El código limpia el
número a solo dígitos sin `+` antes de construir el link
(`CODE/src/app/domain/persona_service.py:417` -- `numero = re.sub(r"\D", "", persona.telefono)`;
mismo patrón en `CODE/src/app/web/routes/packages.py:188`), y el `text=` se codifica vía
`urllib.parse.quote`/`urlencode` de Jinja según el punto. El formato del link **queda descartado
como causa** -- coincide al dígito con el ejemplo "Use" oficial (`wa.me/1XXXXXXXXXX`, mismo patrón
que `wa.me/573334004007` que usa el footer de PaqueteX).

## 6. Diagnóstico oficial para "el link no abre la app en un Android específico"

**No se encontró ninguna guía oficial de Meta/WhatsApp para diagnosticar esto** -- ni en
`faq.whatsapp.com` (se buscó explícitamente "links not opening WhatsApp", sin resultado oficial
más allá de artículos genéricos de terceros sobre "WhatsApp no abre", que no son la fuente
solicitada) ni en `business.whatsapp.com`. Esto es consistente con el resto de la investigación:
Meta no se responsabiliza documentalmente de la capa de sistema operativo que hace el trabajo
real.

Lo que sí existe, oficial pero del lado de Google (no de Meta), es la herramienta y el flujo de
verificación de Android App Links:

- Comando para revisar si el sistema verificó la app como manejador de un dominio (documentado en
  [Verify Android App Links](https://developer.android.com/training/app-links/verify-applinks),
  sección de verificación):
  ```
  adb shell pm get-app-links com.whatsapp
  ```
  (o el paquete correspondiente, `com.whatsapp` para la app estándar / `com.whatsapp.w4b` para
  WhatsApp Business).
- El flujo de usuario final documentado: Ajustes → Apps → WhatsApp → **Open by default** → toggle
  **Open supported links** → confirmar qué dominios están marcados. Es exactamente lo que la
  hipótesis (a) del problema original planteaba ("un ajuste de Android bloqueando la
  intercepción... 'Abrir por defecto' desactivado").

---

## Qué revisar en este caso concreto

Dado que el dominio y el formato del link ya están descartados con evidencia (Preguntas 3 y 5), y
que el síntoma reportado calza con el fallback documentado de Android/Apple para intercepción
fallida (Pregunta 4) -- no con un link roto -- los pasos priorizados son, en orden:

1. **Confirmar el ajuste "Open by default" de WhatsApp en el Android real del cliente.**
   Ajustes → Apps → WhatsApp → *Abrir por defecto* (o *Open by default*) → verificar que el toggle
   *Abrir enlaces admitidos* (*Open supported links*) esté **activado** y que `wa.me` /
   `api.whatsapp.com` aparezcan marcados en la lista de dominios. Si el toggle está apagado o esos
   dominios no están tildados, esa es la causa directa -- coincide con lo que Android documenta
   como requisito para saltar el diálogo/fallback (Pregunta 2).
2. **Revisar si otra app ya "ganó" esos dominios en ese dispositivo.** Android solo permite un
   manejador verificado por dominio a la vez (documentado, Pregunta 2). Si algún gestor de
   enlaces, navegador de terceros, o app de mensajería alternativa quedó asociado a `wa.me`/
   `api.whatsapp.com`, WhatsApp no puede interceptar aunque esté bien instalada.
3. **Repetir la prueba desde un navegador de pila completa (Chrome), no desde un WebView.** Si el
   cliente probó el link tocándolo dentro de otra app (una notificación, un correo, un chat
   interno, un navegador in-app), repetir el mismo link pegándolo directo en la barra de Chrome.
   Esto aísla si el problema es el contexto de apertura -- un factor que ni Google ni Meta
   documentan con precisión (Pregunta 2), pero que es la explicación más común reportada en la
   práctica para este síntoma exacto.
4. **Verificar versión de Android y de WhatsApp instaladas.** Relevante solo si los pasos 1-3 no
   explican el problema: versiones muy desactualizadas de Android (pre-6.0/API 23) no soportan App
   Links verificados en absoluto; y el estado de verificación puede haber quedado obsoleto si
   WhatsApp no se reinstaló/actualizó en mucho tiempo en dispositivos Android 14 o anteriores (sin
   re-verificación periódica, a diferencia de Android 15+, Pregunta 2).
5. **Correr el comando de diagnóstico si hay acceso ADB al dispositivo** (útil para el equipo, no
   para el cliente final): `adb shell pm get-app-links com.whatsapp` muestra el estado de
   verificación real que el sistema tiene para el paquete de WhatsApp.
6. **Como último recurso, tocar el botón "Open WhatsApp" de la página de fallback.** Si aparece la
   página `"Share on WhatsApp"` (justo lo reportado), hay un botón manual que sí dispara el
   esquema `whatsapp://` -- confirma que la app en sí funciona y que el problema es puramente la
   intercepción automática, no la app ni el link.

**Lo que NO hace falta revisar más** (ya descartado con evidencia en esta investigación, no solo
por descarte previo del equipo): el dominio (`wa.me` = `api.whatsapp.com/send`, mismo mecanismo,
Pregunta 3) y el formato del número/texto (coincide al dígito con el ejemplo oficial, Pregunta 5).
Insistir en cambiar el link (a `web.whatsapp.com`, a `whatsapp://` directo, o a variaciones de
formato) repetiría el error ya documentado en issue 301 -- el problema no está en lo que PaqueteX
genera, está en si Android, en ese dispositivo puntual, tiene a WhatsApp registrada como manejador
verificado de esos dominios en el momento del clic.

---

## Caso escritorio: PWA de Chrome de WhatsApp Web

**Contexto de esta sección:** el cliente reporta que en su computador de escritorio sí tiene
WhatsApp instalado como PWA de Chrome -- instalada desde `web.whatsapp.com`, que es la única forma
posible (WhatsApp no ofrece una PWA de `wa.me`). Quiere que el enlace de WhatsApp de PaqueteX abra
esa PWA ya instalada en vez de una pestaña de navegador. Esta sección investiga el mecanismo oficial
de Chrome/Google para eso -- "link capturing" / "navigation capturing" -- independiente de todo lo
ya investigado arriba sobre Android/Meta.

**Nota de metodología:** igual que en la sección anterior, varias páginas de
`developer.chrome.com` son SPAs renderizadas por JavaScript -- `curl` directo solo trae el shell
vacío, no el contenido. Se usó un lector que renderiza y extrae el texto real servido en producción
(`r.jina.ai` como proxy de lectura sobre la URL oficial exacta, 2026-09-03) para poder citar el
texto literal de cada artículo -- no es contenido de terceros, es el HTML/markdown que
`developer.chrome.com` sirve, solo pasado por un extractor de texto. Donde se cita así, la URL
citada sigue siendo la de `developer.chrome.com`/`chromeos.dev`/`support.google.com`, nunca la del
proxy. Adicionalmente, dos URLs pedidas explícitamente en el encargo ya no existen:
`developer.chrome.com/docs/web-platform/best-practices/launch-handler` y
`.../best-practices/url-handlers` devuelven HTTP 404 -- el contenido se movió (ver Pregunta 1 y
Pregunta 6 para las URLs vigentes encontradas en su reemplazo).

### 1. Cómo funciona el link capturing hoy -- y qué le pasó al mecanismo viejo

El mecanismo vigente se llama **navigation capturing** y está documentado en
[developer.chrome.com/docs/capabilities/pwa-navigation-management](https://developer.chrome.com/docs/capabilities/pwa-navigation-management)
(publicado 19 agosto 2025). El artículo describe un proceso de 4 pasos que corre el navegador cada
vez que el usuario hace clic en un link:

> 1. **Determine if the navigation is capturable**: In general, a navigation is considered
>    _capturable_ if it creates a new frame and does not open in an auxiliary browsing context.
> 2. **Identify a controlling PWA**: If the navigation is capturable, the browser tries to find a
>    PWA that "controls" the URL (falls within the scope defined in its Web App Manifest).
> 3. **Verify user preference**: If a controlling PWA is found, the browser checks user preference.
>    If the user hasn't opted out in the app settings, the PWA launches; otherwise, the link opens
>    in a new browser tab.
> 4. **Launch the PWA**: The browser launches the PWA using the Launch Handling Algorithm.

Esto responde directamente la pregunta 1 del encargo: lo que determina si un `<a href>` normal de
*cualquier* página abre la PWA en vez de una pestaña es exactamente el paso 2 (¿la URL cae dentro
del `scope` del manifest de alguna PWA instalada?) combinado con el paso 3 (¿el usuario no
desactivó la captura para esa app?). No hay ningún atributo del `<a>`, `rel`, o `target` que
participe -- el mecanismo es enteramente del lado del navegador + manifest, invisible al HTML del
link.

**El mecanismo viejo (`capture_links` en el manifest) está deprecado y nunca llegó a Windows/macOS/
Linux.** Documentado en
[developer.chrome.com/docs/web-platform/declarative-link-capturing](https://developer.chrome.com/docs/web-platform/declarative-link-capturing):
la página lo marca explícitamente como no lanzado ("isn't launching in its current state"),
reemplazado por la combinación Launch Handler API + navigation capturing descrita arriba. Su origin
trial expiró el 30 de marzo de 2022 (Chromium ≤97) y, mientras existió, **el soporte real era
solo ChromeOS** -- "Windows, macOS, and Linux is in progress" (nunca se completó bajo esa API). Los
valores que tenía (`"none"`, `"new-client"`, `"existing-client-navigate"`, y un
`"existing-client-event"` que se propuso pero nunca se implementó) son historia, no algo vigente
para diseñar nada hoy -- se documentan aquí solo porque el encargo pregunta por ellos
explícitamente (Pregunta 5).

**Lo que sí sigue vigente y es developer-facing hoy es el `launch_handler` manifest member**
(Launch Handler API), documentado en
[developer.chrome.com/docs/web-platform/launch-handler/](https://developer.chrome.com/docs/web-platform/launch-handler/)
y resumido también dentro del artículo de navigation-management. Su único sub-campo, `client_mode`,
decide *cómo* se lanza la PWA una vez que ya se decidió lanzarla (pasos 1-3 arriba) -- no decide
*si* se captura:

> - `focus-existing`: To handle the link in an existing app window, like a PWA that is already
>   running in standalone mode.
> - `navigate-existing`: [...] the most recently interacted with, browsing context in a web app
>   window is navigated to the launch's target URL.
> - `navigate-new`: [...] a new browsing context is created in a web app window to load the
>   launch's target URL.
> - `auto` (default si no se declara `launch_handler`): "the user agent decides the most sensible
>   context" -- móvil típicamente reutiliza cliente existente, escritorio típicamente abre nuevo.

Disponible desde Chrome 110, pero "becomes much more useful with the navigation capturing update"
(Chrome 139) -- es decir, antes de Chrome 139 en desktop casi no importaba porque casi nada llegaba
a activarlo por default.

### 2. ¿Scope exige mismo origen? -- respuesta: sí, confirmado, y es la pregunta que decide todo

El paso 2 citado arriba dice literalmente "falls within the scope defined in its Web App Manifest",
enlazando a la definición de `scope` de MDN. La confirmación más fuerte y más *oficial de Google*
de que ese scope exige mismo origen no viene de un enunciado suelto, sino de la razón de ser de otra
API entera: [developer.chrome.com/docs/capabilities/scope-extensions](https://developer.chrome.com/docs/capabilities/scope-extensions)
(Web App Scope Extensions API) existe **específicamente** para saltarse esa restricción:

> The Scope Extensions API allows web apps to overcome some of the challenges that the
> same-origin policy imposes on this type of site architecture.

Es decir: por default, el `scope` de una PWA está limitado a su propio origen -- si no lo estuviera,
no habría ningún "challenge" que esta API tuviera que resolver. Esto coincide con el algoritmo
normativo del spec del Web App Manifest
([w3.org/TR/appmanifest](https://www.w3.org/TR/appmanifest/), sección "process the scope member" /
"within scope"), que define una URL como "within scope" de un `scope` dado solo si es del mismo
origen que `scope` **y** su path empieza con el path de `scope` -- el spec que Chrome implementa,
citado aquí como confirmación normativa adicional a la de `developer.chrome.com`, no como
reemplazo de ella.

**Aplicado al caso concreto:** `wa.me`, `api.whatsapp.com` y `web.whatsapp.com` son **tres orígenes
distintos** (esquema+host+puerto no coinciden entre ninguno de los tres). La PWA instalada por el
cliente se instaló desde `web.whatsapp.com`, así que su `scope` -- sea cual sea el path exacto
declarado en su manifest -- está anclado a ese origen por la restricción de mismo-origen de arriba.
Ningún link a `wa.me/<numero>` o `api.whatsapp.com/send?phone=<numero>` puede caer dentro de ese
scope bajo el mecanismo default, sin importar el path.

**Sobre la pregunta de si Chrome evalúa antes o después de seguir el redirect 302 de `wa.me`:**
ninguno de los tres artículos oficiales consultados (`pwa-navigation-management`,
`declarative-link-capturing`, `scope-extensions`) menciona redirects en ningún punto -- se buscó
explícitamente y no hay una sola mención. Esto es un vacío real de la documentación, igual que el
que ya se anotó en la sección anterior para WebViews. **Pero en este caso el vacío no cambia la
respuesta:** el redirect de `wa.me` no lleva a `web.whatsapp.com` -- lleva a `api.whatsapp.com`
(confirmado por observación directa en la sección 1 de este mismo archivo, arriba). Así que incluso
bajo la lectura más generosa posible (que Chrome evaluara el scope *después* de seguir el
redirect, algo que ningún documento afirma), el destino final seguiría siendo un origen distinto a
`web.whatsapp.com`. La hipótesis del encargo queda **confirmada**: no puede activarse, por origen
distinto, en ningún escenario del mecanismo default.

**Evidencia directa adicional (2026-09-03, no solo teoría):** se probó si Meta publica el archivo
que un mecanismo cross-origin *sí* exigiría (ver Pregunta 6) -- `https://api.whatsapp.com/
.well-known/web-app-origin-association` responde **HTTP 404** (no existe el archivo). `wa.me` no
sirve nada estático en esa ruta -- redirige (HTTP 302) hacia el resolvedor de deep links de la app
(`api.whatsapp.com/resolve/?deeplink=...&not_found=1`), consistente con que `wa.me` es un
redirector puro, no un host de contenido propio. No hay evidencia de que Meta haya configurado
ninguna asociación cross-origin entre `wa.me`/`api.whatsapp.com` y la PWA de `web.whatsapp.com`.

### 3. Qué debe activar el usuario -- el ajuste tiene nombre distinto según el sistema operativo

**Windows / macOS / Linux (Chrome 139+, el caso del cliente si su escritorio no es ChromeOS):** el
artículo oficial solo dice, en el paso 3 citado arriba, "if the user hasn't opted out in the app
settings" -- **sin nombrar el toggle exacto**. Se buscó el nombre preciso en la página oficial de
soporte de Google,
[support.google.com/chrome/answer/9658361](https://support.google.com/chrome/answer/9658361)
("Use web apps"), sección "Manage web app settings":

> 1. Click on the app in your dock or desktop. 2. At the top right of the app window, select
> **More**. 3. Select **App info** and then **Settings**. 4. Select the setting you want to
> update.

Esa es la ruta oficial confirmada (abrir la PWA → menú de 3 puntos → **App info** → **Settings**),
pero el texto de ayuda de Google **no nombra el toggle en sí** -- se queda en "select the setting
you want to update", genérico. No se encontró ninguna página oficial de `developer.chrome.com` ni
de `support.google.com` que dé el nombre literal del control para Windows/macOS/Linux. Esto se
anota como vacío de documentación, no se rellena con nombres no confirmados.

**ChromeOS sí tiene el nombre documentado explícitamente**, pero es un mecanismo *más viejo y
separado* (no la navigation-capturing de Chrome 139): en
[chromeos.dev/en/posts/customize-pwa-window-launch](https://chromeos.dev/en/posts/customize-pwa-window-launch)
(blog oficial de Google para ChromeOS):

> ChromeOS 98 introduces Link Capturing as a user preference which allows users to customize how to
> open supported in-scope links: in the Chrome browser or in the installed PWA. [...] By default,
> links are set to open in the Chrome browser. [...] In the ChromeOS Settings app, a user can go to
> the "Apps" menu, select "Manage your apps" and find the app they're interested in (your PWA).
> Under **"Opening supported links"**, there are radio button options for opening links in the app
> or in the Chrome browser.

Nombre exacto vigente en ChromeOS hoy: **"Opening supported links"**, con dos opciones de radio
button. Existe desde ChromeOS 98 (~enero 2022) -- mucho antes que la navigation-capturing de Chrome
139 para los otros sistemas operativos.

**Nota importante que el encargo no anticipaba:** el *default* está invertido entre plataformas.
En ChromeOS (mecanismo viejo, por-app, opt-in): default es "open in Chrome browser", el usuario
tiene que activar manualmente "open in app". En Windows/macOS/Linux con Chrome 139+ (mecanismo
nuevo, navigation capturing, opt-out): el default ya es capturar automáticamente -- "Links will
only fall back to a browser tab if the PWA isn't installed or if the user has opted out." (mismo
artículo de `pwa-navigation-management` citado en la Pregunta 5). Es decir, en el sistema operativo
más probable del cliente (Windows o macOS de escritorio, no un Chromebook), **si el link cayera
dentro del scope, no haría falta que el cliente activara nada** -- el problema real, confirmado en
la Pregunta 2, es que el link de PaqueteX nunca cae dentro del scope, así que este ajuste es
irrelevante en la práctica para el caso concreto.

### 4. Diferencias de plataforma y versión mínima

- **Windows, macOS, Linux:** navigation capturing (el mecanismo nuevo, opt-out) disponible **desde
  Chrome 139** -- "This new behavior is available from Chrome 139 for Windows, Mac, and Linux"
  ([pwa-navigation-management](https://developer.chrome.com/docs/capabilities/pwa-navigation-management)).
  Chrome 139 llegó a estable a mediados de 2025; a la fecha de esta investigación (2026-09-03) el
  canal estable de Chrome ya va muy por delante de esa versión, así que cualquier Chrome de
  escritorio actualizado del cliente ya la tiene.
- **ChromeOS:** el artículo de navigation-management, a la fecha de su publicación (19 agosto
  2025), dice explícitamente "with ChromeOS support coming in a future release" -- es decir, el
  mecanismo *nuevo* (Chrome 139) todavía no había llegado a ChromeOS en esa fecha. ChromeOS sí
  tiene, por separado, su propio mecanismo de link capturing desde ChromeOS 98 (ver Pregunta 3) --
  son dos generaciones distintas de la misma idea, documentadas en dos artículos distintos.
- **El mecanismo viejo deprecado** (`capture_links`,
  [declarative-link-capturing](https://developer.chrome.com/docs/web-platform/declarative-link-capturing))
  solo funcionó de verdad en ChromeOS; para Windows/macOS/Linux quedó registrado como "in progress"
  y nunca se completó bajo esa API -- se saltó directo al reemplazo (Launch Handler + navigation
  capturing).
- No se encontró ninguna entrada de changelog/release-notes específica de `developer.chrome.com/
  blog` para el lanzamiento de navigation capturing en Chrome 139 (se revisó el post
  `chrome-139-beta` y no menciona el feature en su listado) -- el anuncio detallado vive en el
  artículo de capabilities citado, no en el blog de release notes.

### 5. Comportamiento por defecto si el usuario no configuró nada

Depende de qué generación del mecanismo aplica, y son opuestas:

- **Windows/macOS/Linux, Chrome 139+ (navigation capturing, vigente):** default es **capturar
  automáticamente**. Cita exacta: "The new, unified approach for navigation capturing,
  automatically opens links in their corresponding installed PWA. Links will only fall back to a
  browser tab if the PWA isn't installed or if the user has opted out."
  ([pwa-navigation-management](https://developer.chrome.com/docs/capabilities/pwa-navigation-management)).
  No se documenta ningún diálogo de primera vez ni prompt -- el artículo no menciona ninguno, y se
  buscó explícitamente.
- **ChromeOS 98+ (mecanismo viejo, todavía el vigente ahí hasta que llegue la actualización):**
  default es **lo contrario**, abrir en el navegador -- "By default, links are set to open in the
  Chrome browser" ([chromeos.dev](https://chromeos.dev/en/posts/customize-pwa-window-launch)),
  requiere que el usuario cambie el radio button a mano.
- **Valores del `capture_links` deprecado** (solo por completitud, pregunta explícita del encargo --
  esta API no es la vigente, ver Pregunta 1): `"none"` (default de esa API vieja -- "No link
  capturing; links clicked leading to this PWA scope navigate as normal"), `"new-client"` ("Each
  clicked link opens a new PWA window at that URL"), `"existing-client-navigate"` ("The clicked
  link opens in an existing PWA window, if one is available, or in a new window if it's not" --
  con advertencia explícita de posible pérdida de datos por navegar una ventana existente), y
  `"existing-client-event"` (propuesto, nunca implementado). Todos documentados en
  [declarative-link-capturing](https://developer.chrome.com/docs/web-platform/declarative-link-capturing).

### 6. Mecanismos para que el DESARROLLADOR declare captura cross-origin (informativo -- WhatsApp, no PaqueteX)

Existen dos APIs de Chrome, ninguna activa por default, que permitirían -- solo si **ambos lados**
cooperan -- que un origen distinto capture links hacia una PWA:

**(a) Web App Scope Extensions** --
[developer.chrome.com/docs/capabilities/scope-extensions](https://developer.chrome.com/docs/capabilities/scope-extensions).
La PWA declara en su manifest los orígenes adicionales (`"scope_extensions": [{"origin":
"https://ejemplo.com"}]`), pero eso no basta: "Each of the listed origins confirms the association
with the web app using a `/.well-known/web-app-origin-association` configuration file" -- el otro
origen (en este caso hipotético, `wa.me` o `api.whatsapp.com`) tendría que publicar ese archivo
autorizando explícitamente a `web.whatsapp.com`. Estado del soporte: origin trial en Chrome 121-126;
navegación cross-origin-en-scope ya soportada en Windows/macOS/Linux, pero la integración con link
*capturing* específicamente aparece documentada como más limitada/ChromeOS. No es una API estable y
lista para producción en todas las plataformas.

**(b) PWAs as URL Handlers** --
[developer.chrome.com/docs/capabilities/pwa-url-handler](https://developer.chrome.com/docs/capabilities/pwa-url-handler).
Mecanismo hermano, diseñado por el equipo de Microsoft Edge, con el mismo principio de doble opt-in
(`"url_handlers"` en el manifest de la PWA + archivo `web-app-origin-association` en el origen
externo). Confirmado **experimental y detrás de flag** -- "To experiment with PWAs as URL Handlers
locally, without an origin trial token, enable the `#enable-desktop-pwas-url-handling` flag in
`about://flags`" -- no está activo por default en Chrome estable. Esta es, probablemente, la URL
que el encargo buscaba bajo `.../best-practices/url-handlers` (404) -- el contenido vive ahora en
`docs/capabilities/pwa-url-handler`, no en `best-practices/`.

Ninguna de las dos aplica al caso de PaqueteX: ambas exigen que el origen externo (`wa.me`/
`api.whatsapp.com`) publique el archivo de asociación -- eso es responsabilidad exclusiva de Meta,
no de PaqueteX, y la comprobación directa de la Pregunta 2 (`api.whatsapp.com/.well-known/
web-app-origin-association` → HTTP 404) no encontró evidencia de que Meta lo haya hecho.

---

### Conclusiones de esta sección

**(a) ¿`web.whatsapp.com/send?phone=...` puede activar el link capturing de la PWA ya instalada?**
**Sí, incondicionalmente, en el escritorio del cliente** -- porque ese es el origen exacto desde el
que se instaló la PWA, así que cualquier URL bajo `https://web.whatsapp.com/...` cae dentro de su
`scope` por definición (mismo origen, y `send` cuelga del mismo path raíz). Con Chrome 139+ en
Windows/macOS/Linux el default ya es capturar automáticamente sin que el usuario configure nada
(Pregunta 5). Fuente:
[developer.chrome.com/docs/capabilities/pwa-navigation-management](https://developer.chrome.com/docs/capabilities/pwa-navigation-management).
**`wa.me` o `api.whatsapp.com` nunca pueden activarlo** -- son orígenes distintos, y el scope de
manifest exige mismo origen (Pregunta 2), confirmado por
[developer.chrome.com/docs/capabilities/scope-extensions](https://developer.chrome.com/docs/capabilities/scope-extensions)
y por el spec [w3.org/TR/appmanifest](https://www.w3.org/TR/appmanifest/).

**(b) ¿Qué debe revisar/activar el cliente?** En su Chrome de escritorio actualizado (Windows o
macOS, casi seguro no ChromeOS dado que dice "computador"), **nada** -- el opt-out (Pregunta 5) es
la excepción, no la regla, desde Chrome 139. Si por algún motivo no capturara, el camino de
verificación oficial es abrir la PWA → menú **⋮ (More)** → **App info** → **Settings** (Pregunta 3,
[support.google.com/chrome/answer/9658361](https://support.google.com/chrome/answer/9658361)) y
revisar ahí el control de links -- Google no publica el nombre exacto del toggle para esta
plataforma, a diferencia de ChromeOS donde sí se llama, documentado, **"Opening supported links"**.
Esto solo importa si el link ya apunta a `web.whatsapp.com` -- apuntando a `wa.me` no hay ajuste de
usuario que lo arregle, por (a).

**(c) ¿El mismo link puede servir para Android y para este caso de escritorio? Son irreconciliables
bajo un solo dominio.** Android exige `wa.me`/`api.whatsapp.com` (App Links de Meta, verificado en
la sección anterior de este archivo); el escritorio con PWA instalada exige `web.whatsapp.com`
(scope same-origin, Pregunta 2 de esta sección) -- y ya está verificado en vivo (issue 304) que
`web.whatsapp.com` no abre nada en Android ni en un escritorio sin la PWA instalada. No existe un
dominio único que sirva a los dos casos con el mecanismo estándar de Chrome/Android -- las dos
únicas vías cross-origin que existen (Scope Extensions, PWA URL Handlers, Pregunta 6) dependen de
que **Meta** publique un archivo de asociación en `wa.me`/`api.whatsapp.com`, y no hay evidencia de
que lo haya hecho (HTTP 404 verificado). **Implicación para PaqueteX:** no hay una solución de un
solo link. Las opciones reales son (i) mantener `wa.me` -- correcto para Android/iOS con app nativa,
funciona igual como página web de fallback en cualquier escritorio sin PWA, pero nunca capturará la
PWA de escritorio aunque esté instalada; o (ii) detectar el caso -- por ejemplo, servir
`web.whatsapp.com/send?phone=...` condicionado a un cliente de escritorio (por `User-Agent` u otra
señal), sabiendo que eso reintroduce exactamente el problema que cerró el issue 304 para todo
dispositivo que no tenga la PWA instalada (la mayoría). No hay una tercera opción documentada por
Chrome o Meta que evite ese trade-off.
