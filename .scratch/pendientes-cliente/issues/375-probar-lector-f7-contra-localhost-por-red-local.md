# 375 — Cómo probar el F7 contra el ambiente local (`localhost:8010`) por red local

**Pedido original (Jesús):** "necesito que me digas como puedo hacer pruebas con el lector en localhost, ya
que hasta el momento me toca hacer pruebas sobre el servidor de pruebas test.papyrus.com.co y es muy tedioso,
como me conecto desde el dispositivo aqui a localhost?".

**Status:** implementado (una vez, para esta sesión) — nota operativa, no un ticket de código

## Qué se hizo

`localhost` en el F7 se refiere al propio F7, no a la computadora que corre el ambiente local — para que el
F7 llegue al servidor de la PC hace falta la IP de la PC en la red local, y que el servidor escuche en todas
las interfaces (`0.0.0.0`), no solo en `127.0.0.1` (loopback, que por diseño ningún otro dispositivo puede
alcanzar).

1. IP de la PC en la red local: `192.168.1.124` (obtenida con `hostname -I`; cambia si la PC se reconecta a la
   red y el router le asigna otra).
2. Se detuvo el `uvicorn` de siempre (que escucha solo en `127.0.0.1:8010`) y se levantó uno nuevo, mismas
   variables de entorno, pero con `--host 0.0.0.0` en vez de `--host 127.0.0.1` — sin tocar
   `scripts/paquetex_dev_up.sh` (que sigue arrancando en modo `127.0.0.1` por defecto; este cambio fue solo
   para esta sesión de pruebas).
3. En el F7: mismo WiFi que la PC, y en Chrome ir a `http://192.168.1.124:8010` (nota: `http`, no `https` — es
   una URL de red local, no la del servidor de test).

## Limitaciones a tener en cuenta

- Si el router del WiFi tiene "aislamiento de clientes" (client isolation) activado, los dispositivos no se
  ven entre sí aunque estén en la misma red — si el F7 no logra conectar, es lo primero a revisar.
- La IP de la PC puede cambiar entre sesiones (DHCP); si deja de funcionar, correr `hostname -I` de nuevo.
- Es solo para pruebas manuales en esta red. No reemplaza la verificación automática (suite de pruebas) ni el
  despliegue a test.papyrus.com.co antes de darlo por confirmado.
- Como el modo lector oculta el botón de cámara, no hizo falta resolver el contexto seguro (HTTPS) que
  exigiría `getUserMedia` — si en el futuro hiciera falta probar la cámara por red local, `http://` sobre una
  IP de LAN no cuenta como contexto seguro para el navegador, y esa prueba sí necesitaría otro mecanismo
  (túnel HTTPS o certificado local).
