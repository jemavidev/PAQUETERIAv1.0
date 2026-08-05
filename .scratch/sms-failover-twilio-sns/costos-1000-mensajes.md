# Comparativo de costos: SMS y WhatsApp — LIWA vs. Twilio vs. AWS

**Fecha de la investigación:** 2026-08-05
**Nota:** todos los precios listados abajo son precios **públicos**, consultados directamente en las
páginas oficiales de cada proveedor (o en los archivos CSV/rate-cards que esas mismas páginas
publican) en la fecha indicada. Los proveedores de mensajería cambian tarifas sin previo aviso —
antes de usar estas cifras para presupuestar, revalidar contra la fuente el día del cálculo.

**Tasa de cambio usada para las columnas en COP:** ~3.200 COP/USD. Es un valor de referencia
redondeado; la tasa de mercado el 2026-08-05 osciló entre 3.181,99 y 3.204,51 COP/USD según la
fuente consultada (ver [dolarhoy.co](https://www.dolarhoy.co/), [Bloomberg Línea
USDCOP](https://www.bloomberglinea.com/quote/USDCOP:CUR/)). Ninguna de las páginas de pricing de los
3 proveedores da precios nativos en COP para SMS/WhatsApp (todas facturan en USD), así que la
columna COP es siempre una conversión aproximada, no una cifra publicada por el proveedor.

---

## Tabla comparativa (costo de enviar 1000 mensajes)

| Proveedor | Canal | Precio unitario | Costo 1000 mensajes (USD) | Costo aprox. (COP, ~3.200/USD) | Notas |
|---|---|---|---|---|---|
| LIWA | SMS | **No publicado** | — | — | Sin página pública de tarifas; requiere contacto comercial. |
| LIWA | WhatsApp | **No publicado** | — | — | LIWA sí ofrece un producto de WhatsApp (plataforma omnicanal, vía liwaempresas.com), pero sin precio público. |
| Twilio | SMS (Colombia, todos los operadores) | $0.0525 / mensaje | $52.50 | ≈ $168.000 | Un solo precio para todos los operadores colombianos (Claro, Movistar, Tigo, Avantel, ETB). |
| Twilio | WhatsApp — Utility (categoría real de uso: "tu paquete llegó") | $0.005 (Twilio) + $0.0008 (Meta) = $0.0058 / mensaje | $5.80 | ≈ $18.560 | Aplica cuando el mensaje es iniciado por el negocio (fuera de la ventana de servicio de 24h); dentro de la ventana el fee de Meta es $0. |
| Twilio | WhatsApp — Authentication | $0.005 + $0.0008 = $0.0058 / mensaje | $5.80 | ≈ $18.560 | Mismo fee de Meta que utility para Colombia. |
| Twilio | WhatsApp — Marketing | $0.005 + $0.0125 = $0.0175 / mensaje | $17.50 | ≈ $56.000 | Fee de Meta ~2x utility para Colombia. |
| AWS | SMS (SNS / End User Messaging, todos los operadores) | $0.05087 / mensaje | $50.87 | ≈ $162.784 | Precio único listado ("All Networks"); no hay distinción publicada Transactional/Promotional por país en la tabla actual. |
| AWS | WhatsApp (End User Messaging Social) — Utility | $0.005 (AWS) + $0.0006 (Meta) = $0.0056 / mensaje | $5.60 | ≈ $17.920 | Sí tiene pricing público self-service (corrige la suposición de que requiere ventas — ver sección AWS). |
| AWS | WhatsApp — Authentication | $0.005 + $0.0006 = $0.0056 / mensaje | $5.60 | ≈ $17.920 | |
| AWS | WhatsApp — Marketing | $0.005 + $0.0096 = $0.0146 / mensaje | $14.60 | ≈ $46.720 | |

---

## 1. LIWA (liwa.co)

**Hallazgo principal: LIWA no publica una tabla de precios pública para su SMS gateway ni para
WhatsApp.** Esto es notable porque el código del proyecto (`liwa_sender.py`) sí usa un endpoint de
producción activo (`https://api.liwa.co/v2/sms/single`), lo que confirma que el producto existe
comercialmente — pero el acceso a precios parece ser vía cuenta/contrato negociado, no self-service
público.

Lo que se verificó directamente:

- `https://liwa.co/` — el sitio principal de LIWA se presenta hoy como un **operador móvil virtual
  (OMV) de consumo** en Colombia (planes de datos, minutos, eSIM, fibra óptica), registrado ante
  MinTIC (Registro OMV N.º 96002790, mencionado en un PDF regulatorio de LIWA:
  https://liwarepo.s3.us-west-2.amazonaws.com/regulatorio/terminos-y-condiciones-de-servicio.pdf).
  No tiene sección de "Desarrolladores" / API / mensajería empresarial en su navegación. Rutas
  candidatas probadas y devolvieron 404: `liwa.co/sms-masivos/`, `liwa.co/empresas/`.
- `https://liwaempresas.com/` ("LIWA Tech") — **esta sí es la línea de negocio B2B de LIWA** y
  confirma que **LIWA ofrece WhatsApp como producto** ("Plataforma Omnicanal WhatsApp", "Agentes IA
  para WhatsApp"), además de telefonía en la nube (PBX, números virtuales, troncales SIP). La página
  no muestra ninguna tarifa: el único llamado a la acción es "Agenda una demo gratis" / "Crear cuenta
  gratis" — es decir, pricing bajo demanda, no publicado.
- `https://register.liwa.co/` — apareció en resultados de búsqueda como "Liwa Empresas" con mención
  a "SMS Masivos, Call Blasting y API integration" entre sus servicios, pero el sitio no fue
  accesible durante esta investigación (fallo de conexión repetido) — no se pudo confirmar contenido
  ni precios directamente.

**Conclusión LIWA:** no hay cifra pública verificable de precio por SMS ni por mensaje de WhatsApp
contra fuente primaria. Ver sección de "Datos no confirmados" abajo.

## 2. Twilio (twilio.com)

### SMS saliente a Colombia (+57)

Fuente primaria: página de pricing por país
[https://www.twilio.com/en-us/sms/pricing/co](https://www.twilio.com/en-us/sms/pricing/co), y el
archivo CSV que esa misma página usa como fuente de datos estructurados:
[SMSPricing.csv](https://www.twilio.com/content/dam/twilio-com/pricing-data/en/csv/PMded94a0dae30eaaec0f115f22859bd38_SMSPricing.csv).

El CSV lista, para Colombia (ISO `CO`), un precio uniforme de **$0.0525 USD por mensaje/segmento**
para todos los operadores de destino: Claro, Movistar, Tigo, Avantel SAS, ETB (Empresa de
Telecomunicaciones de Bogotá) y "Other". Esta cifra fue corroborada por una búsqueda web
independiente que cita el mismo valor.

**Discrepancia detectada y aclarada:** al leer el HTML renderizado de la página
`twilio.com/en-us/sms/pricing/co` (en vez del CSV), aparece también un valor de **$0.0592** bajo el
rótulo "International Numbers — Outbound SMS". No fue posible confirmar a qué corresponde
exactamente ese segundo número (posiblemente una tarifa genérica de referencia para números de
origen internacionales, no específica al operador de destino en Colombia). Para este comparativo se
usó el valor del CSV ($0.0525) por ser el dato estructurado, explícitamente etiquetado por país y
operador de destino, que es lo que el proyecto necesita (costo de ENVIAR hacia números colombianos).

Notas operativas relevantes (misma fuente + guía regulatoria de Twilio para Colombia,
[twilio.com/en-us/guidelines/co/sms](https://www.twilio.com/en-us/guidelines/co/sms)):
- Colombia no soporta Sender ID alfanumérico.
- Long code doméstico no soportado; long code internacional es soportado pero "se sobrescribe con un
  short code" — para un remitente estable se requiere aprovisionar un short code dedicado (4-10
  semanas de trámite).
- Cargo adicional de "failed message processing fee": $0.001 USD, pero **solo se cobra sobre
  mensajes que terminan en estado "Failed"** — no aplica sobre los 1000 mensajes si se asumen
  exitosos.
- La página indica "additional carrier fees may apply" de forma genérica, pero no se encontró una
  cifra específica de carrier fee para Colombia en las fuentes accedidas (a diferencia de EE.UU.,
  donde Twilio sí publica carrier fees explícitos por operador).
- Número internacional (para tener remitente): desde $1.15 USD/mes
  (misma página de pricing).

### WhatsApp Business API vía Twilio hacia Colombia

Fuentes primarias:
- [twilio.com/en-us/whatsapp/pricing](https://www.twilio.com/en-us/whatsapp/pricing) — fee propio de
  Twilio.
- CSV de Meta fees por país que la misma página de Twilio publica para descarga:
  [WhatsAppPricing-pricing-details.csv](https://www.twilio.com/content/dam/twilio-com/pricing-data/en/WhatsAppPricing-pricing-details.csv).

**Modelo de precios vigente confirmado:** desde el **1 de julio de 2025**, Meta factura WhatsApp
Business Platform **por mensaje** (no por conversación de 24h como antes). Esto se confirmó
independientemente contra la documentación oficial de Meta para desarrolladores
([developers.facebook.com/documentation/business-messaging/whatsapp/pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing)),
que declara explícitamente: "Effective July 1, 2025, Meta charges on a per-message basis" — el
modelo anterior de "conversación" quedó deprecado (ver también, del lado de AWS,
[docs.aws.amazon.com/social-messaging/latest/userguide/charged-per-conversation.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/charged-per-conversation.html),
página titulada explícitamente "(Deprecated)").

Composición del costo por mensaje vía Twilio:
- **Fee de canal de Twilio:** $0.005 USD por mensaje, tanto entrante como saliente (fuente:
  twilio.com/en-us/whatsapp/pricing).
- **Fee de plantilla de Meta, pass-through de Twilio, específico para Colombia** (fuente: CSV de
  Twilio arriba):
  - Utility: **$0.0008 USD**
  - Authentication: **$0.0008 USD**
  - Marketing: **$0.0125 USD**
- El fee de Meta para plantillas **utility** no se cobra si el mensaje cae dentro de una ventana de
  servicio de 24h iniciada por el cliente (fuente: twilio.com/en-us/whatsapp/pricing). Para el caso
  de uso real de PaqueteX ("tu paquete llegó" — notificación iniciada por el negocio, sin mensaje
  previo del residente), esta ventana normalmente NO está abierta, así que el fee de Meta sí aplica.
- Requiere plantillas de mensaje pre-aprobadas por Meta (categoría utility/marketing/authentication
  se declara al someter la plantilla en la consola de Twilio) y un WhatsApp Sender verificado
  (número de WhatsApp Business, con proceso de verificación de negocio ante Meta) — no se encontró
  un cargo público adicional específico por ese setup en las páginas revisadas.

## 3. AWS

### SMS transaccional vía SNS / AWS End User Messaging hacia Colombia

Fuente primaria: la página oficial `aws.amazon.com/sns/pricing/` confirma que, **desde el 1 de
noviembre de 2024, los cargos de SMS de SNS se facturan bajo la marca "AWS End User Messaging"**
(cita textual: "Starting November 1, 2024, charges for SMS services will appear under AWS End User
Messaging on your AWS bill") y remite a
[aws.amazon.com/end-user-messaging/pricing/](https://aws.amazon.com/end-user-messaging/pricing/)
para las tarifas por país. Esa página, a su vez, publica un CSV descargable con el precio por país:
[End-User-Messaging-SMS-Prices.csv](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/business-applications/approved/documents/End-User-Messaging-SMS-Prices.ebc340b4d416d90832dd59629c4792b0deb6f8bc.csv).

Ese CSV (columnas: `ISO Country, Country Name, CarrierName, Number Type, Price ($USD)`) lista, para
`CO / Colombia / All Networks / All number types`: **$0.05087 USD por mensaje**.

Notas:
- La tabla actual **no distingue precio Transactional vs. Promotional por país** — es un precio único
  por destino/operador. El código del proyecto (`sns_sender.py`) marca los envíos como
  `AWS.SNS.SMS.SMSType: Transactional`, lo cual en el modelo de AWS afecta la prioridad de entrega y
  el tipo de contenido permitido, pero según la tabla de precios vigente no cambia el costo por
  mensaje hacia Colombia.
- La página vieja `aws.amazon.com/sns/sms-pricing/` sigue existiendo pero ya no muestra tabla
  granular por país en el contenido accedido (remite a usage reports); la fuente autoritativa actual
  es la página de End User Messaging enlazada arriba.
- Región: el código no fija una región AWS explícita para SNS. La tarifa por SMS de AWS End User
  Messaging es una lista global por país de destino (no varía por región de origen de la cuenta AWS
  usada para publicar), así que la ambigüedad de región en el código no afecta esta cifra —
  aclarado explícitamente porque no se pudo confirmar la región exacta contra el código.

### WhatsApp vía "AWS End User Messaging Social" hacia Colombia

**Corrección a la suposición del brief:** sí existe pricing público self-service para este producto
— no hace falta contactar ventas. Fuente primaria:
[aws.amazon.com/end-user-messaging/pricing/](https://aws.amazon.com/end-user-messaging/pricing/), que
enlaza dos CSVs oficiales:
- [AWS_WhatsApp_Meta_Fee CSV](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/business-applications/approved/documents/AWS_WhatsApp_Meta_Fee_7_2026.e7df1dc9019d2d3e1b5f78f4269218c883466dbd.csv)
- [AWS_WhatsApp_Meta_Fee_Volume_Tiers CSV](https://d1.awsstatic.com/onedam/marketing-channels/website/aws/en_US/business-applications/approved/documents/AWS_WhatsApp_Meta_Fee_Volume_Tiers_7_2026.bf291470d871e5247923449b3b3cf1a5643ab6bf.csv)

Composición del costo por mensaje:
- **AWS MessageFee:** $0.005 USD por mensaje saliente (global; excepción: India utility/authentication
  a $0.002 — no aplica a Colombia), y $0.001 USD por mensaje entrante (fuente: página de pricing
  arriba).
- **MetaTemplateMessageFee, específico para Colombia** (fuente: CSV `AWS_WhatsApp_Meta_Fee` arriba,
  archivo fechado 7/2026):
  - Utility: **$0.0006 USD**
  - Authentication: **$0.0006 USD**
  - Marketing: **$0.0096 USD**
  - "Authentication-International" y "Service": sin valor listado (`n/a`) en el archivo vigente.
- El mismo modelo por-mensaje (no por conversación) rige aquí desde el 1 de julio de 2025, confirmado
  por la documentación oficial de AWS:
  [docs.aws.amazon.com/social-messaging/latest/userguide/charged-per-message.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/charged-per-message.html)
  ("Starting on July 1 2025, AWS End User Messaging Social charges per message instead of per
  conversation for WhatsApp messages, inline with Meta's change").
- **Discrepancia entre Twilio y AWS para el mismo fee de Meta:** Twilio reporta $0.0008 (utility/auth)
  y AWS reporta $0.0006 para el mismo rubro y país. Ambos son pass-through del mismo rate card de
  Meta, pero la página de AWS aclara que factura el fee de Meta "aplicando la tasa de cambio INR→USD
  vigente al 1/7/2026" (cita de la página de pricing de AWS End User Messaging) — es decir, Meta
  publica su rate card base en rupias indias (INR) y cada proveedor lo convierte a USD en su propio
  ciclo/fecha, lo que explica la diferencia de centésimas de centavo entre Twilio y AWS. No es un
  error de esta investigación — es una diferencia real y esperable entre proveedores.
- Requiere una WhatsApp Business Account (WABA) vinculada vía Meta Business Manager y plantillas
  aprobadas por Meta, igual que con Twilio. No se encontró mención de cargo adicional de AWS por ese
  setup en las páginas revisadas.

---

## Datos no confirmados / requieren seguimiento

- **Precio de SMS de LIWA hacia números colombianos:** no se encontró página pública de tarifas.
  `liwa.co` se presenta hoy como operador móvil de consumo, sin sección de API/desarrolladores en su
  navegación; `liwaempresas.com` (línea B2B) tampoco publica tarifas, solo "agenda una demo". El
  endpoint usado en producción por el proyecto (`api.liwa.co/v2/sms/single`) confirma que el producto
  existe comercialmente, pero el precio parece depender de un contrato/cuenta negociada
  individualmente, no de una lista pública. **Acción sugerida:** pedir la tarifa directamente al
  contacto comercial de LIWA que gestiona la cuenta actual del proyecto (las credenciales
  `LIWA_ACCOUNT`/`LIWA_API_KEY` ya en uso implican que existe una relación comercial activa que
  debería tener una tarifa asociada, aunque no sea pública).
- **Precio de WhatsApp de LIWA:** se confirmó que el producto existe (plataforma omnicanal de
  WhatsApp vía liwaempresas.com), pero no hay tarifa pública. Mismo seguimiento sugerido que arriba.
- **`register.liwa.co`** apareció en resultados de búsqueda con mención a "SMS Masivos, Call Blasting
  y API integration", pero el sitio no respondió durante esta investigación (falla de conexión) — no
  se pudo confirmar su contenido directamente ni buscar tarifas ahí.
- **Twilio — origen exacto del valor $0.0592** que aparece en el HTML renderizado de
  `twilio.com/en-us/sms/pricing/co` bajo "International Numbers — Outbound SMS", en aparente
  contradicción con el valor $0.0525 del CSV oficial de la misma página para Colombia. Se usó $0.0525
  (el dato estructurado, explícitamente por país/operador) para todos los cálculos de este documento,
  pero valdría la pena confirmar contra la página en un navegador real (no vía fetch automatizado)
  cuál de los dos números es el que efectivamente se factura.
- **Carrier fee específico de Twilio para Colombia:** la página general de pricing menciona
  "additional carrier fees may apply" sin dar cifra para Colombia (a diferencia de EE.UU., donde sí
  hay carrier fees explícitos y documentados). No se encontró una tabla de carrier fees por país que
  cubriera Colombia en las fuentes accedidas.
- **Categoría "Service" de WhatsApp (mensajes de sesión / free-form) tanto en Twilio como en AWS:**
  ambas fuentes primarias muestran esta categoría sin cargo listado (gratis) en los datos vigentes a
  la fecha de esta investigación. Una búsqueda complementaria (no primaria) indica que Meta anunció
  que **a partir del 1 de octubre de 2026 empezará a cobrar por mensajes de "service"** enviados
  dentro de la ventana de 24h — esto es posterior a la fecha de esta investigación (2026-08-05) y NO
  se pudo confirmar contra una fuente primaria de Meta, Twilio o AWS que ya lo reflejara en un rate
  card público al momento de escribir este documento. Revisar de nuevo cerca de esa fecha.
- **Tasa de cambio USD/COP:** se usó ~3.200 COP/USD como valor de referencia redondeado (rango real
  observado el 2026-08-05: 3.181,99–3.204,51 COP/USD, ver
  [dolarhoy.co](https://www.dolarhoy.co/) y
  [Bloomberg Línea USDCOP](https://www.bloomberglinea.com/quote/USDCOP:CUR/)). No es una tasa
  oficial/TRM de Banco de la República verificada directamente contra su fuente — para uso
  presupuestal real, confirmar la TRM oficial del día.
- **Soporte de "Coexistence" (preservar historial) en Twilio y/o AWS:** Meta documenta de forma
  general que, al migrar un número activo en la app de consumo, "if you onboard via a partner who
  supports business app number onboarding, you will be able to use both the WhatsApp Business app
  and the partner's app concurrently, and your messaging history will be preserved"
  ([developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/)).
  Pero ni la documentación propia de Twilio
  ([twilio.com/docs/whatsapp/migrate-numbers-and-senders](https://www.twilio.com/docs/whatsapp/migrate-numbers-and-senders))
  ni la de AWS
  ([docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html))
  mencionan esta ruta para un número que viene de la app de consumo: ambas describen únicamente el
  camino de "elimina la cuenta primero". No se pudo confirmar contra fuente primaria de ninguno de
  los dos proveedores si ofrecen hoy la ruta de Coexistence para este escenario específico. Una
  fuente secundaria (blog de un competidor BSP, no citable como primaria) afirma que Twilio no la
  soporta, pero no se pudo verificar contra `twilio.com`. **Acción sugerida:** preguntar
  explícitamente a soporte de Twilio y de AWS, antes de borrar la cuenta del número actual, si
  soportan la ruta de Coexistence / "business app number onboarding" para este caso puntual.
- **Duración total de indisponibilidad del número durante toda la migración** (no solo el paso de
  borrado): la única cifra de tiempo encontrada en fuente oficial es "It may take up to 3 minutes for
  the disconnected number to become available" — y esa cifra cubre solo la ventana entre borrar la
  cuenta de consumo y que el número quede libre para re-registrarse
  ([developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/)).
  Ninguna fuente oficial revisada da una cifra de cuánto tiempo el número queda sin poder enviar ni
  recibir WhatsApp por ningún canal mientras se completa el registro del WABA y, si aplica, la
  verificación de negocio.
- **Duración general de Meta Business Verification (ruta estándar, no partner-led):** la única cifra
  encontrada ("varies by region and can take several weeks") viene de la documentación de Twilio
  parafraseando el proceso de Meta
  ([twilio.com/docs/whatsapp/self-sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up)), no de
  una página propia de Meta con ese dato explícito — las dos páginas de Meta consultadas directamente
  para este dato
  ([facebook.com/business/help/1095661473946872](https://www.facebook.com/business/help/1095661473946872)
  y
  [developers.facebook.com/documentation/development/release/business-verification](https://developers.facebook.com/documentation/development/release/business-verification))
  no devolvieron un tiempo explícito de procesamiento en el contenido accedido.
- **Facturación en USD como requisito de AWS End User Messaging Social:** apareció en un hilo de la
  comunidad AWS re:Post (foro, no documentación oficial) la afirmación de que el servicio "currently
  only supports WhatsApp Business Accounts that are billed in U.S. dollars" — no se encontró esa
  restricción confirmada en las páginas oficiales de AWS revisadas
  (`getting-started-whatsapp.html`, `managing-phone-numbers_body.html`,
  `whatsapp-business-account.html`). Queda como dato no confirmado contra fuente primaria.
- **Costo de setup de Twilio para WhatsApp Senders:** no se encontró en
  [twilio.com/en-us/whatsapp/pricing](https://www.twilio.com/en-us/whatsapp/pricing) ni en
  [twilio.com/en-us/pricing](https://www.twilio.com/en-us/pricing) una declaración explícita tipo "no
  hay costo de setup" específica para el registro de un WhatsApp Sender — solo lenguaje general de
  "pay-as-you-go" y "no contracts" para la plataforma Twilio en conjunto. Tampoco se encontró mención
  de un cargo, así que lo más probable es que no lo haya, pero no hay una frase explícita que lo
  confirme para este producto puntual.

---

## Migrar un número de WhatsApp Business ya activo a Twilio/AWS

**Fecha de esta sub-investigación:** 2026-08-05. Mismo caveat que arriba: verificar contra la fuente
el día de la ejecución real, ya que estos flujos de producto cambian con frecuencia.

### Twilio

**Proceso vigente (nombre actual de la sección):** Twilio Console → **Messaging → Senders → WhatsApp
Senders** → botón **"Create new sender"**
([twilio.com/docs/whatsapp/self-sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up)). Un
WhatsApp Sender es "a phone number associated with a WhatsApp Business Account (WABA)" que se puede
usar con las APIs de Twilio (misma fuente).

Hay dos rutas de registro documentadas, según el tipo de cliente
([twilio.com/docs/whatsapp/migrate-numbers-and-senders](https://www.twilio.com/docs/whatsapp/migrate-numbers-and-senders)):
- **Cliente directo:** flujo de **Self Sign-up** dentro de la Twilio Console.
- **ISV (revendedor/plataforma):** debe unirse al **Tech Provider program** y usar **Embedded
  Signup** dentro de su propia aplicación.

**Requisitos previos** (fuente:
[twilio.com/docs/whatsapp/self-sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up)):
- Cuenta de Twilio creada y **upgradeada** (pagada) vía el botón "Upgrade" de la Console.
- Acceso de **administrador con permisos completos** al Meta Business Portfolio. Si la empresa no
  tiene uno, se puede crear durante el mismo flujo de Self Sign-up, pero entonces "you'll need to
  complete Meta business verification before you can move into production."
- Un número de teléfono (de Twilio o propio) que cumpla los requisitos de compatibilidad de WhatsApp
  y que **no esté ya registrado en WhatsApp**.

**Si el número YA está activo en WhatsApp Messenger o en la app de consumo WhatsApp Business** (fuente:
[twilio.com/docs/whatsapp/migrate-numbers-and-senders](https://www.twilio.com/docs/whatsapp/migrate-numbers-and-senders),
sección "Migrate phone numbers from WhatsApp or WhatsApp Business App"):
- Cita textual: **"Delete the WhatsApp account to make your phone number available for the WhatsApp
  Business Platform with Twilio."**
- Cita textual, consecuencia directa: **"You won't be able to continue using WhatsApp or WhatsApp
  Business App with the same phone number."**
- Esta misma página no menciona una ruta alterna de "Coexistence" (ver advertencia sobre esto en la
  sección de riesgos abajo y en "Datos no confirmados").

**Si el número viene de otro BSP / otra plataforma WhatsApp Business Platform** (mismo documento,
sección de migración entre proveedores) — este NO es el caso de PaqueteX hoy, pero se documenta para
contraste:
- Requiere Meta Business Portfolio activo y verificado, WABA de origen aprobada, y un método de pago
  válido en la cuenta de origen.
- Hay que entrar al WhatsApp Manager y **desactivar la verificación en dos pasos (2FA)** del número
  antes de migrar.
- Al completar el registro en Twilio, se migran: display name, messaging tier, quality rating, estatus
  OBA y las plantillas de mensaje — pero las plantillas se **duplican, no se transfieren**, y quedan
  con calificación `UNKNOWN` durante 24 horas; las plantillas rechazadas hay que recrearlas y
  reenviarlas.
- Un cambio de región de localización de datos puede tardar **hasta 15 minutos** en aplicarse.

**Verificación de negocio y Display Name:**
- El **Meta Business Manager** es obligatorio: "each business or brand must have a Meta Business
  Manager"
  ([twilio.com/docs/whatsapp/tutorial/whatsapp-business-account](https://www.twilio.com/docs/whatsapp/tutorial/whatsapp-business-account)).
  Sin Business Verification completada, en la vista de conversación solo se muestra el número de
  teléfono; con verificación completada, se muestra el display name en la lista de chats y en los
  hilos (misma fuente).
- **Tiempo de Business Verification, según la documentación de Twilio:** "Meta's processing time for
  business verification varies by region and can take **several weeks**"
  ([twilio.com/docs/whatsapp/self-sign-up](https://www.twilio.com/docs/whatsapp/self-sign-up)). No es
  una cifra exacta ni viene de una página propia de Meta con ese dato explícito (ver "Datos no
  confirmados").
- **Official Business Account (check verde):** requiere evidencia de que el negocio es "well-known
  and recognized by consumers" (artículos, blog posts, reseñas independientes); la aprobación es
  discrecional de Meta, sin criterios públicos, y se evalúa **por cada WhatsApp Sender individual**
  ([twilio.com/docs/whatsapp/tutorial/whatsapp-business-account](https://www.twilio.com/docs/whatsapp/tutorial/whatsapp-business-account)).

**Costo de setup aparte del cobro por mensaje:** no se encontró, en
[twilio.com/en-us/whatsapp/pricing](https://www.twilio.com/en-us/whatsapp/pricing) ni en
[twilio.com/en-us/pricing](https://www.twilio.com/en-us/pricing), un cargo explícito de configuración
o registro de WhatsApp Sender — solo lenguaje general de "pay‑as‑you‑go pricing" y "no contracts".
Ver matiz en "Datos no confirmados" (no hay una frase que lo confirme como "$0" para este producto
puntual, solo ausencia de mención de cobro).

### AWS (End User Messaging Social)

**Proceso vigente** (fuente:
[docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html),
sección "Sign up through the console"):
1. Abrir la consola de AWS End User Messaging Social
   ([console.aws.amazon.com/social-messaging/](https://console.aws.amazon.com/social-messaging/)) →
   **Business accounts** → **Link business account** → **Launch Facebook portal** (abre login de
   Meta).
2. Iniciar sesión con las credenciales de Facebook/Meta de la cuenta que administra el WABA.
3. Elegir o crear la **Meta Business account**.
4. Elegir un WABA existente o crear uno nuevo, y elegir/crear el **WhatsApp Business Profile**
   (display name, categoría, descripción, sitio web — el display name "is reviewed by Meta and must
   comply with WhatsApp display name rules").
5. Registrar el número de teléfono y verificarlo por **SMS o llamada de voz (OTP)**.
6. Configurar un **destino de eventos** (tema de Amazon SNS o instancia de Amazon Connect Customer):
   la documentación marca esto como obligatorio con la nota **"To be able to respond to customer
   messages, you must enable Message and event publishing"** — es decir, sin este paso el número
   puede quedar sin forma de recibir/procesar mensajes entrantes vía la plataforma.

**Requisitos previos** (misma fuente, sección "Prerequisites"):
- Una **Meta Business Account** (se puede crear durante el flujo si no existe).
- Un **WhatsApp Business Account (WABA)** creado con Meta, con un Business Manager account vinculado.
- Ceder el control del WABA a AWS: **"You must provide control of your WABA to us. At your request,
  we will transfer control of your WABA back to you in a reasonable and timely manner using the
  methods Meta makes available to us."**
- Un número que pueda recibir SMS o una llamada de voz para el OTP.
- Si se está **importando un WABA existente** (no necesariamente desde la app de consumo, sino desde
  otro uso previo de la API), se necesitan los **PINs de verificación en dos pasos de todos los
  números** asociados a esa WABA.

**Si el número YA está activo en WhatsApp Messenger o en la app de consumo WhatsApp Business** — cita
textual, listada como prerrequisito explícito: **"To use a phone number that's already in use with
the WhatsApp Messenger application or WhatsApp Business application, you must delete it first."**
(misma fuente,
[getting-started-whatsapp.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html)).
No se documenta, en esta página ni en
[managing-phone-numbers_body.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/managing-phone-numbers_body.html),
una ruta de Coexistence para este escenario — incluso cuando la guía general de Meta sí describe esa
ruta como posible "vía un partner" (ver riesgos abajo).

**Verificación de negocio y Display Name:**
- Cita textual sobre revisión del display name: **"Once you complete registration, Meta performs a
  review of your display name. Meta sends you an email telling you whether the display name has been
  approved or rejected. If your display name is rejected, your per day messaging limit is lowered and
  you could be disconnected from WhatsApp."** (fuente:
  [getting-started-whatsapp.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/getting-started-whatsapp.html)).
  Para cambiar el display name después, "you have to create a ticket with Meta support" (misma
  fuente).
- Como siguiente paso tras completar el sign-up, la propia guía de AWS remite a completar **Business
  Verification** en
  [facebook.com/business/help/1095661473946872](https://www.facebook.com/business/help/1095661473946872)
  "when you're ready to start sending messages at scale" — sin dar aquí una cifra de tiempo propia de
  AWS (ver "Datos no confirmados").
- **Official Business Account (check verde):** AWS documenta los dos tipos de cuenta de WhatsApp —
  *Business Account* y *Official Business Account* — y aclara que el OBA "requires providing evidence
  that the business is well known and recognized by consumers, such as articles, blog posts, or
  independent reviews. Approval for a WhatsApp OBA is not guaranteed, even if the business provides
  the required documentation... WhatsApp does not publicly disclose the specific criteria they use to
  evaluate and approve applications" (fuente:
  [docs.aws.amazon.com/social-messaging/latest/userguide/whatsapp-business-account.html](https://docs.aws.amazon.com/social-messaging/latest/userguide/whatsapp-business-account.html)).
  Nada en esta página describe una transferencia automática de un estatus equivalente desde la app de
  consumo — el OBA se describe como propio de la plataforma Business.

**Costo de setup aparte del cobro por mensaje:** no se encontró mención de un cargo de configuración o
de cuenta en
[aws.amazon.com/end-user-messaging/pricing/](https://aws.amazon.com/end-user-messaging/pricing/); la
página solo detalla el AWS MessageFee ($0.005/mensaje saliente global, $0.001/mensaje entrante) y el
MetaTemplateMessageFee por país/categoría (ya cubiertos en la tabla comparativa arriba).

### Riesgos y advertencias comunes a ambos

- **Pérdida de historial de chat de la app de consumo:** confirmada explícitamente por Meta para la
  ruta estándar de borrar-y-registrar: **"If you delete your WhatsApp Business app phone number and
  then register it for use with Cloud API...your existing messaging history will be lost, and you
  will be unable to use that number with the WhatsApp Business app again, unless you deregister the
  number from Cloud API."**
  ([developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/](https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/migrate-existing-whatsapp-number-to-a-business-account/)).
  Meta documenta una ruta alterna donde el historial se preserva ("Coexistence" /
  [developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users/](https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/onboarding-business-app-users/),
  que además aclara que incluso en ese caso solo se sincronizan **"the most recent 6 months"** de
  chats, no el historial completo, y que requiere WhatsApp Business app **versión 2.24.17 o superior**
  del lado del negocio) — pero, como se detalla arriba, **ni la documentación propia de Twilio ni la
  de AWS revisadas describen ofrecer esta ruta** para un número que viene de la app de consumo. Dado
  esto, lo prudente operativamente es **asumir pérdida total del historial de chat** salvo que Twilio
  o AWS confirmen lo contrario por soporte directo antes de proceder (ver "Datos no confirmados").
  Nota adicional: el historial de la app de consumo, en cualquier caso, **nunca es accesible vía la
  API de la Business Platform** una vez migrado — ninguna fuente oficial revisada describe un
  mecanismo para que el historial pre-migración quede consultable vía API, ni siquiera bajo
  Coexistence (ahí solo se sincroniza hacia la app espejo, no hacia la API del BSP).
- **Indisponibilidad del número durante la migración:** confirmada para la ventana puntual de borrado
  ("up to 3 minutes" para que el número quede libre tras eliminar la cuenta de consumo — misma fuente
  de Meta citada arriba), pero **no hay cifra oficial de cuánto tiempo el número queda sin poder
  enviar/recibir WhatsApp por ningún canal** mientras se completa el registro del WABA y la
  verificación de negocio en Twilio o AWS.
- **Verificación de negocio (Meta Business Verification) es un prerrequisito real en ambos
  proveedores** para operar más allá de límites básicos de mensajería — confirmada en la documentación
  de ambos (Twilio: obligatoria "before you can move into production" si se crea un portfolio nuevo;
  AWS: paso siguiente recomendado explícitamente "when you're ready to start sending messages at
  scale"). El tiempo típico solo se documentó explícitamente del lado de Twilio ("several weeks",
  parafraseando a Meta) — ver matices y la cifra distinta de "partner-led verification" (minutos a
  horas, pero solo para partners Select/Premier aprobados que verifican en nombre del cliente) en
  "Datos no confirmados" y en la sección de Twilio arriba.
- **El check verde (Official Business Account) no se hereda de la app de consumo:** en ambos
  proveedores es un estatus de la Business Platform, sujeto a aprobación discrecional de Meta con
  evidencia de reconocimiento público del negocio — no se encontró en ninguna fuente oficial revisada
  una mención de que un badge previo (si lo hubiera) se transfiera automáticamente al migrar.
- **Aprobación de Display Name puede fallar y tiene consecuencias operativas:** confirmado por AWS
  explícitamente — un display name rechazado baja el límite diario de mensajería y puede llevar a
  desconexión de WhatsApp (cita completa arriba). No se encontró el mismo nivel de detalle explícito
  del lado de Twilio, aunque exige cumplir las mismas reglas de nomenclatura de Meta.
