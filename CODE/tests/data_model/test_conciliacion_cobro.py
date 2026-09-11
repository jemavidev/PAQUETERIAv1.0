# -*- coding: utf-8 -*-
"""
Conciliación automática del cobro (servicio+bodegaje) contra el saldo a
favor vigente al Entregar -- Seam puro del módulo "Gestión de dinero contra
entrega" (.scratch/dinero-contra-entrega).

`conciliar_saldo_con_cobro` no toca la base de datos: se prueba con enteros
a mano, sin sesión ni fixtures de integración (mismo criterio que
`test_cobro_service.py` para `calcular_cobro`).
"""

from app.domain.saldo_contra_entrega_service import conciliar_saldo_con_cobro


def test_saldo_alcanza_exacto_deja_saldo_en_cero():
    resultado = conciliar_saldo_con_cobro(monto_cobro=4500, saldo_actual=4500)
    assert resultado.monto_aplicado_del_saldo == 4500
    assert resultado.monto_pendiente_efectivo == 0
    assert resultado.nuevo_saldo == 0


def test_saldo_sobra_deja_el_resto_como_saldo_a_favor():
    # Ejemplo real del cliente: contra-entrega $30.000 + servicio $1.500 +
    # bodegaje $3.000, con un saldo a favor de $35.000 -- el contra-entrega
    # ya se aplicó como movimiento propio en Recibir (-30.000 contra los
    # $35.000 depositados), dejando $5.000 de saldo vigente ANTES de este
    # Entregar. El cobro de ESTE Entregar es solo servicio+bodegaje
    # ($4.500): se cubre completo y sobra $500 -- el resultado exacto que
    # confirmó el cliente.
    resultado = conciliar_saldo_con_cobro(monto_cobro=4500, saldo_actual=5000)
    assert resultado.monto_aplicado_del_saldo == 4500
    assert resultado.monto_pendiente_efectivo == 0
    assert resultado.nuevo_saldo == 500


def test_saldo_insuficiente_aplica_lo_disponible_y_el_resto_en_efectivo():
    resultado = conciliar_saldo_con_cobro(monto_cobro=4500, saldo_actual=2000)
    assert resultado.monto_aplicado_del_saldo == 2000
    assert resultado.monto_pendiente_efectivo == 2500
    assert resultado.nuevo_saldo == 0


def test_saldo_cero_no_aplica_nada():
    resultado = conciliar_saldo_con_cobro(monto_cobro=4500, saldo_actual=0)
    assert resultado.monto_aplicado_del_saldo == 0
    assert resultado.monto_pendiente_efectivo == 4500
    assert resultado.nuevo_saldo == 0


def test_saldo_negativo_no_se_profundiza_nunca_aplica_nada():
    # Una deuda existente es un asunto aparte (el ajuste manual `pago_saldo`
    # de Entregar) -- esta función nunca la toca ni la agranda.
    resultado = conciliar_saldo_con_cobro(monto_cobro=4500, saldo_actual=-2000)
    assert resultado.monto_aplicado_del_saldo == 0
    assert resultado.monto_pendiente_efectivo == 4500
    assert resultado.nuevo_saldo == -2000
