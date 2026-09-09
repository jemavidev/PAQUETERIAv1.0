# -*- coding: utf-8 -*-
"""
Servicio de dominio de `ContactoExterno` -- fusión e importación incremental
de fuentes externas (módulo "Consolidación de contactos externos",
`.scratch/contactos-externos`).

`fusionar_fuentes` es una función PURA: no toca la base de datos, agrupa
filas de cualquier fuente por teléfono compartido (componentes conexas,
unión-búsqueda) -- separada así para poder probar toda la lógica de fusión
sin sesión de BD ni HTTP de por medio.
"""

from dataclasses import dataclass

from .telefono import normalizar_telefono

# Tags de fuente conocidos -- usados tanto por el script de importación como
# por la regla de desempate de nombre (gana Google Contacts).
FUENTE_GOOGLE_CONTACTS = "google_contacts"
FUENTE_PRODUCCION_V1 = "produccion_v1"


@dataclass(frozen=True)
class FilaFuenteContacto:
    """Una fila cruda de una fuente externa, antes de fusionar. `telefonos`
    viene TAL CUAL como lo trae la fuente (sin normalizar) -- `fusionar_fuentes`
    normaliza y descarta los que no logren normalizarse."""

    nombre: str
    telefonos: tuple[str, ...]
    fuente: str


@dataclass(frozen=True)
class ContactoExternoConsolidado:
    """Resultado de `fusionar_fuentes` -- un contacto ya fusionado, listo
    para persistirse (`importar_contactos_externos`)."""

    nombre: str
    telefonos: frozenset
    fuentes: frozenset


def fusionar_fuentes(filas: list[FilaFuenteContacto]) -> list[ContactoExternoConsolidado]:
    """Fusiona filas de cualquier fuente en contactos consolidados.

    Dos filas (de la misma fuente o de fuentes distintas) que compartan
    CUALQUIER teléfono terminan en el mismo contacto -- incluyendo el caso
    "puente" (fila A comparte un teléfono con fila B, que a su vez comparte
    otro teléfono con fila C: las tres terminan juntas). Descarta filas sin
    nombre o sin ningún teléfono que logre normalizarse; un teléfono
    individual no reconocible se ignora sin descartar el resto de la fila si
    tiene otro teléfono válido.

    Cuando el nombre difiere entre fuentes para el mismo contacto, gana el
    de `FUENTE_GOOGLE_CONTACTS`; si ninguna fila del grupo vino de ahí, gana
    la primera fila en el orden de aparición.
    """
    padre: dict[str, str] = {}

    def encontrar(x: str) -> str:
        raiz = x
        while padre[raiz] != raiz:
            raiz = padre[raiz]
        while padre[x] != raiz:
            padre[x], x = raiz, padre[x]
        return raiz

    def unir(a: str, b: str) -> None:
        ra, rb = encontrar(a), encontrar(b)
        if ra != rb:
            padre[rb] = ra

    filas_validas: list[tuple[str, list[str], str]] = []
    for fila in filas:
        nombre = (fila.nombre or "").strip()
        telefonos_norm = []
        for tel in fila.telefonos:
            try:
                telefonos_norm.append(normalizar_telefono(tel))
            except ValueError:
                continue
        if not nombre or not telefonos_norm:
            continue

        for tel in telefonos_norm:
            padre.setdefault(tel, tel)
        for tel in telefonos_norm[1:]:
            unir(telefonos_norm[0], tel)

        filas_validas.append((nombre, telefonos_norm, fila.fuente))

    grupos: dict[str, dict] = {}
    for nombre, telefonos_norm, fuente in filas_validas:
        raiz = encontrar(telefonos_norm[0])
        grupo = grupos.setdefault(
            raiz, {"filas_nombre": [], "telefonos": set(), "fuentes": set()}
        )
        grupo["filas_nombre"].append((nombre, fuente))
        grupo["telefonos"].update(telefonos_norm)
        grupo["fuentes"].add(fuente)

    resultado = []
    for grupo in grupos.values():
        nombre_google = next(
            (n for n, f in grupo["filas_nombre"] if f == FUENTE_GOOGLE_CONTACTS), None
        )
        nombre_final = nombre_google if nombre_google is not None else grupo["filas_nombre"][0][0]
        resultado.append(
            ContactoExternoConsolidado(
                nombre=nombre_final,
                telefonos=frozenset(grupo["telefonos"]),
                fuentes=frozenset(grupo["fuentes"]),
            )
        )
    return resultado
