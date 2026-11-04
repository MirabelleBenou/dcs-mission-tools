# data/

## weapon_names.json

Table `CLSID -> weapon name`, sorted by key, used by the **Loadout Editor** to show each pylon by the name of its weapon. A CLSID missing from the table is shown as is.

- **Source**: the `dcs/weapons_data.py` module of [pydcs](https://github.com/pydcs/dcs) **1.0.0** (PyPI wheel `pydcs-1.0.0-py3-none-any.whl`).
- **Licence**: pydcs is **LGPL-3.0-or-later**; the table is derived from it and carries the same licence. The full text is in [`COPYING.LESSER`](COPYING.LESSER).
- **Regenerate** (the module is read as text, not executed):

  ```
  pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
  python3 -I tools/gen_weapon_names.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl
  ```

  Running it again on the same version rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* WEAPON_NAMES:BEGIN */` and `/* WEAPON_NAMES:END */`, so the tool stays a single autonomous file. `build_mission_tools.py` stops the build if that copy differs from `weapon_names.json`.

## aircraft_limits.json

Table `DCS aircraft type -> limits`, sorted by key, used by the **Loadout Editor** to show each type's maximum fuel and countermeasure capacity under the *Settings* fields, and to refuse a value above them. A type missing from the table has no maximum shown and no check.

- **Fields**: `fuel_max` (kg), `flare`, `chaff`, `charge_total`, `flare_charge_size`, `chaff_charge_size`, as declared by the aircraft class in pydcs; `null` when the class does not declare the field. Flares and chaff together must fit in `charge_total`: `flares x flare_charge_size + chaff x chaff_charge_size <= charge_total`.
- **Source**: the `dcs/planes.py` and `dcs/helicopters.py` modules of [pydcs](https://github.com/pydcs/dcs) **1.0.0** (same wheel as above), one entry per class that declares an `id`.
- **Licence**: LGPL-3.0-or-later, as for `weapon_names.json` ([`COPYING.LESSER`](COPYING.LESSER)).
- **Regenerate** (the modules are read as text, not executed):

  ```
  pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
  python3 -I tools/gen_aircraft_limits.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl
  ```

  Running it again on the same version rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRCRAFT_LIMITS:BEGIN */` and `/* AIRCRAFT_LIMITS:END */`. `build_mission_tools.py` stops the build if that copy differs from `aircraft_limits.json`.
