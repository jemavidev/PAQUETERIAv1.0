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
from app.domain.paquete import TipoPaquete
from app.domain.paquete_lifecycle import deliver, receive
from app.domain.paquete_service import Destinatario, announce
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
    assert tablero.periodo.total_ingresos == 8000


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
    assert tablero.periodo.total_ingresos == 1000


def test_periodo_una_clave_de_rango_desconocida_se_ignora(db_session):
    staff = _usuario(db_session)
    cobro = _entregar_con_cobro(db_session, staff, 1000, tel="3001111111")
    _mover_cobro_a(db_session, cobro, _local(2024, 1, 1, 8, 0))
    db_session.commit()

    tablero = calcular_tablero(
        db_session, _local(2026, 9, 16, 12, 0), FiltrosTablero(rango="no-existe")
    )

    assert tablero.periodo.rango_activo is None
    assert tablero.periodo.total_ingresos == 1000


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
    assert solo_extra.periodo.total_ingresos == 2000

    solo_anulados = calcular_tablero(db_session, ahora, FiltrosTablero(anulado=True))
    assert solo_anulados.periodo.total_ingresos == 0  # el anulado quedó en $0

    solo_cobrados = calcular_tablero(db_session, ahora, FiltrosTablero(anulado=False))
    assert solo_cobrados.periodo.total_ingresos == 1000 + 2000


def test_periodo_con_base_vacia_no_rompe(db_session):
    tablero = calcular_tablero(db_session, _local(2026, 9, 16, 12, 0))

    assert tablero.periodo.rango_activo is None
    assert tablero.periodo.total_ingresos == 0


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
