# -*- coding: utf-8 -*-
"""
Dominio del rebuild PaqueteXv.2 — modelo de datos nuevo.

Paquete AISLADO a propósito: no importa `app.models` (que carga los modelos
viejos y el subsistema fuera de alcance de facturas/productos/CUFE) ni
`app.config` (god-object que exige credenciales AWS al importar). Así el
esquema nuevo se construye SOLO con sus propias entidades y los tests corren
en CI sin arrastrar el mundo viejo.
"""
