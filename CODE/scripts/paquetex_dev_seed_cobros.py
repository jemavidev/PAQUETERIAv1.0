#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Datos de demostración para ver el módulo de cobro y bodegaje en acción
(`/administracion/estadisticas-cobro`, modales Ver/Entregar de `/paquetes`,
`/consultar`, saldo contra entrega).

SOLO para el Postgres local de desarrollo (`paquetex_dev_up.sh`): se niega a
correr contra cualquier host que no sea localhost. Todo lo que siembra es
ficticio -- el repo es público, nada de datos reales acá.

DOS TANDAS
  1. Tanda principal (últimos 90 días, `--entregados`/`--dias`): ~520 paquetes
     ENTREGADO con su Cobro, ~44 RECIBIDO de distintas edades (el modal Entregar
     calcula el bodegaje contra "ahora", así que envejecen solos), ~18
     ANUNCIADO, ~14 CANCELADO, ~24 operadores y ~196 residentes. Forma
     realista: más movimiento hacia lo reciente, picos de quincena, festivos
     y domingos flojos, entregas dentro del horario del conjunto, clientes
     frecuentes y de una sola vez. Cobros de todos los sabores: primera entrega
     (base exenta), bodegaje de 1 a ~27 bloques, extra-dimensionado, anulados
     con motivo (la anulación exonera SOLO el cargo base -- el bodegaje nunca se
     anula, igual que en `packages.py::deliver_action`), destinatario sin
     teléfono, sin apartamento. Más unos saldos contra entrega y 3 motivos de
     anulación extra en el catálogo (solo si faltan).
  2. Historial (`--historial`, 1000 por defecto, hasta `--dias-historial` días
     atrás): paquetes ANTERIORES a la tanda principal, para poder ver la
     diferencia entre "3 últimos meses", "Semestre" y "Último año" (issue 364).
     Es ADITIVO: población propia, no toca ni un cobro de la tanda principal.
     Trae los casos de un año de operación:
       - ~95% ENTREGADO con cobro (todas las variantes de arriba, más algunos
         "rescatados" tras 1-4 meses en bodega), ~3% CANCELADO, ~1% RECIBIDO
         abandonado (casi siempre de un ex-residente) y ~1% ANUNCIADO que nunca
         llegó.
       - Residentes que viven hoy aquí, que YA SE FUERON (sin apartamento
         actual) y que se MUDARON de unidad: sus paquetes viejos conservan la
         unidad anterior (ADR-0001), así que en "Por cliente / apartamento"
         aparecen en dos filas.
       - Curva anual: crecimiento gradual, Black Friday/Navidad, cierre de año,
         festivos cerrados y operadores que trabajaron un tiempo y se fueron.

CÓMO SE DISTINGUE LO SEMBRADO (para poder limpiarlo sin tocar lo tuyo)
  - Teléfonos de residentes que empiezan con `+57399` (prefijo sin asignar).
  - Operadores con email `demoNN@paquetex.test` (TLD reservado, RFC 2606).

USO (desde CODE/)
  .venv/bin/python scripts/paquetex_dev_seed_cobros.py               # sembrar todo (principal + historial)
  .venv/bin/python scripts/paquetex_dev_seed_cobros.py --agregar     # suma SOLO el historial a lo ya sembrado
  .venv/bin/python scripts/paquetex_dev_seed_cobros.py --dry-run     # ensayo, no guarda
  .venv/bin/python scripts/paquetex_dev_seed_cobros.py --reiniciar   # borra lo demo y siembra de nuevo
  .venv/bin/python scripts/paquetex_dev_seed_cobros.py --limpiar     # solo borra lo demo
  Opciones: --entregados N  --dias N  --operadores N  --historial N  --dias-historial N  --semilla N

No borra nunca usuarios/motivos/tarifas/plantillas/apartamentos reales, ni los
paquetes/personas que ya tenías -- ver `paquetex-limpieza-selectiva-bd`.
"""

import argparse
import math
import os
import random
import re
import sys
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.exc import IntegrityError  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.domain.apartamento import Apartamento  # noqa: E402
from app.domain.cobro import Cobro  # noqa: E402
from app.domain.cobro_service import (  # noqa: E402
    DesgloseCobro,
    calcular_cobro,
    crear_motivo_anulacion,
    motivo_anulacion_valido,
    obtener_tarifas_vigentes,
)
from app.domain.estadisticas_tablero_service import FiltrosTablero, calcular_tablero  # noqa: E402
from app.domain.ocupante import Ocupante  # noqa: E402
from app.domain.ocupante_service import (  # noqa: E402
    agregar_ocupante,
    confirmar_ocupante,
    dar_de_baja_ocupante,
    mover_ocupante,
)
from app.domain.paquete import CondicionPaquete, EstadoPaquete, Paquete, TipoPaquete  # noqa: E402
from app.domain.paquete_service import _generar_access_code  # noqa: E402
from app.domain.persona import Persona  # noqa: E402
from app.domain.saldo_contra_entrega_service import registrar_movimiento_saldo  # noqa: E402
from app.domain.staff_service import create_staff  # noqa: E402
from app.domain.usuario import RolUsuario, Usuario  # noqa: E402

DB_URL_DEFECTO = "postgresql://paquetex:paquetex_dev@localhost:5433/paquetex_dev"
HOSTS_LOCALES = {"localhost", "127.0.0.1", "::1"}

PREFIJO_TELEFONO_DEMO = "+57399"
DOMINIO_EMAIL_DEMO = "@paquetex.test"
PASSWORD_DEMO = "Contrasena1"

# (etiqueta, peso) -- las que falten en el catálogo se crean; las que ya
# existan (ej. la que armaste tú a mano) se reusan tal cual.
MOTIVOS_ANULACION = [
    ("Cliente pago en efectivo aparte", 45),
    ("Cortesía de la administración", 30),
    ("Error de digitación", 15),
    ("Paquete llegó en mal estado", 10),
]
PROB_ANULACION = 0.10

# Bogotá/Lima/Quito: UTC-5 todo el año, sin horario de verano. El horario es
# el del conjunto de ejemplo (L-V 9:30-19:30, sáb 9:30-14:00, dom 14:00-18:00).
TZ = timezone(timedelta(hours=-5))
HORARIO_LOCAL = {
    **{d: (time(9, 30), time(19, 30)) for d in range(5)},
    5: (time(9, 30), time(14, 0)),
    6: (time(14, 0), time(18, 0)),
}
PESO_DIA_SEMANA = {0: 0.95, 1: 1.0, 2: 1.0, 3: 1.05, 4: 1.15, 5: 0.75, 6: 0.35}
DIAS_QUINCENA = {1, 2, 15, 16, 30, 31}  # el pedido llega tras cobrar la quincena
# Festivos de fecha fija (Año Nuevo, Trabajo, Batalla de Boyacá... ): el
# conjunto cierra. Los festivos "movibles" no se modelan.
FESTIVOS_FIJOS = {(1, 1), (5, 1), (7, 20), (8, 7), (12, 8), (12, 25)}

# Cuánto antes de "ahora" se fueron / entraron los operadores de la tanda
# principal -- el historial reconstruye a partir de esto quién trabajaba cuándo.
EX_OPERADOR_SALIDA_DIAS = 40
NUEVO_INGRESO_DIAS = 25

NOMBRES = [
    "CAMILA", "SEBASTIÁN", "VALENTINA", "ANDRÉS", "LAURA", "JUAN", "DANIELA", "CARLOS",
    "MARÍA", "JOSÉ", "PAULA", "DAVID", "SOFÍA", "FELIPE", "NATALIA", "SANTIAGO", "ANA",
    "MIGUEL", "LUISA", "JORGE", "CATALINA", "DIEGO", "MARCELA", "ALEJANDRO", "JULIANA",
    "OSCAR", "ISABEL", "RICARDO", "LUCÍA", "MAURICIO", "CLAUDIA", "HÉCTOR", "PATRICIA",
    "NICOLÁS", "GLORIA", "EDUARDO", "ADRIANA", "CAMILO", "ROSA", "FERNANDO",
]
APELLIDOS = [
    "GÓMEZ", "RODRÍGUEZ", "MARTÍNEZ", "LÓPEZ", "GARCÍA", "PÉREZ", "SÁNCHEZ", "RAMÍREZ",
    "TORRES", "DÍAZ", "VARGAS", "CASTRO", "ROJAS", "MORENO", "JIMÉNEZ", "HERNÁNDEZ",
    "MUÑOZ", "ORTIZ", "SILVA", "CARDONA", "OSPINA", "ARIAS", "BOTERO", "MEJÍA",
    "RESTREPO", "LONDOÑO", "SUÁREZ", "CÁRDENAS", "PARRA", "GUERRERO", "ACOSTA",
    "QUINTERO", "PINEDA", "VALENCIA", "DUQUE", "CORTÉS", "NARVÁEZ", "BERNAL", "LEÓN",
    "PRIETO",
]


# --------------------------------------------------------------------------- #
# Seguridad y utilidades                                                       #
# --------------------------------------------------------------------------- #
def _url_local() -> str:
    url = os.environ.get("DATABASE_URL", DB_URL_DEFECTO)
    host = urlparse(url).hostname
    if host not in HOSTS_LOCALES:
        sys.exit(
            f"Este script solo corre contra Postgres local (el host es {host!r}). "
            "Nunca lo apuntes a test/producción."
        )
    return url


class GeneradorNombres:
    """Nombres completos ficticios, sin repetir dentro de una misma corrida ni
    contra los que ya existen como demo."""

    def __init__(self, rng: random.Random, usados=()):
        self._rng = rng
        self._usados: set[str] = set(usados)

    def siguiente(self) -> str:
        while True:
            nombre = f"{self._rng.choice(NOMBRES)} {self._rng.choice(APELLIDOS)}"
            if nombre not in self._usados:
                self._usados.add(nombre)
                return nombre


def _guia(rng: random.Random) -> str:
    if rng.random() < 0.5:
        return "".join(rng.choices("0123456789", k=rng.choice((9, 10, 12))))
    return rng.choice(("SVD", "INT", "ENV", "CRD", "SRV")) + "".join(rng.choices("0123456789", k=9))


def _factor_estacional(d) -> float:
    """Picos y valles del comercio en línea (aproximados): Black Friday y Cyber
    Monday llegan a la puerta en las 2 semanas siguientes, la temporada
    navideña sostiene el ritmo y el cierre de año lo apaga."""
    md = (d.month, d.day)
    if (11, 25) <= md <= (12, 8):
        return 2.0
    if (12, 9) <= md <= (12, 23):
        return 1.5
    if md >= (12, 24) or md <= (1, 6):
        return 0.4
    return 1.0


# --------------------------------------------------------------------------- #
# Calendario: cuándo pasan las cosas                                           #
# --------------------------------------------------------------------------- #
class Calendario:
    """Los días de una ventana (que termina en `fin`, hoy por defecto) con su
    peso de actividad: día de la semana, tendencia (`tendencia` = peso del
    primer y del último día), quincena, temporada, y cierres (festivos fijos +
    ~4% de días al azar; nunca hoy ni ayer, para que "Hoy"/"Ayer" tengan datos)."""

    def __init__(self, rng: random.Random, ahora: datetime, dias: int, *, fin=None,
                 tendencia=(0.65, 1.35)):
        self.rng = rng
        self.ahora = ahora
        self.ahora_local = ahora.astimezone(TZ)
        self.hoy = self.ahora_local.date()
        fin = fin or self.hoy
        self.dias = [fin - timedelta(days=i) for i in range(dias - 1, -1, -1)]
        candidatos = [d for d in self.dias if d < self.hoy - timedelta(days=1)]
        festivos = {d for d in candidatos if (d.month, d.day) in FESTIVOS_FIJOS}
        al_azar = [d for d in candidatos if d not in festivos]
        self.cerrados = festivos | set(
            rng.sample(al_azar, min(len(al_azar), max(2, round(len(candidatos) * 0.04))))
        )
        n = max(1, len(self.dias) - 1)
        primero, ultimo = tendencia
        self.pesos = [
            0.0
            if d in self.cerrados
            else PESO_DIA_SEMANA[d.weekday()]
            * (primero + (ultimo - primero) * i / n)
            * (1.7 if d.day in DIAS_QUINCENA else 1.0)
            * _factor_estacional(d)
            for i, d in enumerate(self.dias)
        ]

    @property
    def inicio(self) -> datetime:
        return datetime.combine(self.dias[0], time.min, tzinfo=TZ).astimezone(timezone.utc)

    @property
    def fin_utc(self) -> datetime:
        return datetime.combine(self.dias[-1], time.max, tzinfo=TZ).astimezone(timezone.utc)

    def dia_utc(self, indice: int) -> datetime:
        """Mediodía (local) del día `indice` de la ventana, en UTC."""
        return datetime.combine(self.dias[indice], time(12, 0), tzinfo=TZ).astimezone(timezone.utc)

    def horario(self, d):
        return None if d in self.cerrados else HORARIO_LOCAL[d.weekday()]

    def instante_en(self, d, tope: datetime | None = None) -> datetime | None:
        """Un instante dentro del horario del día `d` (más denso al final de la
        tarde entre semana, que es cuando la gente pasa a recoger)."""
        h = self.horario(d)
        if h is None:
            return None
        abre = datetime.combine(d, h[0], tzinfo=TZ)
        cierra = datetime.combine(d, h[1], tzinfo=TZ)
        if tope is not None:
            cierra = min(cierra, tope)
        if cierra - abre < timedelta(minutes=15):
            return None
        a, b = (2.4, 1.4) if d.weekday() < 5 else (1.3, 1.3)
        return (abre + (cierra - abre) * self.rng.betavariate(a, b)).astimezone(timezone.utc)

    def instante_de_entrega(self) -> datetime:
        """Un instante de actividad: día ponderado + hora dentro del horario,
        siempre en el pasado (hoy solo hasta hace un minuto)."""
        for _ in range(200):
            d = self.rng.choices(self.dias, self.pesos)[0]
            tope = self.ahora_local - timedelta(minutes=1) if d == self.hoy else None
            instante = self.instante_en(d, tope)
            if instante is not None:
                return instante
        raise RuntimeError("No se pudo muestrear un instante de entrega.")

    def a_horario_previo(self, objetivo: datetime) -> datetime:
        """El instante hábil más cercano a `objetivo` sin pasarse hacia el
        futuro -- una recepción a las 3 a.m. se vería falsa en el historial."""
        loc = objetivo.astimezone(TZ)
        d = loc.date()
        for _ in range(14):
            h = self.horario(d)
            if h is not None:
                abre = datetime.combine(d, h[0], tzinfo=TZ)
                cierra = datetime.combine(d, h[1], tzinfo=TZ)
                if loc >= abre:
                    if loc <= cierra:
                        return objetivo
                    return (cierra - timedelta(minutes=self.rng.randint(5, 90))).astimezone(
                        timezone.utc
                    )
            d -= timedelta(days=1)
            loc = datetime.combine(d, time(23, 59), tzinfo=TZ)
        return objetivo


def _horas_de_permanencia(rng: random.Random, extremo: float = 0.0) -> float:
    """Horas entre Recibido y Entregado: 40% mismo día, 22% al día siguiente, y
    el resto pasa las 48 h de gracia con cola larga (hasta ~28 días). Con
    `extremo` > 0, esa fracción son "rescatados": paquetes que pasaron entre 1 y
    4 meses en bodega antes de que alguien los recogiera."""
    if extremo and rng.random() < extremo:
        return rng.uniform(30 * 24, 120 * 24)
    u = rng.random()
    if u < 0.40:
        return rng.uniform(0.5, 24)
    if u < 0.62:
        return rng.uniform(24, 48)
    return 48 + min(rng.expovariate(1 / 55), 672)


# --------------------------------------------------------------------------- #
# Actores                                                                      #
# --------------------------------------------------------------------------- #
@dataclass
class PersonalDemo:
    usuario: Usuario
    desde: datetime
    hasta: datetime
    peso: float


@dataclass
class Residente:
    persona: Persona
    apto: Apartamento  # su unidad (la ACTUAL, o la que dejó si `se_fue`)
    principal: Persona  # quien anuncia por la unidad
    nuevo: bool = False  # sin ninguna entrega previa (solo paquetes en curso)
    # --- solo historial ---------------------------------------------------- #
    activo_desde: datetime | None = None  # ventana en la que recibe paquetes
    activo_hasta: datetime | None = None
    se_fue: bool = False  # ya no vive en el conjunto
    apto_anterior: Apartamento | None = None  # unidad de la que se mudó
    mudanza_en: datetime | None = None
    ocupante_original: Ocupante | None = None
    ocupante_actual: Ocupante | None = None
    primero: datetime | None = None  # primer/último instante de sus paquetes
    ultimo: datetime | None = None

    def vigente_en(self, instante: datetime) -> bool:
        return (self.activo_desde is None or instante >= self.activo_desde) and (
            self.activo_hasta is None or instante <= self.activo_hasta
        )

    def unidad_en(self, instante: datetime) -> Apartamento:
        """La unidad en la que vivía cuando se anunció el paquete (ADR-0001: el
        snapshot del Paquete congela ESA, no la actual)."""
        if self.mudanza_en is not None and instante < self.mudanza_en:
            return self.apto_anterior
        return self.apto


def _elegir_residente(rng, candidatos, pesos, instante) -> Residente:
    """Un residente ponderado entre los que estaban activos en `instante`."""
    elegibles = [(r, w) for r, w in zip(candidatos, pesos) if r.vigente_en(instante)]
    if not elegibles:
        elegibles = list(zip(candidatos, pesos))
    return rng.choices([r for r, _ in elegibles], [w for _, w in elegibles])[0]


def _crear_personal(db, rng, cal, admin, cantidad, nombres) -> list[PersonalDemo]:
    """Operadores con altas y bajas dentro del rango: las últimas 3 cuentas son
    ex-operadores (inactivos, solo aparecen en lo antiguo) y las 4 anteriores
    son recién llegados (solo en lo reciente)."""
    n_ex = min(3, cantidad // 6)
    n_nuevos = min(4, cantidad // 5)
    ahora = cal.ahora
    lejos = ahora + timedelta(days=1)
    personal = []
    for i in range(cantidad):
        u = create_staff(
            db, admin, f"demo{i + 1:02d}{DOMINIO_EMAIL_DEMO}", nombres.siguiente(),
            PASSWORD_DEMO, RolUsuario.OPERADOR,
        )
        desde, hasta = cal.inicio - timedelta(days=365), lejos
        if i >= cantidad - n_ex:
            u.activo = False
            hasta = ahora - timedelta(days=EX_OPERADOR_SALIDA_DIAS)
        elif i >= cantidad - n_ex - n_nuevos:
            desde = ahora - timedelta(days=NUEVO_INGRESO_DIAS)
        u.created_at = u.updated_at = max(desde, cal.inicio - timedelta(days=30))
        personal.append(PersonalDemo(u, desde, hasta, 0.0))
    _ponderar(rng, personal)
    db.flush()
    return personal


def _ponderar(rng, personal: list[PersonalDemo]) -> None:
    """Unos pocos operadores hacen casi todo (Zipf sobre un orden al azar)."""
    rng.shuffle(personal)
    for rango, p in enumerate(personal):
        p.peso = 1 / (rango + 1) ** 0.8


def _elegir_personal(rng, personal, instante) -> Usuario:
    elegibles = [p for p in personal if p.desde <= instante <= p.hasta]
    return rng.choices(elegibles, [p.peso for p in elegibles])[0].usuario


def _apartamentos_libres(db) -> list[Apartamento]:
    usados = {
        fila[0]
        for fila in db.execute(
            text(
                "SELECT apartamento_id FROM ocupantes WHERE desvinculado_en IS NULL "
                "UNION SELECT apartamento_actual_id FROM personas "
                "WHERE apartamento_actual_id IS NOT NULL"
            )
        )
    }
    todos = db.query(Apartamento).order_by(Apartamento.torre, Apartamento.apartamento).all()
    return [a for a in todos if a.id not in usados]


def _fechar_alta(persona: Persona, ocupante: Ocupante, alta: datetime) -> None:
    persona.created_at = persona.updated_at = persona.terminos_aceptados_en = alta
    ocupante.created_at = ocupante.updated_at = ocupante.confirmado_en = alta


def _alta_residente(db, admin, apto, nombre, telefono, alta) -> tuple[Persona, Ocupante]:
    """Alta por el camino real (`agregar_ocupante` + `confirmar_ocupante`) y
    fechas en el pasado -- si no, cientos de altas "de hoy" inundarían los
    cambios recientes de cada unidad."""
    ocupante = agregar_ocupante(db, apto, nombre, telefono=telefono)
    confirmar_ocupante(db, ocupante, admin)
    persona = db.get(Persona, ocupante.persona_id)
    _fechar_alta(persona, ocupante, alta)
    return persona, ocupante


def _telefonos_demo(db, rng, cantidad) -> list[str]:
    """Teléfonos `399xxxxxxx` que no choquen con los demo ya existentes."""
    existentes = {
        int(t[len(PREFIJO_TELEFONO_DEMO):])
        for (t,) in db.execute(
            text("SELECT telefono FROM personas WHERE telefono LIKE :pref"),
            {"pref": PREFIJO_TELEFONO_DEMO + "%"},
        )
    }
    candidatos = rng.sample(range(1_000_000, 10_000_000), cantidad + len(existentes) + 20)
    return [f"399{n:07d}" for n in candidatos if n not in existentes][:cantidad]


def _crear_residentes(db, rng, cal, admin, n_principales, n_convivientes, n_nuevos, nombres):
    libres = _apartamentos_libres(db)
    if len(libres) < n_principales + n_nuevos:
        sys.exit(f"Solo hay {len(libres)} apartamentos libres; se necesitan más.")
    elegidos = rng.sample(libres, n_principales + n_nuevos)
    telefonos = _telefonos_demo(db, rng, len(elegidos) + n_convivientes)
    residentes = []
    for i, apto in enumerate(elegidos):
        alta = cal.inicio - timedelta(days=rng.randint(1, 60), hours=rng.randint(0, 23))
        persona, _ = _alta_residente(db, admin, apto, nombres.siguiente(), telefonos.pop(), alta)
        residentes.append(Residente(persona, apto, persona, nuevo=i >= n_principales))
    # Convivientes con teléfono propio: dos clientes distintos en la MISMA unidad
    # (la tabla "Por cliente / apartamento" agrupa también por teléfono).
    for base in rng.sample(residentes[:n_principales], n_convivientes):
        alta = cal.inicio - timedelta(days=rng.randint(1, 60), hours=rng.randint(0, 23))
        persona, _ = _alta_residente(db, admin, base.apto, nombres.siguiente(), telefonos.pop(), alta)
        residentes.append(Residente(persona, base.apto, base.persona))
    db.flush()
    return residentes


# --------------------------------------------------------------------------- #
# Paquetes y cobros                                                            #
# --------------------------------------------------------------------------- #
def _tipo(rng) -> TipoPaquete:
    return TipoPaquete.EXTRA_DIMENSIONADO if rng.random() < 0.14 else TipoPaquete.NORMAL


def _condicion(rng) -> CondicionPaquete:
    return rng.choices(list(CondicionPaquete), [93, 4, 3])[0]


def _paquete(db, rng, nombres, r, *, estado, anunciado_en, recibido_en=None, entregado_en=None,
             cancelado_en=None, tipo=None, condicion=None, recibio=None, entrego=None,
             cancelo=None, motivo_cancelacion=None, solo_nombre=False, sin_apto=False,
             anuncio_staff=None) -> Paquete:
    anunciante = rng.choice([r.persona, r.principal])
    apto = None if sin_apto else r.unidad_en(anunciado_en)
    ultimo = max(t for t in (anunciado_en, recibido_en, entregado_en, cancelado_en) if t)
    r.primero = anunciado_en if r.primero is None else min(r.primero, anunciado_en)
    r.ultimo = ultimo if r.ultimo is None else max(r.ultimo, ultimo)
    paquete = Paquete(
        access_code=_generar_access_code(db),
        guide_number=_guia(rng) if recibido_en and rng.random() < 0.7 else None,
        package_type=tipo,
        package_condition=condicion,
        announced_by_persona_id=anunciante.id,
        announced_by_phone=anunciante.telefono,
        recipient_name=nombres.siguiente() if solo_nombre else r.persona.nombre,
        recipient_phone=None if solo_nombre else r.persona.telefono,
        snapshot_conjunto=apto.conjunto if apto else None,
        snapshot_torre=apto.torre if apto else None,
        snapshot_apartamento=apto.apartamento if apto else None,
        estado=estado,
        announced_at=anunciado_en,
        received_at=recibido_en,
        delivered_at=entregado_en,
        cancelled_at=cancelado_en,
        announced_by_usuario_id=anuncio_staff.id if anuncio_staff else None,
        received_by_usuario_id=recibio.id if recibio else None,
        delivered_by_usuario_id=entrego.id if entrego else None,
        cancelled_by_usuario_id=cancelo.id if cancelo else None,
        cancel_reason=motivo_cancelacion,
        created_at=anunciado_en,
        updated_at=ultimo,
    )
    db.add(paquete)
    db.flush()
    return paquete


def _registrar_cobro(db, rng, paquete, tarifas, primera_entrega, motivos) -> Cobro:
    """Misma aritmética que `packages.py::deliver_action`: `calcular_cobro` al
    instante de entrega y, si se anula, solo el cargo base pasa a $0."""
    desglose = calcular_cobro(paquete, tarifas, paquete.delivered_at, primera_entrega)
    motivo = None
    if desglose.monto_base > 0 and rng.random() < PROB_ANULACION:
        motivo = rng.choices([m for m, _ in motivos], [w for _, w in motivos])[0]
        desglose = DesgloseCobro(
            monto_base=0,
            bloques_bodegaje=desglose.bloques_bodegaje,
            monto_bodegaje=desglose.monto_bodegaje,
            monto_total=desglose.monto_bodegaje,
        )
    cobro = Cobro(
        paquete_id=paquete.id,
        monto_base=desglose.monto_base,
        bloques_bodegaje=desglose.bloques_bodegaje,
        monto_bodegaje=desglose.monto_bodegaje,
        monto_total=desglose.monto_total,
        motivo_anulacion=motivo,
        cobrado_por_usuario_id=paquete.delivered_by_usuario_id,
        cobrado_en=paquete.delivered_at + timedelta(seconds=rng.randint(0, 3)),
    )
    db.add(cobro)
    db.flush()
    return cobro


def _generar_entregados(db, cal, rng, nombres, residentes, personal, tarifas, motivos, n,
                        extremo=0.0):
    """Cronológico a propósito: la exención de "primera entrega" depende de si
    el teléfono ya tuvo un ENTREGADO antes, así que el orden importa."""
    activos = [r for r in residentes if not r.nuevo]
    rng.shuffle(activos)
    pesos = [1 / (i + 1) ** 0.6 for i in range(len(activos))]  # pocos frecuentes, cola larga
    instantes = sorted(cal.instante_de_entrega() for _ in range(n))
    con_entrega: set[str] = set()
    hechos = []
    for entregado_en in instantes:
        r = _elegir_residente(rng, activos, pesos, entregado_en)
        solo_nombre = rng.random() < 0.03
        sin_apto = not solo_nombre and rng.random() < 0.02
        recibido_en = cal.a_horario_previo(
            entregado_en - timedelta(hours=_horas_de_permanencia(rng, extremo))
        )
        anunciado_en = recibido_en - timedelta(
            hours=max(0.3, min(96.0, rng.lognormvariate(math.log(8), 0.9)))
        )
        paquete = _paquete(
            db, rng, nombres, r,
            estado=EstadoPaquete.ENTREGADO, anunciado_en=anunciado_en,
            recibido_en=recibido_en, entregado_en=entregado_en,
            tipo=_tipo(rng), condicion=_condicion(rng),
            recibio=_elegir_personal(rng, personal, recibido_en),
            entrego=_elegir_personal(rng, personal, entregado_en),
            solo_nombre=solo_nombre, sin_apto=sin_apto,
            anuncio_staff=_elegir_personal(rng, personal, anunciado_en) if rng.random() < 0.25 else None,
        )
        telefono = paquete.recipient_phone
        primera = telefono is not None and telefono not in con_entrega
        if telefono is not None:
            con_entrega.add(telefono)
        hechos.append(_registrar_cobro(db, rng, paquete, tarifas, primera, motivos))
    return hechos


def _generar_cancelados(db, cal, rng, nombres, activos, pesos, personal, motivos_cancelacion, n):
    """CANCELADO: 2/3 cancelados apenas anunciados, 1/3 ya recibidos."""
    for _ in range(n):
        cancelado_en = cal.instante_de_entrega()
        r = _elegir_residente(rng, activos, pesos, cancelado_en)
        recibido_en = None
        if rng.random() < 0.33:
            recibido_en = cal.a_horario_previo(cancelado_en - timedelta(hours=rng.uniform(1, 24)))
            anunciado_en = recibido_en - timedelta(hours=rng.uniform(1, 30))
        else:
            anunciado_en = cancelado_en - timedelta(hours=rng.uniform(1, 72))
        _paquete(
            db, rng, nombres, r, estado=EstadoPaquete.CANCELADO,
            anunciado_en=anunciado_en, recibido_en=recibido_en, cancelado_en=cancelado_en,
            tipo=_tipo(rng) if recibido_en else None,
            condicion=_condicion(rng) if recibido_en else None,
            recibio=_elegir_personal(rng, personal, recibido_en) if recibido_en else None,
            cancelo=_elegir_personal(rng, personal, cancelado_en),
            motivo_cancelacion=rng.choice(motivos_cancelacion),
        )


def _generar_en_curso(db, cal, rng, nombres, residentes, personal, motivos_cancelacion,
                      n_recibidos, n_anunciados, n_cancelados):
    ahora = cal.ahora
    regulares = [r for r in residentes if not r.nuevo]
    nuevos = [r for r in residentes if r.nuevo]
    pesos = [1 / (i + 1) ** 0.6 for i in range(len(regulares))]

    # RECIBIDO: edades repartidas para ver todo el rango del bodegaje -- recién
    # llegados (<24 h), en gracia (24-48 h) y de 1 a ~27 días de bodegaje.
    n_frescos = int(n_recibidos * 0.27)
    n_gracia = int(n_recibidos * 0.18)
    n_largos = n_recibidos - n_frescos - n_gracia
    edades = (
        [rng.uniform(1, 24) for _ in range(n_frescos)]
        + [rng.uniform(24, 48) for _ in range(n_gracia)]
        + [48 + (i + 1) * (600 / n_largos) * rng.uniform(0.7, 1.3) for i in range(n_largos)]
    )
    rng.shuffle(edades)
    # Los residentes "nuevos" reciben su primer paquete acá: el modal Entregar
    # les marca "primera entrega" (base exenta) porque no tienen ningún ENTREGADO.
    para_recibir = nuevos[: max(0, min(len(nuevos), n_recibidos // 4))]
    receptores = para_recibir + rng.choices(regulares, pesos, k=n_recibidos - len(para_recibir))
    recibidos = []
    for r, edad in zip(receptores, edades):
        recibido_en = cal.a_horario_previo(ahora - timedelta(hours=edad))
        anunciado_en = recibido_en - timedelta(hours=max(0.3, min(72.0, rng.lognormvariate(math.log(6), 0.8))))
        recibidos.append(_paquete(
            db, rng, nombres, r,
            estado=EstadoPaquete.RECIBIDO, anunciado_en=anunciado_en, recibido_en=recibido_en,
            tipo=_tipo(rng), condicion=_condicion(rng),
            recibio=_elegir_personal(rng, personal, recibido_en),
            solo_nombre=rng.random() < 0.04,
        ))

    # ANUNCIADO: los nuevos que quedaron sin recibir + regulares.
    receptores_anunciados = nuevos[len(para_recibir):] + rng.choices(
        regulares, pesos, k=max(0, n_anunciados - len(nuevos[len(para_recibir):]))
    )
    for r in receptores_anunciados:
        _paquete(
            db, rng, nombres, r, estado=EstadoPaquete.ANUNCIADO,
            anunciado_en=ahora - timedelta(minutes=rng.randint(10, 72 * 60)),
        )

    _generar_cancelados(db, cal, rng, nombres, regulares, pesos, personal, motivos_cancelacion,
                        n_cancelados)
    return recibidos


def _sembrar_saldos(db, cal, rng, personal, recibidos):
    """Saldo contra entrega en algunos de los destinatarios con paquete
    RECIBIDO, para que el modal Entregar lo muestre: deuda, deuda parcialmente
    pagada y saldo a favor."""
    personas = {}
    for p in recibidos:
        if p.recipient_phone:
            personas.setdefault(p.recipient_phone, p)
    perfiles = [[-8000], [-15000], [-25000], [-35000], [-60000], [-12000],
                [-30000, 10000], [-45000, 20000], [50000], [20000]]
    telefonos = rng.sample(sorted(personas), min(len(perfiles), len(personas)))
    creados = 0
    for telefono, movimientos in zip(telefonos, perfiles):
        persona = db.query(Persona).filter(Persona.telefono == telefono).one()
        dias_atras = rng.randint(8, 25)
        for monto in movimientos:
            m = registrar_movimiento_saldo(
                db, persona.id, monto, _elegir_personal(rng, personal, cal.ahora)
            )
            m.created_at = cal.ahora - timedelta(days=dias_atras, hours=rng.randint(0, 6))
            dias_atras = max(1, dias_atras - rng.randint(2, 6))
            creados += 1
    db.flush()
    return creados


# --------------------------------------------------------------------------- #
# Historial: lo que pasó antes de la tanda principal                           #
# --------------------------------------------------------------------------- #
def _personal_existente(db, cal, primera_entrega: datetime) -> list[PersonalDemo]:
    """Los operadores demo que YA existen, con su ventana de actividad
    reconstruida: los inactivos son ex-operadores; los que ingresaron después de
    la primera entrega de la tanda principal no existían en el historial; el
    resto trabajaba todo el rango. Sus altas se llevan atrás de todo el
    historial (una cuenta no puede ser posterior a lo que registró)."""
    desde_siempre = cal.inicio - timedelta(days=3650)
    personal = []
    for u in db.query(Usuario).filter(Usuario.email.like("%" + DOMINIO_EMAIL_DEMO)).all():
        if u.created_at > primera_entrega:
            continue
        hasta = (
            cal.ahora + timedelta(days=1)
            if u.activo
            else cal.ahora - timedelta(days=EX_OPERADOR_SALIDA_DIAS)
        )
        u.created_at = min(u.created_at, cal.inicio - timedelta(days=30))
        personal.append(PersonalDemo(u, desde_siempre, hasta, 0.0))
    return personal


def _crear_ex_operadores(db, rng, cal, admin, cantidad, nombres) -> list[PersonalDemo]:
    """Operadores que trabajaron unos meses durante el historial y se fueron."""
    numeros = [
        int(re.search(r"\d+", email).group())
        for (email,) in db.execute(
            text("SELECT email FROM usuarios WHERE email LIKE :dom"),
            {"dom": "%" + DOMINIO_EMAIL_DEMO},
        )
    ]
    siguiente = max(numeros, default=0) + 1
    personal = []
    for i in range(cantidad):
        u = create_staff(
            db, admin, f"demo{siguiente + i:02d}{DOMINIO_EMAIL_DEMO}", nombres.siguiente(),
            PASSWORD_DEMO, RolUsuario.OPERADOR,
        )
        u.activo = False
        entra = cal.dia_utc(rng.randint(0, int(len(cal.dias) * 0.6)))
        sale = min(entra + timedelta(days=rng.randint(60, 240)), cal.fin_utc - timedelta(days=15))
        u.created_at = u.updated_at = entra - timedelta(days=15)
        personal.append(PersonalDemo(u, entra, sale, 0.0))
    db.flush()
    return personal


def _crear_residentes_historicos(db, rng, cal, admin, n_vivos, n_convivientes, n_ex, n_mudados,
                                 nombres) -> list[Residente]:
    """Población propia del historial (no toca a los residentes de la tanda
    principal): quienes viven hoy en el conjunto, quienes ya se fueron y quienes
    se mudaron de unidad. Cada uno solo recibe paquetes dentro de su tiempo en
    el conjunto; las fechas exactas de alta/baja se ajustan al final con
    `_fechar_altas_y_bajas` a partir de sus paquetes reales."""
    necesarios = n_vivos + n_ex + 2 * n_mudados
    libres = _apartamentos_libres(db)
    if len(libres) < necesarios:
        sys.exit(f"Solo hay {len(libres)} apartamentos libres; el historial necesita {necesarios}.")
    aptos = rng.sample(libres, necesarios)
    telefonos = _telefonos_demo(db, rng, n_vivos + n_ex + n_mudados + n_convivientes)
    n_dias = len(cal.dias)
    inicio = cal.inicio

    def llegada(max_fraccion: float) -> datetime:
        # Casi la mitad ya vivía allí antes de que empiece el historial.
        if rng.random() < 0.45:
            return inicio - timedelta(days=30)
        return cal.dia_utc(rng.randint(0, int(n_dias * max_fraccion)))

    def nuevo_residente(apto, desde, hasta, **extra) -> Residente:
        persona, ocupante = _alta_residente(db, admin, apto, nombres.siguiente(), telefonos.pop(), inicio)
        return Residente(persona, apto, persona, activo_desde=desde, activo_hasta=hasta,
                         ocupante_original=ocupante, ocupante_actual=ocupante, **extra)

    vivos, ex, mudados = [], [], []
    for _ in range(n_vivos):
        vivos.append(nuevo_residente(aptos.pop(), llegada(0.85), cal.fin_utc))
    for _ in range(n_ex):
        desde = llegada(0.70)
        hasta = max(
            desde + timedelta(days=20),
            min(desde + timedelta(days=rng.randint(45, 300)), cal.fin_utc - timedelta(days=10)),
        )
        r = nuevo_residente(aptos.pop(), desde, hasta, se_fue=True)
        dar_de_baja_ocupante(db, r.ocupante_original)
        ex.append(r)
    for _ in range(n_mudados):
        desde = llegada(0.55)
        hasta = cal.fin_utc
        apto_anterior, apto_nuevo = aptos.pop(), aptos.pop()
        r = nuevo_residente(apto_anterior, desde, hasta)
        r.mudanza_en = desde + (hasta - desde) * rng.uniform(0.30, 0.70)
        r.apto_anterior = apto_anterior
        r.apto = apto_nuevo
        r.ocupante_actual = mover_ocupante(db, r.ocupante_original, apto_nuevo)
        confirmar_ocupante(db, r.ocupante_actual, admin)
        mudados.append(r)
    # Convivientes con teléfono propio, en la unidad de un residente que vive hoy.
    convivientes = []
    for base in rng.sample(vivos, min(n_convivientes, len(vivos))):
        persona, ocupante = _alta_residente(db, admin, base.apto, nombres.siguiente(), telefonos.pop(), inicio)
        convivientes.append(Residente(
            persona, base.apto, base.persona, activo_desde=base.activo_desde,
            activo_hasta=base.activo_hasta, ocupante_original=ocupante, ocupante_actual=ocupante,
        ))
    db.flush()
    return vivos + ex + mudados + convivientes


def _fechar_altas_y_bajas(db, rng, cal, residentes) -> None:
    """Una vez generados los paquetes, fecha cada alta, baja y mudanza de forma
    coherente con ellos: nadie existe antes de su primer paquete, y quien se fue
    lo hizo después de su último paquete. Todo en el pasado."""
    ayer = cal.ahora - timedelta(days=1)
    for r in residentes:
        desde = r.activo_desde or cal.inicio
        if r.primero is not None:
            desde = min(desde, r.primero)
        alta = desde - timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 23))
        _fechar_alta(r.persona, r.ocupante_original, alta)
        if r.mudanza_en is not None:
            r.ocupante_original.desvinculado_en = r.ocupante_original.updated_at = r.mudanza_en
            nuevo = r.ocupante_actual
            nuevo.created_at = nuevo.updated_at = nuevo.confirmado_en = r.mudanza_en + timedelta(hours=1)
        if r.se_fue:
            hasta = max(r.activo_hasta, r.ultimo + timedelta(days=1)) if r.ultimo else r.activo_hasta
            r.ocupante_original.desvinculado_en = r.ocupante_original.updated_at = min(hasta, ayer)
    db.flush()


def _generar_casos_borde(db, cal, rng, nombres, residentes, personal, n_abandonados, n_anunciados):
    """Lo que en un año de operación se queda sin resolver: paquetes RECIBIDOS
    hace meses que nadie recogió (casi siempre de alguien que ya se fue) y
    anuncios que el paquete nunca llegó a respaldar."""
    activos = [r for r in residentes if not r.nuevo]
    ex = [r for r in activos if r.se_fue]
    for _ in range(n_abandonados):
        recibido_en = cal.a_horario_previo(cal.instante_de_entrega())
        pool = ex if ex and rng.random() < 0.6 else activos
        r = _elegir_residente(rng, pool, [1.0] * len(pool), recibido_en)
        _paquete(
            db, rng, nombres, r, estado=EstadoPaquete.RECIBIDO,
            anunciado_en=recibido_en - timedelta(hours=rng.uniform(1, 40)), recibido_en=recibido_en,
            tipo=_tipo(rng), condicion=_condicion(rng),
            recibio=_elegir_personal(rng, personal, recibido_en),
        )
    for _ in range(n_anunciados):
        anunciado_en = cal.instante_de_entrega()
        r = _elegir_residente(rng, activos, [1.0] * len(activos), anunciado_en)
        _paquete(db, rng, nombres, r, estado=EstadoPaquete.ANUNCIADO, anunciado_en=anunciado_en)


# --------------------------------------------------------------------------- #
# Limpieza                                                                     #
# --------------------------------------------------------------------------- #
_PERSONAS_DEMO = "SELECT id FROM personas WHERE telefono LIKE :pref"
_PAQUETES_DEMO = (
    f"SELECT id FROM paquetes WHERE announced_by_persona_id IN ({_PERSONAS_DEMO}) "
    "OR recipient_phone LIKE :pref"
)


def _hay_datos_demo(db) -> bool:
    pref = {"pref": PREFIJO_TELEFONO_DEMO + "%", "dom": "%" + DOMINIO_EMAIL_DEMO}
    return bool(
        db.execute(text("SELECT 1 FROM personas WHERE telefono LIKE :pref LIMIT 1"), pref).first()
        or db.execute(text("SELECT 1 FROM usuarios WHERE email LIKE :dom LIMIT 1"), pref).first()
    )


def _primera_entrega_demo(db) -> datetime | None:
    return db.execute(
        text(
            "SELECT min(delivered_at) FROM paquetes WHERE estado = 'ENTREGADO' "
            f"AND announced_by_persona_id IN ({_PERSONAS_DEMO})"
        ),
        {"pref": PREFIJO_TELEFONO_DEMO + "%"},
    ).scalar()


def _limpiar(db) -> None:
    """Borra solo lo demo, en orden de claves foráneas. Los catálogos (motivos,
    tarifas, apartamentos, plantillas) y los usuarios reales no se tocan."""
    pref = {"pref": PREFIJO_TELEFONO_DEMO + "%"}
    pasos = [
        ("saldos", f"DELETE FROM movimientos_saldo_contra_entrega WHERE persona_id IN ({_PERSONAS_DEMO}) OR paquete_id IN ({_PAQUETES_DEMO})"),
        ("cobros", f"DELETE FROM cobros WHERE paquete_id IN ({_PAQUETES_DEMO})"),
        ("fotos", f"DELETE FROM paquete_fotos WHERE paquete_id IN ({_PAQUETES_DEMO})"),
        ("paquetes", f"DELETE FROM paquetes WHERE id IN ({_PAQUETES_DEMO})"),
        ("preferencias", f"DELETE FROM persona_preferencia_notificacion WHERE persona_id IN ({_PERSONAS_DEMO})"),
        ("ocupantes", f"DELETE FROM ocupantes WHERE persona_id IN ({_PERSONAS_DEMO})"),
        ("personas", "DELETE FROM personas WHERE telefono LIKE :pref"),
    ]
    resumen = []
    for nombre, sql in pasos:
        resumen.append(f"{db.execute(text(sql), pref).rowcount} {nombre}")

    borrados = desactivados = 0
    demo = db.execute(
        text("SELECT id FROM usuarios WHERE email LIKE :dom"), {"dom": "%" + DOMINIO_EMAIL_DEMO}
    ).all()
    for (uid,) in demo:
        try:
            with db.begin_nested():
                db.execute(text("DELETE FROM usuarios WHERE id = :u"), {"u": uid})
            borrados += 1
        except IntegrityError:
            # Ya tiene historial propio (ej. entraste con esa cuenta y operaste):
            # no se borra, se desactiva.
            db.execute(text("UPDATE usuarios SET activo = false WHERE id = :u"), {"u": uid})
            desactivados += 1
    resumen.append(f"{borrados} operadores demo")
    print("Limpieza: " + ", ".join(resumen))
    if desactivados:
        print(f"  ({desactivados} operadores demo tienen historial propio: quedaron desactivados)")


# --------------------------------------------------------------------------- #
# Orquestación                                                                 #
# --------------------------------------------------------------------------- #
def _asegurar_motivos_anulacion(db) -> list[tuple[str, int]]:
    for etiqueta, _ in MOTIVOS_ANULACION:
        if not motivo_anulacion_valido(db, etiqueta):
            crear_motivo_anulacion(db, etiqueta)
    return MOTIVOS_ANULACION


def _actores_compartidos(db):
    admin = db.query(Usuario).filter(Usuario.rol == RolUsuario.ADMIN, Usuario.activo.is_(True)).first()
    if admin is None:
        sys.exit("No hay ningún ADMIN en la base: corre paquetex_dev_up.sh primero.")
    tarifas = obtener_tarifas_vigentes(db)
    motivos = _asegurar_motivos_anulacion(db)
    motivos_cancelacion = [
        f[0] for f in db.execute(text("SELECT etiqueta FROM motivos_cancelacion")).all()
    ] or ["Otro"]
    return admin, tarifas, motivos, motivos_cancelacion


def _nombres_ya_usados(db) -> set[str]:
    filas = db.execute(
        text(
            "SELECT nombre FROM personas WHERE telefono LIKE :pref "
            "UNION SELECT nombre FROM usuarios WHERE email LIKE :dom"
        ),
        {"pref": PREFIJO_TELEFONO_DEMO + "%", "dom": "%" + DOMINIO_EMAIL_DEMO},
    )
    return {f[0] for f in filas}


def _sembrar_tanda_principal(db, args, ahora, admin, tarifas, motivos, motivos_cancelacion) -> None:
    rng = random.Random(args.semilla)
    cal = Calendario(rng, ahora, args.dias)
    nombres = GeneradorNombres(rng, _nombres_ya_usados(db))

    n = args.entregados
    n_principales = max(20, round(n * 0.29))
    n_convivientes = max(4, round(n * 0.06))
    n_nuevos = 14
    n_recibidos = max(12, round(n * 0.085))
    n_anunciados = max(6, round(n * 0.035))
    n_cancelados = max(4, round(n * 0.027))

    print("Tanda principal: creando personal demo...")
    personal = _crear_personal(db, rng, cal, admin, args.operadores, nombres)
    print("Tanda principal: creando residentes...")
    residentes = _crear_residentes(db, rng, cal, admin, n_principales, n_convivientes, n_nuevos, nombres)
    print(f"Tanda principal: creando {n} paquetes entregados con su cobro...")
    cobros = _generar_entregados(db, cal, rng, nombres, residentes, personal, tarifas, motivos, n)
    print("Tanda principal: creando paquetes en curso (recibidos, anunciados, cancelados)...")
    recibidos = _generar_en_curso(
        db, cal, rng, nombres, residentes, personal, motivos_cancelacion,
        n_recibidos, n_anunciados, n_cancelados,
    )
    n_saldos = _sembrar_saldos(db, cal, rng, personal, recibidos)

    print()
    print(f"Tanda principal ({args.dias} días, semilla {args.semilla}):")
    print(f"  Paquetes   {len(cobros) + n_recibidos + n_anunciados + n_cancelados}: "
          f"ENTREGADO {len(cobros)} · RECIBIDO {n_recibidos} · ANUNCIADO {n_anunciados} · CANCELADO {n_cancelados}")
    _imprimir_cobros(cobros)
    print(f"  Residentes {len(residentes)} ({n_principales} principales, {n_convivientes} convivientes, "
          f"{n_nuevos} nuevos sin entregas)")
    inactivos = sum(1 for p in personal if not p.usuario.activo)
    print(f"  Operadores {len(personal)} ({inactivos} inactivos), saldos contra entrega: {n_saldos} movimientos")


def _sembrar_historial(db, args, ahora, admin, tarifas, motivos, motivos_cancelacion) -> None:
    primera = _primera_entrega_demo(db)
    if primera is None:
        sys.exit("No hay entregas demo previas sobre las que armar el historial.")
    hoy = ahora.astimezone(TZ).date()
    fin = primera.astimezone(TZ).date() - timedelta(days=1)
    dias = (fin - (hoy - timedelta(days=args.dias_historial))).days + 1
    if dias < 30:
        sys.exit(
            f"El historial ya existe: las entregas demo llegan hasta {fin + timedelta(days=1)}. "
            "Usa --reiniciar para rehacerlo, o sube --dias-historial."
        )

    rng = random.Random(f"{args.semilla}:historial")
    # Crecimiento gradual que empalma con el ritmo con que arranca la tanda
    # principal (su peso inicial es 0.65).
    cal = Calendario(rng, ahora, dias, fin=fin, tendencia=(0.30, 0.65))
    nombres = GeneradorNombres(rng, _nombres_ya_usados(db))

    total = args.historial
    n_cancelados = round(total * 0.03)
    n_abandonados = max(3, round(total * 0.01))
    n_anunciados = max(3, round(total * 0.012))
    n_entregados = max(1, total - n_cancelados - n_abandonados - n_anunciados)
    unidades = max(12, round(n_entregados * 0.30))
    n_mudados = max(2, round(unidades * 0.08))
    n_ex = max(3, round(unidades * 0.35))
    n_vivos = max(4, unidades - n_mudados - n_ex)
    n_convivientes = max(2, round(n_vivos * 0.10))

    print(f"Historial: {cal.dias[0]} .. {cal.dias[-1]} ({dias} días)")
    print("Historial: reconstruyendo el personal que ya existe y creando ex-operadores...")
    personal = _personal_existente(db, cal, primera)
    personal += _crear_ex_operadores(db, rng, cal, admin, max(3, round(args.operadores / 3)), nombres)
    _ponderar(rng, personal)
    print("Historial: creando residentes (viven hoy, ya se fueron, se mudaron de unidad)...")
    residentes = _crear_residentes_historicos(
        db, rng, cal, admin, n_vivos, n_convivientes, n_ex, n_mudados, nombres
    )
    print(f"Historial: creando {n_entregados} paquetes entregados con su cobro...")
    cobros = _generar_entregados(
        db, cal, rng, nombres, residentes, personal, tarifas, motivos, n_entregados, extremo=0.006
    )
    print("Historial: creando cancelados, abandonados y anuncios sin paquete...")
    activos = [r for r in residentes if not r.nuevo]
    _generar_cancelados(db, cal, rng, nombres, activos, [1.0] * len(activos), personal,
                        motivos_cancelacion, n_cancelados)
    _generar_casos_borde(db, cal, rng, nombres, residentes, personal, n_abandonados, n_anunciados)
    _fechar_altas_y_bajas(db, rng, cal, residentes)

    print()
    print(f"Historial ({dias} días antes de la tanda principal, semilla {args.semilla}):")
    print(f"  Paquetes   {n_entregados + n_cancelados + n_abandonados + n_anunciados}: ENTREGADO {n_entregados} · "
          f"CANCELADO {n_cancelados} · RECIBIDO abandonado {n_abandonados} · ANUNCIADO sin llegar {n_anunciados}")
    _imprimir_cobros(cobros)
    rescatados = sum(1 for c in cobros if c.bloques_bodegaje > 28)
    print(f"  Casos      {rescatados} rescatados tras >28 días de bodega (hasta {max(c.bloques_bodegaje for c in cobros)} bloques)")
    print(f"  Residentes {len(residentes)}: {n_vivos} viven hoy · {n_convivientes} convivientes · "
          f"{n_ex} ya se fueron · {n_mudados} se mudaron de unidad")
    print(f"  Operadores {len(personal)} en el historial (incluye {max(3, round(args.operadores / 3))} ex-operadores nuevos)")


def _imprimir_cobros(cobros) -> None:
    anulados = sum(1 for c in cobros if c.motivo_anulacion)
    con_bodegaje = sum(1 for c in cobros if c.bloques_bodegaje > 0)
    exentos = sum(1 for c in cobros if c.monto_base == 0 and not c.motivo_anulacion)
    total = sum(c.monto_total for c in cobros)
    print(f"  Cobros     {len(cobros)} por ${total:,}: {anulados} anulados · {con_bodegaje} con bodegaje · "
          f"{exentos} exentos por primera entrega")


def _imprimir_estadisticas(db, ahora) -> None:
    """Los mismos rangos que los atajos de la pantalla, calculados con el mismo
    servicio (`calcular_tablero`, el que usa la ruta) -- así este resumen y la
    pantalla nunca divergen."""
    print()
    print("Estadísticas de cobro por atajo (mismo cálculo que la pantalla; incluye tus cobros propios):")
    atajos = [("Esta semana", "semana"), ("Este mes", "mes"), ("3 últimos meses", "tres_meses"),
              ("Semestre", "semestre"), ("Último año", "anio"), ("Todos los datos", None)]
    for etiqueta, clave in atajos:
        periodo = calcular_tablero(db, ahora, FiltrosTablero(rango=clave)).periodo
        prom = periodo.recaudo.promedio_por_paquete
        print(f"  {etiqueta:<18} {periodo.paquetes.entregados:>5} entregados · ${periodo.recaudo.total_ingresos:>10,} · "
              f"promedio por paquete {('$' + format(prom, ',.0f')) if prom is not None else '—':>7} · "
              f"{periodo.recaudo.cantidad_anulaciones} anulaciones")


def _sembrar(db, args) -> None:
    ahora = datetime.now(timezone.utc)
    admin, tarifas, motivos, motivos_cancelacion = _actores_compartidos(db)
    if not args.agregar:
        _sembrar_tanda_principal(db, args, ahora, admin, tarifas, motivos, motivos_cancelacion)
    if args.historial > 0:
        if not args.agregar:
            print()
        _sembrar_historial(db, args, ahora, admin, tarifas, motivos, motivos_cancelacion)
    elif args.agregar:
        sys.exit("--agregar con --historial 0 no tiene nada que agregar.")
    _imprimir_estadisticas(db, ahora)


def _parse_args():
    ap = argparse.ArgumentParser(description="Datos demo del módulo de cobro (solo Postgres local).")
    ap.add_argument("--entregados", type=int, default=520, help="tanda principal: paquetes ENTREGADO con cobro (defecto 520)")
    ap.add_argument("--dias", type=int, default=90, help="tanda principal: ventana de días hacia atrás (defecto 90)")
    ap.add_argument("--operadores", type=int, default=24, help="tanda principal: operadores demo (defecto 24; >20 para ver la paginación de 'Por usuario')")
    ap.add_argument("--historial", type=int, default=1000, help="paquetes de historial anteriores a la tanda principal, de todos los estados (defecto 1000; 0 = sin historial)")
    ap.add_argument("--dias-historial", type=int, default=455, help="hasta cuántos días atrás llega el historial (defecto 455, ~15 meses: alcanza para ver qué deja fuera 'Último año')")
    ap.add_argument("--semilla", type=int, default=42, help="semilla del generador aleatorio")
    ap.add_argument("--dry-run", action="store_true", help="ensayo: calcula y muestra el resumen, no guarda nada")
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--agregar", action="store_true", help="no crea la tanda principal: suma SOLO el historial a los datos demo ya sembrados")
    grupo.add_argument("--limpiar", action="store_true", help="solo borra los datos demo")
    grupo.add_argument("--reiniciar", action="store_true", help="borra los datos demo y vuelve a sembrar")
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    url = _url_local()
    db = sessionmaker(bind=create_engine(url))()
    print(f"Base de datos: {urlparse(url).hostname}:{urlparse(url).port}{urlparse(url).path}")
    try:
        if args.limpiar or args.reiniciar:
            _limpiar(db)
        elif args.agregar:
            if not _hay_datos_demo(db):
                sys.exit("No hay datos demo a los que agregarles historial: siembra primero (sin --agregar).")
        elif _hay_datos_demo(db):
            sys.exit(
                "Ya hay datos demo. Usa --agregar para sumarles historial, --reiniciar para "
                "volver a sembrar, o --limpiar para borrarlos."
            )
        if not args.limpiar:
            _sembrar(db, args)
        if args.dry_run:
            db.rollback()
            print("\n(--dry-run: no se guardó nada)")
        else:
            db.commit()
            if not args.limpiar:
                print("\nListo. Entra a http://localhost:8010/administracion/estadisticas-cobro")
                print(f"Operadores demo: demo01{DOMINIO_EMAIL_DEMO} … / {PASSWORD_DEMO}")
    except BaseException:
        db.rollback()
        raise
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
