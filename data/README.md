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

Table `DCS aircraft type -> front view`, used by the **Loadout Editor** to show where each station is: the drawing (SVG text), its `viewBox`, the attachment point of each station in `viewBox` units, and the stations that are off the view. 45 types have a view: every aircraft of the DCS Reference Guide v35 that the editor knows.

- **Source**: [`views/`](views/): the 33 `.svg` drawings and `stations.json`, where each type names its drawing (`svg`, relative to `data/`).
- **Licence**: the drawings are by **Goldwolf** (DCS Reference Guide), used with permission, and are **not covered by the repository's AGPL licence**: do not reuse them without the author's permission (see [`views/LICENSE.md`](views/LICENSE.md)).
- **Regenerate**:

  ```
  python3 -I tools/gen_aircraft_views.py
  ```

  The generator writes `stations.json` with each `svg` replaced by the text of the file; running it again rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRCRAFT_VIEWS:BEGIN */` and `/* AIRCRAFT_VIEWS:END */`. `build_mission_tools.py` stops the build if that copy differs from `aircraft_views.json`.

## country_types.json

Table `DCS country -> id, name written by the mission editor, aircraft and helicopter types it can fly, callsign form and lists`, used by the **Loadout Editor** to move a group to another country of its side: the countries offered, the types a country does not fly (greyed out), the name of a country that has no entry in the mission yet, and the callsign rewritten in the form of the new country. A type missing from the table is not checked.

- **Shape**: `{"types": [...], "cat": {...}, "countries": {"<id>": {"name": ..., "cs": "name" | "number", "lists": {...}, "types": [index, ...]}}}`. `types` is the sorted list of the known types and each country lists its types as indexes into it; `cat` gives the callsign category (`AWACS` or `Tankers`) of the types that are not `Air`; `lists` (the `AWACS`, `Tankers` and `Air` callsign names, in order) is present for the countries whose callsign is a name, `cs` is `number` for the others.
- **Source**: `db_countries.lua` of DCS World (`Scripts/Database/`) and the `dcs/countries.py`, `dcs/planes.py` and `dcs/helicopters.py` modules of [pydcs](https://github.com/pydcs/dcs) **1.0.0** (same wheel as above). From `db_countries.lua`: the countries (a country's id is its rank among the `country:add` and `country:next()` calls), the name written in the `.miz` (third argument) and the `cnt_unit(...)` plane and helicopter types of each `country:get("<KEY>").Units` block, commented lines excluded. From pydcs: the types of each country's `Plane` and `Helicopter` classes, `use_western_callsigns` and the `callsign` lists, and the callsign category of each type. A type is allowed in a country if either source puts it there; `AGGRESSORS`, `CJTF_BLUE`, `CJTF_RED` and `UN_PEACEKEEPERS` take every known type, as the game merges them; service dates are not used.
- **Licence**: LGPL-3.0-or-later for the part derived from pydcs, as for `weapon_names.json` ([`COPYING.LESSER`](COPYING.LESSER)). `db_countries.lua` is a DCS World file and is not part of this repository: only the facts read from it (which country flies which type) are kept here.
- **Regenerate** (both files are read as text, not executed; `db_countries.lua` comes from your own DCS World installation):

  ```
  pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
  python3 -I tools/gen_country_types.py "<DCS World>/Scripts/Database/db_countries.lua" /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl
  ```

  Running it again on the same files rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* COUNTRY_TYPES:BEGIN */` and `/* COUNTRY_TYPES:END */`. `build_mission_tools.py` stops the build if that copy differs from `country_types.json`.

## loadout_rules.json

Table `DCS aircraft type -> rules between stations`, used by the **Loadout Editor** in the *Compose a loadout* window: a weapon that clashes with another one is greyed out with the station it clashes with, and a weapon that needs another one says what to fit and where; a loadout that breaks a rule cannot be kept. 32 types of the editor have rules (A-10, AV-8B, F-14, F-15E, F-4E, M-2000C, Mi-24P, MiG-29 and others). A type missing from the table has no rule from the game.

- **Shape**: `{"<type>": {"r": [...], "x": [...]}, ...}`; each entry is `[sa, [ia...], sb, [ib...]]`, with `sa` and `sb` station numbers as strings (`"5"`) and `ia`, `ib` indexes into `clsids` of [`aircraft_pylons.json`](aircraft_pylons.json). `x` (exclusions): a CLSID of `ia` at `sa` does not go with a CLSID of `ib` at `sb`; `ib` is `null` for "any load" (`sb` must stay empty). `r` (requirements): a CLSID of `ia` at `sa` needs a CLSID of `ib` at `sb`. Each list is sorted by station, then by `ib`, then by `ia`.
- **Source**: the aircraft definitions of DCS World, `CoreMods/aircraft/<type>/`: the `required` and `forbidden` lists of each payload, which the mission editor applies. [`tools/read_payload_rules.py`](../tools/read_payload_rules.py) reads them (the Lua is run with [lupa](https://pypi.org/project/lupa/), the game API replaced by stubs) and [`tools/gen_loadout_rules.py`](../tools/gen_loadout_rules.py) reduces them to what the editor can use: a rule is kept only for a weapon the station accepts in `aircraft_pylons.json`; a rule that names the same station, a station the type does not have, or a load the editor does not know is dropped, and so is a "forbidden: empty" rule.
- **Licence**: none added, these are facts read from the game. The aircraft definitions are DCS World files and are not part of this repository.
- **Regenerate**:

  ```
  pip install lupa
  python3 -I tools/read_payload_rules.py "<DCS World>/CoreMods/aircraft" /tmp/payload_rules.json
  python3 -I tools/gen_loadout_rules.py /tmp/payload_rules.json
  ```

  Running it again on the same files rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* PAYLOAD_GAME_RULES:BEGIN */` and `/* PAYLOAD_GAME_RULES:END */`. `build_mission_tools.py` stops the build if that copy differs from `loadout_rules.json`.

## airport_names.json

Table `DCS theatre -> airfield number -> airfield name`, used by the **Loadout Editor** to name the airfield a group departs from when the summary warns that the group leaves a base of its former side. An airfield missing from the table is shown by its number.

- **Shape**: `{"<theatre>": {"<id>": "<name>", ...}, ...}`, keys sorted. The theatre is written as the terrain of pydcs writes it, which is also the `theatre` of a `.miz` (`Caucasus`, `Syria`, `GermanyCW`...); the id is the airfield number of the mission editor, the one a route point carries as `airdromeId`. 12 theatres, 771 airfields.
- **Source**: the `dcs/terrain/<folder>/<folder>.py` (the theatre, first argument of `super().__init__(`) and `dcs/terrain/<folder>/airports.py` (the `id` and `name` of each airfield class) modules of [pydcs](https://github.com/pydcs/dcs) **1.0.0** (same wheel as above).
- **Licence**: pydcs is **LGPL-3.0-or-later**; the table is derived from it and carries the same licence ([`COPYING.LESSER`](COPYING.LESSER)).
- **Regenerate** (the modules are read as text, not executed):

  ```
  pip download --no-deps pydcs==1.0.0 -d /tmp/pydcs
  python3 -I tools/gen_airport_names.py /tmp/pydcs/pydcs-1.0.0-py3-none-any.whl
  ```

  Running it again on the same version rewrites the same bytes.
- **Copy inside the module**: `modules/dcs_loadout_editor.html` carries the same table between the markers `/* AIRPORT_NAMES:BEGIN */` and `/* AIRPORT_NAMES:END */`. `build_mission_tools.py` stops the build if that copy differs from `airport_names.json`.
