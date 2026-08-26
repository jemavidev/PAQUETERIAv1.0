# 178 — `_buscar_residentes`: esquema `aptNNN` para apartamento exacto + buscar por WhatsApp/email

**Pedido original:** seguimiento a la explicación de cómo buscar por torre/apartamento -- "hagamos
algo solo permite buscar por numero de apartamento y el esquema deberia ser 'apt302' por ejemplo
para buscar los apartamentos que sean el 302 de cualquier torre. Adicional a esto necesito que
permitas la busqueda por usuario de whatsapp y tambien por email."

**Status:** implementado

## Cambio

- `customers_manage.py` (`_buscar_residentes`):
  - **Apartamento por esquema `apt<número>`** (case-insensitive, espacio opcional --
    `apt302`/`APT 302`): match EXACTO contra `Apartamento.apartamento` (no parcial), en
    CUALQUIER torre -- reemplaza el match parcial anterior contra `apartamento` (que sin querer
    también encontraba unidades como "1302" al buscar "302"). Bare digits SIN el prefijo `apt` ya
    NO buscan número de apartamento (evita el falso positivo).
  - Torre sigue igual que antes (parcial, sin prefijo) -- no fue parte del pedido.
  - Nuevos frentes en el filtro de Persona: `Persona.whatsapp_usuario.ilike(...)` y
    `Persona.email.ilike(...)`, mismo criterio parcial que nombre.
  - Docstring actualizado con los 2 esquemas.

## Tests afectados

- `test_buscar_por_apartamento_encuentra_al_residente`: `q="202"` → `q="apt202"`.
- `test_resultados_no_se_duplican_si_varios_criterios_coinciden`: su escenario de dedup usaba
  `q="202"` matcheando nombre + apartamento exacto -- reescrito para usar nombre + TORRE (nombre
  "Ana Torre 2" + unidad en TORRE 2, buscando "TORRE 2"), ya que el número de apartamento ya no
  matchea sin el prefijo `apt`.
- Tests nuevos: WhatsApp encuentra, email encuentra, `apt302` encuentra exacto sin importar la
  torre, `apt30` (prefijo sin el número completo) NO matchea "302" (confirma que es exacto, no
  parcial), bare "302" sin el prefijo `apt` ya NO encuentra el apartamento.

## Verificación

- 6 tests nuevos/reescritos: `apt30` no matchea "302" (exacto, no parcial); `APT 302` (mayúsculas
  + espacio) encuentra en cualquier torre; "302" suelto ya no encuentra apartamento; WhatsApp
  encuentra; email encuentra; los 2 tests existentes de apartamento/dedup migrados al esquema
  nuevo.
- Suite completa: 307/307 (`test_customers_manage.py` + `test_packages.py`).
- Verificado en local (`localhost:8010`): `apt302` trae a los residentes de la unidad 302 en
  CUALQUIER torre (Torre 1 y Torre 2 en los datos de prueba); `302` suelto ya no encuentra nada
  por apartamento; búsqueda por WhatsApp confirmada.
- Pendiente: verificar en test.papyrus.com.co tras deploy.
