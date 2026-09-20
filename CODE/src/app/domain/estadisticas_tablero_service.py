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
from .paquete import CondicionPaquete, Paquete, TipoPaquete
from .persona import Persona
from .tarifa_cobro import TarifaCobro
from .usuario import Usuario
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
    06: Entregados/Cancelados; 07: Tiempos promedio; 08: tendencia).
    `entregados`/`cancelados` cuentan por la fecha de SU PROPIO evento
    (entrega/cancelación) -- tarjetas separadas, nunca sumadas en un solo
    "procesados" (spec.md, ticket 06)."""

    ingresos: TrioHoySemanaMes
    entregados: TrioHoySemanaMes
    cancelados: TrioHoySemanaMes


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
class ClienteDestacado:
    """Un cliente puntual (por su Teléfono de destinatario) con su NOMBRE --
    el de su Persona si existe, o si no el congelado en el snapshot de su
    paquete más reciente del periodo (nunca el teléfono, spec.md: "mostrando
    siempre el NOMBRE del cliente") -- su Apartamento del snapshot MÁS
    RECIENTE (ADR-0001: nunca la unidad actual) y la cifra que lo hizo
    destacar (cantidad de paquetes, o monto gastado, según la tarjeta)."""

    nombre: str
    apartamento: str | None
    valor: int


@dataclass(frozen=True)
class Clientes:
    """Categoría "Clientes" de Periodo seleccionado -- "cliente" = una
    Persona identificada por el Teléfono del destinatario (`recipient_
    phone`); los paquetes de "nombre sin teléfono" (sin Persona detrás)
    nunca cuentan acá."""

    activos: int
    nuevos: int
    recurrentes: int
    con_mas_paquetes: ClienteDestacado | None
    con_mayor_gasto: ClienteDestacado | None


@dataclass(frozen=True)
class OperacionYCalidad:
    """Categoría "Operación y calidad" de Periodo seleccionado. Todos los
    porcentajes son `None` sin ningún paquete que califique (evita un "0%"
    engañoso). `operador_top`/`dia_mas_activo` son `None` sin ninguna
    entrega en el periodo. Empates: operador y día, por nombre/orden
    lunes→domingo respectivamente -- deterministas entre cargas."""

    operador_top_nombre: str | None
    operador_top_cantidad: int
    dia_mas_activo: str | None
    dia_mas_activo_porcentaje: float | None
    hora_pico: str | None
    porcentaje_dentro_de_48h: float | None
    porcentaje_extra_dimensionados: float | None
    porcentaje_mal_estado: float | None


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
    clientes: Clientes
    operacion: OperacionYCalidad


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


def _contar_paquetes_entre(session: Session, columna, desde_utc: datetime, hasta_utc: datetime) -> int:
    return int(
        session.query(func.count(Paquete.id))
        .filter(columna.isnot(None), columna >= desde_utc, columna <= hasta_utc)
        .scalar()
    )


def _calcular_panorama(session: Session, hoy_local: date) -> Panorama:
    desde_hoy, hasta_hoy = _limites_utc_de_dias_locales(hoy_local, hoy_local)
    desde_semana, hasta_semana = _limites_utc_de_dias_locales(
        hoy_local - timedelta(days=hoy_local.weekday()), hoy_local
    )
    desde_mes, hasta_mes = _limites_utc_de_dias_locales(hoy_local.replace(day=1), hoy_local)

    def _trio_paquetes(columna) -> TrioHoySemanaMes:
        return TrioHoySemanaMes(
            hoy=_contar_paquetes_entre(session, columna, desde_hoy, hasta_hoy),
            semana=_contar_paquetes_entre(session, columna, desde_semana, hasta_semana),
            mes=_contar_paquetes_entre(session, columna, desde_mes, hasta_mes),
        )

    ingresos = TrioHoySemanaMes(
        hoy=_suma_ingresos_entre(session, desde_hoy, hasta_hoy),
        semana=_suma_ingresos_entre(session, desde_semana, hasta_semana),
        mes=_suma_ingresos_entre(session, desde_mes, hasta_mes),
    )
    entregados = _trio_paquetes(Paquete.delivered_at)
    cancelados = _trio_paquetes(Paquete.cancelled_at)
    return Panorama(ingresos=ingresos, entregados=entregados, cancelados=cancelados)


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


def _cliente_no_eliminado_ni_de_baja():
    """Condición para descartar de "activos"/"nuevos"/"recurrentes" a
    Personas dadas de baja administrativa (`dar_de_baja_administrativa`
    nunca toca el Teléfono, así que el JOIN por teléfono la sigue
    encontrando) -- spec.md: no cuentan como clientes aunque tengan
    paquetes históricos.

    Límite conocido y aceptado: `anonimizar_persona` (ADR-0005, derecho al
    olvido) SÍ reemplaza el Teléfono por uno sintético -- el
    `recipient_phone` congelado en un paquete viejo queda huérfano, sin
    ninguna Persona VIVA que lo matchee, así que esta condición no puede
    excluir retroactivamente a alguien ya anonimizado (`Persona.id` da
    `NULL` en el JOIN, tratado como "no excluir" -- mismo criterio
    defensivo de siempre: sin Persona que matchee, no se excluye). Esto no
    empeora nada ya existente: cualquier snapshot de Paquete ya conserva el
    nombre histórico tal cual estaba ANTES de anonimizar, por diseño
    (ADR-0001, "los datos permanecen de principio a fin en cada paquete")."""
    return or_(
        Persona.id.is_(None),
        and_(Persona.eliminado_en.is_(None), Persona.baja_administrativa_en.is_(None)),
    )


def _paquetes_por_cliente_con_movimiento(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> list[tuple[str, int]]:
    """`[(recipient_phone, cantidad)]` de paquetes CON destinatario propio
    (excluye "nombre sin teléfono") que tuvieron cualquier movimiento en el
    rango -- mismo criterio que `_contar_total_paquetes`, agrupado por
    cliente. `tipo`, si viene, filtra (matriz: Tipo SÍ acota Clientes)."""
    query = (
        session.query(Paquete.recipient_phone, func.count(Paquete.id))
        .outerjoin(Persona, Persona.telefono == Paquete.recipient_phone)
        .filter(Paquete.recipient_phone.isnot(None), _cliente_no_eliminado_ni_de_baja())
    )
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)

        def _en_rango(columna):
            return and_(columna.isnot(None), columna >= desde_utc, columna <= hasta_utc)

        query = query.filter(
            or_(
                _en_rango(Paquete.announced_at),
                _en_rango(Paquete.received_at),
                _en_rango(Paquete.delivered_at),
                _en_rango(Paquete.cancelled_at),
            )
        )
    return query.group_by(Paquete.recipient_phone).all()


def _contar_clientes_nuevos(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> int:
    """Clientes cuya PRIMERA entrega HISTÓRICA (toda la vida, no solo el
    periodo) cae dentro del periodo -- por eso arranca de un `MIN(delivered_
    at)` sin acotar por fecha, y solo DESPUÉS se filtra ese mínimo contra el
    rango."""
    base = (
        session.query(Paquete.recipient_phone.label("tel"), func.min(Paquete.delivered_at).label("primera"))
        .outerjoin(Persona, Persona.telefono == Paquete.recipient_phone)
        .filter(
            Paquete.recipient_phone.isnot(None),
            Paquete.delivered_at.isnot(None),
            _cliente_no_eliminado_ni_de_baja(),
        )
    )
    if tipo is not None:
        base = base.filter(Paquete.package_type == tipo)
    subq = base.group_by(Paquete.recipient_phone).subquery()

    query = session.query(func.count()).select_from(subq)
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(subq.c.primera >= desde_utc, subq.c.primera <= hasta_utc)
    return int(query.scalar())


def _nombre_y_apartamento_de_cliente(session: Session, telefono: str) -> tuple[str, str | None]:
    """El NOMBRE de la Persona de este teléfono (o, si no existe Persona, el
    nombre congelado en su paquete más reciente) y su Apartamento del
    snapshot MÁS RECIENTE -- ADR-0001, nunca la unidad actual."""
    persona = session.query(Persona).filter(Persona.telefono == telefono).one_or_none()
    fila = (
        session.query(Paquete.recipient_name, Paquete.snapshot_torre, Paquete.snapshot_apartamento)
        .filter(Paquete.recipient_phone == telefono)
        .order_by(Paquete.announced_at.desc())
        .first()
    )
    torre = apto = None
    nombre_snapshot = telefono
    if fila is not None:
        nombre_snapshot, torre, apto = fila
    nombre = persona.nombre if persona is not None else nombre_snapshot
    partes = [p for p in (torre, apto) if p]
    return nombre, " ".join(partes) if partes else None


def _cliente_destacado(session: Session, filas_telefono_valor) -> "ClienteDestacado | None":
    """El cliente con el mayor `valor` de `[(telefono, valor)]` -- empate
    resuelto por NOMBRE (spec.md: "empates por monto y luego por nombre"),
    determinista entre cargas."""
    candidatos = []
    for telefono, valor in filas_telefono_valor:
        nombre, apartamento = _nombre_y_apartamento_de_cliente(session, telefono)
        candidatos.append((int(valor), nombre, apartamento))
    if not candidatos:
        return None
    candidatos.sort(key=lambda c: (-c[0], c[1]))
    valor, nombre, apartamento = candidatos[0]
    return ClienteDestacado(nombre=nombre, apartamento=apartamento, valor=valor)


def _calcular_clientes(session: Session, hoy_local: date, filtros: FiltrosTablero) -> Clientes:
    rango_dias = _rango_por_atajo(filtros.rango, hoy_local)

    filas_movimiento = _paquetes_por_cliente_con_movimiento(session, rango_dias, filtros.tipo)
    activos = len(filas_movimiento)
    recurrentes = sum(1 for _, cantidad in filas_movimiento if cantidad >= 2)
    nuevos = _contar_clientes_nuevos(session, rango_dias, filtros.tipo)
    con_mas_paquetes = _cliente_destacado(session, filas_movimiento)

    # "Cliente con mayor gasto" -- a diferencia del resto de esta categoría,
    # SÍ respeta Cobrado/Anulado (matriz de "no aplica"): reusa la MISMA
    # consulta de Cobros de "Recaudo", agrupada por destinatario.
    filas_gasto = (
        _query_cobros_periodo(session, hoy_local, filtros)
        .filter(Paquete.recipient_phone.isnot(None))
        .with_entities(Paquete.recipient_phone, func.coalesce(func.sum(Cobro.monto_total), 0))
        .group_by(Paquete.recipient_phone)
        .all()
    )
    con_mayor_gasto = _cliente_destacado(session, filas_gasto)

    return Clientes(
        activos=activos,
        nuevos=nuevos,
        recurrentes=recurrentes,
        con_mas_paquetes=con_mas_paquetes,
        con_mayor_gasto=con_mayor_gasto,
    )


_DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def _formato_hora_pico(hora: int) -> str:
    """`hora` (0-23, local) a un rango de una hora legible, ej. 18 ->
    "6 – 7 p. m." -- usa el sufijo AM/PM de la hora de INICIO para ambos
    extremos (simplificación aceptada: el único cruce real, 23 -> "11 – 12
    p. m.", es un caso raro y de lectura igualmente clara)."""

    def _doce_horas(h: int) -> int:
        h12 = h % 12
        return 12 if h12 == 0 else h12

    sufijo = "a. m." if hora < 12 else "p. m."
    return f"{_doce_horas(hora)} – {_doce_horas((hora + 1) % 24)} {sufijo}"


def _operador_top(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> tuple[str | None, int]:
    query = session.query(Paquete.delivered_by_usuario_id, func.count(Paquete.id)).filter(
        Paquete.delivered_at.isnot(None)
    )
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Paquete.delivered_at >= desde_utc, Paquete.delivered_at <= hasta_utc)
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)

    candidatos = []
    for usuario_id, cantidad in query.group_by(Paquete.delivered_by_usuario_id).all():
        if usuario_id is None:
            continue
        usuario = session.get(Usuario, usuario_id)
        if usuario is None:
            continue
        candidatos.append((int(cantidad), usuario.nombre))
    if not candidatos:
        return None, 0
    candidatos.sort(key=lambda c: (-c[0], c[1]))  # empate: por nombre
    cantidad, nombre = candidatos[0]
    return nombre, cantidad


def _dia_y_hora_pico(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> tuple[str | None, float | None, str | None]:
    """Día de la semana y franja horaria (ambos en HORA DE COLOMBIA) con más
    entregas del periodo -- se resuelve en Python sobre los timestamps ya
    traídos (no en SQL), mismo criterio que el resto del servicio: nunca se
    le pide a la base de datos que conozca zonas horarias con nombre."""
    query = session.query(Paquete.delivered_at).filter(Paquete.delivered_at.isnot(None))
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Paquete.delivered_at >= desde_utc, Paquete.delivered_at <= hasta_utc)
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)
    instantes = [fila[0].astimezone(ZONA_HORARIA_APP) for fila in query.all()]
    if not instantes:
        return None, None, None

    conteo_dia = [0] * 7
    conteo_hora = [0] * 24
    for local in instantes:
        conteo_dia[local.weekday()] += 1
        conteo_hora[local.hour] += 1

    mejor_dia = 0
    for i in range(1, 7):
        if conteo_dia[i] > conteo_dia[mejor_dia]:
            mejor_dia = i
    mejor_hora = 0
    for i in range(1, 24):
        if conteo_hora[i] > conteo_hora[mejor_hora]:
            mejor_hora = i

    total = len(instantes)
    return (
        _DIAS_SEMANA[mejor_dia],
        conteo_dia[mejor_dia] / total * 100,
        _formato_hora_pico(mejor_hora),
    )


def _porcentaje_dentro_de_48h(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> float | None:
    query = session.query(Paquete.received_at, Paquete.delivered_at).filter(Paquete.delivered_at.isnot(None))
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Paquete.delivered_at >= desde_utc, Paquete.delivered_at <= hasta_utc)
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)
    filas = query.all()
    if not filas:
        return None
    dentro = sum(
        1 for recibido, entregado in filas if recibido is not None and (entregado - recibido) <= timedelta(hours=48)
    )
    return dentro / len(filas) * 100


def _porcentaje_extra_dimensionados(session: Session, rango_dias: tuple[date, date] | None) -> float | None:
    """Sobre los RECIBIDOS del periodo -- Tipo NUNCA la acota (matriz de "no
    aplica": filtrar por Tipo la volvería trivial, 0% o 100%)."""
    query = session.query(Paquete.package_type).filter(Paquete.received_at.isnot(None))
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Paquete.received_at >= desde_utc, Paquete.received_at <= hasta_utc)
    tipos = [fila[0] for fila in query.all()]
    if not tipos:
        return None
    return sum(1 for t in tipos if t == TipoPaquete.EXTRA_DIMENSIONADO) / len(tipos) * 100


def _porcentaje_mal_estado(
    session: Session, rango_dias: tuple[date, date] | None, tipo: TipoPaquete | None
) -> float | None:
    query = session.query(Paquete.package_condition).filter(Paquete.received_at.isnot(None))
    if rango_dias is not None:
        desde_utc, hasta_utc = _limites_utc_de_dias_locales(*rango_dias)
        query = query.filter(Paquete.received_at >= desde_utc, Paquete.received_at <= hasta_utc)
    if tipo is not None:
        query = query.filter(Paquete.package_type == tipo)
    condiciones = [fila[0] for fila in query.all()]
    if not condiciones:
        return None
    malos = sum(1 for c in condiciones if c in (CondicionPaquete.ABIERTO, CondicionPaquete.REGULAR))
    return malos / len(condiciones) * 100


def _calcular_operacion(session: Session, hoy_local: date, filtros: FiltrosTablero) -> OperacionYCalidad:
    rango_dias = _rango_por_atajo(filtros.rango, hoy_local)
    operador_nombre, operador_cantidad = _operador_top(session, rango_dias, filtros.tipo)
    dia, dia_pct, hora = _dia_y_hora_pico(session, rango_dias, filtros.tipo)
    return OperacionYCalidad(
        operador_top_nombre=operador_nombre,
        operador_top_cantidad=operador_cantidad,
        dia_mas_activo=dia,
        dia_mas_activo_porcentaje=dia_pct,
        hora_pico=hora,
        porcentaje_dentro_de_48h=_porcentaje_dentro_de_48h(session, rango_dias, filtros.tipo),
        porcentaje_extra_dimensionados=_porcentaje_extra_dimensionados(session, rango_dias),
        porcentaje_mal_estado=_porcentaje_mal_estado(session, rango_dias, filtros.tipo),
    )


def _calcular_periodo(session: Session, hoy_local: date, filtros: FiltrosTablero) -> PeriodoSeleccionado:
    rango_activo = filtros.rango if _rango_por_atajo(filtros.rango, hoy_local) is not None else None
    recaudo = _calcular_recaudo(session, hoy_local, filtros)
    paquetes, ritmo = _calcular_paquetes_y_ritmo(session, hoy_local, filtros)
    clientes = _calcular_clientes(session, hoy_local, filtros)
    operacion = _calcular_operacion(session, hoy_local, filtros)
    return PeriodoSeleccionado(
        rango_activo=rango_activo,
        recaudo=recaudo,
        paquetes=paquetes,
        ritmo=ritmo,
        clientes=clientes,
        operacion=operacion,
    )


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
