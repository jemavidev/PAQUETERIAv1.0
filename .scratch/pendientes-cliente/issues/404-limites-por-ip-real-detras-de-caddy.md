# 404 — Los límites de intentos se cuentan por la IP real, no por la de Caddy

**Pedido original (Jesús):** "me confirmas que el personal de staff no tenga límites de consultas, ni para esto ni
para otras cosas" -> al revisar se encontró el problema de abajo -> "ahora sí arregla lo relacionado a lo de la IP".

**Status:** implementado (commit `52e2b24` en rama `deploy-404` del repo de deploy), sin desplegar

## Problema

En `test.papyrus.com.co` la app corre detrás de Caddy (`reverse_proxy app:8000`) y uvicorn arranca sin confiar en
`X-Forwarded-For`: `request.client.host` es SIEMPRE la IP del contenedor de Caddy (visto en el servidor: 300/300
solicitudes desde `172.18.0.4`). Todo límite "por IP" (`rate_limit()`, `/consultar` público) es en realidad UN
contador global: 11 logins de staff en un minuto en todo el sistema bloquean al 11º; 10 consultas públicas bloquean
`/consultar` para todos; 5 pedidos de código SMS bloquean al 6º residente.

Staff con sesión: sin límites en ninguna vista (confirmado; `/consultar` lo exime desde el issue 386).

## Decisión

- `Dockerfile` del repo de deploy: `uvicorn ... --proxy-headers --forwarded-allow-ips '*'`.
- `'*'` es seguro acá: la app solo hace `expose: 8000` (sin puerto publicado, solo Caddy la alcanza) y Caddy 2.11
  descarta el `X-Forwarded-For` que mande el cliente (sin `trusted_proxies`) y escribe la IP real -- uvicorn 0.24 con
  `'*'` toma la primera IP de esa cabecera. La IP de Caddy cambia entre recreaciones, por eso no se fija una IP.
- Los enlaces salen de `PUBLIC_BASE_URL`, no de `request.url`, así que ver `https` en vez de `http` no cambia nada.

## Verificación (local)

Mismo uvicorn 0.24.0 que el servidor, conexión desde una IP que no es loopback (como Caddy -> app), 10 consultas
públicas de un "vecino A" y luego un "vecino B" distinto:

| | 11ª de A | 1ª de B | IPs que ve la app |
|---|---|---|---|
| Sin el cambio (como test hoy) | 429 | **429** | una sola (la del proxy) |
| Con el cambio | 429 | **200** | la real de cada uno |

Pendiente tras el deploy: confirmar en los logs del servidor que ya no aparece solo `172.18.0.x`.
