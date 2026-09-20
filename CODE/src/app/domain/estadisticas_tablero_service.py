# -*- coding: utf-8 -*-
"""
Servicio de dominio del tablero de tarjetas de
`/administracion/estadisticas-cobro` (`.scratch/estadisticas-cobro-dashboard`,
rediseño que reemplaza al de listas de `.scratch/estadisticas-cobro-
interactivas` -- ese servicio, `cobro_service.estadisticas_cobro`, se retira
en el ticket 17 de esta misma feature; hasta entonces convive sin que nada lo
llame desde la ruta web).

Tres zonas (ver la spec del feature):
  - **Panorama**: cifras FIJAS Hoy / Esta semana / Este mes, en HORA DE
    COLOMBIA -- ignoran siempre los filtros de "Periodo seleccionado".
  - **Ahora**: foto del momento (aún sin tarjetas -- llegan en los tickets
    09-10 de esta misma feature).
  - **Periodo seleccionado**: responde a los filtros (atajo de fecha, Tipo,
    Cobrado/Anulado); sin ningún atajo activo, TODOS los datos existentes
    (issue 364, ya vigente antes de este rediseño).

`calcular_tablero` recibe el instante "ahora" como parámetro EXPLÍCITO --
nunca lee el reloj del sistema por su cuenta -- para que las pruebas puedan
fijarlo. Esto es crítico acá: "Hoy" se resuelve en hora de Colombia (UTC-5),
no en UTC -- a las 19:00 UTC el día local ya cambió, y una tarjeta fija de
"Hoy" que siguiera contando en UTC estaría mostrando el día equivocado
durante 5 horas todas las noches.
"""

import calendar
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from .cobro import Cobro
from .cobro_service import obtener_tarifas_vigentes
from .paquete import Paquete, TipoPaquete
from .tarifa_cobro import TarifaCobro
from .zona_horaria import ZONA_HORARIA_APP


@dataclass(frozen=True)
class FiltrosTablero:
    """Filtros de la zona "Periodo seleccionado" -- Panorama y Ahora los
    ignoran siempre (decisiones D1/D9/D11 del grilling: son fijos / una foto
    del momento, nunca dependen de lo que el admin filtre). `rango=None`, o
    una clave que no matchea ningún atajo conocido, significa "todos los
    datos existentes" (issue 364)."""

    rango: str | None = None
    tipo: TipoPaquete | None = None
    anulado: bool | None = None


@dataclass(frozen=True)
class TrioHoySemanaMes:
    """Una métrica de Panorama: su valor Hoy, Esta semana y Este mes -- las
    tres calculadas en hora de Colombia, ninguna depende de `FiltrosTablero`."""

    hoy: int
    semana: int
    mes: int


@dataclass(frozen=True)
class Panorama:
    """Zona fija del tablero. Se completa ticket a ticket (01: Ingresos;
    06: Entregados/Cancelados; 07: Tiempos promedio; 08: tendencia)."""

    ingresos: TrioHoySemanaMes


@dataclass(frozen=True)
class Paquetes:
    """Categoría "Paquetes" de Periodo seleccionado -- cada cifra por la
    fecha de SU PROPIO evento dentro del periodo (`total` es la unión: con
    cualquier movimiento -- anuncio, recepción, entrega o cancelación --, no
    solo anunciados). `recibidos`/`entregados` ya vienen filtrados por Tipo
    si `FiltrosTablero.tipo` viene seteado (matriz de "no aplica": Tipo SÍ
    acota estas dos, NO acota total/anunciados/cancelados)."""

    total: int
    anunciados: int
    recibidos: int
    entregados: int
    cancelados: int


@dataclass(frozen=True)
class RitmoMetrica:
    """Promedio de una cifra por día, por semana y por mes dentro del
    periodo -- `total del periodo / días del periodo * (1, 7, 30)`."""

    por_dia: float
    por_semana: float
    por_mes: float


@dataclass(frozen=True)
class RitmoYTasas:
    """`ritmo_recibidos`/`ritmo_entregados` respetan el filtro de Tipo (igual
    que `Paquetes.recibidos`/`.entregados`); `ritmo_anunciados` y las 2 tasas
    NO (matriz de "no aplica") -- por eso las tasas SIEMPRE se calculan sobre
    entregados/cancelados sin filtrar por Tipo, aunque `Paquetes.entregados`
    de al lado sí esté filtrado. `tasa_entrega`/`tasa_cancelacion` ya vienen
    en escala de PORCENTAJE (0-100, no 0-1); `None` sin ningún paquete
    cerrado en el periodo (evita un "0%" engañoso)."""

    anunciados: RitmoMetrica
    recibidos: RitmoMetrica
    entregados: RitmoMetrica
    tasa_entrega: float | None
    tasa_cancelacion: float | None


@dataclass(frozen=True)
class Recaudo:
    """Categoría "Recaudo" de Periodo seleccionado. `promedio_por_paquete`,
    los 2 porcentajes, `tasa_anulacion`, `cobro_mas_alto` y
    `dias_bodega_del_mas_alto` son `None` sin ningún cobro en el periodo --
    evita una división por cero o un "$0" engañoso, se pintan como "—".

    `exonerado_anulaciones` y `dejado_de_cobrar_primera_entrega` son
    ESTIMACIONES con las tarifas de SERVICIO vigentes HOY según el Tipo de
    cada paquete anulado/exento -- el `Cobro` solo guarda el resultado
    (servicio en 0), nunca lo que se hubiera cobrado, así que no hay forma
    de saber el monto exacto que tenía cada cobro pasado antes de anularse."""

    total_ingresos: int
    promedio_por_paquete: float | None
    recaudado_bodegaje: int
    porcentaje_bodegaje: float | None
    recaudado_servicio: int
    porcentaje_servicio: float | None
    exonerado_anulaciones: int
    cantidad_anulaciones: int
    tasa_anulacion: float | None
    exenciones_primera_entrega: int
    dejado_de_cobrar_primera_entrega: int
    cobro_mas_alto: int | None
    dias_bodega_del_mas_alto: int | None


@dataclass(frozen=True)
class PeriodoSeleccionado:
    """Zona que responde a `FiltrosTablero`. `rango_activo` es la clave del
    atajo tal como quedó resuelta (`None` si no venía ninguno, o si el que
    vino no matchea ningún atajo conocido) -- lista para pintar las píldoras
    y el chip de filtros activos sin que la plantilla tenga que repetir la
    lógica de qué claves son válidas."""

    rango_activo: str | None
    recaudo: Recaudo
    paquetes: Paquetes
    ritmo: RitmoYTasas


@dataclass(frozen=True)
class TableroEstadisticasCobro:
    panorama: Panorama
    periodo: PeriodoSeleccionado


# --- Atajos de fecha (issue 364; relocados acá desde `web/routes/admin.py`
# en el ticket 01: "hoy" pasa de ser "lo que manda el navegador" a ser "lo
# que dice el reloj del servidor, en hora de Colombia" -- lógica de dominio,
# no de la capa web). ---------------------------------------------------- #


def _restar_meses(d: date, meses: int) -> date:
    """`d` menos `meses` meses calendario; si ese mes no tiene el mismo día
    (ej. 31-may menos 3 meses -> febrero) cae en el último día de ese mes."""
    anio, mes = divmod(d.year * 12 + (d.month - 1) - meses, 12)
    mes += 1
    return date(anio, mes, min(d.day, calendar.monthrange(anio, mes)[1]))


# Meses hacia atrás de las ventanas móviles: "3 últimos meses", "Semestre"
# (= últimos 6 meses), "Último año" (= últimos 12 meses).
_MESES_RANGO_PERIODO = {"tres_meses": 3, "semestre": 6, "anio": 12}


def _rango_por_atajo(clave: str | None, hoy: date) -> tuple[date, date] | None:
    """Los días (desde, hasta), ambos inclusive y LOCALES (hora de
    Colombia), de un atajo de fecha, o `None` si `clave` no es un atajo
    conocido -- sin rango, todos los datos.

    "Esta semana" empieza el lunes; "Este mes", el día 1. Las ventanas de
    varios meses son móviles y terminan hoy: empiezan el día SIGUIENTE a la
    misma fecha N meses atrás (hoy 20-sep, 3 meses -> desde 21-jun), así
    abarcan exactamente N meses."""
    if clave == "hoy":
        return hoy, hoy
    if clave == "ayer":
        ayer = hoy - timedelta(days=1)
        return ayer, ayer
    if clave == "semana":
        return hoy - timedelta(days=hoy.weekday()), hoy
    if clave == "mes":
        return hoy.replace(day=1), hoy
    meses = _MESES_RANGO_PERIODO.get(clave)
    if meses is not None:
        return _restar_meses(hoy, meses) + timedelta(days=1), hoy
    return None


def _limites_utc_de_dias_locales(desde: date, hasta: date) -> tuple[datetime, datetime]:
    """Un rango de días LOCALES (hora de Colombia), ambos inclusive, a
    límites UTC listos para filtrar una columna `DateTime(timezone=True)`
    como `Cobro.cobrado_en`."""
    inicio = datetime.combine(desde, time.min, tzinfo=ZONA_HORARIA_APP)
    fin = datetime.combine(hasta, time.max, tzinfo=ZONA_HORARIA_APP)
    return inicio.astimezone(timezone.utc), fin.astimezone(timezone.utc)


# --- Panorama -------------------------------------------------------------- #


def _suma_ingresos_entre(session: Session, desde_utc: datetime, hasta_utc: datetime) -> int:
    total = (
        session.query(func.coalesce(func.sum(Cobro.monto_total), 0))
        .filter(Cobro.cobrado_en >= desde_utc, Cobro.cobrado_en <= hasta_utc)
        .scalar()
    )
    return int(total)


def _calcular_panorama(session: Session, hoy_local: date) -> Panorama:
    desde_hoy, hasta_hoy = _limites_utc_de_dias_locales(hoy_local, hoy_local)
    desde_semana, hasta_semana = _limites_utc_de_dias_locales(
        hoy_local - timedelta(days=hoy_local.weekday()), hoy_local
    )
    desde_mes, hasta_mes = _limites_utc_de_dias_locales(hoy_local.replace(day=1), hoy_local)
    ingresos = TrioHoySemanaMes(
        hoy=_suma_ingresos_entre(session, desde_hoy, hasta_hoy),
        semana=_suma_ingresos_entre(session, desde_semana, hasta_semana),
        mes=_suma_ingresos_entre(session, desde_mes, hasta_mes),
    )
    return Panorama(ingresos=ingresos)


# --- Periodo seleccionado --------------------------------------------------- #


def _query_cobros_periodo(session: Session, hoy_local: date, filtros: FiltrosTablero):
    """La consulta base de "Periodo seleccionado": `Cobro` unido a `Paquete`
    (para poder filtrar por Tipo), acotada al rango del atajo activo (si lo
    hay) y a Tipo/Cobrado-Anulado (si vienen seteados). Sin atajo activo,
    TODOS los cobros existentes (issue 364)."""
    query = session.query(Cobro).join(Paquete, Cobro.paquete_id == Paquete.id)
    rango_dias = _rango_por_atajo(filtros.rango, hoy_local)
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Cobro.cobrado_en >= desde_utc, Cobro.cobrado_en <= hasta_utc)
    if filtros.tipo is not None:
        query = query.filter(Paquete.package_type == filtros.tipo)
    if filtros.anulado is not None:
        condicion = (
            Cobro.motivo_anulacion.isnot(None) if filtros.anulado else Cobro.motivo_anulacion.is_(None)
        )
        query = query.filter(condicion)
    return query


def _contar_paquetes(
    session: Session,
    columna,
    rango_dias: tuple[date, date] | None,
    tipo: TipoPaquete | None = None,
) -> int:
    """Cuántos `Paquete` tienen `columna` (uno de sus 4 timestamps de
    transición) no-nula y, si hay rango, dentro de él. `tipo`, si viene, se
    suma como condición AND -- lo pasan solo los callers a los que el filtro
    de Tipo SÍ les aplica (ver la matriz de "no aplica" en `Paquetes`)."""
    if rango_dias is None:
        condicion = columna.isnot(None)
    else:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        condicion = and_(columna.isnot(None), columna >= desde_utc, columna <= hasta_utc)
    query = session.query(func.count(Paquete.id)).filter(condicion)
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)
    return int(query.scalar())


def _contar_total_paquetes(session: Session, rango_dias: tuple[date, date] | None) -> int:
    """"Total de paquetes" = con CUALQUIER movimiento en el periodo -- unión
    de los 4 timestamps de transición, no solo `announced_at`. Sin rango,
    simplemente todos los paquetes que existen."""
    if rango_dias is None:
        return int(session.query(func.count(Paquete.id)).scalar())
    desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)

    def _en_rango(columna):
        return and_(columna.isnot(None), columna >= desde_utc, columna <= hasta_utc)

    return int(
        session.query(func.count(Paquete.id))
        .filter(
            or_(
                _en_rango(Paquete.announced_at),
                _en_rango(Paquete.received_at),
                _en_rango(Paquete.delivered_at),
                _en_rango(Paquete.cancelled_at),
            )
        )
        .scalar()
    )


def _dias_del_periodo(session: Session, hoy_local: date, rango_dias: tuple[date, date] | None) -> int:
    """Cuántos días abarca el periodo, para el divisor del ritmo. Con un
    atajo activo, los días de su rango (ambos inclusive). Sin ninguno ("todos
    los datos"), desde el primer `announced_at` que exista hasta hoy -- sin
    ningún paquete todavía, 1 (evita dividir por cero; el ritmo da 0 igual,
    porque el numerador también es 0)."""
    if rango_dias is not None:
        return (rango_dias[1] - rango_dias[0]).days + 1
    primero = session.query(func.min(Paquete.announced_at)).scalar()
    if primero is None:
        return 1
    primero_local = primero.astimezone(ZONA_HORARIA_APP).date()
    return max(1, (hoy_local - primero_local).days + 1)


def _calcular_paquetes_y_ritmo(
    session: Session, hoy_local: date, filtros: FiltrosTablero
) -> tuple[Paquetes, RitmoYTasas]:
    rango_dias = _rango_por_atajo(filtros.rango, hoy_local)

    total = _contar_total_paquetes(session, rango_dias)
    anunciados = _contar_paquetes(session, Paquete.announced_at, rango_dias)
    cancelados = _contar_paquetes(session, Paquete.cancelled_at, rango_dias)
    # Sin filtrar por Tipo -- SIEMPRE, incluso si `filtros.tipo` viene
    # seteado: son la base de las tasas (matriz de "no aplica": Tipo NO
    # acota Tasa de entrega/cancelación).
    entregados_todos = _contar_paquetes(session, Paquete.delivered_at, rango_dias)
    # Con el filtro de Tipo aplicado (si viene) -- lo que se muestra en la
    # tarjeta "Recibidos"/"Entregados" y en su ritmo.
    recibidos = _contar_paquetes(session, Paquete.received_at, rango_dias, tipo=filtros.tipo)
    entregados = _contar_paquetes(session, Paquete.delivered_at, rango_dias, tipo=filtros.tipo)

    paquetes = Paquetes(
        total=total, anunciados=anunciados, recibidos=recibidos, entregados=entregados, cancelados=cancelados
    )

    dias = _dias_del_periodo(session, hoy_local, rango_dias)

    def _ritmo(cantidad: int) -> RitmoMetrica:
        return RitmoMetrica(por_dia=cantidad / dias, por_semana=cantidad / dias * 7, por_mes=cantidad / dias * 30)

    cerrados = entregados_todos + cancelados
    tasa_entrega = (entregados_todos / cerrados * 100) if cerrados else None
    tasa_cancelacion = (cancelados / cerrados * 100) if cerrados else None

    ritmo = RitmoYTasas(
        anunciados=_ritmo(anunciados),
        recibidos=_ritmo(recibidos),
        entregados=_ritmo(entregados),
        tasa_entrega=tasa_entrega,
        tasa_cancelacion=tasa_cancelacion,
    )
    return paquetes, ritmo


def _tarifa_servicio(tarifas: TarifaCobro, tipo: TipoPaquete | None) -> int:
    """La tarifa de SERVICIO vigente que le tocaría a un paquete de `tipo`
    (el bodegaje no entra acá -- solo se estima lo exonerado/exento del
    cargo base, nunca del bodegaje, que nunca se exime -- ver
    `cobro_service.calcular_cobro`)."""
    return tarifas.base_extra_dimensionado if tipo == TipoPaquete.EXTRA_DIMENSIONADO else tarifas.base_normal


def _monto_estimado_por_tipo(filas_tipo_y_cantidad, tarifas: TarifaCobro) -> tuple[int, int]:
    """`filas_tipo_y_cantidad` = pares (Tipo, cantidad) ya agrupados.
    Retorna (cantidad total, monto total) usando la tarifa de servicio
    vigente de cada Tipo -- el monto es siempre una ESTIMACIÓN (ver
    `Recaudo`)."""
    cantidad_total = 0
    monto_total = 0
    for tipo, cantidad in filas_tipo_y_cantidad:
        cantidad = int(cantidad)
        cantidad_total += cantidad
        monto_total += cantidad * _tarifa_servicio(tarifas, tipo)
    return cantidad_total, monto_total


def _calcular_recaudo(session: Session, hoy_local: date, filtros: FiltrosTablero) -> Recaudo:
    tarifas = obtener_tarifas_vigentes(session)
    base = _query_cobros_periodo(session, hoy_local, filtros)

    cantidad, total_ingresos, bodegaje, servicio = base.with_entities(
        func.count(Cobro.id),
        func.coalesce(func.sum(Cobro.monto_total), 0),
        func.coalesce(func.sum(Cobro.monto_bodegaje), 0),
        func.coalesce(func.sum(Cobro.monto_base), 0),
    ).one()
    cantidad = int(cantidad)
    total_ingresos = int(total_ingresos)
    bodegaje = int(bodegaje)
    servicio = int(servicio)

    promedio_por_paquete = (total_ingresos / cantidad) if cantidad else None
    porcentaje_bodegaje = (bodegaje / total_ingresos * 100) if total_ingresos else None
    porcentaje_servicio = (servicio / total_ingresos * 100) if total_ingresos else None

    # "Exonerado por anulaciones" -- Tipo Y Cobrado/Anulado SÍ acotan esta
    # tarjeta (matriz de "no aplica"), así que se calcula sobre el MISMO
    # `base` ya filtrado por ambos.
    anulados_por_tipo = (
        base.filter(Cobro.motivo_anulacion.isnot(None))
        .with_entities(Paquete.package_type, func.count(Cobro.id))
        .group_by(Paquete.package_type)
        .all()
    )
    cantidad_anulaciones, exonerado_anulaciones = _monto_estimado_por_tipo(anulados_por_tipo, tarifas)
    tasa_anulacion = (cantidad_anulaciones / cantidad * 100) if cantidad else None

    # "Exenciones por primera entrega" -- Tipo SÍ acota, Cobrado/Anulado NO
    # (matriz): se recalcula sobre una variante de `base` con el mismo rango
    # y Tipo pero IGNORANDO el filtro de Cobrado/Anulado.
    filtros_sin_anulado = FiltrosTablero(rango=filtros.rango, tipo=filtros.tipo, anulado=None)
    base_exenciones = _query_cobros_periodo(session, hoy_local, filtros_sin_anulado)
    exentos_por_tipo = (
        base_exenciones.filter(Cobro.monto_base == 0, Cobro.motivo_anulacion.is_(None))
        .with_entities(Paquete.package_type, func.count(Cobro.id))
        .group_by(Paquete.package_type)
        .all()
    )
    exenciones_primera_entrega, dejado_de_cobrar_primera_entrega = _monto_estimado_por_tipo(
        exentos_por_tipo, tarifas
    )

    # "Cobro más alto" -- `bloques_bodegaje` es la MISMA cifra que el resto
    # de la app ya le muestra al staff como "N días" (ver `/paquetes`).
    fila_max = (
        base.order_by(Cobro.monto_total.desc())
        .with_entities(Cobro.monto_total, Cobro.bloques_bodegaje)
        .first()
    )
    cobro_mas_alto = int(fila_max[0]) if fila_max is not None else None
    dias_bodega_del_mas_alto = int(fila_max[1]) if fila_max is not None else None

    return Recaudo(
        total_ingresos=total_ingresos,
        promedio_por_paquete=promedio_por_paquete,
        recaudado_bodegaje=bodegaje,
        porcentaje_bodegaje=porcentaje_bodegaje,
        recaudado_servicio=servicio,
        porcentaje_servicio=porcentaje_servicio,
        exonerado_anulaciones=exonerado_anulaciones,
        cantidad_anulaciones=cantidad_anulaciones,
        tasa_anulacion=tasa_anulacion,
        exenciones_primera_entrega=exenciones_primera_entrega,
        dejado_de_cobrar_primera_entrega=dejado_de_cobrar_primera_entrega,
        cobro_mas_alto=cobro_mas_alto,
        dias_bodega_del_mas_alto=dias_bodega_del_mas_alto,
    )


def _calcular_periodo(session: Session, hoy_local: date, filtros: FiltrosTablero) -> PeriodoSeleccionado:
    rango_activo = filtros.rango if _rango_por_atajo(filtros.rango, hoy_local) is not None else None
    recaudo = _calcular_recaudo(session, hoy_local, filtros)
    paquetes, ritmo = _calcular_paquetes_y_ritmo(session, hoy_local, filtros)
    return PeriodoSeleccionado(rango_activo=rango_activo, recaudo=recaudo, paquetes=paquetes, ritmo=ritmo)


def calcular_tablero(
    session: Session, ahora: datetime, filtros: FiltrosTablero = FiltrosTablero()
) -> TableroEstadisticasCobro:
    """El tablero completo para el instante `ahora` (UTC-aware, inyectado --
    nunca `datetime.now()` acá dentro, para que las pruebas puedan fijar el
    reloj) y los `filtros` de "Periodo seleccionado". Panorama y Periodo
    resuelven "hoy" con la MISMA hora de Colombia derivada de `ahora`."""
    hoy_local = ahora.astimezone(ZONA_HORARIA_APP).date()
    return TableroEstadisticasCobro(
        panorama=_calcular_panorama(session, hoy_local),
        periodo=_calcular_periodo(session, hoy_local, filtros),
    )
