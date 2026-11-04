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
