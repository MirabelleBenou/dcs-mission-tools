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

## aircraft_masses.json

Table `DCS aircraft type -> empty and maximum weight`, sorted by key, used by the **Loadout Editor** for the weight estimate of each aircraft (empty weight + fuel + stores, gun not counted). A type missing from the table has no estimate.

- **Fields**: `empty` and `max` (kg, integers): the empty weight and the recommended maximum weight.
- **Source**: the aircraft definitions of DCS World (`M_empty`, `M_max`, in `CoreMods/aircraft/<type>/`), read on 6 November 2026 and checked against the mission editor. The Mi-8MT was read in the mission editor (its module was not installed).
- **Licence**: none added; these are values.
- **Regenerate**: no script; the values were entered by hand.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRCRAFT_MASSES:BEGIN */` and `/* AIRCRAFT_MASSES:END */`. `build_mission_tools.py` stops the build if that copy differs from `aircraft_masses.json`.

## aircraft_pylons.json

Table `DCS aircraft type -> pylons -> weapons each pylon accepts`, used by the **Loadout Editor** to compose a loadout station by station: one row per pylon, a drop-down with the weapons the pylon accepts, and the weight of the loadout. A type missing from the table cannot be composed.

- **Shape**: `{"clsids": [...], "weights": [...], "types": {"<type>": {"<pylon>": [index, ...]}}}`. `clsids` is sorted and `weights` has the same rank (kg from pydcs, `null` when pydcs gives none); for each type the pylons are in numeric order and, for each pylon, the weapons (indexes into `clsids`) in pydcs order. Every type that declares at least one pylon is in the table.
- **Source**: the `dcs/planes.py`, `dcs/helicopters.py` and `dcs/weapons_data.py` modules of [pydcs](https://github.com/pydcs/dcs) **1.0.0** (same wheel as above): the `PylonN` classes of each aircraft class that declares an `id`, and the `weight` of each `Weapons` entry.
- **Licence**: LGPL-3.0-or-later, as for `weapon_names.json` ([`COPYING.LESSER`](COPYING.LESSER)).
- **Regenerate** (the modules are read as text, not executed):

  ```
  pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
  python3 -I tools/gen_aircraft_pylons.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl
  ```

  Running it again on the same version rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRCRAFT_PYLONS:BEGIN */` and `/* AIRCRAFT_PYLONS:END */`. `build_mission_tools.py` stops the build if that copy differs from `aircraft_pylons.json`.

## aircraft_views.json

Table `DCS aircraft type -> front view`, used by the **Loadout Editor** to show where each station is: the drawing (SVG text), its `viewBox`, the attachment point of each station in `viewBox` units, and the stations that are off the view. Four types have a view: Mi-24P, Mi-8MT, F-4E-45MC and Mirage-F1EE.

- **Source**: [`views/`](views/): the four `.svg` drawings and `stations.json`, where each type names its drawing (`svg`, relative to `data/`).
- **Licence**: the drawings are by **Goldwolf** (DCS Reference Guide), used with permission, and are **not covered by the repository's MIT licence**: do not reuse them without the author's permission (see [`views/LICENSE.md`](views/LICENSE.md)).
- **Regenerate**:

  ```
  python3 -I tools/gen_aircraft_views.py
  ```

  The generator writes `stations.json` with each `svg` replaced by the text of the file; running it again rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRCRAFT_VIEWS:BEGIN */` and `/* AIRCRAFT_VIEWS:END */`. `build_mission_tools.py` stops the build if that copy differs from `aircraft_views.json`.
