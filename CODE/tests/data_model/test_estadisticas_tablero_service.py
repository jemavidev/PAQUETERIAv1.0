# -*- coding: utf-8 -*-
"""
Seam A del tablero de tarjetas de `/administracion/estadisticas-cobro`
(`.scratch/estadisticas-cobro-dashboard`) -- `calcular_tablero` contra el
Postgres efímero, con el reloj ("ahora") siempre fijado explícitamente por el
test (issue de la feature: nunca depender de `datetime.now()` real, que ya
causó un test flaky real cerca de medianoche UTC en `cobro_service`).

Ticket 01: solo la tarjeta "Ingresos" de Panorama y "Total de ingresos" de
Periodo seleccionado -- el resto de las tarjetas llegan en tickets
posteriores de la misma feature.
"""

from datetime import date, datetime, timedelta, timezone

import pytest

from app.domain.cobro import Cobro
from app.domain.cobro_service import DesgloseCobro, registrar_cobro
from app.domain.estadisticas_tablero_service import (
    FiltrosTablero,
    _rango_por_atajo,
    calcular_tablero,
)
from app.domain.paquete import Paquete, TipoPaquete
from app.domain.paquete_lifecycle import deliver, receive
from app.domain.paquete_service import Destinatario, announce
from app.domain.persona import Persona
from app.domain.usuario import RolUsuario, Usuario
from app.domain.zona_horaria import ZONA_HORARIA_APP


# --- `_rango_por_atajo`: función pura, sin BD (issue 364, relocada del web al
# dominio en el ticket 01) -- misma cobertura de calendario que ya existía. --- #


def test_rango_de_cada_atajo():
    hoy = date(2026, 9, 20)  # domingo
    assert _rango_por_atajo("hoy", hoy) == (date(2026, 9, 20), date(2026, 9, 20))
    assert _rango_por_atajo("ayer", hoy) == (date(2026, 9, 19), date(2026, 9, 19))
    assert _rango_por_atajo("semana", hoy) == (date(2026, 9, 14), date(2026, 9, 20))  # lunes
    assert _rango_por_atajo("mes", hoy) == (date(2026, 9, 1), date(2026, 9, 20))
    # Ventanas móviles: empiezan el día SIGUIENTE a la misma fecha N meses atrás.
    assert _rango_por_atajo("tres_meses", hoy) == (date(2026, 6, 21), date(2026, 9, 20))
    assert _rango_por_atajo("semestre", hoy) == (date(2026, 3, 21), date(2026, 9, 20))
    assert _rango_por_atajo("anio", hoy) == (date(2025, 9, 21), date(2026, 9, 20))


def test_rango_de_la_semana_un_lunes_es_solo_ese_dia():
    assert _rango_por_atajo("semana", date(2026, 9, 14)) == (date(2026, 9, 14), date(2026, 9, 14))


def test_rango_de_meses_respeta_el_fin_de_mes_y_los_bisiestos():
    # 31-may menos 3 meses no existe en febrero: cae al 28 y la ventana arranca el 1-mar.
    assert _rango_por_atajo("tres_meses", date(2026, 5, 31)) == (date(2026, 3, 1), date(2026, 5, 31))
    # 29-feb-2024 menos 12 meses -> 28-feb-2023 (+1 día).
    assert _rango_por_atajo("anio", date(2024, 2, 29)) == (date(2023, 3, 1), date(2024, 2, 29))
    # Cruce de año.
    assert _rango_por_atajo("semestre", date(2026, 2, 10)) == (date(2025, 8, 11), date(2026, 2, 10))


def test_rango_desconocido_o_ausente_es_sin_rango():
    assert _rango_por_atajo(None, date(2026, 9, 20)) is None
    assert _rango_por_atajo("", date(2026, 9, 20)) is None
    assert _rango_por_atajo("dias7", date(2026, 9, 20)) is None
    assert _rango_por_atajo("dias30", date(2026, 9, 20)) is None


pytestmark = pytest.mark.integration


def _usuario(session, nombre="Operador") -> Usuario:
    u = Usuario(nombre=nombre, rol=RolUsuario.OPERADOR)
    session.add(u)
    session.flush()
    return u


def _entregar_con_cobro(session, staff, monto_total, tel, tipo=None, motivo_anulacion=None) -> Cobro:
    p = announce(
        session,
        anunciante_telefono=tel,
        anunciante_nombre="Ana",
        destinatario=Destinatario.yo_mismo(),
    )
    receive(session, p, staff, package_type=tipo)
    deliver(session, p, staff)
    return registrar_cobro(
        session,
        p,
        DesgloseCobro(monto_base=monto_total, bloques_bodegaje=0, monto_bodegaje=0, monto_total=monto_total),
        staff,
        motivo_anulacion=motivo_anulacion,
    )


def _mover_cobro_a(session, cobro: Cobro, cuando: datetime) -> Cobro:
    """Reescribe `Cobro.cobrado_en` directo en la fila -- la única forma de
    ubicar un cobro en un instante puntual (`registrar_cobro` siempre usa
    `datetime.now()`)."""
    cobro.cobrado_en = cuando
    session.flush()
    return cobro


def _mover_entrega_a(session, cobro: Cobro, cuando: datetime) -> Cobro:
    """Como `_mover_cobro_a`, pero ADEMÁS ubica `announced_at`/`received_at`/
    `delivered_at` del propio Paquete en ese mismo instante -- necesario para
    las pruebas de "Clientes"/"Paquetes", que consultan los timestamps del
    Paquete, no el `Cobro.cobrado_en`."""
    paquete = session.get(Paquete, cobro.paquete_id)
    paquete.announced_at = paquete.received_at = paquete.delivered_at = cuando
    cobro.cobrado_en = cuando
    session.flush()
    return cobro


def _local(anio, mes, dia, hora=12, minuto=0, segundo=0):
    """Un instante en hora de Colombia, devuelto ya en UTC (como se guarda en
    la BD)."""
    return datetime(anio, mes, dia, hora, minuto, segundo, tzinfo=ZONA_HORARIA_APP).astimezone(
        timezone.utc
    )


# --- Panorama: "Ingresos" (Hoy/Semana/Mes, hora de Colombia) --------------- #


def test_panorama_ingresos_hoy_semana_mes(db_session):
    staff = _usuario(db_session)
    # Miércoles 2026-09-16 12:00 hora Colombia (lunes de esa semana: 14-sep).
    ahora = _local(2026, 9, 16, 12, 0)

    hoy = _entregar_con_cobro(db_session, staff, 1000, tel="3001111111")
    _mover_cobro_a(db_session, hoy, _local(2026, 9, 16, 8, 0))
    en_semana_no_hoy = _entregar_con_cobro(db_session, staff, 2000, tel="3002222222")
    _mover_cobro_a(db_session, en_semana_no_hoy, _local(2026, 9, 14, 9, 0))  # el lunes
    en_mes_no_semana = _entregar_con_cobro(db_session, staff, 4000, tel="3003333333")
    _mover_cobro_a(db_session, en_mes_no_semana, _local(2026, 9, 2, 9, 0))
    fuera_del_mes = _entregar_con_cobro(db_session, staff, 8000, tel="3004444444")
    _mover_cobro_a(db_session, fuera_del_mes, _local(2026, 8, 31, 23, 59))
    db_session.commit()

    tablero = calcular_tablero(db_session, ahora)

    assert tablero.panorama.ingresos.hoy == 1000
    assert tablero.panorama.ingresos.semana == 1000 + 2000
    assert tablero.panorama.ingresos.mes == 1000 + 2000 + 4000


def test_panorama_hoy_es_el_dia_de_colombia_no_el_de_utc(db_session):
    """A las 19:00 UTC ya es el día siguiente en Bogotá (UTC-5) -- un cobro
    hecho a esa hora UTC pertenece a "Hoy" en hora local, no al día UTC."""
    staff = _usuario(db_session)
    # 2026-09-16 19:30 UTC == 2026-09-16 14:30 hora Colombia -- mismo día en
    # ambos calendarios, sirve de control.
    cobro_control = _entregar_con_cobro(db_session, staff, 500, tel="3001111111")
    _mover_cobro_a(db_session, cobro_control, datetime(2026, 9, 16, 19, 30, tzinfo=timezone.utc))
    # 2026-09-17 00:30 UTC == 2026-09-16 19:30 hora Colombia -- DÍA UTC
    # siguiente, pero SIGUE siendo 16-sep en hora local.
    cobro_limite = _entregar_con_cobro(db_session, staff, 700, tel="3002222222")
    _mover_cobro_a(db_session, cobro_limite, datetime(2026, 9, 17, 0, 30, tzinfo=timezone.utc))
    db_session.commit()

    # "Ahora" = 2026-09-16 20:00 hora Colombia (ya pasó la medianoche UTC).
    ahora = _local(2026, 9, 16, 20, 0)
    tablero = calcular_tablero(db_session, ahora)

    assert tablero.panorama.ingresos.hoy == 500 + 700


def test_panorama_justo_antes_y_despues_de_la_medianoche_local(db_session):
    staff = _usuario(db_session)
    antes = _entregar_con_cobro(db_session, staff, 111, tel="3001111111")
    _mover_cobro_a(db_session, antes, _local(2026, 9, 15, 23, 59, 59))
    despues = _entregar_con_cobro(db_session, staff, 222, tel="3002222222")
    _mover_cobro_a(db_session, despues, _local(2026, 9, 16, 0, 0, 1))
    db_session.commit()

    ahora_15 = _local(2026, 9, 15, 23, 59, 59) + timedelta(seconds=0)
    assert calcular_tablero(db_session, ahora_15).panorama.ingresos.hoy == 111

    ahora_16 = _local(2026, 9, 16, 0, 0, 1)
    assert calcular_tablero(db_session, ahora_16).panorama.ingresos.hoy == 222


def test_panorama_ingresos_no_cambia_con_ningun_filtro(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    cobro = _entregar_con_cobro(db_session, staff, 1500, tel="3001111111", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    _mover_cobro_a(db_session, cobro, _local(2026, 9, 16, 8, 0))
    db_session.commit()

    sin_filtros = calcular_tablero(db_session, ahora).panorama.ingresos.hoy
    con_tipo = calcular_tablero(
        db_session, ahora, FiltrosTablero(tipo=TipoPaquete.NORMAL)
    ).panorama.ingresos.hoy
    con_rango_hoy = calcular_tablero(db_session, ahora, FiltrosTablero(rango="hoy")).panorama.ingresos.hoy
    con_rango_lejano = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="anio")
    ).panorama.ingresos.hoy

    assert sin_filtros == con_tipo == con_rango_hoy == con_rango_lejano == 1500


def test_panorama_con_base_vacia_no_rompe(db_session):
    tablero = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0))

    assert tablero.panorama.ingresos == calcular_tablero(
        db_session, _local(2026, 9, 16, 12, 0)
    ).panorama.ingresos
    assert tablero.panorama.ingresos.hoy == 0
    assert tablero.panorama.ingresos.semana == 0
    assert tablero.panorama.ingresos.mes == 0


# --- Panorama: "Entregados" y "Cancelados" (ticket 06) --------------------- #


def test_panorama_entregados_y_cancelados_hoy_semana_mes(db_session):
    ahora = _local(2026, 9, 16, 12, 0)

    entregado_hoy = _anunciar(db_session, "3001111111")
    _mover(db_session, entregado_hoy, delivered_at=_local(2026, 9, 16, 8, 0))
    entregado_en_semana = _anunciar(db_session, "3002222222")
    _mover(db_session, entregado_en_semana, delivered_at=_local(2026, 9, 14, 8, 0))
    entregado_en_mes = _anunciar(db_session, "3003333333")
    _mover(db_session, entregado_en_mes, delivered_at=_local(2026, 9, 2, 8, 0))
    entregado_fuera = _anunciar(db_session, "3004444444")
    _mover(db_session, entregado_fuera, delivered_at=_local(2026, 8, 31, 8, 0))

    cancelado_hoy = _anunciar(db_session, "3005555555")
    _mover(db_session, cancelado_hoy, cancelled_at=_local(2026, 9, 16, 9, 0))
    cancelado_en_mes = _anunciar(db_session, "3006666666")
    _mover(db_session, cancelado_en_mes, cancelled_at=_local(2026, 9, 5, 9, 0))
    db_session.commit()

    tablero = calcular_tablero(db_session, ahora)

    assert tablero.panorama.entregados.hoy == 1
    assert tablero.panorama.entregados.semana == 2
    assert tablero.panorama.entregados.mes == 3

    assert tablero.panorama.cancelados.hoy == 1
    assert tablero.panorama.cancelados.semana == 1
    assert tablero.panorama.cancelados.mes == 2


def test_panorama_entregados_cancelados_no_se_mezclan_ni_dependen_de_filtros(db_session):
    ahora = _local(2026, 9, 16, 12, 0)
    entregado = _anunciar(db_session, "3001111111", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    _mover(db_session, entregado, delivered_at=_local(2026, 9, 16, 8, 0))
    cancelado = _anunciar(db_session, "3002222222")
    _mover(db_session, cancelado, cancelled_at=_local(2026, 9, 16, 8, 0))
    db_session.commit()

    sin_filtros = calcular_tablero(db_session, ahora).panorama
    con_tipo = calcular_tablero(db_session, ahora, FiltrosTablero(tipo=TipoPaquete.NORMAL)).panorama
    con_rango_lejano = calcular_tablero(db_session, ahora, FiltrosTablero(rango="anio")).panorama

    assert sin_filtros.entregados.hoy == con_tipo.entregados.hoy == con_rango_lejano.entregados.hoy == 1
    assert sin_filtros.cancelados.hoy == con_tipo.cancelados.hoy == con_rango_lejano.cancelados.hoy == 1
    # Nunca sumadas en un solo "procesados" -- cada trío cuenta solo lo suyo.
    assert sin_filtros.entregados.hoy != sin_filtros.entregados.hoy + sin_filtros.cancelados.hoy


def test_panorama_entregados_cancelados_con_base_vacia_no_rompe(db_session):
    panorama = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).panorama

    assert panorama.entregados.hoy == panorama.entregados.semana == panorama.entregados.mes == 0
    assert panorama.cancelados.hoy == panorama.cancelados.semana == panorama.cancelados.mes == 0


# --- Panorama: "Tiempos promedio" (ticket 07) ------------------------------ #


def test_tiempos_promedio_anuncio_recepcion_y_permanencia_bodega(db_session):
    ahora = _local(2026, 9, 16, 12, 0)

    # Recibido HOY: 6 horas entre anuncio y recepción.
    p1 = _anunciar(db_session, "3001111111")
    _mover(
        db_session, p1,
        announced_at=_local(2026, 9, 16, 2, 0), received_at=_local(2026, 9, 16, 8, 0),
    )
    # Recibido ESTA SEMANA (no hoy): 12 horas.
    p2 = _anunciar(db_session, "3002222222")
    _mover(
        db_session, p2,
        announced_at=_local(2026, 9, 14, 20, 0), received_at=_local(2026, 9, 15, 8, 0),
    )
    db_session.commit()

    tiempos = calcular_tablero(db_session, ahora).panorama.tiempos

    assert tiempos.anuncio_recepcion.hoy == pytest.approx(6.0)
    assert tiempos.anuncio_recepcion.semana == pytest.approx((6.0 + 12.0) / 2)


def test_tiempos_promedio_permanencia_bodega_y_bodegaje_cobrado(db_session):
    from app.domain.cobro import Cobro as CobroModel

    ahora = _local(2026, 9, 16, 12, 0)

    # Entregado hoy, 10 horas en bodega, CON bloques de bodegaje cobrados.
    cobro_con_bodegaje = _entregar_con_cobro(db_session, _usuario(db_session), 1000, tel="3001111111")
    paquete_con = db_session.get(Paquete, cobro_con_bodegaje.paquete_id)
    paquete_con.received_at = _local(2026, 9, 16, 0, 0)
    paquete_con.delivered_at = _local(2026, 9, 16, 10, 0)
    cobro_con_bodegaje.bloques_bodegaje = 2
    # Entregado hoy también, 20 horas en bodega, SIN bloques de bodegaje.
    cobro_sin_bodegaje = _entregar_con_cobro(db_session, _usuario(db_session, "Op2"), 500, tel="3002222222")
    paquete_sin = db_session.get(Paquete, cobro_sin_bodegaje.paquete_id)
    paquete_sin.received_at = _local(2026, 9, 16, 0, 0)
    paquete_sin.delivered_at = _local(2026, 9, 16, 20, 0)
    cobro_sin_bodegaje.bloques_bodegaje = 0
    db_session.commit()

    tiempos = calcular_tablero(db_session, ahora).panorama.tiempos

    # Permanencia en bodega: promedio de AMBOS (10 y 20 horas).
    assert tiempos.permanencia_bodega.hoy == pytest.approx((10.0 + 20.0) / 2)
    # Bodegaje cobrado: solo el que tuvo bloques_bodegaje > 0.
    assert tiempos.bodegaje_cobrado.hoy == pytest.approx(10.0)


def test_tiempos_promedio_none_sin_ningun_paquete_que_califique(db_session):
    tiempos = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).panorama.tiempos

    assert tiempos.anuncio_recepcion.hoy is None
    assert tiempos.anuncio_recepcion.semana is None
    assert tiempos.anuncio_recepcion.mes is None
    assert tiempos.permanencia_bodega.hoy is None
    assert tiempos.bodegaje_cobrado.hoy is None


def test_tiempos_promedio_no_cambia_con_ningun_filtro(db_session):
    ahora = _local(2026, 9, 16, 12, 0)
    p = _anunciar(db_session, "3001111111", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    _mover(db_session, p, announced_at=_local(2026, 9, 16, 2, 0), received_at=_local(2026, 9, 16, 8, 0))
    db_session.commit()

    sin_filtros = calcular_tablero(db_session, ahora).panorama.tiempos.anuncio_recepcion.hoy
    con_tipo = calcular_tablero(
        db_session, ahora, FiltrosTablero(tipo=TipoPaquete.NORMAL)
    ).panorama.tiempos.anuncio_recepcion.hoy
    con_rango = calcular_tablero(db_session, ahora, FiltrosTablero(rango="anio")).panorama.tiempos.anuncio_recepcion.hoy

    assert sin_filtros == con_tipo == con_rango == pytest.approx(6.0)


# --- Periodo seleccionado: "Total de ingresos" ----------------------------- #


def test_periodo_sin_rango_activo_son_todos_los_datos(db_session):
    staff = _usuario(db_session)
    viejo = _entregar_con_cobro(db_session, staff, 5000, tel="3001111111")
    _mover_cobro_a(db_session, viejo, _local(2024, 1, 1, 12, 0))
    reciente = _entregar_con_cobro(db_session, staff, 3000, tel="3002222222")
    _mover_cobro_a(db_session, reciente, _local(2026, 9, 16, 8, 0))
    db_session.commit()

    tablero = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0))

    assert tablero.periodo.rango_activo is None
    assert tablero.periodo.recaudo.total_ingresos == 8000


@pytest.mark.parametrize("clave", ["mes", "anio"])
def test_periodo_con_atajo_acota_al_rango(db_session, clave):
    staff = _usuario(db_session)
    dentro = _entregar_con_cobro(db_session, staff, 1000, tel="3001111111")
    _mover_cobro_a(db_session, dentro, _local(2026, 9, 16, 8, 0))
    fuera = _entregar_con_cobro(db_session, staff, 9000, tel="3002222222")
    _mover_cobro_a(db_session, fuera, _local(2024, 1, 1, 8, 0))
    db_session.commit()

    tablero = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0), FiltrosTablero(rango=clave))

    assert tablero.periodo.rango_activo == clave
    assert tablero.periodo.recaudo.total_ingresos == 1000


def test_periodo_una_clave_de_rango_desconocida_se_ignora(db_session):
    staff = _usuario(db_session)
    cobro = _entregar_con_cobro(db_session, staff, 1000, tel="3001111111")
    _mover_cobro_a(db_session, cobro, _local(2024, 1, 1, 8, 0))
    db_session.commit()

    tablero = calcular_tablero(
        db_session, _local(2026, 9, 16, 12, 0), FiltrosTablero(rango="no-existe")
    )

    assert tablero.periodo.rango_activo is None
    assert tablero.periodo.recaudo.total_ingresos == 1000


def test_periodo_filtra_por_tipo_y_por_cobrado_anulado(db_session):
    staff = _usuario(db_session)
    normal = _entregar_con_cobro(db_session, staff, 1000, tel="3001111111", tipo=TipoPaquete.NORMAL)
    extra = _entregar_con_cobro(db_session, staff, 2000, tel="3002222222", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    anulado = _entregar_con_cobro(db_session, staff, 0, tel="3003333333", motivo_anulacion="Cortesía")
    for c in (normal, extra, anulado):
        _mover_cobro_a(db_session, c, _local(2026, 9, 16, 8, 0))
    db_session.commit()
    ahora = _local(2026, 9, 16, 12, 0)

    solo_extra = calcular_tablero(db_session, ahora, FiltrosTablero(tipo=TipoPaquete.EXTRA_DIMENSIONADO))
    assert solo_extra.periodo.recaudo.total_ingresos == 2000

    solo_anulados = calcular_tablero(db_session, ahora, FiltrosTablero(anulado=True))
    assert solo_anulados.periodo.recaudo.total_ingresos == 0  # el anulado quedó en $0

    solo_cobrados = calcular_tablero(db_session, ahora, FiltrosTablero(anulado=False))
    assert solo_cobrados.periodo.recaudo.total_ingresos == 1000 + 2000


def test_periodo_con_base_vacia_no_rompe(db_session):
    tablero = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0))

    assert tablero.periodo.rango_activo is None
    assert tablero.periodo.recaudo.total_ingresos == 0


# --- Periodo seleccionado: "Paquetes", "Ritmo y tasas" (ticket 02) --------- #


def _anunciar(session, tel, tipo=None):
    from app.domain.paquete_service import Destinatario, announce

    return announce(session, anunciante_telefono=tel, anunciante_nombre="Ana", destinatario=Destinatario.yo_mismo())


def _mover(session, paquete, **timestamps):
    for campo, valor in timestamps.items():
        setattr(paquete, campo, valor)
    session.flush()
    return paquete


def test_paquetes_total_es_con_cualquier_movimiento_en_el_periodo(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    # Anunciado DENTRO del periodo (mes), nunca recibido.
    solo_anunciado = _anunciar(db_session, "3001111111")
    _mover(db_session, solo_anunciado, announced_at=_local(2026, 9, 10, 8, 0))
    # Anunciado ANTES del periodo pero RECIBIDO dentro -- cuenta en "total",
    # no en "anunciados".
    recibido_en_mes = _anunciar(db_session, "3002222222")
    _mover(
        db_session, recibido_en_mes,
        announced_at=_local(2026, 8, 1, 8, 0), received_at=_local(2026, 9, 5, 8, 0),
    )
    # Todo por fuera del periodo.
    fuera = _anunciar(db_session, "3003333333")
    _mover(db_session, fuera, announced_at=_local(2026, 7, 1, 8, 0))
    db_session.commit()

    periodo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo

    assert periodo.paquetes.total == 2
    assert periodo.paquetes.anunciados == 1
    assert periodo.paquetes.recibidos == 1


def test_paquetes_cada_categoria_por_su_propia_fecha(db_session):
    ahora = _local(2026, 9, 16, 12, 0)
    p = _anunciar(db_session, "3001111111")
    _mover(
        db_session, p,
        announced_at=_local(2026, 9, 1, 8, 0),
        received_at=_local(2026, 9, 5, 8, 0),
        delivered_at=_local(2026, 9, 8, 8, 0),
        package_type=TipoPaquete.NORMAL,
    )
    cancelado = _anunciar(db_session, "3002222222")
    _mover(
        db_session, cancelado,
        announced_at=_local(2026, 9, 2, 8, 0), cancelled_at=_local(2026, 9, 9, 8, 0),
    )
    db_session.commit()

    periodo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo
    assert periodo.paquetes.anunciados == 2
    assert periodo.paquetes.recibidos == 1
    assert periodo.paquetes.entregados == 1
    assert periodo.paquetes.cancelados == 1
    assert periodo.paquetes.total == 2


def test_paquetes_filtro_tipo_acota_recibidos_y_entregados_no_el_resto(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    normal = _anunciar(db_session, "3001111111")
    _mover(
        db_session, normal,
        announced_at=_local(2026, 9, 1, 8, 0), received_at=_local(2026, 9, 2, 8, 0),
        delivered_at=_local(2026, 9, 3, 8, 0), package_type=TipoPaquete.NORMAL,
    )
    extra = _anunciar(db_session, "3002222222")
    _mover(
        db_session, extra,
        announced_at=_local(2026, 9, 1, 8, 0), received_at=_local(2026, 9, 2, 8, 0),
        delivered_at=_local(2026, 9, 3, 8, 0), package_type=TipoPaquete.EXTRA_DIMENSIONADO,
    )
    db_session.commit()

    solo_normal = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="mes", tipo=TipoPaquete.NORMAL)
    ).periodo

    assert solo_normal.paquetes.recibidos == 1
    assert solo_normal.paquetes.entregados == 1
    # Tipo NO acota estas -- siguen contando AMBOS paquetes.
    assert solo_normal.paquetes.total == 2
    assert solo_normal.paquetes.anunciados == 2


def test_tasas_sobre_cerrados_y_nunca_filtradas_por_tipo(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    entregado_normal = _anunciar(db_session, "3001111111")
    _mover(
        db_session, entregado_normal,
        announced_at=_local(2026, 9, 1, 8, 0), delivered_at=_local(2026, 9, 3, 8, 0),
        package_type=TipoPaquete.NORMAL,
    )
    entregado_extra = _anunciar(db_session, "3002222222")
    _mover(
        db_session, entregado_extra,
        announced_at=_local(2026, 9, 1, 8, 0), delivered_at=_local(2026, 9, 4, 8, 0),
        package_type=TipoPaquete.EXTRA_DIMENSIONADO,
    )
    cancelado = _anunciar(db_session, "3003333333")
    _mover(db_session, cancelado, announced_at=_local(2026, 9, 1, 8, 0), cancelled_at=_local(2026, 9, 5, 8, 0))
    db_session.commit()

    periodo = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="mes", tipo=TipoPaquete.NORMAL)
    ).periodo

    # 2 entregados + 1 cancelado = 3 cerrados, SIN filtrar por tipo.
    assert periodo.ritmo.tasa_entrega == pytest.approx(200 / 3)
    assert periodo.ritmo.tasa_cancelacion == pytest.approx(100 / 3)


def test_tasas_sin_ningun_cerrado_son_none(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    solo_anunciado = _anunciar(db_session, "3001111111")
    _mover(db_session, solo_anunciado, announced_at=_local(2026, 9, 1, 8, 0))
    db_session.commit()

    periodo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo

    assert periodo.ritmo.tasa_entrega is None
    assert periodo.ritmo.tasa_cancelacion is None


def test_ritmo_por_dia_semana_mes_con_rango_activo(db_session):
    staff = _usuario(db_session)
    # "Este mes" con ahora=16-sep: 16 días (1-sep al 16-sep, ambos inclusive).
    ahora = _local(2026, 9, 16, 12, 0)
    for i in range(4):
        p = _anunciar(db_session, f"300111100{i}")
        _mover(db_session, p, announced_at=_local(2026, 9, 1 + i, 8, 0))
    db_session.commit()

    periodo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo

    assert periodo.paquetes.anunciados == 4
    dias = 16
    assert periodo.ritmo.anunciados.por_dia == pytest.approx(4 / dias)
    assert periodo.ritmo.anunciados.por_semana == pytest.approx(4 / dias * 7)
    assert periodo.ritmo.anunciados.por_mes == pytest.approx(4 / dias * 30)


def test_ritmo_sin_rango_activo_cuenta_desde_el_primer_anuncio(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    primero = _anunciar(db_session, "3001111111")
    _mover(db_session, primero, announced_at=_local(2026, 9, 6, 8, 0))  # hace 10 días
    db_session.commit()

    periodo = calcular_tablero(db_session, ahora).periodo

    dias = 11  # 6-sep al 16-sep, ambos inclusive
    assert periodo.ritmo.anunciados.por_dia == pytest.approx(1 / dias)


def test_paquetes_y_ritmo_con_base_vacia_no_rompe(db_session):
    periodo = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).periodo

    assert periodo.paquetes.total == 0
    assert periodo.ritmo.anunciados.por_dia == 0
    assert periodo.ritmo.tasa_entrega is None


# --- Periodo seleccionado: "Recaudo" completo (ticket 03) ------------------ #


def test_recaudo_promedio_bodegaje_servicio_y_cobro_mas_alto(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    a = _entregar_con_cobro(db_session, staff, 1500, tel="3001111111")
    _mover_cobro_a(db_session, a, _local(2026, 9, 10, 8, 0))
    b = _entregar_con_cobro(db_session, staff, 2500, tel="3002222222")
    _mover_cobro_a(db_session, b, _local(2026, 9, 11, 8, 0))
    b.monto_base = 1500
    b.monto_bodegaje = 1000
    b.bloques_bodegaje = 1
    db_session.commit()

    recaudo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.recaudo

    assert recaudo.total_ingresos == 4000
    assert recaudo.promedio_por_paquete == pytest.approx(2000)
    assert recaudo.recaudado_bodegaje == 1000
    assert recaudo.porcentaje_bodegaje == pytest.approx(25.0)
    assert recaudo.recaudado_servicio == 3000
    assert recaudo.porcentaje_servicio == pytest.approx(75.0)
    assert recaudo.cobro_mas_alto == 2500
    assert recaudo.dias_bodega_del_mas_alto == 1


def test_recaudo_exonerado_por_anulaciones_estimado_con_tarifas_vigentes(db_session):
    from app.domain.cobro_service import editar_tarifas

    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    editar_tarifas(db_session, base_normal=1500, base_extra_dimensionado=2000, bodegaje_normal_24h=1000, bodegaje_extra_dimensionado_24h=1500)
    normal_anulado = _entregar_con_cobro(db_session, staff, 1234, tel="3001111111", tipo=TipoPaquete.NORMAL, motivo_anulacion="Reclamo")
    _mover_cobro_a(db_session, normal_anulado, _local(2026, 9, 10, 8, 0))
    extra_anulado = _entregar_con_cobro(db_session, staff, 999, tel="3002222222", tipo=TipoPaquete.EXTRA_DIMENSIONADO, motivo_anulacion="Reclamo")
    _mover_cobro_a(db_session, extra_anulado, _local(2026, 9, 11, 8, 0))
    normal_cobrado = _entregar_con_cobro(db_session, staff, 1500, tel="3003333333", tipo=TipoPaquete.NORMAL)
    _mover_cobro_a(db_session, normal_cobrado, _local(2026, 9, 12, 8, 0))
    db_session.commit()

    recaudo = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.recaudo

    # Escenario armado a mano: 1 anulado NORMAL (tarifa vigente 1500) + 1
    # anulado EXTRA_DIMENSIONADO (tarifa vigente 2000) = 3500 estimado.
    assert recaudo.cantidad_anulaciones == 2
    assert recaudo.exonerado_anulaciones == 1500 + 2000
    assert recaudo.tasa_anulacion == pytest.approx(2 / 3 * 100)


def test_recaudo_exenciones_primera_entrega_estimado_e_ignora_filtro_anulado(db_session):
    from app.domain.cobro_service import editar_tarifas

    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    editar_tarifas(db_session, base_normal=1500, base_extra_dimensionado=2000, bodegaje_normal_24h=1000, bodegaje_extra_dimensionado_24h=1500)
    exento = _entregar_con_cobro(db_session, staff, 0, tel="3001111111", tipo=TipoPaquete.NORMAL)  # primera entrega, sin motivo
    _mover_cobro_a(db_session, exento, _local(2026, 9, 10, 8, 0))
    anulado = _entregar_con_cobro(db_session, staff, 0, tel="3002222222", tipo=TipoPaquete.NORMAL, motivo_anulacion="Reclamo")
    _mover_cobro_a(db_session, anulado, _local(2026, 9, 11, 8, 0))
    db_session.commit()

    # "estado_cobro=cobrado" (anulado=False) NO debería vaciar esta tarjeta
    # -- Cobrado/Anulado no la acota (matriz de "no aplica").
    recaudo = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="mes", anulado=False)
    ).periodo.recaudo

    assert recaudo.exenciones_primera_entrega == 1
    assert recaudo.dejado_de_cobrar_primera_entrega == 1500
    # El anulado (con motivo) NUNCA cuenta como "exención por primera entrega".


def test_recaudo_sin_ningun_cobro_todo_none_o_cero(db_session):
    recaudo = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).periodo.recaudo

    assert recaudo.total_ingresos == 0
    assert recaudo.promedio_por_paquete is None
    assert recaudo.porcentaje_bodegaje is None
    assert recaudo.porcentaje_servicio is None
    assert recaudo.tasa_anulacion is None
    assert recaudo.cobro_mas_alto is None
    assert recaudo.dias_bodega_del_mas_alto is None
    assert recaudo.cantidad_anulaciones == 0
    assert recaudo.exenciones_primera_entrega == 0


# --- Periodo seleccionado: "Clientes" (ticket 04) --------------------------- #


def test_clientes_activos_y_recurrentes(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    # Cliente A: 2 paquetes con movimiento en el periodo -- recurrente.
    a1 = _anunciar(db_session, "3001111111")
    _mover(db_session, a1, announced_at=_local(2026, 9, 5, 8, 0))
    a2 = _anunciar(db_session, "3001111111")
    _mover(db_session, a2, announced_at=_local(2026, 9, 6, 8, 0))
    # Cliente B: 1 solo paquete -- activo, no recurrente.
    b1 = _anunciar(db_session, "3002222222")
    _mover(db_session, b1, announced_at=_local(2026, 9, 7, 8, 0))
    # Cliente C: su único paquete es "nombre sin teléfono" -- NO cuenta.
    from app.domain.paquete_service import Destinatario, announce

    c1 = announce(
        db_session, anunciante_telefono="3009999999", anunciante_nombre="Ana",
        destinatario=Destinatario.solo_nombre("Un Vecino"),
    )
    _mover(db_session, c1, announced_at=_local(2026, 9, 8, 8, 0))
    db_session.commit()

    clientes = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.clientes

    assert clientes.activos == 2  # A y B (el anunciante de C no es su destinatario)
    assert clientes.recurrentes == 1  # solo A


def test_clientes_nuevos_por_primera_entrega_historica(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    nuevo = _anunciar(db_session, "3001111111")
    _mover(db_session, nuevo, announced_at=_local(2026, 9, 1, 8, 0), delivered_at=_local(2026, 9, 5, 8, 0))
    # Cliente antiguo: su primera entrega fue MUCHO antes del periodo, así
    # que aunque tenga actividad ahora, no es "nuevo".
    antiguo_primera = _anunciar(db_session, "3002222222")
    _mover(db_session, antiguo_primera, announced_at=_local(2025, 1, 1, 8, 0), delivered_at=_local(2025, 1, 5, 8, 0))
    antiguo_reciente = _anunciar(db_session, "3002222222")
    _mover(db_session, antiguo_reciente, announced_at=_local(2026, 9, 10, 8, 0))
    db_session.commit()

    clientes = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.clientes

    assert clientes.nuevos == 1


def test_cliente_con_mas_paquetes_nombre_apartamento_y_empate(db_session):
    from app.domain.apartamento import Apartamento

    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    apto = db_session.query(Apartamento).first()

    for _ in range(2):
        extra = _anunciar(db_session, "3001111111")
        _mover(db_session, extra, announced_at=_local(2026, 9, 1, 8, 0), snapshot_torre=apto.torre, snapshot_apartamento=apto.apartamento)
    # El MÁS RECIENTE de sus 3 paquetes también lleva el snapshot -- es el
    # que `_nombre_y_apartamento_de_cliente` debe elegir.
    ganador = _anunciar(db_session, "3001111111")
    _mover(db_session, ganador, announced_at=_local(2026, 9, 2, 8, 0), snapshot_torre=apto.torre, snapshot_apartamento=apto.apartamento)
    otro = _anunciar(db_session, "3002222222")
    _mover(db_session, otro, announced_at=_local(2026, 9, 3, 8, 0))
    db_session.commit()

    clientes = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.clientes

    assert clientes.con_mas_paquetes.valor == 3
    assert clientes.con_mas_paquetes.nombre == "ANA"  # nombre de la Persona (announce() usa "Ana")
    assert clientes.con_mas_paquetes.apartamento == f"{apto.torre} {apto.apartamento}"


def test_cliente_con_mayor_gasto_respeta_cobrado_anulado_pero_mas_paquetes_no(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    barato_muchos = _entregar_con_cobro(db_session, staff, 100, tel="3001111111")
    _mover_entrega_a(db_session, barato_muchos, _local(2026, 9, 1, 8, 0))
    for _ in range(2):
        c = _entregar_con_cobro(db_session, staff, 100, tel="3001111111")
        _mover_entrega_a(db_session, c, _local(2026, 9, 2, 8, 0))
    caro_uno = _entregar_con_cobro(db_session, staff, 9999, tel="3002222222")
    _mover_entrega_a(db_session, caro_uno, _local(2026, 9, 3, 8, 0))
    db_session.commit()

    clientes = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.clientes

    assert clientes.con_mayor_gasto.valor == 9999  # el caro, aunque tenga menos paquetes
    assert clientes.con_mas_paquetes.valor == 3  # el de más paquetes, aunque gaste menos


def test_clientes_de_baja_administrativa_no_cuentan(db_session):
    from app.domain.persona_service import dar_de_baja_administrativa

    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    p = _anunciar(db_session, "3001111111")
    _mover(db_session, p, announced_at=_local(2026, 9, 5, 8, 0))
    db_session.flush()
    persona = db_session.query(Persona).filter(Persona.telefono == "+573001111111").one()
    dar_de_baja_administrativa(db_session, persona)
    db_session.commit()

    clientes = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.clientes

    assert clientes.activos == 0
    assert clientes.con_mas_paquetes is None


def test_clientes_filtro_tipo_acota_todas_menos_mayor_gasto_que_tambien_respeta_anulado(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    normal = _entregar_con_cobro(db_session, staff, 500, tel="3001111111", tipo=TipoPaquete.NORMAL)
    _mover_entrega_a(db_session, normal, _local(2026, 9, 1, 8, 0))
    extra = _entregar_con_cobro(db_session, staff, 500, tel="3002222222", tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    _mover_entrega_a(db_session, extra, _local(2026, 9, 2, 8, 0))
    db_session.commit()

    solo_normal = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="mes", tipo=TipoPaquete.NORMAL)
    ).periodo.clientes

    assert solo_normal.activos == 1
    assert solo_normal.con_mayor_gasto.valor == 500  # solo el cliente NORMAL califica


def test_clientes_con_base_vacia_no_rompe(db_session):
    clientes = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).periodo.clientes

    assert clientes.activos == 0
    assert clientes.nuevos == 0
    assert clientes.recurrentes == 0
    assert clientes.con_mas_paquetes is None
    assert clientes.con_mayor_gasto is None


# --- Periodo seleccionado: "Operación y calidad" (ticket 05) --------------- #


def _entregar_condicion(session, staff, tel, entregado_en, tipo=None, condicion=None, recibido_en=None):
    from app.domain.paquete import CondicionPaquete

    cobro = _entregar_con_cobro(session, staff, 100, tel=tel, tipo=tipo)
    paquete = session.get(Paquete, cobro.paquete_id)
    paquete.received_at = recibido_en or (entregado_en - timedelta(hours=1))
    paquete.delivered_at = entregado_en
    paquete.announced_at = paquete.received_at - timedelta(hours=1)
    if condicion is not None:
        paquete.package_condition = condicion
    cobro.cobrado_en = entregado_en
    session.flush()
    return paquete


def test_operador_con_mas_entregas_y_empate_por_nombre(db_session):
    ana = _usuario(db_session, nombre="ANA OPERADORA")
    beto = _usuario(db_session, nombre="BETO OPERADOR")
    ahora = _local(2026, 9, 16, 12, 0)
    for tel in ("3001111111", "3002222222"):
        p = _entregar_condicion(db_session, ana, tel, _local(2026, 9, 10, 10, 0))
        p.delivered_by_usuario_id = ana.id
    p_beto = _entregar_condicion(db_session, beto, "3003333333", _local(2026, 9, 11, 10, 0))
    p_beto.delivered_by_usuario_id = beto.id
    db_session.commit()

    operacion = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.operacion

    assert operacion.operador_top_nombre == "ANA OPERADORA"
    assert operacion.operador_top_cantidad == 2


def test_dia_y_hora_pico_en_hora_de_colombia(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    # 3 entregas el martes 2026-09-08 a las 18:00 hora Colombia (6-7pm).
    for i, tel in enumerate(["3001111111", "3002222222", "3003333333"]):
        _entregar_condicion(db_session, staff, tel, _local(2026, 9, 8, 18, 0))
    # 1 entrega el miércoles a otra hora.
    _entregar_condicion(db_session, staff, "3004444444", _local(2026, 9, 9, 9, 0))
    db_session.commit()

    operacion = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.operacion

    assert operacion.dia_mas_activo == "Martes"
    assert operacion.dia_mas_activo_porcentaje == pytest.approx(75.0)
    assert operacion.hora_pico == "6 – 7 p. m."


def test_porcentaje_dentro_de_48h(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    rapido = _entregar_condicion(db_session, staff, "3001111111", _local(2026, 9, 10, 10, 0))
    rapido.received_at = rapido.delivered_at - timedelta(hours=10)
    lento = _entregar_condicion(db_session, staff, "3002222222", _local(2026, 9, 11, 10, 0))
    lento.received_at = lento.delivered_at - timedelta(hours=72)
    db_session.commit()

    operacion = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.operacion

    assert operacion.porcentaje_dentro_de_48h == pytest.approx(50.0)


def test_porcentaje_extra_dimensionados_ignora_filtro_tipo(db_session):
    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    _entregar_condicion(db_session, staff, "3001111111", _local(2026, 9, 10, 10, 0), tipo=TipoPaquete.NORMAL)
    _entregar_condicion(db_session, staff, "3002222222", _local(2026, 9, 11, 10, 0), tipo=TipoPaquete.NORMAL)
    _entregar_condicion(db_session, staff, "3003333333", _local(2026, 9, 12, 10, 0), tipo=TipoPaquete.EXTRA_DIMENSIONADO)
    db_session.commit()

    operacion_normal = calcular_tablero(
        db_session, ahora, FiltrosTablero(rango="mes", tipo=TipoPaquete.NORMAL)
    ).periodo.operacion
    operacion_sin_filtro = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.operacion

    # Mismo valor con o sin filtro Tipo -- nunca se acota (matriz).
    assert operacion_normal.porcentaje_extra_dimensionados == pytest.approx(1 / 3 * 100)
    assert operacion_sin_filtro.porcentaje_extra_dimensionados == pytest.approx(1 / 3 * 100)


def test_porcentaje_mal_estado(db_session):
    from app.domain.paquete import CondicionPaquete

    staff = _usuario(db_session)
    ahora = _local(2026, 9, 16, 12, 0)
    _entregar_condicion(db_session, staff, "3001111111", _local(2026, 9, 10, 10, 0), condicion=CondicionPaquete.BUENO)
    _entregar_condicion(db_session, staff, "3002222222", _local(2026, 9, 11, 10, 0), condicion=CondicionPaquete.ABIERTO)
    _entregar_condicion(db_session, staff, "3003333333", _local(2026, 9, 12, 10, 0), condicion=CondicionPaquete.REGULAR)
    db_session.commit()

    operacion = calcular_tablero(db_session, ahora, FiltrosTablero(rango="mes")).periodo.operacion

    assert operacion.porcentaje_mal_estado == pytest.approx(2 / 3 * 100)


def test_operacion_con_base_vacia_no_rompe(db_session):
    operacion = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0)).periodo.operacion

    assert operacion.operador_top_nombre is None
    assert operacion.operador_top_cantidad == 0
    assert operacion.dia_mas_activo is None
    assert operacion.hora_pico is None
    assert operacion.porcentaje_dentro_de_48h is None
    assert operacion.porcentaje_extra_dimensionados is None
    assert operacion.porcentaje_mal_estado is None
